#!/usr/bin/env bash
# Merge assigned ZH chunks into chapters + size report
set -euo pipefail
ROOT="/root/book/price-action-books-zh/books/trading-price-action-reversals"
cd "$ROOT"
python3 notes/do_merge_inline.py
cat notes/merge_size_report_part_i_assigned.txt 2>/dev/null || true
ls -la zh/chapters/07-part-i*.md zh/chapters/10-ch03*.md zh/chapters/11-ch04*.md zh/chapters/12-ch05*.md zh/chapters/14-ch07*.md
wc -c zh/chapters/07-part-i*.md zh/chapters/10-ch03*.md zh/chapters/11-ch04*.md zh/chapters/12-ch05*.md zh/chapters/14-ch07*.md en/chapters/07-part-i*.md en/chapters/10-ch03*.md en/chapters/11-ch04*.md en/chapters/12-ch05*.md en/chapters/14-ch07*.md
