import sys
from pathlib import Path

import streamlit as st
from services import supabase_client
from services.auth_utils import (
    _store_session,
    _clear_session
) 
import streamlit.components.v1 as components

sys.path.insert(0, str(Path(__file__).parent.parent))

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title             = "Criterion — Resume Intelligence",
    page_icon              = ":material/hexagon:",
    layout                 = "wide",
    initial_sidebar_state  = "expanded",
)

# ── Asset loaders ──────────────────────────────────────────────────────────────
_STATIC = Path(__file__).parent / "static"

def _load_fonts() -> str:
    return (
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?'
        'family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;'
        '1,9..144,400&family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;'
        '0,9..40,600;0,9..40,700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">'
    )


def _load_css() -> str:
    css_dir = _STATIC / "css"
    parts   = [
        "variables.css",
        "base.css",
        "components.css",
        "animations.css",
        "streamlit_overrides.css",
    ]
    combined = ""
    for part in parts:
        p = css_dir / part
        if p.exists():
            combined += p.read_text(encoding="utf-8")
    return f"<style>{combined}</style>"


def _load_js() -> None:
    js_path = _STATIC / "js" / "ui.js"
    if js_path.exists():
        components.html(
            f"<script>{js_path.read_text(encoding='utf-8')}</script>",
            height=0,
        )


# Inject fonts first (before any st.markdown that renders HTML)
st.markdown(_load_fonts(), unsafe_allow_html=True)
st.markdown(_load_css(),   unsafe_allow_html=True)
_load_js()

# ── Auth session state ─────────────────────────────────────────────────────────
for key, default in [
    ("access_token",  None),
    ("refresh_token", None),
    ("token_expires_at", None),
    ("user_id",       None),
    ("user_email",    None),
    ("auth_error",    None),
    ("auth_info",     None),
    ("current_view",  "landing"),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ── Google OAuth code exchange ──────────────────────────────────────────────────
if not st.session_state.access_token and "code" in st.query_params:
    
    result = supabase_client.exchange_code_for_session(st.query_params["code"])
    st.query_params.clear()
    if "error" in result:
        st.session_state.auth_error = f"Sign-in failed: {result['error']}"
    else:
        _store_session(result)
        st.rerun()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:10px;padding:4px 0 20px 0;border-bottom:1px solid rgba(255,255,255,.08);margin-bottom:16px;">
            <div style="width:32px;height:32px;background:linear-gradient(135deg,#E8A44A,#C4852E);border-radius:8px;display:flex;align-items:center;justify-content:center;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0C0E12" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>
                </svg>
            </div>
            <span style="font-family:'Fraunces',serif;font-weight:700;font-size:17px;color:#F0F2F5;letter-spacing:-0.02em;">
                Criterion<span style="color:#E8A44A;">.</span>
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#555C6B;padding:0 4px;margin-bottom:8px;">Navigation</div>',
        unsafe_allow_html=True,
    )

    nav_items = [
        ("landing", "Home"),
        ("scorer",  "Analyse"),
        ("history", "History"),
        ("jobs",    "Jobs"), 
    ]

    for view_key, label in nav_items:
        is_active = st.session_state.current_view == view_key
        bg      = "rgba(232,164,74,.07)" if is_active else "transparent"
        color   = "#E8A44A" if is_active else "#8C92A0"
        border  = "1px solid rgba(232,164,74,.2)" if is_active else "1px solid transparent"

        if st.button(
            label,
            key = f"nav_{view_key}",
            use_container_width=True,
        ):
            st.session_state.current_view = view_key
            st.rerun()

    # Model status box
    st.markdown(
        """
        <div style="margin-top:24px;background:#181B22;border:1px solid rgba(255,255,255,.07);border-radius:10px;padding:14px;">
            <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;color:#555C6B;margin-bottom:10px;">Models Active</div>
            <div style="display:flex;align-items:center;gap:8px;padding:5px 0;border-bottom:1px solid rgba(255,255,255,.05);">
                <div style="width:6px;height:6px;border-radius:50%;background:#2ECC8A;box-shadow:0 0 6px #2ECC8A;flex-shrink:0;"></div>
                <div><div style="font-size:12px;font-weight:600;color:#F0F2F5;">Fine-tuned BERT</div><div style="font-size:10px;color:#555C6B;">JD matching · MAE 0.0468</div></div>
            </div>
            <div style="display:flex;align-items:center;gap:8px;padding:5px 0;border-bottom:1px solid rgba(255,255,255,.05);">
                <div style="width:6px;height:6px;border-radius:50%;background:#E8A44A;box-shadow:0 0 6px #E8A44A;flex-shrink:0;"></div>
                <div><div style="font-size:12px;font-weight:600;color:#F0F2F5;">LLaMA 3.3-70B</div><div style="font-size:10px;color:#555C6B;">Extraction · via Groq</div></div>
            </div>
            <div style="display:flex;align-items:center;gap:8px;padding:5px 0;">
                <div style="width:6px;height:6px;border-radius:50%;background:#4A9EF5;box-shadow:0 0 6px #4A9EF5;flex-shrink:0;"></div>
                <div><div style="font-size:12px;font-weight:600;color:#F0F2F5;">spaCy en_core_web_md</div><div style="font-size:10px;color:#555C6B;">NER · privacy check</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Auth state
    st.markdown("<hr style='border-color:rgba(255,255,255,.06);margin:20px 0;'>", unsafe_allow_html=True)
    if st.session_state.auth_error:
        st.markdown(
            f'<div style="background:rgba(240,80,58,.08);border:1px solid rgba(240,80,58,.2);'
            f'border-radius:8px;padding:8px 12px;font-size:12px;color:#F0503A;margin-bottom:10px;">'
            f'{st.session_state.auth_error}</div>',
            unsafe_allow_html=True,
        )
        st.session_state.auth_error = None 
        
    if st.session_state.user_email:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:10px;">'
            f'<div style="width:6px;height:6px;border-radius:50%;background:#2ECC8A;flex-shrink:0;"></div>'
            f'<span style="font-size:12px;color:#E8A44A;font-weight:600;word-break:break-all;">'
            f'{st.session_state.user_email}</span></div>',
            unsafe_allow_html=True,
        )
        if st.button("Sign out", use_container_width=True):
            
            result = supabase_client.sign_out()
            if "error" in result:
                st.session_state.auth_error = f"Sign-out failed: {result['error']}"
            _clear_session()
            st.rerun()
    else:
        st.markdown('<div style="font-size:12px;color:#555C6B;margin-bottom:8px;">Not signed in</div>', unsafe_allow_html=True)
        oauth = supabase_client.google_oauth_url()
        if "error" in oauth:
            st.markdown(
                f'<div style="background:rgba(240,80,58,.08);border:1px solid rgba(240,80,58,.2);'
                f'border-radius:8px;padding:8px 12px;font-size:12px;color:#F0503A;margin-bottom:10px;">'
                f'{oauth["error"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.link_button("Sign in with Google", oauth["url"], use_container_width=True)
            
            
        

# ── Route ──────────────────────────────────────────────────────────────────────
view = st.session_state.current_view

if view == "landing":
    from frontend.views.landing import render
    render()
elif view == "scorer":
    from frontend.views.scorer import render
    render()
elif view == "history":
    from frontend.views.history import render
    render()
elif view == "jobs":
    from frontend.views.jobs import render
    render()
else:
    from frontend.views.landing import render
    render()
    
    
    
# to run app: streamlit run frontend/streamlit_app.py