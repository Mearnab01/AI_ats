from typing import List, Optional
from backend.core.logger import setup_logger
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import Response
from backend.api.auth import get_current_user
from backend.core.config import MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB
from backend.models.schemas import (
    AnalysisResponse,
    ComponentScores,
    JDComparison,
    SkillValidationDetails,
    LocationPrivacy,
)

logger = setup_logger("ats_resume_scorer | backend api routes")

router = APIRouter(prefix="/api/v1", tags=["Analysis"])

_STRIP_PREFIXES = ("✅","🌟","❌","⚠️","📝","🔴","🟡","🟢","🟠","👍","✔","•","-")

def _clean(text: str) -> str:
    for ch in _STRIP_PREFIXES:
        text = text.replace(ch, "")
    return text.strip()

def _clean_list(items: list) -> list:
    return [_clean(s) if isinstance(s, str) else s for s in items]


# ── resume analysis ────────────────────────────────────────────────────────────

@router.post("/analyze-resume", response_model=AnalysisResponse)
async def analyze_resume(
    request:Request,
    resume: UploadFile = File(..., description="Resume - PDF or DOCX, max 5 MB"),
    job_description: str = Form("", description="Job description text (optional)"),
    user_id: str = Depends(get_current_user),
):
    nlp      = request.app.state.nlp
    embedder = request.app.state.embedder

    # ── file validation ───────────────────────────────────────────────────────
    file_bytes = await resume.read()
    filename   = resume.filename or "resume"

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({len(file_bytes)/1024/1024:.1f} MB). Max is {MAX_FILE_SIZE_MB} MB.",
        )

    try:
        from backend.services.resume_parser import parse_resume_file
        resume_text, _ = parse_resume_file(file_bytes, filename)
        logger.info("Parsed '%s': %d chars", filename, len(resume_text))
    except Exception as exc:
        logger.error("File parsing failed: %s", exc)
        raise HTTPException(status_code=422, detail=f"Could not read resume: {exc}")

    # ── analysis ──────────────────────────────────────────────────────────────
    try:
        from backend.services.resume_analyzer import analyze_full_resume
        result = await analyze_full_resume(
            resume_text=resume_text,
            nlp=nlp,
            embedder=embedder,
            job_description=job_description,
        )
    except Exception as exc:
        logger.error("Analysis failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")

    # ── build response ────────────────────────────────────────────────────────
    cs = result.get("component_scores", {})
    component_scores = ComponentScores(
        formatting        = float(cs.get("formatting", 0)),
        keywords          = float(cs.get("keywords", 0)),
        content           = float(cs.get("content", 0)),
        skill_validation  = float(cs.get("skill_validation", 0)),
        ats_compatibility = float(cs.get("ats_compatibility", 0)),
    )

    jd_out: Optional[JDComparison] = None
    jd_raw = result.get("jd_comparison") or result.get("jd_match_analysis")
    if jd_raw:
        if hasattr(jd_raw, "model_dump"):
            jd_raw = jd_raw.model_dump()
        jd_out = JDComparison(
            match_percentage    = round(float(jd_raw.get("match_percentage",   0.0)), 1),
            semantic_similarity = round(float(jd_raw.get("semantic_similarity",0.0)), 3),
            matched_keywords    = jd_raw.get("matched_keywords", [])[:20],
            missing_keywords    = jd_raw.get("missing_keywords", [])[:15],
            skills_gap          = jd_raw.get("skills_gap",       [])[:15],
        )

    svd = result.get("skill_validation_details", {})
    skill_val_out = SkillValidationDetails(
        validated       = svd.get("validated",       []),
        unvalidated     = svd.get("unvalidated",     []),
        total           = svd.get("total",           0),
        validated_count = svd.get("validated_count", 0),
        validation_pct  = svd.get("validation_pct",  0.0),
    )

    # fire-and-forget DB save
    try:
        import asyncio
        from backend.database.supabase_db import save_analysis
        asyncio.ensure_future(save_analysis(user_id=user_id, filename=filename, analysis_result=result))
    except Exception as db_exc:
        logger.warning("DB save skipped: %s", db_exc)

    bert_info = result.get("bert_model_info") or {}
    return AnalysisResponse(
        ATS_score                = float(result.get("ATS_score", 0)),
        ats_score                = float(result.get("ats_score",  0)),
        component_scores         = component_scores,
        issues_summary           = _clean_list(result.get("issues_summary", [])),
        detailed_feedback        = result.get("detailed_feedback", []),
        jd_match_analysis        = jd_out,
        jd_comparison            = jd_out,
        skill_validation_details = skill_val_out,
        keyword_match            = float(jd_out.match_percentage if jd_out else 0),
        missing_keywords         = result.get("missing_keywords", [])[:15],
        matched_keywords         = result.get("matched_keywords", [])[:20],
        suggestions              = _clean_list(result.get("recommendations", [])),
        strengths                = _clean_list(result.get("strengths", [])),
        skills                   = result.get("skills", []),
        warnings                 = [],
        interpretation           = result.get("interpretation", ""),
        bert_model_info          = {
            "using_finetuned": bert_info.get("using_finetuned", False),
            "finetuned_mae":   bert_info.get("finetuned_mae"),
            "base_mae":        bert_info.get("base_mae"),
            "improvement_pct": bert_info.get("improvement_pct"),
        },
        location_privacy=LocationPrivacy(
        risk=(
            result.get("location_privacy", {})
                .get("risk", "none")
        ),
        recommendations=(
            result.get("location_privacy", {})
                .get("recommendations", [])
        ),
    ),
)


