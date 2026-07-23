#!/usr/bin/env python3
from pathlib import Path

ROOT = Path("/root/book/price-action-books-zh/books/trading-price-action-reversals")
CHUNKS = ROOT / "zh" / "chunks"
CHAPTERS = ROOT / "zh" / "chapters"
NOTES = ROOT / "notes"
CHAPTERS.mkdir(parents=True, exist_ok=True)

JOBS = [
    ("07-part-i-trend-reversals-a-trend-becoming-an-opposite-trend", list(range(1, 10))),
    ("10-ch03-major-trend-reversal", list(range(1, 7))),
    ("11-ch04-climactic-reversals-a-spike-followed-by-a-spike-in-the-opposite-direction", list(range(1, 8))),
    ("12-ch05-wedges-and-other-three-push-reversal-patterns", list(range(1, 6))),
    ("14-ch07-final-flags", list(range(1, 6))),
]

report = ["# Merge size report — REVERSALS Part I assigned chapters", ""]
results = []

for stem, part_nums in JOBS:
    parts_info = []
    bodies = []
    for n in part_nums:
        name = f"{stem}.part{n:02d}.md"
        path = CHUNKS / name
        text = path.read_text(encoding="utf-8")
        if not text.endswith("\n"):
            text += "\n"
        bodies.append(text)
        parts_info.append((name, path.stat().st_size))
    merged = "\n".join(b.rstrip("\n") for b in bodies) + "\n"
    dest = CHAPTERS / f"{stem}.md"
    dest.write_text(merged, encoding="utf-8")
    en_path = ROOT / "en" / "chapters" / f"{stem}.md"
    en_bytes = en_path.stat().st_size if en_path.exists() else 0
    zh_bytes = dest.stat().st_size
    cjk = sum(1 for c in merged if "\u4e00" <= c <= "\u9fff")
    ratio = (zh_bytes / en_bytes * 100) if en_bytes else 0.0
    line = f"{stem}: zh={zh_bytes} bytes, chars={len(merged)}, lines={merged.count(chr(10))+1}, cjk={cjk}, en={en_bytes} bytes, zh/en={ratio:.1f}%"
    results.append(line)
    report.append(f"## `{stem}.md`")
    report.append("")
    report.append(f"- EN bytes: {en_bytes:,}")
    report.append(f"- ZH bytes: {zh_bytes:,}")
    report.append(f"- ZH chars: {len(merged):,}")
    report.append(f"- ZH lines: {merged.count(chr(10))+1:,}")
    report.append(f"- CJK chars: {cjk:,}")
    report.append(f"- ZH/EN byte ratio: {ratio:.1f}%")
    report.append(f"- Chunks ({len(parts_info)}):")
    for name, size in parts_info:
        report.append(f"  - `{name}`: {size:,} bytes")
    report.append("")

out = NOTES / "merge_size_report_part_i_assigned.md"
out.write_text("\n".join(report) + "\n", encoding="utf-8")
summary = NOTES / "merge_size_report_part_i_assigned.txt"
summary.write_text("\n".join(results) + "\n" + f"Report: {out}\n", encoding="utf-8")
