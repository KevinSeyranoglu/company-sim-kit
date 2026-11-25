# Playbook: a company simulation for a data science portfolio

The method behind the Boréal Viandes warehouse project, written so it can be repeated for any company.
Each phase has a skill in `.claude/skills/` that Claude Code loads when you work on that phase.

**The idea.** Real operational data is private, so build the company. A simulation that writes the same
records a real system would gives you data with a known generating process: every model can be checked
against the truth, and every policy can be tested before anyone tries it. The data and what it proves
are the product; any animation is the showcase.

## Phases

| # | Phase | Skill | Done when |
|---|---|---|---|
| 0 | Pick the company | `new-company-sim` | A one-page brief names the target jobs, and the repo exists |
| 1 | Spec | `company-spec` | `SPEC.md` has no TODO: flow, decisions with today's method, KPIs with ranges |
| 2 | Simulation | `sim-build` | The real flow runs headless for 180 days in under a minute; invariant tests pass |
| 3 | Realism and signal | `calibrate-realism` | KPIs sit in industry ranges; each scenario moves the KPI it should |
| 4 | Data layer | `data-layer` | Contract, dictionary, DuckDB, 6–10 SQL KPIs, one enterprise-shaped extract |
| 5 | Dashboards | `dashboards` | One tab per business question; numbers match SQL |
| 6 | Models | `ml-models` | 3–5 models, each vs today's method, in money, with a card |
| 7 | Evidence | `multiseed-eval` | Every claim holds over 5 seeds with a paired 95 % interval |
| 8 | Closed loop | `closed-loop-test` | The model that drives a decision has been run in charge of the simulation |
| 9 | Showcase | `case-study`, `visual-showcase` | README front page, case study EN + FR, screenshots, CI badge |

Work in this order. Phases 4–8 depend on 2–3 being right: a flat or unrealistic simulation makes every
later result worthless, and that is where most of the time should go.

## What the warehouse project taught

1. **Spec first, in business terms.** The spec named the decisions (crew size, dock process, which pallets
   to discount) before any code. Every later table, chart and model traced back to one of them.
2. **Calibrate until decisions matter.** The first version had staffing that changed nothing. A test now
   asserts that fewer people means fewer orders on time; without it, no labour model can show value.
3. **Realism comes from mechanisms, not noise.** Spoilage came from aged supplier loads, late orders from
   wave timing, the evening-shift waste from when waves were released. Each finding was a mechanism
   built in for a business reason, then rediscovered from the data.
4. **Count everything.** A conservation test (cases in = cases out + on hand) found two recall leaks that
   no KPI showed.
5. **Records shaped like real systems.** A WMS scan log, an AS/400 fixed-width extract with SAS programs,
   SAP S/4HANA tables with HANA SQL. Recruiters search for those words; pick the systems the target
   employers use.
6. **Beat today's method, in money.** Every model was compared with what the company does now (same
   weekday last week, fixed crew, a shelf-life rule). A one-line rule beat the spoilage model, and saying
   so made the other results more credible.
7. **One run is one draw.** With a single seed, adding pickers looked profitable; over 5 seeds it was a
   loss. Pair scenarios by seed (common random numbers) and report 95 % intervals.
8. **Test the decision, not the model.** The daily labour plan promised $815 a day offline and lost money
   when it ran the simulation. Asking why (per shift, the evening crew was idle) produced the best result
   of the project: $3,500 a day, service unchanged.
9. **Generated numbers only.** Reports are written by scripts, so docs never drift from code.
10. **Tell it as a case study.** One page: the question, what was built, five findings with numbers,
    what to tell a manager, what was learned. English and French.

## Choosing the next company

Good candidates have: a physical or service flow with queues and capacity, recurring decisions with a
money trade-off, public KPI benchmarks, and employers you want to work for. Examples:

| Company | Flow | Decisions to model | Records |
|---|---|---|---|
| Grocery store chain | Deliveries → shelves → checkout | Ordering, markdowns, cashier staffing | POS, inventory, scheduling |
| Hospital emergency department | Arrival → triage → treatment → discharge | Nurse staffing, bed assignment | ADT events, triage scores |
| Bike / car-share network | Trips between stations | Rebalancing trucks, station sizes | Trip log, station status |
| Call centre | Calls → queue → agents | Staffing by half-hour, routing | ACD log, call outcomes |
| Bakery or food plant | Raw materials → lines → packing | Production plan, changeovers, scrap | MES, quality checks |
| Last-mile delivery depot | Parcels → routes → drivers | Route count, cut-off time | Scan events, proof of delivery |
| Airline ground handling | Flights → turnarounds → crews | Crew rostering, delay recovery | Turn events, delay codes |
| Bank branch / loans | Applications → review → decision | Staffing, approval threshold | Application log, defaults |

Choose the one closest to the jobs you are applying for; reuse the starter's engine and change the flow.
