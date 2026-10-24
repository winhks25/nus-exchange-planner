# Recovery procedure for catalog-metadata removal

Date: 2026-10-23 (Asia/Singapore). Scope: T007. This document specifies the
consistent export, local-restore rehearsal, and post-removal recovery choices.
T035 executes the export and restore gate; this document alone is not evidence
that a backup exists.

## Private backup location and retention

| Item | Value |
| --- | --- |
| `PRIVATE_BACKUP_DIR` | `/Users/winhtutkhaungsoe/Backups/nus-exchange-planner/catalog-removal-20261023` |
| Location check | Outside the Git worktree; repository root is `/Users/winhtutkhaungsoe/Desktop/nus-exchange-planner` |
| Directory permissions | `0700` for the backup root and session directory; backup files `0600` |
| Retention | Keep until T080 is complete and at least 90 days after the removal; keep a second encrypted copy on a separate device before deleting anything |
| Access | Operator-only; no backup content, password, or connection URL is committed to Git |

The backup directory is created empty by T007. T035 writes the export there.
A second copy must be made after the verified restore and must also stay outside
Git. Store the production database password in the operator's password manager
or a `~/.pgpass` file with mode `0600`, never in this directory or the repository.

## Export contents

| File | Purpose |
| --- | --- |
| `application.dump` | Single `pg_dump` custom-format snapshot of `public`: all thirteen tables, constraints, indexes, RLS policies, grants, functions, triggers, identity sequences, and data before deletion |
| `application.sql` | Plain-SQL rendering of the same custom dump for inspection and diffing; generated from the archive, not from a second database read |
| `roles.sql` | Production role definitions without passwords (`pg_dumpall --roles-only --no-role-passwords`) for reference |
| `local-roles.sql` | Minimal local-restore roles and `catalog_reader` settings needed by restored ACLs and policies |
| `mapping-source-row-ids.csv` | `module_mappings.id, source_row_id` for every mapping, ordered by mapping ID; the recovery key after the column is dropped |
| `table-counts.csv` | Row counts for the thirteen tables at the export boundary |
| `sequence-state.csv` | `pg_sequences` state for all ten public sequences at the export boundary |
| `manifest.json` | Redacted export metadata, file sizes, SHA-256 digests, counts, sequence values, target ref, and migration versions |
| `SHA256SUMS` | SHA-256 digest for every file except itself |

The custom dump is taken in one `pg_dump` invocation, so schema and data share
one database snapshot. `application.sql` is produced with `pg_restore --file`
from that archive. The CSVs and manifest are read while writes are quiesced, so
they describe the same boundary.

## Prerequisites

### Matching PostgreSQL client

The production server is PostgreSQL 17.11; the installed Homebrew client is
15.15 and is rejected by a 17 server. Install the matching client before T035:

```bash
brew install postgresql@17
export PATH="$(brew --prefix postgresql@17)/bin:$PATH"
pg_dump --version
```

`pg_dump --version` must report 17.x. Do not bypass the version check with an
unverified client.

### Connection settings without exposing secrets

Use the direct or session-mode Supabase connection (not the transaction pooler
on port 6543, which is unsuitable for dumps). Export connection details as
environment variables in the operator shell; never put them on a command line
that is logged.

```bash
export PGHOST="<direct-or-session-pooler-host>"
export PGPORT="5432"
export PGUSER="postgres"
export PGDATABASE="postgres"
export PGSSLMODE="require"
export PGPASSFILE="$HOME/.pgpass"
```

Create `~/.pgpass` with `chmod 600`; its line is
`host:port:postgres:postgres:<password>`. Confirm the target without printing
the password:

```bash
psql --no-psqlrc --set ON_ERROR_STOP=1 \
  --command "select current_database(), current_setting('server_version'), current_user"
```

Verify the linked project and migration versions with the read-only checks in
`deployment-results.md` before exporting.

### Operator tools

- `pg_dump`, `pg_restore`, `pg_dumpall`, `psql` 17.x on `PATH`.
- `shasum` (macOS) or `sha256sum` (Linux).
- `initdb`, `pg_ctl`, and `createdb` from the same PostgreSQL installation.
- Enough free space for two custom dumps plus one restore cluster. The current
  application data is small (well under 1 MB), but do not assume that remains
  true.

