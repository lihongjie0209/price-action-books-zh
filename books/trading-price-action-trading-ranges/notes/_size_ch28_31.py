#!/usr/bin/env python3
"""Size report for ch28–ch31 EN vs ZH."""
from pathlib import Path

base = Path(__file__).resolve().parent.parent
pairs = [
    "39-ch28-entering-on-limits.md",
    "40-ch29-protective-and-trailing-stops.md",
    "41-ch30-profit-taking-and-profit-targets.md",
    "42-ch31-scaling-into-and-out-of-a-trade.md",
]
print(f"{'file':<52} {'en_chars':>10} {'zh_chars':>10} {'en_bytes':>10} {'zh_bytes':>10} {'zh/en_c':>8} {'zh/en_b':>8}")
print("-" * 112)
te_c = te_b = tz_c = tz_b = 0
for f in pairs:
    en = (base / "en" / "chapters" / f).read_bytes()
    zh = (base / "zh" / "chapters" / f).read_bytes()
    en_t = en.decode("utf-8")
    zh_t = zh.decode("utf-8")
    ec, zc = len(en_t), len(zh_t)
    eb, zb = len(en), len(zh)
    te_c += ec; tz_c += zc; te_b += eb; tz_b += zb
    print(f"{f:<52} {ec:10d} {zc:10d} {eb:10d} {zb:10d} {zc/ec:8.2f} {zb/eb:8.2f}")
print("-" * 112)
print(f"{'TOTAL':<52} {te_c:10d} {tz_c:10d} {te_b:10d} {tz_b:10d} {tz_c/te_c:8.2f} {tz_b/te_b:8.2f}")
