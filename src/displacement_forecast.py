from __future__ import annotations
import pandas as pd
import numpy as np

def forecast_displacement(displacement_with_geo: pd.DataFrame, months_ahead: int = 6) -> pd.DataFrame:
    """
    Simple interpretable forecast:
    - Compute net flow = arrivals - departures
    - Fit a linear trend per (country, region, displacement_type)
    """
    df = displacement_with_geo.copy()
    df["net_flow"] = df["arrivals"] - df["departures"]
    df = df.sort_values("month")

    outputs = []
    for keys, g in df.groupby(["country", "region", "displacement_type"], dropna=False):
        g = g.dropna(subset=["month"])
        if len(g) < 3:
            continue

        # Create time index 0..n-1
        t = np.arange(len(g))
        y = g["net_flow"].to_numpy(dtype=float)

        # Linear regression via polyfit
        slope, intercept = np.polyfit(t, y, 1)

        last_month = g["month"].max()
        future_months = pd.date_range(
            start=(last_month + pd.offsets.MonthBegin(1)),
            periods=months_ahead,
            freq="MS"
        )
        t_future = np.arange(len(g), len(g) + months_ahead)
        y_pred = intercept + slope * t_future

        out = pd.DataFrame({
            "country": keys[0],
            "region": keys[1],
            "displacement_type": keys[2],
            "month": future_months,
            "net_flow_forecast": np.maximum(0, y_pred).round(0).astype(int),
        })
        outputs.append(out)

    return pd.concat(outputs, ignore_index=True) if outputs else pd.DataFrame()