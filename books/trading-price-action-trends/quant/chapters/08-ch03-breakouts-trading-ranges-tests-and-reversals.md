# 第 3 章：突破、交易区间、测试与反转

## 元数据

- 英文来源：`books/trading-price-action-trends/en/chapters/08-ch03-breakouts-trading-ranges-tests-and-reversals.md`
- PDF 页码：109–114
- 图表：Figure 3.1；正文已逐项解释 bar 1–9 和相关水平位，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 章节模型

本章把市场行为描述为循环状态机：

```text
TRADING_RANGE
    -> BREAKOUT_SPIKE
    -> CHANNEL
    -> TEST_OF_CHANNEL_START
    -> NEW_TRADING_RANGE
```

突破失败时，`BREAKOUT_SPIKE` 直接转为 `FAILED_BREAKOUT/REVERSAL`；大多数趋势反转首先转成交易区间，而不是立即形成反向趋势。

需要独立检验的作者主张：

- 趋势通常从趋势 bar/spike 开始，随后变成斜率更缓、重叠更多、影线更多的 channel。
- channel 起点通常会被测试；小级别可能当日完成，大级别可能一两天后完成。
- 趋势通道线方向的加速突破通常在约五 bars 内失败。
- 关键位测试必须依据测试时的动量与拒绝行为，在突破延续和反转之间选择。
- 大多数反转只把趋势变成区间，但通常仍足以提供波段利润，因此反转仓位应在首个合理目标部分止盈。

## 2. 基础检测器

### 2.1 实时区间边界

候选区间要求最近 `N=10–40` bars 同时满足：

- 相邻 bar 中至少 50%–80% 的重叠率达到公共阈值。
- 归一化净位移小于 `0.5–1.5 ATR`。
- 至少存在两个已确认上边界测试和两个下边界测试。
- 区间宽度为 `0.8–5 ATR`；更窄形态单独标记为 tight range。

边界使用当时已确认的摆动点或滚动高低，不能在突破发生后回头选择最整齐的水平线。

### 2.2 Spike 与 channel

```text
spike:
    1..5 bars in the same direction
    net move >= 1.0..3.0 ATR
    at least one trend bar
    low overlap and strong closes

channel after spike:
    first meaningful pullback completes
    price resumes in spike direction
    slope is shallower than spike slope
    overlap/tails/countertrend bars increase
```

| 参数 | 宽松 | 基准 | 严格 | 来源 |
|---|---:|---:|---:|---|
| spike bars | 1–5 | 2–4 | 2–3 | `PROXY` |
| spike 净移动 | 1.0 | 1.5 | 2.5 ATR | `PROXY` |
| 首次有效回撤 | 0.20 | 0.40 | 0.70 ATR | `PROXY` |
| channel/spike 斜率比 | ≤0.80 | ≤0.60 | ≤0.40 | `PROXY` |
| channel 最少 bars | 5 | 10 | 20 | `PROXY` |
| channel 重叠率 | ≥0.40 | ≥0.55 | ≥0.70 | `PROXY` |

## 3. 规则卡

### TRENDS-C03-S01：区间突破成功/失败判定

- 类型：完整突破策略，带失败反转分支。
- 英文依据，PDF p.109–110：突破通常表现为趋势 bar 和 spike；最重要的能力是区分成功与失败突破。
- Setup：存在 2.1 的区间或事前定义的支撑阻力线。
- 突破候选：收盘越界 `0.05/0.10/0.20 ATR`。

#### 成功分支

- 1–3 bars 内出现同向趋势 bar，或连续收盘保持边界外。
- 入场：跟进收盘后的下一 bar，或突破回撤的顺势 stop entry。
- 止损：突破回撤极值外；没有回撤则为突破 bar 另一端。
- 目标：区间高度 `0.75/1.00/1.25` 倍、1R、2R。

#### 失败分支

- 1–5 bars 内收回边界，且出现反向趋势 bar或突破反向极值。
- 入场：向区间内部 stop entry。
- 止损：失败突破极值外 1 tick。
- 目标：区间中点、对侧边界；强反向 spike 可保留至2R。

#### 未决分支

- 越界后出现小实体、高重叠、无方向跟进时不交易，等待重分类。

必须把“触发候选数”和“实际成交数”分开报告，避免只统计明显成功的突破。

### TRENDS-C03-S02：趋势通道线加速突破失败

