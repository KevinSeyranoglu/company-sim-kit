"""Discrete-event simulation of {{COMPANY_NAME}}: customers order, stock is allocated, a crew on
shifts processes the orders, suppliers replenish overnight. No drawing here: a renderer (optional)
only reads this state.

This is a working starting point, not the company. Replace the flow with the real one from SPEC.md,
keeping the four properties every later layer depends on:
  1. Reproducible: same seed + scenario -> identical data (tests/test_sim.py checks it).
  2. Common random numbers: demand and supply draw from their own random streams, so two scenarios
     with the same seed see the same customers and deliveries and their difference is the decision's.
  3. Conserved: every unit is accounted for (start + received = shipped + on hand + reserved).
  4. Logged: every business event becomes a row in the data contract (datalog.TABLES).

Time is in minutes since START_DATE 00:00.
"""
from __future__ import annotations

import heapq
import math
import random
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

import config as C
from datalog import NullLog

DAY = 24 * 60
START = datetime.fromisoformat(C.START_DATE)


@dataclass
class Worker:
    id: str
    home_shift: str
    skill: float
    busy: bool = False
    on_until: float = -1.0          # end of the current shift; -1 when off
    shift_start: float = 0.0
    shift_date: str = ""
    orders_done: int = 0
    units_done: int = 0


@dataclass
class Order:
    id: str
    customer_id: str
    created: float
    due: float
    lines: dict                     # product -> units ordered
    allocated: dict = field(default_factory=dict)
    value_ordered: float = 0.0


