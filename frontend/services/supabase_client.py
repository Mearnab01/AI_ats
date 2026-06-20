"""services/supabase_client.py — Supabase auth helpers for Streamlit."""

from __future__ import annotations
import os
from typing import Any, Dict

import requests

_URL = os.getenv("SUPABASE_URL", "")
_KEY = os.getenv("SUPABASE_KEY", "")


def get_google_oauth_url(redirect_url: str) -> str:
    """Return the Google OAuth sign-in URL."""
    return (
        f"{_URL}/auth/v1/authorize"
        f"?provider=google"
        f"&redirect_to={redirect_url}"
    )


def exchange_code_for_session(code: str) -> Dict[str, Any]:
    """Exchange an OAuth code for a Supabase session."""
    resp = requests.post(
        f"{_URL}/auth/v1/token?grant_type=pkce",
        headers={"apikey": _KEY, "Content-Type": "application/json"},
        json={"auth_code": code},
        timeout=15,
    )
    if not resp.ok:
        return {"error": resp.text}
    data = resp.json()
    return {
        "access_token":  data.get("access_token", ""),
        "refresh_token": data.get("refresh_token", ""),
        "user_id":       data.get("user", {}).get("id", ""),
        "email":         data.get("user", {}).get("email", ""),
    }