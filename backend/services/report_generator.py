
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape

from backend.services.bert_matcher import get_model_info
from backend.core.logger import setup_logger

logger = setup_logger("ats_resume_scorer | report_generator")


_TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_STATIC_DIR = _PROJECT_ROOT / "frontend" / "static"

_env = Environment(
    loader        = FileSystemLoader(str(_TEMPLATES_DIR)),
    autoescape    = select_autoescape(["html", "xml"]),
    trim_blocks   = True,
    lstrip_blocks = True,
)


# ── Custom filters ─────────────────────────────────────────────────────────────

def _format_date(value) -> str:
    if isinstance(value, (int, float)):
        value = datetime.fromtimestamp(value)
    if isinstance(value, datetime):
        return value.strftime("%B %d, %Y")
    return str(value)


_env.filters["format_date"] = _format_date



def _url_for(endpoint: str, path: str = "") -> str:
    if endpoint == "static":
        resolved = (_STATIC_DIR / path.lstrip("/")).resolve()
        return resolved.as_uri() 
    return path


def _make_globals() -> dict:
    return {"url_for": _url_for}


# ── Score helpers ──────────────────────────────────────────────────────────────

def _score_color(score: float) -> str:
    if score >= 80: return "#1C7C4A"
    if score >= 60: return "#B86C0C"
    return "#C0281E"


def _component_pct(component_scores: Any) -> dict:
    maxes = {
        "formatting":        20.0,
        "keywords":          25.0,
        "content":           25.0,
        "skill_validation":  15.0,
        "ats_compatibility": 15.0,
    }
    result = {}
    for key, max_val in maxes.items():
        raw = getattr(component_scores, key, None)
        if raw is None and isinstance(component_scores, dict):
            raw = component_scores.get(key, 0)
        result[key] = round((float(raw or 0) / max_val) * 100, 1)
    return result


def _split_feedback(all_feedback: list) -> tuple[list, list, list]:
    high, medium, low = [], [], []
    for item in (all_feedback or []):
        sev = (getattr(item, "severity", None) or item.get("severity", "low") if isinstance(item, dict) else "low").lower()
        if sev in ("high", "critical"):
            high.append(item)
        elif sev in ("medium", "moderate"):
            medium.append(item)
        else:
            low.append(item)
    return high, medium, low


# ── Public API ─────────────────────────────────────────────────────────────────

def generate_html_reports(data: Dict) -> Dict[str, str]:
    overall_score    = float(data.get("ATS_score") or data.get("ats_score") or 0)
    component_scores = data.get("component_scores") or {}
    all_feedback     = data.get("detailed_feedback") or []
    high_p, med_p, low_p = _split_feedback(all_feedback)

    # Skill validation details
    svd             = data.get("skill_validation_details") or {}
    validated_s     = svd.get("validated",       [])
    unvalidated_s   = svd.get("unvalidated",      [])
    validated_count = svd.get("validated_count",  0)
    total_skills    = svd.get("total",            0)
    validation_pct  = svd.get("validation_pct",   0.0)

    # JD comparison
    jd_raw = data.get("jd_comparison") or data.get("jd_match_analysis")
    if hasattr(jd_raw, "model_dump"):
        jd_raw = jd_raw.model_dump()

    timestamp       = data.get("timestamp", datetime.now().timestamp())
    comp_pct        = _component_pct(component_scores)
    bert_info       = data.get("bert_model_info") or get_model_info()

    shared = {
        "timestamp":         timestamp,
        "overall_score":     overall_score,
        "score_color":       _score_color(overall_score),
        "interpretation":    data.get("interpretation", ""),
        "component_scores":  component_scores,
        "component_pct":     comp_pct,
        "strengths":         data.get("strengths", []),
        "high_priority":     high_p,
        "medium_priority":   med_p,
        "low_priority":      low_p,
        "all_feedback":      all_feedback,
        "validated_skills":  validated_s,
        "unvalidated_skills":unvalidated_s,
        "validated_count":   validated_count,
        "total_skills":      total_skills,
        "validation_pct":    validation_pct,
        "jd_analysis":       jd_raw,
        "bert_model_info":   bert_info,
        "grammar_summary":   data.get("grammar_summary", {}),
        "location_privacy":  data.get("location_privacy", {}),
        **_make_globals(),
    }

    results = {}
    for template_name, report_key in [
        ("summary.html",       "summary"),
        ("action_items.html",  "action_items"),
        ("quick_actions.html", "quick_actions"),
        ("jd_comparison.html", "jd_comparison"),
    ]:
        try:
            tmpl           = _env.get_template(template_name)
            results[report_key] = tmpl.render(**shared)
        except Exception as exc:
            logger.error("Template render failed (%s): %s", template_name, exc)
            results[report_key] = f"<p>Report generation failed: {exc}</p>"

    return results