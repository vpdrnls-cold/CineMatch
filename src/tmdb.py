import os
import requests
import pandas as pd

from functools import lru_cache
from dotenv import load_dotenv

import streamlit as st


load_dotenv()

TMDB_API_TOKEN = os.getenv("TMDB_API_TOKEN")

if not TMDB_API_TOKEN:
    try:
        import streamlit as st
        TMDB_API_TOKEN = st.secrets.get("TMDB_API_TOKEN")
    except Exception:
        TMDB_API_TOKEN = None

if TMDB_API_TOKEN:
    TMDB_API_TOKEN = str(TMDB_API_TOKEN).strip()

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


@lru_cache(maxsize=1000)
def get_poster_url(tmdb_id):

    if pd.isna(tmdb_id):
        return None

    if not TMDB_API_TOKEN:
        return None

    url = f"{BASE_URL}/movie/{int(tmdb_id)}"

    headers = {
        "Authorization": f"Bearer {TMDB_API_TOKEN}",
        "accept": "application/json"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params={"language": "en-US"},
            timeout=5
        )

        if response.status_code != 200:
            return None

        data = response.json()

        poster_path = data.get("poster_path")

        if not poster_path:
            return None

        return f"{IMAGE_BASE_URL}{poster_path}"

    except (requests.RequestException, ValueError, TypeError):
        return None