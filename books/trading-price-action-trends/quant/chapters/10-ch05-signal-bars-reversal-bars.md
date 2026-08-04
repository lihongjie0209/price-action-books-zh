# 第 5 章：信号 Bar——反转 Bar

## 元数据

- 英文来源：`books/trading-price-action-trends/en/chapters/10-ch05-signal-bars-reversal-bars.md`
- PDF 页码：121–132
- 图表：Figure 5.1–5.3；正文已给出量化所需的重叠、bar序号和行为，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 反转 Bar 特征模型

反转 bar 必须“反转此前价格行为的某个方面”，不要求一定创新高/低，也不要求传统蜡烛图外形。多头和空头完全镜像。

### 1.1 多头反转 Bar 最低条件

至少满足一项：

- `close > open`；或
- `close_pos > 0.50`。

空头版本为 `close < open` 或 `close_pos < 0.50`。这是 `AUTHOR` 最低定义，不等于足够入场。

### 1.2 强度特征

```text
directional_body       = body_frac with correct close direction
directional_close      = close_pos for bull, 1-close_pos for bear
rejection_tail         = lower_tail_frac for bull, upper_tail_frac for bear
wrong_side_tail        = upper_tail_frac for bull, lower_tail_frac for bear
close_reversal_count   = number of prior consecutive closes crossed by close[t]
extreme_reversal_count = number of prior highs/lows crossed by close[t]
prior_overlap          = overlap with each of prior 1..3 bars
relative_body          = body / median(body, prior 5..10 bars)
```

| 特征 | 宽松 | 基准 | 严格 | 来源 |
|---|---:|---:|---:|---|
| 反转方向 `body_frac` | 0.35 | 0.50 | 0.65 | `PROXY` |
| 反转方向收盘位置 | 0.60 | 0.75 | 0.90 | `PROXY` |
| 拒绝影线 | 1/4 | 1/3 | 1/2 bar | `AUTHOR` 给出约 1/3–1/2；1/4为扩展 |
| 错向最大影线 | 0.30 | 0.20 | 0.10 | `PROXY` |
| 反转 prior closes | 1 | 3 | 5–10 | `AUTHOR` 表示越多越强；分档为 `PROXY` |
| 相对实体窗口 | 5 | 10 | 20 bars | `AUTHOR` 提到近期bars；20为扩展 |

`reversal_score` 先使用各特征等权平均，再在训练集内校准；不允许用示例图拟合权重。

## 2. 规则卡

### TRENDS-C05-S01：上下文过滤的反转 Bar

- 类型：完整策略。
- 英文依据，PDF p.121–123：反转 bar 是可靠 signal bar，但 setup bar 本身不是入场理由；必须属于延续或反转结构并由后续 stop entry 触发。
- 上下文至少满足一项：
  - 趋势回撤结束，交易方向与趋势一致；
  - 趋势线已经突破，随后测试旧极值；
  - 预先登记的支撑/阻力或测量目标；
  - 交易区间边缘，而非中间。
- Setup：反转 bar 通过最低条件和对应上下文的质量阈值。
- 入场：多头 `high[t]+buffer`，空头 `low[t]-buffer` 的 stop entry；只在后续 bar 触发。
- 止损：反转 bar 极值外 1 tick；若完整结构失效位更远，则按完整结构计算仓位。
- 目标：最近摆动、1R、2R；逆势版本在首目标部分止盈。
- 失效：订单触发前反向突破 signal bar；订单默认 `1–3 bars` 到期。

| 上下文 | 最低 reversal score | 最低目标空间 | 来源 |
|---|---:|---:|---|
| 强趋势顺势回撤 | 0.40–0.60 | 1R | `PROXY` |
| 普通趋势顺势 | 0.55–0.70 | 1R | `PROXY` |
| 区间边缘 | 0.60–0.75 | 至中点≥1R | `PROXY` |
| 逆势反转 | 0.75–0.90 | 1–2R | `PROXY` |

### TRENDS-C05-S02：趋势线突破—旧极值测试—反转

- 类型：严格逆势策略。
- 英文依据，PDF p.123：强趋势的逆势交易必须先有趋势线突破，再在旧极值测试处形成强反转 bar；市场第二次尝试失败后常尝试相反方向。
- Setup 顺序：
  1. 现有趋势至少 `10–50 bars`。
  2. 收盘突破实时趋势线 `0.10–0.50 ATR`，并出现反向动量。
  3. 价格在 `3–30 bars` 内测试旧趋势极值；允许更高高点/更低低点，容差 `0–0.50 ATR`。
  4. 测试处出现 `reversal_score≥0.75–0.90` 的强 bar。
