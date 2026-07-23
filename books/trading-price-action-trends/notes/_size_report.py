#!/usr/bin/env python3
from pathlib import Path
ROOT = Path("/root/book/trading-price-action-trends-zh")
files = [
    ROOT / "zh/chapters/04-introduction.md",
    ROOT / "zh/chapters/05-part-i-price-action.md",
    ROOT / "en/chapters/04-introduction.md",
    ROOT / "en/chapters/05-part-i-price-action.md",
]
lines = []
for f in files:
    data = f.read_bytes()
    text = data.decode("utf-8")
    lines.append(
        f"{f.relative_to(ROOT)}: bytes={len(data)} chars={len(text)} lines={text.count(chr(10))+1} cjk={sum(1 for c in text if '\u4e00'<=c<='\u9fff')}"
    )
out = ROOT / "notes/_size_report.txt"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
