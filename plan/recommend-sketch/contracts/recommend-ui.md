# Recommend UI contract

## Application-wide shell

The outer frame, header and left navigation are a single shared shell used by every application route, including `/`, `/compare` and future pages. Their geometry, typography, icon treatment and responsive behavior stay consistent. Mount the shell once in the root layout. Navigation changes the page content and active-link state, not the shell design. The hero, degree field and tiered cards below are Recommend content only.

Theme authority: [NUSMods theme contract](nusmods-theme.md). The screenshot defines layout and copy only; the theme contract supersedes its colors, fonts, font sizes and border treatment.

## Header row content

The full-width header row contains only the site-name link, exactly `nus exchange planner` in lowercase, linking to `/`. No navigation links, logo icon, subtitle, search field or action buttons belong in this row. It is identical across every page. Navigation belongs in the shared left panel on desktop and a separate compact row below the header on narrow screens. This explicit name casing supersedes the original screenshot. Keep the existing header geometry and NUSMods brand typography.

## Exact text

| Element | Required text |
| --- | --- |
| Header | nus exchange planner |
| Navigation | Recommend / Compare |
| Hero | Ready to study abroad? |
| Degree label | Degree Programme |
| Empty picker placeholder | Choose your degree programme |
| Fixture title / badge | University Name / Country |
| Fixture primary metric | 10 NUS Modules |
| Fixture supporting metric | 12 Partner University Modules |
| Action | View Mappings --> |

The arrow is two ASCII hyphens and a greater-than sign. Do not substitute a Unicode arrow. The drawing sometimes wraps the arrow on the smallest cards; preserve its string, permit wrapping only where needed. Real values replace fixture values, and real ranks increase from #1. Remove the old eyebrow, marketing heading and explanatory hero paragraph. Existing loading, error, empty and dropdown messages remain state-dependent exceptions to reference-only copy.

## Reference coordinate system

Source PNG is 2202 × 1560. Measurements below refer to its proportional 1888 × 1337 display, not claimed exact pixel sampling. For an original-size comparison multiply normalized dimensions by 2202/1888 (~1.1663), or normalize the reference to 1888px first. Do not compare mismatched canvas sizes. Widths/heights are starting targets; overlay review is authoritative.

| Region | Approximate normalized bounds / dimensions |
| --- | --- |
| Outer frame | x18 y14, width1745 height1270; radius from theme contract |
| Header bottom divider | y102 |
| Brand | x83 y44 |
| Sidebar divider | x303, y108 through1275 |
| Sidebar links | x45 icon / x83 text; y210 and y284 |
| Hero | x417 y193; plane near x1422 y172, size116×115 |
| Label | centered near x990, y370 |
| Picker | x726 y405, width526 height60 |
| Featured card | x678 y512, width634 height270 |
| Secondary cards | x440 and1010, y839; widths505, heights214 |
| Compact cards | x391,835,1244, y1095; widths~355, heights151 |

At normalized reference width, retain the outer margin to the right of the shell rather than blindly centering it. Header spans shell width. Sidebar is roughly 284px wide inside the frame. The content's row centers follow the reference; do not force every row to share one left edge. Hero-to-picker whitespace and 45–60px inter-row gaps are part of the design. For taller live result lists the shell grows naturally with content and the sidebar divider follows it.

Use constrained responsive row containers and per-tier width tokens, not screenshot-derived absolute positioning for live content. At the reference canvas, match the table; at smaller desktop sizes reduce gaps/widths before allowing overflow.

## Typography targets

Use the exact system font stack in nusmods-theme.md, a 16px root, body line-height 1.5 and heading line-height 1.2. These are explicit mappings of NUSMods/Bootstrap source sizes to this application's roles, replacing all earlier sketch font sizes. Preserve layout boxes and anchors even though text occupies less space. Do not enlarge fonts merely to fill those boxes.

| Role | Size | Weight |
| --- | --- | --- |
| Brand | 1.25rem / 20px | 700 |
| Sidebar labels | 1rem / 16px | 400, line-height 1.6 |
| Hero | 2.5rem / 40px | 500 |
| Picker label / placeholder | 1rem / 16px | 400 |
| Featured rank / title | 1.25rem / 20px; 2rem / 32px | 700 / 500 |
| Featured NUS / partner metrics | 1.5rem / 24px; .875rem / 14px | 500 / 400 |
| Secondary rank / title | 1rem / 16px; 1.5rem / 24px | 700 / 500 |
| Secondary NUS / partner metrics | 1.25rem / 20px; .875rem / 14px | 500 / 400 |
| Compact rank / title | 1rem / 16px; 1.25rem / 20px | 700 / 500 |
| Compact NUS / partner metrics | 1rem / 16px; .875rem / 14px | 500 / 400 |
| Badge, all tiers | .75rem / 12px | 400 |
| Action, all tiers | .875rem / 14px | 400 |

Numbers and count labels share the same size/line. Complete university names may wrap; cards grow only when actual content requires it. No transformed text or viewport-wide scaling. Keep headings semantic even when the visual size maps to a different source heading level.

## Appearance

Use the sourced white, gray and coral theme in nusmods-theme.md: smooth 1px borders, restrained small radii, system type, gray body text, dark headings and coral active/link/focus states. Card, field and shell bounding boxes remain as in the coordinate table; border radii are theme choices and supersede the sketch radii. Keep the name/count insets and bottom-right action position. Keep search/opposing-arrow/paper-plane meanings and locations using clean consistent line icons; replace blue with coral and remove irregular/double-traced contours. The field is white, not blue. No decorative sketch strokes, rasterized interface, new copy or additional controls.

## Interfaces and accessibility

- Header brand and nav use real links on every page. Brand and Recommend target `/`; Compare targets `/compare`. Set aria-current="page" only on the link matching the current route, including direct loads and browser back/forward navigation.
- The hero is the page's h1; card names use h2; cards remain articles inside a labeled results region.
- DegreeProgramme wrapper delegates interaction to the shared picker. Visible label is its accessible name. Placeholder is exact when empty; selected major replaces it when selected.
- View Mappings is a single styled anchor to `/compare?degree=<encoded major>&uni=<encoded university>`; no button nested inside a link.
- Decorative plane/icon strokes are aria-hidden and pointer-events:none. Focus outlines remain visible against themed surfaces.
- The border must not clip the listbox. Preserve dropdown stacking and full keyboard behavior.
- Never use a PNG of the whole interface as the rendered page.

## Responsive behavior

Initial breakpoints to validate: wide ≥1440px uses full 1/2/3 composition; 1024–1439px uses featured, secondary pair, then two-column continuation; <1024px uses one card per row and compact top navigation replacing the fixed-width side rail. Adapt breakpoints if measured content demands it. At 390px, hero 2rem/32px, all card titles 1.5rem/24px, primary metrics 1.25rem/20px and supporting/badge/action text .875rem/14px. These mappings retain the source type scale. All interactive targets are at least 44px tall (invisible hit-area padding may preserve the small desktop action outline). No text clipping or horizontal page scroll at 390px or 200% zoom. Do not retain tiny compact-tier text on phones.

## Behavioral invariants

API contracts, order, zero-count visibility, automatic selection search, cancellation, status states and deep links remain unchanged. Before selection production has no cards; the screenshot fixture is a test surface only. Compare uses the same new header, sidebar and outer frame as Recommend; its page-specific controls, mapping rows and three-count summary retain their behavior and layout while adopting the same theme tokens. Shared navigation uses the same responsive breakpoints on every route.
