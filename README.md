# AI Resume ATS Scorer

An end-to-end ATS (Applicant Tracking System) resume analyser built with a multi-layer NLP pipeline. Parses, scores, and improves resumes against job descriptions using a combination of fine-tuned BERT, spaCy NER, semantic embeddings, and LLM-based extraction.

---

## Links

| Resource | Link |
|-----------|-----------|
| 🚀 Live Demo | https://thunder421-criterion-by-arnab1028.hf.space |
| 📊 Dataset | https://www.kaggle.com/datasets/arnabnath8201/resume-jd |
| 🤗 Fine-Tuned Model | https://huggingface.co/Thunder421/criterion-finetuned-bert |

> Streamlit frontend · FastAPI backend · Supabase auth + storage · Apify

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Streamlit Frontend                        │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP
┌────────────────────────────▼────────────────────────────────────┐
│                     FastAPI Backend (async)                       │
│                                                                   │
│  ┌──────────────┐   ┌─────────────────┐   ┌──────────────────┐  │
│  │ resume_parser│   │  groq_parser.py │   │  bert_matcher.py │  │
│  │ pdfplumber   │──▶│  Groq LLaMA-3.3 │   │  fine-tuned      │  │
│  │ python-docx  │   │  structured JSON│   │  all-mpnet-base  │  │
│  └──────────────┘   └────────┬────────┘   └────────┬─────────┘  │
│                              │                     │             │
│  ┌───────────────────────────▼─────────────────────▼──────────┐ │
│  │                   resume_analyzer.py                        │ │
│  │   asyncio.gather() – Groq calls run concurrently            │ │
│  │   ThreadPoolExecutor – CPU NLP off event loop               │ │
│  └──────┬──────────────────────┬────────────────────┬─────────┘ │
│         │                      │                    │            │
│  ┌──────▼──────┐  ┌────────────▼──────┐  ┌─────────▼─────────┐ │
│  │ ats_scorer  │  │   jd_matcher      │  │  feedback_engine  │ │
│  │ spaCy NER   │  │   bert_matcher    │  │  recommendation   │ │
│  │ rapidfuzz   │  │   keyword fuzzy   │  │  engine           │ │
│  │ MiniLM emb  │  │   skills gap NLP  │  │                   │ │
│  └─────────────┘  └───────────────────┘  └───────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                             │
              ┌──────────────▼──────────────┐
              │     Supabase                 │
              │     Auth (Google OAuth)      │
              │     Analysis history         │
              └─────────────────────────────┘
```

---

## Why multiple models instead of just calling GPT?

Each sub-problem in ATS scoring has a different best tool:

| Sub-task                                         | Tool                         | Why                                                                      |
| ------------------------------------------------ | ---------------------------- | ------------------------------------------------------------------------ |
| Structured extraction (name, skills, experience) | Groq / LLaMA-3.3-70B         | LLMs are best at understanding unstructured resume formats               |
| Document-level JD semantic match                 | Fine-tuned all-mpnet-base-v2 | Trained directly on resume–JD pairs; 70% MAE improvement over GPT cosine |
| Skill-level matching (skill vs project text)     | MiniLM-L6-v2 + LRU cache     | Faster on short strings; skill matching is retrieval not regression      |
| Named entity recognition (location, orgs)        | spaCy en_core_web_lg         | Rule-based NER is faster and more reliable than LLM for this task        |
| Keyword fuzzy matching                           | rapidfuzz                    | Handles abbreviations ("ML" vs "Machine Learning") without LLM overhead  |

---

## The Fine-Tuned BERT Model

### What problem it solves

General-purpose sentence encoders like `all-mpnet-base-v2` are trained on diverse internet text. When asked to measure similarity between a resume and a job description, they have no domain knowledge — they don't know that "Python Developer 6 years FastAPI" should score high against "Senior Python Engineer – FastAPI required" but low against "DevOps Engineer – Kubernetes required."

### How it was trained

|            |                                                                                   |
| ---------- | --------------------------------------------------------------------------------- |
| Base model | `all-mpnet-base-v2` (22.7M params, 768-dim embeddings)                            |
| Dataset    | 266 resume–JD pairs with human-labelled match scores (0.0–1.0)                    |
| Labels     | high (≥0.75), medium (0.40–0.74), low (<0.40) — balanced across all splits        |
| Loss       | `CosineSimilarityLoss` — trains cosine(embed(resume), embed(jd)) ≈ match_score    |
| Epochs     | 10, batch size 16, warmup 10%                                                     |
| Evaluation | `EmbeddingSimilarityEvaluator` on val set after each epoch; best checkpoint saved |

**Training → evaluation split:** 186 train / 40 val / 40 test (stratified by label)

### Results

```
Base model (all-mpnet-base-v2)   MAE: 0.1562   RMSE: 0.1791
Fine-tuned model                 MAE: 0.0468   RMSE: 0.0665
                                 ──────────────────────────
