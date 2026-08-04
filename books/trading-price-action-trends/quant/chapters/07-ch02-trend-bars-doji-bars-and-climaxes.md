# 第 2 章：趋势 Bar、Doji 与高潮

## 元数据

- 英文来源：`books/trading-price-action-trends/en/chapters/07-ch02-trend-bars-doji-bars-and-climaxes.md`
- PDF 页码：91–108
- 图表：Figure 2.1–2.6；本章正文与图注已完整描述量化所需关系，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 章节结论

本章的核心不是蜡烛图命名，而是实时判断单根 bar 和一组 bars 中哪一方占优：

- 单根 bar 应按相对实体、收盘位置、影线和上下文分为趋势 bar 或近似 doji；“完美 doji”没有额外价值。
- 一个强趋势 bar 既可能是新趋势的突破，也可能是成熟趋势的高潮。必须等待跟进或反向突破，不能只凭 bar 大小决定方向。
- 连续同向趋势 bar 通常至少还会产生一个同向新极值；孤立趋势 bar 没有跟进时可能是假突破。
- 同向实体、影线和收盘位置的累积构成买卖压力，可用于识别趋势向区间或反向趋势的过渡。
- doji 是单 bar 交易区间，但一串高点、低点、收盘都递增或递减的 doji 仍然构成趋势。
- “高潮”只表示走得太快，不等于立即反转；高潮后首先预期双向交易，只有反向突破才构成高潮反转。

## 2. Bar 特征与分类

```text
range_t       = high_t - low_t
body_t        = abs(close_t - open_t)
body_frac_t   = body_t / max(range_t, tick_size)
close_pos_t   = (close_t - low_t) / max(range_t, tick_size)
upper_tail_t  = (high_t - max(open_t, close_t)) / max(range_t, tick_size)
lower_tail_t  = (min(open_t, close_t) - low_t) / max(range_t, tick_size)
rel_body_t    = body_t / max(median(body[t-N:t-1]), tick_size)
rel_range_t   = range_t / max(median(range[t-N:t-1]), tick_size)
```

### 2.1 分类优先级

1. `BULL_TREND_BAR`：`close>open`，实体和收盘位置通过趋势 bar 阈值。
2. `BEAR_TREND_BAR`：对称定义。
3. `DOJI_LIKE`：实体相对于自身 range 和近期实体都较小。
4. `AMBIGUOUS`：介于两者之间；不得为满足策略而事后改名。

| 参数 | 宽松 | 基准 | 严格 | 来源 |
|---|---:|---:|---:|---|
| 趋势 bar `body_frac` | 0.45 | 0.60 | 0.75 | `PROXY` |
| 趋势 bar `rel_body` | 0.80 | 1.00 | 1.25 | `AUTHOR` 给出相当于或大于近 5/10 bars 中位实体；具体分档为 `PROXY` |
| bull 收盘位置 | ≥0.65 | ≥0.75 | ≥0.85 | `PROXY`；bear 对称 |
| 单侧最大影线 | 0.35 | 0.25 | 0.15 | `PROXY` |
| doji `body_frac` | ≤0.30 | ≤0.20 | ≤0.10 | `PROXY` |
| doji `rel_body` | ≤0.75 | ≤0.50 | ≤0.25 | `PROXY` |
| 相对窗口 `N` | 5 | 10 | 20 bars | `AUTHOR` 提到 5 或 10；20 为敏感性扩展 |

E-mini 的“一两个 tick 实体”只作为原书示例，跨市场实现必须使用比例或滚动分位数。

## 3. 规则卡

### TRENDS-C02-S01：趋势 Bar 跟进延续

- 类型：完整顺势策略。
- 英文依据，PDF p.92–93：连续强趋势 bars 是健康趋势信号，通常会再创新极值，即使先发生回撤。
- 上下文：最近 `10–40 bars` 的趋势方向与信号 bar 一致；或者信号 bar 是明确区间突破。
- Setup：出现 1–3 根同向趋势 bars；至少一根 `rel_body≥1.0`，收盘靠近同向极值。
- 跟进条件：后续 1–2 bars 满足以下至少一项：
  - 同向趋势 bar 收盘；
  - 收盘继续越过信号 bar 极值；
  - 回撤未跌破/升破信号 bar 中点并再次创新极值。
