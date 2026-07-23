#!/usr/bin/env python3
"""Size report for Part IV + Ch22 EN vs ZH (chunks + chapters)."""
from pathlib import Path

base = Path(__file__).resolve().parent.parent
out_lines = []

def report(label, path):
    data = path.read_bytes()
    text = data.decode("utf-8")
    return len(text), len(data), text.count("\n") + 1

jobs = [
    ("30-part-iv-trading-ranges", 8),
    ("32-ch22-tight-trading-ranges", 5),
]

print(f"{'path':<72} {'chars':>8} {'bytes':>8} {'lines':>6}")
print("-" * 100)
out_lines.append(f"{'path':<72} {'chars':>8} {'bytes':>8} {'lines':>6}")
out_lines.append("-" * 100)

for stem, nparts in jobs:
    total_c = total_b = 0
    for i in range(1, nparts + 1):
        p = base / "zh" / "chunks" / f"{stem}.part{i:02d}.md"
        c, b, ln = report(p.name, p)
        total_c += c
        total_b += b
        line = f"{'zh/chunks/'+p.name:<72} {c:8d} {b:8d} {ln:6d}"
        print(line)
        out_lines.append(line)
    line = f"{'  SUM zh chunks '+stem:<72} {total_c:8d} {total_b:8d}"
    print(line)
    out_lines.append(line)

    zh = base / "zh" / "chapters" / f"{stem}.md"
    en = base / "en" / "chapters" / f"{stem}.md"
    zc, zb, zln = report(zh.name, zh)
    ec, eb, eln = report(en.name, en)
    for label, c, b, ln in [
        (f"zh/chapters/{stem}.md", zc, zb, zln),
        (f"en/chapters/{stem}.md", ec, eb, eln),
    ]:
        line = f"{label:<72} {c:8d} {b:8d} {ln:6d}"
        print(line)
        out_lines.append(line)
    line = f"  ZH/EN ratio chars={zc/ec:.2%} bytes={zb/eb:.2%}"
    print(line)
    out_lines.append(line)
    print()
    out_lines.append("")

report_path = base / "notes" / "_size_partiv_ch22.txt"
report_path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
print(f"Wrote {report_path}")