- 类型：完整失败突破策略。
- 英文依据，PDF p.110：趋势方向突破 channel line 很少持续，通常约五 bars 内失败。
- 上下文：已存在 spike 后 channel，至少有两个实时确认的通道线触点。
- Setup：价格向原趋势方向越过通道线 `0.05–0.50 ATR`，短时斜率高于原 channel。
- 等待窗口：`AUTHOR≈5 bars`；测试 `3–8 bars`。
- 触发：窗口内重新收回通道，随后突破首根反向 bar 的极值。
- 入场：反向 stop entry；若原趋势仍非常强，仓位为标准的 25%–50%。
- 止损：加速突破极值外 1 tick。
- 目标：channel 中线、channel 起点、1R/2R。
- 失效：窗口内连续两根强趋势 bar 保持通道外；此时按加速趋势处理，不继续逆势。

```text
if mature_channel and close_outside_trend_channel_line:
    start failure_clock(max_bars = 3..8)
    if closes_back_inside and opposite_trigger:
        enter_countertrend
    elif two_strong_follow_through_bars:
        cancel_failure_setup
```

### TRENDS-C03-S03：关键水平测试决策树

- 类型：突破/反转路由器。
- 英文依据，PDF p.110：作者列出的测试对象包括趋势线、通道线、测量目标、摆动高低、入场/信号 bar 极值以及昨日 OHLC。

#### 水平位注册

每个水平位在测试发生前登记：

```text
level = {
    price,
    type,
    creation_time,
    last_test_time,
    test_count,
    originating_timeframe
}
```

同一价带内的多个水平可合并，但必须保留来源数量用于 confluence 分层。

#### 接近特征

- 最近 `3–10 bars` 归一化斜率。
- 同方向趋势 bar 比例和实体扩张/收缩。
- 到达水平前的回撤次数。
- 当前是首次还是重复测试。
- 水平位容差 `0.05–0.30 ATR`。

#### 突破分支

- 强动量接近，并收盘越过水平至少 `0.05–0.20 ATR`。
- 入场：水平外 stop entry，或突破回撤。
- 止损：回测摆动点另一侧。
- 目标：下一登记水平、1R/2R。

#### 拒绝/反转分支

- 接近动量减弱，在水平带内出现反转 bar 或越界后收回。
- 入场：反转 bar 反向极值外 stop entry。
- 止损：测试极值外。
- 目标：最近摆动点、区间中点、1R/2R。

不得把“更高高点、双顶或更低高点”硬编码为三种不同策略；本章强调的是水平附近是否出现拒绝。

### TRENDS-C03-S04：Spike—Channel 起点回测

- 类型：channel 成熟后的反向波段策略。
- 英文依据，PDF p.109–110、113–114：spike 后 channel 的起点通常被测试；作者建议把 bull channel 看成潜在 bear flag，反之亦然。
- Setup：
  1. 2.2 的 spike 已完成。
  2. 首次有效回撤终点冻结为 `channel_start`。
  3. 原方向恢复，但形成更缓且重叠更多的 channel。
  4. channel 至少出现两次推进；越成熟，回测假设权重越高。
- 基准触发：channel line 过冲失败、三推进、或强反向突破 channel trend line。
- 入场：反向 stop entry；不允许只因“已经是 channel”就盲目逆势。
- 止损：channel 最终极值外。
- 第一目标：`channel_start ±0.15 ATR`。
- 管理：到达 channel_start 平掉大部分或全部仓位，因为原趋势交易者和逆势交易者都可能在那里反向交易，形成反弹/新区间。
- 后续：目标处出现拒绝时可以启动原趋势方向新策略，但不是 S04 自动反手。

| 参数 | 搜索范围 | 基准 | 来源 |
|---|---:|---:|---|
| channel 最小推进 | 2–4 | 3 | `PROXY` |
| channel 最小年龄 | 8–40 bars | 15 | `PROXY` |
| 起点目标带 | ±0.05–0.30 ATR | ±0.15 | `PROXY` |
| 小形态最长回测时间 | 当日 10–80 bars | 40 | `AUTHOR` 仅说常在当日；数值为 `PROXY` |
| 大形态最长回测时间 | 1–3 sessions | 2 | `AUTHOR` 概念为一两天 |

#### 加仓版本仅作独立高风险研究

原文描述部分交易者在 bull channel 的回撤高点逐步做空，最终在 channel_start 附近使早期仓位保本、后期仓位盈利。该做法不能直接作为默认策略：

- 最多 `2–3` 腿；间距 `0.5–1 ATR`。
- 所有腿按最终结构止损计算的总最坏损失不得超过账户风险上限。
- 必须与“出现反向触发后一次入场”比较。
- 无上限逆势摊平属于禁止实现。