class Simulation:
    def __init__(self, seed: int | None = None, scenario: str = "baseline", datalog=None, staff_plan=None):
        self.seed = C.RANDOM_SEED if seed is None else seed
        self.scenario = scenario
        scen = C.SCENARIOS[scenario]
        self.crew = scen.get("crew", C.BASE_CREW)
        self.short_prob = scen.get("short_shipment_prob", C.SHORT_SHIPMENT_PROB)
        self.staff_plan = staff_plan or {}          # {"YYYY-MM-DD": {shift: n}}: closed-loop tests plug in here
        self.log = datalog or NullLog()

        # one random stream per source of randomness (string seeds are stable across Python runs)
        rs = lambda name: random.Random(f"{self.seed}-{name}")   # noqa: E731
        self.rng_master, self.rng_demand = rs("master"), rs("demand")
        self.rng_supply, self.rng_ops = rs("supply"), rs("ops")

        self.t = 0.0
        self.end_t = 0.0
        self.end_day = 0
        self._heap: list = []
        self._seq = 0
        self._ids = {"order": 0, "receipt": 0}
        self.queue: list = []                       # (due, seq, order) earliest due first
        self.stock = {p: round(v[3] * C.STOCK_TARGET_DAYS) for p, v in C.PRODUCTS.items()}
        self.reserved = {p: 0 for p in C.PRODUCTS}
        self.flows = {"start": sum(self.stock.values()), "received": 0, "shipped": 0}
        self.daily: dict = {}
        self._make_master_data()

    # ------------------------------------------------------------------ master data
    def _make_master_data(self):
        r = self.rng_master
        kinds = list(C.CUSTOMER_KINDS)
        weights = [C.CUSTOMER_KINDS[k][0] for k in kinds]
        self.customers = {}
        for i in range(1, C.N_CUSTOMERS + 1):
            kind = r.choices(kinds, weights)[0]
            size = C.CUSTOMER_KINDS[kind][1] * r.uniform(0.8, 1.2)
            self.customers[f"C{i:03d}"] = {"kind": kind, "size": size, "name": f"Customer {i:03d}"}
        total = sum(c["size"] for c in self.customers.values())
        for c in self.customers.values():
            c["share"] = c["size"] / total
            c["orders_per_day"] = max(1, round(c["size"] * 3))
        # a pool per shift large enough for any plan; the crew is always the first n of the pool
        self.workers = {}
        n = 0
        for shift in C.SHIFTS:
            for _ in range(60):
                n += 1
                w = Worker(f"W{n:04d}", shift, round(r.uniform(*C.SKILL_RANGE), 3))
                self.workers[w.id] = w
        self.pool = {s: [w for w in self.workers.values() if w.home_shift == s] for s in C.SHIFTS}
        for code, (name, price, cost, base) in C.PRODUCTS.items():
            self.log.row("dim_product", product_code=code, name=name, unit_price=price, unit_cost=cost,
                         base_daily_units=base)
        for cid, c in self.customers.items():
            self.log.row("dim_customer", customer_id=cid, name=c["name"], kind=c["kind"], size=round(c["size"], 3))
        for w in self.workers.values():
            self.log.row("dim_worker", worker_id=w.id, home_shift=w.home_shift, skill=w.skill)

    # ------------------------------------------------------------------ time helpers
    def ts(self, t=None):
        return (START + timedelta(minutes=self.t if t is None else t)).isoformat(timespec="seconds")

    def date_of(self, t) -> str:
        return (START + timedelta(minutes=t)).date().isoformat()

    def day_date(self, day) -> date:
        return (START + timedelta(days=day)).date()

    def _stats(self, d):
        if d not in self.daily:
            self.daily[d] = {"orders": 0, "units_ordered": 0, "units_shipped": 0, "on_time": 0, "revenue": 0.0,
                             "cogs": 0.0, "wages": 0.0, "penalties": 0.0, "workers_present": 0}
        return self.daily[d]

    # ------------------------------------------------------------------ event engine
    def schedule(self, t, kind, **payload):
        self._seq += 1
        heapq.heappush(self._heap, (t, self._seq, kind, payload))

    def run(self, days: int):
        """Simulate `days` more days; the last night shift and its overtime are included."""
        first = self.end_day
        self.end_day += days
        for d in range(first, self.end_day):
            self.schedule(d * DAY, "day_start", day=d)
        self.end_t = self.end_day * DAY + 8 * 60
        while self._heap and self._heap[0][0] <= self.end_t:
            t, _, kind, payload = heapq.heappop(self._heap)
            self.t = t
            getattr(self, f"_ev_{kind}")(**payload)
        self.t = self.end_t
        self.log.flush()
        return self

    # ------------------------------------------------------------------ demand
    def demand_factor(self, d: date) -> float:
        f = C.WEEKDAY_FACTOR[d.weekday()]
        md = d.strftime("%m-%d")
        for first, last, factor in C.SEASONS.values():
            if first <= md <= last:
                f *= factor
        return f

    def _ev_day_start(self, day):
        d = self.day_date(day)
        factor = self.demand_factor(d)
        r = self.rng_demand
        mu = -C.ORDER_NOISE ** 2 / 2                      # lognormal with mean 1
        for cid, c in self.customers.items():
            k = c["orders_per_day"]
            for _ in range(k):
                if r.random() > C.ORDER_PROB:
                    continue
                lines = {}
                for p, (_, _, _, base) in C.PRODUCTS.items():
                    mean = base * c["share"] * factor / k
                    q = round(mean * r.lognormvariate(mu, C.ORDER_NOISE))
                    if q > 0 and r.random() < 0.85:
                        lines[p] = q
                at = day * DAY + 60 * r.triangular(C.ORDER_HOURS[0], C.ORDER_HOURS[1], 10)
                if lines:
                    self.schedule(at, "order", customer_id=cid, lines=lines)
        self.schedule(day * DAY + C.RECEIPT_HOUR * 60, "receipt")
        for s, (h0, h1) in C.SHIFTS.items():
            start = day * DAY + h0 * 60
            end = day * DAY + (h1 if h1 > h0 else h1 + 24) * 60
            self.schedule(start, "shift_start", shift=s, end=end)
            self.schedule(end, "shift_end", shift=s)
        self.schedule((day + 1) * DAY - 1, "day_end", day=day)
        self.schedule((day + 1) * DAY + 8 * 60, "kpi", day=day)   # after the night shift's overtime

    def _ev_order(self, customer_id, lines):
        self._ids["order"] += 1
        o = Order(f"SO{self._ids['order']:07d}", customer_id, self.t, self.t + C.SLA_HOURS * 60, lines)
        for p, q in lines.items():
            a = min(q, self.stock[p])
            self.stock[p] -= a
            self.reserved[p] += a
            o.allocated[p] = a
            o.value_ordered += q * C.PRODUCTS[p][1]
        heapq.heappush(self.queue, (o.due, self._ids["order"], o))
        self._dispatch()

    # ------------------------------------------------------------------ supply
    def _ev_receipt(self):
        r = self.rng_supply
        for p, (_, _, _, base) in C.PRODUCTS.items():
            target = base * C.STOCK_TARGET_DAYS
            ordered = max(0, round(target - self.stock[p]))
            if ordered == 0:
                continue
            short = r.random() < self.short_prob
            received = round(ordered * (1 - r.uniform(*C.SHORT_SHIPMENT_FRACTION))) if short else ordered
            self.stock[p] += received
            self.flows["received"] += received
            self._ids["receipt"] += 1
            self.log.row("fact_receipts", receipt_id=f"R{self._ids['receipt']:06d}", ts=self.ts(), product_code=p,
                         units_ordered=ordered, units_received=received, short=int(short))
            if short:
                self.log.row("fact_events", ts=self.ts(), event_type="short_shipment",
                             detail=f"{p}: {received} of {ordered}")

    # ------------------------------------------------------------------ labour
    def _ev_shift_start(self, shift, end):
        d = self.date_of(self.t)
        n = self.staff_plan.get(d, {}).get(shift, self.crew[shift])
        for w in self.pool[shift][:n]:
            if self.rng_ops.random() < C.ABSENCE_PROB:
                self.log.row("fact_labor", date=d, worker_id=w.id, shift=shift, start_ts="", end_ts="", hours=0,
                             orders_done=0, units_done=0, absent=1, wage_cost=0)
                self.log.row("fact_events", ts=self.ts(), event_type="sick_call", detail=w.id)
                continue
            w.on_until, w.shift_start, w.shift_date = end, self.t, d
            w.orders_done = w.units_done = 0
            self._stats(d)["workers_present"] += 1
        self._dispatch()

    def _ev_shift_end(self, shift):
        for w in self.pool[shift]:
            if w.on_until >= 0 and not w.busy:
                self._clock_out(w)

    def _clock_out(self, w):
        hours = (self.t - w.shift_start) / 60
        cost = hours * C.WAGE_PER_HOUR * C.SHIFT_PREMIUM[w.home_shift]
        self.log.row("fact_labor", date=w.shift_date, worker_id=w.id, shift=w.home_shift,
                     start_ts=self.ts(w.shift_start), end_ts=self.ts(), hours=round(hours, 3),
                     orders_done=w.orders_done, units_done=w.units_done, absent=0, wage_cost=round(cost, 2))
        self._stats(w.shift_date)["wages"] += cost
        w.on_until = -1.0

    def _idle_workers(self):
        return [w for w in self.workers.values() if w.on_until > self.t and not w.busy]

    def _dispatch(self):
        for w in self._idle_workers():
            if not self.queue:
                return
            _, _, o = heapq.heappop(self.queue)
            units = sum(o.allocated.values())
            minutes = (C.MINUTES_PER_ORDER + C.MINUTES_PER_UNIT * units) / w.skill
            minutes *= self.rng_ops.uniform(0.9, 1.1)
            w.busy = True
            self.schedule(self.t + minutes, "done", worker_id=w.id, order=o, started=self.t)

    def _ev_done(self, worker_id, order, started):
        w, o = self.workers[worker_id], order
        w.busy = False
        units_ordered = sum(o.lines.values())
        shipped = sum(o.allocated.values())
        revenue = sum(a * C.PRODUCTS[p][1] for p, a in o.allocated.items())
        cogs = sum(a * C.PRODUCTS[p][2] for p, a in o.allocated.items())
        on_time = self.t <= o.due
        penalty = (0 if on_time else C.LATE_PENALTY_RATE * o.value_ordered)
        penalty += C.SHORT_PENALTY_PER_UNIT * (units_ordered - shipped)
        for p, a in o.allocated.items():
            self.reserved[p] -= a
            self.log.row("fact_order_lines", order_id=o.id, product_code=p, units_ordered=o.lines[p], units_shipped=a)
        self.flows["shipped"] += shipped
        self.log.row("fact_orders", order_id=o.id, customer_id=o.customer_id, created_ts=self.ts(o.created),
                     due_ts=self.ts(o.due), started_ts=self.ts(started), done_ts=self.ts(), worker_id=w.id,
                     shift=w.home_shift, lines=len(o.lines), units_ordered=units_ordered, units_shipped=shipped,
                     fill_rate=round(shipped / units_ordered, 4), on_time=int(on_time),
                     late_min=round(max(0.0, self.t - o.due), 1), revenue=round(revenue, 2), penalty=round(penalty, 2))
        s = self._stats(self.date_of(self.t))
        s["orders"] += 1
        s["units_ordered"] += units_ordered
        s["units_shipped"] += shipped
        s["on_time"] += on_time
        s["revenue"] += revenue
        s["cogs"] += cogs
        s["penalties"] += penalty
        w.orders_done += 1
        w.units_done += shipped
        if self.t >= w.on_until:
            self._clock_out(w)                        # finished the order on overtime
        self._dispatch()

    # ------------------------------------------------------------------ daily records
    def _ev_day_end(self, day):
        d = self.day_date(day).isoformat()
        for p in C.PRODUCTS:
            self.log.row("fact_inventory_daily", date=d, product_code=p, units_on_hand=self.stock[p])
        self._stats(d)["backlog_end"] = len(self.queue)

    def _ev_kpi(self, day):
        d = self.day_date(day).isoformat()
        s = self._stats(d)
        profit = s["revenue"] - s["cogs"] - s["wages"] - s["penalties"] - C.FIXED_COST_PER_DAY
        self.log.row("fact_daily_kpi", date=d, orders=s["orders"], units_ordered=s["units_ordered"],
                     units_shipped=s["units_shipped"],
                     on_time=round(s["on_time"] / s["orders"], 4) if s["orders"] else math.nan,
                     fill_rate=round(s["units_shipped"] / s["units_ordered"], 4) if s["units_ordered"] else math.nan,
                     revenue=round(s["revenue"], 2), cogs=round(s["cogs"], 2), wages=round(s["wages"], 2),
                     penalties=round(s["penalties"], 2), fixed_cost=C.FIXED_COST_PER_DAY, profit=round(profit, 2),
                     workers_present=s["workers_present"], backlog_end=s.get("backlog_end", 0))

    # ------------------------------------------------------------------ audit
    def unit_balance(self) -> int:
        """start + received - shipped - on hand - reserved: always 0."""
        f = self.flows
        return f["start"] + f["received"] - f["shipped"] - sum(self.stock.values()) - sum(self.reserved.values())
