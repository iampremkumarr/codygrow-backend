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

    # File paths
    DATASETS_DIR: str = os.getenv("DATASETS_DIR", "generated/datasets")
    SCRIPTS_DIR: str = os.getenv("SCRIPTS_DIR", "generated/scripts")
    OUTPUTS_DIR: str = os.getenv("OUTPUTS_DIR", "generated/outputs")
    METRICS_DIR: str = os.getenv("METRICS_DIR", "generated/metrics")

settings = Settings()