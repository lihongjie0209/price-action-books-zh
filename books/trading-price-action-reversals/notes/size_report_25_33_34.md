# Size report — REVERSALS largest chapters (25 / 33 / 34)

Generated after full EN→ZH chunk translation.

## Status

| Chapter | EN chunks | ZH chunks | ZH chapter merged | Page markers |
|---------|-----------|-----------|-------------------|--------------|
| 25 Part III Opening Range | part01–05 | part01–05 ✅ | ✅ full | PDF 334–355 ✅ |
| 33 Ch23 Options | part01–05 | part01–05 ✅ | ⏳ run `python3 notes/merge_now.py` | PDF 416–438 ✅ in chunks |
| 34 Ch24 Best Trades | part01–13 | part01–13 ✅ | ⏳ run `python3 notes/merge_now.py` | PDF 439–504 ✅ in chunks |

## Merge command

```bash
cd /root/book/price-action-books-zh/books/trading-price-action-reversals
python3 notes/merge_now.py
```

This merges all three chapters and prints ZH/EN byte sizes + ratios.

## EN chapter sizes (from inventory / full_book extract)

| Chapter | Approx EN | Notes |
|---------|-----------|-------|
| 25-part-iii-the-first-hour-the-opening-range | ~55–65 KB | 5 parts, pages 334–355 |
| 33-ch23-options | ~55–70 KB | 5 parts, pages 416–438 |
| 34-ch24-the-best-trades-putting-it-all-together | ~160–165 KB | 13 parts, pages 439–504 (largest) |

## Terminology applied

- options → 期权
- setup → 交易形态
- bar → K线
- breakout → 突破
- pullback → 回撤
- trading range → 震荡区间
- always-in → 始终持仓
- reversal → 反转
- scalp → 剥头皮
- swing → 波段

## Completeness checks

- [x] All 5+5+13 = 23 zh chunks written
- [x] Page markers preserved (`<!-- PDF page N -->`)
- [x] Figure captions translated (图 PIII.x / 图 23.x / 图 24.x)
- [x] Ch25 fully merged to zh/chapters/
- [ ] Ch33/34 chapter files: placeholders until `merge_now.py` runs (chunks complete)

## Output paths

- `/root/book/price-action-books-zh/books/trading-price-action-reversals/zh/chunks/25-*.part*.md`
- `/root/book/price-action-books-zh/books/trading-price-action-reversals/zh/chunks/33-*.part*.md`
- `/root/book/price-action-books-zh/books/trading-price-action-reversals/zh/chunks/34-*.part*.md`
- `/root/book/price-action-books-zh/books/trading-price-action-reversals/zh/chapters/25-part-iii-the-first-hour-the-opening-range.md` (merged)
- `/root/book/price-action-books-zh/books/trading-price-action-reversals/notes/merge_now.py` (merge + size report)
