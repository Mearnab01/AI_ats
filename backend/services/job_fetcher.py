"""
job_fetcher.py
==============
Fetches jobs from Apify actors:
  - LinkedIn Jobs Scraper
  - Naukri Jobs Scraper
  - Wellfound Jobs Scraper

All results normalised to a single JobPosting dict.
Results stored in Supabase `jobs` table with TTL-based cache.
No SQLite — Supabase only.
"""

from __future__ import annotations

import hashlib
import httpx
import os
import json
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from backend.core.logger import setup_logger
from backend.core.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

logger = setup_logger("criterion | job_fetcher")

# ── Config ─────────────────────────────────────────────────────────────────────
APIFY_TOKEN      = os.getenv("APIFY_API_TOKEN", "")
APIFY_BASE       = "https://api.apify.com/v2"

# Actor IDs
ACTOR_LINKEDIN   = "curious_coder~linkedin-jobs-scraper"
ACTOR_NAUKRI = "muhammetakkurtt~naukri-job-scraper"

JOB_CACHE_TTL_HOURS = 12      # re-fetch if older than 12h
MAX_JOBS_PER_SOURCE = 25


# ── Supabase helpers ───────────────────────────────────────────────────────────

def _headers() -> Dict[str, str]:
    return {
        "apikey":        SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type":  "application/json",
        "Prefer":        "return=representation",
    }


def _jobs_url() -> str:
    return f"{SUPABASE_URL.rstrip('/')}/rest/v1/jobs"


# ── Normaliser ─────────────────────────────────────────────────────────────────

def _normalise(raw: Dict, source: str) -> Optional[Dict]:
    """Map source-specific field names → unified JobPosting schema."""
    try:
        title    = (raw.get("title") or raw.get("jobTitle") or raw.get("position") or "").strip()
        company  = (raw.get("company") or raw.get("companyName") or raw.get("organization") or "").strip()
        location = (raw.get("location") or raw.get("jobLocation") or raw.get("place") or "").strip()
        url      = (raw.get("jobUrl") or raw.get("url") or raw.get("link") or "").strip()
        desc     = (raw.get("description") or raw.get("jobDescription") or raw.get("descriptionHtml") or raw.get("details") or "").strip()
        exp      = (raw.get("experienceLevel") or raw.get("experience") or raw.get("seniority") or "").strip()
        salary   = (raw.get("salary") or raw.get("salaryRange") or "").strip()
        posted   = (raw.get("postedAt") or raw.get("datePosted") or raw.get("date") or "").strip()

        if not title or not company:
            return None

        # Stable ID: hash of title+company+source
        job_id = hashlib.md5(f"{source}:{title}:{company}".encode()).hexdigest() 
        
        return {
            "id":          job_id,
            "source":      source,
            "title":       title,
            "company":     company,
            "location":    location,
            "apply_url":   url,
            "description": desc[:3000],   # cap to avoid huge rows
            "experience":  exp,
            "salary":      salary,
            "posted_at":   posted,
            "fetched_at":  datetime.now(timezone.utc).isoformat(),
            "match_score": 0.0,           # filled by matcher
            "skills_matched": [],
            "skills_missing": [],
        }
        
    
    except Exception as exc:
        logger.warning("Normalise failed for %s row: %s", source, exc)
        return None


# ── Apify runner ───────────────────────────────────────────────────────────────

async def _run_actor(
    client: httpx.AsyncClient,
    actor_id: str,
    input_payload: Dict,
    source_label: str,
) -> List[Dict]:
    """Run an Apify actor synchronously and return normalised job list."""
    if not APIFY_TOKEN:
        logger.warning("APIFY_API_TOKEN not set — skipping %s", source_label)
        return []

    run_url = f"{APIFY_BASE}/acts/{actor_id}/run-sync-get-dataset-items"
    params  = {"token": APIFY_TOKEN, "format": "json", "limit": MAX_JOBS_PER_SOURCE}

    try:
        resp = await client.post(
            run_url,
            params  = params,
            json    = input_payload,
            timeout = 90,
        )

        
        resp.raise_for_status()
        items = resp.json()
        
        logger.info("%s returned %d raw items", source_label, len(items))
        jobs  = [j for j in (_normalise(r, source_label) for r in items) if j]
        return jobs
    except httpx.TimeoutException:
        logger.warning("%s actor timed out", source_label)
        return []
    except Exception as exc:
        logger.error("%s actor failed: %s", source_label, exc)
        return []


