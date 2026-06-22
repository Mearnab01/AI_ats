import time
import json
import streamlit as st
import streamlit.components.v1 as components
from services import supabase_client

def restore_session_from_cookie() -> bool:
    """
    Try to restore session from the _session_cookie query param.
    Returns True if session was restored.
    """
    if st.session_state.get("access_token"):
        return True  # already logged in

    raw = st.query_params.get("_session_cookie")
    if not raw:
        return False

    try:
        data = json.loads(raw)
        st.session_state.access_token    = data.get("access_token")
        st.session_state.refresh_token   = data.get("refresh_token")
        st.session_state.user_id         = data.get("user_id")
        st.session_state.user_email      = data.get("user_email")
        st.session_state.token_expires_at = float(data.get("token_expires_at") or 0)
        # Clean the URL
        st.query_params.clear()
        return True
    except Exception:
        return False


# ── Core session helpers ───────────────────────────────────────────────────────

def _store_session(session: dict) -> None:
    st.session_state.access_token     = session.get("access_token")
    st.session_state.refresh_token    = session.get("refresh_token")
    st.session_state.user_id          = session.get("user_id")
    st.session_state.user_email       = session.get("email") or session.get("user_email")
    expires_in                        = session.get("expires_in", 3600)
    st.session_state.token_expires_at = time.time() + expires_in
    # _save_session_cookie()  # Commented out as we're not using cookies


def _clear_session() -> None:
    for key in ("access_token", "refresh_token", "user_id", "user_email", "token_expires_at"):
        st.session_state[key] = None
    # _clear_session_cookie()  # Commented out as we're not using cookies


def ensure_valid_session() -> str | None:
    if not st.session_state.access_token:
        return None

    expires_at = st.session_state.token_expires_at or 0
    if time.time() < expires_at - 60:
        return st.session_state.access_token

    # Token expired — try refresh
    result = supabase_client.refresh_session(st.session_state.refresh_token or "")
    if "error" in result:
        _clear_session()
        st.session_state.auth_error = "Your session expired. Please sign in again."
        return None
    _store_session(result)
    return st.session_state.access_token