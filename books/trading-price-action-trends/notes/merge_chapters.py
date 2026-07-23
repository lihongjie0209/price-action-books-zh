#!/usr/bin/env python3
"""Concatenate zh/chunks/*.partNN.md into zh/chapters/*.md in order."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "zh" / "chunks"
CHAPTERS = ROOT / "zh" / "chapters"
CHAPTERS.mkdir(parents=True, exist_ok=True)

# (chapter_stem, list of part stems without .md)
JOBS = [
    ("04-introduction", [f"04-introduction.part{i:02d}" for i in range(1, 9)]),
    ("05-part-i-price-action", [f"05-part-i-price-action.part{i:02d}" for i in range(1, 6)]),
    ("11-ch06-signal-bars-other-types", [f"11-ch06-signal-bars-other-types.part{i:02d}" for i in range(1, 10)]),
    ("21-ch15-channels", [f"21-ch15-channels.part{i:02d}" for i in range(1, 7)]),
    ("25-ch18-example-of-how-to-trade-a-trend", [f"25-ch18-example-of-how-to-trade-a-trend.part{i:02d}" for i in range(1, 5)]),
    ("29-ch21-spike-and-channel-trend", [f"29-ch21-spike-and-channel-trend.part{i:02d}" for i in range(1, 7)]),
    ("30-ch22-trending-trading-range-days", [f"30-ch22-trending-trading-range-days.part{i:02d}" for i in range(1, 5)]),
    ("31-ch23-trend-from-the-open-and-small-pullback-trends", [f"31-ch23-trend-from-the-open-and-small-pullback-trends.part{i:02d}" for i in range(1, 6)]),
]


def merge_parts(parts):
    out = []
    for i, stem in enumerate(parts):
        path = CHUNKS / f"{stem}.md"
        if not path.exists():
            raise SystemExit(f"Missing chunk: {path}")
        text = path.read_text(encoding="utf-8")
        if i > 0:
            # drop leading "chunk continuation" header line only; keep page comments
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
    for chapter, parts in JOBS:
        dest = CHAPTERS / f"{chapter}.md"
        body = merge_parts(parts)
        dest.write_text(body, encoding="utf-8")
        print(f"Wrote {dest.relative_to(ROOT)} ({len(body)} chars, {body.count(chr(10))+1} lines)")
    # also print inventory of all zh chunks for the assigned chapters
    for chapter, parts in JOBS:
        missing = [p for p in parts if not (CHUNKS / f"{p}.md").exists()]
        present = [p for p in parts if (CHUNKS / f"{p}.md").exists()]
        sizes = sum((CHUNKS / f"{p}.md").stat().st_size for p in present)
        print(f"{chapter}: {len(present)}/{len(parts)} chunks, {sizes} bytes, missing={missing}")


if __name__ == "__main__":
    main()
