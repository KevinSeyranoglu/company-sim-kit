"""Simulation invariants. Every later layer (SQL, dashboards, models) trusts these.

    python -m pytest tests/ -q
"""
from __future__ import annotations

import hashlib
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import config as C  # noqa: E402
import main  # noqa: E402
from datalog import TABLES, CsvLog  # noqa: E402
from simulation import Simulation  # noqa: E402


class MemLog:
    def __init__(self):
        self.rows = {}

    def row(self, table, **fields):
        self.rows.setdefault(table, []).append(fields)

    def flush(self):
        pass


def kpis(seed=42, scenario="baseline", days=60, plan=None):
    log = MemLog()
    sim = Simulation(seed=seed, scenario=scenario, datalog=log, staff_plan=plan).run(days)
    return sim, log


def test_units_are_conserved():
    for scenario in C.SCENARIOS:
        sim, _ = kpis(scenario=scenario, days=45)
        assert sim.unit_balance() == 0, scenario


def test_same_seed_same_data(tmp_path):
    digests = []
    for i in range(2):
        out = tmp_path / f"r{i}"
        main.main(["--days", "20", "--seed", "5", "--out", str(out)])
        digests.append({t: hashlib.md5((out / f"{t}.csv").read_bytes()).hexdigest() for t in TABLES})
    assert digests[0] == digests[1]


def test_different_seeds_differ():
    a = kpis(seed=1, days=10)[1].rows["fact_daily_kpi"]
    b = kpis(seed=2, days=10)[1].rows["fact_daily_kpi"]
    assert a != b


def test_rows_match_the_contract(tmp_path):
    log = CsvLog(str(tmp_path))
    Simulation(seed=3, datalog=log).run(10)          # CsvLog raises on any field mismatch
    log.close()
    for table in TABLES:
        assert (tmp_path / f"{table}.csv").exists(), table


def test_scenarios_share_demand():
    """Common random numbers: staffing must not change what customers order."""
    base = kpis(scenario="baseline", days=30)[1].rows["fact_order_lines"]
    lean = kpis(scenario="lean_staff", days=30)[1].rows["fact_order_lines"]
    key = lambda rows: sorted((r["order_id"], r["product_code"], r["units_ordered"]) for r in rows)  # noqa: E731
    assert key(base) == key(lean)


def mean(rows, key):
    vals = [r[key] for r in rows if r[key] == r[key]]
    return sum(vals) / len(vals)


def test_staffing_moves_service():
    """The data must carry signal: fewer people, fewer orders on time."""
    lean = mean(kpis(scenario="lean_staff", days=60)[1].rows["fact_daily_kpi"], "on_time")
    base = mean(kpis(scenario="baseline", days=60)[1].rows["fact_daily_kpi"], "on_time")
    extra = mean(kpis(scenario="extra_staff", days=60)[1].rows["fact_daily_kpi"], "on_time")
    assert lean < base <= extra


def test_staff_plan_is_applied():
    plan = {"2025-12-02": {"day": 2, "evening": 2, "night": 1}}
    _, log = kpis(days=3, plan=plan)
    rostered = [r for r in log.rows["fact_labor"] if r["date"] == "2025-12-02" and r["shift"] == "day"]
    assert len(rostered) == 2


def test_no_backlog_left_on_a_normal_day():
    _, log = kpis(days=30)
    assert max(r["backlog_end"] for r in log.rows["fact_daily_kpi"]) < 30


@pytest.mark.parametrize("table", ["fact_orders", "fact_labor"])
def test_timestamps_are_iso(table):
    _, log = kpis(days=3)
    ts = next(v for r in log.rows[table] for k, v in r.items() if k.endswith("_ts") and v)
    assert len(ts) == 19 and ts[10] == "T"
