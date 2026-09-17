#!/usr/bin/env python3
"""Create a source-traceable SS 8 draft corpus from the supplied AAOIFI PDF.

This imports only the Statement of the Standard pages. It deliberately writes DRAFT
records: an administrator and qualified scholar must review the preview and record
rights/Arabic-precedence handling before a separate approval step can publish it.
"""
from __future__ import annotations

import argparse
import hashlib
import re
from collections import Counter
from pathlib import Path
from uuid import UUID, uuid5

import asyncpg
import pdfplumber

NAMESPACE = UUID('c6ca3d31-23c1-4d8c-9e77-f2d0fa10e8dd')
SOURCE = Path('/data/Shariaa-Standards-ENG.pdf')
SOURCE_START = 201
SOURCE_END = 215
HEADER = 'Shari’ah Standard No. (8): Murabahah'
# A numbered clause may itself be a short parent heading (for example, "2/4
# Commissions and expenses").  Keep those hierarchy records even though they
# are not citation leaves; the later grammar check filters inline references.
CLAUSE_RE = re.compile(r'^\s*(?P<id>[1-5]/\d+(?:/\d+)?)\s+(?P<text>.+)$')
SECTION_RE = re.compile(r'^\s*(?P<number>[1-6])\.\s+(?P<title>.+)$')
PAGE_RE = re.compile(r'^\d{3,6}$')


def stable_id(name: str) -> UUID:
    return uuid5(NAMESPACE, name)


def collapse(value: str) -> str:
    return re.sub(r'\s+', ' ', value).strip()


