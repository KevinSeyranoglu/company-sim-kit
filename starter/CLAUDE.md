# {{COMPANY_NAME}}: simulation for a data science portfolio

A simulation of a fictional {{INDUSTRY}} company. It produces realistic operational data that feeds SQL,
dashboards and ML models answering the questions a real manager in this industry asks. **The data and what
it proves are the product.** An animated view, if any, is the showcase, not the goal.

Built from company-sim-kit. The method is in `.claude/skills/` (one skill per phase) and `docs/PLAYBOOK.md`.

## Commands

```bash
pip install -r requirements-dev.txt
python main.py --days 180 --seed 42 --scenario baseline   # data/baseline_seed42/*.csv (~1 s)
python analytics/build_db.py --sql                        # data/company.duckdb + every analytics/sql/*.sql
python ml/demand.py                                       # ml/results/, ml/figures/
python analytics/multiseed.py run && python analytics/multiseed.py report   # docs/MULTISEED.md
streamlit run dashboard/app.py
python -m pytest tests/ -q                                # must stay green
```

## Layout

| Path | Role |
|---|---|
| `SPEC.md` | What the company is, its flow, its decisions and KPIs. Read it before changing the simulation. |
| `config.py` | Every tuning number and the scenarios. No magic numbers anywhere else. |
| `simulation.py` | Discrete-event engine and the business flow. No drawing, no file I/O except `log.row()`. |
| `datalog.py` | The data contract (`TABLES`): every table and column. `CsvLog` refuses rows that differ. |
| `main.py` | Headless CLI: `--days --seed --scenario --out --staff-plan`. |
| `analytics/` | DuckDB build, SQL KPIs, multi-seed comparison. |
| `ml/` | One file per model, each against today's method, with a model card in `ml/README.md`. |
| `dashboard/app.py` | Streamlit, one tab per business question. |
| `docs/` | Generated reports (never edit numbers by hand), the playbook and the case study. |
| `DATA_DICTIONARY.md` | Every column, plus "how the data is generated" (the true mechanisms). |

## Rules

1. **Reproducible.** Same seed and scenario give byte-identical CSVs. Never call `random` module
   functions or unseeded numpy directly: draw from the simulation's named streams.
2. **Common random numbers.** Demand and supply have their own streams so scenarios with the same seed
   share customers and deliveries. A new source of randomness gets a new stream, not a shared one.
3. **Conserved.** `sim.unit_balance() == 0` always. Any flow that creates or destroys units (scrap, returns,
   recalls) must be added to the balance and to the test.
4. **Data contract first.** A new column goes in `datalog.TABLES`, `DATA_DICTIONARY.md` and the code in
   the same change. Tables with no rows are still written (header only).
5. **Signal, not noise.** Every pattern a model should find must exist in the generator for a business
   reason (weekday, season, customer mix, worker skill, failures) and be documented in the dictionary's
   "how the data is generated". Scenarios must move KPIs: `tests/test_sim.py::test_staffing_moves_service`.
6. **Honest ML.** Time-based split, no feature unknown at decision time, compared against the method the
   industry uses today, value in money with stated assumptions. Report it when a model loses or a rule wins.
7. **One run is one draw.** No scenario or model claim from a single seed: use `analytics/multiseed.py`
   (paired by seed, 95 % interval). A decision a model drives gets a closed-loop test (rerun the
   simulation with the model in charge), because offline value does not always hold.
8. **Generated numbers.** Reports in `docs/` and `ml/RESULTS.md` are written by scripts. Never type a
   number into them by hand; rerun the script.
9. **Fictional.** Invented company, suppliers, customers and products. No real brands or people.
10. **Tests stay green.** Add a test with every invariant or bug fix. CI runs `pytest` on every push.

## Style

- Python 3.11, standard library + pandas, numpy, scikit-learn, scipy, duckdb, streamlit, plotly, matplotlib.
- Match the surrounding code: short docstrings that say why, aligned trailing comments in `config.py`.
- Docs in plain English, short sentences, numbers with units and intervals. Business terms first
  (on-time, fill rate, $ per day), method second.
- Commit subjects describe the change and its finding in one line, e.g.
  "Closed-loop test of the labour model: its offline saving does not hold".
