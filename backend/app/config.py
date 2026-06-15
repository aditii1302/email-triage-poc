from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    LLM_PROVIDER: str = "ollama"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_TEXT_MODEL: str = "llama3.1"
    OLLAMA_VISION_MODEL: str = "llava"
    ITSM_A_BASE_URL: str = "http://localhost:8001"
    ITSM_B_BASE_URL: str = "http://localhost:8002"
    DIRECTORY_BASE_URL: str = "http://localhost:8003"
    DATABASE_URL: str = "sqlite:///./email_triage.db"

    class Config:
        env_file = ".env"


settings = Settings()
