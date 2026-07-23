#!/usr/bin/env python3
"""Audit & fix ZH chapter mid-sentence breaks and figure reference integrity.

Usage:
  python scripts/audit_zh_chapters.py detect [--book ID] [--out PATH]
  python scripts/audit_zh_chapters.py fix [--book ID]
  python scripts/audit_zh_chapters.py figures [--book ID] [--out PATH]
  python scripts/audit_zh_chapters.py all [--book ID] [--out PATH]

Exit 0 when mid-breaks==0 / missing figures==0 for detect|figures|all.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BOOK_IDS = [
    "trading-price-action-trends",
    "trading-price-action-trading-ranges",
    "trading-price-action-reversals",
]

SENT_END = re.compile(
    r"(?:"
    r"[。！？…]"
    r"|[」』》）】]"
    r'|[.!?]["\')\]]?'
    r")\s*$"
)

PAGE_COMMENT = re.compile(r"<!--\s*PDF page\s+(\d+)\s*-->", re.I)
SOURCE_COMMENT = re.compile(r"<!--\s*Source PDF pages?\s+[^>]+-->", re.I)
HEADING = re.compile(r"^#{1,6}\s")
FIGURE_MD = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
HTML_ONLY = re.compile(r"^<!--.*?-->\s*$", re.S)


def zh_chapters_dir(book_id: str) -> Path:
    return REPO / "books" / book_id / "zh" / "chapters"


def figures_dir(book_id: str) -> Path:
    return REPO / "books" / book_id / "assets" / "figures"


def is_prose_block(text: str) -> bool:
    t = text.strip()
    if not t:
        return False
    if HEADING.match(t):
        return False
    if t.startswith("!["):
        return False
    if PAGE_COMMENT.fullmatch(t) or SOURCE_COMMENT.fullmatch(t) or HTML_ONLY.match(t):
        return False
    if t.startswith("|") and "|" in t[1:]:
        return False
    if t.startswith("- ") or t.startswith("* ") or re.match(r"^\d+\.\s", t):
        return False
    if t.startswith("```"):
        return False
    return True


def is_comment_block(text: str) -> bool:
    t = text.strip()
    if not t:
        return False
    if PAGE_COMMENT.fullmatch(t) or SOURCE_COMMENT.fullmatch(t):
        return True
    if HTML_ONLY.match(t) and not is_prose_block(t):
        return True
    return False


def ends_sentence(text: str) -> bool:
    t = text.rstrip()
    if not t:
        return True
    t2 = re.sub(r"[*_`]+$", "", t).rstrip()
    return bool(SENT_END.search(t2))


def looks_like_continuation(text: str) -> bool:
    t = text.lstrip()
    if not t or not is_prose_block(t):
        return False
    first = t.split("\n", 1)[0].strip()
    # Short bare running-header lines (e.g. "缺口") alone — not a mid-sentence join target
    if (
        "\n" not in t.strip()
        and len(first) <= 16
        and not re.search(r"[，,。；;：:！？]", first)
        and re.fullmatch(r"[\u4e00-\u9fffA-Za-z0-9\s：:\-—]+", first)
    ):
        return False
    return True


def split_top_blocks(text: str) -> list[str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return re.split(r"\n{2,}", text)


def detect_midbreaks_in_text(text: str, path: str) -> list[dict]:
    issues: list[dict] = []
    blocks = split_top_blocks(text)
    i = 0
    while i < len(blocks) - 1:
        left = blocks[i]
        if not is_prose_block(left):
            i += 1
            continue
        j = i + 1
        page_markers: list[str] = []
        while j < len(blocks) and is_comment_block(blocks[j]):
            if PAGE_COMMENT.search(blocks[j]):
                page_markers.append(blocks[j].strip())
            j += 1
        if j >= len(blocks):
            break
        right = blocks[j]
        if (
            is_prose_block(right)
            and not ends_sentence(left)
            and looks_like_continuation(right)
        ):
            issues.append(
                {
                    "path": path,
                    "left_tail": left.rstrip()[-60:].replace("\n", "⏎"),
                    "right_head": right.lstrip()[:60].replace("\n", "⏎"),
                    "page_markers": page_markers,
                }
            )
        i += 1
    return issues


def _inline_comments(comments: list[str]) -> str:
    parts: list[str] = []
    for c in comments:
        m = PAGE_COMMENT.search(c)
        if m:
            parts.append(f"<!-- PDF page {m.group(1)} -->")
        else:
            c2 = c.strip()
            if c2:
                parts.append(c2)
    if not parts:
        return ""
    return " " + " ".join(parts) + " "


def _join_prose(left: str, comments: list[str], right: str) -> str:
    left_s = left.rstrip()
    right_s = right.lstrip()
    mid = _inline_comments(comments)
    if mid:
        return left_s + mid + right_s
    if re.search(r"[A-Za-z0-9]$", left_s) and re.match(r"[A-Za-z0-9]", right_s):
        return left_s + " " + right_s
    return left_s + right_s


def fix_midbreaks_in_text(text: str) -> tuple[str, int]:
    """Join mid-sentence blank-line splits; page markers become inline comments."""
    had_trailing_nl = text.endswith("\n")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    joins = 0

    for _ in range(40):
        blocks = split_top_blocks(text)
        out: list[str] = []
        i = 0
        changed = False
        while i < len(blocks):
            left = blocks[i]
            if not is_prose_block(left):
                out.append(left)
                i += 1
                continue

            # Collect following comment-only blocks
            j = i + 1
            comments: list[str] = []
            while j < len(blocks) and is_comment_block(blocks[j]):
                comments.append(blocks[j].strip())
                j += 1

            if j < len(blocks):
                right = blocks[j]
                if (
                    is_prose_block(right)
                    and not ends_sentence(left)
                    and looks_like_continuation(right)
                ):
                    joined = _join_prose(left, comments, right)
                    joins += 1
                    changed = True
                    # Chain-merge further incomplete joins
                    i = j + 1
                    while i < len(blocks) and not ends_sentence(joined):
                        k = i
                        more: list[str] = []
                        while k < len(blocks) and is_comment_block(blocks[k]):
                            more.append(blocks[k].strip())
                            k += 1
                        if k >= len(blocks):
                            break
                        if not (
                            is_prose_block(blocks[k])
                            and looks_like_continuation(blocks[k])
                        ):
                            break
                        joined = _join_prose(joined, more, blocks[k])
                        joins += 1
                        i = k + 1
                    out.append(joined)
                    continue

            out.append(left)
            # comments stay as separate blocks if we didn't join
            for c in comments:
                out.append(c)
            i = j if comments else i + 1

        new_text = "\n\n".join(out)
        if not changed:
            text = new_text
            break
        text = new_text

    if had_trailing_nl and not text.endswith("\n"):
        text += "\n"
    return text, joins


def iter_books(book: str | None):
    ids = [book] if book else BOOK_IDS
    for bid in ids:
        d = zh_chapters_dir(bid)
        if not d.is_dir():
            print(f"WARN: missing {d}", file=sys.stderr)
            continue
        yield bid, sorted(d.glob("*.md"))


def cmd_detect(book: str | None, out_path: Path | None) -> int:
    lines: list[str] = []
    total = 0
    for bid, files in iter_books(book):
        book_n = 0
        for f in files:
            text = f.read_text(encoding="utf-8")
            issues = detect_midbreaks_in_text(text, str(f.relative_to(REPO)))
            book_n += len(issues)
            for it in issues:
                lines.append(
                    f"{it['path']}: …{it['left_tail']} || {it['right_head']}…"
                    + (f"  markers={it['page_markers']}" if it["page_markers"] else "")
                )
        lines.append(f"BOOK {bid}: mid_breaks={book_n}")
        total += book_n
    lines.append(f"TOTAL mid_breaks={total}")
    report = "\n".join(lines) + "\n"
    print(report, end="")
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
    return 0 if total == 0 else 1


def cmd_fix(book: str | None) -> int:
    total_joins = 0
    total_files = 0
    for bid, files in iter_books(book):
        book_joins = 0
        book_files = 0
        for f in files:
            original = f.read_text(encoding="utf-8")
            fixed, n = fix_midbreaks_in_text(original)
            # second pass for residual chains
            fixed2, n2 = fix_midbreaks_in_text(fixed)
            n += n2
            fixed = fixed2
            if fixed != original:
                if not fixed.endswith("\n"):
                    fixed += "\n"
                f.write_text(fixed, encoding="utf-8")
                book_files += 1
                book_joins += n
        total_joins += book_joins
        total_files += book_files
        print(f"BOOK {bid}: joins={book_joins}, files_written={book_files}")
    print(f"TOTAL joins={total_joins}, files_written={total_files}")
    return 0


def resolve_fig_path(book_id: str, ref: str, chapter_file: Path) -> Path | None:
    ref = ref.strip()
    if ref.startswith("http://") or ref.startswith("https://"):
        return None
    cand = (chapter_file.parent / ref).resolve()
    if cand.is_file():
        return cand
    name = Path(ref).name
    cand2 = figures_dir(book_id) / name
    if cand2.is_file():
        return cand2
    return cand


def cmd_figures(book: str | None, out_path: Path | None) -> int:
    lines: list[str] = []
    missing_total = 0
    for bid, files in iter_books(book):
        missing: list[tuple[str, str, str]] = []
        ok = 0
        chapter_sets = [files]
        en_dir = REPO / "books" / bid / "en" / "chapters"
        if en_dir.is_dir():
            chapter_sets.append(sorted(en_dir.glob("*.md")))
        for flist in chapter_sets:
            for f in flist:
                text = f.read_text(encoding="utf-8")
                for m in FIGURE_MD.finditer(text):
                    alt, ref = m.group(1), m.group(2)
                    resolved = resolve_fig_path(bid, ref, f)
                    if resolved is None:
                        ok += 1
                        continue
                    if resolved.is_file():
                        ok += 1
                    else:
                        missing.append((str(f.relative_to(REPO)), ref, alt))
        missing_total += len(missing)
        lines.append(f"BOOK {bid}: ok_refs={ok}, missing={len(missing)}")
        for path, ref, alt in missing[:80]:
            lines.append(f"  MISSING {path}: {ref} ({alt})")
        if len(missing) > 80:
            lines.append(f"  ... and {len(missing) - 80} more")
        fig_dir = figures_dir(bid)
        n_assets = len(list(fig_dir.glob("fig_*"))) if fig_dir.is_dir() else 0
        lines.append(f"  assets fig_*: {n_assets}")
    lines.append(f"TOTAL missing_figure_refs={missing_total}")
    report = "\n".join(lines) + "\n"
    print(report, end="")
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
    return 0 if missing_total == 0 else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=["detect", "fix", "figures", "all"])
    ap.add_argument("--book", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    out = Path(args.out) if args.out else None

    if args.command == "detect":
        return cmd_detect(args.book, out)
    if args.command == "fix":
        return cmd_fix(args.book)
    if args.command == "figures":
        return cmd_figures(args.book, out)
    if args.command == "all":
        r1 = cmd_detect(args.book, out)
        fig_out = None
        if out:
            fig_out = out.with_name("figure_refs_report.txt")
        r2 = cmd_figures(args.book, fig_out)
        return 0 if (r1 == 0 and r2 == 0) else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
