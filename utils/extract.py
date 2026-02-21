import re
import time
from datetime import datetime
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://fashion-studio.dicoding.dev"
TIMEOUT = 20

class ExtractError(exception):
    pass

def build_page_url(page: int) -> str:
    if page < 1:
        raise ValueError("Page number must be >= 1")
    return f"{BASE_URL}" if page == 1 else f"{BASE_URL}/page/{page}"

def fetch_html(session: requests.Session, url: str) -> str:
    try:
        resp = session.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as exc:
        raise ExtractError(f"Failed to fetch URL: {url}") from exc


def _find_title(card: Tag) -> Optional[str]:
    for selector in ["h3", "h2", ".product-title", ".card-title", ".title"]:
        node = card.select_one(selector)
        if node:
            txt = node.get_text(strip=True)
            if txt:
                return txt
    return None


def _find_text_by_pattern(card: Tag, pattern: str) -> Optional[str]:
    rgx = re.compile(pattern, re.IGNORECASE)
    for txt in card.stripped_strings:
        if rgx.search(txt):
            return txt.strip()
    return None

def parse_product_card(card: Tag, ts: str) -> Optional[Dict[str, str]]:
    try:
        title = _find_title(card)
        price = _find_text_by_pattern(card, r"\$\s*[\d.,]+")
        rating = _find_text_by_pattern(card, r"rating|/ 5")
        colors = _find_text_by_pattern(card, r"\b\d+\s*colors?\b")
        size = _find_text_by_pattern(card, r"size\s*:")
        gender = _find_text_by_pattern(card, r"gender\s*:")

        if not all([title, price, rating, colors, size, gender]):
            return None

        return {
            "Title": title,
            "Price": price,
            "Rating": rating,
            "Colors": colors,
            "Size": size,
            "Gender": gender,
            "timestamp": ts,
        }
    except ExtractError:
        return None