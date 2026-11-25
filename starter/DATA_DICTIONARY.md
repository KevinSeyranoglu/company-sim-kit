# Data dictionary

Every table written by `python main.py` to `data/<scenario>_seed<seed>/`, and every column. The contract
in `datalog.TABLES` is the source of truth; `tests/test_sim.py` fails if code and contract differ, and
this file must change in the same commit as the contract.

Conventions: timestamps ISO 8601 local time without zone (`2025-12-01T06:12:00`), dates `YYYY-MM-DD`,
money in dollars, rates as fractions 0–1. `analytics/build_db.py` adds `run`, `scenario` and `seed`.

> These are the starter tables. Replace them with your company's tables as the simulation grows.

## Dimensions

### dim_product
| Column | Type | Meaning |
|---|---|---|
| product_code | text | Product key (`P01`…) |
| name | text | Fictional product name |
| unit_price | number | Selling price per unit |
| unit_cost | number | Purchase cost per unit |
| base_daily_units | int | Network demand on an average day before weekday and season factors |

### dim_customer
| Column | Type | Meaning |
|---|---|---|
| customer_id | text | Customer key (`C001`…) |
| name | text | Fictional name |
| kind | text | small, medium or large |
| size | number | Demand multiplier |

### dim_worker
| Column | Type | Meaning |
|---|---|---|
| worker_id | text | Worker key (`W0001`…) |
| home_shift | text | day, evening or night |
| skill | number | Speed multiplier (hidden in real life: a model must not use it as a feature) |

## Facts

### fact_orders (one row per completed order)
| Column | Type | Meaning |
|---|---|---|
| order_id | text | `SO0000001`… |
| customer_id | text | → dim_customer |
| created_ts, due_ts, started_ts, done_ts | timestamp | Placed, promised (created + SLA), work started, work done |
| worker_id, shift | text | Who processed it, on which shift |
| lines | int | Number of products ordered |
| units_ordered, units_shipped | int | Shipped < ordered when stock ran out |
| fill_rate | number | units_shipped / units_ordered |
| on_time | 0/1 | done_ts ≤ due_ts |
| late_min | number | Minutes after due_ts (0 when on time) |
| revenue | number | Shipped units × price |
| penalty | number | Late penalty plus short-shipment penalty |

### fact_order_lines
| Column | Type | Meaning |
|---|---|---|
| order_id | text | → fact_orders |
| product_code | text | → dim_product |
| units_ordered, units_shipped | int | Per line |

### fact_receipts (supplier deliveries, 04:00 daily)
| Column | Type | Meaning |
|---|---|---|
| receipt_id | text | `R000001`… |
| ts | timestamp | Delivery time |
| product_code | text | → dim_product |
| units_ordered, units_received | int | Received < ordered on a short shipment |
| short | 0/1 | Short shipment |

### fact_inventory_daily (snapshot at 23:59)
| Column | Type | Meaning |
|---|---|---|
| date | date | |
| product_code | text | → dim_product |
| units_on_hand | int | Free stock (not reserved by an open order) |

### fact_labor (one row per worker and shift)
| Column | Type | Meaning |
|---|---|---|
| date | date | Date the shift started |
| worker_id, shift | text | |
| start_ts, end_ts | timestamp | Empty when absent; end includes overtime to finish an order |
| hours | number | Paid hours |
| orders_done, units_done | int | Output |
| absent | 0/1 | Sick call |
| wage_cost | number | hours × wage × shift premium |

### fact_events
| Column | Type | Meaning |
|---|---|---|
| ts | timestamp | |
| event_type | text | `short_shipment`, `sick_call` |
| detail | text | Free text |

### fact_daily_kpi (one row per day, written after the night shift)
| Column | Type | Meaning |
|---|---|---|
| date | date | |
| orders | int | Orders completed that day |
| units_ordered, units_shipped | int | On those orders |
| on_time, fill_rate | number | Shares for those orders |
| revenue, cogs, wages, penalties, fixed_cost, profit | number | profit = revenue − cogs − wages − penalties − fixed_cost |
| workers_present | int | Workers who came in, all shifts started that day |
| backlog_end | int | Open orders at 23:59 |

## How the data is generated

The true mechanisms, so a model can be checked against them. Keep this section current.

- **Demand:** each customer places up to `orders_per_day` orders (90 % chance each), between 06:00 and
  20:00 (peak 10:00). Units per line = base × customer share × weekday factor × season factor × lognormal
  noise (σ = 0.30). Weekday factors Monday→Sunday 1.05, 1.0, 1.0, 1.1, 1.3, 0.8, 0.5; holiday peak
  Dec 10–24 × 1.45; January lull Jan 2–20 × 0.8.
- **Stock:** each night at 04:00 suppliers top every product up to 1.5 days of *base* demand. The target
  ignores weekday and season, so peaks run short. 6 % of deliveries are short by 30–70 %.
- **Labour:** the crew per shift is fixed by the scenario (or by `--staff-plan`); 4 % of rostered workers
  call in sick. Handling time = (6 min + 3 min × units) / skill × U(0.9, 1.1); skill U(0.75, 1.3).
  Orders are worked earliest-due first; a worker finishes the current order after the shift ends (overtime).
- **Money:** late order 20 % of its value; short unit $2; fixed cost $4,000 a day.
