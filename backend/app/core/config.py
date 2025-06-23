from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    gemini_api_key: str
    anthropic_api_key: str
    groq_api_key: str
    xai_api_key: str
    mistral_api_key: str
    nvidia_api_key: str

    class Config:
        env_file = ".env"

settings = Settings()
