from typing import Literal, Optional

from pydantic import BaseModel, Field, HttpUrl


class IngestRequest(BaseModel):
    source_type: Literal["note", "url"]
    content: Optional[str] = Field(default=None, min_length=1)
    url: Optional[HttpUrl] = None


class Item(BaseModel):
    id: int
    source_type: str
    source: Optional[str]
    content: str
    created_at: str


class IngestResponse(BaseModel):
    item_id: int
    chunks: int


class Source(BaseModel):
    item_id: int
    source_type: str
    source: Optional[str]
    snippet: str
    score: float


class QueryRequest(BaseModel):
    question: str = Field(min_length=1)


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]
