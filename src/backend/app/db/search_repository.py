from __future__ import annotations

import asyncio
import re
from collections.abc import Awaitable
from collections import defaultdict
from typing import Any

import asyncpg

from app.models import SearchRequest

CITATION_PATTERN = re.compile(r'(?i)\b(?:ss|standard)\s*([0-9]+)\s*(?:·|/)\s*([0-9]+(?:/[0-9]+)?)\b')

BASE_FIELDS = '''
  c.id AS clause_db_id,
  standard.authority,
  standard.standard_number,
  standard.title,
  c.clause_id,
  c.verbatim_text,
  c.printed_page_start,
  c.printed_page_end,
  c.source_pdf_page_start,
  c.source_pdf_page_end
'''

SPARSE_SQL = f'''
SELECT {BASE_FIELDS}
FROM clause c
JOIN standard ON standard.id = c.standard_id
WHERE c.embedding_text ||| $1
  AND c.approval_status = 'approved'
  AND standard.approval_status = 'approved'
  AND standard.authority = $2
  AND ($3::text IS NULL OR standard.standard_number = $3)
  AND c.language = $4
ORDER BY pdb.score(c.id) DESC, c.id
LIMIT $5
'''

DENSE_SQL = f'''
SELECT {BASE_FIELDS}
FROM clause c
JOIN standard ON standard.id = c.standard_id
WHERE c.id @@@ pdb.all()
  AND c.embedding IS NOT NULL
  AND c.approval_status = 'approved'
  AND standard.approval_status = 'approved'
  AND standard.authority = $2
  AND ($3::text IS NULL OR standard.standard_number = $3)
  AND c.language = $4
ORDER BY c.embedding <=> $1::vector, c.id
LIMIT $5
'''

DIRECT_SQL = f'''
SELECT {BASE_FIELDS}
FROM clause c
JOIN standard ON standard.id = c.standard_id
WHERE standard.standard_number = $1
  AND c.clause_id = $2
  AND c.approval_status = 'approved'
  AND standard.approval_status = 'approved'
  AND standard.authority = $3
  AND c.language = $4
LIMIT 1
'''


def citation_terms(query: str) -> tuple[str, str] | None:
    match = CITATION_PATTERN.search(query)
    return (match.group(1), match.group(2)) if match else None


def row_to_candidate(row: asyncpg.Record) -> dict[str, Any]:
    return {
        'clause_db_id': row['clause_db_id'],
        'citation': {
            'authority': row['authority'],
            'standard_number': row['standard_number'],
            'title': row['title'],
            'clause_id': row['clause_id'],
            'printed_page_start': row['printed_page_start'],
            'printed_page_end': row['printed_page_end'],
            'source_pdf_page_start': row['source_pdf_page_start'],
            'source_pdf_page_end': row['source_pdf_page_end'],
        },
        'excerpt': row['verbatim_text'][:700],
    }


class SearchRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self.pool = pool

    async def _fetch(self, sql: str, *params: Any) -> list[asyncpg.Record]:
        async with self.pool.acquire() as connection:
            return await connection.fetch(sql, *params)

    async def search(self, request: SearchRequest) -> tuple[list[dict[str, Any]], bool, bool]:
        citation = citation_terms(request.query)
        pending: list[Awaitable[list[asyncpg.Record]]] = [
            self._fetch(
                SPARSE_SQL,
                request.query,
                request.authority,
                request.standard_number,
                request.language,
                request.limit,
            ),
        ]
        branch_names = ['sparse']

        if request.query_embedding is not None:
            vector_literal = '[' + ','.join(str(value) for value in request.query_embedding) + ']'
            pending.append(self._fetch(
                DENSE_SQL,
                vector_literal,
                request.authority,
                request.standard_number,
                request.language,
                request.limit,
            ))
            branch_names.append('dense')

        if citation is not None:
            pending.append(self._fetch(
                DIRECT_SQL,
                citation[0],
                citation[1],
                request.authority,
                request.language,
            ))
            branch_names.append('direct')

        branch_rows = await asyncio.gather(*pending)
        candidates: dict[Any, dict[str, Any]] = {}
        ranks: dict[Any, dict[str, int]] = defaultdict(dict)

        for branch, rows in zip(branch_names, branch_rows, strict=True):
            for position, row in enumerate(rows, start=1):
                clause_id = row['clause_db_id']
                candidates[clause_id] = row_to_candidate(row)
                ranks[clause_id][branch] = position

        results = []
        for clause_id, candidate in candidates.items():
            branch_ranks = ranks[clause_id]
            fused_score = sum(1.0 / (60 + rank) for rank in branch_ranks.values())
            if 'direct' in branch_ranks:
                fused_score += 1.0
            results.append({**candidate, 'branch_ranks': branch_ranks, 'fused_score': fused_score})

        results.sort(key=lambda result: (-result['fused_score'], str(result['clause_db_id'])))
        return results[:request.limit], True, request.query_embedding is not None
