---
name: case-study
description: Write the recruiter-facing case study (English plus a second language) and the README front page for a company simulation, from generated numbers only. Use when the analysis is done and the project needs to be presented, or when asked to write or update the case study, README pitch, LinkedIn post or CV line.
---

# Case study and front page

The reader is a recruiter or hiring manager with two minutes. They should leave knowing the business
question, that the work is rigorous, and three numbers.

## docs/CASE_STUDY.md (template in the repo)

About 900 words, one page:

1. **The question**: the company in two sentences (size, daily volume), the recurring decision, the
   cost of a wrong call. Then why simulate: real data is private; a known generating process lets every
   model be checked and every policy tested first.
2. **What I built**: five bullets: data (tables, rows per run, enterprise extracts), analytics (SQL,
   dashboards), ML (models vs today's methods in money), method (time split, seeds, intervals, closed
   loop), engineering (tests, CI).
3. **Findings**: four or five, each a bold one-line claim with a number and its 95 % interval, then
   two to four sentences. Include at least one failure and what it taught, one result that multiple
   seeds changed, and one place a rule beat a model (or where ML earned its place).
4. **What I would tell a manager**: three or four one-line actions tied to findings.
5. **What I learned**: two or three honest sentences.
6. **Tools line** and "The company is fictional; the data is simulated on purpose."

Every number must come from a generated file (`docs/MULTISEED.md`, `docs/CLOSED_LOOP.md`,
`ml/RESULTS.md`, `ml/results/`). Quote it with the same rounding.

## Second language (docs/ETUDE_DE_CAS.md for French)

A natural translation, not word for word: Québec French terms for the industry (e.g. « quart de
travail », « taux de service »), numbers in French format (3 498 $, 99,7 %). Both files link to each other.

## README front page

- Title, CI badge, one paragraph pitch (question, what was built, headline number), link to the case
  study in both languages.
- A screenshot or GIF of the dashboard (and of the animation if there is one).
- Findings (3–5 lines, linking to the generated reports), quick start, what is inside, roadmap ticked.

## Style

Plain English, short sentences, active voice, business words before method words, no hype. Numbers
with units and intervals. Write for someone who does not know the industry.

## Also offer

A LinkedIn post (5–8 lines, the failure-then-fix story works best, link + one image) and a one-line CV
entry with the headline number. Do not post anything; give the text to the user.
