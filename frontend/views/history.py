from __future__ import annotations
from typing import Any, Dict, List
 
import streamlit as st
from frontend.services import api_client
from frontend.components._helpers import (
    svg_icon, score_color, progress_bar, bar_color, badge,
)
 
 
def _score_chip(score: float) -> str:
    color = score_color(score)
    return (
        f'<span style="font-family:\'Fraunces\',serif;font-size:22px;'
        f'font-weight:700;color:{color};">{score:.0f}</span>'
        f'<span style="font-size:12px;color:#555C6B;">/100</span>'
    )
 
 
def _component_mini(cs: dict | Any) -> None:
    """Render component breakdown using native Streamlit columns (no nested HTML grids)."""
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

    cols = st.columns(5)
    for col, (label, val, mx) in zip(cols, rows):
        pct   = (val / mx) * 100 if mx else 0
        color = score_color(pct)
        with col:
            st.markdown(
                f'<div style="background:#0C0E12;border:1px solid rgba(255,255,255,.07);'
                f'border-radius:8px;padding:10px 12px;text-align:center;">'
                f'<div style="font-size:10px;font-weight:700;text-transform:uppercase;'
                f'letter-spacing:1px;color:#555C6B;margin-bottom:6px;">{label}</div>'
                f'<div style="font-family:\'Fraunces\',serif;font-size:20px;font-weight:700;'
                f'color:{color};">{val:.0f}'
                f'<span style="font-size:12px;color:#555C6B;">/{mx}</span></div>'
                f'<div style="margin-top:6px;">{progress_bar(pct, bar_color(pct / 100))}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
 
 
def render() -> None:
    st.markdown(
        '<h1 style="font-family:\'Fraunces\',serif;font-size:26px;color:#F0F2F5;'
        'margin:0 0 6px;letter-spacing:-0.02em;">Analysis History</h1>'
        '<p style="color:#8C92A0;font-size:14px;margin:0 0 24px;">'
        'Your past resume analyses — expand a row to see scores.</p>',
        unsafe_allow_html=True,
    )
 
    # ── Auth check ─────────────────────────────────────────────────
    from services.auth_utils import ensure_valid_session
    access_token = ensure_valid_session()
 
    if not access_token:
        st.markdown(
            f'<div style="text-align:center;padding:3rem;color:#555C6B;">'
            f'{svg_icon("shield", 36, "#555C6B")}'
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
            '<div style="background:#111318;border:1px solid rgba(255,255,255,.08);'
            'border-radius:16px;padding:20px 24px;">'
            '<div style="text-align:center;padding:3rem;color:#555C6B;">'
            + svg_icon("clock", 40, "#555C6B")
            + '<div style="font-size:16px;font-weight:600;color:#8C92A0;margin:14px 0 8px;">No analyses yet</div>'
            + '<p style="font-size:13px;max-width:280px;margin:0 auto;line-height:1.7;">'
            + 'Upload and analyse a resume to see your history here.</p></div></div>',
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

    # ── Table header (native columns, not HTML grid) ───────────────
    h_cols = st.columns([3, 1, 1.5, 1.5])
    for col, label in zip(h_cols, ["File", "Score", "Date", "Mode"]):
        with col:
            st.markdown(
                f'<div style="font-size:11px;font-weight:700;text-transform:uppercase;'
                f'letter-spacing:1px;color:#555C6B;padding:8px 4px;">{label}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

    # ── Rows ──────────────────────────────────────────────────────
    for i, row in enumerate(history):
        analysis_id = row.get("id", str(i))
        filename    = row.get("filename",  "resume.pdf")
        ats_score   = float(row.get("ats_score") or row.get("ATS_score") or 0)
        created_at  = row.get("created_at", "")[:10] if row.get("created_at") else "—"
        has_jd      = bool(row.get("jd_comparison") or row.get("jd_match_analysis"))
        mode_label  = "JD Comparison" if has_jd else "General ATS"
        score_color_val = score_color(ats_score)

        # Row as native columns
        r_cols = st.columns([3, 1, 1.5, 1.5])
        with r_cols[0]:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:10px;padding:12px 4px;">'
                f'<div style="width:32px;height:32px;background:#181B22;border:1px solid rgba(255,255,255,.08);'
                f'border-radius:6px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">'
                f'{svg_icon("file", 14, "#8C92A0")}</div>'
                f'<span style="font-size:14px;font-weight:600;color:#F0F2F5;">{filename}</span></div>',
                unsafe_allow_html=True,
            )
        with r_cols[1]:
            st.markdown(
                f'<div style="padding:12px 4px;">{_score_chip(ats_score)}</div>',
                unsafe_allow_html=True,
            )
        with r_cols[2]:
            st.markdown(
                f'<div style="font-size:13px;color:#8C92A0;padding:16px 4px;">{created_at}</div>',
                unsafe_allow_html=True,
            )
        with r_cols[3]:
            st.markdown(
                f'<div style="padding:12px 4px;">{badge(mode_label, "brand" if has_jd else "neutral")}</div>',
                unsafe_allow_html=True,
            )

        # Action buttons row
        b_cols = st.columns([1, 1, 1, 5])
        with b_cols[0]:
            with st.expander("Expand", expanded=False):
                cs = row.get("component_scores") or {}
                if cs:
                    st.markdown(
                        '<div style="margin-bottom:12px;font-size:11px;font-weight:700;'
                        'text-transform:uppercase;letter-spacing:1px;color:#555C6B;">Component Scores</div>',
                        unsafe_allow_html=True,
                    )
                    _component_mini(cs)

                strengths = row.get("strengths") or []
                if strengths:
                    items_html = "".join(
                        f'<div style="display:flex;gap:8px;font-size:12px;color:#2ECC8A;'
                        f'padding:5px 0;border-bottom:1px solid rgba(255,255,255,.04);">'
                        f'{svg_icon("check", 12, "#2ECC8A")} {s}</div>'
                        for s in strengths[:4]
                    )
                    st.markdown(
                        f'<div style="background:rgba(46,204,138,.04);border:1px solid rgba(46,204,138,.12);'
                        f'border-radius:8px;padding:12px 14px;margin-top:12px;">'
                        f'<div style="font-size:10px;font-weight:700;text-transform:uppercase;'
                        f'letter-spacing:1px;color:#555C6B;margin-bottom:8px;">Strengths</div>'
                        f'{items_html}</div>',
                        unsafe_allow_html=True,
                    )

                if not cs and not strengths:
                    st.markdown(
                        '<p style="font-size:13px;color:#555C6B;margin:8px 0;">No detailed data available.</p>',
                        unsafe_allow_html=True,
                    )

        with b_cols[1]:
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
 
        with b_cols[2]:
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

        # Divider between rows
        st.markdown(
            '<div style="height:1px;background:rgba(255,255,255,.05);margin:4px 0 8px;"></div>',
            unsafe_allow_html=True,
        )