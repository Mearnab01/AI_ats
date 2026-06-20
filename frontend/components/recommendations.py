"""components/recommendations.py — Recommendations grouped by severity."""

from __future__ import annotations
from typing import Any, Dict, List

import streamlit as st
from frontend.components.helpers import card, section_header, severity_badge, svg_icon


_ORDER   = ["critical", "high", "medium", "moderate", "low"]
_LABELS  = {"critical":"Critical","high":"High Priority","medium":"Medium Priority","moderate":"Medium Priority","low":"Low Priority — Polish"}
_HEADER_BG = {
    "critical": ("rgba(240,80,58,.06)",  "rgba(240,80,58,.14)"),
    "high":     ("rgba(240,80,58,.05)",  "rgba(240,80,58,.12)"),
    "medium":   ("rgba(245,166,35,.05)", "rgba(245,166,35,.12)"),
    "moderate": ("rgba(245,166,35,.05)", "rgba(245,166,35,.12)"),
    "low":      ("rgba(74,158,245,.05)", "rgba(74,158,245,.12)"),
}


def _group(issues: List[Dict]) -> Dict[str, List[Dict]]:
    grouped: Dict[str, List[Dict]] = {k: [] for k in _ORDER}
    for item in issues:
        lvl = (item.get("severity_level") or "low").lower()
        grouped.setdefault(lvl, []).append(item)
    return grouped


def _render_issue(issue: Dict, level: str) -> str:
    title   = issue.get("issue_title",      "Untitled")
    impact  = issue.get("ats_impact",       "")
    expl    = issue.get("explanation",      "")
    where   = issue.get("where_it_appears", "")
    fix     = issue.get("how_to_fix",       "")
    actions = issue.get("action_items")  or []
    example = issue.get("example_improvement", "")

    bg, border = _HEADER_BG.get(level, ("rgba(255,255,255,.03)", "rgba(255,255,255,.08)"))

    detail_rows = ""
    for lbl, val in [("Impact", impact), ("Location", where)]:
        if val:
            detail_rows += (
                f'<div style="display:flex;gap:12px;margin-bottom:7px;">'
                f'<span style="font-size:10px;font-weight:700;text-transform:uppercase;'
                f'letter-spacing:.5px;color:#555C6B;width:68px;flex-shrink:0;padding-top:2px;">{lbl}</span>'
                f'<span style="font-size:13px;color:#8C92A0;flex:1;line-height:1.5;">{val}</span></div>'
            )

    fix_html = ""
    if fix:
        fix_html = (
            f'<div style="background:rgba(46,204,138,.07);border:1px solid rgba(46,204,138,.2);'
            f'border-radius:8px;padding:10px 14px;font-size:13px;color:#2ECC8A;'
            f'line-height:1.6;margin-top:8px;">'
            f'<strong style="display:block;font-size:10px;text-transform:uppercase;'
            f'letter-spacing:.5px;margin-bottom:3px;">How to fix</strong>{fix}</div>'
        )

    action_html = ""
    if actions:
        lis = "".join(
            f'<li style="padding:5px 0 5px 20px;font-size:12px;color:#8C92A0;'
            f'border-bottom:1px solid rgba(255,255,255,.04);position:relative;line-height:1.5;">'
            f'<span style="position:absolute;left:0;color:#555C6B;">→</span>{a}</li>'
            for a in actions
        )
        action_html = f'<ul style="list-style:none;margin:10px 0 0;padding:0;">{lis}</ul>'

    example_html = ""
    if example:
        example_html = (
            f'<div style="margin-top:10px;background:#0C0E12;border:1px solid rgba(255,255,255,.07);'
            f'border-radius:8px;padding:10px 14px;">'
            f'<span style="font-size:10px;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:.5px;color:#555C6B;display:block;margin-bottom:4px;">Example</span>'
            f'<pre style="margin:0;font-family:\'DM Mono\',monospace;font-size:12px;'
            f'color:#8C92A0;white-space:pre-wrap;line-height:1.6;">{example}</pre></div>'
        )

    return (
        f'<div style="background:{bg};border:1px solid {border};border-radius:10px;'
        f'overflow:hidden;margin-bottom:12px;">'
        f'<div style="display:flex;align-items:center;gap:12px;padding:12px 16px;'
        f'border-bottom:1px solid {border};">'
        f'{severity_badge(level)}'
        f'<span style="font-size:14px;font-weight:600;color:#F0F2F5;">{title}</span></div>'
        f'<div style="padding:14px 16px;">'
        f'{"<p style=\'font-size:13px;color:#8C92A0;margin:0 0 10px;line-height:1.6;\'>"+expl+"</p>" if expl else ""}'
        f'{detail_rows}{fix_html}{action_html}{example_html}'
        f'</div></div>'
    )


def display_recommendations(analysis: Dict[str, Any]) -> None:
    issues: List[Dict] = analysis.get("detailed_feedback") or []
    if not issues:
        return

    grouped = _group(issues)
    total   = len(issues)

    st.markdown(
        f'<h3 style="font-family:\'Fraunces\',serif;font-size:17px;color:#F0F2F5;'
        f'margin:0 0 6px;">{total} issue(s) found</h3>'
        f'<p style="color:#8C92A0;font-size:13px;margin:0 0 20px;">Sorted by priority. '
        f'Addressing all of them can significantly improve your score.</p>',
        unsafe_allow_html=True,
    )

    for level in _ORDER:
        items = grouped.get(level, [])
        if not items:
            continue

        label = _LABELS.get(level, level.title())
        with st.expander(
            f"{label}  ·  {len(items)} issue{'s' if len(items) != 1 else ''}",
            expanded=(level in ("critical", "high")),
        ):
            for issue in items:
                st.markdown(_render_issue(issue, level), unsafe_allow_html=True)

    # Checklist
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<h3 style="font-family:\'Fraunces\',serif;font-size:16px;color:#F0F2F5;margin:0 0 14px;">'
        'Action Items Checklist</h3>',
        unsafe_allow_html=True,
    )

    for level in _ORDER:
        items = grouped.get(level, [])
        if not items:
            continue
        bg, border = _HEADER_BG.get(level, ("rgba(255,255,255,.03)", "rgba(255,255,255,.08)"))

        label_html = (
            f'<div style="font-size:11px;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:1px;padding:6px 10px;border-radius:4px;'
            f'background:{bg};border:1px solid {border};'
            f'color:#F0F2F5;margin-bottom:8px;">{level.title()}</div>'
        )

        rows_html = ""
        for issue in items:
            for action in (issue.get("action_items") or []):
                rows_html += (
                    f'<div style="display:flex;align-items:flex-start;gap:10px;'
                    f'padding:8px 0;border-bottom:1px dashed rgba(255,255,255,.05);">'
                    f'<div style="width:15px;height:15px;border:2px solid rgba(255,255,255,.14);'
                    f'border-radius:3px;flex-shrink:0;margin-top:2px;"></div>'
                    f'<span style="font-size:13px;color:#8C92A0;line-height:1.5;">{action}</span></div>'
                )

        if rows_html:
            st.markdown(
                f'<div style="background:#111318;border:1px solid rgba(255,255,255,.07);'
                f'border-radius:10px;padding:14px 16px;margin-bottom:12px;">'
                f'{label_html}{rows_html}</div>',
                unsafe_allow_html=True,
            )