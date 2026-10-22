# Catalog performance evidence (T027)

## Environment

- PostgreSQL: 15.15 (Homebrew), disposable local cluster
- psycopg: 3.3.6
- Dataset: deterministic import preview plus synthetic benchmark rows
- Workload: warmed sequential requests and concurrent recommendation calls

## Command

```bash
uv run --directory backend python -m scripts.verify_catalog --enlarge \
  --output /tmp/api-validation-rerun.md \
  --performance-output ../plan/supabase-migration/performance.md
```

## Dataset

| Table | Rows |
| --- | ---: |
| `degrees` | 56 |
| `nus_modules` | 12,652 |
| `degree_modules` | 12,726 |
| `partner_universities` | 505 |
| `pu_modules` | 125,142 |
| `module_mappings` | 250,151 |

## Query plans

| Query | Top node | Planning ms | Execution ms | Seq scans | Index scans |
| --- | --- | ---: | ---: | ---: | ---: |
| catalog degrees | Sort | 0.038 | 0.040 | 1 | 0 |
| catalog universities | Sort | 0.019 | 0.175 | 1 | 0 |
| recommendations | Sort | 0.981 | 38.500 | 2 | 2 |
| mappings | Sort | 0.665 | 6.884 | 1 | 3 |

## Warm latency (100 sequential calls)

| Endpoint | p50 ms | p95 ms | max ms |
| --- | ---: | ---: | ---: |
| catalog | 1.297 | 1.373 | 15.695 |
| recommendations | 26.866 | 28.875 | 36.649 |
| mappings | 4.949 | 5.173 | 5.330 |

## Pool contention (64 recommendation requests, 16 workers)

| Pool max size | Wall ms | p50 ms | p95 ms | Requests/s |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 1731.2 | 430.330 | 445.405 | 37.0 |
| 8 | 450.3 | 93.603 | 149.446 | 142.1 |

## Interpretation

- The catalog query reads two small dimension tables and sorts them; a full
  scan is cheaper than an index scan at this size.
- The recommendation query aggregates every partner module for one degree.
  Its selective degree lookup uses the `degree_modules` primary key and the
  mapping lookup uses the existing `module_mappings(nus_module_code)` index.
  The remaining sequential scans read `pu_modules` and
  `partner_universities`, which the aggregate must visit for all partners.
- The mappings query uses the existing `pu_modules` unique index,
  `degree_modules` primary key and `nus_modules` primary key. It scans
  `module_mappings` once at this cardinality; the endpoint still returns in
  a few milliseconds.
- Increasing the pool from one to eight connections improves recommendation
  throughput and p95 latency by roughly 4x in one process. The runtime
  default stays at one connection per serverless instance as recorded in
  `research.md`; deployments with persistent workers can raise
  `DB_POOL_MAX_SIZE`.

## Index decision

No new migration is added. Existing indexes cover every selective join and
lookup. The observed sequential scans are bounded dimension or aggregate
reads, and the measured p95 latencies are well below the request budget.

## Limitations

- The cluster is local PostgreSQL, not the target Supabase project or its
  transaction pooler; absolute timings and plans can differ on the target.
- The synthetic rows model cardinality, not real degree/university overlap.
- The measurements use a warm pool and a warm cache; cold-start behavior is
  covered by the outage/recovery checks rather than this benchmark.
