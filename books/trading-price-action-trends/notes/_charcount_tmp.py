#!/usr/bin/env python3
"""Character counts for zh chapter translations."""
from pathlib import Path

files = [
    "03-list-of-terms-used-in-this-book.md",
    "07-ch02-trend-bars-doji-bars-and-climaxes.md",
    "09-ch04-bar-basics-signal-bars-entry-bars-setups-and-candle-patterns.md",
    "10-ch05-signal-bars-reversal-bars.md",
    "12-ch07-outside-bars.md",
    "19-ch13-trend-lines.md",
    "20-ch14-trend-channel-lines.md",
    "37-index.md",
]

zh = Path(__file__).resolve().parent.parent / "zh" / "chapters"
en = Path(__file__).resolve().parent.parent / "en" / "chapters"

print(f"{'file':<70} {'zh':>8} {'en':>8} {'zh/en':>7}")
print("-" * 100)
total_zh = total_en = 0
for f in files:
    zpath = zh / f
    epath = en / f
    zc = len(zpath.read_text(encoding="utf-8")) if zpath.exists() else 0
    ec = len(epath.read_text(encoding="utf-8")) if epath.exists() else 0
    ratio = (zc / ec) if ec else 0
    print(f"{f:<70} {zc:8d} {ec:8d} {ratio:7.2f}")
    total_zh += zc
    total_en += ec
print("-" * 100)
print(f"{'TOTAL':<70} {total_zh:8d} {total_en:8d} {total_zh/total_en if total_en else 0:7.2f}")
