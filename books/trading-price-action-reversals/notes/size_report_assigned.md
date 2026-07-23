# Size report — assigned REVERSALS translation batch

Run merge for remaining chunked chapters:

```bash
cd /root/book/price-action-books-zh/books/trading-price-action-reversals
python3 notes/do_merge_now.py
```

## EN source sizes (chars from chapter_inventory)

| File | EN chars |
|------|----------|
| 02-list-of-terms-used-in-this-book.md | 37,279 |
| 16-ch09-failures.md | 47,059 |
| 23-ch15-always-in.md | 55,711 |
| 24-ch16-extreme-scalping.md | 40,475 |
| 27-ch18-patterns-related-to-yesterday-... | 24,071 |
| 28-ch19-opening-patterns-and-reversals.md | 36,575 |
| 31-ch21-detailed-day-trading-examples.md | 14,958 |
| 32-ch22-daily-weekly-and-monthly-charts.md | 23,686 |
| 35-ch25-trading-guidelines.md | 35,232 |

## ZH outputs produced

### Direct chapters (`zh/chapters/`)
- `02-list-of-terms-used-in-this-book.md` — format `**English** — 中文`
- `27-ch18-patterns-related-to-yesterday-breakouts-breakout-pullbacks-and-failed-breakouts.md`
- `31-ch21-detailed-day-trading-examples.md`
- `32-ch22-daily-weekly-and-monthly-charts.md`
- `28-ch19-opening-patterns-and-reversals.md` (merged)
- `35-ch25-trading-guidelines.md` (merged)

### Chunks (`zh/chunks/`)
- `16-ch09-failures.part01.md` … `part04.md`
- `23-ch15-always-in.part01.md` … `part05.md`
- `24-ch16-extreme-scalping.part01.md` … `part04.md`
- `28-ch19-opening-patterns-and-reversals.part01.md` … `part03.md`
- `35-ch25-trading-guidelines.part01.md` … `part03.md`

### Still need merge into `zh/chapters/` via script
- `16-ch09-failures.md`
- `23-ch15-always-in.md`
- `24-ch16-extreme-scalping.md`

(Script also re-merges 28 and 35 which already exist.)

## Terminology locked
bar=K线, trading range=震荡区间, breakout=突破, pullback=回撤, reversal=反转, always-in=始终持仓, MTR=主要趋势反转, final flag=最后旗形
