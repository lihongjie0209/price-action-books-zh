# 第 14 章：Globex, Premarket, Postmarket, and Overnight Market

## 元数据

- 英文来源：`books/trading-price-action-reversals/en/chapters/22-ch14-globex-premarket-postmarket-and-overnight-market.md`
- PDF 页码：292–296
- 图表：Figure 14.1–14.4；正文与图注已完整说明规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Session Context

```text
session ∈ {regular, globex/overnight, premarket, postmarket}
liquidity_state = spread + depth + trades_per_second + expected_slippage
```

- 同一price-action逻辑可跨时段，但bar速度、成交深度、gap、slippage和setup频率不同，必须分别校准。
- Regular-session策略可只用RTH数据；overnight extreme可作可选magnet，不是必需输入。
- 所有时段由交易所point-in-time calendar和DST处理。

## 2. 规则卡

### REVERSALS-C14-S01：Session-Specific Strategy Partition

- 类型：数据与策略隔离。
- 依据，PDF p.292、296：Globex与day session都可交易，但会呈现不同setup；RTH自身price action足以产生信号。
- 每笔标记session；trend lines、EMA、prior high/low可选择RTH-only或24h，但版本在回测前冻结。
- 不把overnight pattern事后补作RTH entry理由；两个版本共享clock-time母事件比较。
- 分别报告setup频率、净EV、spread和gap风险。

### REVERSALS-C14-S02：Premarket Extreme Magnet Overlay

- 类型：可选目标位。
- 依据，PDF p.292：premarket highs/lows常在day session被测试，但无需查看也可依RTH signal交易。
- 在RTH open前冻结premarket high/low；距离≤`0.25–1.0 ADR`时作为target/support-resistance score。
- Magnet不得单独入场；仍需RTH price-action setup。
- 比较with/without overlay的样本外增量，若无稳定收益则保持RTH-only。

### REVERSALS-C14-S03：Premarket Low-Frequency Setup Gate

- 类型：盘前准入。
- 依据，PDF p.294：开盘前1–2小时可交易但entry通常不多；报告会制造快速trend/reversal。
- Premarket只开放高分setup：wedge/double、HL/LH、EMA H/L2、breakout pullback、second entry。
- 目标和仓位按当时ATR/depth缩放；不得因机会少降低门槛。
- Report blackout交S05，普通低流动阶段需要成本后EV下界>0。

### REVERSALS-C14-S04：Post-Earnings Liquidity Kill Switch

- 类型：盘后风险控制。
- 依据，PDF p.292–293：earnings后move过快、stop slippage大、pullback/反转大，刚看清时行情常已停止，多数交易者不应scalp。
- Earnings release后默认`30–120min`禁止新人工scalp；只允许预授权自动策略/平仓。
- 重新开放需spread、depth、bar duration与slippage回到历史可接受分位。
- 即使图上H1/line break/final flag清晰，也必须先过执行门槛。

### REVERSALS-C14-S05：Report-Speed Blackout

- 类型：新闻执行门控。
- 依据，PDF p.294–295：就业等报告可使100-tick图一分钟形成30bars，实际几乎只能market order，理论scalp不可可靠执行。
- Event前`1min`至后`1–5min`或首`1–3 time bars`完成前禁止新仓。
- 使用trades/sec、median bar duration、spread和market impact动态延长blackout。
- 重开后等orderly breakout/pullback/second entry，不回测理想tick-bar signals。

### REVERSALS-C14-S06：Premarket Failed-Breakout Stop-Flush

- 类型：事件后失败策略。
- 依据，PDF p.294：报告导致upside false breakout+outside down，可在原long stops处short；随后breakout pullback/second entry继续交易。
- Blackout结束后，breakout收回pre-event range且strong opposite bar确认。
- Entry在trapped signal extreme/first pullback；stop在event extreme外，qty按宽risk缩小。
- Target range opposite edge/1R；无保守成交空间则跳过。

### REVERSALS-C14-S07：Strong-Trend Countertrend Timeframe Gate

- 类型：盘后反转安全规则。
- 依据，PDF p.293：强trend只有先有trend-line break才fade，countertrend需要5m而非1/3m reversal bar。
- Old trend strong时要求5m significant line break+reversal/final-flag setup。
- 低周期只允许顺势entry，不能批准countertrend。
- 无5m confirmation则继续顺势或不交易。

### REVERSALS-C14-S08：RTH-Only Equivalent Setup

- 类型：信息最小化方案。
- 依据，PDF p.296：即使Globex有expanding triangle，RTH trader可凭昨日高点突破、EMA pullback、LH/double-top flag独立short。
- 为每个overnight-informed trade寻找同时刻RTH-only setup；没有则标记overlay-dependent。
- 主生产策略优先可由RTH独立复现的entry，以降低数据/认知复杂度。
- 比较两者净EV、miss rate及不同feed可靠性。

### REVERSALS-C14-N01：盘后 Earnings Move 默认不 Scalp

- 类型：`NEGATIVE`硬约束。
- 依据，PDF p.292–293：表面profit potential无法弥补速度、slippage和反转执行难度。
- S04 kill switch期间新scalp数量必须为零。
- 不用事后清晰chart作为实时可执行证明。

### REVERSALS-C14-N02：Fast Tick-Chart 理论信号不算可交易收益

- 类型：`NEGATIVE`回测约束。
- 依据，PDF p.295：一分种30bars虽有标准patterns，但人工无法及时下单，market orders成本巨大。
- Bar close间隔低于系统延迟/人工反应预算时，signal标记`unexecutable`。
- 主绩效排除虚假成交但报告机会数；自动版本需tick/L2 latency simulation。

### REVERSALS-C14-N03：Overnight Pattern 不是 RTH 必需条件

- 类型：`NEGATIVE`特征约束。
- 依据，PDF p.292、296：day-session price action本身足够，Globex与RTH可有不同解释。
- RTH策略不得因overnight feed缺失而无法运行，除非明确声明overlay-dependent。
- 禁止事后在24h图寻找额外形态提高置信度。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 292 | 全时段price action、premarket magnets、RTH/Globex选择与earnings后执行困难 | S01–S04、N01、N03 |
| 293 | Figure 14.1：盘后setup存在但难执行、强trend countertrend需5m line break | S04、S07、N01 |
| 294 | Figure 14.2：盘前低频setup、报告false breakout、breakout pullback/second entry | S03、S05–S06 |
| 295 | Figure 14.3：极速tick bars理论可交易但现实不可执行 | S05、N02 |
| 296 | Figure 14.4：Globex/RTH不同setup且RTH信息充分 | S01、S08、N03 |

## 4. 回测验收

- Session boundaries、DST、early close、earnings/event times全部point-in-time。
- RTH-only、24h与overnight-overlay版本使用同一clock-time母样本比较。
- Fast bars按真实latency、queue、spread与market impact标记可执行性；禁止零延迟成交。
- 报告各session的setup数、fill、slippage、MAE/MFE、净EV和最大gap loss。
- Earnings/report kill switches、5m countertrend gate及overnight非必需性设自动测试。
- Blackout、liquidity阈值、premarket magnet距离做walk-forward、跨品种敏感性测试。
- Figure 14.1–14.4仅作章节例证，不作参数或绩效证据。
