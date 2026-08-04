# 第 17 章：水平线——摆动点与其他关键价位

## 元数据

- 英文来源：`books/trading-price-action-trends/en/chapters/23-ch17-horizontal-lines-swing-points-and-other-key-price-levels.md`
- PDF 页码：301–306
- 图表：Figure 17.1–17.2；正文及图注已完整说明交易关系，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 水平关键位与市场状态

实时维护以下价位，价位只能在其形成或前一交易日结束后生效：

```text
confirmed_swing_high/low = pivot(k_left, k_right)
prior_day_high/low/close
session_open, opening_range_high/low
range_breakout_level
```

- 摆动点确认参数 `k_left/k_right=2–5bars`（`PROXY`）；确认前不得用于信号。
- 多个价位相距不超过 `0.10–0.30ATR` 时合并为zone，中心取成交量加权价或简单均值，分别测试。
- zone有效半宽为 `1tick–0.20ATR`；突破至少要求极值超过zone，强版本要求收盘越界 `0.05–0.25ATR`。
- 每个候选先分类为`TRADING_RANGE/WEAK_TREND`或`STRONG_TREND`。同一水平位在前者用于失败突破反转，在后者主要用于顺势breakout pullback。

## 2. 规则卡

### TRENDS-C17-S01：区间日摆动高低点失败突破

- 类型：完整反转策略。
- 依据，PDF p.301–303：多数交易日包含大量区间行为；摆动高低点突破常失败，并形成higher-high或lower-low reversal。
- Setup：市场状态不是strong trend；价格首次越过已确认swing high/low或其他预登记水平zone。
- 失败定义：越界后 `1–5bars` 内收盘返回zone内，且无连续2bars同向跟进。
- 入场：返回zone后的反转bar外stop；上破失败做空，下破失败做多。
- 止损：失败突破极值外 `1tick–0.25ATR`。
- 目标：区间中点/开盘价第一目标，对侧最近swing第二目标；至少有 `0.5–1R` 空间才入场。
- 失效：失败信号被反向突破，转S03，不重复按首次失败加仓。

### TRENDS-C17-S02：第二个更极端高点/低点反转

- 类型：区间日优先级反转策略。
- 依据，PDF p.301–303：第二个higher high或lower low是第二次反转尝试，距区间中部磁体更远，通常比第一次更可靠。
- Setup：S01第一次反转未达到中部目标，之后价格在 `3–30bars` 内再次越过同一侧水平位，并形成更极端高/低点。
- 极端增量：至少 `1tick`，上限研究 `0.05–1ATR`；近似双顶/底另作子组。
- 触发：第二次越界失败并出现反转bar、micro double top/bottom或第二入场。
- 入场：反转bar外stop。
- 止损：第二极端外。
- 目标：第一次极端、区间中点、1R/2R；默认按scalp管理，不假设新趋势。
- 加分但不强制：第三推进、wedge、expanding triangle、前日高低点或多个水平位重合。

### TRENDS-C17-S03：失败反转的再失败——Breakout Pullback

- 类型：突破延续策略。
- 依据，PDF p.301、304–305：水平突破失败若自身再失败，就是breakout-pullback；市场可能形成第二个更极端高点或低点。
- Setup：已产生S01/S02反转signal，但其入场方向没有跟进，随后价格重新越过原水平位及反转bar极值。
- 入场A：反向突破失败signal bar时stop entry。
- 入场B：突破后 `1–5bars` 回测原水平zone并守住，在顺突破方向的signal bar外入场。
- 止损：回测极值或原水平zone另一侧。
- 目标：前一突破极值、区间高度 `0.75/1.0/1.25×H`、1R/2R。
- 成交互斥：若反转stop和反向breakout stop可在同一bar触发，必须按更保守的bar内路径或次bar成交处理。

### TRENDS-C17-S04：趋势日水平位顺势回测

