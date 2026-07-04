from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False

    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-base"
    LLM_MODEL: str = "Qwen/Qwen2.5-1.5B-Instruct"


settings = Settings()
