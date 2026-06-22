from __future__ import annotations
from typing import Any, Dict

import streamlit as st
from frontend.components.score_display       import display_score_header, display_component_breakdown
from frontend.components.strengths_issues    import display_strengths, display_critical_issues
from frontend.components.skill_validation    import display_skill_validation
from frontend.components.jd_comparison       import display_jd_comparison
from frontend.components.detailed_feedback   import display_detailed_feedback
from frontend.components.action_items        import display_action_items
from frontend.components.recommendations     import display_recommendations

from frontend.components._helpers            import card, section_header, svg_icon

  
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
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    
    # ── Score breakdown + Strengths (two columns) ─────────────────
    col1, col2 = st.columns([1.2, 1])
    with col1:
        display_component_breakdown(analysis)
    with col2:
        display_strengths(analysis)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # ── Skill validation + JD comparison (two columns) ────────────
    col3, col4 = st.columns(2)
    with col3:
        display_skill_validation(analysis)
    with col4:
        display_jd_comparison(analysis)
         
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # ── Critical issues ───────────────────────────────────────────
    display_critical_issues(analysis)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    
    # ── Detailed feedback (expandable by severity) ────────────────
    st.markdown(
        card(section_header("layers", "All Recommendations", "Expandable by severity level")),
        unsafe_allow_html=True,
    )
    display_detailed_feedback(analysis)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    
    # ── Action items checklist ────────────────────────────────────
    display_action_items(analysis)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    
    # ── Recommendations ───────────────────────────────────────────
    display_recommendations(analysis)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    
    # ── Privacy + ATS meta ────────────────────────────────────────
    _display_ats_meta(analysis)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)



# ── ATS meta + privacy ────────────────────────────────────────────────────────

def _display_ats_meta(analysis: Dict[str, Any]) -> None:
    
    grammar   = analysis.get("grammar_summary")  or {}
    privacy   = analysis.get("location_privacy") or {}
    bert      = analysis.get("bert_model_info")  or {}
 
    total_err = int(grammar.get("total_errors", 0))
    penalty   = float(grammar.get("penalty",    0.0))
    priv_risk = (privacy.get("risk") or "none").lower()
    priv_recs = privacy.get("recommendations") or []
 
    err_color = "#2ECC8A" if total_err == 0 else "#F5A623" if total_err <= 3 else "#F0503A"
    err_label = "Clean"   if total_err == 0 else "Minor issues" if total_err <= 3 else "Needs review"
 
    risk_color_map = {"none": "#2ECC8A", "low": "#4A9EF5", "medium": "#F5A623", "high": "#F0503A"}
    risk_color     = risk_color_map.get(priv_risk, "#8C92A0")
 
    risk_icon_map  = {"none": "check", "low": "info", "medium": "alert", "high": "alert"}
    risk_icon      = risk_icon_map.get(priv_risk, "info")
 
    risk_desc_map = {
        "none":   "No personal address or ZIP detected. Good for ATS.",
        "low":    "Minimal location info detected. Generally safe.",
        "medium": "Multiple location entities found. Consider removing specific addresses.",
        "high":   "Full street address or ZIP detected — hurts ATS parse scores and exposes personal data. Remove it.",
    }
    risk_desc = risk_desc_map.get(priv_risk, "")
 
    if bert.get("using_finetuned"):
        bert_label = "Fine-tuned all-mpnet-base-v2 · MAE " + str(bert.get("finetuned_mae", "?"))
    else:
        bert_label = "Base all-mpnet-base-v2 (fine-tuned not found)"
 
    rows_html = (
        '<div style="border:1px solid rgba(255,255,255,.07);border-radius:10px;overflow:hidden;margin-bottom:12px;">'
 
        '<div style="display:flex;justify-content:space-between;align-items:center;'
        'padding:10px 16px;border-bottom:1px solid rgba(255,255,255,.06);font-size:13px;">'
        '<span style="font-weight:600;color:#F0F2F5;">Grammar &amp; Spelling</span>'
        '<span style="color:' + err_color + ';font-weight:700;">'
        + str(total_err) + ' error(s) &nbsp;&middot;&nbsp; ' + err_label + '</span></div>'
 
        '<div style="display:flex;justify-content:space-between;align-items:center;'
        'padding:10px 16px;border-bottom:1px solid rgba(255,255,255,.06);font-size:13px;">'
        '<span style="font-weight:600;color:#F0F2F5;">Score Penalty</span>'
        '<span style="color:#8C92A0;">-' + str(abs(penalty)) + ' pts</span></div>'
 
        '<div style="display:flex;justify-content:space-between;align-items:center;'
        'padding:10px 16px;border-bottom:1px solid rgba(255,255,255,.06);font-size:13px;">'
        '<span style="font-weight:600;color:#F0F2F5;">Address Privacy Risk</span>'
        '<span style="color:' + risk_color + ';font-weight:700;display:flex;align-items:center;gap:5px;">'
        + svg_icon(risk_icon, 13, risk_color) + '&nbsp;' + priv_risk.upper() + '</span></div>'
 
        '<div style="display:flex;justify-content:space-between;align-items:center;'
        'padding:10px 16px;font-size:13px;">'
        '<span style="font-weight:600;color:#F0F2F5;">JD Scorer Model</span>'
        '<span style="color:#4A9EF5;font-size:12px;">' + bert_label + '</span></div>'
 
        '</div>'
    )
 
    privacy_html = ""
    if priv_risk != "none":
        risk_bg_map     = {"low": "rgba(74,158,245,.05)",  "medium": "rgba(245,166,35,.05)",  "high": "rgba(240,80,58,.05)"}
        risk_border_map = {"low": "rgba(74,158,245,.18)",  "medium": "rgba(245,166,35,.18)",  "high": "rgba(240,80,58,.18)"}
        risk_bg     = risk_bg_map.get(priv_risk,     "rgba(255,255,255,.03)")
        risk_border = risk_border_map.get(priv_risk, "rgba(255,255,255,.08)")
 
        privacy_html = (
            '<div style="background:' + risk_bg + ';border:1px solid ' + risk_border + ';'
            'border-radius:8px;padding:12px 16px;margin-bottom:10px;">'
            '<div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;">'
            + svg_icon(risk_icon, 14, risk_color)
            + '<span style="font-size:12px;font-weight:700;text-transform:uppercase;'
            'letter-spacing:.5px;color:' + risk_color + ';">'
            + priv_risk.upper() + ' PRIVACY RISK</span></div>'
            '<p style="margin:0;font-size:13px;color:#8C92A0;line-height:1.6;">' + risk_desc + '</p>'
            '</div>'
        )
 
        if priv_recs:
            items_html = ""
            for r in priv_recs:
                r_clean = str(r).strip().lstrip("-. ")
                if r_clean:
                    items_html += (
                        '<div style="display:flex;align-items:flex-start;gap:8px;'
                        'font-size:12px;color:#F5A623;padding:5px 0;'
                        'border-bottom:1px solid rgba(255,255,255,.04);">'
                        + svg_icon("arrow", 12, "#F5A623")
                        + '<span>' + r_clean + '</span></div>'
                    )
            if items_html:
                privacy_html += (
                    '<div style="background:rgba(245,166,35,.04);border:1px solid rgba(245,166,35,.12);'
                    'border-radius:8px;padding:12px 16px;">'
                    '<div style="font-size:10px;font-weight:700;text-transform:uppercase;'
                    'letter-spacing:1px;color:#555C6B;margin-bottom:8px;">What to do</div>'
                    + items_html + '</div>'
                )
 
    st.markdown(
        card(section_header("shield", "ATS Compatibility Details") + rows_html + privacy_html),
        unsafe_allow_html=True,
    )
 
 
