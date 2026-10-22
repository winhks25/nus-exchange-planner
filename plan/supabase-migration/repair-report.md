# Catalog repair report — T011

**Prepared:** 2026-10-22

**Academic year checked:** AY2026/27

**Source snapshot:** `data/mapping/canada/toronto.json`

**Source SHA-256:** `ad1baec1ee241b7b2ba253a65874615f66471abb384bf93a3fb66fc1430ddef9`
**Machine-readable record:** `data/repairs/catalog_repairs.json`

## Scope and method

T010 found seven Toronto rows whose NUS code field contains a truncated title instead of a
course code, plus one conflicting partner-unit value. This report resolves each inventoried
issue from official NUS and University of Toronto pages.

The source row establishes the exchange pairing. Repairs only recover metadata that the row
lost (NUS code, NUS title, or partner units). No repair invents a new exchange equivalence, and
no original JSON source file was edited. Every `before` value was checked against the raw row
and every `after` value is backed by an official page. Three rows remain unresolved because
multiple official NUS courses share the same title and the source does not identify the variant.

## Result

| Row | Partner course | Raw NUS value | Status | Resolved NUS course |
|---:|---|---|---|---|
| 24 | CSC311H1 | partner units `3.0` (row 11: `0.5`) | verified | CSC311H1 = 0.5 units |
| 48 | CSC207H1 Software Design | `Software Engineering` | unresolved | CS2103 or CS2103T |
| 49 | CSC165H1 Mathematical Expression and Reasoning | `Discrete Structures` | unresolved | CS1231 or CS1231S |
| 50 | CSCC11H3 Machine Learning and Data Mining | `Foundations of Machine Le` | verified | **CS3264** Foundations of Machine Learning |
| 51 | MSE403H1 Data Sciences and Analytics for Materials Engineers | `Machine Learning for Pred` | verified | **BT4240** Machine Learning for Predictive Data Analytics |
| 52 | CSC343H1 Introduction to Databases | `Database Technology and` | verified | **IT2002** Database Technology and Management |
| 53 | 108H1F Introduction to Computer Programming | `Programming Methodology` | unresolved | CS1010 / CS1010E / CS1010S / CS1101S |
| 54 | ECE243H1 Computer Organization | `Computer Organisation` | verified | **CS2100** Computer Organisation |

Totals: **5 verified repairs**, **3 unresolved rows**, **8 affected source rows**. Four of the
verified repairs restore a lost NUS code/title; the fifth corrects the CSC311H1 unit conflict.

## Verified repairs

### Row 24 — CSC311H1 units

- **Before:** `3.0`
- **After:** `0.5`
- **Pointer:** `/mappings/24/partner_course/units`
- **Why:** The first CSC311H1 occurrence at row 11 records `0.5`. The University of Toronto
  Engineering calendar gives CSC311H1 a fixed credit value of `0.50`. Row 24's `3.0` is a
  data-entry error, not a real unit difference.
