import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from backend.core.logger import setup_logger 
from backend.core.config import (
    ALLOWED_ORIGINS,
    APP_TITLE,
    SENTENCE_TRANSFORMER_MODEL,
    SPACY_MODEL_PRIMARY,
    SPACY_MODEL_SECONDARY,
)
from backend.api.routes import router

logger = setup_logger("ats_resume_scorer | backend main")

BASE_DIR      = Path(__file__).resolve().parent
PROJECT_ROOT  = BASE_DIR.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR    = PROJECT_ROOT / "frontend" / "static"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting ATS Resume Analyser API v2…")

    # spaCy
    import spacy
    try:
        app.state.nlp = spacy.load(SPACY_MODEL_PRIMARY)
        logger.info("Loaded spaCy: %s", SPACY_MODEL_PRIMARY)
    except OSError:
        logger.warning("%s not found - falling back to %s", SPACY_MODEL_PRIMARY, SPACY_MODEL_SECONDARY)
        app.state.nlp = spacy.load(SPACY_MODEL_SECONDARY)

    # MiniLM — skill-level matching
    from sentence_transformers import SentenceTransformer
    app.state.embedder = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
    logger.info("Loaded embedder: %s", SENTENCE_TRANSFORMER_MODEL)

    # Fine-tuned BERT — document-level JD matching (warm singleton)
    from backend.services.bert_matcher import _load_model, get_model_info
    _load_model()
    info = get_model_info()
    if info["using_finetuned"]:
        logger.info(
            "Fine-tuned BERT ready | MAE %.4f → %.4f (+%.1f%%)",
            info["base_mae"], info["finetuned_mae"], info["improvement_pct"],
        )
    else:
        logger.warning("Fine-tuned BERT absent - using base %s", info["model_path"])

    logger.info("All models loaded. API ready.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title    = APP_TITLE,
    version  = "2.0.0",
    lifespan = lifespan,
    docs_url = "/docs",
    redoc_url= "/redoc",
)

# ── Static files (/static/css/style.css, etc.) ────────────────────────────────
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ALLOWED_ORIGINS,
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

app.include_router(router)


@app.get("/")
async def root():
    from backend.services.bert_matcher import get_model_info
    info = get_model_info()
    return {
        "name":    "ATS Resume Analyser API",
        "version": "2.0.0",
        "models": {
            "skill_embedder": SENTENCE_TRANSFORMER_MODEL,
            "jd_matcher": (
                f"fine-tuned all-mpnet-base-v2 (MAE {info.get('finetuned_mae')}, +{info.get('improvement_pct')}%)"
                if info.get("using_finetuned")
                else "base all-mpnet-base-v2 (fine-tuned not found)"
            ),
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
    
    
    
    
## to run backend : uvicorn backend.main:app --reload