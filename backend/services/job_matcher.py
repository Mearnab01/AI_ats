"""
job_matcher.py
==============
Ranks job postings against a resume using cosine similarity.

IMPORTANT: reuses the same SentenceTransformer already loaded in bert_matcher.py
           via _load_model() — zero extra model loading cost.

Cache strategy:
  - Resume embedding stored in Supabase `analyses.resume_embedding` on first analysis
  - Job embeddings computed once and stored in `jobs.embedding`
  - Matching = pure cosine on cached vectors — no model re-inference
"""

from __future__ import annotations

import json
import httpx
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from backend.core.logger import setup_logger
from backend.core.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
from backend.services.bert_matcher import _load_model, _encode_chunked

logger = setup_logger("criterion | job_matcher")


# ── Embedding helpers ──────────────────────────────────────────────────────────

def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.clip(np.dot(a, b) / denom, 0.0, 1.0)) if denom > 0 else 0.0


def embed_text(text: str) -> List[float]:
    """Encode text → normalised embedding as plain Python list (JSON-serialisable)."""
    vec = _encode_chunked(text[:6000])
    return vec.tolist()


def embed_resume(resume_text: str) -> List[float]:
    return embed_text(resume_text)


def embed_job(job: Dict) -> List[float]:
    """Combine title + company + description for a richer job embedding."""
    combined = f"{job.get('title','')} at {job.get('company','')}. {job.get('description','')}"
    return embed_text(combined)


# ── Skill gap ──────────────────────────────────────────────────────────────────

_COMMON_TECH_SKILLS = [
    "python","javascript","typescript","java","c++","go","rust","sql","nosql",
    "react","vue","angular","node","fastapi","django","flask","spring",
    "docker","kubernetes","aws","gcp","azure","terraform","ci/cd","git",
    "pytorch","tensorflow","scikit-learn","huggingface","langchain","rag",
    "mlops","spark","kafka","redis","postgresql","mongodb","supabase",
    "llm","nlp","computer vision","restapi","graphql","microservices",
]

def _extract_skills_from_text(text: str) -> List[str]:
    """Simple keyword scan — no spaCy overhead for job matching."""
    text_lower = text.lower()
    return [s for s in _COMMON_TECH_SKILLS if s in text_lower]


def compute_skill_gap(
    resume_skills: List[str],
    job_description: str,
) -> Tuple[List[str], List[str]]:
    """
    Returns (matched_skills, missing_skills).
    resume_skills : already-extracted skills from ATS analysis cache
    """
    job_skills   = _extract_skills_from_text(job_description)
    resume_lower = {s.lower() for s in resume_skills}

    matched = [s for s in job_skills if s in resume_lower]
    missing = [s for s in job_skills if s not in resume_lower]
    return matched, missing


# ── Supabase — update job embedding ───────────────────────────────────────────

def _sb_headers() -> Dict:
    return {
        "apikey":        SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type":  "application/json",
        "Prefer":        "return=minimal",
    }


async def _update_job_embedding(job_id: str, embedding: List[float]) -> None:
    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/jobs"
    try:
        async with httpx.AsyncClient() as client:
            await client.patch(
                url,
                headers = _sb_headers(),
                params  = {"id": f"eq.{job_id}"},
                json    = {"embedding": embedding},
                timeout = 8,
            )
    except Exception as exc:
        logger.warning("Could not update job embedding for %s: %s", job_id, exc)


# ── Main ranker ────────────────────────────────────────────────────────────────
def _sort_date(job: Dict):
    if job.get("posted_at"):
        try:
            return datetime.fromisoformat(job["posted_at"])
        except Exception:
            pass
        
    if job.get("fetched_at"):
        try:
            return datetime.fromisoformat( job["fetched_at"].replace("Z", "+00:00"))
        except Exception:
            pass
        
    return datetime(1970, 1, 1)  # fallback for missing dates
async def rank_jobs(
    jobs:           List[Dict],
    resume_text:    str,
    resume_skills:  List[str],
    resume_embedding: Optional[List[float]] = None,
) -> List[Dict]:
    """
    Score and rank jobs by cosine similarity to resume.

    Parameters
    ----------
    jobs             : raw job dicts from job_fetcher / Supabase cache
    resume_text      : plain text of resume (used only if embedding not cached)
    resume_skills    : extracted skills list from ATS analysis cache
    resume_embedding : pre-computed embedding (from Supabase cache if available)

    Returns
    -------
    Jobs sorted by match_score descending, with skill_gap fields populated.
    """
    if not jobs:
        return []

    # Resume embedding — use cached or compute once
    if resume_embedding:
        r_vec = np.array(resume_embedding, dtype=np.float32)
        logger.info("Using cached resume embedding")
    else:
        logger.info("Computing resume embedding (no cache)")
        r_vec = np.array(embed_resume(resume_text), dtype=np.float32)

    scored: List[Dict] = []

    for job in jobs:
        # Job embedding — use stored or compute + persist
        raw_emb = job.get("embedding")
        if raw_emb:
            j_vec = np.array(raw_emb, dtype=np.float32)
        else:
            j_vec = np.array(embed_job(job), dtype=np.float32)
            # Persist asynchronously (fire and forget pattern — don't await)
            import asyncio
            asyncio.create_task(_update_job_embedding(job["id"], j_vec.tolist()))

        score = _cosine(r_vec, j_vec)

        matched, missing = compute_skill_gap(
            resume_skills,
            job.get("description", "")
        )

        total_skills = len(matched) + len(missing)
        
        skill_match_pct = (
            len(matched) / total_skills if total_skills > 0 else 0.0
        )
        penalty = min(len(missing) * 0.03, 0.3)  # max 30% penalty for missing skills
        final_score = max(
            0,
            (
                score * 0.60
                + skill_match_pct * 0.40
            ) - penalty
        )
        scored.append({
            **job,
            "match_score":    round(final_score * 100, 1),
            
            "semantic_score": round(score * 100, 1),
            "skill_match_pct": round(skill_match_pct * 100, 1),
            
            "skills_matched": matched[:8],
            "skills_missing": missing[:8],
        })

    scored.sort(
        key=lambda x: (x["match_score"], _sort_date(x)),
        reverse=True
    )
    return scored