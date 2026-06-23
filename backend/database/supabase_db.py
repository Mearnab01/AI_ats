import logging
import httpx
import json
from datetime import datetime, timezone
from typing import List, Optional, Dict
from backend.core.logger import setup_logger
from backend.core.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

logger = setup_logger("ats_resume_scorer | supabase_db")


def _get_headers():
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        return None
    return {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

async def save_analysis(
    user_id: str, 
    filename: str, 
    analysis_result: Dict,
    resume_text:     str        = "",
    resume_skills:   List[str]  = None,
    resume_embedding: List[float] = None,
    doc_validation:  Dict       = None,
    ) -> Optional[str]:
    
    headers = _get_headers()
    if not headers:
        return None

    def _json_default(o):
        if hasattr(o, 'model_dump'):
            return o.model_dump()
        return str(o)
    serializable_result = json.loads(json.dumps(analysis_result, default=_json_default))

    doc = {
        "user_id": user_id,
        "filename": filename,
        "ats_score": serializable_result.get("ats_score", 0),
        "keyword_match": serializable_result.get("keyword_match", 0),
        "missing_keywords": serializable_result.get("missing_keywords", []),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "analysis_result": serializable_result,
        
        "resume_text":       resume_text[:20000] if resume_text else "",
        "resume_skills":     resume_skills or [],
        "resume_embedding":  resume_embedding,        # nullable float array
        "doc_validation":    doc_validation or {},
    }

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/analyses"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=doc)
            response.raise_for_status()
            data = response.json()
            if data and len(data) > 0:
                inserted_id = str(data[0].get("id"))
                logger.info(f"Saved analysis for user {user_id}: {inserted_id}")
                return inserted_id
            return None
    except Exception as exc:
        logger.error(f"Failed to save analysis to Supabase: {exc}")
        return None
    
    
async def get_latest_analysis(user_id: str) -> Optional[Dict]:
    """
    Return the most recent analysis row for a user.
    Jobs page uses this to get cached skills + embedding
    without re-running any model.
    """
    headers = _get_headers()
    if not headers:
        return None
 
    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/analyses"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url,
                headers = headers,
                params  = {
                    "user_id": f"eq.{user_id}",
                    "order":   "created_at.desc",
                    "limit":   "1",
                    "select":  "id,filename,ats_score,resume_text,resume_skills,resume_embedding,analysis_result,created_at",
                },
                timeout = 10,
            )
            resp.raise_for_status()
            rows = resp.json()
            return rows[0] if rows else None
    except Exception as exc:
        logger.error("get_latest_analysis failed: %s", exc)
        return None
    
# ── get_cached_embedding ──────────────────────────────────────────────────
 
async def get_cached_embedding(user_id: str) -> Optional[List[float]]:
    """Return stored resume embedding for the user's latest analysis."""
    row = await get_latest_analysis(user_id)
    if not row:
        return None
    return row.get("resume_embedding")

# ── save_job_matches ──────────────────────────────────────────────────────
 
async def save_job_matches(user_id: str, analysis_id: str, jobs: List[Dict]) -> None:
    """
    Persist ranked job matches linked to an analysis.
    Stored in `job_matches` table.
    """
    headers = _get_headers()
    if not headers:
        return
 
    rows = [
        {
            "user_id":     user_id,
            "analysis_id": analysis_id,
            "job_id":      j.get("id"),
            "match_score": j.get("match_score", 0),
            "created_at":  datetime.now(timezone.utc).isoformat(),
        }
        for j in jobs[:50]
    ]
 
    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/job_matches"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                headers = {**headers, "Prefer": "resolution=merge-duplicates,return=minimal"},
                json    = rows,
                timeout = 10,
            )
            resp.raise_for_status()
            logger.info("Saved %d job matches for user %s", len(rows), user_id)
    except Exception as exc:
        logger.error("save_job_matches failed: %s", exc)

async def get_user_history(user_id: str) -> List[Dict]:
    headers = _get_headers()
    if not headers:
        return []

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/analyses"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, 
                headers=headers, 
                params={
                    "user_id": f"eq.{user_id}",
                    "order": "created_at.desc"
                }
            )
            response.raise_for_status()
            docs = response.json()
            
            results = []
            for doc in docs:
                results.append({
                    "id": str(doc.get("id")),
                    "filename": doc.get("filename", "resume"),
                    "resume_name": doc.get("filename", "resume"),
                    "job_title": "Software Engineer",
                    "ats_score": doc.get("ats_score", 0),
                    "keyword_match": doc.get("keyword_match", 0),
                    "missing_keywords": doc.get("missing_keywords", []),
                    "date": doc.get("created_at", ""),
                    "created_at": doc.get("created_at", ""),
                    "analysis_result": doc.get("analysis_result", {}),
                })
            return results
    except Exception as exc:
        logger.error(f"Failed to fetch history from Supabase: {exc}")
        return []

async def delete_analysis(analysis_id: str, user_id: str) -> bool:
    headers = _get_headers()
    if not headers:
        return False

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/analyses"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                url, 
                headers=headers, 
                params={
                    "id": f"eq.{analysis_id}",
                    "user_id": f"eq.{user_id}"
                }
            )
            response.raise_for_status()
            return True
    except Exception as exc:
        logger.error(f"Failed to delete analysis {analysis_id}: {exc}")
        return False