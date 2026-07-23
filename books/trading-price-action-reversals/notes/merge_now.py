#!/usr/bin/env python3
"""Merge zh chunks → zh chapters and print EN/ZH sizes for ch25, ch33, ch34."""
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


def main():
    report = ["# Size report REVERSALS 25/33/34\n"]
    print("==== MERGE + SIZE REPORT (REVERSALS) ====")
    for base, n in JOBS:
        bodies = []
        chunk_bytes = 0
        for i in range(1, n + 1):
            p = CHUNKS / f"{base}.part{i:02d}.md"
            if not p.exists():
                raise SystemExit(f"Missing chunk: {p}")
            raw = p.read_bytes()
            chunk_bytes += len(raw)
            text = raw.decode("utf-8")
            if not text.endswith("\n"):
                text += "\n"
            bodies.append(text)
            print(f"  {p.name}: {len(raw):,} bytes")
        merged = "\n".join(bodies)
        if not merged.endswith("\n"):
            merged += "\n"
        dest = CHAPTERS / f"{base}.md"
        dest.write_text(merged, encoding="utf-8")
        zh = dest.stat().st_size
        en_path = EN / f"{base}.md"
        en = en_path.stat().st_size if en_path.exists() else 0
        ratio = (zh / en) if en else 0
        cjk = sum(1 for c in merged if "\u4e00" <= c <= "\u9fff")
        pages = merged.count("<!-- PDF page")
        print(f"{base}")
        print(f"  ZH chapter: {zh:,} bytes | CJK chars: {cjk:,} | page markers: {pages}")
        print(f"  EN chapter: {en:,} bytes | ZH/EN: {ratio:.2%}")
        print(f"  chunk sum:  {chunk_bytes:,} bytes")
        print()
        report.append(f"## {base}")
        report.append(f"- ZH: {zh:,} bytes, CJK={cjk:,}, pages={pages}")
        report.append(f"- EN: {en:,} bytes, ratio={ratio:.2%}")
        report.append(f"- chunks: {n} parts, sum={chunk_bytes:,} bytes")
        report.append("")
    out = ROOT / "notes" / "merge_size_report_25_33_34.md"
    out.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
