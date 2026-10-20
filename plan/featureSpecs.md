# Feature Specs

Companion to `plan/overview.md`. This spec is self-contained: no other doc or mockup is needed to build the two pages.

## Shared concepts

- **Degree** — a major programme, identified by its major name (for example, "Computer Science") with a full degree title (for example, "Bachelor of Computing (Computer Science)").
- **NUS module** — a module in the degree's list, identified by course code (for example, `CS2102`).
- **Partner university** — one JSON file under `data/mapping/<country>/`. Its **country** comes from the folder name under `data/mapping/`, mapped to a display name (e.g., `korea` → "South Korea", `australia` → "Australia"). Maintain an explicit folder-name → display-name list; do not title-case the folder name automatically. Its display **name** comes from the `partner_university.name` field inside the file.
- **Mapping** — one `mappings` entry in a mapping file.
- **Mappable partner module count** for a degree–university pair — the number of **distinct partner-university module codes** among qualifying mappings whose NUS code appears in the degree's module list. This is the card's primary displayed count.
- **NUS module count** for a degree–university pair — the number of **distinct NUS module codes** among those same qualifying mappings.
- **Mapping count** for a degree–university pair — the number of qualifying mapping rows. One NUS module may have multiple partner mappings, so this can exceed the NUS module count. A partner module may also appear in multiple rows, so the mapping count can exceed the partner module count. Derive this from the filtered `mappings` array, never the source file's `mapping_count` field.

## Data rules

### Degree module list

- Each degree's modules come from one file under `data/majors/`.
- Treat every degree as **one flat list** of NUS course codes. Ignore group labels such as `required`, `elective`, and `specialisation` — every code counts equally. This is a catalog match, not a check that a course satisfies degree requirements.
- Walk all nested dictionaries and lists in the degree data and collect codes from string entries inside lists. Ignore dictionary keys and prose strings.
- A valid course code is 2–3 uppercase letters, then 4 digits, then an optional letter, and must not touch another alphanumeric character. Regex: `(?<![A-Za-z0-9])[A-Z]{2,3}[0-9]{4}[A-Z]?(?![A-Za-z0-9])`.
- Extract **every** code in a string (`"BT2102 or CS2102"` → `BT2102`, `CS2102`), uppercase them (turn `BT2101`-style lowercase mix into uppercase), and remove duplicates. Example: a string like `"CS1231S"` yields `CS1231S`; `"Industry Experience Requirement or CP4101"` yields `CP4101`.
- Prose strings ("20 units total; …") extract nothing unless they contain a valid code.

### Mapping data

