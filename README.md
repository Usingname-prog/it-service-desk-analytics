# IT Service Desk Analytics

A reproducible educational data analytics project using **Python, pandas, SQLite, SQL and matplotlib** to explore IT support ticket volume, response patterns, and resolution SLA performance.

The project generates **fictional, synthetic data**; no real customers, employer data or personal records are involved. Reports and charts are illustrative and must not be interpreted as real business results.

## Scope

- Generate and validate synthetic service tickets
- Load data into SQLite and run business-oriented SQL analyses
- Calculate SLA compliance and operational KPIs
- Produce CSV/JSON reports and a static dashboard
- Verify core logic with `pytest`

## Run locally

```bash
python -m venv .venv
# Activate the virtual environment, then:
pip install -r requirements.txt
python -m service_analytics.pipeline --tickets 1500 --seed 42
python -m pytest -q
```

See `docs/verification.md` for reproducibility notes and `docs/interview_guide.md` for an explanation of the business problem and modelling assumptions.

**Status:** AI-assisted learning portfolio; see project files for implementation. No professional deployment or financial outcomes are claimed.
