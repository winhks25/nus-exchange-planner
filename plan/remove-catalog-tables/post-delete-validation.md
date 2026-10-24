# Post-deletion API baseline comparison

Generated: 2026-10-24T11:21:13+00:00
Endpoint: `http://127.0.0.1:18770`
Baseline: `/Users/winhtutkhaungsoe/Desktop/nus-exchange-planner/plan/remove-catalog-tables/baseline-responses.json`
Baseline captured: 2026-10-23T14:42:17.452174+00:00
Requests: 41
Result: PASS

## Summary

- Differences: 0
- Request failures: 0

## Differences

No response differences.

## Request failures

None.

## T040 — comparator validation against a local fixture

Run on 2026-10-24 (Asia/Singapore) at source commit `c8e740b`, before any request
against the post-deletion database. The fixture was the disposable core-seeded
PostgreSQL runtime from `backend/scripts/serve_catalog_api.py`
(`http://127.0.0.1:18765`), which already reproduced the baseline in T023.

| Check | Command | Result |
| --- | --- | --- |
| Local comparison | `uv run python -m scripts.compare_api_baseline compare --base-url http://127.0.0.1:18765 --expected-origin http://127.0.0.1:18765 --timeout 10 --max-requests 200 --report /tmp/t040-local-compare.md` | exit 0 · 41 requests · 0 differences · 0 failures |
| Tamper detection | compare a copy with `catalog.body.degrees[0].name` changed to `Tampered Degree` | exit 1 · 1 difference · 6 derived-request failures |
| Baseline integrity | SHA-256 before and after both runs | `0f31a6e417ff4614464a95da578339a8c8c51b638f252a03d5f86a89b4ef7ee0` unchanged |

The utility never wrote to the expected baseline, refused redirects, and stayed
inside its request/timeout bounds. A failed comparison returns a nonzero status,
so a mismatch cannot pass silently.

## T041–T042 — post-deletion API comparison through localhost

Date: 2026-10-24 (Asia/Singapore). The comparison ran against a localhost uvicorn
runtime connected to the post-deletion Supabase project, not against the Vercel
origin (which is still returning the pre-existing 503; see
`recovery-validation.md`).

### Runtime under test

| Item | Value |
| --- | --- |
| Endpoint | `http://127.0.0.1:18770` |
| Command | `uv run uvicorn app.main:app --host 127.0.0.1 --port 18770` |
| Mode | `CATALOG_BACKEND=postgres` |
| Project | `wydziozsjibkvpgphpia` (PostgreSQL 17.11) |
| Applied migration | `20261024054553 remove_catalog_metadata` |
| Connection | Transaction pooler `:6543`, TLS required, prepared statements disabled |
| Pool | min 0 / max 4, connect timeout 10 s, statement timeout 8 s |
| Role | Temporary `catalog_verify_e14185b8` (operator-approved), member of `catalog_reader`, dropped after verification |

The `catalog_reader` password is only held in the Vercel environment, so the
operator approved a temporary LOGIN role with membership in `catalog_reader`
instead of rotating the real credential. Membership gives it exactly the
`catalog_reader` SELECT grants and RLS policies; it had no superuser,
`BYPASSRLS`, write, or DDL privilege. It is removed at the end of this phase.

### Result

`uv run python -m scripts.compare_api_baseline compare --base-url http://127.0.0.1:18770 --expected-origin http://127.0.0.1:18770 --timeout 20 --max-requests 200 --report plan/remove-catalog-tables/post-delete-validation.md`

**41 requests · 0 differences · 0 request failures · exit 0.**

| Request group | Count | Result | Checks |
| --- | ---: | --- | --- |
| Catalog | 1 | PASS | 6 degrees and 5 universities in source order, full degree titles |
| Recommendations | 6 | PASS | distinct-module ranking, `C`-collation tie order, partner counts, zero-count entries, NUS units=4 |
| Mappings | 30 | PASS | every degree/university pair, row order, repeated rows, verified partner units, row titles, null omission, count fields |
| Error cases | 4 | PASS | two missing-parameter `422` bodies and two unknown-selection `404` bodies |

