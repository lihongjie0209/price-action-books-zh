# 第 1 章：价格行为谱系——从极端趋势到极端交易区间

## 元数据

- 英文来源：`books/trading-price-action-trends/en/chapters/06-ch01-the-spectrum-of-price-action-extreme-trends-to-extreme-trading-ranges.md`
- PDF 页码：87–90
- 已检查图表：Figure 1.1（5 分钟 E-mini；两段空头趋势、中间紧密区间、bar 2 假突破）
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 本章可量化结论

本章不是单一入场形态，而是一个上层市场状态模型：价格在“强趋势—弱趋势—宽区间—紧密区间”的连续谱上移动。下游策略应先识别状态，再决定使用顺势、突破或失败突破逻辑。

本章给出五类可独立验证的主张：

1. 市场具有惯性；趋势中的反转多数失败，区间中的突破多数失败。
2. 趋势和区间是嵌套的，状态判断必须绑定当前时间周期。
3. 两段式移动常见，第二腿可能在第一腿等幅目标附近结束。
4. High/Low 1–4 可以用状态机对回撤腿数进行实时计数。
5. 强开盘趋势后出现数小时紧密区间时，原趋势恢复概率上升；区间的反向假突破可成为持有至收盘的顺势信号。

## 2. 公共特征

### 2.1 趋势分数

对方向 `d ∈ {+1,-1}` 计算：

```text
directional_close_rate = mean(d * (close[i] - close[i-1]) > 0)
ema_side_rate          = mean(d * (close[i] - EMA20[i]) > 0)
normalized_slope       = d * linear_regression_slope(close, N) / ATR20
pullback_ratio         = max_countertrend_excursion / max(trend_move, tick_size)
overlap_rate           = mean(overlap(i, i-1) >= overlap_threshold)

trend_score = mean(
    directional_close_rate,
    ema_side_rate,
    clip(normalized_slope / slope_threshold, 0, 1),
    1 - clip(pullback_ratio / pullback_threshold, 0, 1),
    1 - overlap_rate
)
```

### 2.2 区间分数

```text
range_width       = (rolling_high(N) - rolling_low(N)) / ATR20
net_displacement  = abs(close[t] - close[t-N+1]) / ATR20
direction_changes = count(sign(close[i]-close[i-1]) changes) / (N-2)

range_score = mean(
    overlap_rate,
    1 - clip(net_displacement / displacement_threshold, 0, 1),
    direction_changes,
    clip(touches_of_both_boundaries / 4, 0, 1)
)
```

状态只使用已经收盘的 bars。分类窗口、阈值必须在训练样本内确定。

| 参数 | 宽松 | 基准 | 严格 | 来源 |
|---|---:|---:|---:|---|
| 分类窗口 `N` | 10 | 20 | 40 bars | `PROXY` |
| 趋势分数阈值 | 0.55 | 0.65 | 0.75 | `PROXY` |
| 区间分数阈值 | 0.55 | 0.65 | 0.75 | `PROXY` |
| 归一化斜率阈值 | 0.03 | 0.07 | 0.15 ATR/bar | `PROXY` |
| 最大回撤/趋势移动 | 0.60 | 0.40 | 0.25 | `PROXY` |
| 相邻 bar 重叠阈值 | 0.50 | 0.65 | 0.80 | `PROXY` |
| 状态确认 | 1 | 2 | 3 bars | `PROXY` |

若趋势分数和区间分数都未通过，状态为 `TRANSITION`；若两者同时通过，选择分数较高者，但当差值小于 0.10 时仍标记为 `TRANSITION`。

## 3. 规则卡

### TRENDS-C01-S01：状态惯性门控

- 类型：策略选择器/负向过滤器。
- 英文依据，PDF p.87：“If it is in a trend, most attempts to reverse it will fail.”以及“If it is in a trading range, most attempts to break out into a trend will fail.”
- Setup：按 2.1–2.2 只用已收盘 bars 得到当前状态。
- 规则：
  - `TREND_UP`：允许多头回撤和多头突破策略；默认禁止第一次空头反转尝试。
  - `TREND_DOWN`：对称处理。
  - `RANGE`：允许边缘反转和失败突破；未经跟进确认，不追逐首次突破。
  - `TRANSITION`：仓位降至标准仓位的 0%–50%，或完全不交易。
- 状态退出：相反状态分数连续达到确认 bars 后才切换，避免逐 bar 抖动。
- 回测：分别比较“不使用状态过滤”“硬状态过滤”“状态分数连续调仓”。

```text
state_t = classify(bars_through_t)
if state_t == TREND_UP:
    enable(with_trend_long)
    disable(first_countertrend_short)
elif state_t == TREND_DOWN:
    enable(with_trend_short)
    disable(first_countertrend_long)
elif state_t == RANGE:
    enable(fade_at_edges, failed_breakout)
    require_follow_through_for_breakout = true
else:
    position_multiplier = 0.0 to 0.5
```

