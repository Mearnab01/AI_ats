import time
import streamlit as st
from services import supabase_client

def _store_session(session: dict)->None:
    st.session_state.access_token  = session.get("access_token")
    st.session_state.refresh_token = session.get("refresh_token")
    st.session_state.user_id       = session.get("user_id")
    st.session_state.user_email    = session.get("email")
    expires_in                     = session.get("expires_in", 3600)
    st.session_state.token_expires_at = time.time() + expires_in
    
def _clear_session()->None:
    for key in ("access_token","refresh_token","user_id","user_email","token_expires_at"):
        st.session_state[key] = None
    
  
def ensure_valid_session() -> str | None:
    if not st.session_state.access_token:
        return None
    
    expires_at = st.session_state.token_expires_at or 0
    if time.time() < expires_at - 60:
        return st.session_state.access_token
    
    # token expired or about to expire, refresh it
    
    result = supabase_client.refresh_session(st.session_state.refresh_token or "")
    
    if "error" in result:
        _clear_session()
        st.session_state.auth_error = "Your session expired. Please sign in again."
        print(f"Session refresh failed: {result['error']}")
        return None
    _store_session(result)
    return st.session_state.access_token