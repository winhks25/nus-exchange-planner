"""Disposable PostgreSQL cluster support for repository validation tests."""

import os
import shutil
import socket
import subprocess
import time
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS = sorted((REPO_ROOT / "supabase" / "migrations").glob("*.sql"))
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}

# Disposable local clusters use trust authentication; these passwords only make
# the role-bearing connection URLs explicit and are never used for a remote server.
IMPORTER_ROLE = "catalog_importer"
READER_ROLE = "catalog_reader"
TEST_ROLE_PASSWORD = "catalog-test-local"

ROLE_SETUP_SQL = f"""
do $$
begin
  if not exists (select 1 from pg_roles where rolname = '{IMPORTER_ROLE}') then
    create role {IMPORTER_ROLE} login password '{TEST_ROLE_PASSWORD}';
  else
    alter role {IMPORTER_ROLE} login password '{TEST_ROLE_PASSWORD}';
  end if;
  alter role {READER_ROLE} login password '{TEST_ROLE_PASSWORD}';
end
$$;
grant usage on schema public to {IMPORTER_ROLE};
grant select, insert, update, delete on all tables in schema public to {IMPORTER_ROLE};
grant usage, select on all sequences in schema public to {IMPORTER_ROLE};
"""


def _find_binary(name: str) -> str:
    """Locate a PostgreSQL binary from PATH or the Homebrew versioned kegs."""

    if found := shutil.which(name):
        return found
    for version in ("16", "15", "17"):
        candidate = Path(f"/opt/homebrew/opt/postgresql@{version}/bin/{name}")
        if candidate.is_file():
            return str(candidate)
    raise RuntimeError(
        f"PostgreSQL binary {name!r} is required for database tests but was not found"
    )


def _free_port() -> int:
    """Reserve and release a local TCP port for the disposable server."""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def require_local_database_url(url: str, label: str = "test database") -> None:
    """Refuse any configured test target that is not a local disposable server."""

    try:
        host = (urlsplit(url).hostname or "").lower()
    except ValueError:
        raise RuntimeError(f"{label} is not a valid PostgreSQL URL") from None
    if host not in LOCAL_HOSTS:
        raise RuntimeError(
            f"{label} must point at a local disposable PostgreSQL server; got host {host!r}"
        )