Improvement                           70.0%         62.8%
```

Production test (3 hand-crafted cases):

| Case                           | Expected | Predicted score | Band     |
| ------------------------------ | -------- | --------------- | -------- |
| Python dev → Python SWE role   | HIGH     | 0.7925          | HIGH ✓   |
| Python dev → Data Analyst role | MEDIUM   | 0.6910          | MEDIUM ✓ |
| Event manager → DevOps role    | LOW      | 0.0359          | LOW ✓    |

### Why not use it for skill-level matching too?

The fine-tuned model was trained on full document pairs (whole resume vs whole JD). Skill-level matching compares short strings like `"React"` against `"Built dashboard using React and D3"` — a different task and input distribution. MiniLM-L6-v2 handles this better and is significantly faster on short inputs.

### Where is the model used?

`backend/services/bert_matcher.py` → called by `jd_matcher.compare_resume_with_jd()` for the semantic similarity component of the JD match score.

The `GET /api/v1/health` endpoint reports whether the fine-tuned model is active along with its MAE metrics.

---

## Scoring Model

Overall score is a weighted blend of five components (max 100):

| Component         | Weight | What it measures                           |
| ----------------- | ------ | ------------------------------------------ |
| Keywords & Skills | 40%    | Keyword coverage + JD fuzzy match          |
| Content Quality   | 30%    | Action verbs + quantifiable achievements   |
| Formatting        | 15%    | Section presence, bullet point density     |
| ATS Compatibility | 15%    | Clean structure, no special chars, privacy |

**Skill validation bonus:** up to +2 points when ≥80% of listed skills are backed by evidence in the Projects or Experience sections (checked via MiniLM semantic similarity, not exact string match — catches "React" validated by "built UI with ReactJS").

**Privacy penalty:** up to -5 points for full street addresses or zip codes in the resume (ATS systems don't need these; they can cause parsing failures in some ATS implementations).

---

## Project Structure

```
ai-resume-ats/
├── backend/
│   ├── api/
│   │   ├── auth.py              # Supabase JWT verification (HS256 + JWKS)
│   │   └── routes.py            # FastAPI routes
│   ├── core/
│   │   └── config.py            # Environment config
│   ├── database/
│   │   └── supabase_db.py       # History persistence
│   ├── models/
│   │   └── schemas.py           # Pydantic request/response models
│   ├── services/
│   │   ├── bert_matcher.py      # Fine-tuned BERT – JD semantic matching ⭐
│   │   ├── ats_scorer.py        # Rule-based scoring pipeline
│   │   ├── feedback_engine.py   # Issue detection and analysis
│   │   ├── groq_parser.py       # LLM structured extraction (Groq/LLaMA)
│   │   ├── jd_matcher.py        # Resume ↔ JD comparison
│   │   ├── recommendation_engine.py
│   │   ├── report_generator.py  # HTML/PDF report generation
│   │   ├── resume_analyzer.py   # Main orchestration (async)
│   │   └── resume_parser.py     # PDF/DOCX text extraction
│   ├── utils/
│   │   ├── file_utils.py
│   │   └── matching.py          # rapidfuzz keyword utilities
│   └── main.py                  # FastAPI app + model warm-up
│
├── ml model/
│   └── finetuned-bert/          # Fine-tuned model artefacts (not in git)
│       ├── config.json
│       ├── model.safetensors
│       ├── tokenizer_config.json
│       └── metadata.json        # Training metrics
│
├── jupyter notebooks/
│   ├── 01_EDA_and_DATA_prep.ipynb      # Dataset analysis + cleaning
│   ├── 02_BERT_EMBEDDINGS.ipynb        # Embedding analysis + baseline eval
│   └── 03_BERT_FINETUNEipynb.ipynb     # Fine-tuning + evaluation
│
├── frontend/                    # Streamlit UI
├── requirements.txt
└── .env.example
```

---

## Setup

### Prerequisites

- Python 3.11+
- Groq API key (free tier works)
- Supabase project (free tier works)

### Install

```bash
git clone https://github.com/your-username/ai-resume-ats.git
cd ai-resume-ats
pip install -r requirements.txt
python -m spacy download en_core_web_lg
```

### Environment variables

Copy `.env.example` to `.env` and fill in:

```env
GROQ_API_KEY=your_groq_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_JWT_SECRET=your_jwt_secret
```

### Fine-tuned model

The fine-tuned model artefacts are not committed to git (438 MB). To use them:

**Option A – Run Notebook 03 yourself:**

```bash
cd "jupyter notebooks"
jupyter notebook 03_BERT_FINETUNEipynb.ipynb
# Run all cells. Model saves to ml model/finetuned-bert/
```

**Option B – Use the base model (automatic fallback):**
The app works without the fine-tuned model. It falls back to the base `all-mpnet-base-v2` automatically. The `/health` endpoint will report `"active": false` for the BERT scorer.

### Run

```bash
# Backend
uvicorn backend.main:app --reload --port 8000

