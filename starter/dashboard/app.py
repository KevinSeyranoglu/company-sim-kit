"""Streamlit dashboard over data/company.duckdb.

    python analytics/build_db.py && streamlit run dashboard/app.py

Grow it one tab per business question (operations, labour, supply, models). Every number shown should
also be reachable from a SQL file in analytics/sql, so the dashboard and the analysis never disagree.
"""
from __future__ import annotations

import os
import sys

import duckdb
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import config as C  # noqa: E402

DB = os.path.join(ROOT, C.DATA_DIR, "company.duckdb")


def load(db=DB) -> dict[str, pd.DataFrame]:
    con = duckdb.connect(db, read_only=True)
    out = {
        "daily": con.execute("SELECT * FROM fact_daily_kpi ORDER BY scenario, seed, date").df(),
        "shift": con.execute("""
            SELECT scenario, shift, SUM(hours) AS hours, SUM(units_done) AS units
            FROM fact_labor WHERE absent = 0 GROUP BY ALL ORDER BY ALL""").df(),
    }
    con.close()
    out["daily"]["date"] = pd.to_datetime(out["daily"]["date"])
    return out


def main():
    import plotly.express as px
    import streamlit as st

    st.set_page_config(page_title=C.COMPANY_NAME, layout="wide")
    st.title(C.COMPANY_NAME)
    if not os.path.exists(DB):
        st.error("No database yet: run `python main.py` then `python analytics/build_db.py`.")
        return
    data = load()
    daily = data["daily"]
    scenarios = sorted(daily.scenario.unique())
    scenario = st.sidebar.selectbox("Scenario", scenarios,
                                    index=scenarios.index("baseline") if "baseline" in scenarios else 0)
    seed = st.sidebar.selectbox("Seed", sorted(daily[daily.scenario == scenario].seed.unique()))
    d = daily[(daily.scenario == scenario) & (daily.seed == seed)]

    ops, labour, compare = st.tabs(["Operations", "Labour", "Scenarios"])
    with ops:
        c = st.columns(4)
        c[0].metric("On-time", f"{d.on_time.mean():.1%}")
        c[1].metric("Fill rate", f"{d.fill_rate.mean():.2%}")
        c[2].metric("Orders / day", f"{d.orders.mean():,.0f}")
        c[3].metric("Profit / day", f"{C.CURRENCY}{d.profit.mean():,.0f}")
        st.plotly_chart(px.line(d, x="date", y="units_ordered", title="Units ordered per day"),
                        width="stretch")
        st.plotly_chart(px.line(d, x="date", y="on_time", title="On-time share per day"), width="stretch")
    with labour:
        s = data["shift"][data["shift"].scenario == scenario].copy()
        s["units_per_hour"] = s.units / s.hours
        st.dataframe(s, hide_index=True)
    with compare:
        k = daily.groupby("scenario")[["on_time", "fill_rate", "wages", "penalties", "profit"]].mean()
        st.caption("Means over every seed loaded. For differences with intervals see docs/MULTISEED.md.")
        st.dataframe(k.style.format("{:.3f}"))


if __name__ == "__main__":
    main()
