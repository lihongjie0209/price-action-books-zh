#!/usr/bin/env python3
"""Inject Markdown image references into EN and ZH chapter files.

Uses assets/figures_manifest.json (from extract_images.py).
Relative path from en/chapters or zh/chapters: ../../assets/figures/...
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "assets" / "figures_manifest.json"
EN_CH = ROOT / "en" / "chapters"
ZH_CH = ROOT / "zh" / "chapters"
REL_PREFIX = "../../assets/figures"

# Match already-injected images so we don't double-insert
IMG_LINE = re.compile(r"^\s*!\[[^\]]*\]\([^)]*assets/figures/")


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def fig_rel(lab: str, fig_files: dict[str, str]) -> str | None:
    path = fig_files.get(lab) or fig_files.get(lab.upper()) or fig_files.get(lab.lower())
    if not path:
        # try normalize 1.1 style
        for k, v in fig_files.items():
            if k.lower() == lab.lower():
                path = v
                break
    if not path:
        return None
    # path is assets/figures/foo.png → ../../assets/figures/foo.png
    name = Path(path).name
    return f"{REL_PREFIX}/{name}"


def inject_en(text: str, fig_files: dict[str, str]) -> tuple[str, int]:
    """After FIGURE x.y or Figure x.y heading lines, insert image once."""
    lines = text.splitlines()
    out: list[str] = []
    inserted = 0
    i = 0
    # Patterns for figure id
    fig_re = re.compile(
        r"(?:FIGURE|Figure|Fig\.?)\s*([0-9]+(?:\.[0-9]+)?|P[IVX]+\.[0-9]+|I\.[0-9]+)",
        re.I,
    )
    seen_in_block: set[str] = set()

    while i < len(lines):
        line = lines[i]
        out.append(line)
        m = fig_re.search(line)
        if m:
            lab = m.group(1)
            # normalize PI.1 etc
            if re.match(r"^[PpIi]", lab):
                lab_key = lab.upper() if lab[0].isalpha() else lab
            else:
                lab_key = lab
            # resolve key in fig_files
            key = None
            for k in fig_files:
                if k.lower() == lab_key.lower():
                    key = k
                    break
            if key and key not in seen_in_block:
                # look ahead: already has image?
                j = i + 1
                while j < len(lines) and j <= i + 4:
                    if IMG_LINE.search(lines[j]) and key.replace(".", "_") in lines[j].replace(
                        ".", "_"
                    ):
                        key = None
                        break
                    if lines[j].strip() and not lines[j].strip().startswith("<!--"):
                        # if next content is another FIGURE, don't skip
                        break
                    j += 1
                if key:
                    rel = fig_rel(key, fig_files)
                    if rel:
                        # skip blank lines then insert once
                        # avoid if immediately next non-empty is already our image
                        nxt = ""
                        for k2 in range(i + 1, min(i + 3, len(lines))):
                            if lines[k2].strip():
                                nxt = lines[k2].strip()
                                break
                        if not (nxt.startswith("![") and "assets/figures" in nxt):
                            cap = f"Figure {key}"
                            out.append("")
                            out.append(f"![{cap}]({rel})")
                            out.append("")
                            inserted += 1
                            seen_in_block.add(key)
        i += 1
    return "\n".join(out) + ("\n" if text.endswith("\n") else ""), inserted


def inject_zh(text: str, fig_files: dict[str, str]) -> tuple[str, int]:
    """After 图 x.y headings, insert image once."""
    lines = text.splitlines()
    out: list[str] = []
    inserted = 0
    fig_re = re.compile(
        r"图\s*([0-9]+(?:\.[0-9]+)?|P[IVX]+\.[0-9]+|I\.[0-9]+)",
        re.I,
    )
    seen: set[str] = set()
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        m = fig_re.search(line)
        if m:
            lab = m.group(1)
            key = None
            for k in fig_files:
                if k.lower() == lab.lower():
                    key = k
                    break
            if key and key not in seen:
                nxt = ""
                for k2 in range(i + 1, min(i + 3, len(lines))):
                    if lines[k2].strip():
                        nxt = lines[k2].strip()
                        break
                if not (nxt.startswith("![") and "assets/figures" in nxt):
                    rel = fig_rel(key, fig_files)
                    if rel:
                        out.append("")
                        out.append(f"![图 {key}]({rel})")
                        out.append("")
                        inserted += 1
                        seen.add(key)
        i += 1
    return "\n".join(out) + ("\n" if text.endswith("\n") else ""), inserted


def also_inject_by_page_marker(
    text: str, page_primary: dict[int, str], already_labs: set[str]
) -> tuple[str, int]:
    """For PDF pages with a primary chart but no figure label nearby, insert page image once after page marker.

    Skipped if the following few lines already contain an assets/figures image.
    """
    lines = text.splitlines()
    out: list[str] = []
    inserted = 0
    page_re = re.compile(r"<!-- PDF page (\d+)")
    i = 0
    while i < len(lines):
        out.append(lines[i])
        m = page_re.search(lines[i])
        if m:
            page = int(m.group(1))
            primary = page_primary.get(page)
            if primary:
                # skip if next lines already have image
                has_img = False
                for k2 in range(i + 1, min(i + 8, len(lines))):
                    if IMG_LINE.search(lines[k2]) or (
                        lines[k2].strip().startswith("![") and "assets/figures" in lines[k2]
                    ):
                        has_img = True
                        break
                    # stop at next page marker
                    if page_re.search(lines[k2]):
                        break
                if not has_img:
                    name = Path(primary).name
                    rel = f"{REL_PREFIX}/{name}"
                    out.append("")
                    out.append(f"![PDF page {page}]({rel})")
                    out.append("")
                    inserted += 1
        i += 1
    return "\n".join(out) + ("\n" if text.endswith("\n") else ""), inserted


def process_dir(ch_dir: Path, lang: str, fig_files: dict, page_primary: dict) -> None:
    total = 0
    for p in sorted(ch_dir.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        if lang == "en":
            new, n = inject_en(text, fig_files)
        else:
            new, n = inject_zh(text, fig_files)
        # Only add page-level fallback for pages that look like figure-only in EN?
        # Enable lightly: only if chapter mentions few figures - actually skip page-wide
        # to avoid clutter; figure-label injection is enough.
        if new != text:
            p.write_text(new if new.endswith("\n") else new + "\n", encoding="utf-8")
        total += n
        if n:
            print(f"  {lang}/{p.name}: +{n} images")
    print(f"{lang} total insertions: {total}")


def main() -> int:
    if not MANIFEST.exists():
        print("Run extract_images.py first", file=sys.stderr)
        return 1
    man = load_manifest()
    fig_files = man["figure_files"]
    page_primary = {
        r["page"]: r["primary"] for r in man["page_records"] if r.get("primary")
    }
    print(f"Figure files available: {len(fig_files)}")
    process_dir(EN_CH, "en", fig_files, page_primary)
    process_dir(ZH_CH, "zh", fig_files, page_primary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
