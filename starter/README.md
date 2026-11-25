# {{COMPANY_NAME}}

[![tests](https://github.com/{{GITHUB_USER}}/{{SLUG}}/actions/workflows/tests.yml/badge.svg)](https://github.com/{{GITHUB_USER}}/{{SLUG}}/actions/workflows/tests.yml)

> TODO, once there are findings: one paragraph for a recruiter. The business question, what you built,
> the headline result with its interval, and a link to `docs/CASE_STUDY.md`.

A simulation of a fictional {{INDUSTRY}} company that writes the records a real one would, so every
dashboard and model can be checked against the truth and every policy tested before anyone tries it.

## Quick start

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
python main.py --days 180 --seed 42                 # data/baseline_seed42/
python analytics/build_db.py --sql                  # DuckDB + SQL KPIs
streamlit run dashboard/app.py
python -m pytest tests/ -q
```

## What is inside

| Layer | Files |
|---|---|
| Simulation | `simulation.py`, `config.py`, `main.py` |
| Data | `datalog.py` (contract), `DATA_DICTIONARY.md`, `analytics/build_db.py`, `analytics/sql/` |
| Dashboards | `dashboard/app.py` |
| Models | `ml/` with model cards in `ml/README.md` |
| Evidence | `analytics/multiseed.py` → `docs/MULTISEED.md` |

## Findings

TODO: 3–5 findings, each one sentence with a number and its interval, linking to the generated report.

## Roadmap

- [ ] Spec: company, flow, decisions, KPIs (`SPEC.md`)
- [ ] Simulation of the real flow, calibrated to industry ranges
- [ ] Data contract, dictionary and SQL KPIs
- [ ] Dashboard
- [ ] Models against today's methods, with model cards
- [ ] Multi-seed evaluation
- [ ] Closed-loop test of the model that drives a decision
- [ ] Case study (English and French)

*The company, its suppliers and customers are fictional; the data is simulated on purpose.*
