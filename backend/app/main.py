import json
import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import rag
from .db import get_conn, init_db
from .embeddings import embed
from .ingest import chunk, fetch_url
from .logging_conf import configure_logging
from .models import (
    IngestRequest,
    IngestResponse,
    Item,
    QueryRequest,
    QueryResponse,
)
from .store import index

configure_logging()
log = logging.getLogger("api")


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    index.load()
    log.info("startup complete")
    yield


app = FastAPI(title="notes-rag", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    rid = uuid.uuid4().hex[:8]
    start = time.perf_counter()
    log.info(f"req start id={rid} {request.method} {request.url.path}")
    response = await call_next(request)
    ms = (time.perf_counter() - start) * 1000
    log.info(f"req done  id={rid} status={response.status_code} {ms:.0f}ms")
    response.headers["X-Request-ID"] = rid
    return response


@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    log.error(f"unhandled error on {request.url.path}: {exc}")
    return JSONResponse(status_code=500, content={"detail": "internal error"})


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse, status_code=201)
def ingest(req: IngestRequest):
    if req.source_type == "note":
        if not req.content:
            raise HTTPException(400, "note requires 'content'")
        content, source = req.content, None
    else:
        if not req.url:
            raise HTTPException(400, "url requires 'url'")
        source = str(req.url)
        try:
            content = fetch_url(source)
        except ValueError as e:
            raise HTTPException(502, str(e)) from e

    chunks = chunk(content)
    if not chunks:
        raise HTTPException(400, "no content to store after chunking")

    try:
        vectors = embed(chunks)
    except Exception as e:
        log.error(f"embedding failed: {e}")
        raise HTTPException(502, "embedding request failed") from e

    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO items (source_type, source, content) VALUES (?, ?, ?)",
            (req.source_type, source, content),
        )
        item_id = cur.lastrowid
        conn.executemany(
            "INSERT INTO chunks (item_id, chunk_index, text, embedding) VALUES (?, ?, ?, ?)",
            [
                (item_id, i, c, json.dumps(v))
                for i, (c, v) in enumerate(zip(chunks, vectors))
            ],
        )

    index.add(
        vectors,
        [
            {
                "item_id": item_id,
                "text": c,
                "source_type": req.source_type,
                "source": source,
            }
            for c in chunks
        ],
    )
    log.info(f"ingested item={item_id} chunks={len(chunks)}")
    return IngestResponse(item_id=item_id, chunks=len(chunks))


@app.get("/items", response_model=list[Item])
def list_items():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, source_type, source, content, created_at FROM items ORDER BY id DESC"
        ).fetchall()
    return [Item(**dict(r)) for r in rows]


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    try:
        text, sources = rag.answer(req.question)
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"query failed: {e}")
        raise HTTPException(502, "llm request failed") from e
    return QueryResponse(answer=text, sources=sources)
