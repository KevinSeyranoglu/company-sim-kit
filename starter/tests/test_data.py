"""The data layer: DuckDB build, every SQL file, the dashboard loader and the multi-seed report."""
from __future__ import annotations

import glob
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "analytics"))

import build_db  # noqa: E402
import main  # noqa: E402
import multiseed  # noqa: E402
from datalog import TABLES  # noqa: E402

pytest.importorskip("duckdb")


@pytest.fixture(scope="module")
def data_dir(tmp_path_factory):
    d = tmp_path_factory.mktemp("data")
    for scenario in ("baseline", "lean_staff"):
        for seed in (1, 2):
            main.main(["--days", "30", "--seed", str(seed), "--scenario", scenario,
                       "--out", str(d / f"{scenario}_seed{seed}")])
    return d


@pytest.fixture(scope="module")
def db(data_dir):
    path = str(data_dir / "test.duckdb")
    build_db.build(str(data_dir), path).close()
    return path


def test_every_table_loaded(db):
    import duckdb
    con = duckdb.connect(db, read_only=True)
    names = {r[0] for r in con.execute("SHOW TABLES").fetchall()}
    assert set(TABLES) <= names
    assert con.execute("SELECT COUNT(DISTINCT run) FROM fact_daily_kpi").fetchone()[0] == 4


def test_every_sql_file_runs(db):
    import duckdb
    con = duckdb.connect(db, read_only=True)
    files = sorted(glob.glob(os.path.join(ROOT, "analytics", "sql", "*.sql")))
    assert files
    for path in files:
        assert len(con.execute(open(path).read()).df()) > 0, path


def test_sql_matches_python(db, data_dir):
    """A KPI computed in SQL equals the same KPI from the CSV: the two paths cannot drift."""
    import duckdb
    import pandas as pd
    con = duckdb.connect(db, read_only=True)
    sql = con.execute("SELECT AVG(on_time) FROM fact_orders WHERE run = 'baseline_seed1'").fetchone()[0]
    csv = pd.read_csv(data_dir / "baseline_seed1" / "fact_orders.csv").on_time.mean()
    assert sql == pytest.approx(csv)


def test_dashboard_loads(db):
    sys.path.insert(0, os.path.join(ROOT, "dashboard"))
    import app
    data = app.load(db)
    assert len(data["daily"]) == 4 * 30 and len(data["shift"]) > 0


def test_multiseed_report(data_dir, tmp_path):
    df = multiseed.report(str(data_dir), str(tmp_path / "MULTISEED.md"))
    m, lo, hi, n = multiseed.paired(df, "lean_staff", "wages")
    assert n == 2 and m < 0 and lo <= m <= hi
    assert "lean_staff" in (tmp_path / "MULTISEED.md").read_text()
