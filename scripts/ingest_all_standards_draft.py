#!/usr/bin/env python3
"""Ingest every AAOIFI standard in the supplied English compilation as draft records.

This is a complete-source ingestion, not a publication step.  Each readable page
becomes a traceable source record.  SS 8's separately validated structure-first
clause records remain intact and coexist with these full-standard page records.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import re
from collections import Counter
from pathlib import Path
from uuid import UUID, uuid5

import asyncpg
from PyPDF2 import PdfReader

NAMESPACE = UUID('c6ca3d31-23c1-4d8c-9e77-f2d0fa10e8dd')
SOURCE = Path('/data/Shariaa-Standards-ENG.pdf')
EDITION = 'Shari’ah Standards (2015)'
# Verified from the published table of contents and cover pages. Each start is
# the PDF cover page; the next cover defines the previous standard's boundary.
STANDARDS: tuple[tuple[str, str, int], ...] = (
    ('1', 'Trading in Currencies', 48),
    ('2', 'Debit Card, Charge Card and Credit Card', 68),
    ('3', 'Procrastinating Debtor (Revised Standard)', 84),
    ('4', 'Settlement of Debts by Set-Off (Revised Standard)', 104),
    ('5', 'Guarantees (Revised Standard)', 120),
    ('6', 'Conversion of a Conventional Bank to an Islamic Bank', 148),
    ('7', 'Hawalah', 172),
    ('8', 'Murabahah (Revised Standard)', 196),
    ('9', 'Ijarah and Ijarah Muntahia Bittamleek (Revised Standard)', 234),
    ('10', 'Salam and Parallel Salam (Revised Standard)', 268),
    ('11', 'Istisna’a and Parallel Istisna’a (Revised Standard)', 292),
    ('12', 'Sharikah (Musharakah) and Modern Corporations (Revised Standard)', 322),
    ('13', 'Mudarabah (Revised Standard)', 366),
    ('14', 'Documentary Credit (Revised Standard)', 392),
    ('15', 'Ju’alah (Revised Standard)', 422),
    ('16', 'Commercial Papers (Revised Standard)', 440),
    ('17', 'Investment Sukuk', 464),
    ('18', 'Possession (Qabd)', 490),
    ('19', 'Loan (Qard)', 514),
    ('20', 'Sale of Commodities in Organized Markets', 536),
    ('21', 'Financial Paper (Shares and Bonds)', 556),
    ('22', 'Concession Contracts', 584),
    ('23', 'Agency and the Act of an Uncommissioned Agent (Fodooli)', 606),
    ('24', 'Syndicated Financing', 630),
    ('25', 'Combination of Contracts', 648),
    ('26', 'Islamic Insurance', 674),
    ('27', 'Indices', 702),
    ('28', 'Banking Services in Islamic Banks', 720),
    ('29', 'Stipulations and Ethics of Fatwa in the Institutional Framework', 734),
    ('30', 'Monetization (Tawarruq)', 754),
    ('31', 'Controls on Gharar in Financial Transactions', 768),
    ('32', 'Arbitration', 790),
    ('33', 'Waqf', 810),
    ('34', 'Hiring of Persons', 840),
    ('35', 'Zakah', 866),
    ('36', 'Impact of Contingent Incidents on Commitments', 906),
    ('37', 'Credit Agreement', 922),
    ('38', 'Online Financial Dealings', 944),
    ('39', 'Mortgage and Its Contemporary Applications', 964),
    ('40', 'Distribution of Profit in Mudarabah-Based Investment Accounts', 990),
    ('41', 'Islamic Reinsurance', 1014),
    ('42', 'Financial Rights and How They Are Exercised and Transferred', 1040),
    ('43', 'Insolvency', 1062),
    ('44', 'Obtaining and Deploying Liquidity', 1084),
    ('45', 'Protection of Capital and Investments', 1098),
    ('46', 'Al-Wakalah Bi Al-Istithmar (Investment Agency)', 1116),
    ('47', 'Rules for Calculating Profit in Financial Transactions', 1134),
    ('48', 'Options to Terminate Due to Breach of Trust (Trust-Based Options)', 1146),
    ('49', 'Unilateral and Bilateral Promise', 1160),
    ('50', 'Irrigation Partnership (Musaqat)', 1176),
    ('51', 'Options to Revoke Contracts Due to Incomplete Performance', 1198),
    ('52', 'Options to Reconsider (Cooling-Off Options, Either-Or Options, and Options to Revoke Due to Non-Payment)', 1214),
    ('53', '’Arboun (Earnest Money)', 1232),
    ('54', 'Revocation of Contracts by Exercise of a Cooling-Off Option', 1246),
)
SOURCE_END = 1259
PAGE_NUMBER = re.compile(r'^\d{1,6}$')
RUNNING_HEADER = re.compile(r"^Shari[’']ah Standard No\. \(\d+\):")


def stable_id(name: str) -> UUID:
    return uuid5(NAMESPACE, name)


def collapse(value: str) -> str:
    return re.sub(r'\s+', ' ', value).strip()


def undupe_line(line: str) -> str:
    line = collapse(line)
    if len(line) >= 2 and len(line) % 2 == 0 and line[:len(line) // 2] == line[len(line) // 2:]:
        return line[:len(line) // 2].strip()
    words = line.split()
    if len(words) >= 8 and len(words) % 2 == 0 and words[:len(words) // 2] == words[len(words) // 2:]:
        return ' '.join(words[:len(words) // 2])
    return line


def clean_lines(raw: str) -> list[str]:
    lines: list[str] = []
    for source_line in raw.splitlines():
        line = undupe_line(source_line)
        if not line or PAGE_NUMBER.fullmatch(line) or RUNNING_HEADER.match(line):
            continue
        lines.append(line)
    return lines


def extract_records() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    pdf = PdfReader(str(SOURCE))
    for index, (number, title, start) in enumerate(STANDARDS):
        end = STANDARDS[index + 1][2] - 1 if index + 1 < len(STANDARDS) else SOURCE_END
        for source_page in range(start, end + 1):
            lines = clean_lines(pdf.pages[source_page - 1].extract_text() or '')
            text = collapse(' '.join(lines))
            if len(text) < 40:
                continue
            records.append({
                'standard_number': number,
                'title': title,
                'clause_id': f'page:{source_page}',
                'text': text,
                'source_page': source_page,
                'printed_page': source_page - 1,
                'breadcrumb': f'Full source > AAOIFI SS {number} > PDF page {source_page}',
            })
    return records


async def ingest(dsn: str, replace: bool) -> None:
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    records = extract_records()
    counts = Counter(str(item['standard_number']) for item in records)
    missing = [number for number, _, _ in STANDARDS if counts[number] == 0]
    if missing:
        raise ValueError(f'no readable source records for standards: {", ".join(missing)}')
    if len(records) < 850:
        raise ValueError(f'expected a full-source corpus, got only {len(records)} records')

    run_id = stable_id(f'aaoifi:all-standards:{source_hash}:draft-run')
    connection = await asyncpg.connect(dsn)
    try:
        async with connection.transaction():
            await connection.execute(
                '''INSERT INTO ingestion_run (id, source_checksum, source_filename, parser_version, approval_status)
                   VALUES ($1, $2, $3, $4, 'draft')
                   ON CONFLICT (id) DO NOTHING''',
                run_id, source_hash, SOURCE.name, 'all-standards-page-source-v1',
            )
            for number, title, _ in STANDARDS:
                standard_id = stable_id(f'aaoifi:ss{number}:{source_hash}:draft-standard')
                await connection.execute(
                    '''INSERT INTO standard (id, authority, standard_number, title, edition, language, source_checksum, approval_status)
                       VALUES ($1, 'AAOIFI', $2, $3, $4, 'en', $5, 'draft')
                       ON CONFLICT (authority, standard_number, edition, language, source_checksum) DO NOTHING''',
                    standard_id, number, title, EDITION, source_hash,
                )
                if replace:
                    await connection.execute(
                        "DELETE FROM clause WHERE standard_id = $1 AND clause_id LIKE 'page:%'", standard_id,
                    )
            for record in records:
                number = str(record['standard_number'])
                standard_id = stable_id(f'aaoifi:ss{number}:{source_hash}:draft-standard')
                clause_id = str(record['clause_id'])
                await connection.execute(
                    '''INSERT INTO clause (
                         id, standard_id, clause_id, parent_clause_id, breadcrumb,
                         verbatim_text, embedding_text, source_pdf_page_start, source_pdf_page_end,
                         printed_page_start, printed_page_end, language, approval_status
                       ) VALUES ($1, $2, $3, NULL, $4, $5, $5, $6, $6, $7, $7, 'en', 'draft')
                       ON CONFLICT (standard_id, clause_id) DO UPDATE SET
                         breadcrumb = EXCLUDED.breadcrumb,
                         verbatim_text = EXCLUDED.verbatim_text,
                         embedding_text = EXCLUDED.embedding_text,
                         source_pdf_page_start = EXCLUDED.source_pdf_page_start,
                         source_pdf_page_end = EXCLUDED.source_pdf_page_end,
                         printed_page_start = EXCLUDED.printed_page_start,
                         printed_page_end = EXCLUDED.printed_page_end,
                         approval_status = 'draft' ''',
                    stable_id(f'aaoifi:ss{number}:{source_hash}:source-page:{clause_id}'),
                    standard_id, clause_id, record['breadcrumb'], record['text'],
                    record['source_page'], record['printed_page'],
                )
    finally:
        await connection.close()

    print(f'Imported {len(records)} full-source page records across {len(counts)} AAOIFI standards.')
    print('Standard page-record counts:', ', '.join(f'SS {number}: {counts[number]}' for number, _, _ in STANDARDS))
    print(f'Source SHA-256: {source_hash}')
    print('Status: draft only; source rights, Arabic precedence handling, and scholar approval remain required before publication.')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--dsn', required=True)
    parser.add_argument('--replace', action='store_true')
    args = parser.parse_args()
    asyncio.run(ingest(args.dsn, args.replace))


if __name__ == '__main__':
    main()
