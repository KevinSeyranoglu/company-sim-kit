"""Operational data export: a star schema of dim_* / fact_* CSV tables.

The simulation calls row(table, **fields) at every business event. CsvLog buffers rows and appends
them to <out_dir>/<table>.csv; the files load straight into DuckDB, pandas or Power BI. NullLog drops
everything (tests and interactive runs that do not need data).

Timestamps are ISO 8601 without zone ("2025-12-01T06:12:00"), dates "YYYY-MM-DD", money in CURRENCY.
"""
from __future__ import annotations

import csv
import os
from collections import defaultdict

# Data contract: every table and its columns, in file order. Tables that got no rows in a run are
# still written (header only) so downstream SQL and dashboards never break. CsvLog refuses a row
# whose fields differ from the contract, so a typo fails the run instead of silently making a column.
# Every column is documented in DATA_DICTIONARY.md.
DIM_COLUMNS = {
    "dim_product": ["product_code", "name", "unit_price", "unit_cost", "base_daily_units"],
    "dim_customer": ["customer_id", "name", "kind", "size"],
    "dim_worker": ["worker_id", "home_shift", "skill"],
}
FACT_COLUMNS = {
    "fact_orders": ["order_id", "customer_id", "created_ts", "due_ts", "started_ts", "done_ts", "worker_id",
                    "shift", "lines", "units_ordered", "units_shipped", "fill_rate", "on_time", "late_min",
                    "revenue", "penalty"],
    "fact_order_lines": ["order_id", "product_code", "units_ordered", "units_shipped"],
    "fact_receipts": ["receipt_id", "ts", "product_code", "units_ordered", "units_received", "short"],
    "fact_inventory_daily": ["date", "product_code", "units_on_hand"],
    "fact_labor": ["date", "worker_id", "shift", "start_ts", "end_ts", "hours", "orders_done", "units_done",
                   "absent", "wage_cost"],
    "fact_events": ["ts", "event_type", "detail"],
    "fact_daily_kpi": ["date", "orders", "units_ordered", "units_shipped", "on_time", "fill_rate", "revenue",
                       "cogs", "wages", "penalties", "fixed_cost", "profit", "workers_present", "backlog_end"],
}
TABLES = {**DIM_COLUMNS, **FACT_COLUMNS}


class NullLog:
    def row(self, table, **fields):
        pass

    def flush(self):
        pass

    def close(self):
        pass


class CsvLog:
    def __init__(self, out_dir, flush_every=5000):
        self.out_dir = out_dir
        self.flush_every = flush_every
        self.buf = defaultdict(list)
        self.n = 0
        os.makedirs(out_dir, exist_ok=True)
        for table, cols in TABLES.items():                 # fresh files with headers, every table
            with open(self._path(table), "w", newline="") as f:
                csv.writer(f).writerow(cols)

    def _path(self, table):
        return os.path.join(self.out_dir, f"{table}.csv")

    def row(self, table, **fields):
        cols = TABLES.get(table)
        if cols is None:
            raise KeyError(f"unknown table {table!r}: add it to datalog.TABLES and DATA_DICTIONARY.md")
        if set(fields) != set(cols):
            missing, extra = set(cols) - set(fields), set(fields) - set(cols)
            raise ValueError(f"{table}: missing {sorted(missing)}, unexpected {sorted(extra)}")
        self.buf[table].append([fields[c] for c in cols])
        self.n += 1
        if self.n >= self.flush_every:
            self.flush()

    def flush(self):
        for table, rows in self.buf.items():
            with open(self._path(table), "a", newline="") as f:
                csv.writer(f).writerows(rows)
        self.buf.clear()
        self.n = 0

    def close(self):
        self.flush()
