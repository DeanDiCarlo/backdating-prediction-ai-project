"""Best-effort section extraction from SEC HTML filings."""
from __future__ import annotations

from html.parser import HTMLParser
import re


class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style"):
            self.skip += 1
        elif tag in ("p", "div", "br", "tr", "h1", "h2", "h3"):
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style") and self.skip:
            self.skip -= 1
        elif tag in ("p", "div", "tr", "h1", "h2", "h3"):
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.skip:
            self.parts.append(data)


def readable_text(raw: bytes) -> str:
    parser = _Text()
    parser.feed(raw.decode("utf-8", errors="replace"))
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in "".join(parser.parts).splitlines()]
    return "\n".join(line for line in lines if line)


def extract_sections(raw: bytes, form: str) -> dict[str, str]:
    """Prefer the last matching heading to avoid most table-of-contents hits."""
    text = readable_text(raw)
    patterns = ({
        "management_discussion": r"(?im)^item\s*7[.\s:—-]+management.{0,180}$",
        "risk_factors": r"(?im)^item\s*1a[.\s:—-]+risk factors?.{0,80}$",
    } if form == "10-K" else {
        "management_discussion": r"(?im)^item\s*2[.\s:—-]+management.{0,180}$",
        "risk_factors": r"(?im)^item\s*1a[.\s:—-]+risk factors?.{0,80}$",
    })
    headings = list(re.finditer(r"(?im)^item\s*(?:\d+[a-z]?)[.\s:—-]+[^\n]{2,180}$", text))
    sections = {}
    for key, pattern in patterns.items():
        matches = list(re.finditer(pattern, text))
        if not matches:
            sections[key] = ""
            continue
        start = matches[-1].end()
        end = next((h.start() for h in headings if h.start() > start), len(text))
        sections[key] = text[start:end].strip()
    return sections
