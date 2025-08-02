from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    gemini_api_key: str
    anthropic_api_key: str
    groq_api_key: str
    xai_api_key: str
    mistral_api_key: str
    nvidia_api_key: str

    google_application_credentials: str
    firebase_storage_bucket: str

    mongodb_host: str
    mongodb_port: str
    mongodb_db_name: str
    mongodb_root_username: str
    mongodb_root_password: str

    redis_host: str
    redis_port: str
    redis_password: str
    redis_username: str
    redis_database: str

    langchain_api_key: str
    langchain_project: str
    langsmith_tracing: str

    class Config:
        env_file = ".env"

settings = Settings() # type: ignore
