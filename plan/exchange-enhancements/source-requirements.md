# Exchange Planner Enhancements — Feature Specification

## 1. Overview

Enhance the existing **Recommend** and **Mappings** pages, and implement a **Universities** directory page. Features include faculty-aware degree selection, geographic filtering, university metadata and cards, and navigation to preselected mappings.

## 2. Database Requirements

### DB-01: Faculties and degree programmes

- Create a `faculties` entity with a stable unique identifier and faculty name.
- Make the existing `nus_modules.faculty` field reference the faculty entity through a foreign key, subject to the schema clarification below.
- Represent degree-to-faculty membership with a **many-to-many** junction table, with foreign keys to the existing degree entity and `faculties` and a unique constraint on each degree–faculty pair.
- A degree may be associated with multiple faculties.
- Inspect existing schema and data before migration; preserve valid existing relationships.

### DB-02: Faculty–partner university availability

- Create a many-to-many table associating NUS faculties with partner universities.
- Use foreign keys and a unique constraint on each faculty–partner university pair.
- Availability is **faculty-based only**; do not model academic year or semester in this feature.

### DB-03: Partner university metadata

- Add `image` and `website` fields to the existing partner university table (confirm its actual name; the source calls it `partner_univerity`).
- Find suitable university photographs online, download and upload them to **Supabase Storage**, and save the resulting image references in the database.
- Find each university's official website and save its URL.
- Allow either field to be missing. The UI must provide a fallback image and gracefully handle missing website links.
- Ensure images have appropriate usage rights and attribution where required; do not assume arbitrary online photographs are reusable.

## 3. Feature 1 — Faculty-based degree selection

**Pages:** Recommend, Mappings.

### Functional requirements

- **FR-01:** Add a searchable, typeable faculty dropdown on both pages.
- **FR-02:** Selecting a faculty restricts the degree dropdown to degrees associated with that faculty.
- **FR-03:** Selecting a degree directly automatically sets the faculty to the degree's sole faculty, or to the **alphabetically first faculty name** if it belongs to multiple faculties.
- **FR-04:** If the user changes faculty while a degree is selected, **retain the degree if it belongs to the new faculty**; otherwise **clear the selected degree**.
- **FR-05:** Keep displayed faculty and degree selections consistent with their underlying relationships.

### Acceptance criteria

- [ ] Faculty selection is searchable on both pages.
- [ ] Faculty selection filters the degree options correctly.
- [ ] Direct degree selection auto-populates faculty, including multi-faculty degrees.
- [ ] Changing faculty preserves a compatible degree and clears an incompatible degree.
- [ ] Existing Recommend and Mappings behavior remains functional.

## 4. Feature 2 — Geographic filtering

**Pages:** Recommend, Universities.

### Functional requirements

- **FR-06:** Provide **multi-select** filters for continent, country, and city.
- **FR-07:** Filters are **dependent**: available country options reflect selected continent(s); available city options reflect selected country/countries (and any selected continents).
- **FR-08:** Apply **AND logic across filter categories**: a university must satisfy each active category. Multiple selections **within the same category** match any selected value (OR within a category).
- **FR-09:** Apply changes **immediately**, without an Apply button.
- **FR-10:** On Recommend, filter the recommendation results; on Universities, filter the displayed cards.
- **FR-11:** An empty selection for a category means no restriction from that category.

### Acceptance criteria

- [ ] All three geographic filters support multiple selections.
- [ ] Dependent option lists reflect higher-level selections.
- [ ] Cross-category AND and within-category OR behavior is correct.
- [ ] Results update immediately after selection changes.
- [ ] Geographic filters work on both specified pages.

## 5. Feature 3 — Universities directory

### Functional requirements

- **FR-12:** On initial load, display **every partner university in the database**, regardless of whether faculty availability has been recorded.
- **FR-13:** Provide a searchable, typeable faculty dropdown.
- **FR-14:** Once a faculty is selected, show only universities linked to that faculty in the availability table.
- **FR-15:** Support the geographic filters from Feature 2, combined with the faculty restriction when active.
- **FR-16:** Render each university as a card defined in Feature 4. (A row must contain 3-4 university cards)

### Acceptance criteria

- [ ] Default listing includes all partner universities.
- [ ] Selecting a faculty filters to its available partner universities.
- [ ] Geographic and faculty filters work together.
- [ ] All displayed universities use the card component.

## 6. Feature 4 — University card

### Required elements

1. University photograph at the top, or a fallback image when missing.
2. University name.
3. City and country tags.
4. Official website link, when available; a non-broken fallback state when unavailable.
5. **View Mappings** button.

Follow the supplied university-card design reference image attached. 
### Acceptance criteria

- [ ] Correct image or fallback is shown.
- [ ] Name, city, and country match database records.
- [ ] Website links point to official university sites when present.
- [ ] Missing website data does not produce a broken link.
- [ ] View Mappings button is present and functional.

## 7. Feature 5 — View Mappings navigation

### Functional requirements

- **FR-17:** Clicking **View Mappings** navigates to the existing Mappings page.
- **FR-18:** Preselect the university represented by the clicked card.
- **FR-19:** **Preserve all other existing Mappings selections** (e.g., faculty and degree) where present.
- **FR-20:** **Automatically load mappings** for the selected university, using the preserved selections and existing mapping logic; no extra Search click is required.

### Acceptance criteria

- [ ] Navigation opens Mappings with the correct university selected.
- [ ] Other existing selections are preserved.
- [ ] Mappings load automatically for the selected university.
- [ ] Existing Mappings functionality remains intact.

