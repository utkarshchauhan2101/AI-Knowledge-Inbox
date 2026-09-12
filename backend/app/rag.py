import logging

from openai import OpenAI

from .config import settings
from .embeddings import embed
from .models import Source
from .store import index

log = logging.getLogger("rag")
_client = OpenAI(api_key=settings.gemini_api_key, base_url=settings.base_url)

SYSTEM_PROMPT = (
    "You answer questions using only the provided context. "
    "If the context does not contain the answer, say you don't know. "
    "Be concise."
)


def retrieve(question: str, k: int) -> list[Source]:
    qvec = embed([question])[0]
    hits = index.search(qvec, k)
    return [
        Source(
            item_id=m["item_id"],
            source_type=m["source_type"],
            source=m["source"],
            snippet=m["text"],
            score=score,
        )
        for m, score in hits
    ]


def answer(question: str) -> tuple[str, list[Source]]:
    sources = retrieve(question, settings.top_k)
    if not sources:
        return "no content saved yet — add some notes or urls first.", []

    context = "\n\n".join(f"[source {s.item_id}] {s.snippet}" for s in sources)
    resp = _client.chat.completions.create(
        model=settings.chat_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )
    return resp.choices[0].message.content, sources