## Consistent export procedure

### 1. Quiesce writes

The production application uses `catalog_reader`, whose default transaction is
read-only. The retired importer and any direct Supabase edits are the only
writers. At the controlled boundary:

1. Announce the window and stop direct edits, SQL jobs, and imports.
2. Do not stop the public API; read traffic does not invalidate the snapshot.
3. Confirm no write transaction is active:

```bash
psql --no-psqlrc --set ON_ERROR_STOP=1 --command "
  select pid, usename, state, left(query, 80) as query
  from pg_stat_activity
  where datname = current_database()
    and pid <> pg_backend_pid()
    and state <> 'idle'
    and query ~* '(insert|update|delete|truncate|copy|alter|create|drop)'
"
```

The result must be empty. A read-only reporting query is fine. If a writer
appears, wait for it to finish or stop it deliberately; do not terminate sessions
blindly.

### 2. Capture the boundary CSVs

```bash
cd "$PRIVATE_BACKUP_DIR"
umask 077

psql --no-psqlrc --set ON_ERROR_STOP=1 --csv \
  --command "select id, source_row_id from public.module_mappings order by id" \
  > mapping-source-row-ids.csv

psql --no-psqlrc --set ON_ERROR_STOP=1 --csv --command "
  select 'catalog_import_batches' as table_name, count(*) as row_count from public.catalog_import_batches
  union all select 'catalog_source_snapshots', count(*) from public.catalog_source_snapshots
  union all select 'catalog_source_rows', count(*) from public.catalog_source_rows
  union all select 'catalog_issues', count(*) from public.catalog_issues
  union all select 'catalog_repairs', count(*) from public.catalog_repairs
  union all select 'degrees', count(*) from public.degrees
  union all select 'nus_modules', count(*) from public.nus_modules
  union all select 'degree_modules', count(*) from public.degree_modules
  union all select 'specializations', count(*) from public.specializations
  union all select 'specialization_modules', count(*) from public.specialization_modules
  union all select 'partner_universities', count(*) from public.partner_universities
  union all select 'pu_modules', count(*) from public.pu_modules
  union all select 'module_mappings', count(*) from public.module_mappings
  order by table_name" > table-counts.csv

psql --no-psqlrc --set ON_ERROR_STOP=1 --csv \
  --command "select sequencename, last_value from pg_sequences where schemaname = 'public' order by sequencename" \
  > sequence-state.csv
```

`mapping-source-row-ids.csv` must contain 151 data rows at the current boundary.
A different count is valid only if it matches `table-counts.csv`.

### 3. Dump schema and data once

```bash
pg_dump --format=custom --schema=public \
  --file "$PRIVATE_BACKUP_DIR/application.dump"

pg_dumpall --roles-only --no-role-passwords \
  --file "$PRIVATE_BACKUP_DIR/roles.sql"

pg_restore --format=custom \
  --file "$PRIVATE_BACKUP_DIR/application.sql" \
  "$PRIVATE_BACKUP_DIR/application.dump"
```

Do not add `--data-only`, `--clean`, or `--if-exists` to the production dump.
The archive is the recovery artifact; `application.sql` is only a readable
rendering. `--schema=public` intentionally excludes Supabase-managed schemas.

### 4. Recheck quiescence and write the manifest

Immediately rerun the count and sequence queries into temporary files and diff
them against the boundary CSVs. Any difference invalidates the export; delete
the incomplete files and repeat from the quiescence step.

```bash
shasum -a 256 application.dump application.sql roles.sql local-roles.sql \
  mapping-source-row-ids.csv table-counts.csv sequence-state.csv \
  > SHA256SUMS
```

`manifest.json` records at least:

- export timestamp with timezone;
- project ref `wydziozsjibkvpgphpia` and PostgreSQL version;
- migration versions `20261022000100`-`20261022000300`;
- every file name, byte size, and SHA-256 digest;
- the row counts and sequence values above;
- the mapping-pair row count;
- role names only, never passwords or connection strings.

