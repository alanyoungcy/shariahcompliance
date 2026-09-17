from __future__ import annotations

from typing import Any

import asyncpg

from app.models import GraphLookupRequest

GRAPH_LOOKUP_SQL = '''
WITH RECURSIVE seed_node AS (
  SELECT node.id
  FROM graph_node node
  LEFT JOIN graph_node_alias alias ON alias.graph_node_id = node.id
  WHERE node.approval_status = 'approved'
    AND (node.canonical_key = $1 OR lower(node.label) = lower($1) OR lower(alias.alias) = lower($1))
  LIMIT 1
), walk AS (
  SELECT
    ARRAY[seed.id, CASE WHEN edge.source_node_id = seed.id THEN edge.target_node_id ELSE edge.source_node_id END] AS node_path,
    ARRAY[edge.id] AS edge_path,
    1 AS depth
  FROM seed_node seed
  JOIN graph_edge edge ON edge.source_node_id = seed.id OR edge.target_node_id = seed.id
  JOIN graph_node other_node ON other_node.id = CASE WHEN edge.source_node_id = seed.id THEN edge.target_node_id ELSE edge.source_node_id END
  WHERE edge.approval_status = 'approved'
    AND other_node.approval_status = 'approved'

  UNION ALL

  SELECT
    walk.node_path || CASE WHEN next_edge.source_node_id = walk.node_path[array_length(walk.node_path, 1)] THEN next_edge.target_node_id ELSE next_edge.source_node_id END,
    walk.edge_path || next_edge.id,
    walk.depth + 1
  FROM walk
  JOIN graph_edge next_edge
    ON next_edge.source_node_id = walk.node_path[array_length(walk.node_path, 1)]
      OR next_edge.target_node_id = walk.node_path[array_length(walk.node_path, 1)]
  JOIN graph_node next_node ON next_node.id = CASE
    WHEN next_edge.source_node_id = walk.node_path[array_length(walk.node_path, 1)] THEN next_edge.target_node_id
    ELSE next_edge.source_node_id
  END
  WHERE walk.depth < $2
    AND next_edge.approval_status = 'approved'
    AND next_node.approval_status = 'approved'
    AND NOT (CASE
      WHEN next_edge.source_node_id = walk.node_path[array_length(walk.node_path, 1)] THEN next_edge.target_node_id
      ELSE next_edge.source_node_id
    END = ANY(walk.node_path))
), limited_paths AS (
  SELECT DISTINCT node_path, edge_path
  FROM walk
  ORDER BY node_path
  LIMIT $3
), candidate_node_ids AS (
  SELECT id FROM seed_node
  UNION
  SELECT DISTINCT unnest(node_path) AS id FROM limited_paths
), selected_nodes AS (
  SELECT id
  FROM candidate_node_ids
  ORDER BY id
  LIMIT $3
), candidate_edge_ids AS (
  SELECT DISTINCT unnest(edge_path) AS id FROM limited_paths
), selected_edges AS (
  SELECT edge.id
  FROM graph_edge edge
  JOIN candidate_edge_ids candidate ON candidate.id = edge.id
  JOIN selected_nodes source_node ON source_node.id = edge.source_node_id
  JOIN selected_nodes target_node ON target_node.id = edge.target_node_id
  WHERE edge.approval_status = 'approved'
  ORDER BY edge.id
  LIMIT $4
), valid_paths AS (
  SELECT path.node_path, path.edge_path
  FROM limited_paths path
  WHERE NOT EXISTS (
    SELECT 1
    FROM unnest(path.edge_path) AS path_edge(id)
    LEFT JOIN selected_edges selected ON selected.id = path_edge.id
    WHERE selected.id IS NULL
  )
)
SELECT jsonb_build_object(
  'seed_id', (SELECT id FROM seed_node),
  'nodes', COALESCE((
    SELECT jsonb_agg(jsonb_build_object(
      'id', node.id, 'type', node.node_type, 'label', node.label,
      'description', node.description,
      'clause_id', COALESCE(clause.clause_id, node.properties ->> 'display_clause_id'),
      'printed_page', COALESCE(clause.printed_page_start, NULLIF(node.properties ->> 'printed_page', '')::integer)
    ) ORDER BY node.label)
    FROM graph_node node
    JOIN selected_nodes selected ON selected.id = node.id
    LEFT JOIN clause ON clause.id = node.clause_id
  ), '[]'::jsonb),
  'edges', COALESCE((
    SELECT jsonb_agg(jsonb_build_object(
      'id', edge.id, 'source', edge.source_node_id, 'target', edge.target_node_id,
      'predicate', edge.predicate,
      'evidence_clause_id', COALESCE(clause.clause_id, evidence_node.properties ->> 'display_clause_id'),
      'printed_page', COALESCE(clause.printed_page_start, edge.source_pdf_page), 'approval_status', 'approved',
      'scholar_reviewer', edge.scholar_reviewer
    ) ORDER BY edge.id)
    FROM graph_edge edge
    JOIN selected_edges selected ON selected.id = edge.id
    LEFT JOIN clause ON clause.id = edge.evidence_clause_id
    LEFT JOIN graph_node evidence_node ON evidence_node.id = edge.target_node_id AND evidence_node.node_type = 'clause'
  ), '[]'::jsonb),
  'paths', COALESCE((
    SELECT jsonb_agg(jsonb_build_object('node_ids', node_path, 'edge_ids', edge_path))
    FROM valid_paths
  ), '[]'::jsonb),
  'has_more', (SELECT count(*) > $3 FROM candidate_node_ids) OR (SELECT count(*) > $4 FROM candidate_edge_ids)
) AS graph
'''


class GraphRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self.pool = pool

    async def lookup(self, request: GraphLookupRequest) -> dict[str, Any] | None:
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow(
                GRAPH_LOOKUP_SQL,
                request.seed,
                request.max_hops,
                request.node_limit,
                request.edge_limit,
            )
        if row is None or row['graph']['seed_id'] is None:
            return None
        return row['graph']
