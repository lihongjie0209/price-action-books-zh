#!/usr/bin/env python3
"""Extract figure images from a Brooks book PDF with reliable Figure-label mapping.

Writes **lossless PNG** only. Do **not** post-process with lossy WebP — chart
axis/bar labels become unreadable.

Fixes the common bug of binding a figure caption on a text-only page to a
full-page screenshot. Strategy:

1. Extract all sufficiently large embedded images per PDF page via
   ``extract_image`` (raw) when the colorspace is normal RGB/gray.
2. Parse EN full_book.md for Figure X.Y mentions per page.
3. For each figure label, score candidate pages (mention page ±1, ±2):
   - Prefer pages with real embedded chart images (size/aspect filters).
   - Prefer landscape chart-like images over portrait full-page text renders.
   - Use full-page / clip render only as last resort (needed for Separation/Black).
4. Write fig_{label}.png and figures_manifest.json.

Usage:
  python scripts/extract_figures.py books/trading-price-action-trading-ranges \\
      --pdf "/root/book/Trading Price Action TRADING RANGES.pdf"
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import fitz

MIN_W = 180
MIN_H = 120
MIN_PIXELS = 40_000
# Reject tiny icons and reject near-full-page grayscale dumps unless needed
MAX_ASPECT = 4.0  # w/h or h/w


def slug_label(lab: str) -> str:
    return lab.replace(".", "_")


def extract_page_images(doc: fitz.Document, fig_dir: Path) -> dict[int, list[dict]]:
    """page_num -> list of {path, width, height, pixels, score_hint}"""
    by_page: dict[int, list[dict]] = {}
    for i in range(doc.page_count):
        page_num = i + 1
        page = doc[i]
        found: list[dict] = []
        for j, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            try:
                # Prefer extract_image (preserves JPEG/PNG payload). Pixmap on
                # Separation(Black)/odd DeviceGray often washes out labels.
                info = doc.extract_image(xref)
                w, h = info["width"], info["height"]
                if w < MIN_W or h < MIN_H or w * h < MIN_PIXELS:
                    continue
                aspect = max(w / h, h / w)
                if aspect > MAX_ASPECT:
                    continue
                raw = info["image"]
                ext = (info.get("ext") or "png").lower()
                # Decode with Pillow when available for a true RGB PNG on disk
                path = fig_dir / f"_emb_p{page_num:03d}_{j:02d}.png"
                try:
                    from PIL import Image
                    import io

                    im = Image.open(io.BytesIO(raw))
                    # Low-range gray embeds (common in TRENDS Separation/Black)
                    # are unusable — skip so page-render fallback can win later.
                    if im.mode == "L":
                        lo, hi = im.getextrema()
                        if hi - lo < 100:
                            continue
                    if im.mode in ("P", "PA"):
                        im = im.convert("RGBA")
                    if im.mode in ("RGBA", "LA"):
                        bg = Image.new("RGB", im.size, (255, 255, 255))
                        bg.paste(im, mask=im.split()[-1])
                        im = bg
                    elif im.mode != "RGB":
                        im = im.convert("RGB")
                    im.save(path, format="PNG", compress_level=3)
                    w, h = im.size
                except Exception:
                    # Fall back to writing raw payload if PNG; else Pixmap RGB
                    if ext in ("png", "jpg", "jpeg"):
                        path = fig_dir / f"_emb_p{page_num:03d}_{j:02d}.{ext if ext != 'jpeg' else 'jpg'}"
                        path.write_bytes(raw)
                    else:
                        pix = fitz.Pixmap(doc, xref)
                        if pix.n - pix.alpha < 3:
                            pix = fitz.Pixmap(fitz.csRGB, pix)
                        if pix.alpha:
                            pix = fitz.Pixmap(pix, 0)
                        path = fig_dir / f"_emb_p{page_num:03d}_{j:02d}.png"
                        pix.save(str(path))
                        w, h = pix.width, pix.height
                landscape_bonus = 1.15 if w >= h else 1.0
                score = w * h * landscape_bonus
                found.append(
                    {
                        "path": path,
                        "width": w,
                        "height": h,
                        "pixels": w * h,
                        "score": score,
                        "kind": "embedded",
                        "page": page_num,
                    }
                )
            except Exception:
                continue
        if found:
            found.sort(key=lambda x: -x["score"])
            by_page[page_num] = found
    return by_page


def labels_by_page_from_markdown(full_md: Path) -> dict[int, list[str]]:
    text = full_md.read_text(encoding="utf-8", errors="replace")
    parts = re.split(r"<!-- PDF page (\d+)(?:[^>]*)-->", text)
    by_page: dict[int, list[str]] = defaultdict(list)
    i = 1
    while i + 1 < len(parts):
        try:
            page = int(parts[i])
        except ValueError:
            i += 1
            continue
        body = parts[i + 1] if i + 1 < len(parts) else ""
        for lab in re.findall(
            r"(?:FIGURE|Figure|Fig\.?)\s*([0-9]+(?:\.[0-9]+)?|P[IVX]+\.[0-9]+|I\.[0-9]+)",
            body,
            flags=re.I,
        ):
            lab = lab.upper() if lab[0].isalpha() else lab
            if lab not in by_page[page]:
                by_page[page].append(lab)
        i += 2
    return dict(by_page)


def best_image_for_label(
    lab: str,
    mention_pages: list[int],
    page_images: dict[int, list[dict]],
    doc: fitz.Document,
    fig_dir: Path,
) -> dict | None:
    """Pick best embedded image near mention pages; full-page only as fallback."""
    candidates: list[dict] = []
    # Expand search window around every mention
    pages_to_try: list[int] = []
    for p in mention_pages:
        for d in (0, 1, -1, 2, -2):
            q = p + d
            if q >= 1 and q not in pages_to_try:
                pages_to_try.append(q)

    for p in pages_to_try:
        for img in page_images.get(p, []):
            # Prefer pages that are not pure text with tiny decorations —
            # already filtered by size.
            # Slight boost if page is the first page AFTER a caption-only page
            boost = 1.0
            if p in mention_pages:
                boost *= 1.05
            # Prefer page+1 when caption is on previous page (common layout)
            if any(p == m + 1 for m in mention_pages):
                boost *= 1.25
            candidates.append({**img, "score": img["score"] * boost})

    if candidates:
        candidates.sort(key=lambda x: -x["score"])
        return candidates[0]

    # Fallback: full-page render of best mention page that has little text? 
    # Prefer mention page with MOST images area — if still none, render page+1 then page.
    for p in pages_to_try:
        page = doc[p - 1]
        text_len = len((page.get_text() or "").strip())
        # Skip dense text pages for full-page fallback if possible
        if text_len > 1800 and p == pages_to_try[0]:
            continue
        try:
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
            # Skip if looks like a full text page (very tall portrait + lots of text)
            if text_len > 1200 and pix.height > pix.width * 1.15:
                continue
            fname = f"_full_p{p:03d}.png"
            path = fig_dir / fname
            pix.save(str(path))
            return {
                "path": path,
                "width": pix.width,
                "height": pix.height,
                "pixels": pix.width * pix.height,
                "score": pix.width * pix.height * 0.3,  # deprioritized
                "kind": "fullpage",
                "page": p,
            }
        except Exception:
            continue

    # Last resort: fullpage of first mention even if text-heavy
    p = mention_pages[0]
    try:
        page = doc[p - 1]
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
        path = fig_dir / f"_full_p{p:03d}_last.png"
        pix.save(str(path))
        return {
            "path": path,
            "width": pix.width,
            "height": pix.height,
            "pixels": pix.width * pix.height,
            "score": 1,
            "kind": "fullpage-lastresort",
            "page": p,
        }
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("book_dir", type=Path, help="books/<id> directory")
    ap.add_argument("--pdf", type=Path, required=True)
    args = ap.parse_args()
    book = args.book_dir.resolve()
    pdf = args.pdf.resolve()
    fig_dir = book / "assets" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    full_md = book / "en" / "full_book.md"
    if not pdf.exists():
        print(f"PDF missing: {pdf}", file=sys.stderr)
        return 1
    if not full_md.exists():
        print(f"full_book.md missing: {full_md}", file=sys.stderr)
        return 1

    # Clean previous fig_* and temps
    for p in fig_dir.glob("fig_*"):
        p.unlink()
    for p in fig_dir.glob("_emb_*"):
        p.unlink()
    for p in fig_dir.glob("_full_*"):
        p.unlink()

    doc = fitz.open(pdf)
    print(f"Extracting embedded images from {doc.page_count} pages…")
    page_images = extract_page_images(doc, fig_dir)
    print(f"Pages with embedded charts: {len(page_images)}")

    labels = labels_by_page_from_markdown(full_md)
    # invert: label -> mention pages
    label_pages: dict[str, list[int]] = defaultdict(list)
    for page, labs in labels.items():
        for lab in labs:
            label_pages[lab].append(page)

    fig_files: dict[str, str] = {}
    fig_to_page: dict[str, int] = {}
    fig_meta: dict[str, dict] = {}

    for lab, pages in sorted(label_pages.items(), key=lambda x: x[0]):
        best = best_image_for_label(lab, pages, page_images, doc, fig_dir)
        if not best:
            print(f"  SKIP {lab}: no image near pages {pages}")
            continue
        dest = fig_dir / f"fig_{slug_label(lab)}.png"
        dest.write_bytes(best["path"].read_bytes())
        fig_files[lab] = f"assets/figures/{dest.name}"
        fig_to_page[lab] = best["page"]
        fig_meta[lab] = {
            "page": best["page"],
            "kind": best["kind"],
            "width": best["width"],
            "height": best["height"],
            "mentions": pages,
        }
        print(
            f"  {lab} -> p{best['page']} {best['kind']} "
            f"{best['width']}x{best['height']} (mentions {pages})"
        )

    # cleanup temps
    for p in fig_dir.glob("_emb_*"):
        p.unlink(missing_ok=True)
    for p in fig_dir.glob("_full_*"):
        p.unlink(missing_ok=True)

    man = {
        "pdf": str(pdf),
        "figure_files": fig_files,
        "figure_to_page": fig_to_page,
        "figure_meta": fig_meta,
        "embedded_pages": len(page_images),
    }
    (book / "assets" / "figures_manifest.json").write_text(
        json.dumps(man, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Wrote {len(fig_files)} figures to {fig_dir}")
    # sanity: flag portrait fullpage-ish figures
    bad = [
        (lab, m)
        for lab, m in fig_meta.items()
        if m["kind"].startswith("fullpage") or m["height"] > m["width"] * 1.2
    ]
    if bad:
        print(f"WARNING: {len(bad)} figures may still be full-page/text-like:")
        for lab, m in bad[:15]:
            print(f"  {lab}: {m}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
