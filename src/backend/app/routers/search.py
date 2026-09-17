from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.db.search_repository import SearchRepository
from app.models import SearchRequest, SearchResponse

router = APIRouter(prefix='/api/v1/standards', tags=['standards search'])


def search_repository(request: Request) -> SearchRepository:
    return SearchRepository(request.app.state.db_pool)


@router.post('/search', response_model=SearchResponse)
async def search_standards(
    payload: SearchRequest,
    repository: SearchRepository = Depends(search_repository),
) -> SearchResponse:
    results, sparse_executed, dense_executed = await repository.search(payload)
    return SearchResponse(
        results=results,
        sparse_executed=sparse_executed,
        dense_executed=dense_executed,
    )
