#!/usr/bin/env python3
"""Extract chart images from Trading Price Action TRENDS PDF into assets/figures/.

Also builds a JSON manifest mapping PDF page → image files and figure labels
discovered from the English full_book / chapter Markdown.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import fitz

PDF_PATH = Path("/root/book/Trading Price Action TRENDS.pdf")
ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "assets" / "figures"
MANIFEST = ROOT / "assets" / "figures_manifest.json"
EN_FULL = ROOT / "en" / "full_book.md"
EN_CH = ROOT / "en" / "chapters"

# Prefer larger pixmaps; skip tiny decorations
MIN_WIDTH = 200
MIN_HEIGHT = 150
MIN_PIXELS = 80_000


def ensure_rgb(pix: fitz.Pixmap) -> fitz.Pixmap:
    if pix.n - pix.alpha >= 3:
        return pix
    # Gray or CMYK → RGB
    return fitz.Pixmap(fitz.csRGB, pix)


def save_pixmap(pix: fitz.Pixmap, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if pix.alpha:
        pix = fitz.Pixmap(pix, 0)  # drop alpha
    pix = ensure_rgb(pix)
    pix.save(str(path))


def extract_page_images(doc: fitz.Document) -> list[dict]:
    """Extract embedded images per page; also render full page when page is figure-heavy."""
    records: list[dict] = []
    seen_xref_paths: dict[int, str] = {}

    for page_index in range(doc.page_count):
        page_num = page_index + 1
        page = doc[page_index]
        text = page.get_text() or ""
        text_len = len(text.strip())
        images = page.get_images(full=True)

        page_files: list[str] = []
        best: tuple[int, int, int] | None = None  # pixels, w, h
        best_path: str | None = None

        for img_i, img in enumerate(images):
            xref = img[0]
            try:
                if xref in seen_xref_paths:
                    # same image reused — still associate with this page
                    rel = seen_xref_paths[xref]
                    page_files.append(rel)
                    continue
                pix = fitz.Pixmap(doc, xref)
                w, h = pix.width, pix.height
                if w < MIN_WIDTH or h < MIN_HEIGHT or w * h < MIN_PIXELS:
                    continue
                fname = f"page{page_num:03d}_img{img_i:02d}_xref{xref}.png"
                out = FIG_DIR / fname
                save_pixmap(pix, out)
                rel = f"assets/figures/{fname}"
                seen_xref_paths[xref] = rel
                page_files.append(rel)
                if best is None or w * h > best[0]:
                    best = (w * h, w, h)
                    best_path = rel
            except Exception as e:
                print(f"warn page {page_num} img {img_i} xref={xref}: {e}", file=sys.stderr)

        # Full-page render for empty/near-empty pages (likely full-bleed charts)
        # or when no usable embedded image was saved
        need_render = (text_len < 80 and page_num > 2) or (
            text_len < 400 and not page_files and page_num > 2
        )
        render_path = None
        if need_render or (not page_files and images):
            # also render if we have images but failed size filter and page looks chart-like
            try:
                # 1.5x scale for readability
                mat = fitz.Matrix(1.5, 1.5)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                if pix.width * pix.height >= MIN_PIXELS:
                    fname = f"page{page_num:03d}_fullpage.png"
                    out = FIG_DIR / fname
                    pix.save(str(out))
                    render_path = f"assets/figures/{fname}"
                    if render_path not in page_files:
                        page_files.append(render_path)
                    if best is None:
                        best_path = render_path
            except Exception as e:
                print(f"warn render page {page_num}: {e}", file=sys.stderr)

        # Prefer primary chart alias for the largest image on the page
        primary = best_path or (page_files[0] if page_files else None)
        if primary:
            # symlink-like stable name for convenience
            alias = FIG_DIR / f"page{page_num:03d}.png"
            src = ROOT / primary
            if src.exists() and not alias.exists():
                try:
                    alias.write_bytes(src.read_bytes())
                except Exception:
                    pass
            primary_rel = f"assets/figures/page{page_num:03d}.png"

        if page_files or primary:
            records.append(
                {
                    "page": page_num,
                    "text_len": text_len,
                    "files": page_files,
                    "primary": primary_rel if primary else None,
                    "n_embedded": len(images),
                }
            )

    return records


def parse_figure_labels_by_page() -> dict[int, list[str]]:
    """Map PDF page → figure labels using EN full_book page comments + nearby Figure lines."""
    if not EN_FULL.exists():
        return {}
    text = EN_FULL.read_text(encoding="utf-8", errors="replace")
    # Split by page markers
    parts = re.split(r"(<!-- PDF page (\d+)(?:[^>]*)-->)", text)
    # parts[0] preamble; then (fullmark, pagenum, body)*
    by_page: dict[int, list[str]] = defaultdict(list)
    i = 1
    while i + 2 <= len(parts):
        # pattern: delimiter, page_num, body — but split with two groups gives:
        # [pre, full, num, body, full, num, body, ...]
        full = parts[i]
        if not full.startswith("<!-- PDF page"):
            i += 1
            continue
        # After split with two groups: parts[i]=full marker, parts[i+1]=num, parts[i+2]=body
        if i + 2 >= len(parts):
            break
        num_s = parts[i + 1]
        body = parts[i + 2] if i + 2 < len(parts) else ""
        try:
            page = int(num_s)
        except ValueError:
            i += 1
            continue
        labels = re.findall(
            r"(?:Figure|FIGURE|Fig\.?)\s*([0-9]+(?:\.[0-9]+)?|P[IVX]+\.[0-9]+|I\.[0-9]+)",
            body,
            flags=re.I,
        )
        # normalize
        for lab in labels:
            lab_n = lab.upper() if lab[0].upper() == "P" or lab[0].upper() == "I" else lab
            if lab_n not in by_page[page]:
                by_page[page].append(lab_n)
        i += 3
    return dict(by_page)


def build_figure_to_page(labels_by_page: dict[int, list[str]], page_records: list[dict]) -> dict[str, int]:
    """Pick best PDF page for each figure label (prefer page that has an image)."""
    pages_with_img = {r["page"] for r in page_records if r.get("primary")}
    fig_pages: dict[str, list[int]] = defaultdict(list)
    for page, labs in labels_by_page.items():
        for lab in labs:
            fig_pages[lab].append(page)

    chosen: dict[str, int] = {}
    for lab, pages in fig_pages.items():
        # Prefer pages that have extracted images; else first mention page
        with_img = [p for p in pages if p in pages_with_img]
        # Also try page-1 (caption sometimes on next page)
        candidates = with_img or pages
        # Prefer earliest page among candidates that has image; if caption on p and image on p-1:
        extended = list(candidates)
        for p in pages:
            if (p - 1) in pages_with_img and (p - 1) not in extended:
                extended.append(p - 1)
            if (p + 1) in pages_with_img and (p + 1) not in extended:
                extended.append(p + 1)
        with_img2 = [p for p in extended if p in pages_with_img]
        chosen[lab] = sorted(with_img2 or candidates)[0]
    return chosen


def copy_figure_aliases(fig_to_page: dict[str, int], page_records: list[dict]) -> dict[str, str]:
    """Create stable assets/figures/fig_{label}.png copies for each figure label."""
    page_primary = {r["page"]: r.get("primary") for r in page_records}
    fig_files: dict[str, str] = {}
    for lab, page in sorted(fig_to_page.items(), key=lambda x: x[0]):
        primary = page_primary.get(page)
        if not primary:
            continue
        src = ROOT / primary
        if not src.exists():
            continue
        safe = lab.replace(".", "_")
        fname = f"fig_{safe}.png"
        dest = FIG_DIR / fname
        if not dest.exists():
            dest.write_bytes(src.read_bytes())
        fig_files[lab] = f"assets/figures/{fname}"
    return fig_files


def main() -> int:
    if not PDF_PATH.exists():
        print(f"PDF not found: {PDF_PATH}", file=sys.stderr)
        return 1
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(PDF_PATH)
    print(f"Extracting images from {doc.page_count} pages…")
    records = extract_page_images(doc)
    labels_by_page = parse_figure_labels_by_page()
    fig_to_page = build_figure_to_page(labels_by_page, records)
    fig_files = copy_figure_aliases(fig_to_page, page_records=records)

    manifest = {
        "pdf": str(PDF_PATH),
        "pages_with_images": len(records),
        "figure_count": len(fig_files),
        "page_records": records,
        "labels_by_page": {str(k): v for k, v in sorted(labels_by_page.items())},
        "figure_to_page": fig_to_page,
        "figure_files": fig_files,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    n_files = len(list(FIG_DIR.glob("*.png")))
    print(f"Wrote {n_files} PNG files under {FIG_DIR}")
    print(f"Pages with images: {len(records)}")
    print(f"Figure labels mapped: {len(fig_files)}")
    print(f"Manifest: {MANIFEST}")
    # sample
    for lab in list(fig_files.keys())[:8]:
        print(f"  Figure {lab} -> page {fig_to_page[lab]} -> {fig_files[lab]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
