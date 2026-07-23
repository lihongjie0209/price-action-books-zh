# Merge assigned Part I chapters

Run:

```bash
cd /root/book/price-action-books-zh/books/trading-price-action-reversals
python3 notes/do_merge_inline.py
# or
python3 notes/merge_part_i_assigned.py
```

This concatenates `zh/chunks/*.partNN.md` → `zh/chapters/*.md` and writes
`notes/merge_size_report_part_i_assigned.md`.
