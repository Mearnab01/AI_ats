from __future__ import annotations
from typing import Any, Dict

import streamlit as st
from frontend.components.score_display       import display_score_header, display_component_breakdown
from frontend.components.strengths_issues    import display_strengths, display_critical_issues
from frontend.components.skill_validation    import display_skill_validation
from frontend.components.jd_comparison       import display_jd_comparison
from frontend.components.detailed_feedback   import display_detailed_feedback
from frontend.components.action_items        import display_action_items
from frontend.components.helpers            import card, section_header, svg_icon


def display_results(analysis: Dict[str, Any]) -> None:
    """Render the full results dashboard."""

    # ── Export row ────────────────────────────────────────────────
    st.markdown(
        '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:24px;">'
        '<h1 style="font-family:\'Fraunces\',serif;font-size:26px;color:#F0F2F5;margin:0;letter-spacing:-0.02em;">Analysis Results</h1>'
        '</div>',
        unsafe_allow_html=True,
    )

    col_dl1, col_dl2, _ = st.columns([1, 1, 4])
    with col_dl1:
        if st.button("PDF Report", use_container_width=True):
            _handle_pdf_export(analysis)
    with col_dl2:
        st.download_button(
            label    = "TXT Summary",
            data     = _build_txt_summary(analysis),
            file_name= "calibr_summary.txt",
            mime     = "text/plain",
            use_container_width=True,
        )

    # ── Score hero ────────────────────────────────────────────────
    display_score_header(analysis)

    # ── Score breakdown + Strengths (two columns) ─────────────────
    col1, col2 = st.columns([1.2, 1])
    with col1:
        display_component_breakdown(analysis)
    with col2:
        display_strengths(analysis)

    # ── Skill validation + JD comparison (two columns) ────────────
    col3, col4 = st.columns(2)
    with col3:
        display_skill_validation(analysis)
    with col4:
        display_jd_comparison(analysis)

    # ── Critical issues ───────────────────────────────────────────
    display_critical_issues(analysis)

    # ── Detailed feedback (expandable by severity) ────────────────
    st.markdown(
        card(section_header("layers", "All Recommendations", "Expandable by severity level")),
        unsafe_allow_html=True,
    )
    display_detailed_feedback(analysis)

    # ── Action items checklist ────────────────────────────────────
    display_action_items(analysis)

    # ── Grammar / privacy summary ─────────────────────────────────
    _display_ats_meta(analysis)


def _display_ats_meta(analysis: Dict[str, Any]) -> None:
    grammar  = analysis.get("grammar_summary")  or {}
    privacy  = analysis.get("location_privacy") or {}
    bert     = analysis.get("bert_model_info")  or {}

    total_err = grammar.get("total_errors",  0)
    penalty   = grammar.get("penalty",       0)
    priv_risk = privacy.get("risk",        "none")
    priv_recs = privacy.get("recommendations", [])

    err_color  = "#2ECC8A" if total_err == 0 else "#F5A623" if total_err <= 3 else "#F0503A"
    err_label  = "Clean"   if total_err == 0 else "Minor"   if total_err <= 3 else "Needs Review"
    risk_color = {"none":"#2ECC8A","low":"#F5A623","medium":"#F5A623","high":"#F0503A"}.get(priv_risk,"#8C92A0")

    rows = f"""
    <div style="border:1px solid rgba(255,255,255,.08);border-radius:10px;overflow:hidden;margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;padding:10px 16px;border-bottom:1px solid rgba(255,255,255,.06);font-size:13px;">
            <span style="font-weight:600;color:#F0F2F5;">Grammar &amp; Spelling</span>
            <span style="color:{err_color};font-weight:700;">{total_err} error(s) &nbsp;·&nbsp; {err_label}</span>
        </div>
        <div style="display:flex;justify-content:space-between;padding:10px 16px;border-bottom:1px solid rgba(255,255,255,.06);font-size:13px;">
            <span style="font-weight:600;color:#F0F2F5;">Penalty Applied</span>
            <span style="color:#8C92A0;">{penalty:.1f} pts</span>
        </div>
        <div style="display:flex;justify-content:space-between;padding:10px 16px;border-bottom:1px solid rgba(255,255,255,.06);font-size:13px;">
            <span style="font-weight:600;color:#F0F2F5;">Privacy Risk</span>
            <span style="color:{risk_color};font-weight:700;">{priv_risk.upper()}</span>
        </div>
        <div style="display:flex;justify-content:space-between;padding:10px 16px;font-size:13px;">
            <span style="font-weight:600;color:#F0F2F5;">JD Scorer</span>
            <span style="color:#4A9EF5;">{"Fine-tuned BERT · MAE "+str(bert.get("finetuned_mae","?")) if bert.get("using_finetuned") else "Base all-mpnet-base-v2"}</span>
        </div>
    </div>
    """

    privacy_html = ""
    if priv_recs:
        items = "".join(
            f'<div style="font-size:12px;color:#F5A623;padding:4px 0;border-bottom:1px solid rgba(255,255,255,.05);">{svg_icon("arrow",12,"#F5A623")} {r}</div>'
            for r in priv_recs
        )
        privacy_html = (
            f'<div style="background:rgba(245,166,35,.05);border:1px solid rgba(245,166,35,.15);'
            f'border-radius:8px;padding:12px 16px;margin-top:8px;">'
            f'<div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;'
            f'color:#555C6B;margin-bottom:8px;">Privacy Recommendations</div>{items}</div>'
        )

    st.markdown(
        card(section_header("shield", "ATS Compatibility Details") + rows + privacy_html),
        unsafe_allow_html=True,
    )


def _handle_pdf_export(analysis: Dict[str, Any]) -> None:
    import requests
    try:
        resp = requests.post(
            "http://localhost:8000/api/v1/generate-pdf",
            json=analysis,
            timeout=30,
        )
        if resp.ok:
            st.download_button(
                label    = "Download PDF",
                data     = resp.content,
                file_name= "calibr_report.pdf",
                mime     = "application/pdf",
            )
        else:
            st.error(f"PDF export failed: {resp.status_code}")
    except Exception as e:
        st.error(f"PDF export error: {e}")


def _build_txt_summary(analysis: Dict[str, Any]) -> str:
    score = float(analysis.get("ATS_score") or analysis.get("ats_score") or 0)
    cs    = analysis.get("component_scores") or {}
    lines = [
        "CALIBR — Resume Analysis Summary",
        "=" * 40,
        f"Overall ATS Score: {score:.0f}/100",
        "",
        "Component Scores",
        "-" * 20,
    ]
    for key, label, mx in [
        ("keywords","Keywords & Skills",25),("content","Content Quality",25),
        ("formatting","Formatting",20),("skill_validation","Skill Validation",15),
        ("ats_compatibility","ATS Compatibility",15),
    ]:
        val = float((cs.get(key) if isinstance(cs, dict) else getattr(cs, key, 0)) or 0)
        lines.append(f"  {label}: {val:.0f}/{mx}")

    lines += ["", "Strengths", "-"*20]
    for s in analysis.get("strengths") or []:
        lines.append(f"  + {s}")

    lines += ["", "Recommendations", "-"*20]
    for r in analysis.get("suggestions") or []:
        lines.append(f"  - {r}")

    return "\n".join(lines)