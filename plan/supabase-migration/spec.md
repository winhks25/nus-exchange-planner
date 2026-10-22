# Supabase catalog migration

Date: 2026-10-22. Status: planning; implementation not started.

## Confirmed scope

Preserve existing pages and API behavior. Research official sources to repair missing
or invalid source data. Select PostgreSQL explicitly, retaining JSON as a manual
rollback mode; never silently fall back on a database error. Import all existing
source information, including raw records that cannot safely become active mappings.
Pagination, specialization UI, new curricula, and a general data administration UI
are deferred. Existing eight-table Supabase schema has been applied manually.

## User stories

### US1 — Complete, traceable data import (P1)

As a maintainer, I can import the checked-in dataset into Supabase repeatedly without
losing source information, duplicating records, or publishing unverified corrections.

Acceptance: archive each source file and checksum; account for all 154 raw mapping
rows; identify the seven rows rejected by the legacy parser separately from the
seven missing course-title occurrences (these are not necessarily the same rows).
Research official NUS/partner sources, record exact citations and evidence for
repairs, and retain unresolved entries as explicit issues. A matching course title
alone does not prove exchange equivalence. No unverified mapping becomes active.
Missing titles may remain null if research fails; preserve the row if its code and
mapping are otherwise valid. Import source-listed specializations and CS focus-area
names, distinguish their kinds, and leave unknown memberships empty with an issue.
Do not infer that every course in a choice group is compulsory.

The baseline has six degrees and five universities. Establish final accepted counts
from the repair report, not a hardcoded expectation of 147 valid mappings. All
remaining metadata, notes, curriculum rules, and source URLs remain in the archive.
Unresolved data issues must be reported; do not claim that all records were repaired.

### US2 — Database-backed API with unchanged behavior (P1)

As a student, I can use the current selectors, recommendations, and mappings pages
against PostgreSQL without changing routes or interaction patterns.

Acceptance: preserve plan/contracts/openapi.yaml response shapes, missing-parameter
422s, unknown-selection 404s, valid-empty results, and unavailable-service 503s.
Catalog order, university tie-breaking, repeated mapping rows, optional title/unit
serialization, and stable ordering of equal NUS codes match the JSON implementation.
Rank all universities, including zero-count universities, by distinct NUS module
count descending then university name. Partner counts remain case-insensitive.
Keep displayed NUS units at 4 for compatibility; store verified actual units without
silently changing the existing API's policy. Verified repairs may change titles,
counts, and rankings only as documented in the data-delta report.

### US3 — Controlled deployment and rollback (P2)

As the operator, I can deploy database mode, diagnose failures without leaking
credentials, and explicitly restore JSON mode with a known dataset version.

Acceptance: CATALOG_BACKEND=json|postgres is explicit; omitted mode defaults to
json during migration, unknown mode fails configuration validation. PostgreSQL mode
requires a valid DATABASE_URL. Missing/malformed settings fail clearly; operational
database failures return 503 and do not load JSON. Local JSON mode works with no
database credentials. Runtime uses a read-only database role; imports/migrations
use separate privileged credentials. Verify a complete import before deployment.

## Verification policy

Use existing automated checks plus a reproducible import/endpoint comparison command
and recorded acceptance exercises. The user additionally requested a dedicated
regression phase: add automated import, repository parity, failure/access-control
and browser tests against isolated PostgreSQL and JSON. Require these to pass before
production deployment; no TDD ordering is mandated. Any updated existing assertions must distinguish verified data changes from
behavior regressions. No production mutations are part of this planning task.
