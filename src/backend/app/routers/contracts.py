from __future__ import annotations

from pathlib import Path
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from app.services.contract_analysis import MAX_UPLOAD_BYTES, analyze_contract, extract_contract_text
from app.services.aaoifi_corpus import retrieve_candidate_sources
from app.services.contract_graph import ContractGraphQueryError, query_contract_graph, validate_contract_graph_query
from app.services.copilot import CopilotUnavailableError, explain_finding

router = APIRouter(prefix='/api/v1/contracts', tags=['contract analysis'])
UPLOAD_DIR = Path('/tmp/shariah-contract-previews')


class ContractGraphQueryRequest(BaseModel):
    analysis_id: str = Field(min_length=36, max_length=36)
    query: str = Field(min_length=12, max_length=800)


class FindingExplanationRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    finding_type: str = Field(min_length=1, max_length=80)
    severity: Literal['critical', 'high', 'medium']
    excerpt: str = Field(min_length=1, max_length=1200)
    citation: str = Field(min_length=1, max_length=320)
    recommendation: str = Field(min_length=1, max_length=700)


@router.post('/analyze')
async def analyze_uploaded_contract(request: Request, file: UploadFile = File(...)) -> dict[str, object]:
    if file.content_type not in {'application/pdf', 'application/x-pdf'} and not (file.filename or '').lower().endswith('.pdf'):
        raise HTTPException(status_code=415, detail='Upload a PDF contract.')

    raw = await file.read(MAX_UPLOAD_BYTES + 1)
    try:
        contract_text = await run_in_threadpool(extract_contract_text, file.filename or 'uploaded-contract.pdf', raw)
        candidate_sources = await retrieve_candidate_sources(request.app.state.db_pool, contract_text)
        analysis = await run_in_threadpool(
            analyze_contract, file.filename or 'uploaded-contract.pdf', raw, candidate_sources
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    async with request.app.state.db_pool.acquire() as connection:
        await connection.execute(
            'INSERT INTO contract_analysis_graph (analysis_id, graph) VALUES ($1::uuid, $2::jsonb) '
            'ON CONFLICT (analysis_id) DO UPDATE SET graph = EXCLUDED.graph, created_at = now()',
            analysis['analysis_id'],
            analysis['graph'],
        )
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    try:
        (UPLOAD_DIR / f"{analysis['analysis_id']}.pdf").write_bytes(raw)
    except OSError as error:
        raise HTTPException(status_code=500, detail='The contract was analysed but its preview could not be prepared.') from error
    return analysis


@router.get('/{analysis_id}/source.pdf')
async def uploaded_contract_pdf(analysis_id: UUID):
    from fastapi.responses import FileResponse

    path = UPLOAD_DIR / f'{analysis_id}.pdf'
    if not path.is_file():
        raise HTTPException(status_code=404, detail='The uploaded contract preview is no longer available. Upload the contract again.')
    return FileResponse(path, media_type='application/pdf', filename='uploaded-contract.pdf', content_disposition_type='inline')


@router.post('/graph/query')
async def query_uploaded_contract_graph(request: Request, payload: ContractGraphQueryRequest) -> dict[str, object]:
    try:
        # Validate the deliberately small query grammar before retrieving any persisted graph.
        # It prevents malformed or destructive expressions from becoming a database concern.
        validate_contract_graph_query(payload.query)
    except ContractGraphQueryError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    async with request.app.state.db_pool.acquire() as connection:
        graph = await connection.fetchval(
            'SELECT graph FROM contract_analysis_graph WHERE analysis_id = $1::uuid',
            payload.analysis_id,
        )
    if graph is None:
        raise HTTPException(status_code=404, detail='The uploaded-contract graph is no longer available. Upload the contract again.')
    return {'graph': query_contract_graph(graph, payload.query), 'query_engine': 'bounded-cypher-compatible'}


@router.post('/explain-finding')
async def explain_contract_finding(request: FindingExplanationRequest) -> dict[str, str]:
    try:
        return await run_in_threadpool(
            explain_finding,
            title=request.title,
            finding_type=request.finding_type,
            severity=request.severity,
            excerpt=request.excerpt,
            citation=request.citation,
            recommendation=request.recommendation,
        )
    except CopilotUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
