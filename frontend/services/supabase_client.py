from __future__ import annotations
import os
from typing import Any, Dict

import requests

_URL = os.getenv("SUPABASE_URL", "")
_KEY = os.getenv("SUPABASE_KEY", "")
_TIMEOUT = 15  # seconds

def _headers(access_token: str = "") -> Dict[str, str]:
    h = {"apikey": _KEY, "Content-Type": "application/json"}
    if access_token:
        h["Authorization"] = f"Bearer {access_token}"
    return h

def get_google_oauth_url(redirect_url: str) -> str:
    """Return the Google OAuth sign-in URL."""
    return (
        f"{_URL}/auth/v1/authorize"
        f"?provider=google"
        f"&redirect_to={redirect_url}"
    )


def exchange_code_for_session(code: str) -> Dict[str, Any]:
    """Exchange an OAuth code for a Supabase session."""
    try:
        resp = requests.post(
            f"{_URL}/auth/v1/token?grant_type=pkce",
            headers=_headers(),
            json={"auth_code": code},
            timeout=_TIMEOUT,
        )
    except requests.RequestException as exc:
        return {"error": f"Network error during sign-in: {exc}"}
    
    if not resp.ok:
        return {"error": resp.text}
    data = resp.json()
    return {
        "access_token":  data.get("access_token", ""),
        "refresh_token": data.get("refresh_token", ""),
        "expires_in":    data.get("expires_in", 3600),
        "user_id":       data.get("user", {}).get("id", ""),
        "email":         data.get("user", {}).get("email", ""),
    }
    
# ── Session refresh ────────────────────────────────────────────────────────────
 
def refresh_session(refresh_token: str) -> Dict[str, Any]:
    if not refresh_token:
        return {"error": "Missing refresh token."}
    
    try:
        resp = requests.post(
            f"{_URL}/auth/v1/token?grant_type=refresh_token",
            headers=_headers(),
            json={"refresh_token": refresh_token},
            timeout=_TIMEOUT,
        )
    except requests.RequestException as exc:
        return {"error": f"Network error during session refresh: {exc}"}
    
    if not resp.ok:
        return {"error": resp.text}
    
    data = resp.json()
    return {
        "access_token":  data.get("access_token", ""),
        "refresh_token": data.get("refresh_token", ""),
        "expires_in":    data.get("expires_in", 3600),
        "user_id":       data.get("user", {}).get("id", ""),
        "email":         data.get("user", {}).get("email", ""),
    }
    
# ── Sign out ───────────────────────────────────────────────────────────────────
 
def sign_out(access_token: str) -> Dict[str, Any]:
    if not access_token:
        return {"ok": True} # No access token means the user is already signed out.
    
    try:
        resp = requests.post(
            f"{_URL}/auth/v1/logout",
            headers=_headers(access_token),
            timeout=_TIMEOUT,
        )
    except requests.RequestException as exc:
        return {"error": f"Network error during sign-out: {exc}"}
    
    if resp.status_code not in (200, 204):
        return {"error": resp.text}
    return {"ok": True}

# ── Get current user ───────────────────────────────────────────────────────────
 
def get_user(access_token: str) -> Dict[str, Any]:
    if not access_token:
        return {"error": "Missing access token."}
    
    try:
        resp = requests.get(
            f"{_URL}/auth/v1/user",
            headers=_headers(access_token),
            timeout=_TIMEOUT,
        )
    except requests.RequestException as exc:
        return {"error": f"Network error during get user: {exc}"}
    
    if not resp.ok:
        return {"error": resp.text}
    
    data = resp.json()
    return {
        "user_id": data.get("id", ""),
        "email":   data.get("email", ""),
        "metadata": data.get("user_metadata", {}),
    }