- 入场：反向 stop entry。
- 止损：测试极值外 1 tick。
- 目标：EMA、趋势线突破起点、1R；余仓寻找第二腿/2R。
- 失效：旧趋势强力创新极值并有 1–2 bars 跟进。
- `NEGATIVE`：没有趋势线突破的首次 1 分钟反转 bar 默认禁止；若研究自动化版本，必须单独统计而不能混入基准策略。

```text
if established_trend:
    if confirmed_trendline_break:
        wait_for_test_of_old_extreme()
        if strong_reversal_bar_at_test:
            arm_countertrend_stop_entry()
```

### TRENDS-C05-S03：高重叠反转 Bar 陷阱过滤

- 类型：禁入过滤器及失败反转策略。
- 英文依据：
  - PDF p.123–125：大幅重叠说明市场可能只是区间，没有趋势可反转。
  - PDF p.124：三根大重叠 bars 的旗形中，强反转 bar 约 60% 可能是陷阱；该概率是待检验的作者主张。
  - PDF p.128：Figure 5.2 的 bar 2 与前 bar 约重叠 50%，不应立即交易。
- 禁入条件满足任一：
  - signal bar 与最近 `2–4 bars` 中至少两根重叠 `≥0.50–0.80`；
  - bull reversal 的中点高于 prior low，或 bear reversal 的中点低于 prior high（作者给出的重叠警示）；
  - 大 doji、错向长影且弱实体；
  - 入场价位于区间/旗形靠近交易方向的一端，目标空间不足1R。
- 第二信号例外：若第一次反转触发后迅速失败，出现强反向 bar，则可交易被困者退出方向。
- 失败反转入场：突破失败 signal/entry bar 的相反极值。
- 止损：陷阱最终极值外；目标为区间中点、对侧或1R/2R。

### TRENDS-C05-S04：非传统强反转与 Always-In 翻转

- 类型：完整动量反转策略。
- 英文依据，PDF p.130–132：Figure 5.3 的 bar 29 不需要高于 prior high；它以强空头实体反转此前13个收盘和12个低点，并可翻转 Always-In 方向。
- Setup：现有 leg 中出现反向强趋势 bar，满足：
  - `body_frac≥0.60–0.80`；
  - `close_reversal_count≥3–13`；
  - `extreme_reversal_count≥2–12`；
  - 收盘突破近期 `5–20 bars` 区间边界。
- 入场：反转 bar 收盘后的下一可成交价，或突破其反向极值。
- 止损：反转 bar 另一端；若range>2 ATR则等待首次回撤。
- 目标：反转 bar 高度 `0.75/1.00/1.25` 测量移动、1R/2R。
- 跟进逻辑：原趋势被困者在反弹/回撤中退出，因此第一次反向 High/Low 1/2 失败可作为加仓或重入候选，但总风险不得增加。
- 失效：1–3 bars 内收回反转 bar 60%以上并恢复旧趋势。

该规则把“反转了多少 prior closes/highs/lows”作为主要特征，不要求传统反转 bar 外形。

### TRENDS-C05-S05：弱 Entry Bar 的退出管理

- 类型：成交后管理规则。
- 英文依据，PDF p.131–132：signal 后出现 doji/inside entry bar 表示缺乏紧迫性；弱 setup 加弱 entry 应尝试保本退出，强 setup 则可保留原结构止损。
- 入场后观察 `1–2 bars`：
  - `STRONG_ENTRY`：同向趋势 bar且创新极值，保留计划。
  - `WEAK_ENTRY`：doji、inside bar、无同向收盘或快速回到 signal bar。
- 若 setup score `<0.70` 且 entry 弱：下一次到达 `-0.1R至+0.1R` 区域退出；否则按市价小亏退出。
- 若 setup score `≥0.75–0.90` 且 entry 弱：保留 signal/结构极值止损，不将止损机械提高到 doji 另一侧。
- 对照组：立即退出、保本退出、原计划不变。
- `AUTHOR` 待检验主张：反转附近 doji 后价格约有 50% 概率交易到其另一侧。

