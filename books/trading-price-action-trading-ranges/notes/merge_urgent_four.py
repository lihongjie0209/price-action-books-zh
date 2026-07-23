#!/usr/bin/env python3
"""Merge urgent ZH chunks into chapters and print size report."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "zh" / "chunks"
CHAPTERS = ROOT / "zh" / "chapters"
CHAPTERS.mkdir(parents=True, exist_ok=True)

JOBS = [
    ("03-introduction", list(range(1, 7))),
    ("07-part-i-breakouts-transitioning-into-a-new-trend", list(range(1, 5))),
    ("09-ch02-signs-of-strength-in-a-breakout", list(range(1, 5))),
    ("13-ch06-gaps", list(range(1, 5))),
]


def merge_one(stem: str, part_nums: list[int]):
    parts_info = []
    bodies = []
    for n in part_nums:
        name = f"{stem}.part{n:02d}.md"
        path = CHUNKS / name
        if not path.exists():
            raise SystemExit(f"Missing chunk: {path}")
        text = path.read_text(encoding="utf-8")
        if not text.endswith("\n"):
            text += "\n"
        bodies.append(text)
        parts_info.append((name, path.stat().st_size))
    merged = "\n".join(b.rstrip("\n") for b in bodies) + "\n"
    return merged, parts_info


def main():
    print("=== URGENT MERGE RESULTS ===")
    for stem, part_nums in JOBS:
        body, parts_info = merge_one(stem, part_nums)
        dest = CHAPTERS / f"{stem}.md"
        dest.write_text(body, encoding="utf-8")
        en_path = ROOT / "en" / "chapters" / f"{stem}.md"
        en_bytes = en_path.stat().st_size if en_path.exists() else 0
        zh_bytes = dest.stat().st_size
        cjk = sum(1 for c in body if "\u4e00" <= c <= "\u9fff")
        ratio = (zh_bytes / en_bytes * 100) if en_bytes else 0.0
        print(
            f"{stem}: zh={zh_bytes} bytes, chars={len(body)}, lines={body.count(chr(10))+1}, "
            f"cjk={cjk}, en={en_bytes} bytes, zh/en={ratio:.1f}%"
        )
        print(f"  wrote {dest}")
        for name, size in parts_info:
            print(f"    {name}: {size} bytes")
        print()


if __name__ == "__main__":
    main()
