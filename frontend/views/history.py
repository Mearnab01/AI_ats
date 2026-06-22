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
        '<span style="font-family:\'Fraunces\',serif;font-size:22px;font-weight:700;color:'
        + color + ';">' + str(int(score)) + '</span>'
        + '<span style="font-size:12px;color:#555C6B;">/100</span>'
    )


def _component_mini(cs: dict | Any) -> None:
    """Render component breakdown using native columns."""
    def _get(key: str) -> float:
        v = cs.get(key) if isinstance(cs, dict) else getattr(cs, key, 0)
        return float(v or 0)

    rows = [
        ("Keywords",   _get("keywords"),          25),
        ("Content",    _get("content"),            25),
        ("Format",     _get("formatting"),         20),
        ("Skills",     _get("skill_validation"),   15),
        ("ATS",        _get("ats_compatibility"),  15),
    ]
    cols = st.columns(5)
    for col, (label, val, mx) in zip(cols, rows):
        pct   = (val / mx) * 100 if mx else 0
        color = score_color(pct)
        with col:
            st.markdown(
                '<div style="background:#0C0E12;border:1px solid rgba(255,255,255,.07);'
                'border-radius:8px;padding:10px 12px;text-align:center;">'
                '<div style="font-size:9px;font-weight:700;text-transform:uppercase;'
                'letter-spacing:1px;color:#555C6B;margin-bottom:6px;">' + label + '</div>'
                '<div style="font-family:\'Fraunces\',serif;font-size:18px;font-weight:700;color:'
                + color + ';">' + str(int(val)) + '<span style="font-size:11px;color:#555C6B;">/' + str(mx) + '</span></div>'
                '<div style="margin-top:6px;">' + progress_bar(pct, bar_color(pct / 100)) + '</div>'
                '</div>',
                unsafe_allow_html=True,
            )


def _get_row_data(row: Dict) -> Dict:
    """Flatten analysis_result fields to the top level for display."""
    ar = row.get("analysis_result") or {}
    cs_raw = ar.get("component_scores") or {}
    # component_scores may be a dict or a Pydantic model-like dict
    if hasattr(cs_raw, "model_dump"):
        cs_raw = cs_raw.model_dump()

    return {
        "id":          str(row.get("id", "")),
        "filename":    row.get("filename", "resume.pdf"),
        "ats_score":   float(row.get("ats_score") or ar.get("ATS_score") or ar.get("ats_score") or 0),
        "created_at":  (row.get("created_at") or "")[:10] or "—",
        "has_jd":      bool(ar.get("jd_comparison") or ar.get("jd_match_analysis")),
        "strengths":   ar.get("strengths") or [],
        "component_scores": cs_raw,
        "missing_keywords": ar.get("missing_keywords") or row.get("missing_keywords") or [],
        "jd":          ar.get("jd_comparison") or ar.get("jd_match_analysis"),
    }