All 30 mapping pairs include the three valid-empty cases
(`Artificial Intelligence / University of Western Australia`,
`Computer Science / University of Western Australia`,
`Computer Science / Yonsei University`), which returned `200` with zero rows.
Every tested request completed; missing or unavailable requests would have been
counted as failures by the utility.

Representative values matched `baseline-responses.json` exactly:

- `Artificial Intelligence` ranking: Toronto 10 mappings / 6 distinct NUS / 10 partner modules, Yonsei 4, Korea 2, Kyoto 1, UWA present at zero.
- `Artificial Intelligence / University of Toronto`: 10 rows, 6 distinct NUS modules, 10 mappable partner modules.
- `Computer Science / University of Toronto`: 7 rows, 3 distinct NUS modules, 7 mappable partner modules.

No expectation was regenerated from the implementation under test; the baseline
file was read-only throughout.

## T043 — retained core-data fingerprint after deletion

Date: 2026-10-24 (Asia/Singapore). The snapshot ran read-only under the temporary
verifier role (`catalog_verify_e14185b8`) through the transaction pooler.

### Reader-role capability checks

| Check | Result |
| --- | --- |
| SELECT on all eight retained tables | PASS — 6 degrees, 152 NUS modules, 226 degree modules, 5 universities, 142 partner modules, 19 specializations, 30 specialization modules, 151 mappings |
| `public.catalog_source_rows` | `UndefinedTable` — relation removed |
| `public.catalog_source_snapshots` | `UndefinedTable` — relation removed |
| `public.catalog_import_batches` | `UndefinedTable` — relation removed |
| `public.catalog_issues` | `UndefinedTable` — relation removed |
| `public.catalog_repairs` | `UndefinedTable` — relation removed |
| Migration history visible to the reader | No (no `supabase_migrations` usage). A temporary read grant on `schema_migrations` was issued only for the snapshot tool and removed with the role. |

No code path attempted to resolve a removed relation; each probe failed at the
catalog with `UndefinedTable` rather than returning data or falling back.

### Snapshot comparison

| Item | Value |
| --- | --- |
| Remote snapshot | `/tmp/remote_core_snapshot.json`, SHA-256 `9f48f627085168baded992e12d16ed34aa54d340f298331478225e5ff6112e88` |
| Rows read | 731 across the eight core tables |
| Target | `aws-0-ap-southeast-2.pooler.supabase.com/postgres`, project `wydziozsjibkvpgphpia`, PostgreSQL 17.11 |
| Migrations recorded | `20261022000100`, `20261022000200`, `20261022000300`, `20261024054553` |

**Against the reviewed core-seeded preview (production-equivalent, 151 mappings)**
— natural-key mode, all retained columns including specializations:

| Table | Rows | Missing | Extra | Result |
| --- | ---: | ---: | ---: | --- |
| `degrees` | 6 | 0 | 0 | PASS |
| `nus_modules` | 152 | 0 | 0 | PASS |
| `degree_modules` | 226 | 0 | 0 | PASS |
| `partner_universities` | 5 | 0 | 0 | PASS |
| `pu_modules` | 142 | 0 | 0 | PASS |
| `specializations` | 19 | 0 | 0 | PASS |
| `specialization_modules` | 30 | 0 | 0 | PASS |
| `module_mappings` | 151 | 0 | 0 | PASS |

**Against the frozen `backend/tests/fixtures/core_dataset.json`** the only
difference is the documented intentional duplicate: the fixture has 152 mapping
rows and the live database has the 151 production rows, so the fixture shows one
missing baseline row and zero extra rows. This is the expected fixture-only
duplicate (`CS3213` / `CITS3301`), not data loss.

### Identifier and sequence continuity

- `module_mappings.id` values remain contiguous `1..151`, matching the
  pre-removal `mapping-source-row-ids.csv` recovery capture (151 IDs, no gaps).
- The temporary reader cannot read sequence state (`pg_sequences.last_value` is
  null without sequence privilege), so sequences were checked read-only through
  the MCP connection as the owner. They are unchanged from T038:
  `degrees_id_seq`=6, `module_mappings_id_seq`=151,
  `partner_universities_id_seq`=5, `pu_modules_id_seq`=142,
  `specializations_id_seq`=19.

No retained row, column, identifier, or sequence state changed.
