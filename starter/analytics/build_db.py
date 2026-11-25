"""Load every run under data/ into one DuckDB database, with scenario and seed columns.

    python analytics/build_db.py                  # data/*/run.json -> data/company.duckdb
    python analytics/build_db.py --sql            # also run every analytics/sql/*.sql and print it

A run is a folder written by main.py (it holds run.json). Every table of the data contract becomes
one DuckDB table holding all runs, so scenario comparisons are a GROUP BY scenario, seed.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

import duckdb
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import config as C  # noqa: E402
from datalog import TABLES  # noqa: E402

DB = os.path.join(ROOT, C.DATA_DIR, "company.duckdb")
SQL_DIR = os.path.join(ROOT, "analytics", "sql")


def runs(data_dir):
    for meta in sorted(glob.glob(os.path.join(data_dir, "*", "run.json"))):
        yield os.path.dirname(meta), json.load(open(meta))


def build(data_dir=None, db=None):
    data_dir = data_dir or os.path.join(ROOT, C.DATA_DIR)
    db = db or DB
    found = list(runs(data_dir))
    if not found:
        raise SystemExit(f"no runs in {data_dir}: run python main.py first")
    if os.path.exists(db):
        os.remove(db)
    con = duckdb.connect(db)
    for table in TABLES:
        frames = []
        for folder, meta in found:
            df = pd.read_csv(os.path.join(folder, f"{table}.csv"))
            df.insert(0, "seed", meta["seed"])
            df.insert(0, "scenario", meta["scenario"])
            df.insert(0, "run", os.path.basename(folder))
            frames.append(df)
        con.register("tmp", pd.concat(frames, ignore_index=True))
        con.execute(f"CREATE TABLE {table} AS SELECT * FROM tmp")
        con.unregister("tmp")
    return con


def run_sql(con):
    for path in sorted(glob.glob(os.path.join(SQL_DIR, "*.sql"))):
        print(f"\n-- {os.path.basename(path)}")
        print(con.execute(open(path).read()).df().to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sql", action="store_true")
    a = ap.parse_args()
    con = build()
    print(f"{DB}: {len(TABLES)} tables")
    if a.sql:
        run_sql(con)
