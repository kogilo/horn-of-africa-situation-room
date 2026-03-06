from __future__ import annotations
import pandas as pd
import numpy as np

def compute_refugee_pressure_index(
    displacement_with_geo: pd.DataFrame,
    target_country: str = "Ethiopia",
    target_region: str = "Gambella",
    origin_country: str = "South Sudan",
    window_months: int = 3,
) -> pd.DataFrame:
    """
    Returns a monthly index for cross-border refugee pressure into a target region.
    Index is normalized 0–100 based on the max rolling arrivals in the series.

    Assumption:
      - Refugee arrivals recorded at destination locations (e.g., camps in Gambella)
      - origin_country identifies source country (South Sudan)
    """
    df = displacement_with_geo.copy()

    # Focus only on refugee arrivals into target region
    df = df[
        (df["displacement_type"].str.lower() == "refugee") &
        (df["country"] == target_country) &
        (df["region"] == target_region) &
        (df["origin_country"].str.lower() == origin_country.lower())
    ].copy()

    if df.empty:
        return pd.DataFrame(columns=["month", "rolling_arrivals", "pressure_index_0_100"])

    monthly = df.groupby("month", as_index=False)["arrivals"].sum().sort_values("month")

    # Rolling window to smooth spikes
    monthly["rolling_arrivals"] = (
        monthly["arrivals"].rolling(window=window_months, min_periods=1).sum()
    )

    max_val = monthly["rolling_arrivals"].max()
    if max_val <= 0:
        monthly["pressure_index_0_100"] = 0.0
    else:
        monthly["pressure_index_0_100"] = (monthly["rolling_arrivals"] / max_val) * 100

    return monthly[["month", "rolling_arrivals", "pressure_index_0_100"]]