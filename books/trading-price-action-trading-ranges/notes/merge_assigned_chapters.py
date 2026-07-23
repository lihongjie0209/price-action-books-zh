#!/usr/bin/env python3
"""Concatenate assigned zh/chunks/*.partNN.md into zh/chapters/*.md and write size report."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "zh" / "chunks"
CHAPTERS = ROOT / "zh" / "chapters"
NOTES = ROOT / "notes"
CHAPTERS.mkdir(parents=True, exist_ok=True)

JOBS = [
    (
        "19-part-iii-pullbacks-trends-converting-to-trading-ranges",
        list(range(1, 6)),
    ),
    (
        "21-ch12-double-top-bear-flags-and-double-bottom-bull-flags",
        list(range(1, 4)),
    ),
    (
        "26-ch17-bar-counting-high-and-low-1-2-3-and-4-patterns-and-abc-corrections",
        list(range(1, 9)),
    ),
]


def merge_one(stem: str, part_nums: list[int]) -> tuple[str, list[tuple[str, int]]]:
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
    # join with single blank line between parts (avoid triple blanks if parts already end with newlines)
    merged = "\n".join(b.rstrip("\n") for b in bodies) + "\n"
    return merged, parts_info


def main():
    report_lines = ["# Merge size report — assigned chapters 19 / 21 / 26", ""]
    print("=== MERGE RESULTS ===")
    for stem, part_nums in JOBS:
        body, parts_info = merge_one(stem, part_nums)
        dest = CHAPTERS / f"{stem}.md"
        dest.write_text(body, encoding="utf-8")
        en_path = ROOT / "en" / "chapters" / f"{stem}.md"
        en_bytes = en_path.stat().st_size if en_path.exists() else 0
        zh_bytes = dest.stat().st_size
        cjk = sum(1 for c in body if "\u4e00" <= c <= "\u9fff")
        ratio = (zh_bytes / en_bytes * 100) if en_bytes else 0.0
        line = (
            f"{stem}: zh={zh_bytes} bytes, chars={len(body)}, lines={body.count(chr(10))+1}, "
            f"cjk={cjk}, en={en_bytes} bytes, zh/en={ratio:.1f}%"
        )
        print(line)
        report_lines.append(f"## `{stem}.md`")
        report_lines.append("")
        report_lines.append(f"- EN bytes: {en_bytes:,}")
        report_lines.append(f"- ZH bytes: {zh_bytes:,}")
        report_lines.append(f"- ZH chars: {len(body):,}")
        report_lines.append(f"- ZH lines: {body.count(chr(10))+1:,}")
        report_lines.append(f"- CJK chars: {cjk:,}")
        report_lines.append(f"- ZH/EN byte ratio: {ratio:.1f}%")
        report_lines.append(f"- Chunks ({len(parts_info)}):")
        for name, size in parts_info:
            report_lines.append(f"  - `{name}`: {size:,} bytes")
        report_lines.append("")
        print(f"  wrote {dest}")
        for name, size in parts_info:
            print(f"    {name}: {size} bytes")
        print()
    out = NOTES / "merge_size_report_19_21_26.md"
    out.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"Report: {out}")


if __name__ == "__main__":
    main()
