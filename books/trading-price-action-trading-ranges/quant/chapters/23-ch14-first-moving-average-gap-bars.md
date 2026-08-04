# 第 14 章：首次均线缺口 Bar

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/23-ch14-first-moving-average-gap-bars.md`
- PDF 页码：277–280
- 图表：Figure 14.1–14.2；正文与图注足以定义规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 定义

默认使用20-period EMA。方向标准化后：

```text
bull_MA_gap_bar = high[t] < EMA[t]   # bar完全在EMA下方，期待向上填补
bear_MA_gap_bar = low[t] > EMA[t]    # bar完全在EMA上方，期待向下填补
gap_size_bull = EMA[t] - high[t]
gap_size_bear = low[t] - EMA[t]
```

- “首次”指当前已确认强趋势中第一根位于EMA错误一侧的完整bar；新regime确认后重置。
- 普通图表多数bar都不触EMA，因此“gap bar”不是独立优势，必须结合regime、空间和信号次数。
- 第一/第二次attempt按同一gap方向的实际触发序列计数，而非仅按视觉swing计数。

## 2. 规则卡

### RANGES-C14-S01：强趋势首次 MA Gap Bar 回测旧极值

- 类型：完整顺势swing策略。
- 依据，PDF p.277–278、280：强趋势的首根错误侧MA gap bar通常仍引出旧趋势极值测试；可能创新极值，也可能形成higher/lower extreme。
- Bull版：强bull regime中首次`high < EMA`，随后bar上破gap bar或合格signal bar高点；bear版镜像。
- 强趋势门槛：trend score达标，且此前至少一个spike/tight channel或连续 `10+bars` 结构性higher highs/lows。
- 入场：signal bar顺旧趋势极值外1tick stop；不在gap bar形成前预判。
- 止损：完整pullback极值外；允许研究scale-in，但必须单独建模并统一总风险。
- 目标：旧趋势极值附近、1R/2R；旧极值可exact、undershoot或overshoot。
- 测试旧极值后切换S03监控，不因创新一点就继续无条件持有。

### RANGES-C14-S02：第二次 Fill-Gap Attempt

- 类型：第二入场策略。
- 依据，PDF p.277、279：首次向EMA填gap尝试可能在1–2bars内失败并继续回调；第二次attempt的可交易反弹/回落概率更高。
- Bull版：bull/range regime中存在EMA下方gap；第一次上破prior bar高点后未触EMA，随后再创新低/继续pullback，第二次上破prior/signal bar高点。
- 入场：第二次signal高点上1tick；bear版镜像。
- 止损：第二次attempt最终极值外。
- 目标：EMA触线；强趋势版本可延伸至旧极值，range版本只按scalp处理。
- 第一次attempt可以是一根bull trend bar，无需完美High 1形状；所有计数只用完成bar。

### RANGES-C14-S03：旧极值测试后的两腿修正 / Major Reversal 监控

- 类型：状态转换组件。
- 依据，PDF p.277–278：首次gap pullback常强到突破trend line；旧极值测试完成后，通常出现至少两腿更长修正，甚至主要反转。
- 若首次MA gap pullback突破major/minor trend line，并随后测试旧极值，标记`post_extreme_test=true`。
- 此后降低旧趋势追价评分 `0.15–0.30`，等待两腿修正、double top/bottom或major reversal第二信号。
- 不在旧极值一到达即逆势；需结构失败、反向breakout及follow-through或第二入场确认。
- 旧趋势重新形成strong spike+tight channel时取消反转候选，并建立新regime事件。

### RANGES-C14-S04：非强趋势 Gap Bar 到 EMA 的 Scalp

- 类型：条件scalp策略。
- 依据，PDF p.278–279：非强趋势中fade gap bar通常只取EMA利润，且必须有足够空间并符合上下文。
- Regime限于trading range或弱趋势；bull版在EMA下方gap bar出现合格bull reversal/第二信号，bear版镜像。
- 入场：signal bar朝EMA方向极值外1tick。
- 止损：signal swing外。
- 目标：EMA前1tick或触EMA；只有`distance_to_EMA >= cost + 1.0R`才允许入场。
- 若signal bar本身太高导致成交位距EMA不足，跳过而非压缩止损制造虚假R倍数。

### RANGES-C14-S05：两次同向失败后的反向 Trend Flip

- 类型：失败尝试状态转换。
- 依据，PDF p.279：第二个MA-gap short setup被向上突破，代表两次下行尝试失败，可确认bull trend；反向同理。
- 维护最近两次同方向fill-gap attempts；第二次触发后在 `1–3bars` 内反向突破其signal极值且有follow-through，确认failure pair。
- 反向入场：失败signal另一端突破或首次pullback；止损放在failure pair最终极值外。
- 目标：range另一侧、失败结构高度measured move、1R/2R。
- Trend flip只从确认bar生效，不回填此前bars。

### RANGES-C14-N01：没有足够 EMA 空间则跳过

- 类型：`NEGATIVE`。
- 依据，PDF p.278–279：gap虽存在，但若到EMA空间不足以支付scalp风险与成本，交易没有意义。
- 最低净空间：`distance_to_EMA - fees - slippage >= max(1.0R, min_scalp_ticks)`。
- 空间在预计成交价计算，不用signal bar极值美化。
- 若强反转刚发生且第二腿很可能延续，即使空间足够也由N02否决。

### RANGES-C14-N02：强反转后不 Fade Gap

- 类型：`NEGATIVE`。
- 依据，PDF p.279：bar 5虽是gap bar，但此前强反转、higher low和第二腿预期使逆势scalp不合理。
- 若最近 `2–5bars` 形成反向spike≥`1.5ATR`，随后higher low/lower high确认，则禁用逆该新方向的S04。
- 等待第二腿完成、range形成或新方向失败，再重新计算regime。
- Flat EMA只能作为range证据之一，不能覆盖刚发生的强价格反转。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 277–278 | gap定义、第二次attempt、强趋势首gap测试极值、后续修正 | 定义、S01–S03 |
| 278–279 | 强趋势做swing、普通环境做scalp、空间与上下文 | S04、N01–N02 |
| 279–280 | 多个第二信号、两次失败后的trend flip、首gap案例 | S02、S05 |

## 4. 回测验收

- EMA和gap仅按当根数据计算，严格使用high/low；不得用未来EMA值。
- Trend regime与“首次”状态实时保存；每次reset必须有可审计原因。
- S01按old extreme的undershoot/exact/overshoot及到达时间分别统计。
- S02第一次必须实际触发；未触发的视觉尝试不能冒充first entry failure。
- S04报告原始gap、预计成交后净空间、成交成本和未成交率。
- S03只在旧极值测试后启用，反转入场仍需独立确认，避免机械抄顶底。
- Scale-in版本与单次stop entry隔离，最大总风险保持一致。
- Figure 14.1–14.2只作章节例证，不作参数拟合或绩效证据。
