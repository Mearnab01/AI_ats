from __future__ import annotations

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional

import spacy
from sentence_transformers import SentenceTransformer
from backend.core.logger import setup_logger
from backend.models.schemas import IssueDetail
from backend.services.groq_parser import parse_resume, parse_job_description
from backend.services.jd_matcher import compare_resume_with_jd
from backend.services.feedback_engine import analyze_issues, generate_issues_summary
from backend.services.ats_scorer import (
    calculate_overall_score,
    validate_skills_with_projects,
    detect_location_info,
)
from backend.services.recommendation_engine import (
    generate_skill_recommendations,
    generate_grammar_recommendations,
)
from backend.services.bert_matcher import get_model_info

logger = setup_logger("ats_resume_scorer | resume_analyzer")

_NLP_POOL = ThreadPoolExecutor(max_workers=4, thread_name_prefix="nlp")


def _run_grammar_check(text: str, nlp: spacy.Language) -> Dict:
    doc = nlp(text[:8_000])  # cap to avoid slow processing on huge inputs

    critical_errors: list = []
    minor_errors:    list = []

    for token in doc:
        if (
            token.is_alpha
            and not token.is_stop
            and not token.is_upper        # acronyms (API, AWS, etc.)
            and not token.like_url
            and not token.like_email
            and token.pos_ not in ("PROPN", "NUM")
            and len(token.text) > 3
            and nlp.vocab[token.lower_].is_oov   # out-of-vocabulary = likely misspelling
        ):
            entry = {
                "error_text": token.text,
                "message":    "Possible misspelling or unknown term",
                "suggestions": [],
                "offset":     token.idx,
            }
           
            if token.sent.text[:30].lower().strip() in ("experience", "skills", "summary"):
                critical_errors.append(entry)
            else:
                minor_errors.append(entry)

    total   = len(critical_errors) + len(minor_errors)
    penalty = min(10.0, len(critical_errors) * 2.0 + len(minor_errors) * 0.5)

    return {
        "total_errors":          total,
        "critical_errors":       critical_errors[:10],
        "moderate_errors":       [],
        "minor_errors":          minor_errors[:20],
        "grammar_score":         max(0, 100 - int(penalty * 10)),
        "penalty_applied":       penalty,
        "error_free_percentage": round((1 - total / max(len(list(doc)), 1)) * 100, 1),
    }


# ── async helper ──────────────────────────────────────────────────────────────

async def _in_pool(fn, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_NLP_POOL, fn, *args)


# ── main orchestrator ──────────────────────────────────────────────────────────

