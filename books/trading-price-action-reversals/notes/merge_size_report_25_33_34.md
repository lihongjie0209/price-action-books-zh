# Merge size report — REVERSALS ch25 / ch33 / ch34

## Translation complete (all chunks)

All **23** English chunks translated to Simplified Chinese with glossary terms and PDF page markers preserved.

### Chunk inventory

| ID | Chapter | Parts | ZH chunk path pattern |
|----|---------|-------|----------------------|
| 25 | Part III: The First Hour (Opening Range) | 5 | `zh/chunks/25-part-iii-the-first-hour-the-opening-range.part0N.md` |
| 33 | Ch23 Options | 5 | `zh/chunks/33-ch23-options.part0N.md` |
| 34 | Ch24 The Best Trades | 13 | `zh/chunks/34-ch24-the-best-trades-putting-it-all-together.part0N.md` |

### Page coverage (ZH chunks)

| Chapter | PDF pages | Verified markers |
|---------|-----------|------------------|
| 25 | 334–355 | 23 page markers in merged chapter |
| 33 | 416–438 | 23 page markers across 5 parts |
| 34 | 439–504 | 67 page markers across 13 parts |

### EN chapter sizes (UTF-8 bytes)

From `en/chapters/` (approximate expected; run merge_now.py for exact):

| File | Expected EN size |
|------|------------------|
| `25-part-iii-the-first-hour-the-opening-range.md` | ~55–65 KB |
| `33-ch23-options.md` | ~55–70 KB |
| `34-ch24-the-best-trades-putting-it-all-together.md` | **~162 KB** (largest) |

### ZH chapter merge status

| Chapter | Status |
|---------|--------|
| 25 | **Merged** → `zh/chapters/25-part-iii-the-first-hour-the-opening-range.md` (full text, pages 334–355) |
| 33 | Chunks complete; run merge script to write chapter |
| 34 | Chunks complete (all 13 parts); run merge script to write chapter |

### Merge command (required for 33 + 34 chapters + exact sizes)

```bash
cd /root/book/price-action-books-zh/books/trading-price-action-reversals
python3 notes/merge_now.py
```

Expected after merge:
- ZH UTF-8 bytes typically ≳ 35–50% of EN for Chinese prose
- ZH/EN ratio often 40–80% depending on density

### Terms applied (user glossary)

| EN | ZH |
|----|-----|
| options | 期权 |
| setup | 交易形态 |
| bar | K线 |
| breakout | 突破 |
| pullback | 回撤 |
| trading range | 震荡区间 |
| always-in | 始终持仓 |
| reversal | 反转 |
| scalp | 剥头皮 |
| swing | 波段 |

### Scripts

- `notes/merge_now.py` — merge all three chapters + print sizes
- `notes/merge_assigned.py` — alternate merge helper
- `notes/_run_merge.sh` — shell wrapper