- 入场：跟进 bar 收盘后的下一 bar，或突破跟进 bar 同向极值的 stop entry。
- 初始止损：最近同向 spike 起点、信号 bar 另一端或跟进回撤极值外 1 tick；三者中选择真正使前提失效的位置。
- 目标：先测试原趋势新极值；然后比较 1R、2R 和 spike 高度测量移动。
- 失效：下一 bar 强反向收盘并收回信号 bar 50%–100%，转交 S02。
- 风险过滤：信号 bar `range>3 ATR` 或止损距离 `>2 ATR` 时不追入。

```text
if trend_context(direction) and consecutive_trend_bars(direction, 1..3):
    wait up to 2 completed bars for follow-through
    if follow_through(direction):
        enter direction on next executable price
        target_1 = prior_extreme
        target_2 = spike_measured_move or 2R
    elif strong_opposite_close_reclaims_signal_bar():
        mark FAILED_TREND_BAR
```

### TRENDS-C02-S02：孤立趋势 Bar 假突破

- 类型：完整反向策略。
- 英文依据，PDF p.103–104：Figure 2.4 的强多头趋势 bar 突破 doji 区域但没有跟进，下一 bar 仅高一个 tick后收近低点，形成多头陷阱。
- 上下文：区间、弱趋势、成熟趋势末端；禁止在刚启动且已有连续跟进的强趋势中逆势。
- Setup：大趋势 bar 突破近期边界 `0.05–0.50 ATR`，但后续 1–3 bars 未出现同向跟进。
- 触发：
  - 后续 bar 创轻微新极值后反向收盘；或
  - 收盘回到突破边界内，并突破暂停/反转 bar 的反向极值。
- 入场：向原突破反方向 stop entry。
- 止损：失败突破极值外 1 tick。
- 目标：突破起点、区间中点、区间另一端；若同方向第二次突破尝试也失败，则保留一部分仓位寻找两段移动。
- 失效：原方向重新突破且出现连续跟进。

| 参数 | 宽松 | 基准 | 严格 | 来源 |
|---|---:|---:|---:|---|
| 跟进等待 | 3 | 2 | 1 bar | `PROXY` |
| 允许的轻微新极值 | 0.25 | 0.10 | 0.05 ATR | `PROXY`；图例为 1 tick |
| 回收突破 bar 比例 | 40% | 60% | 80% | `PROXY` |
| 反向 bar `body_frac` | 0.40 | 0.55 | 0.70 | `PROXY` |

### TRENDS-C02-S03：买卖压力累积因子

- 类型：状态/过滤组件。
- 英文依据，PDF p.96–97、107：同向实体的数量和大小、bar 底部/顶部影线以及新极值后的反向 bar 会累积成买卖压力。
- 用途：发现现有趋势减弱、区间形成或反向趋势概率上升；不单独触发交易。

```text
bull_pressure_component(i) =
    + w1 * I(bull trend bar) * clipped_rel_body
    + w2 * lower_tail_frac
    + w3 * I(low < prior_swing_low and close_pos >= 0.5)
    + w4 * I(two_bar bull reversal)

bear_pressure_component(i) = symmetric_definition

net_pressure(t) = EWMA(bull_pressure - bear_pressure, half_life)
pressure_change = net_pressure(t) - net_pressure(t-lookback)
```

- 参数：半衰期 `3–20 bars`，比较窗口 `5–30 bars`，各组件权重先等权再用训练集正则化；均为 `EMPIRICAL`。
- 状态转换：
  - bear trend 中 `net_pressure` 上升但仍为负：预计先转为区间，不直接判定牛趋势。
  - bull/bear pressure 穿越零且反向突破有跟进：允许反向趋势候选。
  - 新低后 1–2 bars 内持续出现 bull bar 或显著下影：下调空头趋势强度；Figure 2.6 的文字说明属于此类。
- 禁止：用整段走势结束后的最高/最低点反向标记压力；所有 swing 必须实时确认。

### TRENDS-C02-S04：Trending Dojis

- 类型：完整顺势策略。
- 英文依据，PDF p.97、101：单个 doji 表示平衡，但连续 doji 若高点、低点和收盘同向推进，表示趋势压力。
- Setup：连续 `3–8` 根 `DOJI_LIKE`，其中至少 `60%–100%` 同时满足：
  - bull 版本 `close[i]>close[i-1]`；
  - `high[i]>=high[i-1]`；
  - `low[i]>=low[i-1]`；
  - bear 版本完全对称。
