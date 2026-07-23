# Conversion notes — TRADING RANGES

## Tools
- **PyMuPDF (fitz)** version: ('1.28.0', '1.29.0', None)
- **Python**: 3.12.3
- **Source PDF**: `/root/book/Trading Price Action TRADING RANGES.pdf` (copied via wslpath from Windows Downloads)
- **Pages**: 646
- **Total extractable characters**: 1289022
- **Empty / figure-only pages** (3): [1, 2, 9]

## Method
1. `get_text()` per page; normalize hyphenation/whitespace.
2. Split using PDF outline L1/L2 (`get_toc`); L3 subsections stay inside parent chapter.
3. Outputs: `en/full_book.md`, `en/chapters/*.md`, this file, inventory.

## Limits
- ~3 pages may be figure-only / weak text layer.
- Running headers / page numbers residual noise possible.
