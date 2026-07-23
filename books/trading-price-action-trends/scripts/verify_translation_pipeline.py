#!/usr/bin/env python3
"""Structural verification of the EN→ZH translation deliverable.

Drives the real project layout under trading-price-action-trends-zh/:
asserts EN chapters, ZH chapters, glossary, audit record, and quality gates.
Exit 0 only if all gating checks pass.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EN = ROOT / "en" / "chapters"
ZH = ROOT / "zh" / "chapters"
GLOSSARY = ROOT / "glossary" / "glossary.md"
AUDIT = ROOT / "notes" / "audit_record.md"
FULL = ROOT / "en" / "full_book.md"

CORE_TERMS = [
    "震荡区间",
    "突破",
    "回撤",
    "信号K线",
    "始终持仓",
    "趋势K线",
    "价格行为",
    "尖峰",
]


def cn_ratio(text: str) -> float:
    cn = len(re.findall(r"[\u4e00-\u9fff]", text))
    lat = len(re.findall(r"[A-Za-z]", text))
    return cn / (cn + lat + 1)


def main() -> int:
    errors: list[str] = []

    if not FULL.exists() or FULL.stat().st_size < 100_000:
        errors.append(f"full_book.md missing or too small: {FULL}")

    en_files = sorted(EN.glob("*.md"))
    zh_files = sorted(ZH.glob("*.md"))
    if len(en_files) < 30:
        errors.append(f"expected ≥30 EN chapters, got {len(en_files)}")
    if len(zh_files) != len(en_files):
        errors.append(f"EN/ZH count mismatch: {len(en_files)} vs {len(zh_files)}")

    en_names = {p.name for p in en_files}
    zh_names = {p.name for p in zh_files}
    missing = sorted(en_names - zh_names)
    if missing:
        errors.append(f"ZH missing for: {missing[:10]}")

    for name in sorted(en_names & zh_names):
        en_p = EN / name
        zh_p = ZH / name
        en_size = en_p.stat().st_size
        zh_size = zh_p.stat().st_size
        if en_size < 200:
            continue
        if zh_size < max(200, int(en_size * 0.25)):
            errors.append(f"ZH too thin vs EN: {name} en={en_size} zh={zh_size}")
        zt = zh_p.read_text(encoding="utf-8", errors="replace")
        # Skip pure-front-matter tiny files for ratio
        if en_size > 2000 and cn_ratio(zt) < 0.35 and name not in {
            "37-index.md",
            "03-list-of-terms-used-in-this-book.md",
        }:
            errors.append(f"low Chinese ratio: {name} ratio={cn_ratio(zt):.2f}")

    if not GLOSSARY.exists():
        errors.append("glossary missing")
    else:
        g = GLOSSARY.read_text(encoding="utf-8")
        for term in ["trend", "breakout", "pullback", "always", "signal bar", "trading range"]:
            if term.lower() not in g.lower():
                errors.append(f"glossary missing seed term: {term}")

    # preferred ZH terms appear in multiple chapters
    zh_texts = {p.name: p.read_text(encoding="utf-8") for p in zh_files}
    for term in CORE_TERMS:
        files = [n for n, t in zh_texts.items() if term in t]
        if len(files) < 3 and term not in {"始终持仓"}:
            # always-in may be rarer in early chapters only — still require ≥2
            if len(files) < 2:
                errors.append(f"glossary term rare in ZH chapters: {term} in {len(files)} files")
        elif term == "始终持仓" and len(files) < 2:
            errors.append(f"始终持仓 only in {len(files)} files")

    if not AUDIT.exists() or AUDIT.stat().st_size < 500:
        errors.append("audit_record.md missing or too small")
    else:
        audit = AUDIT.read_text(encoding="utf-8")
        for key in ["术语", "完整性", "润色"]:
            if key not in audit:
                errors.append(f"audit record missing section keyword: {key}")


    # skeptic regression: Title Case multi-line EN chapter titles must not remain in body
    title_frags = {
        "09-ch04-bar-basics-signal-bars-entry-bars-setups-and-candle-patterns.md": [
            "Bar Basics:",
            "Signal Bars,",
            "Candle Patterns",
        ],
        "33-ch25-trend-resumption-day.md": ["Resumption Day"],
        "34-ch26-stairs-broad-channel-trend.md": [
            "Stairs: Broad",
            "Channel Trend",
        ],
    }
    for name, frags in title_frags.items():
        pth = ZH / name
        if not pth.exists():
            errors.append(f"missing chapter for title-frag check: {name}")
            continue
        body = []
        for ln in pth.read_text(encoding="utf-8").splitlines():
            s = ln.strip()
            if not s or s.startswith("<!--") or s.startswith("#"):
                continue
            body.append(s)
        for frag in frags:
            if frag in body:
                errors.append(f"residual EN title fragment in body of {name}: {frag!r}")

    # sample early/mid/late substantial prose
    samples = [
        "06-ch01-the-spectrum-of-price-action-extreme-trends-to-extreme-trading-ranges.md",
        "21-ch15-channels.md",
        "29-ch21-spike-and-channel-trend.md",
    ]
    for s in samples:
        p = ZH / s
        if not p.exists():
            errors.append(f"sample chapter missing: {s}")
            continue
        t = p.read_text(encoding="utf-8")
        if len(re.findall(r"[\u4e00-\u9fff]", t)) < 200:
            errors.append(f"sample chapter lacks substantial Chinese: {s}")

    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("PASS")
    print(f"EN chapters: {len(en_files)}")
    print(f"ZH chapters: {len(zh_files)}")
    print(f"full_book bytes: {FULL.stat().st_size}")
    print(f"glossary bytes: {GLOSSARY.stat().st_size}")
    print(f"audit bytes: {AUDIT.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
