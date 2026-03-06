from __future__ import annotations
import pandas as pd
import numpy as np

def _recency_weight(days_ago: float) -> float:
    if days_ago <= 7:
        return 1.0
    if days_ago <= 30:
        return 0.6
    if days_ago <= 90:
        return 0.3
    return 0.1

def compute_region_risk(
    incidents_with_geo: pd.DataFrame,
    week_end: pd.Timestamp,
    refugee_pressure_latest_0_100: float = 0.0,
    refugee_pressure_weight: float = 0.25,
    refugee_pressure_target_country: str = "Ethiopia",
    refugee_pressure_target_region: str = "Gambella",
) -> pd.DataFrame:
    """
    Regional risk score = normalized incident score (0–100) blended with
    cross-border refugee pressure (0–100) for Gambella.

    refugee_pressure_weight:
      - 0.00 = ignore displacement pressure
      - 0.25 = modest influence (recommended)
      - 0.40+ = heavy influence (use carefully)
    """
    df = incidents_with_geo.copy()
    df["days_ago"] = (week_end - df["event_date"]).dt.days.clip(lower=0)
    df["recency_w"] = df["days_ago"].apply(_recency_weight)
    df["sev_w"] = df["severity"].astype(float)
    df["fatal_w"] = np.log1p(df["reported_fatalities"].astype(float))

    df["score_component"] = df["sev_w"] * df["recency_w"] + 0.5 * df["fatal_w"]

    grp = df.groupby(["country", "region"], dropna=False).agg(
        incident_count=("event_id", "count"),
        avg_severity=("severity", "mean"),
        fatalities=("reported_fatalities", "sum"),
        incident_score_raw=("score_component", "sum"),
        last_event=("event_date", "max"),
    ).reset_index()

    # Normalize incident score into 0–100
    if grp["incident_score_raw"].max() > 0:
        grp["incident_score_0_100"] = (grp["incident_score_raw"] / grp["incident_score_raw"].max()) * 100
    else:
        grp["incident_score_0_100"] = 0.0

    # Default: final score = incident score
    grp["refugee_pressure_0_100"] = 0.0
    grp["risk_score_0_100"] = grp["incident_score_0_100"]

    # Apply refugee pressure ONLY to target region (Gambella, Ethiopia)
    mask = (grp["country"] == refugee_pressure_target_country) & (grp["region"] == refugee_pressure_target_region)
    if mask.any():
        rp = float(refugee_pressure_latest_0_100)
        grp.loc[mask, "refugee_pressure_0_100"] = rp

        w = float(refugee_pressure_weight)
        w = max(0.0, min(1.0, w))
        grp.loc[mask, "risk_score_0_100"] = (1 - w) * grp.loc[mask, "incident_score_0_100"] + w * rp

    # Risk level labels based on final risk score
    grp["risk_level"] = pd.cut(
        grp["risk_score_0_100"],
        bins=[-0.1, 33, 66, 1000],
        labels=["LOW", "MEDIUM", "HIGH"],
    ).astype(str)

    grp = grp.sort_values(["risk_score_0_100"], ascending=False)
    return grp