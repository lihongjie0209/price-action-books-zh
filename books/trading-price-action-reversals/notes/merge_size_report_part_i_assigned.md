# Merge size report — REVERSALS Part I assigned chapters

Translated EN→ZH: all assigned chunks → `zh/chunks` → merged `zh/chapters`.

## ZH chapters (merged, full Chinese)

| Chapter file | EN chars (inventory) | ZH lines (approx) | PDF pages | Status |
|--------------|---------------------:|------------------:|-----------|--------|
| `07-part-i-trend-reversals-a-trend-becoming-an-opposite-trend.md` | 107,477 | ~317 | 63–101 | ✅ full |
| `10-ch03-major-trend-reversal.md` | 65,758 | ~226 | 112–138 | ✅ full |
| `11-ch04-climactic-reversals-….md` | 87,165 | ~310 | 139–176 | ✅ full |
| `12-ch05-wedges-and-other-three-push-reversal-patterns.md` | 59,524 | ~204 | 177–201 | ✅ full |
| `14-ch07-final-flags.md` | 55,002 | ~179 | 207–230 | ✅ full |

**EN total (5 chapters): ~374,926 chars**

## ZH chunks written (32 files)

### 1) `07-part-i-…` — part01–part09
### 2) `10-ch03-major-trend-reversal` — part01–part06
### 3) `11-ch04-climactic-reversals-…` — part01–part07
### 4) `12-ch05-wedges-…` — part01–part05
### 5) `14-ch07-final-flags` — part01–part05

## Terms (applied consistently)

| English | 中文 |
|---------|------|
| reversal | 反转 |
| major trend reversal | 主要趋势反转 |
| climax | 高潮 |
| spike | 尖峰 |
| wedge | 楔形 |
| final flag | 最后旗形 |
| expanding triangle | 扩散三角形 |
| bar | K线 |
| breakout | 突破 |
| trading range | 震荡区间 |
| always-in | 始终持仓 |

## Exact byte recount

```bash
cd /root/book/price-action-books-zh/books/trading-price-action-reversals
python3 notes/do_merge_inline.py
```

Refreshes this report with exact UTF-8 bytes, CJK counts, and zh/en ratios.
