# company-sim-kit

A kit for building company simulations as data science portfolio projects: the method (`PLAYBOOK.md`),
one Claude Code skill per phase (`.claude/skills/`), and a working starter project (`starter/`) that
`new_project.py` turns into a new repo.

The user is building a data science portfolio to get a job. Every project made with this kit exists to
show employers SQL, dashboards, ML and sound method on realistic data from their industry.

## When the user wants a new company

Use the `new-company-sim` skill. Do not build the company inside this repo: generate a new repo with
`new_project.py` and do the work there, where its own `CLAUDE.md` and skills apply.

## Working on the kit itself

- `starter/` must always generate a project whose tests pass: `python -m pytest tests -q` does exactly
  that (generate into a temp folder, run its tests). Run it after any change to `starter/` or
  `new_project.py`.
- Placeholders in `starter/` are `{{COMPANY_NAME}}`, `{{INDUSTRY}}`, `{{SLUG}}`, `{{AUTHOR}}`,
  `{{GITHUB_USER}}`, `{{YEAR}}`; `new_project.py` fails on any left unfilled. Add new ones in both.
- Skills: one folder per phase, `SKILL.md` with `name` and `description` frontmatter. The description
  says what the skill does and when to use it. Keep the phase table in `README.md` and `PLAYBOOK.md`
  in sync with the folders.
- Starter code style: Python 3.11, standard library for the simulation, pandas / scikit-learn / scipy /
  duckdb / streamlit for the analytics. Every tuning number in `starter/config.py` with a comment.
- Lessons learned in a company project go into `PLAYBOOK.md` ("What the warehouse project taught" or a
  new section per project) and the matching skill, with the concrete numbers that taught them.
- Docs in plain English, short sentences.
- Commit only when asked; never push without being asked.
