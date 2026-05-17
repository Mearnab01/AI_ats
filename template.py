"""
template.py
Run this script to scaffold the entire project structure for the ATS Scorer.
"""

import os

# Define the structure: (filepath, content)
STRUCTURE = [
    # Root Files
    (".gitignore", ""),
    ("README.md", "# ATS Resume Scorer\n"),
    ("requirements.txt", "fastapi\nstreamlit\nspacy\nsentence-transformers\ngroq\nsupabase\npython-dotenv\n"),
    (".env.example", "GROQ_API_KEY=\nSUPABASE_URL=\nSUPABASE_KEY=\n"),

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
    ("backend/services/job_fetcher.py", ""), # New Apify service
    ("backend/templates/summary.html", ""),
    ("backend/utils/__init__.py", ""),

    # Frontend (Streamlit)
    ("frontend/__init__.py", ""),
    ("frontend/streamlit_app.py", ""),
    ("frontend/.streamlit/config.toml", ""),
    ("frontend/assets/styles.css", ""),
    ("frontend/components/__init__.py", ""),
    ("frontend/services/__init__.py", ""),
    ("frontend/services/api_client.py", ""),
    ("frontend/views/__init__.py", ""),
    ("frontend/views/landing.py", ""),
    ("frontend/views/scorer.py", ""),
    ("frontend/views/history.py", ""),

    # Jupyter Notebooks
    ("jupyter notebooks/01_EDA_and_DATA_prep.ipynb", ""),
    ("jupyter notebooks/02_BERT_EMBEDDINGS.ipynb", ""),
    ("jupyter notebooks/03_BERT_FINETUNE.ipynb", ""),
    
    # ML Artifacts
    ("ml model/.gitkeep", "")
]

def main():
    for path, content in STRUCTURE:
        # Create directory if it doesn't exist
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

        # Create file with content
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
            print(f"Created file: {path}")

    print("\n✅ Project structure scaffolded successfully!")

if __name__ == "__main__":
    main()