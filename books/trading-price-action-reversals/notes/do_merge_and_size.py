#!/usr/bin/env python3
"""Merge assigned zh chunks and report sizes."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "zh" / "chunks"
CHAPTERS = ROOT / "zh" / "chapters"
EN = ROOT / "en" / "chapters"
CHAPTERS.mkdir(parents=True, exist_ok=True)

JOBS = [
    ("25-part-iii-the-first-hour-the-opening-range", 5),
    ("33-ch23-options", 5),
    ("34-ch24-the-best-trades-putting-it-all-together", 13),
]


def merge(base: str, n: int) -> Path:
    parts = []
    for i in range(1, n + 1):
        p = CHUNKS / f"{base}.part{i:02d}.md"
        if not p.exists():
            raise SystemExit(f"Missing: {p}")
        text = p.read_text(encoding="utf-8")
        if not text.endswith("\n"):
            text += "\n"
        parts.append(text)
    body = "\n".join(parts)
    if not body.endswith("\n"):
        body += "\n"
    dest = CHAPTERS / f"{base}.md"
    dest.write_text(body, encoding="utf-8")
    return dest


def main():
    report_lines = ["# Merge size report — REVERSALS (ch25, ch33, ch34)\n"]
    print("==== MERGE + SIZE REPORT ====")
    for base, n in JOBS:
        dest = merge(base, n)
        zh_sz = dest.stat().st_size
        en_path = EN / f"{base}.md"
        en_sz = en_path.stat().st_size if en_path.exists() else 0
        ratio = zh_sz / en_sz if en_sz else 0
        chunk_total = sum((CHUNKS / f"{base}.part{i:02d}.md").stat().st_size for i in range(1, n + 1))
        print(f"\n--- {base} ---")
        print(f"  parts: {n}")
        print(f"  ZH chunks total: {chunk_total:,} bytes")
        print(f"  ZH chapter:      {zh_sz:,} bytes")
        print(f"  EN chapter:      {en_sz:,} bytes")
        print(f"  ZH/EN ratio:     {ratio:.2%}")
        for i in range(1, n + 1):
            p = CHUNKS / f"{base}.part{i:02d}.md"
            print(f"    part{i:02d}: {p.stat().st_size:,} bytes")
        report_lines.append(f"## {base}")
        report_lines.append(f"- parts: {n}")
        report_lines.append(f"- ZH chapter: {zh_sz:,} bytes")
        report_lines.append(f"- EN chapter: {en_sz:,} bytes")
        report_lines.append(f"- ZH/EN ratio: {ratio:.2%}")
        report_lines.append("")
    out = ROOT / "notes" / "merge_size_report_25_33_34.md"
    out.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