本规则不声称逆势或区间突破永远亏损；它把作者的“多数失败”转换为需要通过条件概率验证的过滤假设。

### TRENDS-C01-S02：区间首次突破的跟进确认

- 类型：完整突破策略及反事实基线。
- 上下文：`state=RANGE`，已经存在可实时计算的上下边界。
- Setup：最近 `N=10–40` bars 的宽度为 `0.8–4 ATR`，至少各测试上下边界两次，且净位移小于 `0.5–1.5 ATR`。
- 突破候选：收盘越过边界至少 `0.05/0.10/0.20 ATR`。
- 入场：默认等待 1–3 bars 跟进；至少满足以下一项：
  - 下一 bar 是同向趋势 bar，并收在边界外；
  - 连续两根收盘未回到边界内；
  - 突破后的首次回测没有收回边界。
- 初始止损：回测摆动点外 1 tick；无回测时放在突破 bar 另一端，并拒绝风险超过 2 ATR 的交易。
- 目标：区间高度的 `0.75/1.00/1.25` 倍；同时报告 1R 和 2R 对照。
- 失效：1–3 bars 内收回边界且出现反向趋势 bar，转交 S03。
- 反事实：在相同候选上测试“首次越界立即追入”，用于检验作者关于区间突破多失败的主张。

### TRENDS-C01-S03：区间假突破反转

- 类型：完整反转策略。
- 英文依据，PDF p.88–89：Figure 1.1 的紧密区间先向上突破一个 tick，随后向下突破并形成强空头趋势；作者将该反向假突破描述为良好的波段形态。
- 上下文：`state=RANGE`；越界方向不得与一个仍然很强的上层趋势一致，否则只作为观察信号。
- Setup：价格越过区间边界 `0–0.50 ATR`，随后在 `1–5 bars` 内收回。
- 触发：收回 bar 为反向趋势 bar，或后续价格突破收回 bar 的反向极值。
- 入场：向区间内部的 stop entry。
- 初始止损：假突破极值外 1 tick，加 `0–0.10 ATR` 结构缓冲。
- 目标：区间中点先减仓 25%–50%，对侧边界再减仓；若 S05 的趋势恢复条件成立，剩余仓位持有至测量目标或交易时段结束。
- 失效：原突破方向重新收于边界外，并出现 1–2 bars 强跟进。

| 参数 | 宽松 | 基准 | 严格 | 来源 |
|---|---:|---:|---:|---|
| 最大越界 | 0.50 | 0.25 | 0.10 ATR | `PROXY`；Figure 1.1 示例为一个 tick |
| 收回窗口 | 5 | 3 | 1 bar | `PROXY` |
| 反向 bar `body_frac` | 0.40 | 0.55 | 0.70 | `PROXY` |
| 停损缓冲 | 0.10 | 0.05 | 0 ATR | `PROXY` |

### TRENDS-C01-S04：两段等幅移动目标与反转候选

- 类型：目标模型；反转只作为待确认候选。
- 英文依据，PDF p.88：作者说明两段式移动常见，并提到交易者会在第二腿接近第一腿等幅时寻找反转。
- 实时腿定义：
  1. 用左右各 `1–3` 个已完成 bars 的确认 pivot 建立 `leg 1`。
  2. 中间反向移动至少 `0.15–0.50 ATR` 才开始下一腿。
  3. `leg 2` 与 `leg 1` 同向，幅度至少 `0.3 ATR`。
- 投影：在 leg 2 起点冻结 `target = leg2_start + signed_size(leg1)`，入场后不得重选锚点。
- 用途：
  - 已持有同向仓位：在 `0.75/1.00/1.25 × leg1` 分批止盈。
  - 寻找反转：到达投影本身不能入场；必须同时出现趋势线破坏、极值测试失败或反向趋势 bar。
- 反转止损：第二腿最终极值外 1 tick。
- 反转目标：中间回撤点、1R、两段式反向移动。
- 失效：目标附近仍出现强同向突破和跟进，取消反转候选。

| 参数 | 搜索范围 | 基准 | 来源 |
|---|---:|---:|---|
| pivot 左右确认 | 1–5 bars | 2 | `PROXY` |
| 腿间最小回撤 | 0.15–0.75 ATR | 0.30 | `PROXY` |
| 两腿幅度比 | 0.50–1.50 | 0.67–1.33 | `PROXY` |
| 等幅目标带 | ±0.05–0.25 ATR | ±0.15 ATR | `PROXY` |
| 等幅投影 | 1.00 × leg 1 | 1.00 | `AUTHOR` 概念 |

### TRENDS-C01-S05：开盘强趋势—紧密区间—趋势恢复

- 类型：完整日内策略。
- 英文依据，PDF p.89：“Whenever there is a strong trend on the open and then a tight trading range for several hours, the chances for a trend resumption day are good.”
- 原书特定时间证据：假突破常出现在约 11:00–12:00 PST；这是 E-mini 示例，不能直接迁移到其他市场。
- Setup：
  1. 开盘窗口 `3–12 bars` 内形成同向移动 `1.0–3.0 ATR`，趋势分数通过。
  2. 随后形成持续 `12–48 bars` 的紧密区间；区间宽度 `0.5–2.0 ATR`，相邻 bar 强重叠率至少 60%–80%。
  3. 区间保留在开盘趋势移动的顺势半区，反向回撤不超过开盘移动的 40%–70%。