def render() -> None:
    st.markdown(
        '<h1 style="font-family:\'Fraunces\',serif;font-size:26px;color:#F0F2F5;'
        'margin:0 0 6px;letter-spacing:-0.02em;">Analysis History</h1>'
        '<p style="color:#8C92A0;font-size:14px;margin:0 0 24px;">'
        'Your past resume analyses. Expand a row to see full breakdown.</p>',
        unsafe_allow_html=True,
    )

    from services.auth_utils import ensure_valid_session
    access_token = ensure_valid_session()

    if not access_token:
        st.markdown(
            '<div style="text-align:center;padding:3rem;color:#555C6B;">'
            + svg_icon("shield", 36, "#555C6B")
            + '<div style="font-size:16px;font-weight:600;color:#8C92A0;margin:12px 0 8px;">Sign in required</div>'
            '<p style="font-size:13px;max-width:280px;margin:0 auto;line-height:1.7;">'
            'Sign in to see your analysis history.</p></div>',
            unsafe_allow_html=True,
        )
        return

    with st.spinner("Loading history…"):
        try:
            raw_history: List[Dict[str, Any]] = api_client.get_history(access_token)
        except Exception as exc:
            st.error(f"Could not load history: {exc}")
            return

    if not raw_history:
        st.markdown(
            '<div style="background:#111318;border:1px solid rgba(255,255,255,.08);'
            'border-radius:16px;padding:40px 24px;text-align:center;">'
            + svg_icon("clock", 40, "#555C6B")
            + '<div style="font-size:16px;font-weight:600;color:#8C92A0;margin:14px 0 8px;">No analyses yet</div>'
            '<p style="font-size:13px;max-width:280px;margin:0 auto;line-height:1.7;color:#555C6B;">'
            'Upload and analyse a resume to see your history here.</p></div>',
            unsafe_allow_html=True,
        )
        return

    history = [_get_row_data(r) for r in raw_history]

    # ── Progress callout ──────────────────────────────────────────
    scores = [r["ats_score"] for r in history]
    if len(scores) >= 2:
        lo, hi = min(scores), max(scores)
        st.markdown(
            '<div style="display:flex;align-items:center;gap:12px;background:rgba(232,164,74,.05);'
            'border:1px solid rgba(232,164,74,.15);border-radius:12px;padding:14px 18px;margin-bottom:20px;">'
            + svg_icon("trending", 18, "#E8A44A")
            + '<p style="margin:0;font-size:14px;color:#8C92A0;">Score improved from '
            '<strong style="color:' + score_color(lo) + ';">' + str(int(lo)) + '</strong>'
            ' to <strong style="color:' + score_color(hi) + ';">' + str(int(hi)) + '</strong>'
            ' across ' + str(len(history)) + ' analyses.</p></div>',
            unsafe_allow_html=True,
        )

    # ── Table header ───────────────────────────────────────────────
    h_cols = st.columns([3, 1, 1.5, 1.5])
    for col, label in zip(h_cols, ["File", "Score", "Date", "Mode"]):
        with col:
            st.markdown(
                '<div style="font-size:11px;font-weight:700;text-transform:uppercase;'
                'letter-spacing:1px;color:#555C6B;padding:6px 4px;">' + label + '</div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div style="height:1px;background:rgba(255,255,255,.07);margin-bottom:8px;"></div>', unsafe_allow_html=True)

    # ── Rows ──────────────────────────────────────────────────────
    for i, row in enumerate(history):
        analysis_id = row["id"]
        filename    = row["filename"]
        ats_score   = row["ats_score"]
        created_at  = row["created_at"]
        has_jd      = row["has_jd"]
        mode_label  = "JD Match" if has_jd else "General ATS"

        # Info row
        r_cols = st.columns([3, 1, 1.5, 1.5])
        with r_cols[0]:
            st.markdown(
                '<div style="display:flex;align-items:center;gap:10px;padding:10px 4px;">'
                '<div style="width:30px;height:30px;background:#181B22;border:1px solid rgba(255,255,255,.08);'
                'border-radius:6px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">'
                + svg_icon("file", 13, "#8C92A0") +
                '</div><span style="font-size:13px;font-weight:600;color:#F0F2F5;">' + filename + '</span></div>',
                unsafe_allow_html=True,
            )
        with r_cols[1]:
            st.markdown('<div style="padding:10px 4px;">' + _score_chip(ats_score) + '</div>', unsafe_allow_html=True)
        with r_cols[2]:
            st.markdown('<div style="font-size:13px;color:#8C92A0;padding:14px 4px;">' + created_at + '</div>', unsafe_allow_html=True)
        with r_cols[3]:
            st.markdown('<div style="padding:10px 4px;">' + badge(mode_label, "brand" if has_jd else "neutral") + '</div>', unsafe_allow_html=True)

        # Action buttons
        b1, b2, b3, _ = st.columns([4, 1, 1, 0.5])

        with b1:
            with st.expander("Expand", expanded=False):
                cs = row["component_scores"]
                if cs:
                    st.markdown(
                        '<div style="font-size:10px;font-weight:700;text-transform:uppercase;'
                        'letter-spacing:1px;color:#555C6B;margin:8px 0 10px;">Component Scores</div>',
                        unsafe_allow_html=True,
                    )
                    _component_mini(cs)
                    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

                strengths = row["strengths"]
                if strengths:
                    items_html = ""
                    for s in strengths[:5]:
                        items_html += (
                            '<div style="display:flex;gap:8px;font-size:12px;color:#2ECC8A;'
                            'padding:5px 0;border-bottom:1px solid rgba(255,255,255,.04);">'
                            + svg_icon("check", 12, "#2ECC8A") + ' <span>' + str(s) + '</span></div>'
                        )
                    st.markdown(
                        '<div style="background:rgba(46,204,138,.04);border:1px solid rgba(46,204,138,.12);'
                        'border-radius:8px;padding:12px 14px;margin-top:4px;">'
                        '<div style="font-size:10px;font-weight:700;text-transform:uppercase;'
                        'letter-spacing:1px;color:#555C6B;margin-bottom:8px;">Strengths</div>'
                        + items_html + '</div>',
                        unsafe_allow_html=True,
                    )

                jd = row["jd"]
                if jd and isinstance(jd, dict):
                    kw_pct  = float(jd.get("match_percentage", 0))
                    missing = jd.get("missing_keywords") or []
                    st.markdown(
                        '<div style="background:rgba(74,158,245,.04);border:1px solid rgba(74,158,245,.12);'
                        'border-radius:8px;padding:12px 14px;margin-top:8px;">'
                        '<div style="font-size:10px;font-weight:700;text-transform:uppercase;'
                        'letter-spacing:1px;color:#555C6B;margin-bottom:8px;">JD Match</div>'
                        '<div style="font-size:20px;font-weight:700;color:#4A9EF5;">' + str(int(kw_pct)) + '%</div>'
                        + (
                            '<div style="margin-top:8px;font-size:11px;color:#555C6B;">Missing: '
                            + ', '.join(missing[:8]) + '</div>' if missing else ''
                        ) + '</div>',
                        unsafe_allow_html=True,
                    )

                if not cs and not strengths and not jd:
                    st.markdown('<p style="font-size:13px;color:#555C6B;padding:8px 0;">No detailed data for this entry.</p>', unsafe_allow_html=True)

        with b2:
            if st.button("PDF", key="pdf_" + analysis_id + "_" + str(i), use_container_width=True):
                token = ensure_valid_session()
                if not token:
                    st.warning("Session expired.")
                else:
                    with st.spinner("Generating PDF…"):
                        try:
                            pdf_bytes = api_client.download_history_pdf(analysis_id, token)
                            st.download_button(
                                label="Download",
                                data=pdf_bytes,
                                file_name="Criterion_" + analysis_id + ".pdf",
                                mime="application/pdf",
                                key="dl_" + analysis_id + "_" + str(i),
                            )
                        except Exception as exc:
                            st.error("PDF failed: " + str(exc))

        with b3:
            if st.button("Delete", key="del_" + analysis_id + "_" + str(i), use_container_width=True):
                token = ensure_valid_session()
                if not token:
                    st.warning("Session expired.")
                else:
                    try:
                        api_client.delete_history(analysis_id, token)
                        st.success("Deleted.")
                        st.rerun()
                    except Exception as exc:
                        st.error("Delete failed: " + str(exc))

        st.markdown('<div style="height:1px;background:rgba(255,255,255,.04);margin:4px 0 10px;"></div>', unsafe_allow_html=True)