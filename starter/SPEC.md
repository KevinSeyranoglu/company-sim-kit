# {{COMPANY_NAME}}: spec

**Purpose:** a data science portfolio project aimed at {{INDUSTRY}} employers. The simulation produces
realistic operational data; that data feeds SQL, dashboards and ML models that answer real questions of
this industry. The data and the findings are the goal.

> Fill every section before writing simulation code (the `company-spec` skill walks through it).
> Replace the `TODO` lines; delete this note when done.

## Target jobs
TODO: the job titles and 3–5 employers this project should impress, and the tools their postings name
(SQL dialect, BI tool, ERP, Python libraries). Every later choice is checked against this list.

## The company (fictional)
TODO: what it does, size (sites, people, customers, volume per day), where, what it does NOT do.
No real brands.

## The flow
TODO: the physical or service flow as numbered steps, from what comes in to what goes out. For each
step: who or what does it, how long it takes, what can go wrong, what record a real system writes.

1. TODO
2. TODO

## Resources and constraints
TODO: people (roles, shifts, skills), equipment, capacity limits, opening hours, service promises.

## Decisions a manager makes
TODO: 4–6 recurring decisions, each with how it is made today (the baseline a model must beat) and
what a wrong decision costs in money.

| Decision | How it is made today | Cost of a wrong call |
|---|---|---|
| TODO | TODO | TODO |

## KPIs
TODO: the 6–10 numbers this industry runs on, with their exact definition and a realistic range
(cite the source of the range: industry report, public benchmark, job posting).

| KPI | Definition | Realistic range |
|---|---|---|
| TODO | TODO | TODO |

## Signal to build in
TODO: every pattern the data must carry and why it exists in the business (weekday and season, customer
mix, skill spread, equipment failures, supplier quality, weather …). These are what the models find.

## Random events
TODO: disruptions with rough frequencies (absences, breakdowns, late suppliers, rush orders, recalls …).

## Scenarios
TODO: 4–6 what-if variants (staffing, layout, policy, supply trouble). `baseline` is the published run.

## Records (data contract outline)
TODO: the tables a real system here would hold (ERP, WMS, POS, CRM, scheduling …) and the extracts an
employer would recognise. Detailed columns go in `datalog.py` and `DATA_DICTIONARY.md`.

## Models
TODO: 3–5 models, one per decision above, each with its baseline and how its value is measured in money.

## Out of scope
TODO: what this project will not model, on purpose.
