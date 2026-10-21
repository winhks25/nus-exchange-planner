# NUSMods theme source and adaptation

## Authority and scope

User update, 2026-10-21: preserve the agreed layout and all wording; replace visual styling, including font sizes, with the theme in nusmodifications/nusmods. Use the dark application theme shown in the user’s follow-up screenshot. This supersedes the original light-theme interpretation. A dark-mode switch is not part of this change.

Inspected commit: `f487593c16f580cc6ea5fa6cff9bdc934de7c064`. Sources were read directly from a shallow checkout of the public repository. Bootstrap 4.6.2 is explicitly pinned by its website/package.json; inherited values below were verified against that version's upstream source. These are source-derived values, not a claim that every NUSMods screen uses one universal component style.

## Current palette

The follow-up screenshot’s dominant background pixel is `#222324`; its secondary surface is `#292929`. Text and border tokens below are adapted for readability on those dark surfaces. Typography and geometry remain unchanged. These colors supersede earlier light-surface references in the remaining phase tasks.

## Theme tokens

| Token | Value | Source |
| --- | --- | --- |
| Body/card background | #222324 | Sampled from the user’s dark screenshot |
| Main body text | #b5b5b5 | Dark-surface adaptation |
| Emphasis text | #dddddd | Dark-surface adaptation |
| Secondary navigation | #a3a3a3 | Dark-surface adaptation |
| Placeholder | #aeb1b5 | NUSMods gray-light and components/form.scss |
| Borders/dividers | #484848 | Dark-surface adaptation |
| Subtle surface/hover | #292929 | Sampled from the user’s dark screenshot |
| Primary/active/link/focus border | #ff5138 | NUSMods primary |
| Error | #b71c1c | NUSMods danger |
| Base text | 1rem, weight 400, line-height 1.5 | Bootstrap 4.6.2 defaults |
| Heading scale | 2.5 / 2 / 1.75 / 1.5 / 1.25 / 1rem | Bootstrap h1–h6; weight 500, line-height 1.2 |
| Small text | .875rem; NUSMods also defines .85 / .75 / .65rem | Bootstrap and NUSMods overrides |
| Standard control radius | .25rem | Bootstrap default |
| Card radius | .35rem | NUSMods mpe/form/ModuleCard.scss |
| Border width | 1px | Bootstrap defaults and NUSMods ModuleCard |
| Input focus ring | 0 0 0 .2rem rgba(255,81,56,.25) | Bootstrap focus formula using NUSMods primary |
| Dropdown shadow | 0 2px 6px rgba(0,0,0,.25) | NUSMods bootstrap/style-override.scss |

Font stack, inherited unchanged from Bootstrap:

```css
-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial,
"Noto Sans", "Liberation Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji",
"Segoe UI Symbol", "Noto Color Emoji"
```

No handwritten font, condensed brand font, custom webfont download or font-identification task remains. System font rendering varies by platform; compare visual baselines on the same OS/browser.

## Intentional mappings for this application

Keep the screenshot's element positions, card footprints, row composition, whitespace, internal content order and action placement. Do not import NUSMods' navigation width, header height, page padding, routing, or timetable layout. The typography role mapping in recommend-ui.md selects actual source scale values for our existing roles; NUSMods has no identical hero/three-tier-card screen.

Use charcoal shell/header/sidebar/cards, light headings, gray body text, thin gray dividers and smooth borders. Replace sketch outlines and blue accents. Use .35rem smooth card/outer-frame radii and .25rem field/action radii; this changes decoration, not bounding boxes. Country badges use a subtle gray surface with gray text and border. View Mappings stays an outlined anchor in its current position, using primary-colored text/border and a subtle hover surface. Keep its exact ASCII arrow. Navigation uses gray-mid and primary active color, with existing icon meanings and positions; plane detail uses primary instead of blue. No NUSMods branding or new navigation labels.

Apply the theme tokens application-wide, including Compare controls/text/surfaces, without changing Compare wording, content order, behavior or geometry. Reuse existing Base UI/Tailwind components; port tokens and equivalent styles, not Bootstrap's global stylesheet or its component runtime. This avoids importing NUSMods layout/reset rules. Shared AppShell remains mounted once in the root layout.

## Pinned references

- [NUSMods theme overrides](https://github.com/nusmodifications/nusmods/blob/f487593c16f580cc6ea5fa6cff9bdc934de7c064/website/src/styles/bootstrap/variable-overrides.scss)
- [CSS variables and dark-mode definitions](https://github.com/nusmodifications/nusmods/blob/f487593c16f580cc6ea5fa6cff9bdc934de7c064/website/src/styles/utils/css-variables.scss)
- [Bootstrap import order](https://github.com/nusmodifications/nusmods/blob/f487593c16f580cc6ea5fa6cff9bdc934de7c064/website/src/styles/bootstrap/bootstrap.scss)
- [Dropdown and interaction styles](https://github.com/nusmodifications/nusmods/blob/f487593c16f580cc6ea5fa6cff9bdc934de7c064/website/src/styles/bootstrap/style-override.scss)
- [Placeholder styling](https://github.com/nusmodifications/nusmods/blob/f487593c16f580cc6ea5fa6cff9bdc934de7c064/website/src/styles/components/form.scss)
- [Navigation colors/type](https://github.com/nusmodifications/nusmods/blob/f487593c16f580cc6ea5fa6cff9bdc934de7c064/website/src/views/layout/Navtabs.scss)
- [Card border/radius example](https://github.com/nusmodifications/nusmods/blob/f487593c16f580cc6ea5fa6cff9bdc934de7c064/website/src/views/mpe/form/ModuleCard.scss)
- [Dependency versions](https://github.com/nusmodifications/nusmods/blob/f487593c16f580cc6ea5fa6cff9bdc934de7c064/website/package.json)
- [Bootstrap 4.6.2 defaults](https://github.com/twbs/bootstrap/blob/v4.6.2/scss/_variables.scss)

The original screenshot and generated hand-drawn mockup are now layout/copy references only. Neither is a current theme preview.
