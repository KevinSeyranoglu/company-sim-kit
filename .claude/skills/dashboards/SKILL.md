---
name: dashboards
description: Build dashboards for a company simulation - a Streamlit app with one tab per business question, plus a Power BI (or Tableau) export with a guide, DAX measures and check values, and screenshots for the README. Use when adding or changing dashboard tabs, charts, KPI tiles, or BI exports.
---

# Build the dashboards

## Principles

- **One tab per business question** from the spec (operations, service, labour, supply, quality,
  scenarios, models). The tab title is the question's subject; the first row is 3–5 KPI tiles.
- **Same numbers as SQL.** Load from `data/company.duckdb`; any KPI shown must also exist in
  `analytics/sql/`. `tests/test_data.py::test_dashboard_loads` keeps the loader working.
- **Scenarios and seeds are filters**, and a scenario comparison tab shows means over seeds with a
  link to `docs/MULTISEED.md` for intervals.
- **Model vs baseline** always in the same two colours (`ml/common.py`: model blue, baseline orange).
- Read the `dataviz` skill (if available) before choosing chart types and colours.

## Streamlit (dashboard/app.py)

- Keep data loading in `load()` (testable, no Streamlit import), drawing in `main()`.
- Cache with `st.cache_data` once loading takes more than a second.
- Add a sidebar language switch if the case study is bilingual.
- For a public demo: commit a small sample database (one seed, 60 days) under `dashboard/sample/` and
  fall back to it when `data/` is missing, then deploy on Streamlit Community Cloud. The user does the
  deploy from their account.

## Power BI / Tableau (if the target jobs ask for it)

- `analytics/export_powerbi.py`: the star-schema CSVs with clean column names and a date table.
- `dashboard/POWERBI_GUIDE.md`: model relationships, each DAX measure, and for each a **check value**
  (the number it must show on the published run) taken from SQL, so a reviewer can verify it.
- A theme JSON in the project's palette.

## Screenshots

Take them from the running app (browser preview) at a fixed window size, save to `docs/`, and refresh
them whenever the data is regenerated. The README shows one; the case study may show two.
