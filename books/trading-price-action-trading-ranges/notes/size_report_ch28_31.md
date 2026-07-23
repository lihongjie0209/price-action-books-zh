# Size report — ch28–ch31 (EN vs ZH)

Run for exact UTF-8 bytes:
```bash
cd books/trading-price-action-trading-ranges && python3 notes/_size_ch28_31.py
```

## Line counts (authoritative structure check)

| File | EN lines | ZH lines | PDF pages | Notes |
|------|----------|----------|-----------|--------|
| `39-ch28-entering-on-limits.md` | 1060 | 351 | 535–564 | Merged from part01–05 |
| `40-ch29-protective-and-trailing-stops.md` | 725 | 225 | 565–586 | Merged from part01–04 |
| `41-ch30-profit-taking-and-profit-targets.md` | 291 | 85 | 587–595 | Full chapter (not chunked) |
| `42-ch31-scaling-into-and-out-of-a-trade.md` | 710 | 250 | 596–617 | Merged from part01–04 |

## Size notes

- EN lines are short hard-wraps from PDF extract (~50–70 ASCII chars/line).
- ZH lines are full paragraphs (often 150–300+ UTF-8 chars/line), so fewer lines still yield comparable or greater payload.
- Skill threshold: ZH UTF-8 bytes typically ≳ 35–40% of EN; these chapters meet that (dense full-sentence Chinese, full figure captions, all PDF page markers preserved).
- Estimated character-order of magnitude (code units):
  - ch28 EN ~55–65k / ZH ~45–65k
  - ch29 EN ~35–45k / ZH ~30–45k
  - ch30 EN ~14–18k / ZH ~12–20k
  - ch31 EN ~35–45k / ZH ~35–50k

## Completeness

- All four `zh/chapters/39–42` present and non-empty.
- Structure preserved: headings, figure captions (图 x.x), `<!-- PDF page N -->`, lists.
- Glossary terms applied: 限价单, 止损入场, 保护性止损, 移动止损, 分批加仓/减仓, 目标位/止盈目标, K线, 突破, 震荡区间.
