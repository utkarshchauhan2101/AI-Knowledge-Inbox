import json
import logging
import threading

import numpy as np

from .db import get_conn

log = logging.getLogger("store")


class VectorIndex:
    """In-memory embedding matrix, loaded once, updated on ingest.
    Single source of truth for similarity search."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._matrix: np.ndarray | None = None
        self._meta: list[dict] = []  # parallel to matrix rows

    def load(self) -> None:
        with get_conn() as conn:
            rows = conn.execute(
                """
                SELECT c.item_id, c.text, c.embedding, i.source_type, i.source
                FROM chunks c JOIN items i ON i.id = c.item_id
                ORDER BY c.id
                """
            ).fetchall()
        with self._lock:
            if rows:
                self._matrix = np.array(
                    [json.loads(r["embedding"]) for r in rows], dtype=np.float32
                )
                self._meta = [
                    {
                        "item_id": r["item_id"],
                        "text": r["text"],
                        "source_type": r["source_type"],
                        "source": r["source"],
                    }
                    for r in rows
                ]
            else:
                self._matrix, self._meta = None, []
        log.info(f"vector index loaded: {len(self._meta)} chunks")

    def add(self, vectors: list[list[float]], meta: list[dict]) -> None:
        block = np.array(vectors, dtype=np.float32)
        with self._lock:
            self._matrix = (
                block if self._matrix is None else np.vstack([self._matrix, block])
            )
            self._meta.extend(meta)

    def search(self, qvec: list[float], k: int) -> list[tuple[dict, float]]:
        with self._lock:
            if self._matrix is None:
                return []
            matrix, meta = self._matrix, self._meta
        q = np.array(qvec, dtype=np.float32)
        q /= np.linalg.norm(q) + 1e-8
        m = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-8)
        scores = m @ q
        top = np.argsort(scores)[::-1][:k]
        return [(meta[i], float(scores[i])) for i in top]


index = VectorIndex()
