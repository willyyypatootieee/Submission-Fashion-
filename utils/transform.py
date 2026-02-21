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