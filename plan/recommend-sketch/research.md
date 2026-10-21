# Phase 0 research

Research used the local source, existing specification and tests, and a delegated read-only integration review. No application dependencies were changed.

## Layout

Decision: use independent card variants with relative dimensions approximately 1 : 0.80 : 0.56; arrange explicit row groups 1, 2, then 3. Rationale: the screenshot's featured card is about 634px wide in the 1888px normalized frame, medium 505px, compact 355px. The existing six-track grid instead makes the top card full-width. Alternatives: keeping existing spans fails reference geometry; absolute positioning fails variable live content; whole-card scaling shrinks hit areas.

## NUSMods theme research (supersedes sketch typography)

Decision: adopt the default light application theme at commit `f487593c16f580cc6ea5fa6cff9bdc934de7c064`, using the exact inherited Bootstrap 4.6.2 system-font stack and type scale, NUSMods gray palette, coral primary, thin borders and restrained radii. Verified the repository's overrides, CSS variable mapping, import order, input/dropdown/nav styles and card example, plus Bootstrap's pinned upstream defaults. Full links and values are in contracts/nusmods-theme.md.

Rationale: the user explicitly changed theme while retaining layout/text. The original screenshot is therefore a geometry/copy reference, not a palette or font target. No custom-font identification work remains. Our role-to-size table is a documented adaptation of source values, not a claim that NUSMods has the same page.

Alternatives rejected: retaining handwritten fonts/blue sketch styling conflicts with the update; importing the entire Bootstrap/NUSMods stylesheet would override the agreed layout; copying timetable palettes or introducing dark-mode controls expands scope. Use existing CSS modules/Tailwind/Base UI and port semantic tokens only.

## Integration

Decision: retain RecommendPage's state ownership and request cancellation, Recommendation types, API sorting/counting, and Compare query parameters. Split the single-card component from its collection. Rationale: this is a visual redesign. Alternative: local hardcoded results would violate the user's confirmed live-value requirement.

Decision: add optional placeholder customization to DegreeCombobox, preserving existing defaults for Compare. It already accepts a label override. Reuse TypableDropdown and its ARIA/keyboard behavior rather than replacing it with a decorative box.

Decision: mount one shared AppShell with AppHeader and AppSidebar in RootLayout for every route. The user explicitly requires the same header and left panel throughout the application. Apply theme tokens across both pages while keeping shared chrome styling in its own module and Recommend content layout separately scoped, since globals.css contains broad element selectors. Derive active navigation state in a small client navigation component. Alternative rejected: a Recommend-only shell and legacy Compare shell would violate the shared-layout requirement.

## Copy and specification conflicts

Decision: literal screenshot text is the static UI contract; dynamic rank/name/country/count values remain real, as clarified by the user. Use `Partner University Modules`, never the existing `${university} Modules`; use NUS count as the larger metric. Remove the old third visible count from Recommend only. Retain all three values in API/Compare. Previous requirements to show three counts and span the top card full-width are explicitly superseded by this feature spec.

## Validation

Decision: combine a deterministic six-card fixture with live integration checks. The current live test dataset contains five universities, so it cannot reproduce all six cards in the supplied screenshot. Visual fixture uses unique internal IDs with repeated screenshot labels; live results use actual names and ordinal ranks. Existing flows tests contain stale card-count selectors and width assertions; update presentation assertions while retaining correctness checks.

Research unknowns are resolved into implementation decisions. Computed theme-token matching and unchanged layout geometry remain implementation acceptance tasks. No backend or external API research is necessary for this presentation-only change.
