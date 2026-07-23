#!/usr/bin/env python3
"""Structural verification for Trading Ranges book deliverable."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]
REPO = BOOK.parents[1]
CORE = ["震荡区间", "突破", "回撤", "信号K线", "始终持仓", "等幅运动", "缺口"]


def main() -> int:
    errors: list[str] = []
    en = sorted((BOOK / "en" / "chapters").glob("*.md"))
    zh = sorted((BOOK / "zh" / "chapters").glob("*.md"))
    if len(en) < 30:
        errors.append(f"too few EN chapters: {len(en)}")
    if len(zh) != len(en):
        errors.append(f"EN/ZH count {len(en)} vs {len(zh)}")
    en_names = {p.name for p in en}
    zh_names = {p.name for p in zh}
    missing = sorted(en_names - zh_names)
    if missing:
        errors.append(f"ZH missing: {missing[:8]}")

    for name in sorted(en_names & zh_names):
        en_p = BOOK / "en" / "chapters" / name
        zh_p = BOOK / "zh" / "chapters" / name
        es, zs = en_p.stat().st_size, zh_p.stat().st_size
        if es > 2000 and zs < max(200, int(es * 0.25)):
            errors.append(f"thin ZH: {name} en={es} zh={zs}")
        zt = zh_p.read_text(encoding="utf-8", errors="replace")
        cn = len(re.findall(r"[\u4e00-\u9fff]", zt))
        lat = len(re.findall(r"[A-Za-z]", zt))
        if es > 3000 and cn / (cn + lat + 1) < 0.35 and name not in {
            "46-index.md",
            "02-list-of-terms-used-in-this-book.md",
        }:
            errors.append(f"low Chinese ratio: {name}")

    gloss = BOOK / "glossary" / "glossary.md"
    if not gloss.exists():
        errors.append("glossary missing")
    else:
        g = gloss.read_text(encoding="utf-8")
        for t in ["trading range", "breakout", "pullback", "signal bar"]:
            if t.lower() not in g.lower():
                errors.append(f"glossary missing {t}")

    zh_texts = {
        p.name: p.read_text(encoding="utf-8")
        for p in (BOOK / "zh" / "chapters").glob("*.md")
    }
    for term in CORE:
        files = [n for n, t in zh_texts.items() if term in t]
        if len(files) < 2:
            errors.append(f"term rare: {term} in {len(files)} files")

    audit = BOOK / "notes" / "audit_record.md"
    if not audit.exists() or audit.stat().st_size < 300:
        errors.append("audit_record missing/small")

    cat = json.loads((REPO / "catalog.json").read_text(encoding="utf-8"))
    ids = [b["id"] for b in cat.get("books", [])]
    if "trading-price-action-trading-ranges" not in ids:
        errors.append("catalog missing trading-price-action-trading-ranges")
    else:
        b = next(x for x in cat["books"] if x["id"] == "trading-price-action-trading-ranges")
        if not b.get("toc"):
            errors.append("catalog missing hierarchical toc")

    samples = [
        "03-introduction.md",
        "30-part-iv-trading-ranges.md",
        "36-ch25-mathematics-of-trading-should-i-take-this-trade-will-i-make-money-if-i-take-this.md",
    ]
    for s in samples:
        p = BOOK / "zh" / "chapters" / s
        if not p.exists():
            errors.append(f"sample missing {s}")
            continue
        if len(re.findall(r"[\u4e00-\u9fff]", p.read_text(encoding="utf-8"))) < 200:
            errors.append(f"sample lacks Chinese: {s}")

    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("PASS")
    print(f"EN={len(en)} ZH={len(zh)}")
    print(f"glossary={gloss.stat().st_size} audit={audit.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
