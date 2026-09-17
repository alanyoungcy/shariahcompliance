from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from app.db.graph_repository import GraphRepository
from app.models import GraphLookupRequest, GraphLookupResponse

router = APIRouter(prefix='/api/v1/standards/graph', tags=['knowledge graph'])


def graph_repository(request: Request) -> GraphRepository:
    return GraphRepository(request.app.state.db_pool)


@router.post('/lookup', response_model=GraphLookupResponse)
async def lookup_graph(
    payload: GraphLookupRequest,
    repository: GraphRepository = Depends(graph_repository),
) -> GraphLookupResponse:
    graph = await repository.lookup(payload)
    if graph is None:
        raise HTTPException(status_code=404, detail='No approved graph node matches this seed.')

    nodes = graph['nodes']
    seed = next((node for node in nodes if str(node['id']) == str(graph['seed_id'])), None)
    if seed is None:
        raise HTTPException(status_code=500, detail='Approved graph seed was not returned.')

    return GraphLookupResponse(
        seed=seed,
        nodes=nodes,
        edges=graph['edges'],
        paths=graph['paths'],
        truncated=bool(graph['has_more']),
    )
