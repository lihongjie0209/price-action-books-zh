# 第 4 章：Bar 基础——信号 Bar、入场 Bar、Setup 与蜡烛图形态

## 元数据

- 英文来源：`books/trading-price-action-trends/en/chapters/09-ch04-bar-basics-signal-bars-entry-bars-setups-and-candle-patterns.md`
- PDF 页码：115–120
- 图表：Figure 4.1；正文完整描述其信号、入场与跟进关系，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 事件生命周期

本章最重要的实现约束是：`signal bar` 不是在其收盘时自动成立，而是在后续订单实际成交后，才由 `setup bar` 转为 `signal bar`。

```text
SETUP_CANDIDATE(t)
    -> order submitted after bar t closes
    -> order triggered in bar u, u > t
    -> bar t becomes SIGNAL_BAR
    -> bar u becomes ENTRY_BAR
    -> first later bar supporting the trade becomes FOLLOW_THROUGH_BAR
```

因此数据模型至少需要：

```text
SetupEvent {
    setup_id,
    detected_at,
    direction,
    context_state,
    setup_bar_index,
    trigger_price,
    expires_at,
    status: candidate | armed | filled | cancelled | expired
}

TradeEvent {
    setup_id,
    signal_bar_index,   # 仅成交后赋值
    entry_bar_index,
    fill_price,
    follow_through_bar_index | null
}
```

任何把“所有看起来不错但从未触发的 bars”当成成功信号样本的回测都存在选择偏差。

## 2. 信号质量分数

```text
bar_direction_score =
    mean(body_frac_score, close_position_score,
         relative_body_score, small_opposite_tail_score)

context_score =
    mean(trend_alignment, location_quality,
         support_resistance_confluence, room_to_target)

signal_score = context_weight * context_score
             + bar_weight * bar_direction_score
```

权重不是固定的：趋势越强，顺势交易的 `context_weight` 越大；交易越逆势，`bar_weight` 和最低总分越高。

| 参数 | 顺势强趋势 | 顺势普通趋势 | 逆势 | 来源 |
|---|---:|---:|---:|---|
| `context_weight` 基准 | 0.80 | 0.65 | 0.50 | `PROXY` |
| `bar_weight` 基准 | 0.20 | 0.35 | 0.50 | `PROXY` |
| 最低 `signal_score` | 0.50–0.65 | 0.60–0.75 | 0.75–0.90 | `PROXY` |
| 最低同向 `body_frac` | 可不限制 | 0.40–0.60 | 0.55–0.75 | `PROXY` |
| 最低同向收盘位置 | 可不限制 | 0.60–0.75 | 0.75–0.90 | `PROXY` |

## 3. 规则卡

### TRENDS-C04-S01：顺势信号 Bar Stop Entry

- 类型：完整顺势入场框架。
- 英文依据，PDF p.116–118：趋势回撤中的同向信号 bar 上方/下方通常存在订单失衡；初学者应只交易趋势方向且选择同向趋势 bar。
- 上下文：趋势方向已经由已完成 bars 确认。
- Setup：回撤、暂停或小型旗形结束；普通趋势要求同向趋势 bar，强趋势允许反向实体或 doji，但必须处在高质量位置。
- 多头触发：`signal_high + entry_buffer`；空头对称。
- 入场：后续 bar 的 stop entry。触发后，setup bar 才标为 signal bar。
- 订单有效期：默认下一 bar；敏感性测试 `1–3 bars`。未触发则取消，重新评估最新 bar，不能永久保留旧订单。
- 止损：信号 bar/完整回撤结构另一侧加 1 tick。
- 目标：前趋势极值、1R/2R；出现跟进后允许趋势跟踪。
- 失效：触发前价格突破 setup 的反方向、趋势状态翻转，或到目标空间小于初始风险。

```text
on_close(t):
    if trend(direction) and pullback_or_pause_ending(t):
        quality = weighted_signal_score(t, direction)
        if quality >= threshold_for_context:
            arm_stop(direction, extreme(t) + buffer, expires=t+1..3)

on_fill(u):
    mark t as SIGNAL_BAR
    mark u as ENTRY_BAR
    freeze initial_stop and R
```

### TRENDS-C04-S02：逆势交易严格门控

