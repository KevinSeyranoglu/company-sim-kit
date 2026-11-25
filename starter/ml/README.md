# Machine-learning models: model cards

Rules followed by every model:
- **Time-based split.** Train on the first two thirds of a 180-day run and test on the last third, never a
  random split.
- **No leakage.** Only information available when the decision is made. Hidden simulation variables
  (worker skill, true season factor) are never features.
- **An honest baseline.** Each model is compared with the simple method the industry uses today, both
  scored on the same test days.
- **Money with stated assumptions.** Value per day = the model's net benefit minus the baseline's. Every
  assumption is listed in the card. A result is reported even when the model loses.
- **Several seeds.** A claim holds over 5 seeds (`analytics/multiseed.py`), not one run.

Copy the card below for each new model.

---

## 1. Demand forecast (`demand.py`)

| | |
|---|---|
| **Decision** | How much to order from suppliers tonight and how much work to plan tomorrow |
| **Unit** | Product × day |
| **Features** | Lags 7 and 14, mean of the same weekday over 4 weeks, 28-day mean (lagged 7), weekday, season flags (calendar facts), product |
| **Model** | `HistGradientBoostingRegressor`, Poisson loss |
| **Baseline** | Same weekday last week |
| **Metric** | WAPE (sum of absolute errors / sum of actuals) |
| **$ assumption** | An under-forecast unit is a lost sale worth its margin; over-forecasts are not valued |
| **Result** | `ml/results/demand.json` (generated) |
| **Limits** | TODO once the company's real flow replaces the starter |
