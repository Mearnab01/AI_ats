from typing import Dict, List
from rapidfuzz import fuzz


SKILL_ALIASES: Dict[str, str] = {
    # =========================
    # Languages
    # =========================
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "golang": "go",
    "c sharp": "c#",
    "c-sharp": "c#",
    "dotnet": ".net",
    "asp.net": ".net",
    "vb.net": ".net",

    # =========================
    # Frontend
    # =========================
    "reactjs": "react",
    "react.js": "react",
    "react js": "react",

    "nextjs": "next.js",
    "next": "next.js",

    "vuejs": "vue",
    "vue.js": "vue",

    "angularjs": "angular",
    "angular.js": "angular",

    "tailwindcss": "tailwind",
    "tailwind css": "tailwind",

    "bootstrap5": "bootstrap",
    "bootstrap 5": "bootstrap",

    "mui": "material ui",
    "material-ui": "material ui",

    # =========================
    # Backend
    # =========================
    "node": "node.js",
    "nodejs": "node.js",
    "node js": "node.js",

    "expressjs": "express",
    "express.js": "express",

    "nestjs": "nest.js",
    "nest js": "nest.js",

    "springboot": "spring boot",
    "spring-boot": "spring boot",

    "fast api": "fastapi",

    "django rest framework": "drf",

    # =========================
    # Databases
    # =========================
    "mongo": "mongodb",
    "mongo db": "mongodb",

    "postgres": "postgresql",
    "postgre": "postgresql",

    "mssql": "sql server",
    "ms sql": "sql server",

    "sqlite3": "sqlite",

    # =========================
    # Cloud
    # =========================
    "amazon web services": "aws",
    "amazon aws": "aws",

    "google cloud": "gcp",
    "google cloud platform": "gcp",

    "azure cloud": "azure",

    "ec2": "aws",
    "s3": "aws",
    "lambda": "aws",

    # =========================
    # DevOps
    # =========================
    "k8s": "kubernetes",

    "docker compose": "docker",

    "github actions": "ci/cd",
    "gitlab ci": "ci/cd",
    "gitlab-ci": "ci/cd",

    "jenkins pipeline": "jenkins",

    # =========================
    # AI / ML
    # =========================
    "ml": "machine learning",
    "dl": "deep learning",

    "ai": "artificial intelligence",

    "nlp": "natural language processing",

    "cv": "computer vision",

    "llm": "large language models",
    "llms": "large language models",

    "gen ai": "generative ai",
    "genai": "generative ai",

    "rag": "retrieval augmented generation",

    "agentic ai": "ai agents",
    "agents": "ai agents",

    # =========================
    # ML Frameworks
    # =========================
    "sklearn": "scikit-learn",
    "sci kit learn": "scikit-learn",

    "tf": "tensorflow",

    "hf": "hugging face",
    "huggingface": "hugging face",

    "pytorch lightning": "pytorch",

    "keras.io": "keras",

    # =========================
    # Data Science
    # =========================
    "pd": "pandas",
    "np": "numpy",

    "matplotlib.pyplot": "matplotlib",

    # =========================
    # Data Engineering
    # =========================
    "apache spark": "spark",
    "spark sql": "spark",
    "pyspark": "spark",

    "apache hadoop": "hadoop",
    "map reduce": "hadoop",
    "mapreduce": "hadoop",

    # =========================
    # APIs
    # =========================
    "rest": "rest api",
    "restful api": "rest api",

    "graphql api": "graphql",

    # =========================
    # Mobile
    # =========================
    "rn": "react native",
    "reactnative": "react native",

    "flutter sdk": "flutter",

    "android sdk": "android",
    "ios sdk": "ios",

    # =========================
    # Testing
    # =========================
    "pytest framework": "pytest",

    "jestjs": "jest",

    "cypress io": "cypress",

    # =========================
    # Version Control
    # =========================
    "github": "git",
    "gitlab": "git",
    "bitbucket": "git",

    # =========================
    # Operating Systems
    # =========================
    "ubuntu": "linux",
    "debian": "linux",
    "centos": "linux",
    "redhat": "linux",
    "rhel": "linux",

    # =========================
    # Message Queues
    # =========================
    "apache kafka": "kafka",
    "rabbit mq": "rabbitmq",

    # =========================
    # Vector DBs
    # =========================
    "chromadb": "chroma",
    "pinecone db": "pinecone",
    "faiss index": "faiss",

    # =========================
    # ORMs
    # =========================
    "sequelizejs": "sequelize",
    "typeorm": "typeorm",
    "prisma orm": "prisma",

    # =========================
    # Auth
    # =========================
    "jwt token": "jwt",
    "oauth2": "oauth",
    "oauth 2.0": "oauth",

    # =========================
    # AI APIs
    # =========================
    "openai api": "openai",
    "chatgpt api": "openai",

    "claude api": "anthropic",

    "gemini api": "gemini",

    # =========================
    # MLOps
    # =========================
    "ml ops": "mlops",
    "ml-flow": "mlflow",

    # =========================
    # BI
    # =========================
    "power bi": "powerbi",
    "ms power bi": "powerbi",

    # =========================
    # Misc
    # =========================
    "oop": "object oriented programming",
    "oops": "object oriented programming",

    "dsa": "data structures and algorithms",

    "micro-services": "microservices",
    "micro service": "microservices",
}


def normalize_skill(skill: str) -> str:
    cleaned = (
        skill.strip()
        .lower()
        .replace("-", " ")
        .replace("_", " ")
    )

    cleaned = " ".join(cleaned.split())

    return SKILL_ALIASES.get(cleaned, cleaned)


def fuzzy_match_keywords(
    resume_keywords: List[str],
    jd_keywords: List[str],
    threshold: int = 85,
):
    resume_normalized = {
        normalize_skill(skill)
        for skill in resume_keywords
    }

    jd_normalized = {
        normalize_skill(skill)
        for skill in jd_keywords
    }

    matched = []
    missing = []

    for jd_skill in jd_normalized:

        if jd_skill in resume_normalized:
            matched.append(jd_skill)
            continue

        best_score = max(
            (
                fuzz.token_sort_ratio(
                    jd_skill,
                    resume_skill,
                )
                for resume_skill in resume_normalized
            ),
            default=0,
        )

        if best_score >= threshold:
            matched.append(jd_skill)
        else:
            missing.append(jd_skill)

    return {
        "matched": sorted(matched),
        "missing": sorted(missing),
    }