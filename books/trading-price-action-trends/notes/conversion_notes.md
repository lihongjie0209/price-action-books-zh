# Conversion notes

## Tools
- **PyMuPDF (fitz)** version: ('1.28.0', '1.29.0', None)
- **Python**: 3.12.3
- **Source PDF**: `/root/book/Trading Price Action TRENDS.pdf`
- **Pages**: 479
- **Total extractable characters**: 961900
- **Empty / figure-only pages** (27): [1, 2, 8, 12, 14, 30, 32, 86, 90, 108, 186, 200, 208, 216, 222, 226, 240, 300, 306, 320, 350, 354, 414, 446, 454, 470, 472]

## Method
1. Open PDF with PyMuPDF `get_text()` per page.
2. Normalize hyphenation and whitespace; emit page markers as HTML comments.
3. Split into units using PDF embedded outline (`get_toc`), not arbitrary page chunks.
4. `pandoc` is available as an optional helper binary under `scripts/pandoc` (amd64);
   primary PDF extraction uses PyMuPDF because pandoc alone is weak on PDF.

## Limits
- ~27 pages have no extractable text (charts/figures without OCR layer).
- Figure captions and surrounding prose are kept where present in the text layer.
- Running headers / page numbers may remain as residual noise in places.
- Hyphenation fix is heuristic; rare mid-word splits may remain.

## Outputs
- Full book: `en/full_book.md`
- Per-unit chapters: `en/chapters/*.md`
- Inventory: `notes/chapter_inventory.md`