# ── history ────────────────────────────────────────────────────────────────────

@router.get("/history")
async def get_history(request: Request, user_id: str = Depends(get_current_user)):
    try:
        from backend.database.supabase_db import get_user_history
        return await get_user_history(user_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Could not retrieve history.")


@router.delete("/history/{analysis_id}")
async def delete_history(
    analysis_id: str, request: Request, user_id: str = Depends(get_current_user)
):
    try:
        from backend.database.supabase_db import delete_analysis
        await delete_analysis(user_id=user_id, analysis_id=analysis_id)
        return {"deleted": analysis_id}
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Could not delete entry.")


# ── PDF ────────────────────────────────────────────────────────────────────────

@router.post("/generate-pdf")
async def generate_pdf(request: Request):
    body = await request.json()
    try:
        from backend.services.pdf_export import generate_pdf_report
        from fastapi.responses import Response
        pdf_bytes   = generate_pdf_report(body)
        return Response(
            content    = pdf_bytes,
            media_type = "application/pdf",
            headers    = {"Content-Disposition": 'attachment; filename="ats_report.pdf"'},
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {exc}")

@router.get("/history/{analysis_id}/pdf")
async def generate_history_pdf(
    analysis_id: str,
    user_id: str = Depends(get_current_user),
):
    from backend.database.supabase_db import get_user_history
    from backend.services.pdf_export import generate_pdf_report
 
    history = await get_user_history(user_id)
    analysis_data = next(
        (item["analysis_result"] for item in history if str(item["id"]) == str(analysis_id)),
        None,
    )
    if not analysis_data:
        raise HTTPException(status_code=404, detail="Analysis not found")
 
    try:
        pdf_bytes = generate_pdf_report(analysis_data)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=Criterion_report_{analysis_id}.pdf"
            },
        )
    except Exception as e:
        logger.error(f"Failed to generate PDF for history: {e}")
# ── health ─────────────────────────────────────────────────────────────────────

@router.get("/health")
async def health(request: Request):
    from backend.services.bert_matcher import get_model_info
    bert_info  = get_model_info()
    models_ok  = (
        hasattr(request.app.state, "nlp")
        and hasattr(request.app.state, "embedder")
    )
    return {
        "status":         "ok" if models_ok else "degraded",
        "nlp_loaded":     hasattr(request.app.state, "nlp"),
        "embedder_loaded":hasattr(request.app.state, "embedder"),
        "bert_scorer": {
            "active":          bert_info["using_finetuned"],
            "model":           "fine-tuned all-mpnet-base-v2" if bert_info["using_finetuned"] else "base all-mpnet-base-v2",
            "base_mae":        bert_info.get("base_mae"),
            "finetuned_mae":   bert_info.get("finetuned_mae"),
            "improvement_pct": bert_info.get("improvement_pct"),
            "trained_pairs":   bert_info.get("trained_on_pairs"),
        },
    }