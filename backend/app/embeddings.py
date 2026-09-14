from google import genai

from .config import settings

_client = genai.Client(api_key=settings.gemini_api_key)


def embed(texts: list[str]) -> list[list[float]]:
    result = _client.models.embed_content(
        model=settings.embed_model,
        contents=texts,
    )
    return [e.values for e in result.embeddings]