---
name: ml-models
description: Build an ML model for a company simulation that is scored in money against the method the industry uses today - time-based split, leakage checks, model card, generated results, honest reporting when a rule wins. Use when adding or changing a model in ml/, or when asked what a model is worth.
---

# Build a model

One file per model in `ml/`, one card in `ml/README.md`, results generated into `ml/results/` and
summarised in `ml/RESULTS.md` by a script (`ml/train_all.py` once there are several).

## Before coding: fill the card

Decision · unit (e.g. product × day) · features · model · **baseline (today's method)** · metric ·
**$ assumption** · limits. If the baseline or the $ assumption is unclear, ask; they decide whether the
result means anything.

## Rules

1. **Time-based split** (`common.split_date`): first two thirds train, last third test. Never random.
2. **No leakage.** Features known at decision time only (lags ≥ the decision horizon, calendar facts,
   forecasts not actuals). Never hidden simulation variables (true skill, true season factor, hidden
   flags). Add a test asserting the split is by time and listing forbidden features.
3. **Today's method first.** Implement the baseline exactly as the industry does it (same weekday last
   week, fixed roster, a threshold rule), score it on the same test days, then the model.
4. **Money.** Value per day = model's net benefit − baseline's, with every assumption in the card.
   Count only what you can defend (e.g. under-forecasts at the lost margin, over-forecasts in units).
5. **Several seeds.** Rerun on the 5 seeds (`analytics/multiseed.py` pattern) and report mean and
   interval; a model that wins on one seed only has not won.
6. **Report losses.** If a simple rule beats the model, say so and keep the rule. In the warehouse, a
   one-line shelf-life rule beat the spoilage model, and the honest report made the other results
   more credible.
7. **Check against the truth.** The data dictionary says how the data is generated. A model that finds
   the real mechanism (feature importance, partial dependence) and not an artefact is the check.
8. **If the model drives a decision**, its offline value is not enough: run `closed-loop-test`.

## Typical models by decision

| Decision | Model | Baseline | Metric |
|---|---|---|---|
| How much to order / produce | Gradient boosting, Poisson loss | Same weekday last week | WAPE, lost margin $ |
| How many people per shift | Forecast + capacity curve per shift | Fixed roster | Wages + service penalties $ |
| Which items/orders are at risk | Classifier, calibrated | A threshold rule | PR-AUC, precision@k, $ saved |
| Equipment / quality early warning | Anomaly detection or classifier | Fixed alarm threshold | Lead time, false alarms per week |

## Figures

`common.figure()` for style; model vs baseline in the fixed colours; save to `ml/figures/` and use
the best one in the README and the case study.
