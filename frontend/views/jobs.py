"""
jobs.py — AI Job Discovery page
================================
Route: current_view == "jobs"

Flow:
  1. Load cached resume data from Supabase (skills + embedding from last ATS run)
  2. User can refine query / location
  3. Fetch + rank jobs via /api/v1/jobs (Apify → cosine match)
  4. Show career dashboard + ranked job cards with skill gap
"""

from __future__ import annotations
import requests
import streamlit as st

from frontend.services import api_client
from frontend.components._helpers import svg_icon, card, section_header, alert


# ── Pill renderers ─────────────────────────────────────────────────────────────

def _green_pill(text: str) -> str:
    return (
        f'<span style="display:inline-block;background:rgba(46,204,138,.1);'
        f'color:#2ECC8A;border:1px solid rgba(46,204,138,.25);border-radius:9999px;'
        f'padding:2px 10px;font-size:11px;font-weight:600;margin:2px 3px;">'
        f'✓ {text}</span>'
    )


def _red_pill(text: str) -> str:
    return (
        f'<span style="display:inline-block;background:rgba(240,80,58,.07);'
        f'color:#F0503A;border:1px solid rgba(240,80,58,.2);border-radius:9999px;'
        f'padding:2px 10px;font-size:11px;font-weight:600;margin:2px 3px;">'
        f'✗ {text}</span>'
    )


def _match_color(score: float) -> str:
    if score >= 75:
        return "#2ECC8A"
    if score >= 55:
        return "#E8A44A"
    return "#F0503A"


# ── Dashboard summary strip ────────────────────────────────────────────────────