- 类型：完整顺势策略。
- 依据，PDF p.301、304–305：趋势日的水平线通常只用于回撤入场；强势突破区间后回测突破位，是breakout-pullback机会。
- Setup：strong trend已确认；价格强势突破交易区间、opening range或重要swing水平。
- 强突破代理：breakout bar实体≥ `0.5ATR`、收盘位于bar顺势端25%，并有1–2bars跟进。
- 回测：突破后 `2–20bars` 回到水平zone `±0.20ATR`，但没有强收盘重新进入旧区间。
- 触发：回测处顺势反转bar、High/Low 1/2或失败的逆势突破。
- 入场：signal bar外stop。
- 止损：回测极值外；若结构止损过宽则缩小仓位。
- 目标：趋势旧极值、区间高度测量移动、1R/2R；强趋势保留部分仓位跟踪。
- 失效：回测以强spike重新进入旧区间并跟进，重新分类市场状态。

### TRENDS-C17-S05：强趋势中的逆势水平位过滤

- 类型：反转门控/有限scalp。
- 依据，PDF p.304–305：强趋势中只有先出现良好trend-line break和强反转bar，才考虑fade摆动点；若反向动能很小，这类交易仍弱且只能scalp。
- strong trend中，单独的swing high/low失败突破不构成逆势入场。
- 最低门槛：已确认trend-line break、强反向bar，并出现higher low/lower high或第二信号。
- 若反向spike不足2bars、未穿EMA或首次pullback未守住，只允许研究性scalp：风险≤标准仓位的 `0.25–0.50`，目标 `0.5–1R`。
- 若逆势信号与S04顺势回测冲突，优先S04，并记录被过滤信号；不得因逆势交易错过顺势swing。
- 只有反向spike、跟进和结构确认使Always-In翻转后，才允许按新方向持有swing仓位。

### TRENDS-C17-S06：尾盘逆势陷阱后的顺势新极值

- 类型：时段条件顺势策略。
- 依据，PDF p.305：11:30后常有较强逆势移动，把交易者带离原趋势；随后可靠顺势交易通常创出新极值并可能持续到收盘。
- 时间必须转换为session fraction；初测窗口为 `0.45–0.75`，11:30只作为原书案例，不跨市场硬编码。
- Setup：上午strong trend；时段窗口内出现首个触及/穿越EMA的逆势回撤，并测试已登记水平位。
- 触发：逆势突破失败、MA gap bar失败，或顺势第二入场。
- 入场：顺势signal bar外stop。
- 止损：逆势回撤极值外。
- 目标：当日旧极值、收盘退出、1R/2R三种模型。
- 禁用：趋势已正式翻转、剩余时段不足预期持有期，或事件数据不含可靠session时区。

### TRENDS-C17-N01：同一水平位不能脱离状态机械反向

- 类型：`NEGATIVE`。
- 依据，PDF p.301、304：区间日应寻找水平突破失败，强趋势日则通常只在回测时顺势交易。
- 禁止统一执行“触及阻力即空、触及支撑即多”。
- 禁止使用尚未确认的未来swing点；pivot必须延迟 `k_right` bars生效。
- 禁止把图中事后可见的最佳双顶/双底作为唯一标签；若多个历史底/顶都在容差内，必须全部由固定聚类算法处理。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 301 | 区间日水平突破失败；第二信号；趋势日只用于回测 | S01–S04、N01 |
| 302–303 | 第二higher high/lower low、中部磁体、三推进与复合形态 | S02 |
| 303 | 失败旗形、double top/bottom、breakout pullback | S02、S03 |
| 304 | 强趋势不可轻易fade；trend-line break与反转bar门槛 | S05 |
| 304–305 | 失败后的再失败、opening range、spike and channel | S03、S04 |
| 305–306 | MA gap bar、较晚逆势陷阱及顺势新极值 | S06 |

## 4. 回测验收

- 每条水平线记录`known_at`，pivot延迟、前日价位和opening range不得回填。
- 以相同检测器分别报告range/weak trend与strong trend，验证状态分流而非事后挑选。
- S01、S02和S03使用互斥事件ID，统计首次失败、第二极端和失败后的再失败的完整转移概率。
- 比较单一价位与cluster zone，报告容差 `0.10/0.20/0.30ATR` 的敏感性。
- S04报告回测等待bar数、重新进入旧区间深度及是否创趋势新极值。
- S05同时记录被过滤的逆势信号，以衡量机会成本，而非只展示成功顺势交易。
- S06按session fraction和市场分别验证；不得把11:30直接用于非美股日盘。
- Figure 17.1–17.2仅作章节例证，不作参数拟合或绩效证据。
