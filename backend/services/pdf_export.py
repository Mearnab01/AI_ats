"""pdf_export.py — Pure-Python PDF generation via ReportLab.
Replaces WeasyPrint (requires libpango which is unavailable on Windows without GTK).
"""
import io
from backend.core.logger import setup_logger

logger = setup_logger("pdf export service")


def _get_color(score: float):
    from reportlab.lib import colors
    if score >= 80:
        return colors.HexColor("#2ECC8A")
    elif score >= 60:
        return colors.HexColor("#F5A623")
    return colors.HexColor("#F0503A")


def generate_pdf_report(analysis: dict) -> bytes:
    """Generate a clean PDF report from an analysis result dict."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    )

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=18*mm, bottomMargin=18*mm,
    )

    BG      = colors.HexColor("#0C0E12")
    FG      = colors.HexColor("#F0F2F5")
    MUTED   = colors.HexColor("#8C92A0")
    BRAND   = colors.HexColor("#E8A44A")
    CARD    = colors.HexColor("#111318")
    BORDER  = colors.HexColor("#1E2129")
    GREEN   = colors.HexColor("#2ECC8A")
    RED     = colors.HexColor("#F0503A")
    YELLOW  = colors.HexColor("#F5A623")

    styles = getSampleStyleSheet()

    def _style(name, **kw):
        base = ParagraphStyle(name, parent=styles["Normal"], **kw)
        return base

    title_s   = _style("title",   fontName="Helvetica-Bold", fontSize=22, textColor=FG,   spaceAfter=4)
    sub_s     = _style("sub",     fontName="Helvetica",      fontSize=10, textColor=MUTED, spaceAfter=12)
    h2_s      = _style("h2",      fontName="Helvetica-Bold", fontSize=13, textColor=FG,   spaceBefore=14, spaceAfter=6)
    body_s    = _style("body",    fontName="Helvetica",      fontSize=9,  textColor=MUTED, spaceAfter=4, leading=13)
    green_s   = _style("green",   fontName="Helvetica",      fontSize=9,  textColor=GREEN, spaceAfter=3)
    red_s     = _style("red",     fontName="Helvetica",      fontSize=9,  textColor=RED,   spaceAfter=3)
    brand_s   = _style("brand",   fontName="Helvetica-Bold", fontSize=9,  textColor=BRAND, spaceAfter=3)

    ats   = float(analysis.get("ATS_score") or analysis.get("ats_score") or 0)
    cs    = analysis.get("component_scores") or {}
    def _cs(k): return float((cs.get(k) if isinstance(cs, dict) else getattr(cs, k, 0)) or 0)

    story = []

    # ── Header ────────────────────────────────────────────────────
    story.append(Paragraph("Criterion", _style("logo", fontName="Helvetica-Bold", fontSize=26, textColor=BRAND)))
    story.append(Paragraph("Resume Intelligence Report", sub_s))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=12))

    # ── Score hero ────────────────────────────────────────────────
    score_color = _get_color(ats)
    band = "Excellent" if ats >= 80 else "Good" if ats >= 60 else "Needs Work"
    score_tbl = Table(
        [[
            Paragraph(f'<font color="{score_color.hexval()}" size="36"><b>{ats:.0f}</b></font><font color="#555C6B" size="16">/100</font>', styles["Normal"]),
            Paragraph(
                f'<font color="#555C6B" size="8">OVERALL ATS SCORE</font><br/>'
                f'<font color="{score_color.hexval()}" size="12"><b>{band}</b></font><br/>'
                f'<font color="#8C92A0" size="8">{analysis.get("interpretation","")}</font>',
                styles["Normal"]
            ),
        ]],
        colWidths=["35%", "65%"],
    )
    score_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), CARD),
        ("BOX",        (0,0), (-1,-1), 0.5, BORDER),
        ("ROUNDEDCORNERS", [8]),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING",(0,0),(-1,-1), 16),
        ("RIGHTPADDING",(0,0),(-1,-1), 16),
        ("TOPPADDING", (0,0),(-1,-1), 14),
        ("BOTTOMPADDING",(0,0),(-1,-1),14),
    ]))
    story.append(score_tbl)
    story.append(Spacer(1, 12))

    # ── Component scores ──────────────────────────────────────────
    story.append(Paragraph("Score Breakdown", h2_s))
    comp_rows = [
        ["Component",          "Score", "Max", ""],
        ["Keywords & Skills",  f"{_cs('keywords'):.0f}",          "25", ""],
        ["Content Quality",    f"{_cs('content'):.0f}",           "25", ""],
        ["Formatting",         f"{_cs('formatting'):.0f}",        "20", ""],
        ["Skill Validation",   f"{_cs('skill_validation'):.0f}",  "15", ""],
        ["ATS Compatibility",  f"{_cs('ats_compatibility'):.0f}", "15", ""],
    ]
    comp_tbl = Table(comp_rows, colWidths=["45%", "15%", "15%", "25%"])
    comp_style = [
        ("BACKGROUND",    (0,0), (-1,0),  BORDER),
        ("BACKGROUND",    (0,1), (-1,-1), CARD),
        ("TEXTCOLOR",     (0,0), (-1,0),  MUTED),
        ("TEXTCOLOR",     (0,1), (-1,-1), FG),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("GRID",          (0,0), (-1,-1), 0.3, BORDER),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ]
    for i in range(1, len(comp_rows)):
        val  = float(comp_rows[i][1])
        mxv  = float(comp_rows[i][2])
        pct  = val / mxv if mxv else 0
        clr  = GREEN if pct >= 0.8 else YELLOW if pct >= 0.6 else RED
        comp_style.append(("TEXTCOLOR", (1, i), (1, i), clr))
        comp_style.append(("FONTNAME",  (1, i), (1, i), "Helvetica-Bold"))
    comp_tbl.setStyle(TableStyle(comp_style))
    story.append(comp_tbl)
    story.append(Spacer(1, 12))

    # ── Strengths ─────────────────────────────────────────────────
    strengths = analysis.get("strengths") or []
    if strengths:
        story.append(Paragraph("Strengths", h2_s))
        for s in strengths:
            story.append(Paragraph("✓  " + str(s), green_s))
        story.append(Spacer(1, 8))

    # ── Critical issues ───────────────────────────────────────────
    feedback = analysis.get("detailed_feedback") or []
    high = [f for f in feedback if (f.get("severity_level") or "low").lower() in ("critical", "high")]
    if high:
        story.append(Paragraph("Critical Issues", h2_s))
        for issue in high:
            title = issue.get("issue_title", "Untitled")
            fix   = issue.get("how_to_fix", "")
            story.append(Paragraph("⚠  " + title, red_s))
            if fix:
                story.append(Paragraph("   Fix: " + fix, body_s))
        story.append(Spacer(1, 8))

    # ── JD comparison ────────────────────────────────────────────
    jd = analysis.get("jd_comparison") or analysis.get("jd_match_analysis")
    if jd:
        if hasattr(jd, "model_dump"): jd = jd.model_dump()
        story.append(Paragraph("Job Description Match", h2_s))
        kw_pct  = float(jd.get("match_percentage",   0))
        sem_pct = float(jd.get("semantic_similarity", 0)) * 100
        jd_rows = [
            ["Keyword Match",       f"{kw_pct:.0f}%"],
            ["Semantic Similarity", f"{sem_pct:.0f}%"],
        ]
        jd_tbl = Table(jd_rows, colWidths=["50%", "50%"])
        jd_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), CARD),
            ("TEXTCOLOR",  (0,0), (0,-1),  MUTED),
            ("TEXTCOLOR",  (1,0), (1,-1),  BRAND),
            ("FONTNAME",   (1,0), (1,-1),  "Helvetica-Bold"),
            ("FONTSIZE",   (0,0), (-1,-1), 9),
            ("GRID",       (0,0), (-1,-1), 0.3, BORDER),
            ("LEFTPADDING",(0,0), (-1,-1), 10),
            ("TOPPADDING", (0,0), (-1,-1), 7),
            ("BOTTOMPADDING",(0,0),(-1,-1),7),
        ]))
        story.append(jd_tbl)

        missing = jd.get("missing_keywords") or []
        if missing:
            story.append(Spacer(1, 6))
            story.append(Paragraph("Missing Keywords:", brand_s))
            story.append(Paragraph(", ".join(missing[:15]), body_s))
        story.append(Spacer(1, 8))

    # ── Recommendations ───────────────────────────────────────────
    suggestions = analysis.get("suggestions") or analysis.get("recommendations") or []
    if suggestions:
        story.append(Paragraph("Recommendations", h2_s))
        for r in suggestions[:10]:
            story.append(Paragraph("→  " + str(r), body_s))

    doc.build(story)
    return buf.getvalue()


# ── Compatibility shim so routes.py keep working unchanged ─────────────────────

def generate_combined_pdf(html_docs: dict) -> bytes:
    """Routes.py calls this with html_docs dict. We ignore the HTML and
    regenerate from the analysis_result that was passed in."""
    # html_docs is keyed by section name; we can't easily use it
    # The caller already has analysis_data, so we raise to force using generate_pdf_report
    raise RuntimeError(
        "generate_combined_pdf is deprecated. Use generate_pdf_report(analysis_dict) directly."
    )


def html_to_pdf(html: str) -> bytes:
    raise RuntimeError(
        "html_to_pdf (WeasyPrint) is unavailable on Windows. Use generate_pdf_report instead."
    )