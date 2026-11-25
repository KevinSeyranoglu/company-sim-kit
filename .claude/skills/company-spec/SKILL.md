---
name: company-spec
description: Write or complete SPEC.md for a company simulation - the business flow, the decisions a manager makes and how they are made today, the KPIs with realistic ranges, the signal the data must carry, scenarios and the records a real system would hold. Use before writing simulation code, or when SPEC.md still has TODO lines.
---

# Write the spec

The spec is the contract for everything after it. A table, chart or model that does not trace back to
a decision in the spec does not belong in the project.

## Inputs

- `docs/BRIEF.md` (target jobs, tools, language) if it exists; otherwise ask for target jobs first.
- The `SPEC.md` template in the repo root.

## Steps

1. **Research the industry before writing.** Use web search for: how the operation actually runs
   (process descriptions, trade associations, operations textbooks, job postings for floor roles), the
   KPIs it reports and their typical ranges (benchmark reports), and the systems it runs (ERP, WMS, POS,
   scheduling). Note every source; the ranges go in the KPI table with their source.
2. **Flow.** Numbered steps from input to output. For each: who/what does it, duration distribution,
   what goes wrong and how often, and the record a real system writes at that moment. These records
   become the fact tables.
3. **Decisions.** 4–6 recurring ones. For each: how it is made today (this is the baseline every model
   must beat: a rule of thumb, last week's number, a fixed roster) and what a wrong call costs in money.
   Prefer decisions with a real trade-off (labour vs service, stock vs waste, speed vs quality).
4. **KPIs.** 6–10, exact formula, realistic range with source. Include at least one service KPI
   (on-time, wait time), one cost KPI and one quality/compliance KPI.
5. **Signal.** List each pattern the data must carry and its business reason: weekday and season,
   holidays, customer or patient mix, worker skill spread, equipment failures, supplier quality,
   weather. Each is something a model or analysis will later find. Also list deliberate noise floors.
6. **Events and scenarios.** Disruptions with frequencies; 4–6 scenarios, each changing one decision
   or condition, `baseline` first.
7. **Records.** Name the tables and the enterprise extracts the target employers would recognise
   (SAP tables, an AS/400 extract, HL7 / ADT for hospitals, ACD logs for call centres …).
8. **Models.** One per decision, with its baseline and its money metric.
9. **Out of scope.** Say what is not modelled, so reviewers see it was a choice.

## Checks before finishing

- No TODO left; every KPI has a range and a source.
- Every model maps to a decision, and every decision has today's method written down.
- The company, suppliers, customers and products are fictional.
- Show the user the decisions and models table and ask for a go-ahead before `sim-build`.