- One university's mappings come from its `data/mapping/<country>/<university>.json`.
- Show module names exactly as stored in the data; do not fix truncated names (see the README's known data limitations).
- A university lists `mapping_count` and a `mappings` array; trust the `mappings` array, not the count field, when counting.

## Page 1: Recommend (`/`)

**Goal:** rank partner universities by how many of a degree's modules they can map.

### 1. Degree picker

Searchable combobox.

- Each option shows the major name (for example, "Computer Science") and the full degree title beneath or beside it. The stored value used for filtering and selection is the major name.
- Focusing or clicking the field shows the full degree list before any typing.
- Typing filters the list, case-insensitive, by partial match against both the major name and the full degree title.
- ArrowUp/ArrowDown move the highlight; Home/End jump to the first/last option. The highlighted option is exposed to assistive technology through the combobox's active-descendant mechanism.
- Enter selects the highlighted option, or the first filtered match when nothing is highlighted. Escape closes the list without changing the selection.
- If nothing matches, show "Program not available. Check the degree list." and select nothing.

### 2. Search behavior

- Selecting a valid degree starts the search automatically. There is **no Search button**.
- Before any degree is selected: no university cards, no placeholder text asking to choose — just the empty picker.
- Selecting a valid degree: show one card per partner university.
- Selecting a different valid degree: clear the old cards and show the new degree's cards.
- Clearing the field or leaving it invalid: hide all cards and show the message "Choose a degree to see results."

### 3. Ranking

- Rank by distinct NUS module count, highest first. Count unique normalized NUS codes among qualifying mapping rows, so repeated mappings for one NUS code contribute one to the rank. All universities appear, including count = 0 at the bottom.
- Ties: sort by university display name, A → Z. (Two universities can tie at the same rank position; the name order fixes the display order.)

### 4. University cards

Each card shows:

- Partner university display name.
- Country name.
- Mappable partner module count for this degree as the primary number.
- Distinct NUS module count and mapping count for this degree as separate secondary numbers. Label all three values explicitly so the number of rows behind View Mappings is predictable.
- A **View Mappings** link → navigates to `/compare` with this degree and this university preselected.

Layout rules:

- At desktop width, rank #1 renders alone and spans the full card-grid width. Ranks #2 and #3 each occupy half that width on one row. Every remaining card (including count = 0) occupies one third of the rank #1 width, in rank order. On narrow screens, cards stack at full available width without overflow and keep their rank order.
- A count = 0 card stays visible and clickable; View Mappings opens Compare's empty state for that pair.

### 5. Consistency rule

A card's partner module count must equal the number of distinct partner course codes shown for the same pair in Compare. Its NUS module count must equal Compare's distinct NUS code count, and its mapping count must equal the number of Compare rows. Both pages compute from the same filtered mapping data. For Artificial Intelligence at University of Toronto, the current dataset has 9 distinct partner modules, 6 distinct NUS modules, and 9 mapping rows; three `CS3230` rows and two `CS4248` rows explain the difference. A mapping row is not necessarily a unique partner module: Business Analytics at University of Western Australia has 19 distinct partner modules across 22 rows. Zero-match pairs show 0 for all three values.

Regression checks must cover the Toronto 9 partner/6 NUS/9 row example, the Western Australia 19 partner/22 row example, all current degree–university pairs, duplicate mapping rows, zero-match pairs, NUS-count ranking with name tie breaks, the API response contract, the Recommend-to-Compare browser deep link, and the card-width proportions at desktop and narrow widths.

## Page 2: Compare (`/compare`)

**Goal:** show every mapping between one degree and one partner university.

### 1. Pickers

- Two pickers: degree (same searchable combobox as Recommend, same filtering and keyboard behavior) and partner university.
- Partner university picker: plain dropdown listing all partner universities by display name; placeholder reads "select a partner university".
- URL deep link: `/compare?degree=<major-name>&uni=<university-display-name>`. On load, pickers are set from the URL when the values are valid; invalid values fall back to empty with a note. Recommend's View Mappings links use this deep link.
- While either picker is unset: show no rows.
- Changing either picker clears old rows and shows mappings for the new pair.

### 2. Mapping rows

Show only mappings whose NUS module code appears in the selected degree's module list. One row per mapping:

- NUS module on the left, partner module on the right. Each side shows code, name, and units.
- Sorted by NUS module code, ascending; ties keep file order.
- A module with multiple mappings appears in multiple rows: the rows are per-mapping, not per-module.
- Above the rows, show the distinct partner module count, distinct NUS module count, and mapping-row count with the same labels used on Recommend. Explain briefly that one NUS module can have several partner mappings and one partner module may appear in more than one mapping row.
- Show only the fields present in the data. Details absent from the source stay blank.

Units rule:

- NUS units: mapping files never contain them. Always render 4 for the NUS side. This is a display default, not source data.
- Partner units: show as stored; leave blank when absent. Do not default.

### 3. Empty state

If the selected pair has no qualifying mappings, show an empty state (a message plus a way back to Recommend is enough for the MVP).

## Error handling

- Results for the current dataset render in under 1 second.
- If a data file is missing or malformed, show a clear error state. Never crash. Never show partial or wrong results.
- If a mapping's NUS module code fails the course-code check, skip that mapping silently and log.

## Out of scope

Recommend: admission chances, application advice, exchange placement decisions.

Compare: mapping approval status, timetable planning, credit conversion.

Both pages: editing or writing data files.
