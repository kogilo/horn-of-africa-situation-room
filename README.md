# Horn of Africa Situation Room (Python)

A policy + humanitarian analytics project that turns incident and displacement data into:
- A weekly diplomatic situation brief (Markdown)
- Regional risk scores (Low/Medium/High)
- Displacement trends + simple 3–6 month forecast
- Charts for reporting (PNG)

## Why this matters (Diplomatic/NGO Use)
- Supports early warning, protection analysis, and scenario planning
- Standardizes weekly reporting for embassies, INGOs, UN clusters, and donors
- Produces transparent, reproducible outputs for decision-making

## Data Inputs
Place CSVs in `data/raw/`:
- `incidents.csv`: conflict/protest/crime events with severity and sources
- `displacement.csv`: monthly IDP/refugee flows by location
- `locations.csv`: location metadata + region/country mapping

## Outputs
Generated into `outputs/`:
- `tables/risk_scores.csv`
- `figures/*.png`
- `briefs/weekly_brief_YYYY-MM-DD.md`

## How to run
```bash
pip install -r requirements.txt
python run_weekly_brief.py --week_end 2026-02-28