"""Demand forecast: units per product per day, against the method used today (same weekday last week).

    python ml/demand.py          # -> ml/results/demand.json, ml/figures/demand.png

Decision it serves: how much to order from suppliers tonight and how much work to plan tomorrow.
Features use only what is known the evening before: calendar, season flags, lags of 7 days or more.
"""
from __future__ import annotations

import json
import os

import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from common import (ACTUAL_COLOR, BASE_COLOR, MODEL_COLOR, RESULTS_DIR, SEED, figure, split_date, table,
                    wape)
import config as C


def daily_units(run_dir=None):
    o = table("fact_orders", run_dir)[["order_id", "created_ts"]]
    lines = table("fact_order_lines", run_dir).merge(o, on="order_id")
    lines["date"] = pd.to_datetime(lines.created_ts).dt.normalize()
    d = lines.groupby(["product_code", "date"]).units_ordered.sum().unstack(0).asfreq("D").fillna(0)
    return d.stack().rename("units").reset_index()


def features(d):
    d = d.sort_values(["product_code", "date"]).copy()
    g = d.groupby("product_code").units
    d["lag7"] = g.shift(7)
    d["lag14"] = g.shift(14)
    d["same_wd_4w"] = sum(g.shift(7 * k) for k in range(1, 5)) / 4
    d["mean28_lag7"] = g.transform(lambda s: s.shift(7).rolling(28).mean())
    d["weekday"] = d.date.dt.day_of_week
    md = d.date.dt.strftime("%m-%d")
    for name, (first, last, _) in C.SEASONS.items():          # calendar facts, not the hidden factor
        d[f"season_{name}"] = ((md >= first) & (md <= last)).astype(int)
    d["product"] = d.product_code.astype("category").cat.codes
    return d.dropna()


def evaluate(run_dir=None, save=True):
    d = features(daily_units(run_dir))
    cut = split_date(d.date)
    train, test = d[d.date < cut], d[d.date >= cut].copy()
    X = [c for c in d.columns if c not in ("product_code", "date", "units")]
    model = HistGradientBoostingRegressor(loss="poisson", max_iter=300, learning_rate=0.05,
                                          categorical_features=[X.index("product")], random_state=SEED)
    model.fit(train[X], train.units)
    test["model"] = model.predict(test[X])
    test["baseline"] = test.lag7
    margin = {p: v[1] - v[2] for p, v in C.PRODUCTS.items()}
    under = lambda col: float(((test.units - test[col]).clip(lower=0) * test.product_code.map(margin)).sum())  # noqa: E731
    days = test.date.nunique()
    res = {
        "test_days": int(days), "train_until": str(pd.Timestamp(cut).date()),
        "wape_model": round(wape(test.units, test.model), 4),
        "wape_baseline": round(wape(test.units, test.baseline), 4),
        # assumption: an under-forecast unit is a lost sale worth its margin; over-forecasts are not valued
        "lost_margin_per_day_model": round(under("model") / days, 0),
        "lost_margin_per_day_baseline": round(under("baseline") / days, 0),
    }
    res["value_per_day"] = res["lost_margin_per_day_baseline"] - res["lost_margin_per_day_model"]
    if save:
        os.makedirs(RESULTS_DIR, exist_ok=True)
        json.dump(res, open(os.path.join(RESULTS_DIR, "demand.json"), "w"), indent=1)
        tot = test.groupby("date")[["units", "model", "baseline"]].sum()
        fig, ax, path = figure("demand.png")
        ax.plot(tot.index, tot.units, color=ACTUAL_COLOR, label="Actual")
        ax.plot(tot.index, tot.model, color=MODEL_COLOR, label=f"Model (WAPE {res['wape_model']:.1%})")
        ax.plot(tot.index, tot.baseline, color=BASE_COLOR, ls="--",
                label=f"Same weekday last week (WAPE {res['wape_baseline']:.1%})")
        ax.set_ylabel("Units ordered per day")
        ax.legend()
        fig.tight_layout()
        fig.savefig(path, dpi=130)
    return res


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=1))
