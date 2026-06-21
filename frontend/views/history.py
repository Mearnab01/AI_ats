from __future__ import annotations
from typing import Any, Dict, List
 
import streamlit as st
from frontend.services import api_client
from frontend.components.helpers import (
    card, section_header, svg_icon, badge, score_color, progress_bar, bar_color,
)
 
 
def _score_chip(score: float) -> str:
    color = score_color(score)
    return (
        f'<span style="font-family:\'Fraunces\',serif;font-size:22px;'
        f'font-weight:700;color:{color};">{score:.0f}</span>'
        f'<span style="font-size:12px;color:#555C6B;">/100</span>'
    )
 
 
def _component_mini(cs: dict | Any) -> str:
    def _get(key: str) -> float:
        v = cs.get(key) if isinstance(cs, dict) else getattr(cs, key, 0)
        return float(v or 0)
 
    rows = [
        ("Formatting",   _get("formatting"),        20),
        ("Keywords",     _get("keywords"),           25),
        ("Content",      _get("content"),            25),
        ("Skill Val.",   _get("skill_validation"),   15),
        ("ATS Compat.",  _get("ats_compatibility"),  15),
    ]
    cols_html = ""
    for label, val, mx in rows:
        pct   = (val / mx) * 100 if mx else 0
        color = score_color(pct)
        cols_html += (
            f'<div style="background:#0C0E12;border:1px solid rgba(255,255,255,.07);'
            f'border-radius:8px;padding:10px 12px;">'
            f'<div style="font-size:10px;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:1px;color:#555C6B;margin-bottom:6px;">{label}</div>'
            f'<div style="font-family:\'Fraunces\',serif;font-size:20px;font-weight:700;'
            f'color:{color};">{val:.0f}'
            f'<span style="font-size:12px;color:#555C6B;">/{mx}</span></div>'
            f'<div style="margin-top:6px;">{progress_bar(pct, bar_color(pct / 100))}</div>'
            f'</div>'
        )
    return (
        f'<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px;">'
        f'{cols_html}</div>'
    )
 
 
