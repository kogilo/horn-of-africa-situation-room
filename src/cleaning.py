from __future__ import annotations
import pandas as pd

def clean_incidents(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["event_date"] = pd.to_datetime(out["event_date"], errors="coerce")
    out["severity"] = pd.to_numeric(out["severity"], errors="coerce").fillna(1).clip(1, 5)
    out["reported_fatalities"] = pd.to_numeric(out.get("reported_fatalities", 0), errors="coerce").fillna(0).clip(lower=0)
    out["event_type"] = out["event_type"].astype(str).str.strip()
    out["location_id"] = out["location_id"].astype(str).str.strip()
    out = out.dropna(subset=["event_date", "location_id", "event_type"])
    return out

def clean_displacement(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["month"] = pd.to_datetime(out["month"], format="%Y-%m", errors="coerce")
    out["arrivals"] = pd.to_numeric(out["arrivals"], errors="coerce").fillna(0).clip(lower=0)
    out["departures"] = pd.to_numeric(out.get("departures", 0), errors="coerce").fillna(0).clip(lower=0)
    out["displacement_type"] = out["displacement_type"].astype(str).str.strip()
    out["location_id"] = out["location_id"].astype(str).str.strip()

    # NEW: optional origin_country
    if "origin_country" in out.columns:
        out["origin_country"] = out["origin_country"].fillna("").astype(str).str.strip()
    else:
        out["origin_country"] = ""

    out = out.dropna(subset=["month", "location_id", "displacement_type"])
    return out

def join_locations(df: pd.DataFrame, locations: pd.DataFrame) -> pd.DataFrame:
    return df.merge(locations, on="location_id", how="left")