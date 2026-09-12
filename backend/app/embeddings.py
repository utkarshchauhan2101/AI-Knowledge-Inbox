from openai import OpenAI

from .config import settings

_client = OpenAI(api_key=settings.gemini_api_key, base_url=settings.base_url)


def embed(texts: list[str]) -> list[list[float]]:
    resp = _client.embeddings.create(model=settings.embed_model, input=texts)
    return [d.embedding for d in resp.data]
