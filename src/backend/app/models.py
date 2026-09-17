from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

NodeType = Literal['standard', 'section', 'clause', 'concept', 'contract_type', 'risk_pattern', 'rule', 'control', 'finding', 'authority']


class GraphLookupRequest(BaseModel):
    seed: str = Field(min_length=1, max_length=200)
    max_hops: int = Field(default=2, ge=1, le=3)
    node_limit: int = Field(default=50, ge=1, le=50)
    edge_limit: int = Field(default=75, ge=1, le=75)


class GraphNodeResponse(BaseModel):
    id: UUID
    type: NodeType
    label: str
    description: str | None = None
    clause_id: str | None = None
    printed_page: int | None = None


class GraphEdgeResponse(BaseModel):
    id: UUID
    source: UUID
    target: UUID
    predicate: str
    evidence_clause_id: str | None = None
    printed_page: int | None = None
    approval_status: Literal['approved']
    scholar_reviewer: str | None = None


class GraphPathResponse(BaseModel):
    node_ids: list[UUID]
    edge_ids: list[UUID]


class GraphLookupResponse(BaseModel):
    seed: GraphNodeResponse
    nodes: list[GraphNodeResponse]
    edges: list[GraphEdgeResponse]
    paths: list[GraphPathResponse]
    truncated: bool


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    authority: str = 'AAOIFI'
    standard_number: str | None = Field(default=None, max_length=30)
    language: str = Field(default='en', min_length=2, max_length=10)
    query_embedding: list[float] | None = Field(default=None, min_length=1, max_length=3072)
    limit: int = Field(default=5, ge=1, le=10)


class SearchCitation(BaseModel):
    authority: str
    standard_number: str
    title: str
    clause_id: str
    printed_page_start: int
    printed_page_end: int
    source_pdf_page_start: int
    source_pdf_page_end: int


class SearchResult(BaseModel):
    clause_db_id: UUID
    citation: SearchCitation
    excerpt: str
    branch_ranks: dict[str, int]
    fused_score: float


class SearchResponse(BaseModel):
    results: list[SearchResult]
    sparse_executed: bool
    dense_executed: bool
