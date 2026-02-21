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