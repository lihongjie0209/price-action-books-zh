# Assigned batch status — REVERSALS EN→zh

Date: 2026-07-23

## Done

### Direct full chapters → `zh/chapters/`
| File | EN chars | Status |
|------|----------|--------|
| `02-list-of-terms-used-in-this-book.md` | 37,279 | ✅ format `**English** — 中文` |
| `27-ch18-patterns-related-to-yesterday-breakouts-breakout-pullbacks-and-failed-breakouts.md` | 24,071 | ✅ |
| `31-ch21-detailed-day-trading-examples.md` | 14,958 | ✅ |
| `32-ch22-daily-weekly-and-monthly-charts.md` | 23,686 | ✅ |

### Chunks → `zh/chunks/` then merge
| Stem | Parts | Chunks | Merged chapter |
|------|-------|--------|----------------|
| `16-ch09-failures` | 01–04 | ✅ | run `python3 notes/do_merge_now.py` |
| `23-ch15-always-in` | 01–05 | ✅ | run merge script |
| `24-ch16-extreme-scalping` | 01–04 | ✅ | run merge script |
| `28-ch19-opening-patterns-and-reversals` | 01–03 | ✅ | ✅ `zh/chapters/` |
| `35-ch25-trading-guidelines` | 01–03 | ✅ | ✅ `zh/chapters/` |

## Merge command

```bash
cd /root/book/price-action-books-zh/books/trading-price-action-reversals
python3 notes/do_merge_now.py
# writes size report to notes/merge_size_report.txt
```

## Terms used
- bar → K线
- trading range → 震荡区间
- breakout → 突破
- pullback → 回撤
- reversal → 反转
- always-in → 始终持仓
- MTR / major trend reversal → 主要趋势反转
- final flag → 最后旗形

## Notes
- Terms list mirrors trading-ranges glossary style with page markers 11–25.
- Figure captions: Figure → 图.
- PDF page comments preserved.
