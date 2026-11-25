"""Every tuning number of the simulation, in one place, plus the what-if scenarios.

Rule: no magic numbers in simulation.py. If a number shapes the data, it lives here with a comment
saying what it means and, when it comes from industry, where the order of magnitude comes from.
"""
from __future__ import annotations

COMPANY_NAME = "{{COMPANY_NAME}}"
INDUSTRY = "{{INDUSTRY}}"
CURRENCY = "$"
START_DATE = "2025-12-01"          # first simulated day; start before a peak season so the data holds one
RANDOM_SEED = 42
DATA_DIR = "data"

# ------------------------------------------------------------------ time
SHIFTS = {                         # name: (start hour, end hour); night wraps past midnight
    "day": (6, 14),
    "evening": (14, 22),
    "night": (22, 6),
}
ORDER_HOURS = (6, 20)              # customers place orders between these hours
SLA_HOURS = 6                      # promise: an order is on time if done within this many hours

# ------------------------------------------------------------------ products (fictional)
# code: (name, unit price, unit cost, base daily units network-wide)
PRODUCTS = {
    "P01": ("Product A", 24.0, 15.0, 900),
    "P02": ("Product B", 18.0, 11.0, 700),
    "P03": ("Product C", 42.0, 30.0, 350),
    "P04": ("Product D", 9.5, 5.0, 1200),
    "P05": ("Product E", 65.0, 44.0, 150),
}

# ------------------------------------------------------------------ customers (fictional)
N_CUSTOMERS = 30
CUSTOMER_KINDS = {                 # kind: (share of customers, size multiplier)
    "small": (0.5, 0.6),
    "medium": (0.35, 1.0),
    "large": (0.15, 2.2),
}
ORDER_PROB = 0.9                   # chance each of a customer's usual daily orders is placed
ORDER_NOISE = 0.30                # lognormal sigma of a customer's daily quantity: the floor on forecast error

# ------------------------------------------------------------------ demand signal (what the models can learn)
WEEKDAY_FACTOR = [1.05, 1.0, 1.0, 1.1, 1.3, 0.8, 0.5]          # Monday..Sunday
SEASONS = {                        # name: (first MM-DD, last MM-DD, factor)
    "holiday_peak": ("12-10", "12-24", 1.45),
    "january_lull": ("01-02", "01-20", 0.8),
}

# ------------------------------------------------------------------ supply
STOCK_TARGET_DAYS = 1.5            # nightly replenishment tops each product up to this many days of base demand (no season: peaks run short)
SHORT_SHIPMENT_PROB = 0.06         # chance a supplier delivery is short
SHORT_SHIPMENT_FRACTION = (0.3, 0.7)
RECEIPT_HOUR = 4                   # supplier deliveries land at 04:00

# ------------------------------------------------------------------ labour
WAGE_PER_HOUR = 26.0
SHIFT_PREMIUM = {"day": 1.0, "evening": 1.08, "night": 1.15}
MINUTES_PER_ORDER = 6.0            # fixed handling per order
MINUTES_PER_UNIT = 3.0             # variable handling per unit (calibrated: peaks strain the baseline crew)
SKILL_RANGE = (0.75, 1.3)          # worker speed multiplier: real heterogeneity the data should carry
ABSENCE_PROB = 0.04                # chance a rostered worker calls in sick

# ------------------------------------------------------------------ money
LATE_PENALTY_RATE = 0.20          # late order: chargeback plus margin lost to unhappy customers, as a share of its value
SHORT_PENALTY_PER_UNIT = 2.0
FIXED_COST_PER_DAY = 4000.0

# ------------------------------------------------------------------ scenarios: what-if knobs
# Each scenario overrides some of the numbers above. Keep "baseline" the published one.
BASE_CREW = {"day": 14, "evening": 10, "night": 4}
SCENARIOS = {
    "baseline": {},
    "lean_staff": {"crew": {"day": 11, "evening": 8, "night": 3}},
    "extra_staff": {"crew": {"day": 17, "evening": 12, "night": 5}},
    "supply_trouble": {"short_shipment_prob": 0.2},
}

HEADLESS_LOG_EVERY_DAYS = 30