| 参数 | 搜索范围 | 基准 | 来源 |
|---|---:|---:|---|
| 弱 entry 观察窗口 | 1–3 bars | 1 | `PROXY` |
| 强 setup 阈值 | 0.70–0.90 | 0.80 | `EMPIRICAL` |
| scratch 区域 | ±0.05–0.20R | ±0.10R | `PROXY` |
| 最大可接受小亏 | 0.05–0.30R | 0.15R | `EMPIRICAL` |

### TRENDS-C05-S06：收盘前反转失败陷阱

- 类型：bar 内执行规则；需要 tick 或快照数据。
- 英文依据，PDF p.124–125：强趋势中的反转 bar 可能在最后数秒崩回趋势方向，使提前逆势者被困并推动趋势延续。
- Setup：bar 进行中曾达到反转质量阈值，产生潜在逆势意图。
- 禁止：在 bar 收盘前把临时 OHLC 当作最终 reversal bar 下 stop order。
- 趋势延续触发：最终收盘变成旧趋势方向强 bar，且下一 bar 突破其趋势方向极值。
- 入场：旧趋势方向 stop entry。
- 止损：失败 bar 另一侧。
- 目标：原趋势新极值、1R/2R。
- 参数：最后 `2%–10%` bar 时间内收回临时反转幅度的 `50%–100%`；均为 `PROXY`。
- 只有最终 OHLC 时，本规则只能识别最终趋势 bar，不能声称检测到“收盘前失败”。

### TRENDS-C05-N01：禁止跨图寻找完美反转 Bar

- 类型：`NEGATIVE` 数据挖掘约束。
- 英文依据，PDF p.125：每个反转都可能在某个任意周期上呈现完美 bar；搜索大量周期只为找到完美形态会分散注意并造成挑选偏差。
- 回测限制：目标周期和备选周期集合必须在训练前冻结；不得对每笔交易选择事后最漂亮的 bar 周期。
- 多周期模型必须同时输入固定周期，并在高周期收盘后才可使用其特征。

## 3. 原文覆盖表

| PDF | 原文章节主张 | 量化映射 |
|---:|---|---|
| 121–122 | bull/bear reversal bar 的最低条件和强度特征 | 第1节、S01 |
| 122 | 反转更多 prior closes/highs/lows 通常更强 | 第1节、S04 |
| 122–123 | setup 必须结合上下文；成交后才成为 signal bar | S01；沿用第4章事件生命周期 |
| 123 | 强趋势逆势必须等趋势线突破和旧极值测试 | S02 |
| 123–125 | 高重叠、区间中部、大doji和错向长影是弱反转 | S03 |
| 124 | 大重叠旗形强 signal 约60%可能是陷阱 | S03，作为 `AUTHOR` 假设验证 |
| 124–125 | 最后数秒反转失败会形成顺势陷阱 | S06 |
| 125 | 不应跨任意周期寻找完美反转 bar | N01 |
| 126–127 | 区间内重叠 reversal 无物可反；失败后反向可交易 | S03 |
| 128–129 | 长影小实体必须结合突破、支撑和高潮上下文 | S01、S03 |
| 129 | 连续卖出高潮后作者预期至少两腿和10bars反弹 | 沿用第2章S06，避免重复策略 |
| 130–131 | 非传统强反转可翻转多根收盘和Always-In方向 | S04 |
| 131–132 | weak signal + weak entry 应scratch；强setup可容忍doji | S05 |
| 132 | 三根以上大重叠bars靠近EMA的旗形易成陷阱 | S03 |

## 4. 回测与验收

- 反转 bar 特征逐项做消融：实体、收盘位置、影线、重叠、反转 prior closes/extremes、上下文。
- 按顺势回撤、区间边缘、区间中部、首次逆势、趋势线突破后测试分层。
- S03 必须直接检验作者的约 50% 重叠警示和约 60% trap 主张，并报告置信区间。
- S04 比较传统外形与“反转多根 closes/lows/highs”的增量预测价值。
- S05 同时报告 scratch 减少的亏损与错过的盈利，且用真实可成交价。
- S06 没有 bar 内数据时标为不可检验；有数据时计入决策延迟和滑点。
- 所有 pivot、趋势线和水平位必须在 signal bar 前实时存在；Figure 5.1–5.3 仅作解释，不作拟合样本。
