#!/usr/bin/env python3
"""Merge ch25 zh chunks and report sizes."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "zh" / "chunks"
CHAPTERS = ROOT / "zh" / "chapters"
STEM = "36-ch25-mathematics-of-trading-should-i-take-this-trade-will-i-make-money-if-i-take-this"
NPARTS = 11

bodies = []
parts_info = []
print("=== CH25 MERGE ===")
for i in range(1, NPARTS + 1):
    name = f"{STEM}.part{i:02d}.md"
    path = CHUNKS / name
    if not path.exists():
        raise SystemExit(f"Missing: {path}")
    text = path.read_text(encoding="utf-8")
    if not text.endswith("\n"):
        text += "\n"
    bodies.append(text)
    sz = path.stat().st_size
    cjk = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
    parts_info.append((name, sz, cjk))
    print(f"  {name}: {sz:,} bytes, cjk={cjk:,}")

merged = "\n".join(b.rstrip("\n") for b in bodies) + "\n"
dest = CHAPTERS / f"{STEM}.md"
dest.write_text(merged, encoding="utf-8")

en_path = ROOT / "en" / "chapters" / f"{STEM}.md"
en_bytes = en_path.stat().st_size if en_path.exists() else 0
zh_bytes = dest.stat().st_size
cjk = sum(1 for c in merged if "\u4e00" <= c <= "\u9fff")
ratio = (zh_bytes / en_bytes * 100) if en_bytes else 0.0
lines = merged.count("\n") + (0 if merged.endswith("\n") else 1)

print()
print(f"Wrote: {dest}")
print(f"ZH chapter: {zh_bytes:,} bytes, chars={len(merged):,}, lines≈{lines}, cjk={cjk:,}")
print(f"EN chapter: {en_bytes:,} bytes")
print(f"ZH/EN byte ratio: {ratio:.1f}%")
print(f"Chunk sum: {sum(s for _, s, _ in parts_info):,} bytes")
print(f"PDF pages: 467–523 (57 pages)")
