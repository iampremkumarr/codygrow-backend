import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # API Settings
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000/api")

    # CORS Settings
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "http://localhost:8080,http://localhost:5173").split(",")

    # OpenRouter API Keys
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    # JWT Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "insecure-default-secret-change-in-production")

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Vercel Serverless environment detection
    IS_VERCEL: bool = os.getenv("VERCEL") == "1"

    # File paths (use /tmp on Vercel to support read-only filesystem)
    base_dir = "/tmp/generated" if os.getenv("VERCEL") == "1" else "generated"
    DATASETS_DIR: str = os.getenv("DATASETS_DIR", f"{base_dir}/datasets")
    SCRIPTS_DIR: str = os.getenv("SCRIPTS_DIR", f"{base_dir}/scripts")
    OUTPUTS_DIR: str = os.getenv("OUTPUTS_DIR", f"{base_dir}/outputs")
    METRICS_DIR: str = os.getenv("METRICS_DIR", f"{base_dir}/metrics")

settings = Settings()