from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    gemini_api_key: str
    base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    embed_model: str = "text-embedding-004"
    chat_model: str = "gemini-2.0-flash"
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 4
    db_path: str = "notes.db"


settings = Settings()
