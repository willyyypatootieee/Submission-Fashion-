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