"""Shared helpers for the ML models: data access, the time split, metrics and figure style.

Every model trains on the first TRAIN_FRACTION of a run's days and is evaluated on the days after
(time-based split, never random), using only information available when the decision is made.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import config as C  # noqa: E402

RUN_DIR = os.environ.get("RUN_DIR", os.path.join(ROOT, C.DATA_DIR, "baseline_seed42"))
FIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
TRAIN_FRACTION = 2 / 3
SEED = 42

# model vs baseline are always these two colours, in every figure and dashboard
MODEL_COLOR, BASE_COLOR, ACTUAL_COLOR = "#2a78d6", "#eb6834", "#52514e"


def table(name, run_dir=None):
    path = os.path.join(run_dir or RUN_DIR, f"{name}.csv")
    if not os.path.exists(path):
        raise SystemExit(f"{path} not found: run python main.py --days 180 first")
    return pd.read_csv(path)


def split_date(dates):
    """First date of the test period."""
    days = sorted(pd.unique(pd.Series(dates)))
    return days[int(len(days) * TRAIN_FRACTION)]


def wape(actual, pred):
    actual, pred = np.asarray(actual, float), np.asarray(pred, float)
    return float(np.abs(actual - pred).sum() / max(actual.sum(), 1e-9))


def figure(name):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.color": "#e1e0d9",
                         "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False})
    fig, ax = plt.subplots(figsize=(8, 3.6))
    os.makedirs(FIG_DIR, exist_ok=True)
    return fig, ax, os.path.join(FIG_DIR, name)
