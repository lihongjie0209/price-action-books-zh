#!/usr/bin/env python3
"""Extract Trading Price Action TRENDS PDF to Markdown and split by TOC chapters."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import fitz

PDF_PATH = Path("/root/book/Trading Price Action TRENDS.pdf")
ROOT = Path(__file__).resolve().parents[1]
EN_DIR = ROOT / "en"
CHAPTERS_DIR = EN_DIR / "chapters"
FULL_MD = EN_DIR / "full_book.md"
INVENTORY = ROOT / "notes" / "chapter_inventory.md"
CONVERSION_NOTES = ROOT / "notes" / "conversion_notes.md"


def slugify(title: str) -> str:
    s = title.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"[\s_]+", "-", s).strip("-")
    s = re.sub(r"-+", "-", s)
    return s[:80] or "section"


def normalize_text(text: str) -> str:
    # Fix common PDF hyphenation at line breaks: "fol- lowed" -> "followed"
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    # Collapse runs of spaces but keep newlines
    text = re.sub(r"[ \t]+", " ", text)
    # Normalize Windows newlines
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Drop isolated page-number-only lines that are just digits
    lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        if re.fullmatch(r"\d{1,3}", stripped):
            continue
        # Drop repeated running headers that are all-caps short titles
        lines.append(line.rstrip())
    text = "\n".join(lines)
    # Paragraph join: single newlines inside paragraphs become spaces when
    # next line starts lowercase or continues mid-sentence (heuristic)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def page_to_markdown(page_num_1based: int, text: str) -> str:
    if not text.strip():
        return f"\n\n<!-- PDF page {page_num_1based}: no extractable text (likely figure-only) -->\n\n"
    body = normalize_text(text)
    return f"\n\n<!-- PDF page {page_num_1based} -->\n\n{body}\n"


def clean_title(title: str) -> str:
    title = re.sub(r"\s+", " ", title).strip()
    # PDF TOC sometimes concatenates without spaces
    title = title.replace("TradingPriceActionTRENDS", "Trading Price Action TRENDS")
    return title


def heading_for(level: int, title: str) -> str:
    # Map PDF outline levels to markdown: L1/L2 -> # or ##, L3 chapters -> ##
    depth = min(max(level, 1), 3)
    return f"{'#' * depth} {title}\n"


def build_units(toc: list[tuple[int, str, int]], page_count: int):
    """Build split units from TOC. Page numbers from get_toc are 1-based PDF pages."""
    # Skip decorative root title if present
    entries = []
    for level, title, page in toc:
        title = clean_title(title)
        if title.lower() in {"trading price action trends", "tradingpriceactiontrends"}:
            continue
        entries.append((level, title, page))

    units = []
    for i, (level, title, start) in enumerate(entries):
        end = entries[i + 1][2] - 1 if i + 1 < len(entries) else page_count
        start = max(1, min(start, page_count))
        end = max(start, min(end, page_count))
        units.append(
            {
                "index": i + 1,
                "level": level,
                "title": title,
                "start_page": start,
                "end_page": end,
            }
        )
    return units


def filename_for(unit: dict) -> str:
    idx = unit["index"]
    title = unit["title"]
    # Prefer chapter numbers when present
    m = re.search(r"CHAPTER\s+(\d+)", title, re.I)
    if m:
        num = int(m.group(1))
        rest = re.sub(r"CHAPTER\s+\d+\s*", "", title, flags=re.I).strip(" :.-")
        return f"{idx:02d}-ch{num:02d}-{slugify(rest)}.md"
    m = re.search(r"PART\s+([IVX]+)", title, re.I)
    if m:
        rest = re.sub(r"PART\s+[IVX]+\s*", "", title, flags=re.I).strip(" :.-")
        return f"{idx:02d}-part-{m.group(1).lower()}-{slugify(rest) or 'intro'}.md"
    return f"{idx:02d}-{slugify(title)}.md"


def main() -> int:
    if not PDF_PATH.exists():
        print(f"PDF not found: {PDF_PATH}", file=sys.stderr)
        return 1

    EN_DIR.mkdir(parents=True, exist_ok=True)
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
    (ROOT / "notes").mkdir(parents=True, exist_ok=True)

    doc = fitz.open(PDF_PATH)
    page_count = doc.page_count
    toc = doc.get_toc(simple=True)

    # Extract all pages
    page_texts: list[str] = []
    empty_pages: list[int] = []
    for i in range(page_count):
        t = doc[i].get_text() or ""
        page_texts.append(t)
        if not t.strip():
            empty_pages.append(i + 1)

    # Full book markdown
    full_parts = [
        "# Trading Price Action TRENDS\n",
        "\n**Author:** Al Brooks  \n",
        "**Source:** Trading Price Action TRENDS.pdf  \n",
        f"**PDF pages:** {page_count}  \n",
        f"**Extractor:** PyMuPDF {fitz.version[0]}  \n",
        "\n---\n",
    ]
    for i, t in enumerate(page_texts):
        full_parts.append(page_to_markdown(i + 1, t))
    FULL_MD.write_text("".join(full_parts), encoding="utf-8")

    units = build_units(toc, page_count)
    inv_lines = [
        "# Chapter inventory (English source)\n",
        f"\nSource PDF pages: {page_count}\n",
        f"Split units: {len(units)}\n",
        "\n| # | File | Title | PDF pages | Chars |\n",
        "|---|------|-------|-----------|-------|\n",
    ]

    for unit in units:
        fname = filename_for(unit)
        unit["file"] = fname
        chunks = [heading_for(unit["level"], unit["title"]), "\n"]
        chunks.append(
            f"<!-- Source PDF pages {unit['start_page']}–{unit['end_page']} -->\n\n"
        )
        char_count = 0
        for p in range(unit["start_page"], unit["end_page"] + 1):
            md = page_to_markdown(p, page_texts[p - 1])
            chunks.append(md)
            char_count += len(page_texts[p - 1])
        out = CHAPTERS_DIR / fname
        out.write_text("".join(chunks), encoding="utf-8")
        inv_lines.append(
            f"| {unit['index']} | `{fname}` | {unit['title']} | "
            f"{unit['start_page']}–{unit['end_page']} | {char_count} |\n"
        )

    INVENTORY.write_text("".join(inv_lines), encoding="utf-8")

    notes = f"""# Conversion notes

