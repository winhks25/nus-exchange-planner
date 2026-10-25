# Additive catalog contract — exchange planner enhancements

Date: 2026-10-25 (T002). This is an **additive** contract: every existing field,
endpoint, query parameter, and response shape is preserved unchanged. The
repository OpenAPI document at `plan/contracts/openapi.yaml` describes the
pre-change surface; this document defines what the enhancement adds to it.
Syncing that file happens during the final documentation pass (T050).

## Catalog response (`GET /api/v1/catalog`)

The response object gains a `faculties` array and per-option metadata. Existing
fields keep their names, types, and order.

```json
{
  "faculties": [
    { "id": 1, "name": "School of Computing" }
  ],
  "degrees": [
    {
      "name": "Computer Science",
      "degree": "Bachelor of Computing (Computer Science)",
      "faculty_ids": [1]
    }
  ],
  "universities": [
    {
      "id": 1,
      "name": "University of Western Australia",
      "country": "Australia",
      "city": "Perth",
      "continent": "Oceania",
      "faculty_ids": [1],
      "image": "https://<storage-url>/university-assets/uwa.jpg",
      "website": "https://www.uwa.edu.au",
      "image_attribution": null
    }
  ]
}
```

### Field rules

| Field | Source | Rules |
| --- | --- | --- |
| `faculties[].id` | `faculties.id` | Stable database identity; never reused for another faculty |
| `faculties[].name` | `faculties.name` | Nonblank, trimmed, unique; list sorted by name then id |
| `degrees[].name` / `degrees[].degree` | `degrees.name` / `degrees.full_title` | Unchanged from today |
| `degrees[].faculty_ids` | `degree_faculties` | Stable faculty ids, sorted by faculty name then id; `[]` when no membership is recorded |
| `universities[].id` | `partner_universities.id` | Stable database identity; `null` when the source cannot assign one (JSON mode) |
| `universities[].name` / `universities[].country` | unchanged | Unchanged from today |
| `universities[].city` | `partner_universities.city` | Nullable; missing means unknown, never inferred |
| `universities[].continent` | `partner_universities.continent` | Nullable; missing means unknown, never inferred |
| `universities[].faculty_ids` | `faculty_partner_universities` | Explicit availability links only, sorted by faculty name then id; `[]` means no availability recorded, not "unavailable" |
| `universities[].image` | `partner_universities.image` | Nullable public URL; never an unverified third-party photo |
| `universities[].website` | `partner_universities.website` | Nullable; official site only |
| `universities[].image_attribution` | `partner_universities.image_attribution` | Nullable; required in the UI whenever the license of `image` demands it, independent of whether it is present |

Array order for `degrees` and `universities` is the persisted source order
(currently stable `id` order because `source_order` is absent in the deployed
schema). `faculties` has no source order and is always name-sorted.

### JSON mode

The frozen JSON snapshot has no stable ids, geography, or availability. In
`CATALOG_BACKEND=json` mode the catalog emits the same shape with
`faculties: []`, `faculty_ids: []` on every degree and university,
`id: null`, and `city`/`continent`/`image`/`website`/`image_attribution` all
`null`. Recommendation and mapping behavior is byte-for-byte unchanged.

### Unchanged surfaces

- `GET /api/v1/recommendations?degree=<name>` — same body, same rank order
  (descending distinct NUS modules, then name in "C" collation).
- `GET /api/v1/mappings?degree=<name>&uni=<name>` — same name-based parameters,
  same body, same 404/422 semantics.
- Error responses (`CatalogUnavailable` 503, unknown-selection 404) are
  unchanged.

## Faculty–degree selection rules

These are the pure transition rules implemented by the frontend helpers (T014)
and mirrored by any server-side validation:

1. **Faculty → degrees (FR-02).** A selected faculty restricts the degree
   options to degrees whose `faculty_ids` contain that faculty.
2. **Degree → faculty (FR-03).** Selecting a degree directly sets the faculty
   to its sole faculty, or to the **alphabetically first faculty name** when it
   belongs to several; equal names tie-break by stable id. This applies even
   when another compatible faculty was previously selected.
3. **Faculty change with a degree selected (FR-04).** Keep the degree when it
   belongs to the newly selected faculty; otherwise clear the degree.
4. **Clear faculty.** The degree stays selected and all degrees become
   available again; choosing that degree again re-derives its faculty by rule 2.
5. **No recorded membership.** A degree without `faculty_ids` remains
   selectable on its own but is hidden under every faculty filter, and its
   direct selection leaves the faculty unset.
6. **Atomicity (FR-05).** Faculty and degree change as one transition; when the
   degree is invalidated, any stale recommendation/mapping results are cleared
   in the same transition.

## Faculty–university availability rules (DB-02)

- Availability is faculty-based only; no academic year or semester is modeled.
- Links are **explicit**: `faculty_partner_universities` rows are the only
  source of truth. Availability is never inferred from mapping existence.
- A verified university-wide agreement is stored as one explicit row per
  relevant faculty; that expansion must be repeated whenever a new faculty is
  added.
- Missing links mean *unknown*, and unknown universities stay out of a
  faculty-filtered directory while remaining visible in the unfiltered one.

## University metadata rules (DB-03)

- `image` holds only reviewed, rights-cleared photographs uploaded to Supabase
  Storage; `image_attribution` carries the required credit when the license
  demands it.
- `website` holds the official university site only.
- Either (or both) may be null; the UI renders fallbacks and never invents
  values.
