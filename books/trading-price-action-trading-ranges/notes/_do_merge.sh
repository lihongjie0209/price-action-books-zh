#!/bin/bash
set -e
cd /root/book/price-action-books-zh/books/trading-price-action-trading-ranges
python3 notes/merge_assigned_chapters.py
echo "---"
# Also report chunk totals
for base in \
  19-part-iii-pullbacks-trends-converting-to-trading-ranges \
  21-ch12-double-top-bear-flags-and-double-bottom-bull-flags \
  26-ch17-bar-counting-high-and-low-1-2-3-and-4-patterns-and-abc-corrections
do
  echo "CHUNKS $base:"
  wc -c zh/chunks/${base}.part*.md | tail -1
  if [ -f zh/chapters/${base}.md ]; then
    wc -c zh/chapters/${base}.md
    wc -c en/chapters/${base}.md
  fi
done
