#!/usr/bin/env python3
"""Merge assigned zh/chunks into zh/chapters; report EN vs ZH sizes."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "zh" / "chunks"
CHAPTERS = ROOT / "zh" / "chapters"
EN_CH = ROOT / "en" / "chapters"
EN_CK = ROOT / "en" / "chunks"
CHAPTERS.mkdir(parents=True, exist_ok=True)

JOBS = [
    ("16-ch09-failures", [f"16-ch09-failures.part{i:02d}" for i in range(1, 5)]),
    ("23-ch15-always-in", [f"23-ch15-always-in.part{i:02d}" for i in range(1, 6)]),
    ("24-ch16-extreme-scalping", [f"24-ch16-extreme-scalping.part{i:02d}" for i in range(1, 5)]),
    ("28-ch19-opening-patterns-and-reversals", [f"28-ch19-opening-patterns-and-reversals.part{i:02d}" for i in range(1, 4)]),
    ("35-ch25-trading-guidelines", [f"35-ch25-trading-guidelines.part{i:02d}" for i in range(1, 4)]),
]

DIRECT = [
    "02-list-of-terms-used-in-this-book.md",
    "27-ch18-patterns-related-to-yesterday-breakouts-breakout-pullbacks-and-failed-breakouts.md",
    "31-ch21-detailed-day-trading-examples.md",
    "32-ch22-daily-weekly-and-monthly-charts.md",
]


def merge_parts(parts):
    out = []
    for i, stem in enumerate(parts):
        path = CHUNKS / f"{stem}.md"
        if not path.exists():
            raise SystemExit(f"Missing chunk: {path}")
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
    return "".join(out)


def main():
    print("=== MERGE CHUNKS ===")
    for chapter, parts in JOBS:
        dest = CHAPTERS / f"{chapter}.md"
        body = merge_parts(parts)
        dest.write_text(body, encoding="utf-8")
        print(f"Wrote zh/chapters/{chapter}.md  ({len(body.encode('utf-8'))} bytes, {len(body)} chars)")

    print("\n=== SIZE REPORT (bytes) ===")
    print(f"{'file':<72} {'EN':>8} {'ZH':>8} {'ZH/EN':>7}")
    for name in DIRECT:
        en = EN_CH / name
        zh = CHAPTERS / name
        eb = en.stat().st_size if en.exists() else 0
        zb = zh.stat().st_size if zh.exists() else 0
        ratio = f"{zb/eb:.2f}" if eb else "n/a"
        print(f"{name:<72} {eb:8d} {zb:8d} {ratio:>7}")

    for chapter, parts in JOBS:
        name = f"{chapter}.md"
        en = EN_CH / name
        zh = CHAPTERS / name
        eb = en.stat().st_size if en.exists() else 0
        zb = zh.stat().st_size if zh.exists() else 0
        ratio = f"{zb/eb:.2f}" if eb else "n/a"
        print(f"{name:<72} {eb:8d} {zb:8d} {ratio:>7}")
        for p in parts:
            ep = EN_CK / f"{p}.md"
            zp = CHUNKS / f"{p}.md"
            epb = ep.stat().st_size if ep.exists() else 0
            zpb = zp.stat().st_size if zp.exists() else 0
            r = f"{zpb/epb:.2f}" if epb else "n/a"
            print(f"  chunk {p:<64} {epb:8d} {zpb:8d} {r:>7}")


if __name__ == "__main__":
    main()
