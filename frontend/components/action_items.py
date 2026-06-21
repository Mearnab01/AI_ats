"""action_items.py — Action items sorted by urgency."""

from __future__ import annotations
from typing import Any, Dict, List, Tuple

import streamlit as st
from frontend.components._helpers import card, section_header, svg_icon

_RANK = {"critical": 0, "high": 1, "medium": 2, "moderate": 3, "low": 4}

_SEV_STYLE = {
    "critical": ("#F0503A", "rgba(240,80,58,.08)",  "rgba(240,80,58,.2)"),
    "high":     ("#F0503A", "rgba(240,80,58,.06)",  "rgba(240,80,58,.15)"),
    "medium":   ("#F5A623", "rgba(245,166,35,.06)", "rgba(245,166,35,.15)"),
    "moderate": ("#F5A623", "rgba(245,166,35,.06)", "rgba(245,166,35,.15)"),
    "low":      ("#4A9EF5", "rgba(74,158,245,.06)", "rgba(74,158,245,.15)"),
}


def _collect(analysis: Dict[str, Any]) -> List[Tuple[str, str, str]]:
    items: List[Tuple[str, str, str]] = []
    for issue in analysis.get("detailed_feedback") or []:
        level = (issue.get("severity_level") or "low").lower()
        title = issue.get("issue_title", "")
        for action in issue.get("action_items") or []:
            items.append((level, title, action))
    if not items:
        for suggestion in analysis.get("suggestions") or []:
            items.append(("medium", "General", suggestion))
    items.sort(key=lambda r: _RANK.get(r[0], 99))
    return items


def display_action_items(analysis: Dict[str, Any]) -> None:
    items = _collect(analysis)
    if not items:
        return

    rows_html = ""
    for level, source, action in items:
        color, bg, border = _SEV_STYLE.get(level, ("#8C92A0","rgba(255,255,255,.04)","rgba(255,255,255,.1)"))
        dot = f'<span style="width:7px;height:7px;border-radius:50%;background:{color};box-shadow:0 0 5px {color};flex-shrink:0;margin-top:5px;display:inline-block;"></span>'
        rows_html += (
            f'<div style="display:flex;align-items:flex-start;gap:10px;padding:9px 0;'
            f'border-bottom:1px solid rgba(255,255,255,.05);">'
            f'{dot}'
            f'<div style="flex:1;">'
            f'<span style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;'
            f'color:{color};margin-right:6px;">[{source}]</span>'
            f'<span style="font-size:13px;color:#8C92A0;line-height:1.5;">{action}</span>'
            f'</div></div>'
        )

    st.markdown(
        card(
            section_header("arrow", "Action Items", f"{len(items)} steps — sorted by urgency")
            + f'<div style="margin-top:-4px;">{rows_html}</div>'
        ),
        unsafe_allow_html=True,
    )