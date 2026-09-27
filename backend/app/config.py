from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./aura.db"
    jwt_secret: str = "development-only-change-me"
    access_token_minutes: int = 60
    frontend_origin: str = "http://localhost:3000"
    openai_api_key: str = ""
    openai_model: str = "llama-3.1-8b-instant"
    openai_base_url: str = "https://api.groq.com/openai/v1"
    max_upload_mb: int = 20
    upload_dir: str = "uploads"
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

settings = Settings()