# ── Per-source fetchers ────────────────────────────────────────────────────────

async def _fetch_linkedin(client: httpx.AsyncClient, query: str, location: str) -> List[Dict]:
    search_url = (
        "https://www.linkedin.com/jobs/search/"
        f"?keywords={query.replace(' ', '%20')}"
        f"&location={location.replace(' ', '%20')}"
    )
    payload = {
        "count": MAX_JOBS_PER_SOURCE,
        "scrapeCompany": True,
        "splitByLocation": False,
        "urls": [search_url]
    }
    return await _run_actor(client, ACTOR_LINKEDIN, payload, "LinkedIn")


# ── Supabase cache read/write ──────────────────────────────────────────────────

async def _load_cached_jobs(query_hash: str) -> List[Dict]:
    """Return cached jobs if fetched within TTL, else empty list."""
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=JOB_CACHE_TTL_HOURS)).isoformat()
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                _jobs_url(),
                headers = _headers(),
                params  = {
                    "query_hash": f"eq.{query_hash}",
                    "fetched_at": f"gte.{cutoff}",
                    "order":      "match_score.desc",
                    "limit":      "200",
                },
                timeout = 10,
            )
            resp.raise_for_status()
            rows = resp.json()
            logger.info("Cache hit: %d jobs for query_hash %s", len(rows), query_hash[:8])
            return rows
    except Exception as exc:
        logger.warning("Cache load failed: %s", exc)
        return []


async def _save_jobs_to_supabase(jobs: List[Dict], query_hash: str) -> None:
    """Upsert jobs into Supabase. Uses job id as conflict target."""
    if not jobs:
        return
    rows = [{**j, "query_hash": query_hash} for j in jobs]
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                _jobs_url(),
                headers = {**_headers(), "Prefer": "resolution=merge-duplicates,return=minimal"},
                json    = rows,
                timeout = 15,
            )
            resp.raise_for_status()
            logger.info("Saved %d jobs to Supabase", len(rows))
    except Exception as exc:
        logger.error("Failed to save jobs: %s", exc)


# ── Public API ─────────────────────────────────────────────────────────────────

async def fetch_jobs(
    query:    str,
    location: str = "India",
    sources:  List[str] = ("LinkedIn"),
) -> List[Dict]:
    """
    Fetch jobs from Apify sources with Supabase cache.

    Parameters
    ----------
    query    : job title / role  e.g. "AI Engineer"
    location : preferred location  e.g. "Bangalore"
    sources  : which scrapers to use

    Returns
    -------
    List of normalised job dicts (empty list if Apify not configured).
    """
    print("="*80)
    print("FINAL QUERY SENT TO FETCHER:", query)
    print("="*80)
    query_hash = hashlib.md5(f"{query}:{location}".encode()).hexdigest()

    # 1. Try cache first
    cached = await _load_cached_jobs(query_hash)
    if cached:
        return cached

    # 2. Fetch live
    logger.info("Fetching live jobs for '%s' in '%s'", query, location)
    all_jobs: List[Dict] = []

    async with httpx.AsyncClient() as client:
        if "LinkedIn" in sources:
            all_jobs.extend(await _fetch_linkedin(client, query, location))

    # Deduplicate by id
    seen: set = set()
    unique = []
    for j in all_jobs:
        if j["id"] not in seen:
            seen.add(j["id"])
            unique.append(j)

    logger.info("Fetched %d unique jobs across all sources", len(unique))

    # 3. Persist
    await _save_jobs_to_supabase(unique, query_hash)
    return unique