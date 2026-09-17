from __future__ import annotations

import re
from collections import deque
from copy import deepcopy
from typing import Any



def _clean_text(value: str) -> str:
    return re.sub(r'\s+', ' ', value).strip()

_ALLOWED_TYPES = {'standard', 'section', 'clause', 'concept', 'contract_type', 'risk_pattern', 'rule', 'control', 'finding', 'authority'}
_ALLOWED_PREDICATES = {'EVIDENCED_BY', 'RELATED_TO', 'REQUIRES', 'CONFLICTS_WITH', 'CONTAINS', 'PARENT_OF', 'CITES', 'DEFINES', 'GOVERNS', 'PROHIBITS', 'PERMITS'}
_MAX_QUERY_CHARS = 800
_PATTERN = re.compile(
    r'''^\s*MATCH\s*(?:[A-Za-z_]\w*\s*=\s*)?
    \(\s*(?P<left_var>[A-Za-z_]\w*)?\s*(?::\s*(?P<left_type>[A-Za-z_]+))?\s*(?:\{\s*(?:id|label)\s*:\s*['\"](?P<left_value>[^'\"]+)['\"]\s*\})?\s*\)
    (?:\s*-\s*\[\s*(?P<edge_var>[A-Za-z_]\w*)?\s*(?::\s*(?P<predicate>[A-Za-z_]+))?\s*\]\s*->\s*
    \(\s*(?P<right_var>[A-Za-z_]\w*)?\s*(?::\s*(?P<right_type>[A-Za-z_]+))?\s*(?:\{\s*(?:id|label)\s*:\s*['\"](?P<right_value>[^'\"]+)['\"]\s*\})?\s*\))?
    \s*RETURN\s+.+?\s*$''',
    re.IGNORECASE | re.VERBOSE,
)


class ContractGraphQueryError(ValueError):
    """Raised when a supplied expression is outside the bounded query grammar."""


def _node_matches(node: dict[str, Any], node_type: str | None, value: str | None) -> bool:
    if node_type and str(node.get('type', '')).lower() != node_type.lower():
        return False
    if value:
        probe = value.strip().lower()
        return probe == str(node.get('id', '')).lower() or probe == str(node.get('label', '')).lower()
    return True


def _parse(query: str) -> dict[str, str | None]:
    normalized = _clean_text(query)
    if len(normalized) > _MAX_QUERY_CHARS:
        raise ContractGraphQueryError('The graph query is too long.')
    match = _PATTERN.fullmatch(normalized)
    if not match:
        raise ContractGraphQueryError('Use a bounded MATCH … RETURN query. Example: MATCH (f:finding)-[r:EVIDENCED_BY]->(c:clause) RETURN f,r,c')
    values = {key: value for key, value in match.groupdict().items()}
    for key in ('left_type', 'right_type'):
        if values[key] and values[key].lower() not in _ALLOWED_TYPES:
            raise ContractGraphQueryError(f'Unsupported node type: {values[key]}.')
    if values['predicate'] and values['predicate'].upper() not in _ALLOWED_PREDICATES:
        raise ContractGraphQueryError(f'Unsupported relationship: {values["predicate"]}.')
    return values


def validate_contract_graph_query(query: str) -> None:
    _parse(query)


def _subgraph(graph: dict[str, Any], nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
    if not nodes:
        seed = graph.get('seed') if isinstance(graph.get('seed'), dict) else {'id': 'contract:empty', 'type': 'concept', 'label': 'Uploaded contract'}
        return {**deepcopy(graph), 'seed': deepcopy(seed), 'nodes': [], 'edges': [], 'paths': [], 'truncated': False}
    node_ids = {str(node['id']) for node in nodes}
    retained_edges = [edge for edge in edges if str(edge.get('source')) in node_ids and str(edge.get('target')) in node_ids]
    seed = next((node for node in nodes if str(node['id']) == str(graph.get('seed', {}).get('id'))), nodes[0])
    return {
        **deepcopy(graph),
        'seed': deepcopy(seed),
        'nodes': deepcopy(nodes),
        'edges': deepcopy(retained_edges),
        'paths': [],
        'truncated': False,
    }


def query_contract_graph(graph: dict[str, Any], query: str) -> dict[str, Any]:
    parsed = _parse(query)
    nodes = [node for node in graph.get('nodes', []) if isinstance(node, dict)]
    edges = [edge for edge in graph.get('edges', []) if isinstance(edge, dict)]
    selected_left = [node for node in nodes if _node_matches(node, parsed['left_type'], parsed['left_value'])]
    selected_left_ids = {str(node['id']) for node in selected_left}

    if not parsed['right_var']:
        return _subgraph(graph, selected_left[:50], [])

    predicate = parsed['predicate'].upper() if parsed['predicate'] else None
    nodes_by_id = {str(node['id']): node for node in nodes}
    selected_edges = []
    for edge in edges:
        if str(edge.get('source')) not in selected_left_ids:
            continue
        if predicate and str(edge.get('predicate', '')).upper() != predicate:
            continue
        target = nodes_by_id.get(str(edge.get('target')))
        if target and _node_matches(target, parsed['right_type'], parsed['right_value']):
            selected_edges.append(edge)
    result_nodes = {str(node['id']): node for node in selected_left}
    for edge in selected_edges:
        target = nodes_by_id.get(str(edge['target']))
        if target:
            result_nodes[str(target['id'])] = target
    return _subgraph(graph, list(result_nodes.values())[:50], selected_edges[:75])


def neighborhood_contract_graph(graph: dict[str, Any], seed_id: str, max_hops: int = 2) -> dict[str, Any]:
    nodes = [node for node in graph.get('nodes', []) if isinstance(node, dict)]
    edges = [edge for edge in graph.get('edges', []) if isinstance(edge, dict)]
    nodes_by_id = {str(node['id']): node for node in nodes}
    if seed_id not in nodes_by_id:
        return _subgraph(graph, nodes[:50], edges[:75])

    visited = {seed_id}
    queue: deque[tuple[str, int]] = deque([(seed_id, 0)])
    selected_edges: list[dict[str, Any]] = []
    while queue and len(visited) < 50 and len(selected_edges) < 75:
        current, depth = queue.popleft()
        if depth >= max_hops:
            continue
        for edge in edges:
            if edge.get('source') == current:
                other = str(edge.get('target'))
            elif edge.get('target') == current:
                other = str(edge.get('source'))
            else:
                continue
            selected_edges.append(edge)
            if other in nodes_by_id and other not in visited:
                visited.add(other)
                queue.append((other, depth + 1))
    return _subgraph(graph, [nodes_by_id[node_id] for node_id in visited if node_id in nodes_by_id], selected_edges)
