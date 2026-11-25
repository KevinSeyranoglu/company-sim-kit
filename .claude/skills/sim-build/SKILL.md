---
name: sim-build
description: Build or extend the discrete-event simulation of a company from its SPEC.md - entities, events, resources, random streams, conservation and the data contract, with invariant tests. Use when turning the spec's flow into code, adding a process step, a resource or a random event to simulation.py.
---

# Build the simulation

The starter's `simulation.py` is a working order-fulfilment engine. Replace its flow with the spec's
flow step by step, keeping the tests green after each step.

## Architecture (keep it)

- **Event heap** (`schedule(t, kind, **payload)` → `_ev_<kind>` handlers), time in minutes. Use a fixed
  time step only for continuous things (temperatures, vehicle movement) and only if needed.
- **No drawing and no I/O** in the simulation except `self.log.row(table, **fields)`. A renderer, if any,
  reads the state (see `visual-showcase`).
- **All numbers in `config.py`**, with a comment giving the meaning and, for industry numbers, the source.
- **Scenarios** are dicts of overrides in `config.SCENARIOS`, read once in `__init__`.
- **Decision hooks**: each decision a model will drive gets an input that overrides the default policy
  (like `staff_plan`), so the closed-loop test can put a model in charge without editing the engine.

## Randomness

- One `random.Random(f"{seed}-{name}")` stream per source (demand, supply, ops, equipment …). Never the
  global `random` or unseeded numpy.
- Exogenous randomness (what customers order, when suppliers arrive, weather) must not depend on
  decisions, so scenarios with the same seed share it. Draw it up front per day where possible, as the
  starter does in `_ev_day_start`. `tests/test_sim.py::test_scenarios_share_demand` guards this.

## Order of work

1. Entities as dataclasses (what has state: orders, patients, trucks, machines, workers).
2. The flow, one step at a time; after each, run 30 days headless and look at the rows.
3. Resources and capacity (people per shift and role, equipment, rooms, doors), with queues and a clear
   dispatch rule (earliest due, FIFO, priority), the way the real operation does it.
4. Random events from the spec, each logged to `fact_events`.
5. Money: revenue, every cost and penalty, a daily KPI row.

## Invariants (tests/test_sim.py)

- **Conservation**: every unit (case, patient, parcel) is in exactly one place; extend `unit_balance()`
  for each new flow (scrap, returns, recalls). It found two leaks in the warehouse project.
- **Reproducible**: same seed → identical CSV bytes.
- **No deadlock**: backlog stays bounded over 60+ days in every scenario.
- **Contract**: `CsvLog` raises on unknown tables or fields; add new columns to `datalog.TABLES` and
  `DATA_DICTIONARY.md` in the same change.
- **Speed**: 180 days headless should take well under a minute, so 5 seeds × 5 scenarios stays cheap.
  Profile with `python -m cProfile -s cumtime main.py --days 30` before optimising.

## Done when

The spec's whole flow runs, every record in the spec's list is written, and `pytest` passes. Then go to
`calibrate-realism`.
