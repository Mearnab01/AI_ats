## need changes
## 1. write this then go to jd_matcher.py

from __future__ import annotations
import json
import os
import streamlit as st
import numpy as np
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional
from backend.core.logger import setup_logger
from sentence_transformers import SentenceTransformer


logger = setup_logger("ats_resume_scorer | bert_matcher")

_PROJECT_ROOT    = Path(__file__).resolve().parents[2]
_FINETUNED_PATH  = _PROJECT_ROOT / "ml model" / "models" / "finetuned-bert"
_METADATA_PATH   = _FINETUNED_PATH / "metadata.json"
_FALLBACK_MODEL  = "all-mpnet-base-v2"

_CHUNK_SIZE    = 1_500   # chars ≈ 375 tokens, well within 512
_CHUNK_OVERLAP = 200

@st.cache_resource(show_spinner=False)
def _load_model() -> tuple[SentenceTransformer, bool, dict]:
    if _FINETUNED_PATH.exists():
        try:
            model    = SentenceTransformer(str(_FINETUNED_PATH))
            metadata = {}
            if _METADATA_PATH.exists():
                with open(_METADATA_PATH) as f:
                    metadata = json.load(f)
            logger.info(
                "Fine-tuned BERT loaded from %s | MAE %.4f → %.4f (+%.1f%%)",
                _FINETUNED_PATH,
                metadata.get("base_mae", "?"),
                metadata.get("finetuned_mae", "?"),
                metadata.get("improvement_pct", "?"),
            )
            return model, True, metadata
        except Exception as exc:
            logger.warning("Fine-tuned model load failed (%s) - falling back to %s", exc, _FALLBACK_MODEL)
 
    model = SentenceTransformer(_FALLBACK_MODEL)
    logger.warning(
        "Fine-tuned model not found at '%s'. "
        "Using base %s. Run Notebook 03 and save to 'ml model/finetuned-bert/' "
        "to enable the fine-tuned scorer.",
        _FINETUNED_PATH,
        _FALLBACK_MODEL,
    )
    return model, False, {}



def get_model_info() -> dict:
    """Return metadata about which model is active. Safe to call any time."""
    _, using_finetuned, metadata = _load_model()
    return {
        "using_finetuned":  using_finetuned,
        "model_path":       str(_FINETUNED_PATH) if using_finetuned else _FALLBACK_MODEL,
        "base_mae":         metadata.get("base_mae"),
        "finetuned_mae":    metadata.get("finetuned_mae"),
        "improvement_pct":  metadata.get("improvement_pct"),
        "trained_on_pairs": metadata.get("total_pairs"),
    }


@st.cache_resource(show_spinner=False)
def _encode_cached(text: str, model_id: int) -> tuple:
    model, _, _ = _load_model()
    vec = model.encode(text, convert_to_tensor=False, normalize_embeddings=True)
    return tuple(vec.tolist())
 
 
def _encode(text: str) -> np.ndarray:
    model, _, _ = _load_model()
    tup = _encode_cached(text, id(model))
    return np.array(tup, dtype=np.float32)
 
 
def _encode_chunked(text: str) -> np.ndarray:
    """
    Sliding-window mean-pool for texts longer than _CHUNK_SIZE.
    Prevents silent truncation at the model's token limit.
    """
    if len(text) <= _CHUNK_SIZE:
        return _encode(text)
 
    step   = _CHUNK_SIZE - _CHUNK_OVERLAP
    chunks = [
        text[s: s + _CHUNK_SIZE]
        for s in range(0, len(text), step)
        if text[s: s + _CHUNK_SIZE].strip()
    ]
    if not chunks:
        return _encode(text[:_CHUNK_SIZE])
 
    vecs = np.stack([_encode(c) for c in chunks])
    pooled = vecs.mean(axis=0)
    # Re-normalise after averaging
    norm = np.linalg.norm(pooled)
    return pooled / norm if norm > 0 else pooled
 
 
def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.clip(np.dot(a, b) / denom, 0.0, 1.0)) if denom > 0 else 0.0
 
 
# ── public API ────────────────────────────────────────────────────────────────
 
def score_resume_jd(resume_text: str, jd_text: str) -> Dict:
    _, using_finetuned, _ = _load_model()
 
    resume_vec = _encode_chunked(resume_text[:8_000])
    jd_vec     = _encode_chunked(jd_text[:8_000])
    score      = _cosine(resume_vec, jd_vec)
 
    if score >= 0.75:
        band, confidence = "high",   "strong"
    elif score >= 0.55:
        band, confidence = "high",   "moderate"
    elif score >= 0.40:
        band, confidence = "medium", "moderate"
    elif score >= 0.25:
        band, confidence = "medium", "weak"
    else:
        band, confidence = "low",    "strong"
 
    return {
        "semantic_score":   round(score, 4),
        "match_band":       band,
        "confidence":       confidence,
        "using_finetuned":  using_finetuned,
        "model_info":       get_model_info(),
    }
 
 
def batch_score(
    resume_text: str,
    jd_texts:    list[str],
) -> list[Dict]:
    """
    Score one resume against multiple JDs.
    Useful for a future "best-fit JD" feature.
    """
    resume_vec = _encode_chunked(resume_text[:8_000])
    results    = []
    for jd in jd_texts:
        jd_vec = _encode_chunked(jd[:8_000])
        score  = _cosine(resume_vec, jd_vec)
        results.append({"jd_preview": jd[:80], "semantic_score": round(score, 4)})
    return sorted(results, key=lambda x: x["semantic_score"], reverse=True)
 