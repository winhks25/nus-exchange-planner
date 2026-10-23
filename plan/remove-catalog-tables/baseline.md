# Baseline and starting state

Date: 2026-10-23 (Asia/Singapore). Scope: Phase 1 setup and scope verification.

## Starting repository state (T001)

| Item | Value |
| --- | --- |
| Branch | `master` |
| Starting commit | `32833566669e88b89062b1c27e265d5657681a60` (`docs: record final migration validation (T040)`) |
| Tracked working tree | Clean; no staged or unstaged tracked changes |
| Unrelated untracked files | `.agents/`, `skills-lock.json` |
| Feature planning files | `plan/remove-catalog-tables/` (untracked at start) |
| Ignored local files present | `.env.local`, `backend/.env`, `.vercel/`, caches |

The untracked skill assets are user-owned inputs from the Supabase skill install and
are preserved unchanged. No tracked or staged user work was present, so Phase 1
does not need to stash or selectively stage around unrelated edits.

## Inputs read

- `plan/remove-catalog-tables/spec.md`, `plan.md`, `data-model.md`, and `tasks.md`
- `frontend/AGENTS.md` and the repository Supabase skill at `.agents/skills/supabase/SKILL.md`
- `plan/contracts/openapi.yaml`, current runtime repository, settings, and related tests
- Historical planning and deployment evidence under `plan/supabase-migration/`

No repository-level `AGENTS.md` exists outside `frontend/AGENTS.md`. The
`.specify/` directory, setup script, constitution, and hook registry are absent,
matching the planning note in `tasks.md`. No pre- or post-implementation hooks
are registered.

## Supabase guidance and CLI

Current guidance consulted on 2026-10-23:

- <https://supabase.com/docs/guides/platform/backups>
- <https://supabase.com/docs/guides/local-development/restoring-downloaded-backup>
- <https://supabase.com/docs/guides/platform/migrating-within-supabase/backup-restore>
- <https://supabase.com/docs/reference/cli/supabase-db-dump>

The `supabase` binary is not installed on `PATH`. CLI help was inspected through
`npx --yes supabase@latest` (version `2.121.0`):

- `supabase migration --help` exposes `list`, `new`, `repair`, and `up`.
- `supabase db dump --help` supports `--linked`, `--schema`, `--data-only`, and
  `--file`; the default dump includes schema and data.
- `supabase db push --help` supports `--dry-run`, `--linked`, and
  `--include-all`; `--dry-run` is the supported pending-migration preview.
- `supabase migration list --help` supports `--linked` and `--project-ref`.

The linked CLI call could not authenticate because no access token or login
session is available. Remote verification therefore used the configured Supabase
MCP connection and read-only SQL instead; no secret value was printed.

## Execution constraints carried into later tasks

- Production must not be mutated in Phase 1. All database inspection was read-only.
- The linked project must be re-checked at the change boundary because the current
  deployment record does not tie its Vercel deployment to a source commit.
- Local disposable PostgreSQL and Playwright dependencies are present; see the
  baseline checks section appended by T005.
- No operational command may depend on the five metadata tables after the removal
  migration is applied.
