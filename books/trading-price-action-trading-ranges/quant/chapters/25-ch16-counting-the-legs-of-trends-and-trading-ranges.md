# 第 16 章：趋势与交易区间的腿数计数

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/25-ch16-counting-the-legs-of-trends-and-trading-ranges.md`
- PDF 页码：286–289
- 图表：Figure 16.1–16.3；正文与图注足以定义规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 因果 Leg 计数器

方向标准化后，以已确认pivot构建层级腿：

```text
micro_leg: 位移 >= 0.5ATR，反向确认 >= max(2ticks, 0.20ATR)
primary_leg: 位移 >= 1.0ATR，且持续 >= 3bars
leg_2: leg_1结束后发生可区分pullback，再次向同方向推进
```

- Pivot只能在右侧确认bar到来后生效；保存`pivot_time`与`known_time`，禁止回填交易信号。
- 一条primary leg可递归包含两条micro legs；计数必须带尺度，如`primary=1, micro=2`。
- 参数范围建议：反向阈值 `0.15–0.40ATR`，最小腿位移 `0.5–1.5ATR`，最小持续 `2–5bars`。
- “两腿常见”是结构先验而非强制终点；第二腿后仍可继续成为多腿趋势。

## 2. 规则卡

### RANGES-C16-S01：强首反转腿后的 Higher-Low / Lower-High 第二腿

- 类型：主要反转延续策略。
- 依据，PDF p.286–287：长期趋势后若首个反转腿动量强、突破EMA和最后lower/higher swing，双方会预期旧极值测试失败并形成第二腿。
- Bull版Setup：protracted bear trend后反弹≥`1.5ATR`，bull trend bars≥60%，收盘越EMA及最后lower high；bear版镜像。
- 等待pullback测试旧低但保持higher low，出现High 1/2、double bottom或strong reversal bar。
- 入场：signal高点上1tick；止损在higher low/测试极值下。
- 目标：第一反转腿高点、leg1=leg2测量、1R/2R。
- Pullback强势突破旧极值并follow-through则失效；旧趋势可能仍在延续。

### RANGES-C16-S02：任意显著 Move 的第二次反转尝试

- 类型：通用第二入场组件。
- 依据，PDF p.286–287：任何规模的move最终常有两次反转尝试；趋势、逆势move及每条腿都可能细分为两腿。
- 对每个primary move维护同方向反转attempt计数；第一次失败后，第二个独立signal才标记attempt 2。
- 独立条件：两signal之间至少一次恢复原move方向的推进≥`0.25ATR`或间隔≥2bars。
- 交易方向由regime决定：趋势中优先顺势第二入场，range边缘允许fade；不得只凭“第二次”忽略位置。
- 入场/止损沿用对应High/Low 2或double top/bottom策略；该组件输出计数和评分，不重复开仓。

### RANGES-C16-S03：Spike-and-Channel 视为两阶段 Move

- 类型：结构分段与回调预期。
- 依据，PDF p.287–288：所有spike-and-channel按定义是两阶段move——高动量spike加低动量channel。
- Spike：`2–5bars` 位移≥`1.5ATR`、overlap≤0.35；channel：随后至少两次同向pivot推进，斜率/每bar位移低于spike。
- 计数标记`leg1=spike, leg2=channel`，同时允许channel内部保存micro-leg计数。
- Channel第三推、trend-line break或明显失速后，开启两腿修正监控；不在spike刚结束时机械逆势。
- 回调策略需等待breakout、pullback及第二信号；目标为channel起点、EMA、1R/2R。

### RANGES-C16-S04：Perfect / Near-Perfect Breakout Test 的等幅延续

- 类型：突破回测策略。
- 依据，PDF p.288：精确或近乎精确的breakout test常运行breakeven stops，随后约走一个measured move。
- 确认已存在breakout point；回测进入 `max(1–2ticks, 0.05–0.15ATR)` 容差带，可轻微穿越但必须收回。
- 入场：顺breakout方向reversal signal极值外stop。
- 止损：test最终极值外。
- 目标：breakout前一条impulse的点数投影；同时报告1R/2R。
- Breakout point必须在回测前已知，不得从后来最吻合的价位反选。

### RANGES-C16-S05：Failed Low/High 2 的挤压突破

- 类型：失败形态反向策略。
- 依据，PDF p.288：两腿反弹后的Low 2 short高点被突破，会迫使新空回补并形成快速bull spike；failed double top也增加突破燃料。
- Bull版：Low 2 short实际触发，随后未达到 `0.5R`，价格在 `1–5bars` 内突破两腿反弹高点；bear版镜像。
- 入场：失败结构高点上stop或首次breakout pullback。
- 止损：failure pullback最终低点或breakout bar另一侧。
- 目标：失败结构高度measured move、1R/2R；多个失败形态共振只计一笔交易。

### RANGES-C16-S06：Bear/Bull Trend 中 EMA 两腿 Pullback

- 类型：可靠顺势Low/High 2策略。
- 依据，PDF p.288–289：bear trend中两腿反弹到EMA并形成double top/Low 2是可靠short；bull方向镜像。
- Setup：trend regime明确；pullback含两个primary或合格micro pushes，第二推触及/接近EMA并测试第一推极值。
- 入场：Low 2/High 2 signal顺趋势端外1tick。
- 止损：两腿pullback最终极值外。
- 目标：旧趋势极值、range高度/2倍高度（若结构支持）、1R/2R。
- 若EMA已趋平且价格双侧反复穿越，降级为range策略而非趋势入场。

### RANGES-C16-S07：Wedge 后“看似两腿”仍可能只是第一条大腿

- 类型：层级修正等待策略。
- 依据，PDF p.287、289：若两小腿都处于tight channel、bar数相对被修正的大形态不足，它们可能只是高周期第一腿；大型wedge后常还需一条修正腿。
- 计算`correction_duration / prior_pattern_duration`和`correction_size / prior_move_size`。
- 若小于阈值 `duration<0.25–0.50`，且两腿共享tight channel（overlap低、无显著反向pullback），合并为一个primary leg。
- 大wedge后的首次tight-channel修正结束不立即重仓反转；等待反弹后第二条primary correction leg或强趋势恢复确认。
- 第二腿可横向结束并形成double bottom/top，不要求创新修正极值。

### RANGES-C16-N01：不要把每个 Micro Swing 当作完整 Leg

- 类型：`NEGATIVE`。
- 依据，PDF p.287、289：腿会递归细分，低周期两个小推可能只构成高周期一腿；错误计数会过早判断修正完成。
- 每个策略必须声明使用`micro`还是`primary`尺度，禁止在持仓中切换尺度以证明“已经两腿”。
- 小于最小位移/持续阈值的pivot只作噪声，不增加primary count。
- 同时报告固定ATR算法与时间聚合稳健性，不能事后挑选最合意周期。

### RANGES-C16-N02：第二腿不是必然反转

- 类型：`NEGATIVE`。
- 依据，PDF p.286–289：两腿普遍出现，但一方最终仍会胜出，趋势可继续多腿发展。
- `leg_count==2`只允许降低延续评分或开启反转监控，不可单独入场。
- 必须另有位置、signal bar、breakout failure或regime flip。
- 报告第二腿后“延续第三腿 / range / reversal”的条件转移概率，而非只统计成功反转案例。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 286–287 | 强首反转腿、旧极值测试、两腿普遍且递归 | S01–S02、N02 |
| 287–288 | tight channel可能仅一腿、spike-channel、breakout test | S03–S04、S07、N01 |
| 288–289 | failed Low 2挤压、EMA两腿pullback、wedge后的大尺度第二腿 | S05–S07 |

## 4. 回测验收

- 每个pivot同时保存发生时点与确认时点；入场只能使用确认时点。
- Micro/primary两套计数分别输出，且同一策略运行中尺度固定。
- Leg参数在训练集选择后锁定；报告ATR阈值和bar阈值敏感性。
- S01按旧极值测试的higher/equal/lower结果及第二腿到达率建立转移矩阵。
- S03的spike/channel边界只用当时信息；不得按最终图形最佳分段。
- S04测量起点与breakout point须在入场前记录。
- S07比较“合并为一腿”与“计作两腿”的样本外预测能力。
- Figure 16.1–16.3只作章节例证，不作参数拟合或绩效证据。