def _render_dashboard(jobs: list, query: str) -> None:
    if not jobs:
        return

    total      = len(jobs)
    avg_match  = round(sum(j.get("match_score", 0) for j in jobs) / total, 1) if total else 0
    best_job   = jobs[0] if jobs else {}
    best_score = best_job.get("match_score", 0)
    best_title = best_job.get("title", "—")

    st.markdown(
        f"""
        <div style="background:#181B22;border:1px solid rgba(255,255,255,.07);
        border-radius:12px;padding:20px 24px;margin-bottom:24px;">
            <div style="font-size:11px;font-weight:700;text-transform:uppercase;
            letter-spacing:1.2px;color:#555C6B;margin-bottom:14px;">
                Career Match Dashboard
            </div>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;">
                <div>
                    <div style="font-size:28px;font-weight:700;color:#F0F2F5;
                    font-family:'Fraunces',serif;">{total}</div>
                    <div style="font-size:12px;color:#555C6B;margin-top:2px;">
                        Recommended Jobs
                    </div>
                </div>
                <div>
                    <div style="font-size:28px;font-weight:700;color:#E8A44A;
                    font-family:'Fraunces',serif;">{avg_match}%</div>
                    <div style="font-size:12px;color:#555C6B;margin-top:2px;">
                        Average Match
                    </div>
                </div>
                <div>
                    <div style="font-size:14px;font-weight:600;color:#2ECC8A;
                    margin-top:4px;">{best_title}</div>
                    <div style="font-size:12px;color:#555C6B;margin-top:2px;">
                        Best Match · {best_score}%
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Single job card ────────────────────────────────────────────────────────────

def _render_job_card(job: dict, idx: int) -> None:
    score     = job.get("match_score", 0)
    title     = job.get("title", "Unknown Role")
    company   = job.get("company", "")
    location  = job.get("location", "")
    source    = job.get("source", "")
    exp       = job.get("experience", "")
    apply_url = job.get("apply_url", "#")
    matched   = job.get("skills_matched", [])
    missing   = job.get("skills_missing", [])
    color     = _match_color(score)

    matched_pills = "".join(_green_pill(s) for s in matched[:6])
    missing_pills = "".join(_red_pill(s) for s in missing[:6])
    skill_section = ""
    if matched or missing:
        skill_section = (
            f'<div style="margin-top:12px;padding-top:12px;'
            f'border-top:1px solid rgba(255,255,255,.06);">'
        )
        if matched:
            skill_section += (
                f'<div style="font-size:10px;font-weight:700;text-transform:uppercase;'
                f'letter-spacing:1px;color:#555C6B;margin-bottom:6px;">Why Matched</div>'
                f'<div style="display:flex;flex-wrap:wrap;">{matched_pills}</div>'
            )
        if missing:
            skill_section += (
                f'<div style="font-size:10px;font-weight:700;text-transform:uppercase;'
                f'letter-spacing:1px;color:#555C6B;margin:8px 0 6px;">Missing</div>'
                f'<div style="display:flex;flex-wrap:wrap;">{missing_pills}</div>'
            )
        skill_section += "</div>"

    exp_badge = (
        f'<span style="font-size:11px;color:#8C92A0;background:rgba(255,255,255,.04);'
        f'border:1px solid rgba(255,255,255,.07);border-radius:6px;padding:2px 8px;">'
        f'{exp}</span>'
        if exp else ""
    )
    source_badge = (
        f'<span style="font-size:10px;color:#555C6B;margin-left:6px;">{source}</span>'
        if source else ""
    )

    st.markdown(
        f"""
        <div style="background:#181B22;border:1px solid rgba(255,255,255,.07);
        border-radius:12px;padding:18px 20px;margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div style="flex:1;min-width:0;">
                    <div style="font-size:15px;font-weight:600;color:#F0F2F5;
                    margin-bottom:2px;">{title}</div>
                    <div style="font-size:13px;color:#8C92A0;">
                        {company}
                        {source_badge}
                    </div>
                    <div style="font-size:12px;color:#555C6B;margin-top:4px;">
                        {location} {exp_badge}
                    </div>
                </div>
                <div style="text-align:right;flex-shrink:0;margin-left:16px;">
                    <div style="font-size:22px;font-weight:700;color:{color};
                    font-family:'Fraunces',serif;">{score}%</div>
                    <div style="font-size:10px;color:#555C6B;">Match</div>
                </div>
            </div>
            {skill_section}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Apply button as native Streamlit link (avoids HTML injection issues)
    if apply_url and apply_url != "#":
        st.link_button("Apply →", apply_url, use_container_width=False)


# ── Main render ────────────────────────────────────────────────────────────────

def render() -> None:
    st.markdown(
        '<h1 style="font-family:\'Fraunces\',serif;font-size:26px;color:#F0F2F5;'
        'margin:0 0 6px;letter-spacing:-0.02em;">AI Job Discovery</h1>'
        '<p style="color:#8C92A0;font-size:14px;margin:0 0 24px;">Jobs matched to your '
        'resume using semantic similarity — no re-analysis required.</p>',
        unsafe_allow_html=True,
    )

    # Auth check
    if not st.session_state.get("user_id"):
        st.markdown(
            alert("Sign in to see personalised job matches.", "warning"),
            unsafe_allow_html=True,
        )
        return

    from frontend.services.auth_utils import ensure_valid_session
    access_token = ensure_valid_session()
    if not access_token:
        st.markdown(
            alert("Session expired. Please sign in again.", "warning"),
            unsafe_allow_html=True,
        )
        return

    # ── Search controls ────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        query = st.text_input(
            "Role / Skills",
            placeholder="e.g. AI Engineer, Python Developer…",
            label_visibility="collapsed",
        )
    with col2:
        location = st.text_input(
            "Location",
            value="India",
            label_visibility="collapsed",
        )
    with col3:
        search = st.button("Find Jobs", type="secondary", use_container_width=True)

    # Load on first visit or on explicit search
    trigger = search or ("jobs_data" not in st.session_state)

    if trigger:
        with st.spinner("Finding best matches for your resume... This takes less than a minute..."):
            try:
                data = api_client.get_jobs(
                    query        = query or "",
                    location     = location or "India",
                    access_token = access_token,
                )
                st.session_state["jobs_data"]   = data.get("jobs", [])
                st.session_state["jobs_query"]  = data.get("query", "")
                st.session_state["jobs_cached"] = data.get("cached_from", "")
            except requests.HTTPError as exc:
                if exc.response is not None and exc.response.status_code == 404:
                    st.markdown(
                        alert(
                            "No resume analysis found. Go to **Analyse** and run an ATS score first "
                            "— your skills and resume will be cached automatically.",
                            "warning",
                        ),
                        unsafe_allow_html=True,
                    )
                    return
                st.markdown(
                    alert(f"Could not fetch jobs: {exc}", "danger"),
                    unsafe_allow_html=True,
                )
                return
            except requests.ConnectionError:
                st.markdown(
                    alert("Cannot reach backend. Is it running on port 8000?", "danger"),
                    unsafe_allow_html=True,
                )
                return

    jobs       = st.session_state.get("jobs_data", [])
    used_query = st.session_state.get("jobs_query", "")
    cached_fn  = st.session_state.get("jobs_cached", "")

    if not jobs:
        st.markdown(
            alert("No jobs found for this query. Try a different role or location.", "warning"),
            unsafe_allow_html=True,
        )
        return

    # Cache source note
    if cached_fn:
        st.markdown(
            f'<div style="font-size:12px;color:#555C6B;margin-bottom:16px;">'
            f'Matched against: <span style="color:#E8A44A;">{cached_fn}</span> '
            f'· Query: <span style="color:#8C92A0;">{used_query}</span></div>',
            unsafe_allow_html=True,
        )

    # Dashboard summary
    _render_dashboard(jobs, used_query)

    # Job cards header
    st.markdown(
        '<div style="font-size:13px;font-weight:600;color:#8C92A0;'
        'text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">'
        'Top Job Matches</div>',
        unsafe_allow_html=True,
    )

    for idx, job in enumerate(jobs):
        _render_job_card(job, idx)