"""Render completed contract text as a readable, text-searchable PDF."""
from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer


def render_contract(
    output: Path,
    *,
    title: str,
    sample_id: str,
    variant: str,
    source_file: str,
    completed_text: str,
    demo_terms: list[str],
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ContractTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=22, leading=27, alignment=TA_CENTER, textColor=colors.HexColor("#181818"),
        spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name="Badge", parent=styles["BodyText"], fontName="Helvetica-Bold",
        fontSize=10, leading=14, alignment=TA_CENTER,
        textColor=colors.HexColor("#1d6b40" if variant == "good" else "#a12222"),
        spaceAfter=18,
    ))
    styles.add(ParagraphStyle(
        name="ContractBody", parent=styles["BodyText"], fontName="Times-Roman",
        fontSize=9.3, leading=13, spaceAfter=7, textColor=colors.HexColor("#202020"),
    ))
    styles.add(ParagraphStyle(
        name="ContractHeading", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=11, leading=14, spaceBefore=9, spaceAfter=5,
        textColor=colors.HexColor("#222222"), keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="DemoTerm", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=9.5, leading=14, leftIndent=5 * mm, firstLineIndent=-5 * mm,
        spaceAfter=7,
    ))

    def page(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#d5d5d5"))
        canvas.line(18 * mm, 15 * mm, 192 * mm, 15 * mm)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawString(18 * mm, 10 * mm, f"Synthetic demo - {sample_id}")
        canvas.drawRightString(192 * mm, 10 * mm, f"Page {document.page}")
        canvas.restoreState()

    document = SimpleDocTemplate(
        str(output), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=18 * mm, bottomMargin=20 * mm,
        title=f"{title} - {variant.title()} demo sample",
        author="Shariah Compliance Copilot demo generator",
    )
    story = [
        Spacer(1, 22 * mm),
        Paragraph(escape(title), styles["ContractTitle"]),
        Paragraph(
            "GOOD EXAMPLE - no issue intentionally seeded" if variant == "good"
            else "BAD EXAMPLE - intentionally seeded review issues",
            styles["Badge"],
        ),
        Paragraph(
            f"Synthetic sample ID: {escape(sample_id)}<br/>Source template: {escape(source_file)}",
            styles["BodyText"],
        ),
        Spacer(1, 8 * mm),
        Paragraph(
            "For product demonstration and testing only. This synthetic document is not legal advice, "
            "a Shariah ruling, or an executable agreement. Names, identifiers and transactions are fictional.",
            styles["BodyText"],
        ),
        PageBreak(),
        Paragraph("DEMO COMMERCIAL TERMS", styles["ContractHeading"]),
    ]
    for index, term in enumerate(demo_terms, 1):
        story.append(Paragraph(f"{index}. {escape(term)}", styles["DemoTerm"]))
    story.extend([
        Paragraph(
            "For this synthetic sample, the demo commercial terms above prevail over inconsistent "
            "wording in the historical source template.", styles["ContractBody"],
        ),
        Spacer(1, 3 * mm),
        Paragraph("COMPLETED SOURCE TEMPLATE", styles["ContractHeading"]),
    ])
    for paragraph in completed_text.split("\n\n"):
        clean = paragraph.strip()
        if not clean:
            continue
        is_heading = len(clean) < 95 and (
            clean.isupper() or clean[:2].rstrip(".").isdigit()
            or clean.startswith(("APPENDIX", "Document ", "EXHIBIT "))
        )
        story.append(Paragraph(escape(clean), styles["ContractHeading" if is_heading else "ContractBody"]))
    document.build(story, onFirstPage=page, onLaterPages=page)
