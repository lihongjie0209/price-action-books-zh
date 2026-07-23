# Chapter merge

All Chinese chunk translations for the assigned incomplete work are in `zh/chunks/`.

Run from repo root:

```bash
python3 notes/merge_chapters.py
```

This concatenates ordered `*.partNN.md` files into:

- `zh/chapters/04-introduction.md`
- `zh/chapters/05-part-i-price-action.md`
- `zh/chapters/11-ch06-signal-bars-other-types.md`
- `zh/chapters/21-ch15-channels.md` (also already existed complete)
- `zh/chapters/25-ch18-example-of-how-to-trade-a-trend.md`
- `zh/chapters/29-ch21-spike-and-channel-trend.md` (also already existed complete)
- `zh/chapters/30-ch22-trending-trading-range-days.md`
- `zh/chapters/31-ch23-trend-from-the-open-and-small-pullback-trends.md`

Already complete (no action needed):

- `zh/chapters/24-part-iii-trends.md` (full chapter translate, no chunks)
- `zh/chapters/21-ch15-channels.md`
- `zh/chapters/29-ch21-spike-and-channel-trend.md`
