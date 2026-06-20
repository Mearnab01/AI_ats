"""score_display.py — Overall score hero + component breakdown bars."""

from __future__ import annotations
from typing import Any, Dict

import streamlit as st
from frontend.components.helpers import (
    card, section_header, progress_bar, bar_color, score_color, badge,
)


def display_score_header(analysis: Dict[str, Any]) -> None:
    overall = float(analysis.get("ATS_score") or analysis.get("ats_score") or 0)
    interp  = analysis.get("interpretation", "")
    color   = score_color(overall)
    band    = "Excellent" if overall >= 80 else "Good" if overall >= 60 else "Needs Work"
    band_v  = "success" if overall >= 80 else "warning" if overall >= 60 else "danger"

    st.markdown(
        f"""
        <div style="text-align:center;padding:3rem 2rem;background:linear-gradient(160deg,#181B22 0%,#111318 100%);
                    border:1px solid {color}20;border-radius:20px;position:relative;overflow:hidden;margin-bottom:20px;">
            <div style="position:absolute;top:-80px;left:50%;transform:translateX(-50%);
                        width:320px;height:320px;border-radius:50%;
                        background:radial-gradient(circle,{color}0D 0%,transparent 65%);pointer-events:none;"></div>
            <div style="position:relative;">
                <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:2px;
                            color:#555C6B;margin-bottom:16px;">Overall ATS Score</div>
                <div class="score-hero-number animate-count-up" data-score="{overall:.0f}"
                     style="font-family:'Fraunces',serif;font-size:80px;font-weight:700;
                            color:{color};line-height:1;letter-spacing:-4px;">
                    {overall:.0f}<span style="font-size:32px;font-weight:400;color:#555C6B;">/100</span>
                </div>
                <p style="color:#8C92A0;font-size:14px;margin-top:16px;font-style:italic;">
                    {interp or ("Excellent — your resume is highly ATS-optimised." if overall >= 80 else
                                "Good. A few targeted improvements will push this higher." if overall >= 60 else
                                "Needs work. Follow the recommendations below.")}
                </p>
                <div style="margin-top:12px;">{badge(band, band_v)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_component_breakdown(analysis: Dict[str, Any]) -> None:
    cs = analysis.get("component_scores") or {}

    def _get(key: str) -> float:
        v = cs.get(key) if isinstance(cs, dict) else getattr(cs, key, 0)
        return float(v or 0)

    rows = [
        ("Keywords & Skills",  "Keyword density & JD relevance",   _get("keywords"),          25),
        ("Content Quality",    "Action verbs & achievements",       _get("content"),           25),
        ("Formatting",         "Structure & section headers",       _get("formatting"),        20),
        ("Skill Validation",   "Skills backed by project evidence", _get("skill_validation"),  15),
        ("ATS Compatibility",  "Clean format, no parse blockers",   _get("ats_compatibility"), 15),
    ]

    rows_html = ""
    for label, sub, val, max_val in rows:
        pct   = (val / max_val) * 100 if max_val else 0
        color = score_color(val / max_val * 100) if max_val else "#8C92A0"
        rows_html += f"""
        <div style="display:flex;align-items:center;gap:16px;padding:10px 0;
                    border-bottom:1px solid rgba(255,255,255,.06);">
            <div style="width:152px;flex-shrink:0;">
                <div style="font-size:13px;font-weight:600;color:#F0F2F5;">{label}</div>
                <div style="font-size:11px;color:#555C6B;margin-top:2px;">{sub}</div>
            </div>
            <div style="flex:1;">{progress_bar(pct, bar_color(pct / 100))}</div>
            <div style="width:52px;text-align:right;font-size:13px;font-weight:700;
                        color:{color};flex-shrink:0;">{val:.0f}/{max_val}</div>
        </div>
        """

    st.markdown(
        card(
            section_header("chart", "Score Breakdown", "Five weighted components")
            + f'<div style="margin-top:-4px;">{rows_html}</div>'
        ),
        unsafe_allow_html=True,
    )