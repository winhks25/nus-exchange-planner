# PostgreSQL API validation (T025)

Generated: 2026-10-22T09:03:06+00:00

## Environment

- Python: 3.12.14
- PostgreSQL: 15.15 (Homebrew)
- psycopg: 3.3.6
- Source checksum: `b393cd0f6b34adb506a23ba810d65c083238339fab0b76a236167fdbef6901b9`
- Repair checksum: `61268be6b39c1effc644d72c8cc4787287cdbcafc86d32fb3c48814d48064a3e`

## Command

```bash
uv run --directory backend python -m scripts.verify_catalog
```

## Checks

| Check | Result | Evidence |
| --- | --- | --- |
| JSON catalog matches baseline | PASS | GET /api/v1/catalog |
| PostgreSQL catalog matches preview | PASS | source-ordered degrees and universities |
| JSON recommendations match baseline: Artificial Intelligence | PASS | GET /api/v1/recommendations?degree=Artificial Intelligence |
| PostgreSQL recommendations match preview: Artificial Intelligence | PASS | GET /api/v1/recommendations?degree=Artificial Intelligence |
| Recommendation deltas are enumerated: Artificial Intelligence | PASS | only documented repairs change ranking counts |
| JSON recommendations match baseline: Business Analytics | PASS | GET /api/v1/recommendations?degree=Business Analytics |
| PostgreSQL recommendations match preview: Business Analytics | PASS | GET /api/v1/recommendations?degree=Business Analytics |
| Recommendation deltas are enumerated: Business Analytics | PASS | only documented repairs change ranking counts |
| JSON recommendations match baseline: Business Artificial Intelligence Systems | PASS | GET /api/v1/recommendations?degree=Business Artificial Intelligence Systems |
| PostgreSQL recommendations match preview: Business Artificial Intelligence Systems | PASS | GET /api/v1/recommendations?degree=Business Artificial Intelligence Systems |
| Recommendation deltas are enumerated: Business Artificial Intelligence Systems | PASS | only documented repairs change ranking counts |
| JSON recommendations match baseline: Computer Science | PASS | GET /api/v1/recommendations?degree=Computer Science |
| PostgreSQL recommendations match preview: Computer Science | PASS | GET /api/v1/recommendations?degree=Computer Science |
| Recommendation deltas are enumerated: Computer Science | PASS | only documented repairs change ranking counts |
| JSON recommendations match baseline: Information Systems | PASS | GET /api/v1/recommendations?degree=Information Systems |
| PostgreSQL recommendations match preview: Information Systems | PASS | GET /api/v1/recommendations?degree=Information Systems |
| Recommendation deltas are enumerated: Information Systems | PASS | only documented repairs change ranking counts |
| JSON recommendations match baseline: Information Security | PASS | GET /api/v1/recommendations?degree=Information Security |
| PostgreSQL recommendations match preview: Information Security | PASS | GET /api/v1/recommendations?degree=Information Security |
| Recommendation deltas are enumerated: Information Security | PASS | only documented repairs change ranking counts |
| Documented ranking deltas | PASS | 4 changed degree/university pairs |
| JSON mappings match baseline: Artificial Intelligence || University of Western Australia | PASS | GET /api/v1/mappings?degree=Artificial Intelligence&uni=University of Western Australia |
| PostgreSQL mappings match preview: Artificial Intelligence || University of Western Australia | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Artificial Intelligence || University of Toronto | PASS | GET /api/v1/mappings?degree=Artificial Intelligence&uni=University of Toronto |
| PostgreSQL mappings match preview: Artificial Intelligence || University of Toronto | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Artificial Intelligence || Kyoto University | PASS | GET /api/v1/mappings?degree=Artificial Intelligence&uni=Kyoto University |
| PostgreSQL mappings match preview: Artificial Intelligence || Kyoto University | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Artificial Intelligence || Korea University | PASS | GET /api/v1/mappings?degree=Artificial Intelligence&uni=Korea University |
| PostgreSQL mappings match preview: Artificial Intelligence || Korea University | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Artificial Intelligence || Yonsei University | PASS | GET /api/v1/mappings?degree=Artificial Intelligence&uni=Yonsei University |
| PostgreSQL mappings match preview: Artificial Intelligence || Yonsei University | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Business Analytics || University of Western Australia | PASS | GET /api/v1/mappings?degree=Business Analytics&uni=University of Western Australia |
| PostgreSQL mappings match preview: Business Analytics || University of Western Australia | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Business Analytics || University of Toronto | PASS | GET /api/v1/mappings?degree=Business Analytics&uni=University of Toronto |
| PostgreSQL mappings match preview: Business Analytics || University of Toronto | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Business Analytics || Kyoto University | PASS | GET /api/v1/mappings?degree=Business Analytics&uni=Kyoto University |
| PostgreSQL mappings match preview: Business Analytics || Kyoto University | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Business Analytics || Korea University | PASS | GET /api/v1/mappings?degree=Business Analytics&uni=Korea University |
| PostgreSQL mappings match preview: Business Analytics || Korea University | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Business Analytics || Yonsei University | PASS | GET /api/v1/mappings?degree=Business Analytics&uni=Yonsei University |
| PostgreSQL mappings match preview: Business Analytics || Yonsei University | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Business Artificial Intelligence Systems || University of Western Australia | PASS | GET /api/v1/mappings?degree=Business Artificial Intelligence Systems&uni=University of Western Australia |
| PostgreSQL mappings match preview: Business Artificial Intelligence Systems || University of Western Australia | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Business Artificial Intelligence Systems || University of Toronto | PASS | GET /api/v1/mappings?degree=Business Artificial Intelligence Systems&uni=University of Toronto |
| PostgreSQL mappings match preview: Business Artificial Intelligence Systems || University of Toronto | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Business Artificial Intelligence Systems || Kyoto University | PASS | GET /api/v1/mappings?degree=Business Artificial Intelligence Systems&uni=Kyoto University |
| PostgreSQL mappings match preview: Business Artificial Intelligence Systems || Kyoto University | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Business Artificial Intelligence Systems || Korea University | PASS | GET /api/v1/mappings?degree=Business Artificial Intelligence Systems&uni=Korea University |
| PostgreSQL mappings match preview: Business Artificial Intelligence Systems || Korea University | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Business Artificial Intelligence Systems || Yonsei University | PASS | GET /api/v1/mappings?degree=Business Artificial Intelligence Systems&uni=Yonsei University |
| PostgreSQL mappings match preview: Business Artificial Intelligence Systems || Yonsei University | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Computer Science || University of Western Australia | PASS | GET /api/v1/mappings?degree=Computer Science&uni=University of Western Australia |
| PostgreSQL mappings match preview: Computer Science || University of Western Australia | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Computer Science || University of Toronto | PASS | GET /api/v1/mappings?degree=Computer Science&uni=University of Toronto |
| PostgreSQL mappings match preview: Computer Science || University of Toronto | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Computer Science || Kyoto University | PASS | GET /api/v1/mappings?degree=Computer Science&uni=Kyoto University |
| PostgreSQL mappings match preview: Computer Science || Kyoto University | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Computer Science || Korea University | PASS | GET /api/v1/mappings?degree=Computer Science&uni=Korea University |
| PostgreSQL mappings match preview: Computer Science || Korea University | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Computer Science || Yonsei University | PASS | GET /api/v1/mappings?degree=Computer Science&uni=Yonsei University |
| PostgreSQL mappings match preview: Computer Science || Yonsei University | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Information Systems || University of Western Australia | PASS | GET /api/v1/mappings?degree=Information Systems&uni=University of Western Australia |
| PostgreSQL mappings match preview: Information Systems || University of Western Australia | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Information Systems || University of Toronto | PASS | GET /api/v1/mappings?degree=Information Systems&uni=University of Toronto |
| PostgreSQL mappings match preview: Information Systems || University of Toronto | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Information Systems || Kyoto University | PASS | GET /api/v1/mappings?degree=Information Systems&uni=Kyoto University |
| PostgreSQL mappings match preview: Information Systems || Kyoto University | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Information Systems || Korea University | PASS | GET /api/v1/mappings?degree=Information Systems&uni=Korea University |
| PostgreSQL mappings match preview: Information Systems || Korea University | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Information Systems || Yonsei University | PASS | GET /api/v1/mappings?degree=Information Systems&uni=Yonsei University |
| PostgreSQL mappings match preview: Information Systems || Yonsei University | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Information Security || University of Western Australia | PASS | GET /api/v1/mappings?degree=Information Security&uni=University of Western Australia |
| PostgreSQL mappings match preview: Information Security || University of Western Australia | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Information Security || University of Toronto | PASS | GET /api/v1/mappings?degree=Information Security&uni=University of Toronto |
| PostgreSQL mappings match preview: Information Security || University of Toronto | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Information Security || Kyoto University | PASS | GET /api/v1/mappings?degree=Information Security&uni=Kyoto University |
| PostgreSQL mappings match preview: Information Security || Kyoto University | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Information Security || Korea University | PASS | GET /api/v1/mappings?degree=Information Security&uni=Korea University |
| PostgreSQL mappings match preview: Information Security || Korea University | PASS | all qualifying rows, order and optional fields |
| JSON mappings match baseline: Information Security || Yonsei University | PASS | GET /api/v1/mappings?degree=Information Security&uni=Yonsei University |
| PostgreSQL mappings match preview: Information Security || Yonsei University | PASS | all qualifying rows, order and optional fields |
| Documented mapping deltas | PASS | 4 changed pairs; 18 pairs preserve repeated NUS codes |
| Valid-empty pairs | PASS | Artificial Intelligence / University of Western Australia, Computer Science / University of Western Australia, Computer Science / Yonsei University |
| JSON missing degree is 422 | PASS | status 422 |
| JSON missing university is 422 | PASS | status 422 |
| JSON unknown degree is 404 | PASS | status 404 |
| JSON unknown university is 404 | PASS | status 404 |
| PostgreSQL missing degree is 422 | PASS | status 422 |
| PostgreSQL missing university is 422 | PASS | status 422 |
| PostgreSQL unknown degree is 404 | PASS | status 404 |
| PostgreSQL unknown university is 404 | PASS | status 404 |
| JSON valid-empty pair is 200 | PASS | Artificial Intelligence / University of Western Australia |
| PostgreSQL valid-empty pair is 200 | PASS | Artificial Intelligence / University of Western Australia |
| Database available before outage | PASS | status 200 |
| Database outage returns 503 without JSON fallback | PASS | status 503 |
| Database recovers after restart | PASS | status 200 |
| Null titles and units are omitted | PASS | optional title/unit fields stay absent when unknown |

## Scope and limitations

- The PostgreSQL side is seeded from the deterministic import preview into a
  disposable TLS-enabled local database created from the checked-in migrations.
- The real Phase 3 importer publication has not run against Supabase yet, so this
  records API behavior and repair deltas rather than target-project import evidence.
- Catches, counts and ordering are compared exactly for all six degrees and all
  thirty degree/university pairs; only the documented repairs are allowed to differ.