- 触发：突破该组 doji 的顺势边界，并有一根顺势收盘。
- 入场：突破后下一 bar，或首次小回撤后的 stop entry。
- 止损：doji 序列另一端，若大于 2 ATR 则跳过。
- 目标：序列高度测量移动、1R/2R。
- 失效：向反方向突破整个序列并跟进。
- 对照组：完美 `open=close` 定义 vs 相对实体 doji 定义；验证作者认为完美定义无用的主张。

### TRENDS-C02-S05：高潮—暂停—延续/反转状态机

- 类型：状态机，包含延续与反转两个分支。
- 英文依据，PDF p.94–95：高潮结束于第一根暂停 bar；高潮不等于反转，反转还需要相反方向的突破。

#### 高潮候选

- 1–5 根同向趋势 bars。
- 累计净移动 `1.5–5 ATR`，或最后 bar range/实体处于滚动 `80%–99%` 分位。
- `rel_body` 连续扩大，或短窗口斜率显著高于前一窗口。

#### 暂停确认

第一根满足任一条件的 bar 结束高潮序列：doji、inside bar、明显同向上/下影、小实体，或反向趋势 bar。

#### 分支 A：延续

- 暂停后 1–3 bars 再次同向突破高潮极值并跟进。
- 只允许回撤后顺势入场，不在高潮末端直接追价。
- 止损放在暂停结构另一侧；目标为新极值和高潮高度 `0.75–1.25` 倍。

#### 分支 B：高潮反转

- 必须出现反向趋势 bar/反向 spike，且突破暂停结构。
- 入场为反向突破或其首次回测。
- 止损放在高潮最终极值外。
- 目标为 1R、EMA、高潮起点；强反转保留至两段移动。

#### 分支 C：双向交易

若两个方向都没有跟进，状态设为 `RANGE_AFTER_CLIMAX`，禁止继续按高潮方向追价，改用区间策略。

### TRENDS-C02-S06：成熟趋势末端的大 Bar 反转

- 类型：完整反转策略；S05 的严格子集。
- 英文依据：
  - PDF p.104：持续 30 bars 或更多且少有回撤的空头趋势中，大空头 bar 常是卖出真空和衰竭高潮。
  - PDF p.106：在支撑附近出现该形态后，作者预期修正至少两腿、至少 10 bars，并至少略高于均线。
- 上下文：
  - 趋势年龄 `AUTHOR=30+ bars`；测试范围 `20–60 bars`。
  - 回撤稀少：过去趋势移动中最大反向回撤小于 `0.5–1.5 ATR`。
  - 价格到达事前已定义的支撑/阻力或测量移动目标。
- Setup：末端出现异常大顺势 bar，range 位于滚动 85%–99% 分位，最好连续实体扩大。
- 触发：
  - 激进版本：大 bar 收盘按市价反向，作为高风险对照；
  - 基准版本：下一 bar 形成反向/inside bar并突破；
  - 严格版本：失败突破或两 bar 反转确认。
- 止损：高潮极值外 1 tick。
- 目标：
  - `AUTHOR`：至少 10 bars、至少两腿、至少略穿 EMA；这是待验证主张而非保证。
  - 量化目标：EMA、1R、2R、第二腿结束，分别统计。
- 失效：大 bar 后继续出现 1–2 根同向强跟进；取消逆势挂单。

```text
if trend_age >= age_threshold
   and shallow_pullbacks
   and at_predefined_level
   and extreme_trend_bar:
       wait_for_reversal_confirmation()
       if confirmed:
           enter_countertrend
           evaluate targets = {EMA, 10 bars, two legs, 1R, 2R}
```

### TRENDS-C02-S07：安静期后的强 Spike 趋势恢复

- 类型：完整顺势策略。
- 英文依据，PDF p.104：Figure 2.4 的安静期后出现多个不重叠的大空头实体，作者将其视为高概率空头趋势恢复和测量移动候选。
- Setup：
  1. 先有明确趋势方向。
  2. 随后 `10–40 bars` 低波动/高重叠盘整，range 处于滚动 20%–50% 分位。
  3. 原趋势方向出现 2–4 根大趋势 bars，至少两根相邻实体重叠小于 0%–25%。
- 入场：第二或第三根趋势 bar 收盘后下一可成交价；风险过大时仅按固定账户风险缩仓，不能扩大账户风险。
- 止损：最后入场信号 bar 另一端；另测整个 spike 起点止损。
- 目标：从 spike 首 bar 开盘/高低至末 bar 收盘/高低形成多个事前固定的测量投影；不得事后选择表现最好的锚点。
- 管理：出现下一根强同向 bar后，可比较原始止损、移至盈亏平衡、移至该 bar 极值外三种方案。
- 失效：spike 后立即出现强反向 bar并收回超过 60%，转为 S05 高潮候选。

