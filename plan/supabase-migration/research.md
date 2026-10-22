# Connection and migration research

Researched: 2026-10-22
Scope: Supabase connection modes, Psycopg 3 pool/TLS behavior, and migration
history repair. This file records the decisions that T004-T009 must implement.
It does not contain credentials or project passwords.

## Sources

| Source | Used for |
|---|---|
| [Supabase: Connect to your database](https://supabase.com/docs/guides/database/connecting-to-postgres) | Direct, session-pooler, transaction-pooler endpoints; serverless guidance; TLS; client settings |
| [Supabase: Disabling prepared statements](https://supabase.com/docs/guides/troubleshooting/disabling-prepared-statements-qL8lEL) | Psycopg `prepare_threshold=None` under transaction mode |
| [Psycopg 3: Connection pools](https://www.psycopg.org/psycopg3/docs/advanced/pool.html) | Pool lifecycle, `open=False`, `wait()`, `connection()` transaction behavior, `check_connection` |
| [Psycopg 3: `psycopg_pool` API](https://www.psycopg.org/psycopg3/docs/api/pool.html) | `min_size`, `max_size`, `timeout`, `max_waiting`, `max_lifetime`, `max_idle`, `close()` |
| [Psycopg 3: Connection classes](https://www.psycopg.org/psycopg3/docs/api/connections.html) | `prepare_threshold`, `connect_timeout`, `read_only`, transaction methods |
| [Supabase CLI: migration repair](https://supabase.com/docs/reference/cli/supabase-migration-repair) | `--status applied` history repair without running SQL |
| [Supabase CLI: db push](https://supabase.com/docs/reference/cli/supabase-db-push) | First-run history table and pending-migration behavior |
| [Supabase CLI: migration list](https://supabase.com/docs/reference/cli/supabase-migration-list) | Local/remote history comparison |
| PyPI package metadata | Current `psycopg` and `psycopg-pool` versions and Python floors |

## Decisions

### 1. Use the transaction pooler for runtime traffic

The backend runs as a serverless FastAPI deployment on Vercel. Supabase's
guidance for serverless functions is the shared pooler in transaction mode on
port `6543`, not a direct connection.

Runtime connection shape:

```text
postgresql://[RUNTIME-ROLE].[PROJECT-REF]:[PASSWORD]@[POOLER-HOST]:6543/postgres
```

The host must be copied from the project's Connect dialog; it cannot be derived
from the project ref or region. The runtime role is not `postgres`; T008 creates
a dedicated read-only role. Direct connections and the dedicated pooler use
`postgres`, while shared-pooler usernames are `[ROLE].[PROJECT-REF]`.

### 2. Disable prepared statements in transaction mode

Supabase transaction mode does not support prepared statements, query pipelining,
or session state that outlives a transaction. The Psycopg setting is
`prepare_threshold=None` on every pooled connection.

Consequences for the repository code:

- Use one parameterized statement per short transaction, not `PREPARE`.
- Do not use `withhold` cursors, temporary tables, `SET` that must persist,
  `LISTEN`/`NOTIFY`, or session-level advisory locks on runtime connections.
- Do not enable Psycopg pipeline mode on the runtime pool.
- Import code may use a direct connection, where prepared statements and session
  state are supported.

### 3. Enforce TLS

Set `sslmode=require` on both runtime and import connections so the driver
refuses plaintext. This encrypts the connection but, per Supabase's docs, does
not verify the server certificate. The follow-up hardening is `sslmode=verify-full`
with the project's downloaded root certificate and `sslrootcert`. That requires
shipping a public CA file or mounting it in the deployment; it is not part of the
first implementation.

### 4. Bound the synchronous pool

The API handlers are synchronous, so the implementation uses
`psycopg_pool.ConnectionPool`, not the async pool. The pool is created with
`open=False` and opened in the FastAPI lifespan, never at module import. This
matches Psycopg's guidance and keeps import-time network access out of the app.

Provisional runtime settings, to be validated in T006:

| Setting | Value | Reason |
|---|---:|---|
| `min_size` | 0 | A cold serverless instance should not hold idle connections |
| `max_size` | 1 by default, override up to 10 | Supabase recommends one connection per serverless instance; the override supports local/persistent use |
| `timeout` | 5 s | Bound request time spent waiting for a pooled connection |
| `max_waiting` | 16 | Reject excess queueing instead of piling up requests |
| `max_lifetime` | 1800 s | Recycle connections before long-lived pooler churn |
| `max_idle` | 300 s | Release connections above the minimum |
| `check` | `ConnectionPool.check_connection` | Detect a connection lost while idle |
| pool `close()` timeout | 5 s | Bound shutdown |
| `connect_timeout` | 5 s | Bound TCP/TLS/authentication setup |
| `statement_timeout` | 5 s | Bound a single catalog query |
| `idle_in_transaction_session_timeout` | 5 s | Prevent an abandoned read transaction from holding a connection |

Use `conn.read_only = True` for runtime transactions. Call `pool.wait()` during
startup with a short timeout only if the deployment should fail fast; a transient
outage must still surface as a request-time 503, not a process crash.

### 5. Keep runtime and import credentials separate

| Purpose | Connection | Role | Privileges |
|---|---|---|---|
| API runtime | Shared transaction pooler, port 6543 | `catalog_reader` (T008) | `USAGE` on `public`; `SELECT` only on catalog tables; no raw archives, issues, or writes |
| Migrations and imports | Direct connection, port 5432, or session pooler on IPv4-only networks | Migration owner and `catalog_importer` | DDL and import writes; never exposed to the runtime |

The importer uses a direct connection so advisory locks, multi-statement
transactions, and session settings behave normally. It must not share the runtime
password. Passwords are provisioned outside migrations and are never committed.

### 6. Repair migration history instead of replaying DDL

The initial migration was applied through the SQL Editor, which does not insert a
row into `supabase_migrations.schema_migrations`. The safe order is:

```bash
# Link once, then compare local files with remote history.
npx supabase link --project-ref wydziozsjibkvpgphpia
npx supabase migration list

# After the remote schema is verified equivalent to the local file, insert the
# missing history row. This does not execute the migration SQL.
npx supabase migration repair 20261022000100 --status applied

# Confirm the histories now agree before the next db push.
npx supabase migration list
```

`supabase db push` creates `supabase_migrations.schema_migrations` on its first
run and skips versions already recorded. It must not run before the history row is
repaired, because it would treat `20261022000100` as pending and try to replay
`CREATE TABLE` statements against the existing schema. This is also why T002 stays
blocked until remote access is available.

### 7. Sanitize database failures

Catch `psycopg.Error`, `psycopg_pool.PoolTimeout`, `PoolClosed`, and
`TooManyRequests` at the repository boundary. Log the exception class and a short
operation label, never the conninfo, username, password, or full SQL parameters.
Return the existing 503 shape with a generic message. A database failure must
never select the JSON adapter.

### 8. Package versions

Checked on PyPI on 2026-10-22:

| Package | Current version | Python floor | Decision |
|---|---|---|---|
| `psycopg` | 3.3.6 | >=3.10 | Pin 3.3.6 |
| `psycopg-binary` | 3.3.6 | >=3.10 | Pin 3.3.6 through the `binary` extra |
| `psycopg-pool` | 3.3.3 | >=3.10 | Pin 3.3.3 explicitly; the `pool` extra does not pin it |
| Supabase CLI | 2.121.0 | - | Use `npx supabase@latest` during operations |

The project already requires Python 3.12, so both floors are satisfied. T004
should declare `psycopg[binary,pool]==3.3.6` plus `psycopg-pool==3.3.3` (or an
equivalent lock-file pin) so a fresh install and the existing venv resolve the
same versions. `requirements.txt` must match.

## Open issues

- The project is not linked and no access token or database password is present;
  remote schema and history verification is blocked.
- The runtime pooler host must be copied from the Connect dialog; it is not
  recorded here.
- `sslmode=require` is encrypted but not certificate-verified. Upgrading to
  `verify-full` needs a CA file and a deployment mount.
- Pool size and timeouts above are starting values. T027 must measure contention
  and latency before production deployment.
