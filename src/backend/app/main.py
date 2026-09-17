from __future__ import annotations

import json
import os
from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.contracts import router as contracts_router
from app.routers.graph import router as graph_router
from app.routers.search import router as search_router


async def configure_connection(connection: asyncpg.Connection) -> None:
    await connection.set_type_codec('jsonb', encoder=json.dumps, decoder=json.loads, schema='pg_catalog')


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_pool = await asyncpg.create_pool(
        dsn=os.environ.get('DATABASE_URL', 'postgresql://shariah:shariah@postgres:5432/shariah'),
        min_size=1,
        max_size=10,
        init=configure_connection,
    )
    async with app.state.db_pool.acquire() as connection:
        await connection.execute("""
            CREATE TABLE IF NOT EXISTS contract_analysis_graph (
                analysis_id uuid PRIMARY KEY,
                graph jsonb NOT NULL,
                created_at timestamptz NOT NULL DEFAULT now()
            )
        """)
    try:
        yield
    finally:
        await app.state.db_pool.close()


app = FastAPI(title='Shariah Compliance Copilot', version='0.2.0', lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(','),
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(contracts_router)
app.include_router(graph_router)
app.include_router(search_router)


@app.get('/health')
async def health() -> dict[str, str]:
    return {'status': 'ok'}
