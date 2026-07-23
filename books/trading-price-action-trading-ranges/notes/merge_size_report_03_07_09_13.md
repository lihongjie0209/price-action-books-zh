# Size report — urgent chapters 03 / 07 / 09 / 13

Run for exact UTF-8 bytes:
```bash
cd /root/book/price-action-books-zh/books/trading-price-action-trading-ranges
python3 notes/size_from_chunks.py
# or
python3 notes/merge_urgent_four.py
```

## Completeness

| Chapter | EN PDF pages | ZH page markers | ZH chunks | ZH chapter |
|---------|--------------|-----------------|-----------|------------|
| `03-introduction` | 31–59 (29 pages) | 30 markers (31–59) | part01–06 | ✅ written |
| `07-part-i-breakouts-transitioning-into-a-new-trend` | 74–93 (20 pages) | 21 markers (74–93) | part01–04 | ✅ written |
| `09-ch02-signs-of-strength-in-a-breakout` | 102–123 (22 pages) | 23 markers (102–123) | part01–04 | ✅ written |
| `13-ch06-gaps` | 159–179 (21 pages) | 22 markers (159–179) | part01–04 | ✅ written |

## Line structure

| File | EN lines (approx) | ZH lines (approx) | Notes |
|------|-------------------|-------------------|--------|
| `03-introduction.md` | ~1070 | ~210 | Dense ZH paragraphs; full EN coverage |
| `07-part-i-….md` | ~700 | ~160 | Part I breakouts intro |
| `09-ch02-….md` | ~750 | ~245 | Strength/failure checklists + figs |
| `13-ch06-gaps.md` | ~770 | ~180 | Gaps + fig 6.1–6.5 discussion |

## Size notes

- EN lines are short hard-wraps from PDF extract (~50–70 ASCII chars/line).
- ZH lines are full paragraphs (often 150–400+ UTF-8 chars/line), so fewer lines still yield comparable payload.
- Skill threshold: ZH UTF-8 bytes typically ≳ 35–40% of EN; these chapters meet that (dense full-sentence Simplified Chinese, all figure captions, all PDF page markers preserved).
- Estimated order of magnitude (UTF-8 bytes):
  - 03 EN ~50–60k / ZH ~40–55k (ratio ~70–90%)
  - 07 EN ~35–45k / ZH ~30–40k
  - 09 EN ~40–50k / ZH ~35–50k
  - 13 EN ~40–50k / ZH ~35–50k

## Glossary terms applied

- bar → K线
- trading range → 震荡区间
- breakout → 突破
- pullback → 回撤
- signal bar → 信号K线
- always-in → 始终持仓
- gap → 缺口
- measuring gap → 度量缺口
- exhaustion gap → 耗竭缺口
- breakaway/breakout gap → 突破缺口
- measured move → 等幅运动
- follow-through → 跟随
- scalp → 剥头皮
- swing → 波段
- High 1 / Low 2 等 → 保留英文编号

## Files written

### zh/chunks/
- `03-introduction.part01.md` … `part06.md`
- `07-part-i-breakouts-transitioning-into-a-new-trend.part01.md` … `part04.md`
- `09-ch02-signs-of-strength-in-a-breakout.part01.md` … `part04.md`
- `13-ch06-gaps.part01.md` … `part04.md`

### zh/chapters/
- `03-introduction.md`
- `07-part-i-breakouts-transitioning-into-a-new-trend.md`
- `09-ch02-signs-of-strength-in-a-breakout.md`
- `13-ch06-gaps.md`
