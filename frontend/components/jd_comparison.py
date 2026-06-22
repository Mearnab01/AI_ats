"""jd_comparison.py — JD match analysis panel."""

from __future__ import annotations
from typing import Any, Dict

import streamlit as st
from frontend.components._helpers import card, section_header, progress_bar, bar_color, pill, svg_icon


def display_jd_comparison(analysis: Dict[str, Any]) -> None:
    
    jd = analysis.get("jd_comparison") or analysis.get("jd_match_analysis")    
    if not jd:
        st.markdown(
            card(
                section_header("target", "Job Description Match")
                + '<div style="text-align:center;padding:2rem;color:#555C6B;">'
                + '<div style="margin:0 auto 12px;">'
                + svg_icon("file", 36, "#555C6B")
                + '</div><div style="font-size:14px;font-weight:600;color:#8C92A0;margin-bottom:8px;">No Job Description Provided</div>'
                + '<p style="font-size:13px;max-width:360px;margin:0 auto;line-height:1.7;">Upload a JD on the Analyse page for keyword gap, semantic similarity, and tailored recommendations.</p>'
                + '</div>'
            ),
            unsafe_allow_html=True,
        )
        return

    if hasattr(jd, "model_dump"):
        jd = jd.model_dump()

    kw_pct  = float(jd.get("match_percentage",   0))
    sem_raw = float(jd.get("semantic_similarity", 0))
    sem_pct = sem_raw * 100
    band    = jd.get("match_band", "")
    matched = jd.get("matched_keywords", [])
    missing = jd.get("missing_keywords",  [])
    gap     = jd.get("skills_gap",        [])

    bert_info = analysis.get("bert_model_info") or {}
    bert_active = bert_info.get("using_finetuned", False)
    bert_mae    = bert_info.get("finetuned_mae", "")

    kw_color  = "#4A9EF5" if kw_pct  >= 70 else "#F5A623" if kw_pct  >= 45 else "#F0503A"
    sem_color = "#A78BFA" if sem_pct >= 70 else "#F5A623" if sem_pct >= 45 else "#F0503A"

    bert_badge_html = ""
    if bert_active:
        bert_badge_html = (
            f'<div style="margin-top:8px;display:inline-flex;align-items:center;gap:5px;'
            f'background:rgba(74,158,245,.1);color:#4A9EF5;'
            f'border:1px solid rgba(74,158,245,.25);border-radius:4px;'
            f'font-size:10px;font-weight:700;padding:2px 8px;letter-spacing:.03em;">'
            f'{svg_icon("cpu", 10, "#4A9EF5")} Fine-tuned BERT · MAE {bert_mae}</div>'
        )

    band_html = ""
    if band:
        band_styles = {
            "high":   ("#2ECC8A","rgba(46,204,138,.08)","rgba(46,204,138,.2)"),
            "medium": ("#F5A623","rgba(245,166,35,.08)","rgba(245,166,35,.2)"),
            "low":    ("#F0503A","rgba(240,80,58,.08)", "rgba(240,80,58,.2)"),
        }
        bc, bg, br = band_styles.get(band, ("#8C92A0","rgba(255,255,255,.04)","rgba(255,255,255,.1)"))
        desc = {"high":"Strong overall fit with the job description.",
                "medium":"Partial fit — address the missing keywords below.",
                "low":"Resume needs significant tailoring for this role."}.get(band,"")
        band_html = (
            f'<div style="margin-bottom:16px;background:{bg};border:1px solid {br};border-radius:8px;'
            f'padding:10px 14px;font-size:13px;color:{bc};display:flex;align-items:center;gap:8px;">'
            f'<span style="font-weight:700;text-transform:uppercase;letter-spacing:.5px;">{band.upper()}</span>'
            f'<span style="opacity:.85;">— {desc}</span></div>'
        )

    score_cards = f"""
    <div style="display:flex;gap:12px;margin-bottom:16px;">
        <div style="flex:1;background:#181B22;border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:18px 16px;text-align:center;">
            <div style="font-family:'Fraunces',serif;font-size:36px;font-weight:700;color:{kw_color};letter-spacing:-0.03em;">{kw_pct:.0f}%</div>
            <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;color:#555C6B;margin-top:6px;">Keyword Match</div>
        </div>
        <div style="flex:1;background:#181B22;border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:18px 16px;text-align:center;">
            <div style="font-family:'Fraunces',serif;font-size:36px;font-weight:700;color:{sem_color};letter-spacing:-0.03em;">{sem_pct:.0f}%</div>
            <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;color:#555C6B;margin-top:6px;">Semantic Similarity</div>
            {bert_badge_html}
        </div>
    </div>
    """

    def _pills(keywords: list[str], variant: str) -> str:
        styles = {
            "success": ("rgba(46,204,138,.08)","#2ECC8A","rgba(46,204,138,.2)"),
            "danger":  ("rgba(240,80,58,.08)", "#F0503A","rgba(240,80,58,.2)"),
            "warning": ("rgba(245,166,35,.08)","#F5A623","rgba(245,166,35,.2)"),
        }
        bg, color, border = styles.get(variant, styles["success"])
        return "".join(
            f'<span style="display:inline-block;background:{bg};color:{color};'
            f'border:1px solid {border};border-radius:9999px;padding:3px 11px;'
            f'font-size:12px;font-weight:600;margin:2px 3px;">{k}</span>'
            for k in keywords
        )

    matched_html = ""
    if matched:
        matched_html = (
            f'<div style="margin-bottom:14px;">'
            f'<div style="font-size:11px;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:1px;color:#555C6B;margin-bottom:8px;">Matched ({len(matched)})</div>'
            f'<div style="display:flex;flex-wrap:wrap;">{_pills(matched, "success")}</div></div>'
        )

    missing_html = ""
    if missing:
        missing_html = (
            f'<div style="margin-bottom:14px;">'
            f'<div style="font-size:11px;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:1px;color:#555C6B;margin-bottom:8px;">Missing ({len(missing)})</div>'
            f'<div style="display:flex;flex-wrap:wrap;">{_pills(missing, "danger")}</div></div>'
        )

    gap_html = ""
    if gap:
        gap_items = "".join(
            f'<div style="padding:8px 12px;border-left:3px solid #F5A623;background:rgba(245,166,35,.05);'
            f'border-radius:0 6px 6px 0;margin-bottom:6px;font-size:13px;color:#F5A623;">'
            f'Consider adding: <strong>{s}</strong></div>'
            for s in gap[:12] if s and len(s) > 1
        )
        gap_html = (
            f'<div style="padding-top:12px;border-top:1px solid rgba(255,255,255,.07);margin-top:4px;">'
            f'<div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;'
            f'color:#555C6B;margin-bottom:10px;">Skills Gap ({len(gap)})</div>'
            f'{gap_items}</div>'
        )

    st.markdown(
        card(
            section_header("target", "Job Description Match", "Fine-tuned BERT semantic analysis")
            + band_html
            + score_cards
            + matched_html
            + missing_html
            + gap_html
        ),
        unsafe_allow_html=True,
    )