def undupe_line(line: str) -> str:
    line = line.strip()
    if len(line) >= 2 and len(line) % 2 == 0 and line[:len(line) // 2] == line[len(line) // 2:]:
        return line[:len(line) // 2].strip()
    # PyPDF2 sometimes repeats fragments, rather than whole lines, on the affected source.
    words = line.split()
    if len(words) >= 8 and len(words) % 2 == 0 and words[:len(words) // 2] == words[len(words) // 2:]:
        return ' '.join(words[:len(words) // 2])
    return line


def clean_page(raw: str, printed_page: int) -> list[str]:
    result: list[str] = []
    for source_line in raw.splitlines():
        line = undupe_line(source_line)
        if not line or line == HEADER or PAGE_RE.fullmatch(line):
            continue
        # The footer may be duplicated as 200200 on this source.
        if line == f'{printed_page}{printed_page}' or line == str(printed_page):
            continue
        result.append(line)
    return result


def parse() -> tuple[list[dict[str, object]], str]:
    clauses: list[dict[str, object]] = []
    section = 'Statement of the Standard'
    current: dict[str, object] | None = None
    all_clean: list[str] = []

    with pdfplumber.open(str(SOURCE)) as pdf:
        for source_page in range(SOURCE_START, SOURCE_END + 1):
            printed_page = source_page - 1
            # The supplied English compilation duplicates glyphs in its text layer.
            # Geometry-aware de-duplication restores one readable source line.
            page = pdf.pages[source_page - 1].dedupe_chars(tolerance=1)
            lines = clean_page(page.extract_text(x_tolerance=2, y_tolerance=3) or '', printed_page)
            all_clean.extend(lines)
            for line in lines:
                section_match = SECTION_RE.match(line)
                if section_match:
                    if current is not None:
                        clauses.append(current)
                    section_number = section_match.group('number')
                    section = f"{section_number}. {collapse(section_match.group('title'))}"
                    # Section 1 has normative scope text but no N/N leaf in this source.
                    current = ({
                        'clause_id': '1',
                        'text': '',
                        'section': section,
                        'source_start': source_page,
                        'source_end': source_page,
                        'printed_start': printed_page,
                        'printed_end': printed_page,
                    } if section_number == '1' else None)
                    continue
                match = CLAUSE_RE.match(line)
                # Inline cross-references sometimes begin a wrapped source line. A valid
                # heading must carry a substantive sentence, not merely a reference.
                if match and not re.search(r'[A-Za-z]', match.group('text')):
                    match = None
                # Direct N/N items can be short hierarchy labels ("2/4
                # Commissions and expenses").  A short N/N/N fragment in
                # body text is an inline cross-reference, such as "3/1/5
                # should be observed", rather than a new leaf.
                if match and match.group('id').count('/') == 2 and len(match.group('text').split()) < 4:
                    match = None
                if match and current is not None and match.group('id') == current['clause_id']:
                    remainder = match.group('text')
                    if remainder and remainder not in str(current['text']):
                        current['text'] = f"{current['text']} {remainder}"
                    current['source_end'] = source_page
                    current['printed_end'] = printed_page
                    continue
                if match:
                    if current is not None:
                        clauses.append(current)
                    current = {
                        'clause_id': match.group('id'),
                        'text': match.group('text'),
                        'section': section,
                        'source_start': source_page,
                        'source_end': source_page,
                        'printed_start': printed_page,
                        'printed_end': printed_page,
                    }
                    continue
                if current is not None:
                    current['text'] = f"{current['text']} {line}"
                    current['source_end'] = source_page
                    current['printed_end'] = printed_page
    if current is not None:
        clauses.append(current)

    output: list[dict[str, object]] = []
    seen: set[str] = set()
    for clause in clauses:
        clause_id = str(clause['clause_id'])
        if clause_id in seen:
            raise ValueError(f'duplicate clause id: {clause_id}')
        seen.add(clause_id)
        text = collapse(str(clause['text']))
        if len(text) < 20:
            continue
        parent = clause_id.rsplit('/', 1)[0] if clause_id.count('/') >= 2 else None
        output.append({**clause, 'text': text, 'parent': parent, 'breadcrumb': f"Statement of the Standard > {clause['section']} > {clause_id}"})
    return output, '\n'.join(all_clean)


async def ingest(dsn: str, replace: bool) -> None:
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    clauses, clean_text = parse()
    ids = [str(value['clause_id']) for value in clauses]
    expected = {'3/1/1', '3/2/2', '4/6', '5/6', '5/8'}
    missing = expected - set(ids)
    if missing:
        raise ValueError(f'critical SS 8 clauses were not parsed: {sorted(missing)}')
    hierarchy = Counter(value['clause_id'].count('/') for value in clauses)
    # Validated against the rendered Statement of the Standard: one scope
    # record, 28 direct records (including seven parent headings), and 42
    # nested rule leaves.  A change here requires a fresh visual review.
    if len(clauses) != 71 or hierarchy != Counter({0: 1, 1: 28, 2: 42}):
        raise ValueError(
            'unexpected SS 8 hierarchy: '
            f'{len(clauses)} records with depth counts {dict(hierarchy)}'
        )
    if 'LIBOR' not in clean_text.upper():
        raise ValueError('source validation failed: expected LIBOR reference was not extracted')

    run_id = stable_id(f'aaoifi:ss8:{source_hash}:draft-run')
    standard_id = stable_id(f'aaoifi:ss8:{source_hash}:draft-standard')
    connection = await asyncpg.connect(dsn)
    try:
        async with connection.transaction():
            if replace:
                await connection.execute('DELETE FROM clause WHERE standard_id = $1', standard_id)
                await connection.execute('DELETE FROM standard WHERE id = $1', standard_id)
            await connection.execute(
                '''INSERT INTO ingestion_run (id, source_checksum, source_filename, parser_version, approval_status)
                   VALUES ($1, $2, $3, $4, 'draft')
                   ON CONFLICT (id) DO NOTHING''',
                run_id, source_hash, SOURCE.name, 'ss8-structure-first-v1',
            )
            await connection.execute(
                '''INSERT INTO standard (id, authority, standard_number, title, edition, language, source_checksum, approval_status)
                   VALUES ($1, 'AAOIFI', '8', 'Murabahah (Revised Standard)', 'Shari’ah Standards (2015)', 'en', $2, 'draft')
                   ON CONFLICT (authority, standard_number, edition, language, source_checksum) DO NOTHING''',
                standard_id, source_hash,
            )
            for clause in clauses:
                clause_id = str(clause['clause_id'])
                await connection.execute(
                    '''INSERT INTO clause (
                        id, standard_id, clause_id, parent_clause_id, breadcrumb,
                        verbatim_text, embedding_text, source_pdf_page_start, source_pdf_page_end,
                        printed_page_start, printed_page_end, language, approval_status
                    ) VALUES ($1, $2, $3, $4, $5, $6, $6, $7, $8, $9, $10, 'en', 'draft')
                    ON CONFLICT (standard_id, clause_id) DO UPDATE SET
                      parent_clause_id = EXCLUDED.parent_clause_id,
                      breadcrumb = EXCLUDED.breadcrumb,
                      verbatim_text = EXCLUDED.verbatim_text,
                      embedding_text = EXCLUDED.embedding_text,
                      source_pdf_page_start = EXCLUDED.source_pdf_page_start,
                      source_pdf_page_end = EXCLUDED.source_pdf_page_end,
                      printed_page_start = EXCLUDED.printed_page_start,
                      printed_page_end = EXCLUDED.printed_page_end,
                      approval_status = 'draft' ''',
                    stable_id(f'aaoifi:ss8:{source_hash}:clause:{clause_id}'), standard_id, clause_id,
                    clause['parent'], clause['breadcrumb'], clause['text'], clause['source_start'],
                    clause['source_end'], clause['printed_start'], clause['printed_end'],
                )
    finally:
        await connection.close()
    counts = Counter(item['clause_id'].count('/') for item in clauses)
    print(f'Imported SS 8 draft: {len(clauses)} clause records ({counts[1]} direct, {counts[2]} subclauses).')
    print(f'Source SHA-256: {source_hash}')
    print('Status: draft only; nothing has been published for semantic retrieval.')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--dsn', required=True)
    parser.add_argument('--replace', action='store_true')
    args = parser.parse_args()
    import asyncio
    asyncio.run(ingest(args.dsn, args.replace))


if __name__ == '__main__':
    main()
