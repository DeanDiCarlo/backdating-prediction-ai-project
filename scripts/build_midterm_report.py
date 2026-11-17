"""Render the report's Markdown source to a letter PDF with 11-point text.

Run: python -m scripts.build_midterm_report
Requires the optional report dependencies. No data downloads are performed.
"""
from __future__ import annotations

import argparse
from html import escape
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    Flowable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]


def inline(text):
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return re.sub(r"\[([^\]]+)\]\((https://[^ )]+)\)", r'<link href="\2" color="#214e72">\1</link>', text)


class Architecture(Flowable):
    def __init__(self):
        super().__init__()
        self.width, self.height = 456, 92

    def draw(self):
        c = self.canv
        c.setFont("Times-Roman", 11)
        for y, label in [(72, "Executed: prices > momentum > portfolio / SPY"),
                         (47, "Executed: SEC > eligible sections > index > passages"),
                         (22, "Planned: cited generation > signals > matched comparison")]:
            c.setFillColor(colors.HexColor("#edf2f6"))
            c.rect(0, y-5, 456, 22, fill=1, stroke=0)
            c.setFillColor(colors.black)
            c.drawString(8, y+2, label)


class Returns(Flowable):
    def __init__(self):
        super().__init__()
        self.width, self.height = 456, 106

    def draw(self):
        c = self.canv
        c.setFont("Times-Roman", 11)
        zero, scale = 273, 1.7
        for i, (name, value) in enumerate([("NVDA", -51.842578), ("XOM", 69.900892), ("Portfolio", 9.029157), ("SPY", -18.743715)]):
            y = 83-i*24
            c.setFillColor(colors.black)
            c.drawString(0, y, name)
            end=zero+value*scale
            c.setFillColor(colors.HexColor("#a64e43" if value < 0 else "#356d82"))
            c.rect(min(zero,end), y-2, abs(value)*scale, 13, fill=1, stroke=0)
            c.setFillColor(colors.black)
            c.drawRightString(454, y, f"{value:.2f}%")
        c.setStrokeColor(colors.grey)
        c.line(zero, 6, zero, 99)


def example(body):
    rows = [["Evidence supplied", "Recorded model response"],
            ["Graphics revenue +29%; Compute & Networking +109% in fiscal 2021.",
             "Summarized the reported segment growth with evidence IDs."],
            ["Third-party production reduces control over quantity and quality.",
             "Identified manufacturing dependence; abstained from an outperformance score."]]
    result=Table([[Paragraph(inline(v),body) for v in row] for row in rows], colWidths=[234,234])
    result.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#edf2f6")),("VALIGN",(0,0),(-1,-1),"TOP"),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    return result


def roadmap(body):
    rows = [("Nov 18–20", "Local inference; data access and price checks"),
            ("Nov 21–24", "Reviewed outputs; freeze coverage and score rules"),
            ("Nov 25–27", "Matched comparison; investigate failures"),
            ("Nov 28–30", "Reproduce results; finalize report and demo")]
    result = Table([[Paragraph(inline(v), body) for v in row] for row in rows],
                   colWidths=[88, 368], hAlign="LEFT")
    result.setStyle(TableStyle([("VALIGN", (0,0),(-1,-1),"TOP"),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[colors.HexColor("#edf3f5"),colors.white]),
        ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)]))
    return result


