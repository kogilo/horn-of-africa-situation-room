from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

from src.io_utils import ensure_dirs, PROJECT_ROOT
from src.cleaning import clean_incidents, clean_displacement, join_locations
from src.risk_scoring import compute_region_risk
from src.displacement_forecast import forecast_displacement
from src.plots import plot_incidents_timeseries, plot_displacement_forecast
from src.brief_generator import generate_weekly_brief
from src.refugee_pressure import compute_refugee_pressure_index
from src.plots import plot_ssudan_to_gambella_flow

def main(week_end: str):
    week_end_dt = pd.to_datetime(week_end)

    raw_dir = PROJECT_ROOT / "data" / "raw"
    out_fig = PROJECT_ROOT / "outputs" / "figures"
    out_tables = PROJECT_ROOT / "outputs" / "tables"
    out_briefs = PROJECT_ROOT / "outputs" / "briefs"
    ensure_dirs(out_fig, out_tables, out_briefs, PROJECT_ROOT / "data" / "clean")

    locations = pd.read_csv(raw_dir / "locations.csv")
    incidents = pd.read_csv(raw_dir / "incidents.csv")
    displacement = pd.read_csv(raw_dir / "displacement.csv")

    incidents = clean_incidents(incidents)
    displacement = clean_displacement(displacement)

    inc_geo = join_locations(incidents, locations)
    disp_geo = join_locations(displacement, locations)

    pressure_ts = compute_refugee_pressure_index(
    disp_geo,
    target_country="Ethiopia",
    target_region="Gambella",
    origin_country="South Sudan",
    window_months=3,
)
    pressure_latest = float(pressure_ts["pressure_index_0_100"].iloc[-1]) if not pressure_ts.empty else 0.0

    risk_table = compute_region_risk(
    inc_geo,
    week_end_dt,
    refugee_pressure_latest_0_100=pressure_latest,
    refugee_pressure_weight=0.25,
    refugee_pressure_target_country="Ethiopia",
    refugee_pressure_target_region="Gambella",
)


    risk_table.to_csv(out_tables / "risk_scores.csv", index=False)

    forecast = forecast_displacement(disp_geo, months_ahead=6)
    if not forecast.empty:
        forecast.to_csv(out_tables / "displacement_forecast.csv", index=False)

    # plots
    plot_incidents_timeseries(incidents, out_fig / "incidents_last_30_days.png", days=30)
    plot_displacement_forecast(disp_geo, forecast, out_fig / "displacement_forecast.png")
    plot_ssudan_to_gambella_flow(
    disp_geo,
    out_fig / "ssudan_to_gambella_arrivals.png",
    target_country="Ethiopia",
    target_region="Gambella",
    origin_country="South Sudan",
)

    brief_text = generate_weekly_brief(week_end_dt, risk_table, incidents, forecast)
    brief_path = out_briefs / f"weekly_brief_{week_end_dt.date()}.md"
    brief_path.write_text(brief_text, encoding="utf-8")

    

    print(f"Saved: {brief_path}")
    print(f"Saved: {out_tables / 'risk_scores.csv'}")
    print(f"Saved figures in: {out_fig}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--week_end", required=True, help="Week ending date (YYYY-MM-DD)")
    args = parser.parse_args()
    main(args.week_end)