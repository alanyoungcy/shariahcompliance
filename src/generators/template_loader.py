"""Extract the actual source PDFs and fill only explicitly mapped placeholders.

The catalog pins each source file and its ordered placeholders. A changed PDF
must be inspected and mapped again; guessing at a financial field is unsafe.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = Path(__file__).with_name("template_catalog.json")
BLANK = re.compile(
    r"\[[^\[\]]{0,180}\]|_{2,}|\.{3,}|-{3,}|\(currency and amount\)|\(insert[^)]{0,180}\)",
    re.IGNORECASE,
)


def catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(str.maketrans({"“": '"', "”": '"', "’": "'", "‘": "'", "–": "-", "—": "-"}))
    return re.sub(r"\s+", " ", text).strip()


def extract_source(path: Path) -> tuple[str, int]:
    reader = PdfReader(path)
    if reader.is_encrypted:
        raise ValueError(f"Encrypted template: {path.name}")
    pages = []
    for page in reader.pages:
        text = re.sub(r"https://ethica\.institute|!\d+", "", page.extract_text() or "")
        # Keep paragraph boundaries, but allow sentences to flow across pages.
        pages.append(text.replace("\u2028", "\n"))
    text = "\n".join(pages)
    paragraphs = [normalize(part) for part in re.split(r"\n\s*\n", text)]
    text = "\n\n".join(part for part in paragraphs if part)
    if len(text) < 100:
        raise ValueError(f"No readable template text: {path.name}; a text-based PDF is required.")
    # Repairs are deliberately narrow and recorded in the catalog documentation.
    text = text.replace("[Insert name of the Agent)", "[Insert name of the Agent]")
    text = text.replace("shall be date]", "shall be [delivery date]")
    text = text.replace("Salam Document # ;", "Salam Document # [receiving note];")
    text = text.replace("lump sum on , or", "lump sum on [repayment date], or")
    text = re.sub(r"(_+)\s*2001", r"\1 [agreement year]", text)
    text = text.replace("20XX", "[agreement year]")
    text = text.replace("200 ________", "________")
    return text, len(reader.pages)


def inspect_template(path: Path) -> dict:
    text, pages = extract_source(path)
    return {
        "file": path.name,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "source_pages": pages,
        "fields": [
            {"id": i, "placeholder": m.group(), "before": normalize(text[max(0, m.start()-90):m.start()]),
             "after": normalize(text[m.end():m.end()+90])}
            for i, m in enumerate(BLANK.finditer(text), 1)
        ],
    }


def load_template(key: str, directory: Path) -> tuple[str, dict]:
    definition = catalog()[key]
    path = directory / definition["file"]
    if not path.is_file():
        raise ValueError(f"Template not found: {path}")
    if hashlib.sha256(path.read_bytes()).hexdigest() != definition["sha256"]:
        raise ValueError(f"Template changed: {path.name}. Run --inspect-template and update its field mapping first.")
    text, _ = extract_source(path)
    if len(list(BLANK.finditer(text))) != len(definition["fields"]):
        raise ValueError(f"Placeholder count changed for {path.name}; inspect the mapping before generating.")
    return text, definition


def fill_template(text: str, definition: dict, values: dict[str, str]) -> tuple[str, list[dict]]:
    fields = iter(enumerate(definition["fields"], 1))
    audit = []

    def fill(match: re.Match) -> str:
        index, field = next(fields)
        if field["placeholder"] != match.group():
            raise ValueError(f"Placeholder {index} changed in {definition['file']}.")
        replacement = field["value"].format_map(values)
        audit.append({"id": index, "placeholder": match.group(), "value": replacement,
                      "mapping": field["value"]})
        # Many originals have no spaces around underscores: at_____on, _____only.
        left = " " if match.start() and text[match.start()-1].isalnum() else ""
        right = " " if match.end() < len(text) and text[match.end()].isalnum() else ""
        return left + replacement + right

    filled = BLANK.sub(fill, text)
    # No bracket instructions, ellipsis lines or repeated underscores may survive.
    if BLANK.search(filled):
        raise ValueError(f"Unfilled placeholder in {definition['file']}")
    return filled, audit
