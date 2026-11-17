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
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    Flowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]


def inline(text):
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return re.sub(r"`([^`]+)`", r"\1", text)


class Architecture(Flowable):
    """Vector diagram: status is encoded in labels, not inferred from color."""

    def __init__(self):
        super().__init__()
        self.width, self.height = 468, 146

    def draw(self):
        c = self.canv
        rows = [
            (108, "Yahoo snapshot", "Momentum / top two", "Matched SPY returns", "MEASURED; REPRODUCED IN NICK'S WORKSPACE"),
            (62, "SEC eligibility / HTML", "Sections / chunks / index", "Retrieval / mock score", "IMPLEMENTED; FIXTURE-TESTED"),
            (16, "Real qualitative signals", "Join with quant scores", "Matched comparison", "PLANNED"),
        ]
        for y, *labels, status in rows:
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.HexColor("#365269"))
            c.drawString(0, y + 22, status)
            for i, label in enumerate(labels):
                x = i * 158
                c.setStrokeColor(colors.HexColor("#9baab6"))
                c.setFillColor(colors.HexColor("#f2f5f7"))
                c.roundRect(x, y, 150, 18, 3, fill=1)
                c.setFillColor(colors.black)
                c.drawCentredString(x + 75, y + 6, label)
                if i < 2:
                    c.line(x + 150, y + 9, x + 157, y + 9)
                    c.line(x + 157, y + 9, x + 154, y + 12)
                    c.line(x + 157, y + 9, x + 154, y + 6)


def build(source, output):
    body = ParagraphStyle("body", fontName="Times-Roman", fontSize=11,
                          leading=12, spaceAfter=4)
    heading = ParagraphStyle("heading", parent=body, fontName="Times-Bold",
                             spaceBefore=7, spaceAfter=4, keepWithNext=True)
    title = ParagraphStyle("title", parent=heading, fontSize=14, leading=16,
                           alignment=TA_CENTER, spaceAfter=7)
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

    in_code = False
    for line in source.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            flush()
            in_code = not in_code
            if in_code:
                story.append(Architecture())
            continue
        if in_code or line.startswith("System diagram specification"):
            continue
        if not line.strip():
            flush()
        elif line.startswith("# "):
            flush()
            story.append(Paragraph(inline(line[2:]), title))
        elif line.startswith("## "):
            flush()
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
                            title="FinSight midpoint report",
                            author="Dean DiCarlo; Nicholas Stanis")
    doc.build(story)
    print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "docs/midterm-draft.md")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/midterm-report.pdf")
    args = parser.parse_args()
    build(args.source, args.output)
