"""Upload reviewed partner-university photographs to Supabase Storage.

Downloads only the manifest-approved download URLs (Wikimedia hosts),
validates MIME by magic bytes and enforces a size cap, uploads to a
deterministic object path under the university-images bucket, and reuses an
existing object when its checksum already matches. The service role key is
fetched at runtime from the Supabase Management API using the owner's
SUPABASE_ACCESS_TOKEN; it never touches the frontend or the repository.

Successful uploads update partner_universities.image, website, and
image_attribution per university (a failure keeps the existing row), and
every outcome is written back to the manifest. Use --dry-run to preview the
plan without any storage or database writes.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = REPO_ROOT / "data" / "exchange-enhancements" / "university-assets.json"
DEFAULT_BUCKET = "university-images"
DEFAULT_PROJECT_REF = "wydziozsjibkvpgphpia"
MANAGEMENT_API = "https://api.supabase.com/v1/projects"
ALLOWED_HOSTS = {"upload.wikimedia.org", "thumb.wikimedia.org"}
MAX_BYTES = 4 * 1024 * 1024
# Reviewed redistribution licenses: the manifest records the exact label.
ALLOWED_LICENSES = re.compile(r"^(CC0 1\.0|CC BY(-SA)? [0-9.]+)$")

MIME_SNIFF = (
    (b"\xff\xd8\xff", "jpeg", ".jpg"),
    (b"\x89PNG\r\n\x1a\n", "png", ".png"),
)


class UploadError(RuntimeError):
    """Raised when an asset cannot be acquired or verified safely."""


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, build the plan, and apply it unless dry-run."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="reviewed asset manifest; defaults to data/exchange-enhancements/university-assets.json",
    )
    parser.add_argument(
        "--bucket",
        default=DEFAULT_BUCKET,
        help="storage bucket name (default: university-images)",
    )
    parser.add_argument(
        "--project-ref",
        default=DEFAULT_PROJECT_REF,
        help="Supabase project ref (default: the deployed exchange catalog project)",
    )
    parser.add_argument(
        "--database-url",
        help="PostgreSQL URL for the metadata update; when omitted, a SQL "
        "artifact is written for manual application instead",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="download, validate, and report without uploading or writing",
    )
    args = parser.parse_args(argv)

    manifest_path = args.manifest
    if manifest_path is None and DEFAULT_MANIFEST.is_file():
        manifest_path = DEFAULT_MANIFEST
    if manifest_path is None:
        parser.error("no manifest found; pass --manifest")

    access_token = os.environ.get("SUPABASE_ACCESS_TOKEN", "").strip()
    if not access_token:
        print("error: SUPABASE_ACCESS_TOKEN is required", file=sys.stderr)
        return 1

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entries = manifest.get("universities")
        if not isinstance(entries, list) or not entries:
            raise UploadError("manifest must contain a non-empty 'universities' list")
        problems = _validate_entries(entries)
        if problems:
            for problem in problems:
                print(f"error: {problem}", file=sys.stderr)
            return 1

        storage_url = f"https://{args.project_ref}.supabase.co/storage/v1"
        service_key = _fetch_service_key(access_token, args.project_ref)
        plan = build_upload_plan(entries, storage_url, service_key, bucket=args.bucket)
        _print_plan(plan, dry_run=args.dry_run)

        if args.dry_run:
            return 0

        outcomes = _apply_plan(plan, args)
        _write_manifest_outcomes(manifest_path, manifest, outcomes)
        sql = _render_sql(outcomes)
        artifact = manifest_path.parent / "university-assets-updates.sql"
        artifact.write_text(sql, encoding="utf-8")
        print(f"SQL artifact written: {artifact}")

        failed = [item for item in outcomes if item["status"] == "failed"]
        if args.database_url:
            _apply_sql(args.database_url, outcomes)
        else:
            print("no --database-url given; apply the SQL artifact (e.g. via the MCP channel)")
        return 1 if failed else 0
    except (UploadError, OSError, ValueError, urllib.error.URLError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def _validate_entries(entries: list[Any]) -> list[str]:
    """Check every manifest entry before any network or storage access."""

    problems: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            problems.append(f"malformed entry: {entry!r}")
            continue
        name = str(entry.get("partner_university") or "")
        partner_id = entry.get("partner_university_id")
        if not name or not isinstance(partner_id, int):
            problems.append(f"{name or '<unknown>'}: partner_university_id must be an integer")
        website = entry.get("website")
        if not (isinstance(website, dict) and str(website.get("url", "")).startswith("https://")):
            problems.append(f"{name}: website.url must be an https URL")
        image = entry.get("image")
        if not isinstance(image, dict) or image.get("status") != "approved":
            problems.append(f"{name}: image must have status 'approved'")
            continue
        url = str(image.get("download_url") or "")
        host = urllib.request.urlparse(url).netloc
        if not url.startswith("https://") or host not in ALLOWED_HOSTS:
            problems.append(f"{name}: download_url must be https on a reviewed Wikimedia host")
        if not ALLOWED_LICENSES.match(str(image.get("license") or "")):
            problems.append(f"{name}: license {image.get('license')!r} is not redistribution-cleared")
        if not str(image.get("attribution") or "").strip():
            problems.append(f"{name}: attribution text is required")
        for field in ("width", "height"):
            if not isinstance(image.get(field), int) or image[field] <= 0:
                problems.append(f"{name}: image.{field} must be a positive integer")
    return problems


def build_upload_plan(
    entries: list[dict],
    storage_url: str,
    service_key: str,
    bucket: str,
) -> list[dict[str, Any]]:
    """Download, validate, and hash each approved photo; compare checksums."""

    plan: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="university-assets-") as tmp:
        for entry in entries:
            name = str(entry["partner_university"])
            partner_id = int(entry["partner_university_id"])
            image = entry["image"]
            object_name = f"universities/{partner_id}"
            record: dict[str, Any] = {
                "partner_university": name,
                "partner_university_id": partner_id,
                "object": object_name,
                "attribution": image["attribution"],
                "website": entry["website"]["url"],
                "download_url": image["download_url"],
            }
            try:
                local_path = _download(image["download_url"], Path(tmp))
                mime, ext = _sniff_mime(local_path)
                record["object"] = f"{object_name}{ext}"
                record["content_type"] = f"image/{mime}"
                record["bytes"] = local_path.stat().st_size
                record["sha256"] = hashlib.sha256(local_path.read_bytes()).hexdigest()
                existing = _fetch_existing(storage_url, service_key, bucket, record["object"])
                record["reused"] = existing is not None and existing == record["sha256"]
                record["public_url"] = (
                    f"https://{urllib.request.urlparse(storage_url).netloc}"
                    f"/storage/v1/object/public/{bucket}/{record['object']}"
                )
                record["status"] = "reused" if record["reused"] else "ready"
            except UploadError as exc:
                record["status"] = "failed"
                record["detail"] = str(exc)
            plan.append(record)
    return plan


def _apply_plan(plan: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    """Upload the ready objects, verify them publicly, and keep outcomes."""

    storage_url = f"https://{args.project_ref}.supabase.co/storage/v1"
    service_key = _fetch_service_key(_require_token(), args.project_ref)
    outcomes = [dict(record) for record in plan]
    with tempfile.TemporaryDirectory(prefix="university-assets-") as tmp:
        for record in outcomes:
            if record["status"] == "failed":
                continue
            if record["status"] == "reused":
                if not _verify_public(record["public_url"]):
                    record["status"] = "failed"
                    record["detail"] = "existing object is not publicly readable"
                continue
            try:
                local_path = _download(record["download_url"], Path(tmp))
                _put_object(storage_url, service_key, args.bucket, record, local_path)
                if not _verify_public(record["public_url"]):
                    raise UploadError("public read-back failed after upload")
                record["status"] = "uploaded"
            except UploadError as exc:
                record["status"] = "failed"
                record["detail"] = str(exc)
    return outcomes


def _require_token() -> str:
    token = os.environ.get("SUPABASE_ACCESS_TOKEN", "").strip()
    if not token:
        raise UploadError("SUPABASE_ACCESS_TOKEN is required")
    return token


def _fetch_service_key(access_token: str, project_ref: str) -> str:
    """Retrieve the service role key through the Management API (never printed)."""

    request = urllib.request.Request(
        f"{MANAGEMENT_API}/{project_ref}/api-keys?reveal=true",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            keys = json.loads(response.read())
    except (urllib.error.URLError, ValueError) as exc:
        raise UploadError(f"cannot retrieve the service role key: {exc}") from None
    for key in keys:
        if key.get("name") == "service_role":
            return str(key["api_key"])
    for key in keys:
        if key.get("type") == "secret":
            return str(key["api_key"])
    raise UploadError("no service-role credential found in the api-keys response")


def _download(url: str, target_dir: Path) -> Path:
    """Fetch one manifest-approved URL; enforce https, the host allowlist, size."""

    parsed = urllib.request.urlparse(url)
    if parsed.scheme != "https" or parsed.netloc not in ALLOWED_HOSTS:
        raise UploadError(f"refusing non-approved download host: {parsed.netloc}")
    request = urllib.request.Request(url, headers={"User-Agent": "nus-exchange-planner-assets/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            if response.status != 200:
                raise UploadError(f"download returned HTTP {response.status}")
            data = response.read(MAX_BYTES + 1)
    except urllib.error.URLError as exc:
        raise UploadError(f"download failed: {exc}") from None
    if len(data) > MAX_BYTES:
        raise UploadError(f"download exceeds the {MAX_BYTES}-byte limit")
    if len(data) == 0:
        raise UploadError("download returned an empty body")
    path = target_dir / "asset"
    path.write_bytes(data)
    return path


def _sniff_mime(path: Path) -> tuple[str, str]:
    """Identify the image type by magic bytes; reject anything else."""

    head = path.read_bytes()[:16]
    if head.startswith(b"RIFF") and head[8:12] == b"WEBP":
        return "webp", ".webp"
    for signature, mime, ext in MIME_SNIFF:
        if head.startswith(signature):
            return mime, ext
    raise UploadError("bytes are not a JPEG, PNG, or WebP image")


def _fetch_existing(storage_url: str, service_key: str, bucket: str, object_name: str) -> str | None:
    """Return the sha256 of the stored object, or None when absent."""

    request = urllib.request.Request(
        f"{storage_url}/object/{bucket}/{object_name}",
        headers={"Authorization": f"Bearer {service_key}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return hashlib.sha256(response.read(MAX_BYTES + 1)).hexdigest()
    except urllib.error.HTTPError as exc:
        if exc.code == 400 or exc.code == 404:
            return None
        raise UploadError(f"existing-object check failed: HTTP {exc.code}") from None
    except urllib.error.URLError as exc:
        raise UploadError(f"existing-object check failed: {exc}") from None


def _put_object(
    storage_url: str,
    service_key: str,
    bucket: str,
    record: dict[str, Any],
    local_path: Path,
) -> None:
    """Upload the validated bytes to the deterministic object path."""

    request = urllib.request.Request(
        f"{storage_url}/object/{bucket}/{record['object']}",
        data=local_path.read_bytes(),
        method="PUT",
        headers={
            "Authorization": f"Bearer {service_key}",
            "Content-Type": record["content_type"],
            "x-upsert": "true",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            if response.status not in (200, 201):
                raise UploadError(f"upload returned HTTP {response.status}")
    except urllib.error.HTTPError as exc:
        body = exc.read(300).decode("utf-8", "replace")
        raise UploadError(f"upload failed: HTTP {exc.code} {body}") from None
    except urllib.error.URLError as exc:
        raise UploadError(f"upload failed: {exc}") from None


def _verify_public(public_url: str) -> bool:
    """Confirm the public read path serves the object without credentials."""

    request = urllib.request.Request(public_url, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.status == 200
    except urllib.error.URLError:
        return False


def _render_sql(outcomes: list[dict[str, Any]]) -> str:
    """Per-university UPDATE statements for every uploaded/reused asset."""

    lines = [
        "-- Partner university metadata for the university-images bucket.",
        "-- Generated by backend/scripts/upload_university_assets.py; apply in one transaction.",
    ]
    for record in outcomes:
        if record["status"] not in ("uploaded", "reused"):
            continue
        lines.append(
            "update public.partner_universities"
            " set image = {image}, website = {website}, image_attribution = {attribution}"
            " where id = {id};".format(
                image=_quote(record["public_url"]),
                website=_quote(record["website"]),
                attribution=_quote(record["attribution"]),
                id=record["partner_university_id"],
            )
        )
    return "\n".join(lines) + "\n"


def _quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _apply_sql(database_url: str, outcomes: list[dict[str, Any]]) -> None:
    """Apply the per-university updates directly when the pooler is reachable."""

    import psycopg

    ready = [r for r in outcomes if r["status"] in ("uploaded", "reused")]
    if not ready:
        return
    try:
        with psycopg.connect(database_url, autocommit=False, prepare_threshold=None) as conn, \
                conn.transaction():
            for record in ready:
                conn.execute(
                    "update public.partner_universities"
                    " set image = %s, website = %s, image_attribution = %s where id = %s",
                    (record["public_url"], record["website"], record["attribution"],
                     record["partner_university_id"]),
                )
    except psycopg.Error as exc:
        raise UploadError(f"database update failed: {exc}") from None


def _write_manifest_outcomes(
    manifest_path: Path,
    manifest: dict[str, Any],
    outcomes: list[dict[str, Any]],
) -> None:
    """Record the acquisition state of each university back in the manifest."""

    stamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    by_name = {str(item["partner_university"]): item for item in outcomes}
    for entry in manifest["universities"]:
        outcome = by_name.get(str(entry.get("partner_university")))
        if outcome is None:
            continue
        entry["acquisition"] = {
            "status": outcome["status"],
            "object": outcome.get("object"),
            "public_url": outcome.get("public_url"),
            "sha256": outcome.get("sha256"),
            "bytes": outcome.get("bytes"),
            "recorded_at": stamp,
            **({"detail": outcome["detail"]} if "detail" in outcome else {}),
        }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _print_plan(plan: list[dict[str, Any]], dry_run: bool) -> None:
    """Print the deterministic upload plan for review and the run log."""

    mode = "dry run - no storage or database writes" if dry_run else "will apply"
    print(f"University asset plan ({mode})")
    for record in plan:
        if record["status"] == "failed":
            print(f"  {record['partner_university']}: failed - {record['detail']}")
        elif record["status"] == "reused":
            print(f"  {record['partner_university']}: checksum matches, keep existing object")
        else:
            print(
                f"  {record['partner_university']}: upload {record['object']} "
                f"({record['bytes']} bytes, sha256 {record['sha256'][:12]}...)"
            )


if __name__ == "__main__":
    sys.exit(main())
