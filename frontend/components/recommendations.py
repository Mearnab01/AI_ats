from __future__ import annotations
from typing import Any, Dict, List

import streamlit as st
from frontend.components._helpers import card, section_header, svg_icon


def display_recommendations(analysis: Dict[str, Any]) -> None:
    suggestions: List[str] = analysis.get("suggestions") or []
    if not suggestions:
        return
    print(f"Displaying {len(suggestions)} suggestions")
    
    items_html = ""
    for s in suggestions:
        arrow = svg_icon("arrow", 13, "#4A9EF5")
        items_html += (
            '<div style="display:flex;align-items:flex-start;gap:10px;'
            'padding:9px 0;border-bottom:1px solid rgba(255,255,255,.05);">'
            + arrow
            + '<span style="font-size:13px;color:#8C92A0;line-height:1.5;">'
            + str(s)
            + "</span></div>"
        )

    st.markdown(
        card(
            section_header("bulb", "Recommendations", str(len(suggestions)) + " suggestion(s)")
            + items_html
        ),
        unsafe_allow_html=True,
    )