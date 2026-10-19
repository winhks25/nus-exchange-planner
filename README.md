# NUS Exchange Planner

An open source tool that helps NUS students find partner universities with the
most modules that map to their degree, and to see which NUS modules map to
which partner modules.

- **Recommend** (`/`): ranks partner universities by how many of a degree's
  modules have a mapping.
- **Compare** (`/compare`): shows the module mappings for one degree and one
  partner university.

See [`plan/overview.md`](plan/overview.md) and
[`plan/featureSpecs.md`](plan/featureSpecs.md) for scope and behavior.

## Known data limitations

- **Module names may be incomplete.** Module names are shown exactly as stored
  in the source data. Some NUS module names in `data/mapping/` are truncated
  (for example, `CS2106` shows as "Introduction to Operating"). Full titles are
  not available in the current dataset.
