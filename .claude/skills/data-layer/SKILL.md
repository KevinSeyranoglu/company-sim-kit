---
name: data-layer
description: Build the data layer of a company simulation - the star-schema data contract, the data dictionary, the DuckDB build, SQL KPI queries checked against Python, and enterprise-shaped extracts (SAP, AS/400, HL7, POS...) the target employers use. Use when adding tables or columns, writing KPI SQL, or producing exports for Power BI or legacy systems.
---

# Build the data layer

## Contract

- `datalog.TABLES` lists every table and its columns in order. `dim_*` for things (product, customer,
  worker, site), `fact_*` for events and daily snapshots. Keys are short readable codes (`SO0000001`).
- Each fact row is written at the moment a real system would write it, with the fields that system
  would know then. Do not log hidden simulation variables into operational tables; if analysis needs
  them, put them in a clearly named `dim_*` column documented as hidden.
- Every column is documented in `DATA_DICTIONARY.md` in the same change, plus the "How the data is
  generated" section (true mechanisms with their numbers).

## Database

`analytics/build_db.py` loads every run into DuckDB with `run`, `scenario`, `seed` columns. Add views
for common joins only when two or more queries need them.

## SQL KPIs (analytics/sql/NN_name.sql)

- 6–10 queries, one per business question in the spec, numbered, each starting with a comment saying
  the question and the KPI definition.
- `tests/test_data.py` runs every file, and for each headline KPI compares the SQL result with the same
  number computed in pandas from the CSVs (`test_sql_matches_python`). Add one such check per new KPI.
- Use standard SQL that also runs on the dialect the target employers use; note dialect differences
  in a comment when you use DuckDB-only syntax (`GROUP BY ALL`, `FILTER`).

## Enterprise-shaped extracts (choose from the brief)

Recruiters search for system names. Produce the extract the target employers run, from the same run:

| System | What to write | Example check |
|---|---|---|
| SAP S/4HANA | Tables with SAP names (MARA, MATDOC with movement types, VBAK/VBAP, LIKP/LIPS), dates `YYYYMMDD` as text, HANA SQL scripts | SQL on the extract equals the simulation's KPI |
| IBM i / AS/400 | Fixed-width files with a record layout, SAS programs reading them | SAS-style totals equal the CSV totals |
| Power BI | Star-schema CSVs, a guide with DAX measures and a check value for each | Each DAX check value equals the SQL KPI |
| Healthcare | HL7 v2 ADT-style messages or FHIR resources | Census per hour equals the simulation's |
| Retail | POS transaction lines, store/day sales | Sales equal shipped units × price |

Each exporter is one script in `analytics/export_<system>.py` with a test that reconciles it against
the simulation's own numbers. State in its README what was not run on the real system.
