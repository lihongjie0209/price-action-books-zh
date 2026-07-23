#!/usr/bin/env python3
"""Extract Trading Price Action REVERSALS PDF → EN chapter Markdown."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import fitz

PDF_PATH = Path("/root/book/Trading Price Action REVERSALS.pdf")
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
    return re.sub(r"-+", "-", s)[:80] or "section"


def normalize_text(text: str) -> str:
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = []
    for line in text.split("\n"):
        if re.fullmatch(r"\d{1,3}", line.strip()):
            continue
        lines.append(line.rstrip())
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def page_to_markdown(page_num: int, text: str) -> str:
    if not text.strip():
        return f"\n\n<!-- PDF page {page_num}: no extractable text (likely figure-only) -->\n\n"
    return f"\n\n<!-- PDF page {page_num} -->\n\n{normalize_text(text)}\n"


def clean_title(title: str) -> str:
    return re.sub(r"\s+", " ", title).strip()


def build_units(toc, page_count):
    skip = {"cover", "series", "title page", "copyright", "dedication"}
    entries = []
    for level, title, page in toc:
        title = clean_title(title)
        if title.lower() in skip:
            continue
        entries.append((level, title, page))
    # All L1/L2 as split boundaries for this book (mostly L1)
    split_entries = [(lv, t, p) for lv, t, p in entries if lv <= 2]
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
    idx, title = unit["index"], unit["title"]
    m = re.search(r"Chapter\s+(\d+)", title, re.I)
    if m:
        rest = re.sub(r"Chapter\s+\d+\s*:?\s*", "", title, flags=re.I).strip(" :.-")
        return f"{idx:02d}-ch{int(m.group(1)):02d}-{slugify(rest)}.md"
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
    page_texts, empty = [], []
    for i in range(page_count):
        t = doc[i].get_text() or ""
        page_texts.append(t)
        if not t.strip():
            empty.append(i + 1)

    full = [
        "# Trading Price Action REVERSALS\n",
        "\n**Author:** Al Brooks  \n",
        f"**Source:** {PDF_PATH.name}  \n",
        f"**PDF pages:** {page_count}  \n",
        f"**Extractor:** PyMuPDF {fitz.version[0]}  \n\n---\n",
    ]
    for i, t in enumerate(page_texts):
        full.append(page_to_markdown(i + 1, t))
    FULL_MD.write_text("".join(full), encoding="utf-8")

    units = build_units(toc, page_count)
    inv = [
        "# Chapter inventory — REVERSALS\n",
        f"\nPages: {page_count} | Units: {len(units)}\n\n",
        "| # | File | Title | Pages | Chars |\n|---|------|-------|-------|-------|\n",
    ]
    for unit in units:
        fname = filename_for(unit)
        unit["file"] = fname
        parts = [f"{'#' * min(unit['level'], 3)} {unit['title']}\n\n"]
        parts.append(f"<!-- Source PDF pages {unit['start_page']}–{unit['end_page']} -->\n\n")
        chars = 0
        for p in range(unit["start_page"], unit["end_page"] + 1):
            parts.append(page_to_markdown(p, page_texts[p - 1]))
            chars += len(page_texts[p - 1])
        (CHAPTERS_DIR / fname).write_text("".join(parts), encoding="utf-8")
        inv.append(
            f"| {unit['index']} | `{fname}` | {unit['title']} | "
            f"{unit['start_page']}–{unit['end_page']} | {chars} |\n"
        )
        print(f"{unit['index']:02d} p{unit['start_page']}-{unit['end_page']}: {unit['title']} -> {fname}")
    INVENTORY.write_text("".join(inv), encoding="utf-8")
    CONVERSION_NOTES.write_text(
        f"""# Conversion notes — REVERSALS

- **PyMuPDF**: {fitz.version}
- **Source**: `{PDF_PATH}` (wslpath from Downloads)
- **Pages**: {page_count}
- **Chars**: {sum(len(t) for t in page_texts)}
- **Empty pages** ({len(empty)}): {empty[:60]}{"..." if len(empty) > 60 else ""}
- Split by PDF outline L1/L2.
""",
        encoding="utf-8",
    )
    print(f"full_book {FULL_MD.stat().st_size} units {len(units)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