def render() -> None:
    st.markdown(
        '<h1 style="font-family:\'Fraunces\',serif;font-size:26px;color:#F0F2F5;'
        'margin:0 0 6px;letter-spacing:-0.02em;">Analysis History</h1>'
        '<p style="color:#8C92A0;font-size:14px;margin:0 0 24px;">'
        'Your past resume analyses — click a row to expand scores.</p>',
        unsafe_allow_html=True,
    )
 
    # ── Fetch (token transparently refreshed if expired) ────────────
    from services.auth_utils import ensure_valid_session
    access_token = ensure_valid_session()
 
    if not access_token:
        st.markdown(
            f'<div style="text-align:center;padding:3rem;color:#555C6B;">'
            f'{svg_icon("shield",36,"#555C6B")}'
            f'<div style="font-size:16px;font-weight:600;color:#8C92A0;margin:12px 0 8px;">Sign in required</div>'
            f'<p style="font-size:13px;max-width:280px;margin:0 auto;line-height:1.7;">Sign in to see your analysis history.</p></div>',
            unsafe_allow_html=True,
        )
        return
 
    with st.spinner("Loading history…"):
        try:
            history: List[Dict[str, Any]] = api_client.get_history(access_token)
        except Exception as exc:
            st.error(f"Could not load history: {exc}")
            return
 
    if not history:
        st.markdown(
            card(
                '<div style="text-align:center;padding:3rem;color:#555C6B;">'
                + svg_icon("clock", 40, "#555C6B")
                + '<div style="font-size:16px;font-weight:600;color:#8C92A0;margin:14px 0 8px;">No analyses yet</div>'
                + '<p style="font-size:13px;max-width:280px;margin:0 auto;line-height:1.7;">'
                + 'Upload and analyse a resume to see your history here.</p></div>'
            ),
            unsafe_allow_html=True,
        )
        return
 
    # ── Progress callout ──────────────────────────────────────────
    scores = [float(r.get("ats_score") or r.get("ATS_score") or 0) for r in history]
    if len(scores) >= 2:
        low, high = min(scores), max(scores)
        lo_c = score_color(low)
        hi_c = score_color(high)
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:12px;background:rgba(232,164,74,.05);'
            f'border:1px solid rgba(232,164,74,.15);border-radius:12px;padding:14px 18px;margin-bottom:20px;">'
            f'{svg_icon("trending", 18, "#E8A44A")}'
            f'<p style="margin:0;font-size:14px;color:#8C92A0;">'
            f'Score improved from <strong style="color:{lo_c};">{low:.0f}</strong> to '
            f'<strong style="color:{hi_c};">{high:.0f}</strong> across {len(history)} '
            f'analys{"e" if len(history)==1 else "e"}s.</p></div>',
            unsafe_allow_html=True,
        )
 
    # ── Table header ──────────────────────────────────────────────
    st.markdown(
        '<div style="display:grid;grid-template-columns:2fr 80px 120px 140px 100px;'
        'gap:12px;padding:10px 16px;background:#181B22;border-radius:8px;'
        'margin-bottom:4px;font-size:11px;font-weight:700;text-transform:uppercase;'
        'letter-spacing:1px;color:#555C6B;">',
        unsafe_allow_html=True,
    )
    for h in ["File", "Score", "Date", "Mode", "Action"]:
        st.markdown(f'<span>{h}</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
 
    # ── Rows ──────────────────────────────────────────────────────
    if "history_expanded" not in st.session_state:
        st.session_state.history_expanded = set()
 
    for i, row in enumerate(history):
        analysis_id = row.get("id", str(i))
        filename    = row.get("filename",  "resume.pdf")
        ats_score   = float(row.get("ats_score") or row.get("ATS_score") or 0)
        created_at  = row.get("created_at", "")[:10] if row.get("created_at") else "—"
        has_jd      = bool(row.get("jd_comparison") or row.get("jd_match_analysis"))
        mode_label  = "JD Comparison" if has_jd else "General ATS"
        is_expanded = analysis_id in st.session_state.history_expanded
 
        st.markdown(
            f'<div style="display:grid;grid-template-columns:2fr 80px 120px 140px 100px;'
            f'gap:12px;padding:14px 16px;background:#111318;'
            f'border:1px solid rgba(255,255,255,.07);border-radius:10px;'
            f'margin-bottom:4px;align-items:center;">'
 
            f'<div style="display:flex;align-items:center;gap:10px;">'
            f'<div style="width:32px;height:32px;background:#181B22;border:1px solid rgba(255,255,255,.08);'
            f'border-radius:6px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">'
            f'{svg_icon("file", 14, "#8C92A0")}</div>'
            f'<span style="font-size:14px;font-weight:600;color:#F0F2F5;">{filename}</span></div>'
 
            f'<div>{_score_chip(ats_score)}</div>'
            f'<div style="font-size:13px;color:#8C92A0;">{created_at}</div>'
            f'<div>{badge(mode_label, "brand" if has_jd else "neutral")}</div>'
            f'<div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
 
        bcol1, bcol2, bcol3, bcol4 = st.columns([1, 1, 1, 5])
        with bcol1:
            expand_label = "Collapse" if is_expanded else "Expand"
            if st.button(expand_label, key=f"expand_{analysis_id}_{i}", use_container_width=True):
                if is_expanded:
                    st.session_state.history_expanded.discard(analysis_id)
                else:
                    st.session_state.history_expanded.add(analysis_id)
                st.rerun()
 
        with bcol2:
            # Calls the /history/{id}/pdf endpoint
            if st.button("PDF", key=f"pdf_{analysis_id}_{i}", use_container_width=True):
                token = ensure_valid_session()
                if not token:
                    st.warning("Session expired — please sign in again.")
                else:
                    try:
                        pdf_bytes = api_client.download_history_pdf(analysis_id, token)
                        st.download_button(
                            label    = "Download",
                            data     = pdf_bytes,
                            file_name= f"calibr_report_{analysis_id}.pdf",
                            mime     = "application/pdf",
                            key      = f"dl_{analysis_id}_{i}",
                        )
                    except Exception as exc:
                        st.error(f"PDF generation failed: {exc}")
 
        with bcol3:
            if st.button("Delete", key=f"del_{analysis_id}_{i}", use_container_width=True):
                token = ensure_valid_session()
                if not token:
                    st.warning("Session expired — please sign in again.")
                else:
                    try:
                        api_client.delete_history(analysis_id, token)
                        st.success("Deleted.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Delete failed: {exc}")
 
        if is_expanded:
            cs = row.get("component_scores") or {}
            if cs:
                st.markdown(
                    f'<div style="background:#181B22;border:1px solid rgba(255,255,255,.07);'
                    f'border-radius:10px;padding:16px;margin-bottom:8px;">'
                    f'{_component_mini(cs)}</div>',
                    unsafe_allow_html=True,
                )
 
            strengths = row.get("strengths") or []
            if strengths:
                items = "".join(
                    f'<div style="display:flex;gap:8px;font-size:12px;color:#2ECC8A;'
                    f'padding:4px 0;border-bottom:1px solid rgba(255,255,255,.04);">'
                    f'{svg_icon("check",12,"#2ECC8A")} {s}</div>'
                    for s in strengths[:4]
                )
                st.markdown(
                    f'<div style="background:rgba(46,204,138,.04);border:1px solid rgba(46,204,138,.12);'
                    f'border-radius:8px;padding:12px 14px;margin-bottom:8px;">'
                    f'<div style="font-size:10px;font-weight:700;text-transform:uppercase;'
                    f'letter-spacing:1px;color:#555C6B;margin-bottom:8px;">Strengths</div>'
                    f'{items}</div>',
                    unsafe_allow_html=True,
                )
 
        st.markdown("<div style='height:2px;'></div>", unsafe_allow_html=True)