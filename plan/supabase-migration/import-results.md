# Supabase catalog import results (T018)

Generated: 2026-10-22

## Scope

Phase 3 publishes the reviewed catalog snapshot into the empty Supabase project
`wydziozsjibkvpgphpia`. The application continues to run from JSON; this task records
catalog storage and reconciliation only.

## Target

- Supabase project ref: `wydziozsjibkvpgphpia`
- Host: `aws-0-ap-southeast-2.pooler.supabase.com`
- Database: `postgres`
- Port: `6543` (transaction pooler)
- PostgreSQL: `17.11`
- Migrations: all three reviewed migrations applied

The transaction pooler was used because the session pooler on port `5432` timed out
during preparation. Credentials were supplied through `IMPORT_DATABASE_URL` and are
not recorded here.

## Source snapshot

- Source checksum: `b393cd0f6b34adb506a23ba810d65c083238339fab0b76a236167fdbef6901b9`
- Repair checksum: `61268be6b39c1effc644d72c8cc4787287cdbcafc86d32fb3c48814d48064a3e`
- Academic year: `AY2026/27`
- Prepared on: `2026-10-22`
- Archived files: 8 (manifest, majors, five mapping files, repairs)

## Published batch

- Batch id: `1`
- Status: `completed`
- Current: `true`
- Started: `2026-10-22T10:01:15.611850+00:00`
- Completed: `2026-10-22T10:01:15.611850+00:00`
- Raw source rows: `154`
- Accepted rows: `146`
- Repaired rows: `5`
- Quarantined rows: `3`

The batch marker was committed in the same transaction as every catalog row, archive,
issue and repair.

## Published counts

| Table | Rows |
| --- | ---: |
| `degrees` | 6 |
| `nus_modules` | 152 |
| `degree_modules` | 226 |
| `specializations` | 19 |
| `specialization_modules` | 30 |
| `partner_universities` | 5 |
| `pu_modules` | 142 |
| `module_mappings` | 151 |
| `catalog_source_snapshots` | 8 |
| `catalog_source_rows` | 154 |
| `catalog_issues` | 34 |
| `catalog_repairs` | 44 |

Source-row outcomes: `accepted=146`, `repaired=5`, `quarantined=3`.

## Retained issues

Issue status totals: `open=16`, `resolved=9`, `quarantined=9`.

| Issue code | Rows |
| --- | ---: |
| `focus_area_memberships_missing` | 10 |
| `invalid_nus_code` | 7 |
| `missing_nus_title` | 7 |
| `partner_unit_conflict` | 1 |
| `specialization_memberships_missing` | 6 |
| `unresolved_repair` | 3 |

The six membership-note issues retain their source notes in the issue message. The
three quarantined rows are all in `data/mapping/canada/toronto.json`:

| Source row | Raw NUS code | Reason |
| ---: | --- | --- |
| 48 | `Software Engineering` | unresolved code/title repair |
| 49 | `Discrete Structures` | unresolved code/title repair |
| 53 | `Programming Methodology` | unresolved code/title repair |

These rows remain in `catalog_source_rows` with `outcome='quarantined'`; they are not
normalized into `module_mappings` and are not silently discarded. The 20 unresolved
repair evidence rows cover six field pointers across those three mapping rows.

## Reconciliation

Command shape:

```bash
uv run --directory backend python -m scripts.verify_catalog \
  --reconcile --target-project-ref wydziozsjibkvpgphpia
```

Result: **19/19 checks passed** at `2026-10-22T10:04:14.212256+00:00`.

| Check | Records | Digest |
| --- | ---: | --- |
| Archived source snapshots | 8 | `775fec03936a118049194af514afb820a63ff374435023a547899d0f0d1449f9` |
| Catalog source rows | 154 | `6cf9a0998bc7bd8fc852e641ff38912f8cd9e7cf0fbc1a98fe0a27f2ca4f50a9` |
| Module mappings | 151 | `d1653896e8d8a03ed6498dc3370aefb42ba5c29d7752e98c67f7b56106f4c7bb` |
| Catalog issues | 34 | `d7e6c0a2f14135978347062532175cb726510c10620697ec5a25586d03573cb3` |
| Catalog repairs | 44 | `2b6b4bf47f2410b196d05a8acf13cb7fb00b76765ca73713d7c889f271db585e` |

Entity and link checks also matched exactly: 6 degrees, 152 NUS modules, 226 degree
memberships, 5 partner universities, 142 partner modules, 19 specializations and 30
specialization memberships. Referential-integrity checks found zero orphaned mappings,
source rows, issues or repairs. Duplicate multiplicity matched for partner codes
(8 duplicate groups / 17 rows), NUS codes (30 groups / 77 rows) and exact pairs
(0 duplicate groups / 151 rows).

## Isolated PostgreSQL exercise

A disposable local PostgreSQL cluster was migrated from the checked-in SQL and
exercised through the same CLI entry points with `--target-project-ref local`:

| Step | Result |
| --- | --- |
| Dry-run | exit 0, `would_import`, zero existing rows |
| Initial import | exit 0, `imported`, batch `1` |
| Identical rerun | exit 0, `noop`, batch remained `1` |
| Reconciliation | exit 0, 19/19 checks passed |
| Injected mid-import failure | exit 1, `rolled_back`, all 13 table counts `0` |
| Reconcile failed database | exit 1, missing publication marker detected |

The injected failure exercised `--simulate-failure` on a fresh database and proved the
single transaction left no partial batch, archive rows, entities, mappings, issues or
repairs behind.

## Safeguards exercised

- `--dry-run` is the default; publishing requires explicit `--apply`.
- Remote applies require both `--target-project-ref` and a matching
  `--confirm-project-ref`.
- Publishing takes an advisory transaction lock and uses one transaction for the batch
  marker, archives, rows, entities, mappings and provenance.
- An identical source+repair checksum is a no-op.
- A different or partial published catalog is refused; no table is truncated.
- The reconciliation pass is read-only and emits a sanitized JSON report.

## Limitations and next steps

- The application still uses JSON; Phase 4 PostgreSQL-backed API work is not part of
  this result.
- The importer used an owner credential through the transaction pooler. The
  least-privilege runtime role remains to be exercised with the API in Phase 4.
- Three quarantined rows and their unresolved repairs remain intentionally unresolved;
  they require reviewed source evidence before they can become mappings.
- API and performance validation against the target project remain in later tasks.
