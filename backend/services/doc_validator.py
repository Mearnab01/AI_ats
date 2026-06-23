"""
doc_validator.py
================
Preprocessing gate — run BEFORE ATS analysis.

Classifies the uploaded document and blocks non-resumes.
No ML model required; pure regex + weighted signal scoring.
Fast: ~5-20 ms per document.

Usage
-----
from backend.services.doc_validator import validate_document

result = validate_document(text)
# result = {
#     "is_resume": True,
#     "document_type": "Resume",
#     "confidence": 91,
#     "reasoning": ["Has email contact", "Has work experience section", ...]
# }
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple

# ── Signal tables ──────────────────────────────────────────────────────────────

# Each signal: (regex_pattern, weight, reason_label)
# Positive weight → resume evidence
# Used by type detectors with their own negative weights

_RESUME_SIGNALS: List[Tuple[str, int, str]] = [
    # Contact
    (r"\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b",                                   10, "Has email address"),
    (r"\b(\+91[\-\s]?)?\d{10}\b|\b\d{3}[\-\s]\d{3}[\-\s]\d{4}\b",         8,  "Has phone number"),
    (r"linkedin\.com/in/\S+",                                             7,  "Has LinkedIn profile"),
    (r"github\.com/\S+",                                                  6,  "Has GitHub profile"),
    (r"\bportfolio\b|\bpersonal\s+website\b",                             4,  "Has portfolio link"),

    # Sections
    (r"(?i)^\s*(work\s+)?experience\s*$",                                   12, "Has work experience section"),
    (r"(?i)^\s*(technical\s+)?skills?\s*$",                                 10, "Has skills section"),
    (r"(?i)^\s*education\s*$",                                               9, "Has education section"),
    (r"(?i)^\s*projects?\s*$",                                               8, "Has projects section"),
    (r"(?i)^\s*(professional\s+)?summary\b",                                 7, "Has professional summary"),
    (r"(?i)^\s*certifications?\s*$",                                         6, "Has certifications section"),
    (r"(?i)^\s*internships?\s*$",                                            7, "Has internships section"),
    (r"(?i)^\s*achievements?\s*$",                                           5, "Has achievements section"),
    (r"(?i)^\s*(career\s+)?objective\s*$",                                   6, "Has career objective"),
    (r"(?i)^\s*(hobbies|interests)\s*$",                                     3, "Has interests section"),

    # Career indicators
    (r"(?i)\b(software\s+engineer|data\s+scientist|product\s+manager|"
     r"developer|analyst|consultant|designer|architect|manager|intern)\b",    7, "Has job title keywords"),
    (r"(?i)\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{4}\b", 6, "Has employment dates"),
    (r"(?i)\b(present|current|till\s+date|to\s+date)\b",                      5, "Has current employment indicator"),
    (r"(?i)\b(cgpa|gpa|percentage|grade|semester|batch)\b",                   5, "Has academic performance metric"),
    (r"(?i)\b(b\.?tech|m\.?tech|b\.?e|m\.?e|bca|mca|b\.?sc|m\.?sc|"
     r"bachelor|master|phd|diploma)\b",                                       6, "Has degree qualification"),
]

_ACADEMIC_SIGNALS: List[Tuple[str, int, str]] = [
    (r"(?i)\bunit\s*[--]\s*\d+\b",                                          10, "Contains unit chapters"),
    (r"(?i)\bchapter\s*[--:]\s*\d+\b",                                       9, "Contains chapter markers"),
    (r"(?i)\blecture\s*(notes?)?\s*\d*\b",                                   9, "Contains lecture notes"),
    (r"(?i)\b(operating\s+system|dbms|compiler\s+design|data\s+structures|"
    r"computer\s+networks|mathematics|physics|chemistry|biology)\b",         8, "Academic subject terminology"),
    (r"(?i)\b(tutorial|worksheet|exercise|assignment\s+\d+)\b",               7, "Academic exercise indicators"),
    (r"(?i)\b(theorem|corollary|lemma|proof|derivation)\b",                   8, "Mathematical/theoretical content"),
    (r"(?i)\bsyllabus\b|\bcurriculum\b|\bcourse\s+code\b",                    9, "Course/syllabus structure"),
]

_RESEARCH_SIGNALS: List[Tuple[str, int, str]] = [
    (r"(?i)^\s*abstract\s*$",                                         12, "Has abstract section"),
    (r"(?i)^\s*references?\s*$",                                      10, "Has references section"),
    (r"(?i)^\s*(literature\s+review|related\s+work)\s*$",             10, "Has literature review"),
    (r"(?i)^\s*methodology\s*$",                                      9, "Has methodology section"),
    (r"(?i)\b(doi:|arxiv:|ieee|springer|elsevier|acm)\b",             8, "Academic publisher reference"),
    (r"(?i)\bet\s+al\.",                                              7, "Uses 'et al.' citation"),
    (r"(?i)\b(hypothesis|experimental\s+results?|conclusion)\b",      6, "Research paper structure"),
]

_INVOICE_SIGNALS: List[Tuple[str, int, str]] = [
    (r"(?i)\binvoice\s*(no\.?|number|#)?\s*[\d-]+\b",                15, "Has invoice number"),
    (r"(?i)\b(gst|vat|tax)\s*(no\.?|number|%)?\s*[\w-]*\b",          12, "Has GST/tax reference"),
    (r"(?i)\bbill\s+to\b|\bship\s+to\b",                             10, "Has billing address"),
    (r"(?i)\b(subtotal|grand\s+total|amount\s+due)\b",               10, "Has financial totals"),
    (r"(?i)\b(quantity|unit\s+price|line\s+item)\b",                 8, "Has item pricing structure"),
]

_CERTIFICATE_SIGNALS: List[Tuple[str, int, str]] = [
    (r"(?i)\bcertificate\s+of\s+(completion|achievement|participation)\b",  15, "Certificate of completion"),
    (r"(?i)\bawarded\s+to\b|\bpresented\s+to\b",                            12, "Award presentation language"),
    (r"(?i)\bissued\s+by\b|\bauthorized\s+by\b|\bsigned\s+by\b",            9, "Has issuing authority"),
    (r"(?i)\bthis\s+is\s+to\s+certify\b",                                   10, "Certification language"),
    (r"(?i)\bvalid\s+(till|until|through)\b",                                 7, "Has validity period"),
]

_BOOK_SIGNALS: List[Tuple[str, int, str]] = [
    (r"(?i)^\s*table\s+of\s+contents?\s*$",                                 12, "Has table of contents"),
    (r"(?i)^\s*foreword\s*$|^\s*preface\s*$",                               10, "Has foreword/preface"),
    (r"(?i)\bchapter\s+\d+\s*[:\-]",                                        8, "Has numbered chapters"),
    (r"(?i)\bfirst\s+edition\b|\bsecond\s+edition\b|\bpublished\s+by\b",    9, "Has publication metadata"),
]

_PRESENTATION_SIGNALS: List[Tuple[str, int, str]] = [
    (r"(?i)\bslide\s+\d+\b|\bpage\s+\d+\s+of\s+\d+\b",                     10, "Has slide numbering"),
    (r"(?i)\b(agenda|overview|key\s+takeaways|thank\s+you)\b",                6, "Presentation structure keywords"),
    (r"(?i)\bpresented\s+by\b",                                               8, "Has presenter attribution"),
]


# ── Scorer ─────────────────────────────────────────────────────────────────────

def _score_signals(
    text: str,
    signals: List[Tuple[str, int, str]],
    multiline: bool = True,
) -> Tuple[int, List[str]]:
    """Return (total_score, list_of_triggered_reasons)."""
    flags   = re.MULTILINE if multiline else 0
    score   = 0
    reasons = []
    for pattern, weight, label in signals:
        if re.search(pattern, text, flags):
            score += weight
            reasons.append(label)
    return score, reasons


def _classify(text: str) -> Dict:
    """
    Run all signal groups and return the best classification.
    """
    resume_score,       resume_reasons       = _score_signals(text, _RESUME_SIGNALS)
    academic_score,     academic_reasons     = _score_signals(text, _ACADEMIC_SIGNALS)
    research_score,     research_reasons     = _score_signals(text, _RESEARCH_SIGNALS)
    invoice_score,      invoice_reasons      = _score_signals(text, _INVOICE_SIGNALS)
    certificate_score,  certificate_reasons  = _score_signals(text, _CERTIFICATE_SIGNALS)
    book_score,         book_reasons         = _score_signals(text, _BOOK_SIGNALS)
    presentation_score, presentation_reasons = _score_signals(text, _PRESENTATION_SIGNALS)

    # Non-resume winner
    contenders = [
        (academic_score,     "Academic Notes",  academic_reasons),
        (research_score,     "Research Paper",  research_reasons),
        (invoice_score,      "Invoice",         invoice_reasons),
        (certificate_score,  "Certificate",     certificate_reasons),
        (book_score,         "Book",            book_reasons),
        (presentation_score, "Presentation",    presentation_reasons),
    ]
    best_nonresume_score, best_nonresume_type, best_nonresume_reasons = max(
        contenders, key=lambda x: x[0]
    )

    # Decision logic
    # Resume must hit a minimum absolute score AND beat best non-resume type
    RESUME_MIN        = 20   # at least 20 pts of resume evidence
    NONRESUME_THRESH  = 20   # non-resume type must reach 20 pts to override

    is_resume = (
        resume_score >= RESUME_MIN
        and (resume_score >= best_nonresume_score * 1.2 or best_nonresume_score < NONRESUME_THRESH)
    )

    if is_resume:
        # Confidence scales with resume score; cap at 98
        confidence  = min(98, int(50 + resume_score * 1.5))
        doc_type    = "Resume"
        reasoning   = resume_reasons
    else:
        if best_nonresume_score < 10:
            doc_type   = "Unknown"
            confidence = max(30, min(60, best_nonresume_score * 3))
        else:
            doc_type   = best_nonresume_type
            confidence = min(97, int(40 + best_nonresume_score * 2))
        reasoning = best_nonresume_reasons

        # Mention absence of resume signals in reasoning
        if resume_score < RESUME_MIN:
            missing = []
            if not re.search(r"\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b", text):
                missing.append("No contact information detected")
            if not re.search(r"(?i)^\s*(work\s+)?experience\s*$", text, re.MULTILINE):
                missing.append("No work experience section")
            if not re.search(r"(?i)^\s*(technical\s+)?skills?\s*$", text, re.MULTILINE):
                missing.append("No skills section")
            reasoning = missing + reasoning

    return {
        "is_resume":     is_resume,
        "document_type": doc_type,
        "confidence":    confidence,
        "reasoning":     reasoning[:6],   # top 6 reasons
        "_debug": {
            "resume_score":       resume_score,
            "best_nonresume":     best_nonresume_type,
            "best_nonresume_score": best_nonresume_score,
        },
    }


# ── Public API ─────────────────────────────────────────────────────────────────

def validate_document(text: str) -> Dict:
    """
    Main entry point.

    Parameters
    ----------
    text : str
        Extracted plain text from the uploaded file.

    Returns
    -------
    dict with keys:
        is_resume     : bool
        document_type : str   ("Resume" | "Academic Notes" | "Research Paper" | ...)
        confidence    : int   (0-100)
        reasoning     : List[str]
    """
    if not text or len(text.strip()) < 50:
        return {
            "is_resume":     False,
            "document_type": "Unknown",
            "confidence":    0,
            "reasoning":     ["Document is empty or too short to classify"],
        }

    result = _classify(text)
    # Remove internal debug key from public output
    result.pop("_debug", None)
    return result