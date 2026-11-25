# company-sim-kit

Everything needed to build a portfolio project like the
[Boréal Viandes warehouse simulation](https://github.com/KevinSeyranoglu/boreal-viandes-warehouse-sim)
for any other company: a working starter project, a playbook, and Claude Code skills for every phase.

A simulated company writes the same records a real one would, so every dashboard and model can be
checked against the truth and every policy tested before anyone tries it. The data and what it proves
are the product.

## Start a new company

**With Claude Code** (recommended): open this folder in Claude Code and say
*"start a new company simulation"*. The `new-company-sim` skill asks about your target jobs, helps you
pick the industry and a fictional name, and generates the repo.

**By hand:**

```bash
python new_project.py "Maple Ridge Bakery" --industry "industrial bakery" --dest ~/Desktop/Projects
cd ~/Desktop/Projects/maple-ridge-bakery
python -m venv .venv && . .venv/bin/activate && pip install -r requirements-dev.txt
python main.py --days 180 && python analytics/build_db.py --sql
```

Then open the new repo in Claude Code: its `CLAUDE.md` and skills load, and the next step is the spec.

## What is inside

| Path | What it is |
|---|---|
| `PLAYBOOK.md` | The method, phase by phase, with what the warehouse project taught |
| `.claude/skills/` | One Claude Code skill per phase (see below); copied into every new repo |
| `starter/` | A working generic company: discrete-event simulation, data contract, DuckDB + SQL, multi-seed evaluation, a demand model, Streamlit dashboard, 17 tests, CI, `CLAUDE.md`, spec / dictionary / case study templates |
| `templates/COMPANY_BRIEF.md` | The intake questions: target jobs, tools, industry |
| `briefs/` | Filled briefs, one per company |
| `new_project.py` | Generates a new repo from `starter/` |
| `tests/` | Checks that a generated project passes its own tests |

## Skills

| Phase | Skill | Use it to |
|---|---|---|
| 0 | `new-company-sim` | Interview, pick the company, generate the repo (kit only) |
| 1 | `company-spec` | Research the industry and write `SPEC.md`: flow, decisions, KPIs with ranges |
| 2 | `sim-build` | Turn the flow into the simulation with invariant tests |
| 3 | `calibrate-realism` | Make KPIs realistic and decisions matter |
| 4 | `data-layer` | Contract, dictionary, SQL KPIs, SAP / AS/400 / HL7 / POS-style extracts |
| 5 | `dashboards` | Streamlit tabs, Power BI export with DAX check values |
| 6 | `ml-models` | Models vs today's method, in money, with cards |
| 7 | `multiseed-eval` | Paired seeds and 95 % intervals before any claim |
| 8 | `closed-loop-test` | Run the simulation with the model in charge |
| 9 | `case-study`, `visual-showcase` | Recruiter case study (two languages), README, optional animation |

To have the skills everywhere, not only in these repos: `cp -r .claude/skills/* ~/.claude/skills/`.

## The starter company

A generic order-fulfilment operation: 30 customers order 5 products from 06:00 to 20:00, stock is
topped up nightly, and a crew on three shifts works orders earliest-due first. It is calibrated so
staffing has a real trade-off (lean staffing about breaks even on profit but loses ~9 points of
on-time), it carries weekday, season and skill signal, and it has a demand model that beats "same
weekday last week". Replace its flow with your company's; keep its properties (reproducible, common
random numbers, conserved, contract-checked).

## Develop the kit

```bash
pip install -r starter/requirements-dev.txt
python -m pytest tests -q          # generates a project in a temp folder and runs its tests
```

When a company project teaches something new, add it to `PLAYBOOK.md` and the matching skill, and if
it is generic, to `starter/`.
