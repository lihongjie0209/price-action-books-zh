#!/usr/bin/env python3
"""Merge assigned zh chunks into zh chapters."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "zh" / "chunks"
CHAPTERS = ROOT / "zh" / "chapters"
CHAPTERS.mkdir(parents=True, exist_ok=True)

JOBS = [
    ("30-part-iv-trading-ranges", [f"30-part-iv-trading-ranges.part{i:02d}" for i in range(1, 9)]),
    ("32-ch22-tight-trading-ranges", [f"32-ch22-tight-trading-ranges.part{i:02d}" for i in range(1, 6)]),
    (
        "36-ch25-mathematics-of-trading-should-i-take-this-trade-will-i-make-money-if-i-take-this",
        [
            f"36-ch25-mathematics-of-trading-should-i-take-this-trade-will-i-make-money-if-i-take-this.part{i:02d}"
            for i in range(1, 12)
        ],
    ),
]


def merge_parts(parts):
    out = []
    for i, stem in enumerate(parts):
        path = CHUNKS / f"{stem}.md"
        if not path.exists():
            raise SystemExit(f"Missing chunk: {path}")
        text = path.read_text(encoding="utf-8")
        if i > 0:
            if out and not out[-1].endswith("\n"):
                out.append("\n")
            out.append("\n")
        out.append(text if text.endswith("\n") else text + "\n")
    return "".join(out)


def main():
    report = []
    for chapter, parts in JOBS:
        dest = CHAPTERS / f"{chapter}.md"
        body = merge_parts(parts)
        # strip merge markers if any leftover
        body = body.replace("<!-- MERGE_PART02 -->\n", "")
        dest.write_text(body, encoding="utf-8")
        chunk_sizes = []
        for p in parts:
            sz = (CHUNKS / f"{p}.md").stat().st_size
            chunk_sizes.append((p, sz))
        ch_sz = dest.stat().st_size
        report.append((chapter, chunk_sizes, ch_sz, body.count("\n") + 1))
        print(f"Wrote {dest} ({ch_sz} bytes, {body.count(chr(10))+1} lines)")
        for name, sz in chunk_sizes:
            print(f"  {name}.md: {sz} bytes")
        print(f"  TOTAL chapter: {ch_sz} bytes")
        # EN comparison
        en = ROOT / "en" / "chapters" / f"{chapter}.md"
        if en.exists():
            en_sz = en.stat().st_size
            print(f"  EN chapter: {en_sz} bytes; ZH/EN ratio: {ch_sz/en_sz:.2%}")


if __name__ == "__main__":
    main()
