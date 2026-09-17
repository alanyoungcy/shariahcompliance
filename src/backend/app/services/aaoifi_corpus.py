from __future__ import annotations

import re
from typing import Any

import asyncpg

# Draft source records span the full supplied AAOIFI compilation. Each uploaded
# contract receives only a small relevance-selected pack from the full corpus.
MAX_CANDIDATE_SOURCES = 12
_STOP_WORDS = frozenset({
    'about', 'after', 'against', 'also', 'among', 'and', 'any', 'are', 'as', 'at', 'be',
    'been', 'between', 'by', 'can', 'contract', 'customer', 'for', 'from', 'has', 'have',
    'in', 'into', 'is', 'it', 'its', 'of', 'on', 'or', 'shall', 'that', 'the', 'their',
    'this', 'to', 'under', 'which', 'with', 'will', 'would',
})


def _retrieval_query(contract_text: str) -> str:
    """Create a bounded lexical query without sending the corpus to the model."""
    words = re.findall(r"[A-Za-z][A-Za-z'’-]{2,}", contract_text.lower())
    selected: list[str] = []
    seen: set[str] = set()
    for word in words:
        if word in _STOP_WORDS or word in seen:
            continue
        seen.add(word)
        selected.append(word)
        if len(selected) == 120:
            break
    return ' '.join(selected) or 'contract review'


async def retrieve_candidate_sources(pool: asyncpg.Pool, contract_text: str) -> list[dict[str, Any]]:
    """Return a small, source-traceable pack from all 54 draft standards."""
    async with pool.acquire() as connection:
        rows = await connection.fetch(
            '''SELECT
                 s.authority, s.standard_number, s.title, s.edition,
                 c.clause_id, c.verbatim_text,
                 c.source_pdf_page_start, c.source_pdf_page_end,
                 c.printed_page_start, c.printed_page_end
               FROM clause c
               JOIN standard s ON s.id = c.standard_id
               WHERE s.authority = 'AAOIFI'
                 AND s.approval_status = 'draft'
                 AND c.approval_status = 'draft'
                 AND c.embedding_text ||| $1
               ORDER BY pdb.score(c.id) DESC, c.id
               LIMIT $2''',
            _retrieval_query(contract_text), MAX_CANDIDATE_SOURCES,
        )
    sources: list[dict[str, Any]] = []
    for row in rows:
        source = dict(row)
        source['source_key'] = f"SS {source['standard_number']} {source['clause_id']}"
        sources.append(source)
    return sources
