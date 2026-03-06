from __future__ import annotations
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def read_csv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    return pd.read_csv(path)

def ensure_dirs(*paths: str | Path) -> None:
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)