# Frontend (separate terminal)
streamlit run frontend/app.py
```

---

## API

```
POST /api/v1/analyze-resume    Upload resume + optional JD text
GET  /api/v1/history           User analysis history
DELETE /api/v1/history/{id}    Delete history entry
POST /api/v1/generate-pdf      Export analysis as PDF
GET  /api/v1/health            Model status + BERT scorer metrics
```

### Health endpoint example response

```json
{
  "status": "ok",
  "bert_scorer": {
    "active": true,
    "model": "fine-tuned all-mpnet-base-v2",
    "base_mae": 0.1562,
    "finetuned_mae": 0.0468,
    "improvement_pct": 70.01,
    "trained_pairs": 266
  }
}
```

---

## Design Decisions

**Why Groq instead of OpenAI for extraction?**
Groq's LPU inference runs LLaMA-3.3-70B at ~300 tokens/second vs ~50 for GPT-4o. For structured extraction tasks (name, skills, experience), output quality is equivalent and latency matters for UX. Free tier is generous enough for development and demo.

**Why not fine-tune on more data?**
266 pairs is small but sufficient for domain adaptation — the task is regression (predicting a similarity score), not classification from scratch. The 70% MAE improvement with 10 epochs on 186 training pairs shows the model adapted well. Collecting more labelled pairs would improve it further.

**Why Streamlit instead of React?**
This is a GenAI/NLP project. Streamlit communicates "I built this to demonstrate the AI pipeline" rather than "I'm a frontend engineer." For ML/AI engineering roles, that is the right signal.

**Why not end-to-end LLM scoring?**
Sending the full scoring logic to an LLM on every request would cost ~2 000 tokens/request with no determinism. The hybrid approach (LLM for extraction only, rule-based + fine-tuned model for scoring) is faster, cheaper, and more interpretable.

---

## Tech Stack

| Layer             | Technology                                           |
| ----------------- | ---------------------------------------------------- |
| Backend           | FastAPI (async), Python 3.11                         |
| LLM               | Groq API – LLaMA-3.3-70B-Versatile                   |
| Semantic matching | Fine-tuned all-mpnet-base-v2 (sentence-transformers) |
| Skill matching    | all-MiniLM-L6-v2                                     |
| NER               | spaCy en_core_web_lg                                 |
| Fuzzy matching    | rapidfuzz                                            |
| PDF parsing       | pdfplumber, python-docx                              |
| PDF export        | WeasyPrint                                           |
| Auth              | Supabase (Google OAuth + JWT)                        |
| Database          | Supabase (PostgreSQL)                                |
| Frontend          | Streamlit                                            |
| Hosting           | —                                                    |
