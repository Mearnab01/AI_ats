"""skill_validation.py — Skill validation analysis panel."""

from __future__ import annotations
from typing import Any, Dict

import streamlit as st
from frontend.components.helpers import card, section_header, progress_bar, badge, pill


def display_skill_validation(analysis: Dict[str, Any]) -> None:
    svd        = analysis.get("skill_validation_details") or {}
    validated  = svd.get("validated",       [])
    unvalidated= svd.get("unvalidated",     [])
    total      = svd.get("total",           len(validated) + len(unvalidated))
    val_count  = svd.get("validated_count", len(validated))
    val_pct    = svd.get("validation_pct",  (val_count / total * 100) if total else 0)

    bar_pct   = (val_count / total * 100) if total else 0
    bar_clr   = "success" if bar_pct >= 80 else "warning" if bar_pct >= 50 else "danger"

    # Stats
    stats = f"""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:16px;">
        <div style="background:#181B22;border:1px solid rgba(255,255,255,.07);border-radius:10px;padding:14px 12px;text-align:center;">
            <div style="font-family:'Fraunces',serif;font-size:26px;font-weight:700;color:#F0F2F5;">{total}</div>
            <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#555C6B;margin-top:4px;">Total</div>
        </div>
        <div style="background:#181B22;border:1px solid rgba(46,204,138,.15);border-radius:10px;padding:14px 12px;text-align:center;">
            <div style="font-family:'Fraunces',serif;font-size:26px;font-weight:700;color:#2ECC8A;">{val_count}</div>
            <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#555C6B;margin-top:4px;">Validated ({val_pct:.0f}%)</div>
        </div>
        <div style="background:#181B22;border:1px solid rgba(240,80,58,.15);border-radius:10px;padding:14px 12px;text-align:center;">
            <div style="font-family:'Fraunces',serif;font-size:26px;font-weight:700;color:#F0503A;">{len(unvalidated)}</div>
            <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#555C6B;margin-top:4px;">Need Evidence</div>
        </div>
    </div>
    <div style="margin-bottom:16px;">{progress_bar(bar_pct, bar_clr)}</div>
    """

    # Validated list
    validated_html = ""
    for item in (validated or []):
        skill    = item.get("skill", "") if isinstance(item, dict) else str(item)
        projects = item.get("projects", []) if isinstance(item, dict) else []
        chips    = "".join(
            f'<span style="display:inline-block;background:rgba(46,204,138,.07);color:#2ECC8A;'
            f'border:1px solid rgba(46,204,138,.2);border-radius:9999px;padding:1px 9px;'
            f'font-size:11px;font-weight:600;margin:2px 3px 0 0;">'
            f'{p[:55]}{"…" if len(p) > 55 else ""}</span>'
            for p in projects
        )
        validated_html += f"""
        <div style="padding:9px 12px;background:rgba(46,204,138,.05);
                    border-left:3px solid #2ECC8A;border-radius:0 8px 8px 0;margin-bottom:7px;">
            <div style="font-size:14px;font-weight:700;color:#2ECC8A;">{skill}</div>
            {"<div style='margin-top:5px;'>"+chips+"</div>" if chips else ""}
        </div>
        """

    # Unvalidated
    unvalidated_html = ""
    if unvalidated:
        pills = "".join(
            f'<span style="display:inline-block;background:rgba(240,80,58,.07);color:#F0503A;'
            f'border:1px solid rgba(240,80,58,.2);border-radius:9999px;padding:3px 11px;'
            f'font-size:12px;font-weight:600;margin:2px 3px;">{s}</span>'
            for s in unvalidated
        )
        unvalidated_html = f"""
        <div style="margin-top:16px;padding-top:16px;border-top:1px solid rgba(255,255,255,.07);">
            <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;
                        color:#555C6B;margin-bottom:10px;">Need Evidence</div>
            <div style="display:flex;flex-wrap:wrap;">{pills}</div>
            <div style="margin-top:12px;background:rgba(245,166,35,.06);border:1px solid rgba(245,166,35,.15);
                        border-radius:8px;padding:10px 14px;font-size:13px;color:#F5A623;line-height:1.6;">
                <strong>How to fix:</strong> Add a project or experience bullet that names each skill above
                in context. Example: <em style="opacity:.85;">"Built a CI/CD pipeline using Kubernetes and Terraform,
                reducing deployment time by 35%."</em>
            </div>
        </div>
        """

    st.markdown(
        card(
            section_header("shield", "Skill Validation", "Skills backed by project evidence")
            + stats
            + (validated_html or '<p style="color:#555C6B;font-size:13px;">No validated skills found.</p>')
            + unvalidated_html
        ),
        unsafe_allow_html=True,
    )