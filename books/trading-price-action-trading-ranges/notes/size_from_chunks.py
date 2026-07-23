#!/usr/bin/env python3
"""Report sizes of assigned zh chunks and write merged chapters + size report."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "zh" / "chunks"
CHAPTERS = ROOT / "zh" / "chapters"
NOTES = ROOT / "notes"
CHAPTERS.mkdir(parents=True, exist_ok=True)

JOBS = {
    "03-introduction": 6,
    "07-part-i-breakouts-transitioning-into-a-new-trend": 4,
    "09-ch02-signs-of-strength-in-a-breakout": 4,
    "13-ch06-gaps": 4,
}


def main():
    lines = ["# Size report — urgent chapters 03 / 07 / 09 / 13", ""]
    print("=== URGENT MERGE + SIZE REPORT ===")
    for stem, nparts in JOBS.items():
        bodies = []
        lines.append(f"## {stem}")
        total = 0
        for i in range(1, nparts + 1):
            p = CHUNKS / f"{stem}.part{i:02d}.md"
            if not p.exists():
                raise SystemExit(f"Missing: {p}")
            data = p.read_bytes()
            text = data.decode("utf-8")
            bodies.append(text.rstrip("\n"))
            cjk = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
            line = f"- chunk part{i:02d}: {len(data):,} bytes, cjk={cjk:,}"
            lines.append(line)
            print(f"  {stem}.part{i:02d}: {len(data)} bytes, cjk={cjk}")
            total += len(data)
        merged = "\n\n".join(bodies) + "\n"
        dest = CHAPTERS / f"{stem}.md"
        dest.write_text(merged, encoding="utf-8")
        en = ROOT / "en" / "chapters" / f"{stem}.md"
        en_b = en.stat().st_size if en.exists() else 0
        zh_b = dest.stat().st_size
        cjk = sum(1 for c in merged if "\u4e00" <= c <= "\u9fff")
        ratio = (zh_b / en_b * 100) if en_b else 0
        summary = (
            f"- **merged chapter**: {zh_b:,} bytes, chars={len(merged):,}, cjk={cjk:,}\n"
            f"- **EN chapter**: {en_b:,} bytes, zh/en ratio={ratio:.1f}%\n"
            f"- chunk bytes sum: {total:,}"
        )
        lines.append(summary)
        lines.append("")
        print(
            f"{stem}: zh={zh_b} bytes, cjk={cjk}, en={en_b} bytes, zh/en={ratio:.1f}%"
        )
        print(f"  wrote {dest}\n")
    out = NOTES / "merge_size_report_03_07_09_13.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Report: {out}")
    print(out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
