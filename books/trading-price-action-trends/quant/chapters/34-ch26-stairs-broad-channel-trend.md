# 第 26 章：阶梯——宽通道趋势

## 元数据

- 英文来源：`books/trading-price-action-trends/en/chapters/34-ch26-stairs-broad-channel-trend.md`
- PDF 页码：463–468
- 图表：Figure 26.1–26.3；正文与图注已完整说明，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Stairs 检测

```text
breakout_extension[i] = abs(swing_extreme[i] - prior_swing_extreme[i])
pullback_overlap[i] = pullback crosses back beyond prior breakout point
swing_trend = monotonic confirmed swing highs and lows
```

- `STAIRS`：至少3个同向trending swings/ranges，位于宽、缓斜channel内；大多数新极值突破后，pullback重新穿过breakout point，但未持续破坏前一主swing。
- `SHRINKING_STAIRS`：至少连续3次breakout extension递减，允许 `0–0.15ATR` 噪声容差。
- `ACCELERATING_STAIRS`：某次extension≥此前中位数 `1.5–2.5倍`，并顺趋势突破channel line。
- pivot确认窗口 `2–5bars`，channel使用当时已确认swings的robust/best-fit line；所有参数为`PROXY`。

## 2. 规则卡

### TRENDS-C26-S01：Stairs/Broad Channel 状态分类

- 类型：市场状态组件。
- 依据，PDF p.463–466：stairs是至少三个range的trending trading range变体；具有宽摆动、trending highs/lows，以及突破后回穿breakout point的重叠。
- 最少3个已确认同向swings，最近 `2/3` pullbacks满足overlap，channel width≥ `1.5ATR`。
- 与tight channel区分：中位pullback深度≥前推进的0.35，且双方至少各有2根有效trend bars。
- 输出方向、swing序号、breakout point、extension、pullback depth及strict/loose标签。
- 若不足三层，只标`BROAD_CHANNEL_CANDIDATE`，不得回填早期stairs交易。

### TRENDS-C26-S02：宽 Stairs 的顺势 Swing

- 类型：完整顺势策略。
- 依据，PDF p.463–466：双向交易允许双向入场，但顺势交易应持有部分或全部为swing。
- Setup：S01确认；pullback重新进入prior breakout zone并接近trend line/前swing区域。
- 触发：顺势反转bar、High/Low 2、double top/bottom flag或第二信号。
- 入场：signal bar外stop。
- 止损：pullback swing外。
- 目标：旧趋势极值、下一阶extension、1R/2R；至少 `25–50%` 仓位跟踪至新swing。
- pullback轻微越过此前主swing时不自动翻转；需要强反向breakout及跟进。

### TRENDS-C26-S03：Stairs 边缘逆势 Scalp

- 类型：边缘双向策略。
- 依据，PDF p.463–466、468：宽摆动使逆势交易可盈利；可在trend-channel line、新breakout延伸或强trend bar突破处fade，但stop entry更安全。
- Setup：S01确认且非ACCELERATING；价格到channel外缘或extension达到历史尺度。
- 标准入场：反转bar外stop；高级limit版在新极值延伸距离达到此前 `0.7–1.2×median extension` 时分批挂单。
- 止损：channel极值外；limit最多2–3腿且总账户风险固定。
- 目标：prior breakout point、channel中线、此前pullback长度的 `0.7–1.2×`。
- 按scalp管理，不假设趋势反转；无足够空间达到 `0.5–1R` 时跳过。

### TRENDS-C26-S04：Shrinking Stairs 的两腿修正

- 类型：动能衰减反转策略。
- 依据，PDF p.463–464、466、468：连续breakout变小表示动能减弱，常导致trend-line break和两腿较大修正；许多三推反转也是失败的stairs。
- Setup：至少3个同向extension满足 `e1>e2>e3`，或线性回归斜率显著为负；同时靠近channel line。
- 第一逆向break只建立候选。
- 触发：breakout pullback形成lower high/higher low，或第二反转信号。
- 入场：反向signal bar外stop。
- 止损：最后stair极值外。
- 目标：trend line、channel对侧、两腿、channel起点、1R/2R。
- 失效：顺趋势重新加速并突破channel，转S05。

### TRENDS-C26-S05：Stairs 加速突破的成功与失败

- 类型：双分支突破策略。
- 依据，PDF p.464、467：某一stair可突然顺势突破channel；失败则通常至少两腿反转，成功则通常再有两腿或约channel height的测量移动。
- Event：S01后顺趋势收盘越过channel line `0.10–0.50ATR`，extension≥此前中位数1.5倍。
- 成功：`1–3bars` 同向跟进或breakout pullback守住channel；顺势stop入场。
- 成功止损/目标：回测极值外；目标2个推进或 `0.75/1/1.25×channel height`。
- 失败：`1–5bars` 返回channel且形成反向bar；保守版等待lower high/higher low。
- 失败止损/目标：最终overshoot外；目标两腿、channel中线/对侧。
- channel height在breakout bar冻结，不事后扩大。

### TRENDS-C26-S06：跨 Session Flag Breakout

- 类型：跨日延续/反转组件。
- 依据，PDF p.464：stairs常是高周期pullback或flag，尤其尾盘形成后可在次日开盘突破；bull stairs也可能是大级别bear flag。
- Setup：session最后 `0.15–0.35` 时段确认stairs；次日保存其完整上下边界和方向，不预判breakout方向。
- 入场：次日边界突破后的follow-through或breakout pullback。
- 止损：回测结构外；隔夜gap越过触发位时不得假设原stop价成交。
- 目标：stairs高度、前一高周期趋势极值、1R/2R。
- 高周期趋势只在已完成bar上计算，当前session stairs方向不能自动等同于次日breakout方向。

### TRENDS-C26-N01：第三推进不保证反转

- 类型：`NEGATIVE`。
- 依据，PDF p.466–468：三推/shrinking stair只是衰减迹象；若缺少强逆向压力，趋势可恢复或加速，失败wedge会产生测量移动。
- 禁止在第三推进出现时无确认立即反转；至少等待trend-line break及S04第二信号。
- 没有大逆向trend bar、climax reversal或强反向跟进时，维持原趋势评分。
- 如果反转signal没有触发，不得在回测中记为成交；failed wedge转S05顺势分支。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 463–464 | stairs定义、宽摆动、突破回穿及shrinking stairs | 第1节、S01–S04 |
| 464 | 跨日flag、加速突破成功/失败与测量移动 | S05、S06 |
| 464–466 | 按历史extension/pullback尺度双向交易 | S02、S03 |
| 466 | 三推无反向压力不保证反转 | N01 |
| 467–468 | 加速stairs与shrinking stairs案例 | S04、S05、N01 |

## 4. 回测验收

- pivot和第三stair只在确认bar后生效；不得在第一stair时回填完整形态。
- S01报告strict/loose overlap定义、channel width及至少3/4/5层的敏感性。
- S02/S03使用同一事件样本比较顺势swing与逆势scalp，并计入limit未成交。
- S04同时测试严格单调递减和回归斜率版本，报告假反转与等待第二信号成本。
- S05建立成功/失败互斥终态，冻结breakout时channel height。
- S06包含隔夜gap和session边界，不使用未完成高周期bar。
- Figure 26.1–26.3仅作章节例证，不作参数拟合或绩效证据。