- 类型：反转策略门控。
- 英文依据，PDF p.117–118、120：多数逆势尝试失败；最低要求是强趋势线突破后的回测，以及强反转 signal bar。Figure 4.1 的 countertrend long 使用了强多头反转 bar。
- 必须全部满足：
  1. 现有趋势已持续至少 `10–50 bars`，并出现减弱或高潮迹象。
  2. 价格强力突破趋势线，突破距离 `0.10–0.50 ATR`，而非仅盘中轻触。
  3. 随后回测旧极值或形成更高低点/更低高点；允许回测创新极值。
  4. 出现反转方向趋势 bar，`body_frac≥0.55–0.75`，收盘位置≥`0.75–0.90`。
  5. 到第一合理目标的空间至少 `1R`。
- 触发：强反转 bar 的反向 stop entry。
- 止损：回测最终极值外 1 tick。
- 目标：EMA、趋势线突破起点、1R；部分仓位等待第二腿或2R。
- 失效：触发前恢复原趋势；触发后没有反向跟进且收回信号 bar。
- `NEGATIVE`：未发生趋势线强突破时的第一次逆势 signal bar，只作为反事实基线，默认禁止。

### TRENDS-C04-S03：上下文自适应信号质量

- 类型：过滤组件。
- 英文依据，PDF p.117–118：趋势越强，signal bar 外观越不重要；越逆势，越需要强 signal bar。
- 趋势强度输入：连续同向趋势 bars、EMA 同侧率、突破跟进、回撤深度和新极值频率。
- 动态阈值：

```text
required_bar_quality =
    base_quality
    - alpha * aligned_trend_strength
    + beta  * countertrend_strength

required_bar_quality = clip(required_bar_quality, 0.35, 0.90)
```

- 初始搜索：`base=0.65–0.75`、`alpha=0.15–0.35`、`beta=0.15–0.35`，全部为 `EMPIRICAL`。
- 强趋势中允许“较差信号 bar”不等于无条件入场；位置、风险和目标空间仍必须通过。
- 输出：`pass/fail`、具体分数及被放宽/收紧的原因，便于审计。

### TRENDS-C04-S04：跟进 Bar 质量与早期退出

- 类型：持仓管理组件。
- 英文依据，PDF p.115：入场后的下一 bar 是 follow-through bar；即使横盘一两 bars 后才跟进仍有价值。
- 观察窗口：成交后 `1–3 bars`。
- 正向跟进：
  - 同向趋势 bar；或
  - 至少一根同向收盘并创新极值；或
  - 1–2 bars 横盘但未触及结构止损，随后同向突破。
- 负向跟进：反向强 bar、收盘越过 signal bar 中点、或价格快速回到原区间。
- 管理对照：
  - 无正向跟进立即退出。
  - 无正向跟进减仓 50%，保留结构止损。
  - 完全忽略早期跟进，作为基线。
- 跟进不得用于美化入场：只有窗口结束后才能标记，相关退出在下一可成交时点执行。

| 参数 | 搜索范围 | 基准 | 来源 |
|---|---:|---:|---|
| 跟进窗口 | 1–3 bars | 2 | `AUTHOR` 允许横盘一两 bars；具体实现为 `PROXY` |
| 正向最小收盘改善 | 0–0.25 ATR | 0.10 | `PROXY` |
| 负向收回 signal bar | 40%–80% | 60% | `PROXY` |
| 无跟进减仓比例 | 0%–100% | 50% | `EMPIRICAL` |

### TRENDS-C04-S05：双向挂单与一 Tick 陷阱

- 类型：订单执行研究。
- 英文依据，PDF p.115–116、118：每根 bar 两端都有 breakout 与 fade 订单；股票中一 tick 假突破常见，可将触发价放到 signal bar 外数 ticks。

#### 单向版本

- 只在上下文明确时，于 signal bar 顺势方向放 stop entry。
- `entry_buffer = max(1 tick, k × ATR)`，`k=0–0.10`。
- 未在 `1–3 bars` 内触发就取消。

#### 双向版本

- 仅在上下文中性且 bar 形成真实压缩时研究 OCO 双向 stop。
- 一侧成交后立即取消另一侧；回测必须模拟同 bar 两侧均触及时的最不利顺序。
- 大 range、高重叠的混乱区间禁止使用，因为双向陷阱和滑点过高。

#### 缓冲参数

- 固定 ticks 只对特定合约有效。
- 跨市场基准测试 `1、2、3 ticks` 与 `0.02、0.05、0.10 ATR`，并报告少成交与少假突破之间的权衡。

### TRENDS-C04-S06：临近收盘变形时等待第二次入场

