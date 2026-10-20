# NUS Exchange Planner: Project Overview

## What this is

An open source web app for NUS students planning exchange.

It answers two questions:

1. "Which partner universities map the most distinct NUS modules in my degree programme?" — answered by the **Recommend** page.
2. "Which NUS modules map to which modules at this partner university?" — answered by the **Compare** page.

## The two pages

- **Recommend** (`/`): the student picks their degree programme. The app ranks every partner university by the number of distinct NUS modules with qualifying mappings. Cards also show the distinct partner modules and mapping rows behind the result.
- **Compare** (`/compare`): the student picks a degree and a partner university. The app lists every mapping between them, one per row (NUS module on the left, partner module on the right).

## Data for the MVP

All data lives in the `data/` folder. No database.

- `data/majors/nus_soc_majors.json` — one file listing the modules for each degree programme. It currently covers School of Computing majors only. The file structures each degree into groups (required modules, electives, specialisations, and so on). For the MVP we ignore the group labels: all modules under a degree are treated as one flat list.
- `data/mapping/<country>/<university>.json` — one JSON file per partner university. The folder under `data/mapping/` is the country; each file inside contains that university's module mappings, one entry per mapping with the NUS module on one side and the partner module on the other.

All module counts and mappings come directly from these files. Nothing is hardcoded.

## Type of app

A web app:

- React on the frontend.
- FastAPI on the backend, serving the data as JSON.

For the MVP, the UI is deliberately bare. Visual polish is out of scope; the goal is correct functionality. Basic usability and accessibility behaviors already specified in `featureSpecs.md` stay in scope.

## MVP scope boundaries

In scope:

- Ranking partner universities by module count for a degree.
- Browsing the mappings between one degree and one partner university.

Out of scope for the MVP:

- Admission chances, application advice, exchange placement decisions.
- Mapping approval status, timetable planning, credit conversion.
- Degrees outside School of Computing.
- Login, accounts, and saving plans.

## Glossary

- **Module (course)** — a single course. "Module" is the NUS term; both words mean the same thing here.
- **Degree programme** — a major, for example "Computer Science" (BComp). Shorthand in this repo: "degree".
- **Partner university** — a foreign university that NUS students can go on exchange to.
- **Mapping** — a pair saying: this NUS module is considered equivalent to that partner-university module. A mapping belongs to exactly one partner university.
- **Mappable module** — a partner-university module that has at least one mapping to a NUS module.
