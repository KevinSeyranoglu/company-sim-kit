---
name: calibrate-realism
description: Calibrate a company simulation so its KPIs land in realistic industry ranges and its data carries learnable signal - scenarios must move the KPIs they should, decisions must have a money trade-off. Use after building or changing the simulation flow, or when results look flat, too perfect or unrealistic.
---

# Calibrate realism and signal

A simulation where every order is on time and staffing changes nothing produces data no model can use
and no manager would believe. Calibration is where most of the project's value is made.

## 1. Measure

Run every scenario over at least 3 seeds for 120–180 days (in memory is fastest: a log object that keeps
only `fact_daily_kpi`, as in the starter's tests) and print each KPI's mean and spread per scenario.

## 2. Compare with the spec's ranges

For each KPI in `SPEC.md`, is the baseline inside the industry range? Typical failures and fixes:

| Symptom | Likely cause | Fix |
|---|---|---|
| Service ~100 % in every scenario | Capacity far above load | Raise work content or volume until the baseline runs ~70–85 % busy on average days |
| Lean staffing saves money with no downside | Penalty for bad service too small | Price service failures as the industry does (chargebacks, lost sales, fines) |
| Extra resources always win | Resources too cheap or load too high | Check wages, premiums, and peak vs average load |
| Nothing ever runs out | Buffers too large or replenishment too smart | Make replenishment use the simple rule the industry uses (it ignores seasons, so peaks run short) |
| Metrics identical across days | No weekday, season or event variation | Add the spec's signal list, each for a business reason |

Change one number at a time, in `config.py`, and record why in its comment.

## 3. Check signal

- Each pattern in the spec's "signal to build in" is visible in a simple group-by (weekday, season,
  shift, customer kind, worker skill …). If you cannot see it in SQL, a model will not find it either.
- The baseline policy is reasonable but not optimal, so a better decision exists to be found.
  The warehouse had an over-staffed evening shift because waves were released for morning departures.
- Noise has a floor (order noise, absences) so models cannot be perfect.
- Hidden variables (skill, true season factor) stay out of features but explain results.

## 4. Lock it in with tests

Add or update tests asserting the direction of each scenario's effect (e.g. `lean < base <= extra` for
on-time) and that KPIs stay in range. Calibration that is not tested drifts the next time the flow changes.

## 5. Document

Update `DATA_DICTIONARY.md` "How the data is generated" with every mechanism and number.
