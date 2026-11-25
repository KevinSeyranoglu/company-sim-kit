"""{{COMPANY_NAME}} simulation: headless data generation.

    python main.py --days 180 --seed 42 --scenario baseline        # -> data/baseline_seed42/*.csv
    python main.py --days 60 --staff-plan plan.json --out data/x   # closed-loop run with a staffing plan
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import config as C
from datalog import CsvLog
from simulation import Simulation


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=C.COMPANY_NAME)
    ap.add_argument("--days", type=int, default=180)
    ap.add_argument("--seed", type=int, default=C.RANDOM_SEED)
    ap.add_argument("--scenario", default="baseline", choices=list(C.SCENARIOS))
    ap.add_argument("--out", default=None, help="output folder (default data/<scenario>_seed<seed>)")
    ap.add_argument("--staff-plan", metavar="FILE.json", help="crew per date and shift {date: {shift: n}}")
    return ap.parse_args(argv)


def main(argv=None):
    a = parse_args(argv)
    out = a.out or os.path.join(C.DATA_DIR, f"{a.scenario}_seed{a.seed}")
    plan = json.load(open(a.staff_plan)) if a.staff_plan else None
    log = CsvLog(out)
    sim = Simulation(seed=a.seed, scenario=a.scenario, datalog=log, staff_plan=plan)
    t0 = time.time()
    done = 0
    while done < a.days:
        step = min(C.HEADLESS_LOG_EVERY_DAYS, a.days - done)
        sim.run(step)
        done += step
        print(f"  day {done}/{a.days}  ({time.time() - t0:.1f} s)", file=sys.stderr)
    log.close()
    assert sim.unit_balance() == 0, "unit conservation broken"
    with open(os.path.join(out, "run.json"), "w") as f:
        json.dump({"scenario": a.scenario, "seed": a.seed, "days": a.days, "start": C.START_DATE,
                   "staff_plan": a.staff_plan}, f, indent=1)
    print(out)


if __name__ == "__main__":
    main()
