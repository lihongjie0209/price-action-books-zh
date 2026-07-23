#!/usr/bin/env python3
from pathlib import Path

ROOT = Path("/root/book/price-action-books-zh/books/trading-price-action-reversals")
CHUNKS = ROOT / "zh" / "chunks"
CHAPTERS = ROOT / "zh" / "chapters"
EN_CH = ROOT / "en" / "chapters"
EN_CK = ROOT / "en" / "chunks"
CHAPTERS.mkdir(parents=True, exist_ok=True)

JOBS = [
    ("16-ch09-failures", 4),
    ("23-ch15-always-in", 5),
    ("24-ch16-extreme-scalping", 4),
    ("28-ch19-opening-patterns-and-reversals", 3),
    ("35-ch25-trading-guidelines", 3),
]

DIRECT = [
    "02-list-of-terms-used-in-this-book.md",
    "27-ch18-patterns-related-to-yesterday-breakouts-breakout-pullbacks-and-failed-breakouts.md",
    "31-ch21-detailed-day-trading-examples.md",
    "32-ch22-daily-weekly-and-monthly-charts.md",
]

report = []

for chapter, nparts in JOBS:
    parts = [f"{chapter}.part{i:02d}" for i in range(1, nparts + 1)]
    out = []
    for i, stem in enumerate(parts):
        path = CHUNKS / f"{stem}.md"
        text = path.read_text(encoding="utf-8")
        if i > 0:
            lines = text.splitlines(keepends=True)
            if lines and "chunk continuation" in lines[0]:
                lines = lines[1:]
                if lines and lines[0].strip() == "":
                    lines = lines[1:]
            text = "".join(lines)
            if out and not out[-1].endswith("\n"):
                out.append("\n")
            out.append("\n")
        out.append(text if text.endswith("\n") else text + "\n")
    body = "".join(out)
    dest = CHAPTERS / f"{chapter}.md"
    dest.write_text(body, encoding="utf-8")
    report.append(f"MERGED {dest.name}: {dest.stat().st_size} bytes")

report.append("")
report.append(f"{'file':<75} {'EN':>8} {'ZH':>8} {'ratio':>7}")
for name in DIRECT + [f"{c}.md" for c, _ in JOBS]:
    en = EN_CH / name
    zh = CHAPTERS / name
    eb = en.stat().st_size if en.exists() else 0
    zb = zh.stat().st_size if zh.exists() else 0
    ratio = f"{zb/eb:.2f}" if eb else "n/a"
    report.append(f"{name:<75} {eb:8d} {zb:8d} {ratio:>7}")

for chapter, nparts in JOBS:
    for i in range(1, nparts + 1):
        stem = f"{chapter}.part{i:02d}"
        ep = EN_CK / f"{stem}.md"
        zp = CHUNKS / f"{stem}.md"
        epb = ep.stat().st_size if ep.exists() else 0
        zpb = zp.stat().st_size if zp.exists() else 0
        r = f"{zpb/epb:.2f}" if epb else "n/a"
        report.append(f"  {stem:<73} {epb:8d} {zpb:8d} {r:>7}")

out_path = ROOT / "notes" / "merge_size_report.txt"
out_path.write_text("\n".join(report) + "\n", encoding="utf-8")
print("\n".join(report))
