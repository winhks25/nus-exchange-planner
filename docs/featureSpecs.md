# Feature specifications

## Partner recommendations (`/`)

- Show the available degree programmes in a searchable selector.
- After a degree is selected, show every partner university with at least one matching mapping, ranked by the number of distinct NUS modules.
- Break ties by university name.
- For each partner, show its country, distinct NUS module count, and partner module count.
- Link each partner to its mappings for the selected degree.
- Show loading and service error messages when needed.

## Module mappings (`/mappings`)

- Let users search for and select a degree programme and partner university.
- Show every mapping row that matches both selections, including repeated NUS or partner module codes.
- Show the number of distinct NUS modules, partner modules, and mapping rows.
- For each row, show the NUS and partner course codes, available titles, and available units.
- Keep the selections in the URL so a mapping list can be shared or opened directly. Ignore unknown URL selections and explain the issue.
- Show an empty state when no mappings match, and loading or service error messages when needed.

## Shared behavior

- Load degree and partner choices from the catalog.
- Show only catalog data. Leave unavailable course titles or units blank.