- **Evidence:**
  - [University of Toronto Engineering calendar — Electrical and Computer Engineering](https://engineering.calendar.utoronto.ca/electrical-and-computer-engineering-aeescbaser), accessed 2026-10-22, academic year 2025-26: “CSC311H1 : Introduction to Machine Learning F/S 2 - 1 0.50”.
  - [University of Toronto Arts & Science calendar — CSC311H1](https://artsci.calendar.utoronto.ca/course/csc311h1), accessed 2026-10-22, academic year 2026-27: “CSC311H1: Introduction to Machine Learning … Hours 24L/12T”.

### Row 50 — CS3264

- **Before:** code `Foundations of Machine Le`, title `null`
- **After:** code `CS3264`, title `Foundations of Machine Learning`
- **Pointers:** `/mappings/50/nus_course/code`, `/mappings/50/nus_course/title`
- **Why:** CS3264 is the unique NUS course with the full title. The source row already pairs it
  with CSCC11H3. Only the truncated code and missing title are restored.
- **Evidence:**
  - [NUS Computing — Artificial Intelligence curriculum](https://www.comp.nus.edu.sg/programmes/ug/ai/curr/), accessed 2026-10-22, AY2026/27: “CS3264 Foundations of Machine Learning”.
  - [NUS Computing — Minor in Artificial Intelligence](https://www.comp.nus.edu.sg/programmes/ug/minorc/minor-in-ai), accessed 2026-10-22: “CS3264 Foundations of Machine Learning”.
  - [UTSC Academic Calendar — CSCC11H3](https://utsc.calendar.utoronto.ca/course/cscc11h3), accessed 2026-10-22: “CSCC11H3: Introduction to Machine Learning and Data Mining”.

### Row 51 — BT4240

- **Before:** code `Machine Learning for Pred`, title `null`
- **After:** code `BT4240`, title `Machine Learning for Predictive Data Analytics`
- **Pointers:** `/mappings/51/nus_course/code`, `/mappings/51/nus_course/title`
- **Why:** The truncated title is unique to BT4240. Rows 30, 31, and 40 already use the same
  truncated title with the valid code BT4240.
- **Evidence:**
  - [NUS Computing — Bachelor of Science in Business Analytics](https://www.comp.nus.edu.sg/programmes/ug/ba), accessed 2026-10-22, AY2026/27: “BT4240 Machine Learning for Predictive Data Analytics”.
  - [University of Toronto Engineering calendar — MSE403H1](https://engineering.calendar.utoronto.ca/course/mse403h1), accessed 2026-10-22, 2025-26: “MSE403H1: Advanced A.I. for Accelerated Materials Discovery”.
- **Observation:** The source partner title (`Data Sciences and Analytics for Materials
  Engineers`) is older than the current U of T title. The partner side is preserved exactly as
  recorded; this observation does not change the exchange pairing.

### Row 52 — IT2002

- **Before:** code `Database Technology and`, title `null`
- **After:** code `IT2002`, title `Database Technology and Management`
- **Pointers:** `/mappings/52/nus_course/code`, `/mappings/52/nus_course/title`
- **Why:** IT2002 is the unique NUS course with the full title. Row 9 already uses the same
  truncated title with the valid code IT2002.
- **Evidence:**
  - [NUS College of Design and Engineering — Minor in Data Engineering](https://cde.nus.edu.sg/ece/undergraduate/electrical-engineering/specialisations-and-minor/data-engineering), accessed 2026-10-22: “IT2002 Database Technology and Management or CS2102 Database Systems”.
  - [NUS ISEM — Industrial and Systems Engineering specialisation requirements](https://cde.nus.edu.sg/isem/wp-content/uploads/sites/12/2026/06/Binder-BYOD1.pdf), accessed 2026-10-22, AY2026/27: “IT2002 Database Technology and Management or CS2102 Database Systems 4”.
  - [University of Toronto Arts & Science calendar — CSC343H1](https://artsci.calendar.utoronto.ca/course/csc343h1), accessed 2026-10-22, 2026-27: “CSC343H1: Introduction to Databases”.

### Row 54 — CS2100

- **Before:** code `Computer Organisation`, title `null`
- **After:** code `CS2100`, title `Computer Organisation`
- **Pointers:** `/mappings/54/nus_course/code`, `/mappings/54/nus_course/title`
- **Why:** CS2100 is the official NUS course with this title. Row 19 already uses the same
  title with the valid code CS2100. Only the lost code and title are restored.
- **Evidence:**
  - [NUS Computing — CS2100 course information](https://www.comp.nus.edu.sg/~cs2100/1_course_info/desc.html), accessed 2026-10-22, AY2025/26 Semester 2: “CS2100 Computer Organisation … Units: 4”.
  - [NUS Bulletin AY2026/27 — Undergraduate Education](https://www.nus.edu.sg/nusbulletin/ay202627/programmes/school-of-computing/undergraduate-education), accessed 2026-10-22, AY2026/27: “CS2100 Computer Organisation | 4”.
  - [University of Toronto Engineering calendar — ECE243H1](https://engineering.calendar.utoronto.ca/course/ece243h1), accessed 2026-10-22, 2025-26: “ECE243H1: Computer Organization”.

## Unresolved rows

### Row 48 — CS2103 or CS2103T

The source says `Software Engineering`, which is the official title for both CS2103 and
CS2103T. Current NUS Bulletin AY2026/27 lists CS2103T in the Computer Science foundation, while
the School of Computing Software Engineering focus page says CS2103 is the introductory and
required course. The source does not identify which variant was intended. Inferring one would
violate the rule against guessing. **Quarantine.**

Evidence:

- [NUS Bulletin AY2026/27 — Undergraduate Education](https://www.nus.edu.sg/nusbulletin/ay202627/programmes/school-of-computing/undergraduate-education): “CS2103T Software Engineering | 4”.
- [NUS Computing — Software Engineering focus area](https://www.comp.nus.edu.sg/programmes/ug/focus/software): “CS2103 Software Engineering is the introductory course for this focus area (and a required course for all computer science students).”
- [University of Toronto Arts & Science calendar — CSC207H1](https://artsci.calendar.utoronto.ca/course/csc207h1).

### Row 49 — CS1231 or CS1231S

The source says `Discrete Structures`, which is the official title for both CS1231 and CS1231S.
Current NUS Bulletin AY2026/27 uses CS1231S, while the official Minor in AI page uses CS1231.
The source does not identify the intended variant. **Quarantine.**

Evidence:

- [NUS Bulletin AY2026/27 — Undergraduate Education](https://www.nus.edu.sg/nusbulletin/ay202627/programmes/school-of-computing/undergraduate-education): “CS1231S Discrete Structures | 4”.
- [NUS Computing — Minor in Artificial Intelligence](https://www.comp.nus.edu.sg/programmes/ug/minorc/minor-in-ai): “CS1231 Discrete Structures or MA1100/T Basic Discrete Mathematics”.
- [University of Toronto Arts & Science calendar — CSC165H1](https://artsci.calendar.utoronto.ca/course/csc165h1).

### Row 53 — Programming Methodology variants

`Programming Methodology` is the official title for CS1010, CS1010E, CS1010S, and CS1101S. The
source row does not identify the variant. The partner code is also truncated as `108H1F`; the
official U of T code is `CSC108H1F`. Because the NUS side is unresolved, the row remains
quarantined and no partner-side correction is applied.

Evidence:

- [NUS Computing — Computer Science curriculum](https://www.comp.nus.edu.sg/programmes/ug/cs/curr/): “CS1101S Programming Methodology” and “CS1010 Programming Methodology”.
- [NUS Computing — Minor in Business Analytics](https://www.comp.nus.edu.sg/programmes/ug/minorc/ba-minor): “CS1010S Programming Methodology”.
- [NUS Mechanical Engineering sample schedule](https://cde.nus.edu.sg/me/wp-content/uploads/sites/11/2025/07/Sample-Schedule_RMI_AY2025-26-Onwards_20250624.pdf): “CS1010E Programming Methodology 4”.
- [University of Toronto Arts & Science calendar — CSC108H1](https://artsci.calendar.utoronto.ca/course/csc108h1).

## Import impact

The raw source has 154 rows. The legacy loader accepts 147 rows and rejects the 7 invalid-code
rows. Applying the four verified NUS code/title repairs recovers four rows, so T012 should
publish:

| Measure | Expected |
|---|---:|
| Raw rows archived | 154 |
| Active mappings | 151 |
| Repaired rows | 5 |
| Quarantined rows | 3 |
| Rejected by legacy loader before repair | 7 |

The CSC311H1 repair does not change the row count; it changes one partner unit value from `3.0`
to `0.5`. T012 must compute the final counts and ranking deltas from the preview rather than
copying these expectations.

## Reproduction

```sh
backend/.venv/bin/python backend/scripts/audit_catalog.py
jq empty data/repairs/catalog_repairs.json
```

`catalog_repairs.json` records the exact source checksum and every `before` value. The importer
must refuse to apply a repair if the raw source no longer matches those values. Only
`status: "verified"` entries are eligible for import.
