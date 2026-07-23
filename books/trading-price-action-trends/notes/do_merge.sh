#!/bin/bash
cd /root/book/trading-price-action-trends-zh
python3 notes/merge_chapters.py
ls -la zh/chapters/04-introduction.md zh/chapters/05-part-i-price-action.md zh/chapters/11-ch06-signal-bars-other-types.md zh/chapters/25-ch18-example-of-how-to-trade-a-trend.md zh/chapters/30-ch22-trending-trading-range-days.md zh/chapters/31-ch23-trend-from-the-open-and-small-pullback-trends.md 2>/dev/null
wc -c zh/chapters/04-introduction.md zh/chapters/05-part-i-price-action.md zh/chapters/11-ch06-signal-bars-other-types.md zh/chapters/21-ch15-channels.md zh/chapters/24-part-iii-trends.md zh/chapters/25-ch18-example-of-how-to-trade-a-trend.md zh/chapters/29-ch21-spike-and-channel-trend.md zh/chapters/30-ch22-trending-trading-range-days.md zh/chapters/31-ch23-trend-from-the-open-and-small-pullback-trends.md 2>/dev/null
