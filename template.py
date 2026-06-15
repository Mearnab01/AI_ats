"""
template.py
Run this script to scaffold the ATS Resume Scorer project.
Creates missing files/folders only.
"""

import os

STRUCTURE = [

    # Root Files
    (".gitignore", ""),
    ("README.md", "# ATS Resume Scorer\n"),
    ("requirements.txt", "fastapi\nstreamlit\nspacy\nsentence-transformers\ngroq\nsupabase\npython-dotenv\n"),
    (".env.example", "GROQ_API_KEY=\nSUPABASE_URL=\nSUPABASE_SERVICE_ROLE_KEY=\n"),

    # Backend
    ("backend/__init__.py", ""),
    ("backend/main.py", ""),
    ("backend/api/__init__.py", ""),
    ("backend/api/auth.py", ""),
    ("backend/api/routes.py", ""),
    ("backend/core/__init__.py", ""),
    ("backend/core/config.py", ""),
    ("backend/database/__init__.py", ""),
    ("backend/database/supabase_db.py", ""),
    ("backend/models/__init__.py", ""),
    ("backend/models/schemas.py", ""),
    ("backend/services/__init__.py", ""),
    ("backend/services/ats_scorer.py", ""),
    ("backend/services/feedback_engine.py", ""),
    ("backend/services/groq_parser.py", ""),
    ("backend/services/jd_matcher.py", ""),
    ("backend/services/pdf_export.py", ""),
    ("backend/services/recommendation_engine.py", ""),
    ("backend/services/report_generator.py", ""),
    ("backend/services/resume_analyzer.py", ""),
    ("backend/services/resume_parser.py", ""),
    ("backend/services/job_fetcher.py", ""),
    ("backend/templates/summary.html", ""),
    ("backend/utils/__init__.py", ""),

    # Frontend Core
    ("frontend/__init__.py", ""),
    ("frontend/streamlit_app.py", ""),
    ("frontend/.streamlit/config.toml", ""),

    # Existing Frontend
    ("frontend/services/__init__.py", ""),
    ("frontend/services/api_client.py", ""),
    ("frontend/views/__init__.py", ""),
    ("frontend/views/landing.py", ""),
    ("frontend/views/scorer.py", ""),
    ("frontend/views/history.py", ""),
    ("frontend/components/__init__.py", ""),

    # New Static CSS
    ("frontend/static/css/variables.css", ""),
    ("frontend/static/css/base.css", ""),
    ("frontend/static/css/components.css", ""),
    ("frontend/static/css/animations.css", ""),
    ("frontend/static/css/streamlit_overrides.css", ""),
    ("frontend/static/css/style.css", ""),

    # New Static JS
    ("frontend/static/js/ui.js", ""),

    # Components
    ("frontend/components/_helpers.py", ""),
    ("frontend/components/score_display.py", ""),
    ("frontend/components/skill_validation.py", ""),
    ("frontend/components/jd_comparison.py", ""),
    ("frontend/components/strengths_issues.py", ""),
    ("frontend/components/detailed_feedback.py", ""),
    ("frontend/components/action_items.py", ""),
    ("frontend/components/recommendations.py", ""),
    ("frontend/components/dashboard.py", ""),

    # Jupyter Notebooks
    ("jupyter notebooks/01_EDA_and_DATA_prep.ipynb", ""),
    ("jupyter notebooks/02_BERT_EMBEDDINGS.ipynb", ""),
    ("jupyter notebooks/03_BERT_FINETUNE.ipynb", ""),

    # ML Artifacts
    ("ml model/.gitkeep", ""),
]


def main():

    created = 0
    skipped = 0

    for path, content in STRUCTURE:

        directory = os.path.dirname(path)

        if directory:
            os.makedirs(directory, exist_ok=True)

        if os.path.exists(path):
            print(f"⏭ Skipped existing: {path}")
            skipped += 1
            continue

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ Created: {path}")
        created += 1

    print("\n" + "=" * 50)
    print(f"Created: {created}")
    print(f"Skipped: {skipped}")
    print("ATS Resume Scorer structure ready!")


if __name__ == "__main__":
    main()