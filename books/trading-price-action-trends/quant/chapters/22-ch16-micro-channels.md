# 第 16 章：微通道

## 元数据

- 英文来源：`books/trading-price-action-trends/en/chapters/22-ch16-micro-channels.md`
- PDF 页码：281–300
- 图表：Figure 16.1–16.6；正文及图注已完整说明规则关系，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 微通道与微趋势线定义

对方向 `d∈{bull,bear}`、候选长度 `L=2–10bars`，使用当时可见数据计算：

```text
bull_line(t) = robust_line_through_lows(t-L+1 ... t)
bear_line(t) = robust_line_through_highs(t-L+1 ... t)
line_error   = median(abs(price - line)) / ATR20
violation_rate = mean(extreme crosses line by more than tolerance)
body_score   = mean(directional_body / max(range, tick))
tail_penalty = mean(countertrend_tail / max(range, tick))
```

- `MICRO_TREND_LINE`：至少2根连续bar的同向极值可由短线连接，大多数bar触及或靠近该线。
- `MICRO_CHANNEL`：极紧的短趋势；相邻bar几乎没有逆向回撤，通常每根低点不低于前低（bull）或每根高点不高于前高（bear）。
- 允许 `0–1` 次轻微破坏作为噪声版本，但必须单独报告；严格版本不允许破坏。
- 强度随持续bar数、同向实体占比增加而上升，随逆向尾部、线误差和破坏次数增加而下降。
- `L>=10` 不再简单解释为更安全的延续信号，同时标为潜在climax。

| 参数 | 初始测试范围 | 来源 |
|---|---:|---|
| 候选长度 `L` | 2–10 bars | `AUTHOR` |
| 触线容差 | 0–0.15 ATR | `PROXY` |
| 最大轻微破坏 | 0–1次 | `PROXY` |
| directional body占range | 0.45–0.80 | `PROXY` |
| countertrend tail占range | 0–0.35 | `PROXY` |
| climax长度 | ≥10 bars | `AUTHOR` + `PROXY`边界 |

检测器只描述局部价格结构，不能独立决定方向。每个信号必须另行记录外层状态：`WITH_TREND`、`COUNTERTREND_FLAG`、`TRADING_RANGE`或`REVERSAL_CONFIRMED`。

## 2. 规则卡

### TRENDS-C16-S01：微通道检测与强度评分

- 类型：状态组件，不单独成交。
- 依据，PDF p.281–283、286–288：micro trend line通常持续2至约10bars；micro channel极紧、回撤很少，bar越多且实体越强，首次突破越容易失败。
- 评分候选：
  - `+0.25 × normalized_length`；
  - `+0.30 × body_score`；
  - `+0.20 × (1-tail_penalty)`；
  - `+0.25 × (1-violation_rate-line_error_cap)`。
- `score>=0.70` 为strong，`0.50–0.70` 为weak；阈值均为`PROXY`，必须做敏感性测试。
- 结束：出现明确逆向突破，或连续2bars不再满足单调极值/容差条件。
- 输出必须保留起点、终点、方向、长度、严格/宽松版本、外层市场状态，禁止事后向左延长。

### TRENDS-C16-S02：顺势微通道的首次逆向突破失败

- 类型：完整顺势策略。
- 依据，PDF p.281–289、294–295：强趋势中的微通道首次逆向突破通常只持续1–2bars，常形成High 1/Low 1后恢复趋势；持续bar越多，首次反转越容易失败。
- Setup：S01为strong且方向与Always-In一致；首次bar穿越微趋势线或首次出现逆向极值回撤。
- 等待：不在首次突破上逆势；观察 `1–2bars`，最长测试 `3bars`。
- 多头触发：首次下破后，价格突破bull signal bar高点或形成High 1；空头对称。
- 入场：signal bar外1 tick或 `0–0.10ATR` 的stop entry。
- 止损：首次回撤极值外 `1tick–0.25ATR`；高波动时按结构止损缩小仓位，不收紧到噪声内。
- 目标：旧趋势极值、1R/2R、或直到新的微通道被明确破坏。
- 失效：逆向突破形成强spike、穿越EMA并有2–3bars跟进；转入反转确认流程，不机械加仓。

### TRENDS-C16-S03：逆势微通道作为旗形

- 类型：顺外层趋势的旗形策略。
- 依据，PDF p.283–286、289、296–297：bear trend中的bull micro channel通常是bear flag，反之亦然；应交易其顺大趋势突破或breakout pullback。
- Setup：微通道方向与已确认Always-In相反，且尚无major trend reversal确认。
- 触发A：顺外层趋势突破微通道边界，突破bar实体≥ `0.5ATR` 或收盘位于其range外25%。
- 触发B：突破后 `1–5bars` 回测边界失败，形成lower high/higher low。
- 入场：A为激进stop，B为标准breakout-pullback stop。
- 止损：旗形极值外；B可用回测极值外。
- 目标：外层趋势旧极值、旗形高度等幅、1R/2R。
- 例外：若该旗形位于成熟趋势末端，并有climax、主要支撑阻力及强反向spike，则标为`POSSIBLE_FINAL_FLAG`，等待S05或正式反转确认，不能预设必然延续。

### TRENDS-C16-S04：突破失败与“失败后的再失败”状态机

- 类型：双向事件驱动策略。
- 依据，PDF p.282–286、290–293：micro channel可以成功突破、失败反转或横盘；失败突破后的反转若再失败，会困住另一侧并产生breakout-pullback机会。
- 状态机：

```text
CHANNEL -> FIRST_BREAK
FIRST_BREAK -> FAILED_BREAK       if price returns across boundary within 1–3 bars
FAILED_BREAK -> TREND_RESUMPTION  if reversal entry gets follow-through
FAILED_BREAK -> FAILURE_OF_FAILURE if reversal signal is broken oppositely
any state -> RANGE                if doji/overlap dominates for 3–8 bars
```

