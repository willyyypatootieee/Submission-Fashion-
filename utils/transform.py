import re
from typing import Optional 

import pandas as pd

def _parse_price_to_idr(value: str, exchange_rate: int =16000) -> Optional[int]:    
    if not isinstance(value, str):
        return None
    m = re.search(r"\$\s*([\d.,]+)", value)
    if not m:
        return None
    usd = m.group(1).replace(",", "")
    try:
        usd_val = float(usd)
        return int(round(usd_val * exchange_rate))
    except ValueError:
        return None
    
def _parse_rating(value: str) -> Optional[float]:
    if not isinstance(value, str):
        return None
    m = re.search(r"(\d+(?:\.\d+)?)", value)
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


def _parse_colors(value: str) -> Optional[int]:
    if not isinstance(value, str):
        return None
    m = re.search(r"(\d+)", value)
    return int(m.group(1)) if m else None


def _clean_size(value: str) -> Optional[str]:
    if not isinstance(value, str):
        return None
    cleaned = re.sub(r"(?i)^size\s*:\s*", "", value).strip()
    return cleaned or None

def _clean_size(value: str) -> Optional[str]:
    if not isinstance(value, str):
        return None
    cleaned = re.sub(r"(?i)^size\s*:\s*", "", value).strip()
    return cleaned or None

def _clean_gender(value: str) -> Optional[str]:
    if not isinstance(value, str):
        return None
    cleaned = re.sub(r"(?i)^gender\s*:\s*", "", value).strip()
    return cleaned or None


def transform_products(df_raw: pd.DataFrame, exchange_rate: int = 16000) -> pd.DataFrame:
    if df_raw is None or df_raw.empty:
        raise ValueError("Input dataframe is empty")

    required = ["Title", "Price", "Rating", "Colors", "Size", "Gender", "timestamp"]
    missing = [c for c in required if c not in df_raw.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df_raw.copy()

    df["Price"] = df["Price"].apply(lambda x: _parse_price_to_idr(x, exchange_rate))
    df["Rating"] = df["Rating"].apply(_parse_rating)
    df["Colors"] = df["Colors"].apply(_parse_colors)
    df["Size"] = df["Size"].apply(_clean_size)
    df["Gender"] = df["Gender"].apply(_clean_gender)
    df["Title"] = df["Title"].astype(str).str.strip()

    invalid_title = {"Unknown Product", "N/A", "None", ""}
    df = df[~df["Title"].isin(invalid_title)]

    df = df.dropna(subset=["Title", "Price", "Rating", "Colors", "Size", "Gender", "timestamp"])
    df = df.drop_duplicates()

    df["Price"] = df["Price"].astype("int64")
    df["Rating"] = df["Rating"].astype("float64")
    df["Colors"] = df["Colors"].astype("int64")
    df["Size"] = df["Size"].astype("string")
    df["Gender"] = df["Gender"].astype("string")
    df["Title"] = df["Title"].astype("string")
    df["timestamp"] = df["timestamp"].astype("string")

    return df[["Title", "Price", "Rating", "Colors", "Size", "Gender", "timestamp"]]