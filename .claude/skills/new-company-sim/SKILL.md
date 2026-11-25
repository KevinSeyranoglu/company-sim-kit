---
name: new-company-sim
description: Start a new company simulation project from company-sim-kit. Use when the user wants to simulate a new company or industry ("make a sim of a hospital", "next company", "start a new simulation"). Interviews for a brief, picks the company with the user, then generates the repo with new_project.py.
---

# Start a new company simulation

Run from the company-sim-kit folder. The output is a new git repository next to the kit (or where the
user says), ready for the `company-spec` skill.

## 1. Brief (ask, do not guess)

Use `templates/COMPANY_BRIEF.md`. Ask the user, in one short round of questions:

- **Target jobs**: titles and 3–5 employers (or sectors) they are applying to, and the city/country.
- **Industry**: if they have none in mind, propose 3 from the table in `PLAYBOOK.md` that fit those
  employers, each with the decisions it would model, and recommend one.
- **Tools the postings ask for**: SQL dialect, BI tool (Power BI, Tableau, Looker), ERP (SAP, Oracle,
  Dynamics), cloud (Azure, AWS, GCP), Python libraries. If unknown, offer to read 3 real job postings
  with the browser or web search and list the tools that repeat.
- **Language**: case study in English, plus French (default for Québec) or another language.

Write the answers to `briefs/<slug>.md` in the kit (a filled copy of the template).

## 2. Name the fictional company

A believable, invented name that fits the region and industry (no real brand, no real person). Check
with a quick web search that the name is not an existing company in that industry.

## 3. Generate the repo

```bash
python new_project.py "Company Name" --industry "short industry phrase" --slug company-slug \
    --dest ~/Desktop/Projects
```

It copies `starter/`, fills the placeholders, copies the phase skills to `.claude/skills/`, copies
`PLAYBOOK.md` to `docs/`, copies `briefs/<slug>.md` to `docs/BRIEF.md` if it exists, runs `git init`,
and runs the starter tests once. Report the path and the test result.

## 4. Hand over

Tell the user the next step is the spec, done inside the new repo (open it in Claude Code so its own
CLAUDE.md and skills load). Do not create a GitHub remote or push unless asked; give the command:

```bash
gh repo create <slug> --public --source . --push
```
