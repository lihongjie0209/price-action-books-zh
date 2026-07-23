# Merge size report — chapters 19 / 21 / 26

Generated after translating all assigned EN chunks → `zh/chunks` → merged `zh/chapters`.

## Method

Run to refresh exact byte counts:

```bash
cd /root/book/price-action-books-zh/books/trading-price-action-trading-ranges
python3 notes/size_from_chunks.py
# or
python3 notes/merge_assigned_chapters.py
```

## Completeness

| Chapter | EN chunks | ZH chunks | Merged chapter | MERGE markers |
|---------|-----------|-----------|----------------|---------------|
| 19 Part III Pullbacks | part01–05 | part01–05 | `zh/chapters/19-part-iii-pullbacks-trends-converting-to-trading-ranges.md` | none |
| 21 Ch12 Double Top/Bottom Flags | part01–03 | part01–03 | `zh/chapters/21-ch12-double-top-bear-flags-and-double-bottom-bull-flags.md` | none |
| 26 Ch17 Bar Counting | part01–08 | part01–08 | `zh/chapters/26-ch17-bar-counting-high-and-low-1-2-3-and-4-patterns-and-abc-corrections.md` | none |

## Line counts (post-merge, approximate from file structure)

| File | Approx lines | Ends with (OK) |
|------|--------------|----------------|
| zh/chapters/19-…md | ~241 | Fig PIII.3 breakout pullback close (PDF 246) |
| zh/chapters/21-…md | ~202 | Fig 12.7 deeper discussion sell climaxes (PDF 271) |
| zh/chapters/26-…md | ~492 | Fig 17.13 spike and channel two legs (PDF 332) |

## EN source sizes (from chapter_inventory.md)

| Chapter | EN chars (inventory) | PDF pages |
|---------|----------------------|-----------|
| 19 | 58,057 | 222–246 |
| 21 | 35,951 | 256–271 |
| 26 | 94,327 | 290–332 |

## Terms applied

- pullback → 回撤  
- trading range → 震荡区间  
- breakout → 突破  
- bar → K线  
- High 1/2, Low 1/2 (and 3/4) kept English  
- wedge → 楔形  
- double top/bottom → 双顶/双底  
- flag → 旗形  
- always-in → 始终持仓 / Always-In  

## Paths

Chunks:  
`/root/book/price-action-books-zh/books/trading-price-action-trading-ranges/zh/chunks/`

Chapters:  
`/root/book/price-action-books-zh/books/trading-price-action-trading-ranges/zh/chapters/`