@dataclass(frozen=True)
class DatabaseTarget:
    """Connection details for one disposable test database."""

    cluster: "PostgresCluster"
    name: str

    @property
    def owner_url(self) -> str:
        return f"postgresql://postgres@127.0.0.1:{self.cluster.port}/{self.name}"

    @property
    def importer_url(self) -> str:
        return (
            f"postgresql://{IMPORTER_ROLE}:{TEST_ROLE_PASSWORD}"
            f"@127.0.0.1:{self.cluster.port}/{self.name}"
        )

    @property
    def reader_url(self) -> str:
        return (
            f"postgresql://{READER_ROLE}:{TEST_ROLE_PASSWORD}"
            f"@127.0.0.1:{self.cluster.port}/{self.name}"
        )

    @property
    def url(self) -> str:
        """Backward-compatible owner connection URL."""

        return self.owner_url

    def execute(self, sql: str) -> None:
        """Run SQL as the database owner and fail on any statement error."""

        result = subprocess.run(
            [
                self.cluster.psql,
                "-X",
                "-v",
                "ON_ERROR_STOP=1",
                "-d",
                self.owner_url,
                "-c",
                sql,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"SQL failed: {result.stderr.strip()}")


class PostgresCluster:
    """One temporary PostgreSQL server used by database-backed tests."""

    def __init__(self) -> None:
        self._initdb = _find_binary("initdb")
        self._pg_ctl = _find_binary("pg_ctl")
        self.psql = _find_binary("psql")
        self.port = _free_port()
        self._temp_dir = Path(
            os.environ.get("TMPDIR", "/tmp")
        ) / f"nus-catalog-pg-{uuid.uuid4().hex}"
        self._data_dir = self._temp_dir / "data"
        self._log_path = self._temp_dir / "postgres.log"
        self._cert_path = self._temp_dir / "server.crt"
        self._key_path = self._temp_dir / "server.key"
        self._started = False

    def start(self) -> None:
        """Initialize and start a local server with trust authentication."""

        self._temp_dir.mkdir(parents=True)
        self._write_tls_certificate()
        subprocess.run(
            [
                self._initdb,
                "-D",
                str(self._data_dir),
                "-U",
                "postgres",
                "--auth=trust",
                "--encoding=UTF8",
                "--no-locale",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self._start_server()

    def _start_server(self) -> None:
        """Start the initialized server with TLS on the reserved port."""

        subprocess.run(
            [
                self._pg_ctl,
                "-D",
                str(self._data_dir),
                "-l",
                str(self._log_path),
                "-o",
                (
                    f"-h 127.0.0.1 -p {self.port} -F -c ssl=on "
                    f"-c ssl_cert_file={self._cert_path} "
                    f"-c ssl_key_file={self._key_path}"
                ),
                "-w",
                "start",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self._started = True
        self._wait_until_ready()

    def pause(self) -> None:
        """Stop accepting connections without deleting the database files."""

        subprocess.run(
            [self._pg_ctl, "-D", str(self._data_dir), "-m", "fast", "-w", "stop"],
            check=True,
            capture_output=True,
            text=True,
        )
        self._started = False

    def resume(self) -> None:
        """Restart a paused server on the same port and data directory."""

        self._start_server()

    def _write_tls_certificate(self) -> None:
        """Create a throwaway certificate so the runtime can require TLS."""

        subprocess.run(
            [
                _find_binary("openssl"),
                "req",
                "-new",
                "-x509",
                "-days",
                "1",
                "-nodes",
                "-subj",
                "/CN=localhost",
                "-keyout",
                str(self._key_path),
                "-out",
                str(self._cert_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self._key_path.chmod(0o600)

    def stop(self) -> None:
        """Stop the server and remove its temporary data directory."""

        if self._started:
            subprocess.run(
                [self._pg_ctl, "-D", str(self._data_dir), "-m", "immediate", "-w", "stop"],
                check=False,
                capture_output=True,
                text=True,
            )
        shutil.rmtree(self._temp_dir, ignore_errors=True)

    def create_database(self) -> DatabaseTarget:
        """Create an empty database, apply every migration, and provision test roles."""

        database = DatabaseTarget(self, f"catalog_test_{uuid.uuid4().hex[:12]}")
        self._run_psql("postgres", f'create database "{database.name}"')
        for migration in MIGRATIONS:
            self._run_psql(database.name, None, migration)
        self._run_psql(database.name, ROLE_SETUP_SQL)
        return database

    def drop_database(self, database: DatabaseTarget) -> None:
        """Drop a test database, terminating any leftover pooled sessions."""

        self._run_psql(
            "postgres",
            f'drop database if exists "{database.name}" with (force)',
        )

    def _run_psql(self, database: str, sql: str | None, file: Path | None = None) -> None:
        command = [
            self.psql,
            "-X",
            "-v",
            "ON_ERROR_STOP=1",
            "-d",
            f"postgresql://postgres@127.0.0.1:{self.port}/{database}",
        ]
        command.extend(["-c", sql] if sql is not None else ["-f", str(file)])
        subprocess.run(command, check=True, capture_output=True, text=True)

    def _wait_until_ready(self) -> None:
        """Poll with psql until the new server accepts connections."""

        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            result = subprocess.run(
                [
                    self.psql,
                    "-X",
                    "-d",
                    f"postgresql://postgres@127.0.0.1:{self.port}/postgres",
                    "-c",
                    "select 1",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return
            time.sleep(0.1)
        raise RuntimeError("Disposable PostgreSQL server did not become ready")


@contextmanager
def disposable_database() -> Iterator[DatabaseTarget]:
    """Provide a migrated test database and remove it afterwards."""

    cluster = PostgresCluster()
    cluster.start()
    database = cluster.create_database()
    try:
        yield database
    finally:
        cluster.drop_database(database)
        cluster.stop()
