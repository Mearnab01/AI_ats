from __future__ import annotations

from io import BytesIO
from typing import Any, Dict, List

import requests

_BASE = "http://localhost:8000/api/v1"
_TIMEOUT = 60


def _headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"} if token else {}


def analyze_resume(
    file,
    job_description: str = "",
    access_token: str    = "",
) -> Dict[str, Any]:
    """
    POST /api/v1/analyze-resume
    
    """
    file_bytes = file.read() if hasattr(file, "read") else file
    file_name  = getattr(file, "name", "resume.pdf")

    resp = requests.post(
        f"{_BASE}/analyze-resume",
        headers = _headers(access_token),
        files   = {"resume": (file_name, BytesIO(file_bytes), "application/octet-stream")},
        data    = {"job_description": job_description or ""},
        timeout = _TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()

def validate_document(file, access_token: str = "") -> Dict[str, Any]:
    """POST /api/v1/validate-document"""
    file_bytes = file.read() if hasattr(file, "read") else file
    file_name  = getattr(file, "name", "upload.pdf")
 
    if hasattr(file, "seek"):
        file.seek(0)
 
    resp = requests.post(
        f"{_BASE}/validate-document",
        headers = _headers(access_token),
        files   = {"resume": (file_name, BytesIO(file_bytes), "application/octet-stream")},
        timeout = 30,
    )
    resp.raise_for_status()
    return resp.json()

def get_jobs(
    query:        str = "",
    location:     str = "India",
    access_token: str = "",
) -> Dict[str, Any]:
    """GET /api/v1/jobs"""
    resp = requests.get(
        f"{_BASE}/jobs",
        headers = _headers(access_token),
        params  = {"query": query, "location": location},
        timeout = 250,
    )
    resp.raise_for_status()
    return resp.json()

def get_history(access_token: str) -> List[Dict[str, Any]]:
    """GET /api/v1/history"""
    resp = requests.get(
        f"{_BASE}/history",
        headers = _headers(access_token),
        timeout = _TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def delete_history(analysis_id: str, access_token: str) -> None:
    """DELETE /api/v1/history/{analysis_id}"""
    resp = requests.delete(
        f"{_BASE}/history/{analysis_id}",
        headers = _headers(access_token),
        timeout = _TIMEOUT,
    )
    resp.raise_for_status()

def download_history_pdf(analysis_id: str, access_token: str) -> bytes:
    """GET /api/v1/history/{analysis_id}/pdf"""
    resp = requests.get(
        f"{_BASE}/history/{analysis_id}/pdf",
        headers = _headers(access_token),
        timeout = _TIMEOUT,
    )
    resp.raise_for_status()
    return resp.content

def get_health() -> Dict[str, Any]:
    """GET /api/v1/health — returns model status."""
    resp = requests.get(f"{_BASE}/health", timeout=10)
    resp.raise_for_status()
    return resp.json()