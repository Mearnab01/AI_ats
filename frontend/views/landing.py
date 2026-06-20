import streamlit as st
from frontend.components.helpers import svg_icon


def render() -> None:
    # ── Hero ──────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="position:relative;background:linear-gradient(135deg,#111318 0%,#181B22 50%,#1A1510 100%);
                    border:1px solid rgba(232,164,74,.2);border-radius:20px;
                    padding:4rem 3rem;margin-bottom:2rem;overflow:hidden;text-align:center;">
            <div style="position:absolute;top:-80px;left:50%;transform:translateX(-50%);
                        width:400px;height:400px;border-radius:50%;
                        background:radial-gradient(circle,rgba(232,164,74,.07) 0%,transparent 65%);
                        pointer-events:none;"></div>
            <div style="position:relative;">
                <div style="display:inline-flex;align-items:center;gap:8px;
                            background:rgba(232,164,74,.08);border:1px solid rgba(232,164,74,.2);
                            border-radius:9999px;padding:4px 14px;font-size:12px;font-weight:600;
                            color:#E8A44A;margin-bottom:24px;letter-spacing:.06em;text-transform:uppercase;">
                    AI-Powered Resume Intelligence
                </div>
                <h1 style="font-family:'Fraunces',serif;font-size:clamp(2rem,5vw,3rem);
                           font-weight:700;color:#F0F2F5;letter-spacing:-0.03em;
                           margin:0 0 16px;line-height:1.15;">
                    Score, Validate &<br>
                    <span style="color:#E8A44A;">Elevate</span> Your Resume
                </h1>
                <p style="color:#8C92A0;font-size:16px;max-width:560px;margin:0 auto 32px;line-height:1.7;">
                    Criterion analyses your resume against ATS requirements using a fine-tuned BERT model
                    trained on 4.5k+ resume-JD pairs — 70% more accurate than off-the-shelf models.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Analyse Resume", type="primary", use_container_width=False):
        st.session_state.current_view = "scorer"
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Stats ─────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    for col, val, label, icon in [
        (c1, "70%",  "MAE improvement over base model",     "trending"),
        (c2, "4.5k+",  "Resume-JD pairs in training set",      "layers"),
        (c3, "5",    "Scoring dimensions analysed",          "chart"),
    ]:
        with col:
            st.markdown(
                f"""
                <div style="background:#111318;border:1px solid rgba(255,255,255,.08);
                            border-radius:14px;padding:20px 16px;text-align:center;">
                    <div style="width:36px;height:36px;background:rgba(232,164,74,.08);
                                border:1px solid rgba(232,164,74,.2);border-radius:8px;
                                display:flex;align-items:center;justify-content:center;
                                margin:0 auto 12px;">
                        {svg_icon(icon, 18, "#E8A44A")}
                    </div>
                    <div style="font-family:'Fraunces',serif;font-size:28px;font-weight:700;
                                color:#F0F2F5;letter-spacing:-0.02em;">{val}</div>
                    <div style="font-size:12px;color:#555C6B;margin-top:4px;">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Features ──────────────────────────────────────────────────
    st.markdown(
        '<h2 style="font-family:\'Fraunces\',serif;font-size:20px;color:#F0F2F5;margin-bottom:16px;">What Calibr does</h2>',
        unsafe_allow_html=True,
    )

    fc1, fc2, fc3 = st.columns(3)
    features = [
        ("award",  "ATS Scoring",       "Five-dimensional scoring: formatting, keywords, content quality, skill validation, and ATS compatibility.", "#E8A44A"),
        ("shield", "Privacy Guard",     "Detects full street addresses and zip codes that reduce ATS parse scores and flag privacy risks.", "#4A9EF5"),
        ("cpu",    "Fine-tuned BERT",   "Domain-adapted all-mpnet-base-v2 for JD matching. Trained on real resume-JD pairs, not generic text.", "#2ECC8A"),
    ]
    for col, (icon, title, body, accent) in zip([fc1, fc2, fc3], features):
        with col:
            st.markdown(
                f"""
                <div style="background:#111318;border:1px solid rgba(255,255,255,.08);
                            border-top:2px solid {accent}30;border-radius:14px;
                            padding:20px 18px;height:100%;">
                    <div style="width:36px;height:36px;background:{accent}12;
                                border:1px solid {accent}30;border-radius:8px;
                                display:flex;align-items:center;justify-content:center;margin-bottom:14px;">
                        {svg_icon(icon, 18, accent)}
                    </div>
                    <h4 style="font-family:'Fraunces',serif;font-size:15px;color:#F0F2F5;
                               margin:0 0 8px;">{title}</h4>
                    <p style="font-size:13px;color:#8C92A0;margin:0;line-height:1.65;">{body}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Steps ─────────────────────────────────────────────────────
    st.markdown(
        '<h2 style="font-family:\'Fraunces\',serif;font-size:20px;color:#F0F2F5;margin-bottom:16px;">How it works</h2>',
        unsafe_allow_html=True,
    )

    s1, s2, s3 = st.columns(3)
    steps = [
        ("01", "upload",   "Upload Resume",     "PDF or DOCX, up to 5 MB. Text extracted with pdfplumber and python-docx."),
        ("02", "cpu",      "Pipeline Runs",     "Groq LLaMA-3.3 extracts structure. Fine-tuned BERT scores JD match. spaCy checks privacy."),
        ("03", "download", "Get Results",       "Score breakdown, skill validation map, keyword gap analysis, and PDF export."),
    ]
    for col, (num, icon, title, body) in zip([s1, s2, s3], steps):
        with col:
            st.markdown(
                f"""
                <div style="background:#111318;border:1px solid rgba(255,255,255,.08);
                            border-radius:14px;padding:20px 18px;">
                    <div style="font-size:11px;font-weight:700;color:#E8A44A;letter-spacing:1px;margin-bottom:12px;">{num}</div>
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                        {svg_icon(icon, 18, "#8C92A0")}
                        <span style="font-family:'Fraunces',serif;font-size:15px;font-weight:600;color:#F0F2F5;">{title}</span>
                    </div>
                    <p style="font-size:13px;color:#8C92A0;margin:0;line-height:1.65;">{body}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )