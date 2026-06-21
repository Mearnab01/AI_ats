import os
from typing import Any, Dict
import streamlit as st
from supabase import Client, create_client
from dotenv import load_dotenv
import logging 

load_dotenv()  

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("supabase_client")

_URL = os.getenv("SUPABASE_URL", "")
_KEY = os.getenv("SUPABASE_ANON_KEY", "")
_TIMEOUT = 15  # seconds
    

OAUTH_REDIRECT_URL = (
    os.getenv('AUTH_REDIRECT_URL')
    or 'http://localhost:8501'
)
    
def _missing_config() -> str | None:
    if not _URL or not _KEY:
        return 'Supabase is not configured — set SUPABASE_URL and SUPABASE_ANON_KEY in .env or .streamlit/secrets.toml'
    return None

@st.cache_resource
def get_client() -> Client:
    if _missing_config():
        logger.error(_missing_config())
        
    return create_client(_URL, _KEY)


def _session_dict(session, user):
    return {
        "access_token":  session.access_token,
        "refresh_token": session.refresh_token,
        "expires_in":    session.expires_in,
        "user_id":       user.id,
        "email":         user.email,
        "metadata":      user.user_metadata or {},
    }
 
def google_oauth_url() -> Dict[str, Any]:
    err = _missing_config()
    if err:
        return {"error": err}
    try:
        resp = get_client().auth.sign_in_with_oauth({
            'provider': 'google',
            'options': { 'redirect_to': OAUTH_REDIRECT_URL }
        })
        return {"url": resp.url}
    except Exception as exc:
        logger.error(f"Error during Google OAuth sign-in: {exc}")
        return {"error": f"Error during Google OAuth sign-in: {exc}"}

def exchange_code_for_session(auth_code: str) -> Dict[str, Any]:
    err = _missing_config()
    if err:
        return {"error": err}
    client = get_client()
    try:
        storage_key = f'{client.auth._storage_key}-code-verifier'
        code_verifier = client.auth._storage.get_item(storage_key) or ""
        
        # ===== DEBUG START =====
        logger.info("=" * 50)
        logger.info(f"Auth Code: {auth_code}")
        logger.info(f"Storage Key: {storage_key}")
        logger.info(f"Code Verifier Exists: {bool(code_verifier)}")
        logger.info(f"Code Verifier Length: {len(code_verifier)}")
        logger.info(f"Redirect URL: {OAUTH_REDIRECT_URL}")
        logger.info("=" * 50)
        # ===== DEBUG END =====
        
        resp = client.auth.exchange_code_for_session({
            'auth_code': auth_code,
            'code_verifier': code_verifier,
            'redirect_to': OAUTH_REDIRECT_URL
        })
        
        # ===== DEBUG RESPONSE =====
        logger.info(f"Response Session: {resp.session}")
        logger.info(f"Response User: {resp.user}")
        # ===== DEBUG RESPONSE =====
        
        if not resp.session or not resp.user:
            return {"error": "Failed to exchange code for session."}
        return _session_dict(resp.session, resp.user)
    except Exception as exc:
        logger.error(f"Error during code exchange: {exc}")
        return {"error": f"Error during code exchange: {exc}"}

    
# ── Session refresh ────────────────────────────────────────────────────────────
 
def refresh_session(refresh_token: str) -> Dict[str, Any]:
    if _missing_config():
        logger.error(_missing_config())
        return {"error": _missing_config()}
    try:
        resp = get_client().auth.refresh_session(refresh_token)
        if not resp.session or not resp.user:
            return {"error": "Failed to refresh session."}
        return _session_dict(resp.session, resp.user)
    except Exception as exc:
        logger.error(f"Error during session refresh: {exc}")
        return {"error": f"Error during session refresh: {exc}"}
    
# ── Sign out ───────────────────────────────────────────────────────────────────
 
def sign_out()-> None:
    if _missing_config():
        logger.error(_missing_config())
        return
    try:
        get_client().auth.sign_out()
    except Exception as exc:
        logger.error(f"Error during sign-out: {exc}")
        return {"error": f"Error during sign-out: {exc}"}

# ── Get current user ───────────────────────────────────────────────────────────
 
def get_user(access_token: str) -> Dict[str, Any]:
    if _missing_config():
        logger.error(_missing_config())
        return {"error": _missing_config()}
    try:
        resp = get_client().auth.get_user(access_token)
        if not resp.user:
            return {"error": "Failed to retrieve user."}
        return _session_dict(resp.session, resp.user)
    except Exception as exc:
        logger.error(f"Error retrieving user: {exc}")
        return {"error": f"Error retrieving user: {exc}"}