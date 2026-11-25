"""The models run end to end and keep the rules: time split, honest baseline."""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "ml"))

pytest.importorskip("sklearn")

import main  # noqa: E402


@pytest.fixture(scope="module")
def run_dir(tmp_path_factory):
    d = tmp_path_factory.mktemp("ml") / "baseline_seed42"
    main.main(["--days", "180", "--seed", "42", "--out", str(d)])
    return str(d)


def test_demand_model_beats_last_week(run_dir):
    import demand
    res = demand.evaluate(run_dir, save=False)
    assert res["test_days"] >= 45                 # 180 days, minus 35 for the lags, last third
    assert res["wape_model"] < res["wape_baseline"]


def test_split_is_by_time(run_dir):
    import demand
    from common import split_date
    d = demand.features(demand.daily_units(run_dir))
    cut = split_date(d.date)
    assert d[d.date < cut].date.max() < d[d.date >= cut].date.min()
