---
name: multiseed-eval
description: Evaluate scenarios and models over several random seeds with paired differences and 95 % intervals, and write the generated report docs/MULTISEED.md. Use before making any claim that one scenario, policy or model is better than another, or when a result came from a single run.
---

# Multi-seed evaluation

One run is one draw. In the warehouse project, a single seed said adding pickers was profitable; over
5 seeds it lost $2,815 a day. Every comparison in the README or case study must come from here.

## How

```bash
python analytics/multiseed.py run --days 180 --jobs 8    # every scenario x SEEDS
python analytics/multiseed.py report                     # docs/MULTISEED.md
```

- **Paired by seed.** Same seed = same customers, demand and deliveries (separate random streams), so
  `scenario − baseline` per seed removes the shared noise. Report the mean paired difference, the 95 %
  t interval over seeds, and "better in k of n seeds".
- **5 seeds** is the default (42 is the published run). Use more when an interval straddles 0 and the
  decision matters; say how many in the report.
- **Generated report only.** Never type numbers into `docs/MULTISEED.md`; change the script and rerun.
- **Models too.** Run each model on every seed's baseline run and report its value per day with the
  same paired logic (model − today's method, per seed).

## Reading the results

- An interval containing 0: "the runs do not show a difference", not "no effect".
- Report service and cost side by side; a saving that costs service is a trade-off, not a win.
- Note what the seeds do not vary (the season calendar, the layout): the interval covers run-to-run
  noise only.

## Check

`tests/test_data.py::test_multiseed_report` covers the paired function. If you add KPIs to `KPIS`,
add them to the test.
