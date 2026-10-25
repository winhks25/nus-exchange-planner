"""Generate reviewed task 6–7 SQL from captured official-source evidence.

No network or database writes are performed by this tool. Apply the generated
transaction only after reviewing it and capturing a backup. Missing modules or
unknown universities fail closed so an incomplete API fetch cannot delete data.
"""

import argparse
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from psycopg import sql


def cleanup_sql(modules: list[dict], locations: list[dict]) -> str:
    """Validate evidence and generate an atomic, rerunnable cleanup transaction."""
    if not modules or not locations:
        raise ValueError("Module and location evidence must be nonempty")
    codes = set()
    module_values = []
    for row in modules:
        code, title = row["code"], row["title"]
        if not isinstance(code, str) or not code.strip() or code in codes:
            raise ValueError("Module codes must be nonempty and unique")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"Missing official title for {code}; review before deletion")
        try:
            units = Decimal(str(row["units"]))
        except InvalidOperation:
            raise ValueError(f"Invalid credits for {code}") from None
        if not units.is_finite() or units <= 0:
            raise ValueError(f"Invalid credits for {code}")
        codes.add(code)
        module_values.append(
            sql.SQL("({}, {}, {})").format(
                sql.Literal(code), sql.Literal(title), sql.Literal(units)
            )
        )
    names = set()
    location_values = []
    for row in locations:
        fields = [row[k] for k in ("name", "city", "country", "continent")]
        if any(not isinstance(v, str) or not v.strip() for v in fields):
            raise ValueError("Location fields must be nonempty")
        if fields[0] in names or not row.get("source", "").startswith("https://"):
            raise ValueError("Locations must be unique and cite a source")
        names.add(fields[0])
        location_values.append(
            sql.SQL("({}, {}, {}, {})").format(*(sql.Literal(value) for value in fields))
        )
    return (
        sql.SQL("""
begin;
set local lock_timeout = '5s';
set local statement_timeout = '30s';
lock table public.nus_modules, public.partner_universities in access exclusive mode;
create temporary table cleanup_modules(code text primary key, title text, units numeric)
  on commit drop;
insert into cleanup_modules values {modules};
create temporary table cleanup_locations(name text primary key, city text, country text,
  continent text) on commit drop;
insert into cleanup_locations values {locations};
do $$
begin
  if exists (select code from public.nus_modules except select code from cleanup_modules)
     or exists (select code from cleanup_modules except select code from public.nus_modules)
     or exists (select name from public.partner_universities
                except select name from cleanup_locations)
     or exists (select name from cleanup_locations
                except select name from public.partner_universities) then
    raise exception 'Catalog changed or evidence incomplete; capture and review again';
  end if;
  if exists (select 1 from information_schema.columns where table_schema='public'
             and table_name='nus_modules' and column_name='offering_faculty') then
    alter table public.nus_modules rename column offering_faculty to faculty;
  end if;
  if exists (select 1 from information_schema.columns where table_schema='public'
             and table_name='nus_modules' and column_name='verified_units') then
    alter table public.nus_modules rename column verified_units to units;
  end if;
end $$;
update public.nus_modules n set name=e.title, units=e.units, faculty='School of Computing'
from cleanup_modules e where n.code=e.code;
update public.partner_universities u set city=e.city, country=e.country, continent=e.continent
from cleanup_locations e where u.name=e.name;
alter table public.partner_universities drop column if exists source_order;
commit;
""")
        .format(
            modules=sql.SQL(",\n").join(module_values),
            locations=sql.SQL(",\n").join(location_values),
        )
        .as_string()
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modules", type=Path, required=True)
    parser.add_argument("--locations", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    evidence = json.loads(args.modules.read_text())
    args.output.write_text(cleanup_sql(evidence["modules"], json.loads(args.locations.read_text())))


if __name__ == "__main__":
    main()
