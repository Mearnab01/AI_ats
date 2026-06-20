"""detailed_feedback.py — Full issue list grouped by severity."""

from __future__ import annotations
from typing import Any, Dict, List

import streamlit as st
from frontend.components.helpers import card, section_header, severity_badge, svg_icon


_ORDER = ["critical", "high", "medium", "moderate", "low"]


def _group(issues: List[Dict]) -> Dict[str, List[Dict]]:
    grouped: Dict[str, List[Dict]] = {k: [] for k in _ORDER}
    for item in issues:
        lvl = (item.get("severity_level") or "low").lower()
        grouped.setdefault(lvl, []).append(item)
    return grouped


def _header_style(level: str) -> tuple[str, str]:
    return {
        "critical": ("rgba(240,80,58,.06)",  "rgba(240,80,58,.14)"),
        "high":     ("rgba(240,80,58,.05)",  "rgba(240,80,58,.12)"),
        "medium":   ("rgba(245,166,35,.05)", "rgba(245,166,35,.12)"),
        "moderate": ("rgba(245,166,35,.05)", "rgba(245,166,35,.12)"),
        "low":      ("rgba(74,158,245,.05)", "rgba(74,158,245,.12)"),
    }.get(level, ("rgba(255,255,255,.03)", "rgba(255,255,255,.08)"))


def display_detailed_feedback(analysis: Dict[str, Any]) -> None:
    issues: List[Dict] = analysis.get("detailed_feedback") or []
    if not issues:
        return

    grouped = _group(issues)

    for level in _ORDER:
        items = grouped.get(level, [])
        if not items:
            continue

        bg, border = _header_style(level)
        level_label = level.title()

        with st.expander(f"{level_label}  ({len(items)} issue{'s' if len(items) != 1 else ''})", expanded=(level in ("critical","high"))):
            for issue in items:
                title   = issue.get("issue_title",      "Untitled")
                impact  = issue.get("ats_impact",       "")
                expl    = issue.get("explanation",      "")
                where   = issue.get("where_it_appears", "")
                fix     = issue.get("how_to_fix",       "")
                actions = issue.get("action_items")  or []
                example = issue.get("example_improvement", "")

                action_html = ""
                if actions:
                    lis = "".join(
                        f'<li style="padding:5px 0 5px 20px;font-size:12px;color:#8C92A0;'
                        f'border-bottom:1px solid rgba(255,255,255,.05);position:relative;">'
                        f'<span style="position:absolute;left:0;color:#555C6B;">→</span>{a}</li>'
                        for a in actions
                    )
                    action_html = f'<ul style="list-style:none;margin:8px 0 0;padding:0;">{lis}</ul>'

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

                detail_rows = "".join(
                    f'<div style="display:flex;gap:12px;margin-bottom:7px;">'
                    f'<span style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;'
                    f'color:#555C6B;width:70px;flex-shrink:0;padding-top:2px;">{lbl}</span>'
                    f'<span style="font-size:13px;color:#8C92A0;flex:1;line-height:1.5;">{val}</span></div>'
                    for lbl, val in [("Impact", impact), ("Location", where)]
                    if val
                )

                st.markdown(
                    f"""
                    <div style="background:{bg};border:1px solid {border};border-radius:10px;
                                overflow:hidden;margin-bottom:12px;">
                        <div style="display:flex;align-items:center;gap:12px;padding:12px 16px;
                                    border-bottom:1px solid {border};">
                            {severity_badge(level)}
                            <span style="font-size:14px;font-weight:600;color:#F0F2F5;">{title}</span>
                        </div>
                        <div style="padding:14px 16px;">
                            {"<p style='font-size:13px;color:#8C92A0;margin:0 0 10px;line-height:1.6;'>"+expl+"</p>" if expl else ""}
                            {detail_rows}
                            {"<div style='background:rgba(46,204,138,.07);border:1px solid rgba(46,204,138,.2);border-radius:8px;padding:10px 14px;font-size:13px;color:#2ECC8A;line-height:1.6;margin-top:8px;'><strong style='display:block;font-size:11px;text-transform:uppercase;letter-spacing:.5px;margin-bottom:3px;'>Fix:</strong>"+fix+"</div>" if fix else ""}
                            {action_html}
                            {example_html}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )