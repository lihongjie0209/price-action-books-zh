#!/usr/bin/env python3
"""Size report for assigned REVERSALS ZH translations."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "01-acknowledgments.md",
    "04-how-to-read-these-books.md",
    "05-signs-of-strength-trends-breakouts-reversal-bars-and-reversals.md",
    "06-bar-counting-basics-high-1-high-2-low-1-low-2.md",
    "08-ch01-example-of-how-to-trade-a-reversal.md",
    "09-ch02-signs-of-strength-in-a-reversal.md",
    "13-ch06-expanding-triangles.md",
    "15-ch08-double-top-and-bottom-pullbacks.md",
    "17-ch10-huge-volume-reversals-on-daily-charts.md",
    "18-part-ii-day-trading.md",
    "19-ch11-key-times-of-the-day.md",
    "20-ch12-markets.md",
    "21-ch13-time-frames-and-chart-types.md",
    "22-ch14-globex-premarket-postmarket-and-overnight-market.md",
    "26-ch17-patterns-related-to-the-premarket.md",
    "29-ch20-gap-openings-reversals-and-continuations.md",
    "30-part-iv-putting-it-all-together.md",
    "36-about-the-author.md",
    "37-about-the-website.md",
    "38-index.md",
]

def stats(p: Path):
    data = p.read_bytes()
    text = data.decode("utf-8")
    cjk = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
    return len(data), len(text), text.count("\n") + (0 if text.endswith("\n") else 1), cjk

rows = []
rows.append(f"{'file':<70} {'en_b':>7} {'zh_b':>7} {'ratio':>6} {'zh_cjk':>7} {'en_ln':>6} {'zh_ln':>6}")
for name in FILES:
    en = ROOT / "en" / "chapters" / name
    zh = ROOT / "zh" / "chapters" / name
    if not en.exists() or not zh.exists():
        rows.append(f"{name}: MISSING en={en.exists()} zh={zh.exists()}")
        continue
    eb, ec, el, _ = stats(en)
    zb, zc, zl, zcjk = stats(zh)
    ratio = zb / eb if eb else 0
    flag = "OK" if ratio >= 0.35 else "THIN"
    rows.append(f"{name:<70} {eb:7d} {zb:7d} {ratio:5.2f}x {zcjk:7d} {el:6d} {zl:6d} {flag}")

out = ROOT / "notes" / "_size_report_batch.txt"
out.write_text("\n".join(rows) + "\n", encoding="utf-8")
print("\n".join(rows))
print(f"\nWrote {out}")