| 参数 | 搜索范围 | 基准 | 来源 |
|---|---:|---:|---|
| 安静期 | 10–40 bars | 20 | `PROXY` |
| spike bars | 2–4 | 3 | `PROXY` |
| 大 bar range 分位 | 0.70–0.95 | 0.85 | `PROXY` |
| 相邻 bar 最大重叠 | 0%–30% | 15% | `PROXY` |
| 测量移动倍数 | 0.75–1.25 | 1.00 | `AUTHOR` 概念；范围为 `PROXY` |

### TRENDS-C02-N01：禁止依赖人工反应速度的超低周期反转

- 类型：`NEGATIVE` 实现约束。
- 英文依据，PDF p.94、105–106：作者明确认为在人类无法及时处理的低周期上与计算机竞争是错误；Figure 2.5 的最后一分钟包含 33 根 100-tick bars。
- 规则：如果 `decision_latency + order_latency` 大于信号有效期的 25%–50%，或只有聚合 OHLC 而形态需要逐笔顺序，则策略标记为不可实现，不进行理想化成交回测。
- 若自动化系统研究同一形态，必须使用 tick/盘口级数据、真实延迟、排队和滑点模型；不能把作者对人工交易的否定误写成任何自动化频率都不可行。

## 4. 原文主张覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 91–92 | bar 分为趋势 bar 和近似 doji；分类相对且主观 | 第 2 节 |
| 92 | 大实体通常更强，但成熟移动后的极大实体可能是高潮 | S01、S05、S06 |
| 93 | 连续强趋势 bars 通常产生进一步极值 | S01 |
| 93–94 | 强逆势 spike 需要下一 bar 跟进；没有跟进常变成旗形 | S01、S02、S05 |
| 94–95 | 高潮结束于暂停 bar；高潮不等于反转 | S05 |
| 95 | 理想趋势 bar 的实体与近 5/10 bars 中位实体相当或更大 | 第 2 节 |
| 96–97 | 同向实体、影线和新极值拒绝形成累积压力 | S03 |
| 97–101 | doji 是单 bar 区间，但 trending dojis 仍表示趋势 | S04 |
| 98–99 | 极大趋势 bar 后的相反 bar可形成两 bar反转 | S05、S06 |
| 101–102 | doji 是否可交易取决于上下文 | S04；禁止单独交易所有 doji |
| 103–104 | 无跟进的趋势 bar 突破可能成为陷阱 | S02 |
| 104 | 安静期后多个不重叠趋势 bars 支持趋势恢复和测量移动 | S07 |
| 104–106 | 30+ bars 成熟趋势末端的大 bar可能是衰竭高潮 | S06 |
| 105–106 | 人类不应在信息速度明显不足的极低周期竞争 | N01 |
| 107–108 | 新极值后的反向 bar/长影表示累积反向压力 | S03 |

## 5. 回测与验收

### 5.1 必须分层

- 趋势 bar 位于：趋势启动、趋势中段、30+ bars 成熟趋势、交易区间。
- 单根 vs 连续趋势 bars；有跟进 vs 无跟进。
- 正常 bar、80%–95%分位大 bar、95%–99%分位极端 bar。
- doji：完美定义、相对实体定义、trending doji 序列。
- 高潮后：延续、反转、区间三种真实结果，不能只标反转样本。

### 5.2 关键标签必须无前视

- “趋势年龄”只能从当时已确认的趋势起点计算。
- 支撑/阻力和测量目标必须在高潮 bar 形成前存在。
- `leg count` 和 pivot 只能在确认后使用，回测成交相应延后。
- “异常大 bar”的分位数只用历史窗口，不包含未来数据。

### 5.3 验收指标

- S01 验证连续趋势 bars 后再创新极值的条件概率和达到新极值前的 MAE。
- S02 比较即时追突破与等待跟进，并统计第二次失败后两段反向移动概率。
- S05 报告高潮后三分支比例，不能把暂停自动计为反转成功。
- S06 单独检验作者的 `30+ bars / 10+ bars / 至少两腿 / 穿越EMA` 数值主张。
- S07 同时报告不同测量锚点，锚点选择规则必须在入场时冻结。
- N01 使用真实延迟和成交模型；无法获得相应数据时结论必须是“不可检验”，而不是“盈利”。
