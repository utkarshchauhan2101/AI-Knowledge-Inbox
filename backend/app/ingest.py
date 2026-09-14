import logging

import httpx
import trafilatura

from .config import settings

log = logging.getLogger("ingest")


def chunk(text: str) -> list[str]:
    """Fixed-size char windows with overlap. Simple + deterministic."""
    size, overlap = settings.chunk_size, settings.chunk_overlap
    text = text.strip()
    if len(text) <= size:
        return [text] if text else []
    step = size - overlap
    return [
        text[i : i + size]
        for i in range(0, len(text), step)
        if text[i : i + size].strip()
    ]


def fetch_url(url: str) -> str:
    """Fetch a page and extract main content (strips nav/ads/boilerplate)."""
    try:
        resp = httpx.get(
            url,
            timeout=10.0,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0 Safari/537.36"
                )
            },
        )
        resp.raise_for_status()
    except httpx.HTTPError as e:
        log.warning(f"url fetch failed: {url} ({e})")
        raise ValueError(f"could not fetch url: {e}") from e

    extracted = trafilatura.extract(resp.text)
    if not extracted:
        raise ValueError("no readable content extracted from url")
    return extracted
