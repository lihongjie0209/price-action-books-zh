#!/usr/bin/env python3
"""Extract Trading Price Action TRADING RANGES PDF → EN chapter Markdown."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import fitz

PDF_PATH = Path("/root/book/Trading Price Action TRADING RANGES.pdf")
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
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        if re.fullmatch(r"\d{1,3}", stripped):
            continue
        lines.append(line.rstrip())
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def page_to_markdown(page_num_1based: int, text: str) -> str:
    if not text.strip():
        return f"\n\n<!-- PDF page {page_num_1based}: no extractable text (likely figure-only) -->\n\n"
    body = normalize_text(text)
    return f"\n\n<!-- PDF page {page_num_1based} -->\n\n{body}\n"


def clean_title(title: str) -> str:
    return re.sub(r"\s+", " ", title).strip()


def heading_for(level: int, title: str) -> str:
    depth = min(max(level, 1), 3)
    return f"{'#' * depth} {title}\n"


def build_units(toc: list[tuple[int, str, int]], page_count: int):
    entries = []
    skip = {"cover", "series", "title page", "copyright", "dedication"}
    for level, title, page in toc:
        title = clean_title(title)
        if title.lower() in skip:
            continue
        # collapse L3 under chapter into same chapter unit later by only using L1/L2 splits
        entries.append((level, title, page))

    # Prefer splitting on L1 and L2 only (drop pure L3 as separate units — attach to parent)
    split_entries = [(lv, t, p) for lv, t, p in entries if lv <= 2]
    if not split_entries:
        split_entries = entries

    units = []
    for i, (level, title, start) in enumerate(split_entries):
        end = split_entries[i + 1][2] - 1 if i + 1 < len(split_entries) else page_count
        start = max(1, min(start, page_count))
        end = max(start, min(end, page_count))
        units.append(
            {"index": i + 1, "level": level, "title": title, "start_page": start, "end_page": end}
        )
    return units


def filename_for(unit: dict) -> str:
    idx = unit["index"]
    title = unit["title"]
    m = re.search(r"Chapter\s+(\d+)", title, re.I)
    if m:
        num = int(m.group(1))
        rest = re.sub(r"Chapter\s+\d+\s*:?\s*", "", title, flags=re.I).strip(" :.-")
        return f"{idx:02d}-ch{num:02d}-{slugify(rest)}.md"
    m = re.search(r"Part\s+([IVX]+)", title, re.I)
    if m:
        rest = re.sub(r"Part\s+[IVX]+\s*:?\s*", "", title, flags=re.I).strip(" :.-")
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

    page_texts: list[str] = []
    empty_pages: list[int] = []
    for i in range(page_count):
        t = doc[i].get_text() or ""
        page_texts.append(t)
        if not t.strip():
            empty_pages.append(i + 1)

    full_parts = [
        "# Trading Price Action TRADING RANGES\n",
        "\n**Author:** Al Brooks  \n",
        f"**Source:** {PDF_PATH.name}  \n",
        f"**PDF pages:** {page_count}  \n",
        f"**Extractor:** PyMuPDF {fitz.version[0]}  \n",
        "\n---\n",
    ]
    for i, t in enumerate(page_texts):
        full_parts.append(page_to_markdown(i + 1, t))
    FULL_MD.write_text("".join(full_parts), encoding="utf-8")

    units = build_units(toc, page_count)
    inv = [
        "# Chapter inventory (English source) — TRADING RANGES\n",
        f"\nSource PDF pages: {page_count}\n",
        f"Split units: {len(units)}\n\n",
        "| # | File | Title | PDF pages | Chars |\n",
        "|---|------|-------|-----------|-------|\n",
    ]
    for unit in units:
        fname = filename_for(unit)
        unit["file"] = fname
        chunks = [heading_for(unit["level"], unit["title"]), "\n"]
        chunks.append(f"<!-- Source PDF pages {unit['start_page']}–{unit['end_page']} -->\n\n")
        char_count = 0
        for p in range(unit["start_page"], unit["end_page"] + 1):
            chunks.append(page_to_markdown(p, page_texts[p - 1]))
            char_count += len(page_texts[p - 1])
        (CHAPTERS_DIR / fname).write_text("".join(chunks), encoding="utf-8")
        inv.append(
            f"| {unit['index']} | `{fname}` | {unit['title']} | "
            f"{unit['start_page']}–{unit['end_page']} | {char_count} |\n"
        )
    INVENTORY.write_text("".join(inv), encoding="utf-8")

    notes = f"""# Conversion notes — TRADING RANGES

## Tools
- **PyMuPDF (fitz)** version: {fitz.version}
- **Python**: {sys.version.split()[0]}
- **Source PDF**: `{PDF_PATH}` (copied via wslpath from Windows Downloads)
- **Pages**: {page_count}
- **Total extractable characters**: {sum(len(t) for t in page_texts)}
- **Empty / figure-only pages** ({len(empty_pages)}): {empty_pages[:50]}{"..." if len(empty_pages) > 50 else ""}

## Method
1. `get_text()` per page; normalize hyphenation/whitespace.
2. Split using PDF outline L1/L2 (`get_toc`); L3 subsections stay inside parent chapter.
3. Outputs: `en/full_book.md`, `en/chapters/*.md`, this file, inventory.

## Limits
- ~{len(empty_pages)} pages may be figure-only / weak text layer.
- Running headers / page numbers residual noise possible.
"""
    CONVERSION_NOTES.write_text(notes, encoding="utf-8")
    print(f"Wrote {FULL_MD} ({FULL_MD.stat().st_size} bytes)")
    print(f"Wrote {len(units)} units to {CHAPTERS_DIR}")
    for u in units:
        print(f"  {u['index']:02d} p{u['start_page']}-{u['end_page']}: {u['title']} -> {u['file']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