### TRENDS-C03-S05：反转先按区间管理

- 类型：反转仓位退出规则。
- 英文依据，PDF p.111：多数反转不会立即成为反向趋势，而只是从趋势过渡到交易区间；但移动通常足以构成波段。
- Setup：现有趋势出现有效反向 spike 或主要反转信号。
- 入场：沿用具体反转形态。
- 管理：
  - 首个合理目标（1R、EMA、原 channel 起点或最近摆动）减仓 25%–75%。
  - 剩余仓位只有在反向突破区间并跟进后，才按新趋势跟踪。
  - 若价格进入重叠区间，停止按“必然形成反向趋势”的假设扩大目标。
- 对照：全仓在首目标退出、部分止盈后等待、全仓追踪三种方案。
- 失效：原趋势恢复突破；按结构止损退出，不能因相信“大反转”而放宽止损。

### TRENDS-C03-S06：强突破后的 Always-In 方向过滤

- 类型：方向过滤组件。
- 英文依据，PDF p.113–114：Figure 3.1 的强多头趋势 bar 显示 Always-In 已翻多，作者建议多数交易者只沿该方向交易。
- 方向状态：`LONG / SHORT / NEUTRAL`。
- 翻转证据分数包括：
  - 反向突破重要边界。
  - 强趋势 bar。
  - 1–2 bars 跟进。
  - EMA 两侧状态。
  - 最近摆动结构反转。
- 至少 `2–4` 项通过才翻转；仅一个大 bar 且无跟进时保持旧状态或设为 `NEUTRAL`。
- 用途：
  - `LONG` 只允许多头 S01/S03 突破或回撤；空头仅可作为明确 S02/S04 反转研究。
  - `SHORT` 对称。
  - `NEUTRAL` 使用区间策略或不交易。
- 参数：证据阈值 `0.55–0.80`、确认 `1–3 bars`，均为 `EMPIRICAL`。

## 4. 原文覆盖表

| PDF | 原文章节主张 | 量化映射 |
|---:|---|---|
| 109 | 趋势通常以趋势 bar/spike 突破开始 | S01、2.2 |
| 109–110 | spike 之后斜率变缓、重叠增加并形成 channel | 2.2、S04 |
| 109–110 | channel 起点通常会被测试 | S04 |
| 110 | 趋势通道线方向加速突破通常约五 bars 内失败 | S02 |
| 110 | 多数高周期区间顺原趋势突破；几乎所有反转先形成区间 | S05；作为分层假设而非硬规则 |
| 110 | 测试对象包括趋势线、测量目标、摆动点、bar极值和昨日OHLC | S03 |
| 110 | 强突破与水平拒绝对应不同交易方向 | S03 |
| 111 | 多数反转只形成临时区间，但通常足以做波段 | S05 |
| 111 | 反转在不同周期可表现为单bar、两bar或多阶段结构 | 多周期测试要求 |
| 112–113 | 突破失败后出现 spike，再转 channel，最终回测起点 | S01、S04 |
| 113 | channel 的重叠、获利了结和逆势加仓体现双向交易增强 | S04 |
| 113–114 | 强趋势 bar 与跟进可改变 Always-In 方向 | S06 |
| 114 | spike/channel 回测后可能反弹、形成长期区间或反向趋势 | S04、S05，不预设目标后的方向 |

## 5. 回测与验收

### 必须避免的前视

- channel_start 在首次回撤结束并确认后冻结；不能用最终最优低点/高点重标。
- 区间边界、关键位和趋势通道线必须在测试或突破前存在。
- Always-In 翻转只能在所需跟进 bar 收盘后生效。
- 多周期反转标签必须等待对应周期 bar 收盘。

### 必须报告的比较

- 突破 bar 立即入场 vs 1–3 bars 跟进 vs 突破回测。
- 首次突破成功率与首次失败后反向交易结果。
- channel 起点回测：按 channel 年龄、推进数、斜率和高周期状态分层。
- S04 单次确认入场 vs 有上限、固定总风险的逆势加仓。
- 反转全仓追踪 vs 首目标部分止盈。
- 使用与不使用 Always-In 过滤器的信号数、期望和回撤。

### 验收标准

- S02 单独统计 3、5、8 bars 内失败率，以检验作者的“约五 bars”。
- S04 报告触及 channel_start 前的 MAE/MFE 和所需 bars，不只报告最终是否触及。
- 所有策略报告成本后样本外结果和相邻参数敏感性。
- Figure 3.1 只作为定义说明，不能作为拟合样本或盈利证据。