## Tools
- **PyMuPDF (fitz)** version: {fitz.version}
- **Python**: {sys.version.split()[0]}
- **Source PDF**: `{PDF_PATH}`
- **Pages**: {page_count}
- **Total extractable characters**: {sum(len(t) for t in page_texts)}
- **Empty / figure-only pages** ({len(empty_pages)}): {empty_pages[:40]}{"..." if len(empty_pages) > 40 else ""}

## Method
1. Open PDF with PyMuPDF `get_text()` per page.
2. Normalize hyphenation and whitespace; emit page markers as HTML comments.
3. Split into units using PDF embedded outline (`get_toc`), not arbitrary page chunks.
4. `pandoc` is available as an optional helper binary under `scripts/pandoc` (amd64);
   primary PDF extraction uses PyMuPDF because pandoc alone is weak on PDF.

## Limits
- ~{len(empty_pages)} pages have no extractable text (charts/figures without OCR layer).
- Figure captions and surrounding prose are kept where present in the text layer.
- Running headers / page numbers may remain as residual noise in places.
- Hyphenation fix is heuristic; rare mid-word splits may remain.

## Outputs
- Full book: `en/full_book.md`
- Per-unit chapters: `en/chapters/*.md`
- Inventory: `notes/chapter_inventory.md`
"""
    CONVERSION_NOTES.write_text(notes, encoding="utf-8")

    print(f"Wrote {FULL_MD} ({FULL_MD.stat().st_size} bytes)")
    print(f"Wrote {len(units)} chapter units to {CHAPTERS_DIR}")
    print(f"Empty pages: {len(empty_pages)}")
    for u in units:
        print(f"  {u['index']:02d} p{u['start_page']}-{u['end_page']}: {u['title']} -> {u['file']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
