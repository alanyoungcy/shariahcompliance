from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse

from app.db.search_repository import SearchRepository
from app.models import SearchRequest, SearchResponse

router = APIRouter(prefix='/api/v1/standards', tags=['standards search'])
STANDARDS_PDF = Path(os.environ.get('AAOIFI_STANDARDS_PDF', '/data/Shariaa-Standards-ENG.pdf'))


def search_repository(request: Request) -> SearchRepository:
    return SearchRepository(request.app.state.db_pool)


@router.get('/source.pdf')
async def standards_source_pdf():
    if not STANDARDS_PDF.is_file():
        raise HTTPException(status_code=404, detail='The AAOIFI standards compilation is not available.')
    return FileResponse(
        STANDARDS_PDF,
        media_type='application/pdf',
        filename='aaoifi-shariah-standards.pdf',
        content_disposition_type='inline',
    )


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