The manifest must not contain the database URL, password, pooler host with
credentials, or any user secret. `roles.sql` contains role definitions, not
passwords, because `--no-role-passwords` is used.

## Local restore rehearsal

A backup is not accepted until this restore succeeds on an isolated local
cluster. Never restore into the repository's development database or any remote
target.

### 1. Start an isolated cluster

```bash
RESTORE_ROOT="$(mktemp -d /tmp/nus-catalog-restore.XXXXXX)"
initdb -D "$RESTORE_ROOT/data" -U postgres --auth=trust --no-locale --encoding=UTF8
pg_ctl -D "$RESTORE_ROOT/data" \
  -o "-p 55432 -c listen_addresses=127.0.0.1" -w start
createdb -h 127.0.0.1 -p 55432 -U postgres restore_check
```

The `/tmp` cluster is disposable and must be stopped and removed after
verification. Local trust authentication means no local password is written to
disk; `catalog_reader` is created with `LOGIN` for the API check but receives no
stored password.

### 2. Create roles required by restored ACLs

`local-roles.sql` must create only the roles the dump references:

```sql
do $$
begin
  if not exists (select 1 from pg_roles where rolname = 'anon') then
    create role anon nologin;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'authenticated') then
    create role authenticated nologin;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'service_role') then
    create role service_role nologin bypassrls;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'catalog_reader') then
    create role catalog_reader login nosuperuser nocreatedb nocreaterole
      noreplication nobypassrls;
  end if;
end
$$;

alter role catalog_reader set statement_timeout = '5s';
alter role catalog_reader set idle_in_transaction_session_timeout = '5s';
alter role catalog_reader set default_transaction_read_only = on;
```

The local cluster's `postgres` role already exists and owns the restore. Do not
restore the full production `roles.sql` into a local cluster; it contains
platform roles and may conflict with the bootstrap superuser. Keep it only as a
record of production roles.

### 3. Restore the archive

```bash
psql -h 127.0.0.1 -p 55432 -U postgres -d restore_check \
  --set ON_ERROR_STOP=1 --file "$PRIVATE_BACKUP_DIR/local-roles.sql"

pg_restore -h 127.0.0.1 -p 55432 -U postgres -d restore_check \
  --single-transaction --exit-on-error --disable-triggers \
  "$PRIVATE_BACKUP_DIR/application.dump"
```

`--disable-triggers` requires the local superuser and prevents foreign-key and
archive triggers from rejecting data during load. Do not use it against
production. The archive restores the schema, all thirteen tables, data,
constraints, indexes, policies, grants, the archive function and triggers, and
sequence values.

### 4. Prove the restore is usable

Run all of the following against `restore_check`:

1. Compare table counts with `table-counts.csv`; every count must match.
2. Re-export mapping pairs and diff them:

   ```bash
   psql -h 127.0.0.1 -p 55432 -U postgres -d restore_check \
     --no-psqlrc --set ON_ERROR_STOP=1 --csv \
     --command "select id, source_row_id from public.module_mappings order by id" \
     > /tmp/restored-mapping-source-row-ids.csv
   diff -u "$PRIVATE_BACKUP_DIR/mapping-source-row-ids.csv" \
     /tmp/restored-mapping-source-row-ids.csv
   ```

3. Compare sequence values with `sequence-state.csv`; `last_value` must match
   for all ten sequences.
4. Confirm the five metadata tables and `source_row_id` exist, all eight core
   tables exist, the four archive triggers exist, and `catalog_import_batches`
   has its `catalog_reader` SELECT policy.
5. As `catalog_reader`, select one row from each core table and
   `catalog_import_batches`; confirm `INSERT`, `UPDATE`, and `DELETE` are denied
   by `default_transaction_read_only` and the absence of write grants. Do not
   attempt a write as `postgres` for this check.
6. Optionally start the compatible backend with a local `DATABASE_URL` for
   `catalog_reader` and compare its responses with
   `plan/remove-catalog-tables/baseline-responses.json` using
   `backend/scripts/compare_api_baseline.py`. A local restore that serves the
   same responses is stronger evidence than row counts alone.

