from __future__ import annotations

import numpy as np
import spacy
from typing import List, Dict

from rapidfuzz import fuzz

from backend.utils.matching import fuzzy_match_keywords, normalize_skill
from backend.services.bert_matcher import score_resume_jd


def identify_matched_keywords(
    resume_keywords: List[str],
    jd_keywords:     List[str],
) -> List[str]:
    return fuzzy_match_keywords(resume_keywords, jd_keywords, threshold=80)["matched"]


def identify_missing_keywords(
    resume_keywords: List[str],
    jd_keywords:     List[str],
    top_n: int = 15,
) -> List[str]:
    return fuzzy_match_keywords(resume_keywords, jd_keywords, threshold=80)["missing"][:top_n]


def analyze_skills_gap(
    resume_skills: List[str],
    jd_text:       str,
    nlp:           spacy.Language,
) -> List[str]:
    doc       = nlp(jd_text[:5_000])
    jd_skills: set[str] = set()

    for ent in doc.ents:
        if ent.label_ in ("PRODUCT", "ORG", "LANGUAGE"):
            val = ent.text.lower().strip()
            if len(val) > 2:
                jd_skills.add(val)

    for chunk in doc.noun_chunks:
        ct = chunk.text.lower().strip()
        if len(ct) > 2 and not chunk.root.is_stop and 1 <= len(ct.split()) <= 4:
            jd_skills.add(ct)

    resume_normalized = {normalize_skill(s) for s in resume_skills}

    gap: list[str] = []
    for jd_skill in jd_skills:
        jd_norm = normalize_skill(jd_skill)
        if jd_norm in resume_normalized:
            continue
        best = max(
            (fuzz.token_sort_ratio(jd_norm, rs) for rs in resume_normalized),
            default=0,
        )
        if best < 75:
            gap.append(jd_skill)

    return sorted(gap)[:20]


def calculate_match_percentage(
    resume_keywords:     List[str],
    jd_keywords:         List[str],
    semantic_score:      float,
) -> float:
    if not jd_keywords:
        return 0.0
    matched     = identify_matched_keywords(resume_keywords, jd_keywords)
    keyword_pct = len(matched) / len(jd_keywords)
    # 60% keyword overlap + 40% semantic similarity (same weights as before)
    return float(np.clip((keyword_pct * 0.6 + semantic_score * 0.4) * 100, 0.0, 100.0))


def compare_resume_with_jd(
    resume_text:     str,
    resume_keywords: List[str],
    resume_skills:   List[str],
    jd_text:         str,
    jd_keywords:     List[str],
    embedder,        # kept for API compatibility; not used (BERT matcher is self-contained)
    nlp:             spacy.Language,
) -> Dict:
    bert_result      = score_resume_jd(resume_text, jd_text)
    semantic_score   = bert_result["semantic_score"]

    matched_keywords = identify_matched_keywords(resume_keywords, jd_keywords)
    missing_keywords = identify_missing_keywords(resume_keywords, jd_keywords)
    skills_gap       = analyze_skills_gap(resume_skills, jd_text, nlp)
    match_percentage = calculate_match_percentage(resume_keywords, jd_keywords, semantic_score)

    return {
        "match_percentage":    round(match_percentage, 1),
        "semantic_similarity": semantic_score,
        "match_band":          bert_result["match_band"],
        "matched_keywords":    matched_keywords,
        "missing_keywords":    missing_keywords,
        "skills_gap":          skills_gap,
        "model_info":          bert_result["model_info"],
    }