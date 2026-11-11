# Learning to Spot the Hook
Adaptive phishing practice game + training dashboard. Quinnipiac CYB 691, Fall 2026.
Megan Mohr, Jessica Theodore | Advisor: Frederick Scholl | Client: John Coursen (Fortify Cyber / Edwin)

Players sort practice emails as Phishing or Safe; a dashboard shows weak spots; the adaptive engine
picks the next email from the categories the player keeps missing. Compared against random, fixed-difficulty,
and an Edwin-style rules baseline using simulated players. Fictional brands, no working links, email only.

## Setup
    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env        # add ANTHROPIC_API_KEY for LLM generation (optional)
    python -m app.generator     # builds data/email_bank.json (LLM if key set, else templates)
    python -m app.web           # game at http://127.0.0.1:5000, dashboard at /dashboard
    python -m app.simulate      # writes results/simulation.csv
    pytest

## Layout
- `app/phishscale.py` simplified NIST Phish Scale (TODO: official rubric)
- `app/generator.py` LLM + offline email generation (LLM emails flagged `needs_review` for hand spot-check)
- `app/engines.py` adaptive / random / fixed / rules engines
- `app/simulate.py` simulated players (assumptions in file header)
- `app/web.py` Flask game + dashboard

## Timeline
| Dates | Deliverable |
|---|---|
| Oct 5-16 | Requirements brief |
| Oct 19-30 | Game + scored email bank |
| Nov 2-13 | Working prototype |
| Nov 16-27 | Results data |
| Nov 30-Dec 7 | Final report, demo (IRB approval first for any classmate test) |
