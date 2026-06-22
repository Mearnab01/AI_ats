import os
import json
import hashlib
from functools import lru_cache
from typing import Dict
from groq import Groq
from backend.core.logger import setup_logger

logger = setup_logger("ats_resume_scorer | groq parser")
 
GROQ_MODEL = "llama-3.3-70b-versatile"

# ── Disk-backed cache (survives server restarts) ──────────────────────────────
import pathlib, pickle, threading

_CACHE_DIR  = pathlib.Path(__file__).parent.parent / ".cache"
_CACHE_FILE = _CACHE_DIR / "groq_parse_cache.pkl"
_CACHE_LOCK = threading.Lock()

def _load_disk_cache() -> dict:
    try:
        if _CACHE_FILE.exists():
            with open(_CACHE_FILE, "rb") as f:
                return pickle.load(f)
    except Exception:
        pass
    return {}

def _save_disk_cache(cache: dict) -> None:
    try:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(_CACHE_FILE, "wb") as f:
            pickle.dump(cache, f)
    except Exception as e:
        logger.warning(f"Cache save failed: {e}")

_PARSE_CACHE: dict[str, dict] = _load_disk_cache()
 
MAX_INPUT_CHARS = 6_000   # ~1 500 tokens;
MAX_TOKENS      = 2_048   # JSON output never exceeds this

@lru_cache(maxsize=1)
def _get_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")
    return Groq(api_key=api_key)

# ── prompts ───────────────────────────────────────────────────────────────────
 
RESUME_SYSTEM_PROMPT = (
    "You are a resume parser. "
    "Extract information and return ONLY a valid JSON object. "
    "No explanation, no markdown, no code fences."
)

RESUME_USER_PROMPT = """\
Extract from this resume and return as JSON with exactly these keys:
name, email, phone, linkedin, github, professional_summary,
skills (array), experience (array of {{job_title,company,start_date,end_date,duration_months,description}}),
education (array of {{degree,institution,year}}), certifications (array),
projects (array of {{title,description,technologies}}),
action_verbs (array), keywords (array).
 
Rules:
- duration_months: integer months between dates; use 0 if unknown.
- skills: ALL technical and soft skills found anywhere.
- keywords: noun phrases and technical terms useful for ATS matching.
- Return ONLY raw JSON. No markdown.
 
Resume:
{raw_text}"""
 
JD_SYSTEM_PROMPT = (
    "You are a job description parser. "
    "Return ONLY a valid JSON object. No explanation, no markdown."
)
 
JD_USER_PROMPT = """\
Extract from this job description and return as JSON with exactly these keys:
job_title, required_skills (array), preferred_skills (array),
experience_required, education_required,
key_responsibilities (array), keywords (array).
 
Rules:
- required_skills: explicitly required / must-have.
- preferred_skills: nice-to-have / preferred.
- keywords: ALL important ATS-matching terms.
- Return ONLY raw JSON. No markdown.
 
Job Description:
{raw_text}"""

# helpers
def _cache_key(prefix:str, text:str)->str:
    return hashlib.sha256(f"{prefix}:{text[:MAX_INPUT_CHARS]}".encode()).hexdigest()

def _call_groq(system_prompt: str, user_prompt: str) -> str:
    client = _get_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.0,
        max_tokens=MAX_TOKENS,
    )
    return response.choices[0].message.content.strip()

def _try_parse_json(text: str) -> dict | None:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        first_newline = cleaned.find("\n")
        cleaned = cleaned[first_newline + 1:] if first_newline != -1 else cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None
    
def _call_with_retry(system_prompt: str, user_prompt: str) -> dict:
    raw = _call_groq(system_prompt, user_prompt)
    result = _try_parse_json(raw)
    if result is not None:
        return result
    
    logger.warning("Groq: first attempt returned invalid JSON - retrying…")
    strict_prompt = (
        "Your previous response was not valid JSON. "
        "Return ONLY the raw JSON object with no markdown or explanation.\n\n"
        + user_prompt
    )
    raw = _call_groq(system_prompt, strict_prompt)
    result = _try_parse_json(raw)
    if result is not None:
        return result
 
    raise ValueError(
        f"Groq returned unparseable JSON after retry. Preview:\n{raw[:400]}"
    )
    
# public api

def parse_resume(raw_text:str)->Dict:
    text = raw_text[:MAX_INPUT_CHARS]
    key = _cache_key("resume", text)
    
    if key in _PARSE_CACHE:
        logger.info("parse_resume: cache hit - skipping Groq call")
        return _PARSE_CACHE[key]
    
    prompt = RESUME_USER_PROMPT.format(raw_text=text)
    result = _validate_resume_result(_call_with_retry(RESUME_SYSTEM_PROMPT, prompt))
    with _CACHE_LOCK:
        _PARSE_CACHE[key] = result
        _save_disk_cache(_PARSE_CACHE)
    return result

def parse_job_description(raw_text: str) -> Dict:
    text = raw_text[:MAX_INPUT_CHARS]
    key  = _cache_key("jd", text)
 
    if key in _PARSE_CACHE:
        logger.info("parse_job_description: cache hit - skipping Groq call")
        return _PARSE_CACHE[key]
 
    prompt = JD_USER_PROMPT.format(raw_text=text)
    result = _validate_jd_result(_call_with_retry(JD_SYSTEM_PROMPT, prompt))
    with _CACHE_LOCK:
        _PARSE_CACHE[key] = result
        _save_disk_cache(_PARSE_CACHE)
    return result

# ── validators ────────────────────────────────────────────────────────────────
 
def _validate_resume_result(result: dict | None) -> dict:
    if result is None:
        result = {}
    defaults = {
        "name": "", "email": None, "phone": None,
        "linkedin": None, "github": None,
        "professional_summary": "",
        "skills": [], "experience": [], "education": [],
        "certifications": [], "projects": [],
        "action_verbs": [], "keywords": [],
    }
    for key, default in defaults.items():
        if key not in result or result[key] is None:
            result[key] = default
        if isinstance(default, list) and not isinstance(result[key], list):
            result[key] = default
 
    for exp in result.get("experience", []):
        if not isinstance(exp, dict):
            continue
        exp.setdefault("job_title", "")
        exp.setdefault("company", "")
        exp.setdefault("start_date", "")
        exp.setdefault("end_date", "")
        exp.setdefault("duration_months", 0)
        exp.setdefault("description", "")
        try:
            exp["duration_months"] = int(exp["duration_months"])
        except (ValueError, TypeError):
            exp["duration_months"] = 0
 
    for proj in result.get("projects", []):
        if not isinstance(proj, dict):
            continue
        proj.setdefault("title", "")
        proj.setdefault("description", "")
        proj.setdefault("technologies", [])
 
    return result
 
 
def _validate_jd_result(result: dict | None) -> dict:
    if result is None:
        result = {}
    defaults = {
        "job_title": "",
        "required_skills": [],
        "preferred_skills": [],
        "experience_required": "",
        "education_required": "",
        "key_responsibilities": [],
        "keywords": [],
    }
    for key, default in defaults.items():
        if key not in result or result[key] is None:
            result[key] = default
        if isinstance(default, list) and not isinstance(result[key], list):
            result[key] = default