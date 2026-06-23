from __future__ import annotations
import requests
import streamlit as st

from frontend.services  import api_client
from frontend.components._helpers import svg_icon, alert, card, section_header
from frontend.components.dashboard import display_results


def _show_backend_error(exc: Exception) -> None:
    if isinstance(exc, requests.ConnectionError):
        st.markdown(alert("Cannot reach the backend. Is it running on port 8000?", "danger"), unsafe_allow_html=True)
    elif isinstance(exc, requests.HTTPError) and exc.response is not None:
        st.markdown(alert(f"Backend returned {exc.response.status_code}: {exc.response.text}", "danger"), unsafe_allow_html=True)
    else:
        st.markdown(alert(f"Unexpected error: {exc}", "danger"), unsafe_allow_html=True)

# ── _show_rejection_ui ───────────────────────────────────────────────────────────────
 
def _show_rejection_ui(doc_type: str, confidence: int, reasoning: list) -> None:
    reasons_html = "".join(
        f'<li style="margin:4px 0;color:#8C92A0;font-size:13px;">{r}</li>'
        for r in reasoning
    )
 
    st.markdown(
        f"""
        <div style="background:rgba(240,80,58,.06);border:1px solid rgba(240,80,58,.25);
        border-radius:12px;padding:24px 28px;margin:24px 0;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
                <div style="font-size:28px;">❌</div>
                <div>
                    <div style="font-size:18px;font-weight:700;color:#F0503A;
                    font-family:'Fraunces',serif;">ATS Analysis Stopped</div>
                    <div style="font-size:13px;color:#8C92A0;margin-top:2px;">
                        This file does not appear to be a resume
                    </div>
                </div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;">
                <div style="background:#181B22;border:1px solid rgba(255,255,255,.07);
                border-radius:8px;padding:12px 16px;">
                    <div style="font-size:10px;font-weight:700;text-transform:uppercase;
                    letter-spacing:1px;color:#555C6B;margin-bottom:4px;">Detected File Type</div>
                    <div style="font-size:16px;font-weight:600;color:#F0F2F5;">{doc_type}</div>
                </div>
                <div style="background:#181B22;border:1px solid rgba(255,255,255,.07);
                border-radius:8px;padding:12px 16px;">
                    <div style="font-size:10px;font-weight:700;text-transform:uppercase;
                    letter-spacing:1px;color:#555C6B;margin-bottom:4px;">Confidence</div>
                    <div style="font-size:16px;font-weight:600;color:#F0503A;">{confidence}%</div>
                </div>
            </div>
            <div style="background:#181B22;border:1px solid rgba(255,255,255,.07);
            border-radius:8px;padding:14px 16px;margin-bottom:16px;">
                <div style="font-size:10px;font-weight:700;text-transform:uppercase;
                letter-spacing:1px;color:#555C6B;margin-bottom:8px;">Reason</div>
                <ul style="margin:0;padding-left:16px;">{reasons_html}</ul>
            </div>
            <div style="font-size:13px;color:#8C92A0;">
                Upload a valid resume (PDF, DOC, or DOCX) to continue.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
def render() -> None:
    st.markdown(
        '<h1 style="font-family:\'Fraunces\',serif;font-size:26px;color:#F0F2F5;margin:0 0 6px;letter-spacing:-0.02em;">Analyse Resume</h1>'
        '<p style="color:#8C92A0;font-size:14px;margin:0 0 24px;">Upload your resume and optionally a job description for a targeted match score.</p>',
        unsafe_allow_html=True,
    )

    # ── Mode toggle ───────────────────────────────────────────────
    mode = st.radio(
        "Analysis mode",
        ["General ATS Score", "Job Description Comparison"],
        horizontal=True,
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # ── Upload column ─────────────────────────────────────────────
    with col1:
        st.markdown(
            card(section_header("file", "Resume", "PDF, DOC or DOCX — max 5 MB")),
            unsafe_allow_html=True,
        )
        resume_file = st.file_uploader(
            "Upload resume",
            type=["pdf", "doc", "docx"],
            label_visibility="collapsed",
        )
        if resume_file:
            st.markdown(
                f'<div style="margin-top:8px;background:rgba(46,204,138,.07);'
                f'border:1px solid rgba(46,204,138,.2);border-radius:8px;'
                f'padding:8px 14px;display:flex;align-items:center;gap:8px;'
                f'font-size:13px;color:#2ECC8A;">'
                f'{svg_icon("check", 14, "#2ECC8A")}'
                f'{resume_file.name} — {resume_file.size / 1024:.0f} KB</div>',
                unsafe_allow_html=True,
            )

    # ── JD column ─────────────────────────────────────────────────
    with col2:
        if mode == "General ATS Score":
            st.markdown(
                card(
                    section_header("target", "Job Description")
                    + '<div style="background:rgba(74,158,245,.07);border:1px solid rgba(74,158,245,.2);'
                    'border-radius:10px;padding:14px 16px;display:flex;align-items:flex-start;gap:10px;">'
                    + svg_icon("info", 18, "#4A9EF5")
                    + '<p style="font-size:13px;color:#4A9EF5;margin:0;line-height:1.6;">'
                    'Switch to <strong>Job Description Comparison</strong> mode to get keyword match '
                    'and fine-tuned BERT semantic analysis.</p></div>'
                ),
                unsafe_allow_html=True,
            )
            job_description = ""
        else:
            st.markdown(
                card(section_header("target", "Job Description", "Paste or upload the target JD")),
                unsafe_allow_html=True,
            )
            jd_method = st.radio(
                "JD input method",
                ["Paste text", "Upload .txt"],
                horizontal=True,
                label_visibility="collapsed",
            )
            if jd_method == "Paste text":
                job_description = st.text_area(
                    "Job description",
                    height=160,
                    placeholder="Paste the full job description here…",
                    label_visibility="collapsed",
                )
            else:
                jd_file = st.file_uploader(
                    "Upload JD",
                    type=["txt"],
                    label_visibility="collapsed",
                )
                job_description = jd_file.read().decode("utf-8", errors="ignore") if jd_file else ""

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Run button ────────────────────────────────────────────────
    run_disabled = resume_file is None
    col_btn, _ = st.columns([1, 3])
    with col_btn:
        run = st.button(
            "Run Analysis" if not run_disabled else "Upload a resume to begin",
            type    = "secondary",
            disabled= run_disabled,
            use_container_width=True,
        )

    if run and resume_file:
        from frontend.services.auth_utils import ensure_valid_session
        access_token = ensure_valid_session()

        if not access_token:
            st.markdown(
                alert("Your session has expired or you're not signed in. Please sign in to run an analysis.", "warning"),
                unsafe_allow_html=True,
            )
            return
        
        # Step 1: Validate document type BEFORE running expensive analysis
        with st.spinner("Checking document type…"):
            try:
                val_result = api_client.validate_document(resume_file, access_token)
                if not val_result.get("is_resume", True):
                    _show_rejection_ui(
                        doc_type   = val_result.get("document_type", "Unknown"),
                        confidence = val_result.get("confidence", 0),
                        reasoning  = val_result.get("reasoning", []),
                    )
                    return
            except requests.HTTPError as exc:
                if exc.response is not None and exc.response.status_code == 422:
                    try:
                        detail = exc.response.json().get("detail", {})
                        if isinstance(detail, dict) and detail.get("type") == "not_a_resume":
                            _show_rejection_ui(
                                doc_type   = detail.get("document_type", "Unknown"),
                                confidence = detail.get("confidence", 0),
                                reasoning  = detail.get("reasoning", []),
                            )
                            return
                    except Exception:
                        pass
                _show_backend_error(exc)
                return
            except Exception as exc:
                pass
        
        # Step 2: Full ATS analysis
        with st.spinner("Analyzing your resume… This may take sometime..."):
            try:
                result = api_client.analyze_resume(
                    file = resume_file,
                    job_description   = job_description or "",
                    access_token     = access_token,
                )
            except requests.HTTPError as exc:
                if exc.response is not None and exc.response.status_code == 401:
                    st.markdown(
                        alert("Your session was rejected by the server. Please sign out and sign in again.", "danger"),
                        unsafe_allow_html=True,
                    )
                    return
                _show_backend_error(exc)
                return
            except requests.RequestException as exc:
                _show_backend_error(exc)
                return

        st.markdown("<hr style='border-color:rgba(255,255,255,.07);margin:2rem 0;'>", unsafe_allow_html=True)
        display_results(result)