- `FAILED_BREAK`：按S02交易原趋势恢复。
- `FAILURE_OF_FAILURE`：原恢复方向的signal被反向突破后，在首次pullback交易最新突破方向；两侧交易者被困可提高评分，但不改变止损。
- 入场：第二次失败signal bar外stop，或突破后首次回测；不得在同一bar同时假设两个互斥成交。
- 止损：最新失败极值外。
- 目标：通道起点、最近swing、1R/2R。
- RANGE分支：停止趋势追单，等待区间明确突破及跟进。

### TRENDS-C16-S05：持续10bars以上的微通道高潮反转

- 类型：条件式反转策略。
- 依据，PDF p.287–289：持续约10bars以上的micro trend line代表不可持续的极端行为，反转交易价值上升，但首次尝试仍常失败，应等待breakout pullback或第二次尝试。
- Setup：`L>=10`，同时至少满足两项：远离EMA `1.5–3ATR`、连续同向趋势bar、到达预定义测量目标、出现wedge/第三推进、关键支撑阻力。
- 首次逆向突破只建立候选，不成交。
- 触发：首次反转失败后第二次反转，或强逆向spike后的breakout pullback保持在微趋势线/EMA反向一侧。
- 入场：第二信号bar外stop。
- 止损：climax最终极值外。
- 目标：EMA、micro channel起点、10bars两腿、1R/2R。
- 失效：突破pullback回到旧趋势方向且创新极值；切回S02，不连续猜顶底。

### TRENDS-C16-S06：强趋势内两点微趋势线失败突破

- 类型：短周期顺势策略。
- 依据，PDF p.289–294：在很陡的趋势中，哪怕仅相邻两bar构成的微趋势线，其逆向突破失败也可提供顺势入场；理论穿越可能小于一个tick。
- Setup：外层trend score≥0.70；最近2–5bars形成同向微趋势线；首次逆向穿越或测试没有跟进。
- 数据实现：小于tick的几何穿越不可观察，统一映射为“触线/越线≤1tick”；不得用插值伪造可成交价格。
- 触发：下一bar恢复外层趋势并越过失败bar极值。
- 入场：stop；若触发bar过大（range>2ATR），等待首次小回撤。
- 止损：失败bar或最近swing外。
- 目标：旧极值、1R/2R；若形成新微通道可跟踪退出。
- 禁用：交易区间中部、外层趋势未确认、或所需止损导致仓位小于最小可交易单位。

### TRENDS-C16-S07：微通道作为高周期 Spike 的状态转换

- 类型：多周期解释与目标组件。
- 依据，PDF p.282、295–300：低周期micro channel常对应高周期spike，之后常演化为较宽channel；无需下钻到1分钟寻找解释。
- 在基础周期检测到strong micro channel后，于高一周期聚合bar记录 `HTF_SPIKE_CANDIDATE`。
- 微通道结束后 `5–20bars` 若出现有序回撤及第二推进，转为`SPIKE_AND_CHANNEL`候选。
- 延续目标分别测试：micro channel高度、首个spike高度，以及spike起点至首回撤的测量移动；目标在事件发生时冻结。
- 该组件只能修改市场状态和退出目标，不因多周期标签本身新增入场。
- 多周期数据必须使用已完成bar；禁止读取尚未收盘的高周期bar。

### TRENDS-C16-N01：禁止微趋势线逆势和1分钟确认偏差

- 类型：`NEGATIVE`。
- 依据，PDF p.288–294：micro trend line break只应用于顺势setup；bull trend回撤内的bear micro line，其失败通常是买点而非卖点。下钻1分钟过快，容易只挑选事后成功的形态并持续亏损。
- 在major trend reversal确认前，禁止把回撤内部微趋势线的失败突破作为逆外层趋势入场。
- 不允许用“1分钟图上能找到更好信号”作为历史成交条件，除非策略从研究开始即固定使用该周期、完整保存全部信号并建模滑点。
- 禁止只保留支持基础周期结论的低周期案例；必须统计所有候选。
- 只有反向spike、跟进和higher low/lower high完成Always-In翻转后，微趋势线的可交易方向才随之改变。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 281–283 | micro trend line/channel定义、首次突破多失败 | 第1节、S01、S02 |
| 283–286 | 顺势、逆势旗形及三种突破结局 | S03、S04 |
| 286–289 | 长度、实体和尾部决定强度；10bars高潮 | S01、S02、S05 |
| 289–294 | 极短微线、失败后的再失败、只顺势交易 | S04、S06、N01 |
| 294–297 | 强趋势/大波动例子、仓位与高周期spike | S02、S03、S07 |
| 297–300 | micro channel后channel、多周期解释及测量目标 | S07 |

## 4. 回测验收

- S01逐bar建立候选；长度、端点和强度只能使用当时已完成bar，不得事后重画。
- 严格零破坏与允许一次轻微破坏的检测结果分别报告。
- 按外层状态、方向、长度 `2–4/5–9/≥10`、body score、尾部和距EMA距离分层。
- S02直接报告首次逆向突破在1、2、3bars内恢复旧趋势的概率、MAE/MFE及High 1/Low 1增量。
- S04按首次突破成功、失败、失败后的再失败、横盘四个互斥终态建立事件账本。
- S05必须与“第一次突破立即反转”基线对比，验证等待第二信号的代价和收益。
- 高波动案例使用固定账户风险反推仓位；不得用固定合约数比较。
- S07所有高周期特征延迟至聚合bar收盘后生效。
- Figure 16.1–16.6仅作章节例证，不作参数拟合或绩效证据。