- 类型：实时执行过滤器。
- 英文依据，PDF p.119：5 分钟 signal bar 可能在最后 5–10 秒突然扩大；不稳定的交易者应放弃并等待第二次入场。
- 仅在有 bar 内快照或 tick 数据时启用。
- 变形特征：
  - 最后 `2%–10%` bar 时间内 range 扩大 `20%–100%`；
  - 触发价相对原计划恶化 `0.10–0.50 ATR`；
  - signal bar 新高/低进入相反结构边界带；
  - 最近数 bars 都是大 range 且重叠率高。
- 动作：取消首次 stop entry，等待同方向第二次入场结构；不得仍按早期快照的止损/目标计算交易者方程。
- 若只有最终 OHLC，无 bar 内数据，则无法回测“最后几秒变形”，只能使用最终 signal bar 重新计算风险。

### TRENDS-C04-N01：蜡烛图名称不得作为独立信号

- 类型：`NEGATIVE` 研究约束。
- 英文依据，PDF p.118–119：作者认为大量蜡烛图名称脱离趋势/区间上下文时没有高概率预测价值。
- 禁止实现：仅凭 hammer、harami、hanging man 等名称入场。
- 合法对照：将形态分解成实体比例、影线、inside/outside 关系、位置和当前 regime，再测试：
  1. 只有名称；
  2. 只有数值特征；
  3. 数值特征加上下文。
- 若名称模型在样本外有独立增益，可保留为特征，但不能因传统名称预设方向。

## 4. Setup 类型登记表

本章列举但由后续章节详细定义的 setup，当前只建立标准枚举，防止实现时同义重复：

```text
CONTINUATION_SPIKE
REVERSAL_BAR
TWO_BAR_REVERSAL
THREE_BAR_REVERSAL
INSIDE_BAR
II_OR_III
SMALL_BAR_AT_EXTREME
IOI
OUTSIDE_BAR
OO
DOUBLE_TOP_OR_BOTTOM
FAILED_REVERSAL
FAILED_CONTINUATION
SHAVED_BAR
COUNTERINTUITIVE_TREND_BAR
PAUSE_IN_SPIKE
CHANNEL_BAR
HIGHER_LOW_OR_LOWER_HIGH
```

这些枚举不能自行产生订单。每个事件必须附带 `direction、regime、location、signal_score、trigger_price`，并等待对应后续章节补全规则。

## 5. 原文覆盖表

| PDF | 原文章节主张 | 量化映射 |
|---:|---|---|
| 115 | setup、signal、entry、follow-through 的先后关系 | 第 1 节、S04 |
| 115–116 | 每根 bar 两端同时存在 breakout 与 fade 交易者 | S01、S05；以状态和上下文路由 |
| 116 | 真正优势来自判断 prior bar 上下方的订单失衡 | 第 2 节、S01 |
| 116–117 | 列举 continuation/reversal/setup 类型 | 第 4 节枚举 |
| 117 | 初学者只交易趋势方向和同向趋势 signal bar | S01 |
| 117–118 | 逆势要求更强 signal bar、趋势线突破和回测 | S02 |
| 118 | 趋势越强，signal bar 外观越不重要 | S03 |
| 118 | stop entry 未触发应取消；股票存在一 tick trap | S01、S05 |
| 118–119 | 蜡烛名称脱离价格行为上下文无独立价值 | N01 |
| 119 | signal bar 在收盘前可能显著变形，宜等第二次入场 | S06 |
| 119 | 高重叠连续大 range bars 使交易风险增加 | S05、S06 风险过滤 |
| 119 | 高潮结束于第一根暂停 bar | 沿用第 2 章 S05，不重复定义 |
| 120 | countertrend 示例需要强反转 signal bar；后续跟进提高质量 | S02、S04 |

## 6. 回测与验收

- 候选 setup、挂单、未成交、取消、成交必须分别计数。
- signal bar 标签必须在成交后赋值；预测模型只能使用成交前可见的 setup 特征。
- 分层比较：顺势/逆势、强/普通趋势、同向/反向 signal body、首次/第二次入场。
- S03 必须展示趋势强度与所需 signal bar 质量的二维表现，避免只给单一阈值。
- S04 报告跟进发生的具体 bar、早退减少的亏损和错失的后续盈利。
- S05 使用保守的同 bar 成交顺序，并对触发缓冲做成本/成交率敏感性分析。
- S06 若缺少 bar 内数据必须标为不可检验，不得用最终 OHLC 伪造“最后几秒”。
- 所有结果遵守公共 walk-forward、成本和最少样本协议。