def _handle_pdf_export(analysis: Dict[str, Any]) -> None:
    import os
    import requests
    base = os.getenv("BACKEND_URL", "http://localhost:8000")
    try:
        resp = requests.post(base + "/api/v1/generate-pdf", json=analysis, timeout=30)
        if resp.ok:
            st.download_button(
                label="Download PDF",
                data=resp.content,
                file_name="criterion_report.pdf",
                mime="application/pdf",
            )
        else:
            st.error("PDF export failed: " + str(resp.status_code))
    except Exception as e:
        st.error("PDF export error: " + str(e))
 
 
def _build_txt_summary(analysis: Dict[str, Any]) -> str:
    score = float(analysis.get("ATS_score") or analysis.get("ats_score") or 0)
    cs    = analysis.get("component_scores") or {}
 
    def _v(k):
        return float((cs.get(k) if isinstance(cs, dict) else getattr(cs, k, 0)) or 0)
 
    privacy  = analysis.get("location_privacy") or {}
    grammar  = analysis.get("grammar_summary")  or {}
 
    lines = [
        "CRITERION — Resume Analysis Summary",
        "=" * 40,
        "Overall ATS Score : " + str(int(score)) + "/100",
        "",
        "Component Scores",
        "-" * 20,
        "  Keywords & Skills  : " + str(int(_v("keywords")))         + "/25",
        "  Content Quality    : " + str(int(_v("content")))          + "/25",
        "  Formatting         : " + str(int(_v("formatting")))       + "/20",
        "  Skill Validation   : " + str(int(_v("skill_validation"))) + "/15",
        "  ATS Compatibility  : " + str(int(_v("ats_compatibility")))+ "/15",
        "",
        "Privacy & Grammar",
        "-" * 20,
        "  Address Privacy Risk : " + str(privacy.get("risk", "none")).upper(),
        "  Grammar Errors       : " + str(grammar.get("total_errors", 0)),
        "  Grammar Penalty        : -" + str(grammar.get("penalty", 0)) + " pts",
        "",
        "Strengths",
        "-" * 20,
    ]
    for s in analysis.get("strengths") or []:
        lines.append("  + " + str(s))
 
    lines += ["", "Recommendations", "-" * 20]
    for r in analysis.get("suggestions") or analysis.get("recommendations") or []:
        lines.append("  - " + str(r))
 
    jd = analysis.get("jd_comparison") or analysis.get("jd_match_analysis")
    if jd:
        if hasattr(jd, "model_dump"):
            jd = jd.model_dump()
        lines += [
            "", "JD Match", "-" * 20,
            "  Keyword Match       : " + str(int(float(jd.get("match_percentage", 0)))) + "%",
            "  Semantic Similarity : " + str(int(float(jd.get("semantic_similarity", 0)) * 100)) + "%",
        ]
        missing = jd.get("missing_keywords") or []
        if missing:
            lines.append("  Missing Keywords : " + ", ".join(missing[:10]))
            
    return "\n".join(lines)
 