- 优先触发：区间向开盘趋势反方向假突破，随后收回区间。
- 备选触发：直接向原趋势方向突破并出现 S02 的跟进。
- 入场：原开盘趋势方向 stop entry。
- 初始止损：假突破极值外；直接突破版本放在区间另一侧。若风险超过 2 ATR，按固定账户风险缩仓或跳过。
- 目标：区间高度测量移动；1R/2R 分批；日内版本最迟在 session close 退出。
- 失效：反方向有效突破并跟进，或价格穿越开盘趋势起点。

跨市场时段参数：

| 参数 | 宽松 | 基准 | 严格 | 来源 |
|---|---:|---:|---:|---|
| 开盘窗口 | session 前 15% | 前 10% | 前 5% | `PROXY` |
| 中段假突破窗口 | session 45%–75% | 50%–70% | 55%–65% | `PROXY`；用于替代固定 PST 时间 |
| 初始趋势移动 | 1.0 | 1.5 | 2.0 ATR | `PROXY` |
| 紧密区间长度 | 12 | 24 | 48 bars | `PROXY` |
| 区间重叠率 | 60% | 70% | 80% | `PROXY` |

## 4. High/Low 1–4 实时计数器

本章定义了术语，但详细交易规则留待后续书章。因此本章只建立可复用事件流，不把所有 H1/H2/L1/L2 都当成独立策略。

```text
state = {direction_of_pullback, leg_count, last_trigger_bar}

in bull trend or range with a downward pullback:
    when high[t] > high[t-1]:
        emit HIGH_(leg_count)
        last_trigger_bar = t
    if downward movement resumes after the trigger:
        leg_count += 1

in bear trend or range with an upward pullback:
    when low[t] < low[t-1]:
        emit LOW_(leg_count)
        last_trigger_bar = t
    if upward movement resumes after the trigger:
        leg_count += 1
```

实现必须额外固定：inside bar、outside bar、同一 bar 同时满足两个方向、最小腿幅和重置条件。初始建议为最小腿 `0.10–0.50 ATR`、最大事件间隔 `5–20 bars`；这些均为 `PROXY`。待第二本书第 17 章再扩展计数优先级。

## 5. 原文主张覆盖表

| PDF | 原文章节主张 | 量化映射 |
|---:|---|---|
| 87 | 价格行为位于极端趋势至极端区间的连续谱 | 2.1、2.2 |
| 87 | 趋势与区间在不同周期相互嵌套 | 状态必须绑定当前周期；见 6.1 |
| 87 | 市场具有惯性；趋势反转和区间突破多数失败 | S01–S03 |
| 88 | 两段移动常见，第二腿可能在第一腿等幅处反转 | S04 |
| 88–89 | 使用腿数以及 High/Low 1–4，而不是混用 ABC 与 AB=CD | 第 4 节状态机 |
| 88–90 | Figure 1.1：紧密区间向上一个 tick 假突破后，出现强下破 | S03、S05 |
| 89 | 开盘强趋势后数小时紧密区间，提高趋势恢复概率 | S05 |
| 89 | 约 11:00–12:00 PST 的假突破可形成持有至收盘的波段 | S05；固定钟点只保留为 E-mini `AUTHOR` 参数 |

## 6. 回测矩阵与验收

### 6.1 时间周期嵌套

作者指出趋势可能只是高周期区间的一部分，区间也可能只是高周期趋势的一部分。应分别测试：

- 只使用执行周期状态。
- 执行周期与 3–6 倍高周期同状态。
- 执行周期趋势、高周期区间；执行周期区间、高周期趋势。

高周期特征只能在高周期 bar 收盘后更新，禁止使用尚未完成的高周期数据。

### 6.2 必须报告的对照组

- 趋势中首次逆势信号 vs 等待趋势线破坏/第二次信号。
- 区间首次突破立即追入 vs 跟进确认后入场。
- 区间首次突破 vs 假突破反向入场。
- 两段等幅仅作止盈目标 vs 到价即反转 vs 到价加反转确认。
- S05 直接顺势突破 vs 反向假突破后顺势恢复。

### 6.3 通过条件

- 所有 pivot、区间边界、状态和高周期数据均无前视。
- 分别报告趋势、区间、过渡状态中的条件胜率和期望值，验证“多数失败”是否成立。
- S05 分别按市场、交易时段和开盘缺口分层，不能以 E-mini 的固定 PST 时段代表所有市场。
- 每个策略按公共协议报告成本后样本外期望、最大回撤、MAE/MFE 与参数敏感性。
- Figure 1.1 只作为规则解释样例，不作为参数拟合样本。