Pass criteria: restore exits 0, counts and mapping pairs match, sequence values
match, metadata objects are present, core policies/grants are intact, and the
reader has no write path. A file that merely exists does not pass this gate.

### 5. Clean up

```bash
pg_ctl -D "$RESTORE_ROOT/data" -m fast -w stop
rm -rf "$RESTORE_ROOT"
```

Record the restore command, exit status, counts, mapping-pair diff, sequence
comparison, and any limitation in `recovery-validation.md` (T035).

## Post-removal recovery choices

The compatible backend from US1 does not query any metadata table. Use these
choices in order; do not restore production tables merely to recover a frontend
or runtime defect.

### 1. Keep or redeploy the compatible backend

The preferred recovery is to keep the US1-compatible deployment running. If a
later deployment regresses, redeploy the last tested compatible commit. No
database restore is needed. This preserves the cleaned schema and current core
data.

### 2. Explicit JSON fallback

Set `CATALOG_BACKEND=json` in the backend project, remove `DATABASE_URL`, and
redeploy the backend. The API then serves the frozen checked-in snapshot with no
database connection. Limitations:

- The JSON snapshot has 147 mapping rows; the PostgreSQL branch has 151.
- Four Toronto pairs differ from the repaired database: Artificial Intelligence
  9 vs 10, Business Analytics 18 vs 19, Computer Science 6 vs 7, Information
  Security 7 vs 8.
- JSON mode does not undo database changes and cannot restore deleted
  metadata. It is a service fallback, not a data restore.
- Returning to PostgreSQL requires restoring the server-only `DATABASE_URL` and
  redeploying; this works without the retired importer or metadata tables.

### 3. Restore metadata for an old PostgreSQL runtime

Only a pre-US1 backend that queries `catalog_import_batches` requires this path.
The compatible runtime must not be rolled back to that older code.

1. Restore only the five metadata tables, their indexes, policies, grants,
   triggers, and `reject_catalog_archive_mutation()` from `application.dump`.
   Do not restore the eight core tables, because they may contain post-export
   edits.
2. Re-add `module_mappings.source_row_id`, its unique key, and its foreign key.
3. Backfill `source_row_id` by joining the restored mapping IDs to
   `mapping-source-row-ids.csv`. Never invent a value for a mapping created after
   the export; leave it null and record it.
4. Verify the old runtime's batch marker query returns exactly one completed
   current batch and that `catalog_reader` can select only the intended tables.
5. If the restore is into production, review every post-export edit first. A
   full `application.dump` restore would overwrite newer core data and is not an
   acceptable default.

## Edits made after the export

The export is bound to a quiesced timestamp. Before any real restore:

1. Take a fresh read-only snapshot of current production counts, mapping IDs,
   and sequence values.
2. Compare it with the manifest and `mapping-source-row-ids.csv`.
3. If only new mappings exist, preserve them and backfill source links only for
   IDs present in the CSV.
4. If core rows changed, prefer targeted inserts/updates by natural key. If a
   full restore is unavoidable, capture a new export at a new controlled
   boundary, verify it, and obtain explicit operator approval for overwriting
   post-export edits.
5. Never treat the original baseline responses as current after a legitimate
   data edit; capture a new versioned baseline for verification.

## Recovery evidence to record (T035/T039)

- `PRIVATE_BACKUP_DIR` path and permissions, without secrets.
- Export start/end timestamps and the quiescence check output.
- File names, sizes, and SHA-256 digests; manifest digest.
- Local restore command and exit status.
- Table-count comparison, mapping-pair diff, sequence comparison.
- Metadata/core object existence and reader privilege checks.
- The chosen post-removal recovery path and any limitation found.

## Execution status (2026-10-24)

The full export and restore rehearsal were **not** executed: the operator chose
the Supabase MCP apply path, skipping the recoverable-backup prerequisite. A
minimal data-only capture (the `source_row_id` mapping, sequence state, and a
manifest) was written to `PRIVATE_BACKUP_DIR` before the apply. The post-removal
recovery choice is **choice 1 (keep the compatible core-readiness runtime)** — no
restore or redeploy is required. See `recovery-validation.md` for the capture
digests and the resulting limitations.
