from __future__ import annotations
from typing import Any, Dict, List

import streamlit as st
from frontend.components._helpers import card, section_header, severity_badge, svg_icon


def display_strengths(analysis: Dict[str, Any]) -> None:
    strengths: List[str] = analysis.get("strengths") or []
    if not strengths:
        return

    st.markdown(
        '<div style="background:#111318;border:1px solid rgba(255,255,255,.08);'
        'border-radius:16px;padding:20px 24px;position:relative;overflow:hidden;">'
        '<div style="position:absolute;inset:0;background:linear-gradient(145deg,rgba(255,255,255,.025) 0%,transparent 100%);pointer-events:none;"></div>'
        + section_header("star", "Strengths", str(len(strengths)) + " detected"),
        unsafe_allow_html=True,
    )

    for s in strengths:
        check = svg_icon("check", 14, "#2ECC8A")
        st.markdown(
            '<div style="display:flex;align-items:flex-start;gap:10px;padding:8px 12px;'
            'background:rgba(46,204,138,.05);border-left:3px solid #2ECC8A;'
            'border-radius:0 8px 8px 0;margin-bottom:7px;font-size:13px;color:#2ECC8A;line-height:1.5;">'
            '<span style="flex-shrink:0;margin-top:1px;">' + check + '</span>'
            '<span>' + s + '</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)


def display_critical_issues(analysis: Dict[str, Any]) -> None:
    feedback: List[Dict] = analysis.get("detailed_feedback") or []
    high = [
        f for f in feedback
        if (f.get("severity_level") or "low").lower() in ("critical", "high")
    ]

    count = len(high)
    hdr = section_header("alert", "Critical Issues", str(count) + " high-priority item(s)")

    if not high:
        check = svg_icon("check", 15, "#2ECC8A")
        body = (
            '<div style="background:rgba(46,204,138,.06);border:1px solid rgba(46,204,138,.2);'
            'border-radius:8px;padding:14px 18px;font-size:13px;color:#2ECC8A;">'
            + check + ' No critical issues found. '
            'Review medium-priority items in the Recommendations section.</div>'
        )
        st.markdown(card(hdr + body), unsafe_allow_html=True)
        return

    st.markdown(
        '<div style="background:#111318;border:1px solid rgba(255,255,255,.08);'
        'border-radius:16px;padding:20px 24px;position:relative;overflow:hidden;">'
        '<div style="position:absolute;inset:0;background:linear-gradient(145deg,rgba(255,255,255,.025) 0%,transparent 100%);pointer-events:none;"></div>'
        + hdr,
        unsafe_allow_html=True,
    )

    for issue in high:
        title   = issue.get("issue_title",   "Untitled")
        impact  = issue.get("ats_impact",    "")
        expl    = issue.get("explanation",   "")
        fix     = issue.get("how_to_fix",    "")

        expl_html = ""
        if expl:
            expl_html = (
                '<p style="font-size:13px;color:#8C92A0;margin:0 0 10px;line-height:1.6;">'
                + expl + '</p>'
            )

        impact_html = ""
        if impact:
            impact_html = (
                '<div style="display:flex;gap:12px;margin-bottom:8px;">'
                '<span style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;'
                'color:#555C6B;width:72px;flex-shrink:0;padding-top:1px;">Impact</span>'
                '<span style="font-size:13px;color:#8C92A0;">' + impact + '</span></div>'
            )

        fix_html = ""
        if fix:
            fix_html = (
                '<div style="background:rgba(46,204,138,.07);border:1px solid rgba(46,204,138,.2);'
                'border-radius:8px;padding:10px 14px;font-size:13px;color:#2ECC8A;line-height:1.6;margin-top:8px;">'
                '<strong style="display:block;font-size:11px;text-transform:uppercase;letter-spacing:.5px;margin-bottom:3px;">Fix:</strong>'
                + fix + '</div>'
            )

        sbadge = severity_badge("high")
        st.markdown(
            '<div style="background:rgba(240,80,58,.04);border:1px solid rgba(240,80,58,.15);'
            'border-radius:10px;overflow:hidden;margin-bottom:12px;">'
            '<div style="display:flex;align-items:center;gap:12px;padding:12px 16px;'
            'background:rgba(240,80,58,.06);border-bottom:1px solid rgba(240,80,58,.12);">'
            + sbadge +
            '<span style="font-size:14px;font-weight:600;color:#F0F2F5;">' + title + '</span></div>'
            '<div style="padding:12px 16px;">'
            + expl_html + impact_html + fix_html +
            '</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)