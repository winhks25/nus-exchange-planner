# Implementation decisions — exchange planner enhancements

Date: 2026-10-25 (T003). Each decision cites its authority: a confirmed
observation from the deployed data (baseline.md), an explicit default from
spec.md, or a planning assumption that still needs confirmation.

## Migration and backfill

1. **Additive nullable `nus_modules.faculty_id` foreign key** (confirmed
   approach). The deployed `nus_modules` table has the legacy `faculty` text
   column; the new `faculty_id bigint REFERENCES faculties(id)` is nullable so
   no existing row is forced to change before it is resolved. The legacy text
   is retained until its readers migrate, per the spec default.
2. **Degree membership is explicit, never derived** (spec default).
   `degree_faculties` rows are the only degree–faculty source. Membership is
   not inferred from the faculties that offer a degree's modules; the October
   25 cleanup set every module's faculty to `School of Computing`, which would
   make derived membership meaningless.
3. **No academic year or semester anywhere** (DB-02). Neither
   `faculty_partner_universities` nor any other new relation models time.
4. **Audited alias backfill** (T004–T005, T008). Legacy labels are mapped to
   canonical faculties through the reviewed `data/exchange-enhancements/
   faculty-aliases.json`. A label with no reviewed alias leaves
   `faculty_id` null and keeps its legacy text. Confirmed at baseline: the
   only label present in `degrees.faculty`, `nus_modules.faculty`, and the
   frozen JSON sources is `School of Computing`, so the first backfill
   resolves every row and leaves none unknown — the null path is still
   implemented for future data.
5. **Contract-driven column extension** (assumption, recorded for review).
   T006's list names `partner_universities.image` and `website`; the T002
   contract also carries *optional* image attribution, and US4 (T039) must
   render required attribution on each card. The catalog is the frontend's
   only data path, so the migration adds one further nullable
   `partner_universities.image_attribution text` column (nonblank check,
   seeded from the reviewed US4 manifest in T038). It is null until US4
   populates it and does not affect any existing query.
6. **Migration naming and application channel** (operational). The file is
   generated with `npx supabase@latest migration new exchange_enhancements`
   so the timestamp is CLI-produced, then filled in the repository. The
   pooler is unreachable from this machine and the live migration history
   has the `remove_catalog_metadata` version drift recorded in baseline.md,
   so `db push` cannot be used; the migration and the backfill are applied
   through the Supabase MCP channel (which reaches the database) inside
   transactions, then re-verified read-only. Repairing the drift with
   `supabase migration repair` is deferred to a session where the CLI can
   authenticate.

## Unknown-data handling

7. **Unknown module faculty stays null** (spec default). The backfill never
   invents a faculty for an unresolved label; the module stays readable
   through its legacy text until a reviewed alias exists.
8. **Missing geography stays null and is never inferred** (spec default).
   `city`/`continent` absence means unknown; a university with a null value
   in a category matches only when that category is unrestricted (FR-11
   semantics). Confirmed at baseline: all five universities currently have
   both values, so the null path is exercised only by future data.
9. **Unknown availability stays unknown** (spec default, DB-02). Phase 2
   creates `faculty_partner_universities` empty. No links are created from
   mapping existence. US3 (T026) adds only verified links, expanding
   university-wide agreements explicitly.
10. **Missing media and websites stay null** (DB-03). Phase 2 leaves
    `image`/`website`/`image_attribution` null; US4 (T034–T039) fills them
    from reviewed, rights-cleared sources only.

## Unresolved decision — no-degree navigation (FR-20)

11. **Status: unresolved, pending product confirmation.** The mappings API
    requires a degree, but a directory card click may arrive without one.
    Proposed default (from spec.md): preselect the university, prompt for a
    degree, and load mappings automatically once the user chooses one. The
    application must not silently choose a degree and no all-degrees endpoint
    is added. This is an explicit exception to unconditional FR-20; until the
    product owner confirms it, FR-20 cannot be marked fully satisfied and
    T047's acceptance record must carry the decision as open.

## Confirmed vs assumed

| Item | Status |
| --- | --- |
| Deployed schema shape, row counts, faculty labels, geography values | Confirmed (baseline.md, read 2026-10-25) |
| No runtime API consumer of `degrees.faculty` / `nus_modules.faculty` | Confirmed (code inspection) |
| Pooler unreachable from this machine; production API 503 | Confirmed (observed 2026-10-25) |
| `remove_catalog_metadata` version drift between repo and live history | Confirmed (MCP migration list vs repo) |
| Faculty selection transition matrix | Spec default (applied as written in T014) |
| Geographic AND/OR, dependent pruning, city+country identity | Spec default (applied as written in T020/T022) |
| `image_attribution` nullable column (decision 5) | Assumption recorded for review |
| No-degree prompt instead of silent degree choice (decision 11) | Unresolved; needs product confirmation |
