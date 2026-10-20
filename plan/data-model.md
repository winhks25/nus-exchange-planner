# Data model

The MVP persists only source JSON. API models are read-only projections.

## Source entities

| Entity | Fields | Relationships and rules |
| --- | --- | --- |
| Degree | `name` (major, unique), `degree` (full title), nested curriculum data | One record in a `data/majors/*.json` `majors` array. Recursively visit dictionaries/lists and extract codes only from strings that are list items. Deduplicate codes per degree. |
| Partner university | `partner_university.name`, country folder, source file | One `data/mapping/<country>/*.json` file per university. Country label comes from an explicit folder map: `australia` → Australia, `canada` → Canada, `japan` → Japan, `korea` → South Korea. Unknown folders fail catalog validation until mapped. |
| Mapping | `nus_course`, `partner_course`, file order | Belongs to one partner. NUS code must match the course-code rule; invalid records are logged and excluded. Preserve source titles and optional fields. Ignore `mapping_count` for calculations. |

## Derived entities

| Entity | Fields | Rule |
| --- | --- | --- |
| DegreeCourseSet | degree major name, unique uppercase course codes | Regex `(?<![A-Za-z0-9])[A-Z]{2,3}[0-9]{4}[A-Z]?(?![A-Za-z0-9])`, applied case-insensitively to list strings; normalize matches to uppercase. |
| PairMappings | degree name, university name, mapping rows | Keep all mappings whose normalized NUS code is in DegreeCourseSet. Stable sort by NUS code; ties retain file order. |
| UniversityRanking | degree name, university name, country, partner module count, NUS module count, mapping count | Count distinct normalized partner codes, distinct normalized NUS codes, and all rows in PairMappings. Include zero counts. Sort descending partner module count, then ascending university display name. Never use source `mapping_count`. |

## Display rules

- Mapping rows show source code, title and units when available. NUS units always display as `4`; partner units have no default.
- Blank source fields remain blank; do not repair truncated titles.
- Selection state is held in the frontend and URL, not persisted. It transitions from unset → valid pair → changed/cleared pair; stale rows are hidden immediately on a change.
- Invalid URL values transition to an unset selection with a note. API validation errors and catalog load errors are separate states.
