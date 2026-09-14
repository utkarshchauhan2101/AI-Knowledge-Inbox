from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    gemini_api_key: str
    embed_model: str = "gemini-embedding-001"
    chat_model: str = "gemini-3.6-flash"
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 4
    db_path: str = "notes.db"


settings = Settings()