async def analyze_full_resume(
    resume_text:     str,
    nlp:             spacy.Language,
    embedder:        SentenceTransformer,
    job_description: Optional[str] = None,
) -> Dict:

    # ── Step 1: Groq parsing (concurrent when JD present) ────────────────────
    if job_description and job_description.strip():
        parsed_resume, parsed_jd = await asyncio.gather(
            _in_pool(parse_resume, resume_text),
            _in_pool(parse_job_description, job_description.strip()),
        )
    else:
        parsed_resume = await _in_pool(parse_resume, resume_text)
        parsed_jd     = None

    logger.info(
        "Parsed resume - skills: %d, experience: %d, projects: %d",
        len(parsed_resume.get("skills", [])),
        len(parsed_resume.get("experience", [])),
        len(parsed_resume.get("projects", [])),
    )

    skills       = parsed_resume.get("skills", [])
    projects     = parsed_resume.get("projects", [])
    keywords     = parsed_resume.get("keywords", [])
    action_verbs = parsed_resume.get("action_verbs", [])

    experience_months = sum(
        int(e.get("duration_months", 0))
        for e in parsed_resume.get("experience", [])
        if isinstance(e, dict)
    )

    contact_info = {
        "email":     parsed_resume.get("email"),
        "phone":     parsed_resume.get("phone"),
        "linkedin":  parsed_resume.get("linkedin"),
        "github":    parsed_resume.get("github"),
        "portfolio": None,
    }

    # ── Step 2: CPU-bound NLP in thread pool ──────────────────────────────────
    skill_validation, grammar_results, location_results = await asyncio.gather(
        _in_pool(
            validate_skills_with_projects,
            skills,
            projects,
            parsed_resume.get("experience", []),
            embedder,
        ),
        _in_pool(_run_grammar_check, resume_text, nlp),
        _in_pool(detect_location_info, resume_text, nlp),
    )

    # ── Step 3: JD comparison via fine-tuned BERT (only if JD present) ───────
    jd_comparison_result = None
    jd_keywords:          list = []
    bert_model_info             = get_model_info()   # always include in response, even without a JD

    if parsed_jd:
        jd_keywords = list(set(
            parsed_jd.get("keywords", [])
            + parsed_jd.get("required_skills", [])
            + parsed_jd.get("preferred_skills", [])
        ))
        jd_comparison_result = await _in_pool(
            compare_resume_with_jd,
            resume_text,
            keywords,
            skills,
            job_description.strip(),
            jd_keywords,
            embedder,   
            nlp,
        )
        bert_model_info = jd_comparison_result.get("model_info", bert_model_info)

    # ── Step 4: Scoring ────────────────────────────────────────────────────────
    scores = calculate_overall_score(
        text=resume_text,
        parsed_resume=parsed_resume,
        skills=skills,
        keywords=keywords,
        action_verbs=action_verbs,
        skill_validation_results=skill_validation,
        grammar_results=grammar_results,
        location_results=location_results,
        jd_keywords=jd_keywords or None,
        experience_months=experience_months,
    )

    # ── Step 5: Issue detection ─
    detailed_feedback = analyze_issues(
        resume_text=resume_text,
        parsed_resume=parsed_resume,
        skills=skills,
        projects=projects,
        action_verbs=action_verbs,
        skill_validation=skill_validation,
        scores=scores,
        contact_info=contact_info,
    )
    issues_summary = generate_issues_summary(detailed_feedback)

    # ── Step 6: Recommendations ─
    recommendations = (
        generate_skill_recommendations(skill_validation)
        + generate_grammar_recommendations(grammar_results)
    )
    recommendation_texts = [r.description for r in recommendations]

    # ── Step 6b: Skill validation summary ─────────────────────────────────────
    validated_raw   = skill_validation.get("validated_skills", [])
    unvalidated_raw = skill_validation.get("unvalidated_skills", [])
    total_skills    = len(validated_raw) + len(unvalidated_raw)
    val_pct         = round((len(validated_raw) / total_skills * 100) if total_skills else 0, 1)

    skill_validation_details = {
        "validated": [
            {"skill": item["skill"], "projects": item.get("projects", [])}
            for item in validated_raw
        ],
        "unvalidated":     unvalidated_raw,
        "total":           total_skills,
        "validated_count": len(validated_raw),
        "validation_pct":  val_pct,
    }

    # ── Step 7: Assemble final response ───────────────────────────────────────
    return {
        "ATS_score":        scores["overall_score"],
        "ats_score":        scores["overall_score"],
        "component_scores": {
            "formatting":        scores["formatting_score"],
            "keywords":          scores["keywords_score"],
            "content":           scores["content_score"],
            "skill_validation":  scores["skill_validation_score"],
            "ats_compatibility": scores["ats_compatibility_score"],
        },
        "issues_summary":           issues_summary,
        "detailed_feedback":        detailed_feedback,
        "jd_match_analysis":        jd_comparison_result,
        "jd_comparison":            jd_comparison_result,
        "skills":                   skills,
        "matched_keywords": (
            jd_comparison_result["matched_keywords"] if jd_comparison_result else list(keywords[:20])
        ),
        "missing_keywords": (
            jd_comparison_result["missing_keywords"] if jd_comparison_result else []
        ),
        "strengths": _generate_strengths(
            parsed_resume, skills, projects, action_verbs, skill_validation, scores
        ),
        "recommendations":          recommendation_texts,
        "interpretation":           scores.get("overall_interpretation", ""),
        "skill_validation_details": skill_validation_details,
        "experience_months":        experience_months,
        "grammar_summary": {
            "total_errors": grammar_results.get("total_errors", 0),
            "penalty":      grammar_results.get("penalty_applied", 0.0),
        },
        "location_privacy": {
            "risk":            location_results.get("privacy_risk", "none"),
            "recommendations": location_results.get("recommendations", []),
        },
        "bert_model_info": bert_model_info,
    }


# ── strengths helper ─────────────────

def _generate_strengths(
    parsed_resume: Dict,
    skills: List,
    projects: List,
    action_verbs: List,
    skill_validation: Dict,
    scores: Dict,
) -> List[str]:
    """Generate a list of things the resume does well, based on actual structured data."""
    strengths = []

    if parsed_resume.get("experience"):
        strengths.append("Has a dedicated Experience section")
    if parsed_resume.get("projects") or len(projects) > 0:
        strengths.append("Includes a Projects section showcasing applied skills")
    if parsed_resume.get("education"):
        strengths.append("Education section is present")
    if parsed_resume.get("skills"):
        strengths.append("Clear Skills section with listed technologies")
    if (parsed_resume.get("professional_summary") or "").strip():
        strengths.append("Professional Summary provides a quick overview")

    if len(skills) >= 8:
        strengths.append(f"Strong skill set — {len(skills)} skills detected")
    if len(action_verbs) >= 5:
        strengths.append(f"Uses {len(action_verbs)} strong action verbs in bullet points")

    validated = skill_validation.get("validated_skills", [])
    if len(validated) >= 3:
        strengths.append(f"{len(validated)} skills are backed by project/experience evidence")

    if scores.get("formatting_score", 0) >= 16:
        strengths.append("Well-formatted and ATS-friendly structure")
    if scores.get("content_score", 0) >= 20:
        strengths.append("Content quality is high with measurable achievements")

    return strengths