def build(source, output):
    body = ParagraphStyle("body", fontName="Times-Roman", fontSize=11,
                          leading=13.5, spaceAfter=5)
    heading = ParagraphStyle("heading", parent=body, fontName="Helvetica-Bold", textColor=colors.HexColor("#244858"),
                             spaceBefore=9, spaceAfter=5, keepWithNext=True)
    title = ParagraphStyle("title", parent=heading, fontSize=19, leading=22,
                           alignment=TA_LEFT, spaceAfter=10)
    story, paragraph, table = [], [], []

    def flush():
        if paragraph:
            story.append(Paragraph(inline(" ".join(paragraph)), body))
            paragraph.clear()
        if table:
            cells = [[Paragraph(inline(cell), body) for cell in row] for row in table]
            item = Table(cells, colWidths=[190, 139, 139], repeatRows=1, hAlign="LEFT")
            item.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef3")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LINEBELOW", (0, 0), (-1, 0), .5, colors.grey),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.extend([item, Spacer(1, 5)])
            table.clear()

    for line in source.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            raise ValueError("Fenced code is unsupported in report source; use an explicit figure marker.")
        if line in ("[[architecture]]", "[[returns]]", "[[example]]", "[[roadmap]]"):
            flush()
            story.append({"[[architecture]]": Architecture, "[[returns]]": Returns,
                          "[[example]]": lambda: example(body), "[[roadmap]]": lambda: roadmap(body)}[line]())
            continue
        if line.startswith("[["):
            raise ValueError(f"Unknown report marker: {line}")
        if not line.strip():
            flush()
        elif line.startswith("# "):
            flush()
            story.append(Paragraph(inline(line[2:]), title))
        elif line.startswith("## "):
            flush()
            if line.startswith(('## III.', '## IV.')):
                story.append(PageBreak())
            story.append(Paragraph(inline(line[3:]), heading))
        elif line.startswith("|"):
            if paragraph:
                flush()
            row = [cell.strip() for cell in line.strip("|").split("|")]
            if not all(re.fullmatch(r"[:\- ]+", cell) for cell in row):
                table.append(row)
        else:
            paragraph.append(line)
    flush()
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output), pagesize=letter, leftMargin=72,
                            rightMargin=72, topMargin=72, bottomMargin=72,
                            title="FinSight midpoint report", invariant=1,
                            author="Dean DiCarlo; Nicholas Stanis")
    def footer(canvas, doc):
        canvas.setFont("Times-Roman", 11)
        canvas.setFillColor(colors.HexColor("#52636b"))
        canvas.drawString(72, 45, "FinSight | Midpoint Check-In")
        canvas.drawRightString(540, 45, str(doc.page))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    if source.resolve() == (ROOT / "docs/midpoint-checkin.md").resolve():
        attach_evidence(output)
    print(output)


EVIDENCE = [("1", "nick-reproduction.md"), ("3", "live-nvda.md"), ("4", "manual-nvda-case.md")]


def attach_evidence(output):
    import pymupdf
    with pymupdf.open(output) as document:
        for number, filename in EVIDENCE:
            path = ROOT / "docs/evidence" / filename
            document.embfile_add(filename, path.read_bytes(), filename=filename,
                                 desc=f"Source [{number}]: {filename}")
        for xref in range(1, document.xref_length()):
            if document.xref_get_key(xref, "Type")[1] == "/EmbeddedFile":
                document.xref_set_key(xref, "Params/CreationDate", "null")
                document.xref_set_key(xref, "Params/ModDate", "null")
        data = document.tobytes(no_new_id=True, garbage=4, deflate=True)
    output.write_bytes(data)


def build_evidence(output):
    body = ParagraphStyle("evidence", fontName="Times-Roman", fontSize=11, leading=14, spaceAfter=6)
    heading = ParagraphStyle("evidence_heading", parent=body, fontName="Helvetica-Bold", fontSize=14, leading=17, spaceAfter=12)
    story = []
    for number, filename in EVIDENCE:
        if story:
            story.append(PageBreak())
        story.append(Paragraph(f"FinSight supporting evidence [{number}]", heading))
        story.append(Paragraph("Recorded evidence from the midpoint baseline. These notes preserve execution and review limitations; they do not imply completed contributor approval.", body))
        source_url = "https://github.com/DeanDiCarlo/backdating-prediction-ai-project/blob/453faa7a8423557fed65c25698db4876e2db6838/docs/evidence/" + filename
        story.append(Paragraph(inline(f"[View source {number} on GitHub]({source_url})"), body))
        # Render the complete original note, including commands, as selectable text.
        paragraphs = (ROOT / "docs/evidence" / filename).read_text().split("\n\n")
        for paragraph in paragraphs:
            if paragraph.strip():
                lines = [line for line in paragraph.splitlines() if not line.startswith("```")]
                if not lines:
                    continue
                if lines[0].startswith("#"):
                    story.append(Paragraph(inline(lines[0].lstrip("# ")), heading))
                    lines = lines[1:]
                clean = [line for line in lines if not re.fullmatch(r"[| :\-]+", line)]
                if clean:
                    story.append(Paragraph(inline(" ".join(clean)), body))
    def footer(canvas, doc):
        canvas.setFont("Times-Roman",11)
        canvas.drawString(72,45,"FinSight | Supporting Evidence")
        canvas.drawRightString(540,45,str(doc.page))
    SimpleDocTemplate(str(output), pagesize=letter, leftMargin=72, rightMargin=72,
                      topMargin=72,bottomMargin=72,invariant=1,
                      title="FinSight supporting evidence").build(story,onFirstPage=footer,onLaterPages=footer)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "docs/midpoint-checkin.md")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/midpoint-checkin.pdf")
    args = parser.parse_args()
    build(args.source, args.output)
    if args.source.resolve() == (ROOT / "docs/midpoint-checkin.md").resolve():
        build_evidence(args.output.with_name("FinSight-midpoint-evidence.pdf"))
