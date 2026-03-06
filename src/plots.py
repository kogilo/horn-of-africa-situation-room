from __future__ import annotations
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def plot_incidents_timeseries(incidents: pd.DataFrame, outpath: Path, days: int = 30) -> None:
    df = incidents.copy()
    df = df.dropna(subset=["event_date"])
    cutoff = df["event_date"].max() - pd.Timedelta(days=days)
    df = df[df["event_date"] >= cutoff]

    daily = df.groupby(pd.Grouper(key="event_date", freq="D")).size().reset_index(name="count")

    plt.figure()
    plt.plot(daily["event_date"], daily["count"])
    plt.title(f"Incidents per day (last {days} days)")
    plt.xlabel("Date")
    plt.ylabel("Incidents")
    plt.tight_layout()
    plt.savefig(outpath, dpi=200)
    plt.close()

def plot_displacement_forecast(history: pd.DataFrame, forecast: pd.DataFrame, outpath: Path) -> None:
    if history.empty or forecast.empty:
        return

    # aggregate to total net_flow per month
    h = history.copy()
    h["net_flow"] = h["arrivals"] - h["departures"]
    h = h.groupby("month")["net_flow"].sum().reset_index()

    f = forecast.groupby("month")["net_flow_forecast"].sum().reset_index()

    plt.figure()
    plt.plot(h["month"], h["net_flow"], label="Historical net flow")
    plt.plot(f["month"], f["net_flow_forecast"], label="Forecast net flow")
    plt.title("Displacement net flow: history + forecast")
    plt.xlabel("Month")
    plt.ylabel("People (net)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outpath, dpi=200)
    plt.close()



def plot_ssudan_to_gambella_flow(
    displacement_with_geo: pd.DataFrame,
    outpath: Path,
    target_country: str = "Ethiopia",
    target_region: str = "Gambella",
    origin_country: str = "South Sudan",
) -> None:
    df = displacement_with_geo.copy()

    df = df[
        (df["displacement_type"].str.lower() == "refugee") &
        (df["country"] == target_country) &
        (df["region"] == target_region) &
        (df["origin_country"].str.lower() == origin_country.lower())
    ].copy()

    if df.empty:
        return

    monthly = df.groupby("month", as_index=False)["arrivals"].sum().sort_values("month")

    plt.figure()
    plt.plot(monthly["month"], monthly["arrivals"])
    plt.title(f"Refugee arrivals: {origin_country} → {target_region}")
    plt.xlabel("Month")
    plt.ylabel("Arrivals")
    plt.tight_layout()
    plt.savefig(outpath, dpi=200)
    plt.close()






