# Exchange enhancement data audit (dry-run)

Generated: 2026-10-25T12:08:43+00:00 UTC
Target: `127.0.0.1/catalog_test_e64d631ec3e6` (local replica of the live core tables (MCP capture 2026-10-25))
Result: **PASS**

The audit is read-only: it counts rows, verifies referential integrity,
and lists legacy faculty labels and university coverage. It writes
nothing to the inspected database and stores no credentials.

## Row counts (core tables)

| Table | Rows |
| --- | ---: |
| `degrees` | 6 |
| `nus_modules` | 152 |
| `degree_modules` | 226 |
| `specializations` | 19 |
| `specialization_modules` | 30 |
| `partner_universities` | 5 |
| `pu_modules` | 142 |
| `module_mappings` | 151 |

## Enhancement objects (post-migration state)

| Object | Present | Rows |
| --- | --- | ---: |
| `faculties` | no | n/a |
| `degree_faculties` | no | n/a |
| `faculty_partner_universities` | no | n/a |
| column `nus_modules.faculty_id` | no | n/a |
| column `partner_universities.image` | no | n/a |
| column `partner_universities.website` | no | n/a |
| column `partner_universities.image_attribution` | no | n/a |

## Distinct legacy faculty labels

| Source | Label | Rows |
| --- | --- | ---: |
| `degrees.faculty` | School of Computing | 6 |
| `nus_modules.faculty` | School of Computing | 152 |

## Candidate faculty mappings

Candidate mappings are deterministic: without a reviewed alias file the
canonical faculty is the trimmed label itself. Variants are flagged,
never silently merged.

| Legacy label | Canonical faculty | Flags |
| --- | --- | --- |
| School of Computing | School of Computing | — |

Null-label rows: 0. Casefold collisions: 0.

## Orphan relations

| Relation | Orphan rows |
| --- | ---: |
| `degree_modules` | 0 |
| `specializations` | 0 |
| `specialization_modules` | 0 |
| `pu_modules` | 0 |
| `module_mappings` | 0 |

## Missing geography

Universities with a null city or continent: 0.

All universities have both city and continent.

## University coverage

| University | Country | City | Continent | Partner modules | Mapping rows | Mapped degrees |
| --- | --- | --- | --- | ---: | ---: | ---: |
| Korea University | South Korea | Seoul | Asia | 35 | 36 | 6 |
| Kyoto University | Japan | Kyoto | Asia | 7 | 7 | 6 |
| University of Toronto | Canada | Toronto | North America | 49 | 52 | 6 |
| University of Western Australia | Australia | Perth | Oceania | 29 | 32 | 4 |
| Yonsei University | South Korea | Seoul | Asia | 22 | 24 | 5 |

## Dry-run conclusion

Referential integrity holds and the core catalog is present. The additive
migration and alias backfill can proceed; no legacy row requires special
handling beyond the candidate mappings above.

## Data provenance

The pooler host of Supabase project `wydziozsjibkvpgphpia` is unreachable from
this machine (connection timeout, checked 2026-10-25; the deployed API
returned 503 in the same window — see baseline.md), so the audit ran against
a disposable local replica instead of the live database:

1. Every row of the eight core tables was captured read-only through the
   Supabase MCP channel on 2026-10-25.
2. A disposable local PostgreSQL database (this repository's
   `PostgresCluster` test infrastructure) was created with the deployed
   cleaned schema and seeded with the captured rows.
3. Before the audit ran, the replica was verified: exact row counts for all
   eight tables, zero orphan rows, and all six per-degree ranking outputs
   byte-identical to the live baseline recorded in baseline.md.

The numbers above are therefore live-data numbers produced by the script's
own SQL; only the transport channel differed. Re-running the same command
against the live database once the pooler is reachable must produce the same
table of row counts, labels, orphans, and coverage.

## How to re-run

```sh
# From the repository root:
uv run --directory backend python -m scripts.audit_exchange_enhancements \
  --database-url '<local or live postgres url>' \
  --target '<confirmation label>' \
  --output "$PWD/plan/exchange-enhancements/data-audit.md" --force
```

The script reads only, opens one repeatable-read transaction, and never
writes credentials into the report.
