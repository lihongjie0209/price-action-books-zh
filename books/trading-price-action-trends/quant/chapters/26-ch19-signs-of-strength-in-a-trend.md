# 第 19 章：趋势强度的迹象

## 元数据

- 英文来源：`books/trading-price-action-trends/en/chapters/26-ch19-signs-of-strength-in-a-trend.md`
- PDF 页码：339–350
- 图表：Figure 19.1–19.3；正文与图注已完整定义量化关系，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 逐 Bar 趋势强度模型

本章的特征不能用全日数据一次性打标签，必须在每根bar收盘时更新：

```text
body_overlap = overlap(body[t], body[t-1]) / min(body_range[t], body_range[t-1])
directional_bar_rate = mean(sign(close-open) == trend_direction, N)
tail_ratio = (upper_tail + lower_tail) / max(range, tick)
pullback_depth = countertrend_move / session_range_so_far
ema_gap_run = consecutive bars not touching EMA
opposite_ema_closes = consecutive closes across EMA against trend
```

建议把特征分为四组，避免同一事实重复加分：

| 组 | 正向特征 | 初始范围 | 来源 |
|---|---|---:|---|
| 结构 | 同向trending highs/lows、突破多个阻力/支撑 | 2–4个连续swing | `AUTHOR` + `PROXY` |
| Bar | 同向trend bar多、实体重叠少、尾部小 | `N=5–20` | `AUTHOR` + `PROXY` |
| 回调 | 小、少、横向、反转无跟进、重复两腿 | 深度<session range的20–35% | `AUTHOR` + `PROXY` |
| Gap/EMA | opening gap、measuring gap、micro gap、20 gap bars | 见S02/S03 | `AUTHOR` |

各组先缩放到0–1，再等权或用训练期权重求`trend_strength`。初测：`>=0.70 STRONG`、`>=0.85 RUNAWAY`、`<0.50 WEAKENING`，阈值均为`PROXY`。

## 2. 规则卡

### TRENDS-C19-S01：趋势强度综合评分与顺势门控

- 类型：状态组件。
- 依据，PDF p.339–341：趋势越强，方向性高低点、同向bar、低重叠、小尾部、小而稀少回调等迹象越多；迹象越多越应专注顺势。
- 每根bar仅用当时已知的最近 `5/10/20bars` 和已确认swings计算四组分数。
- `STRONG`：只启用顺势入场；普通逆势signal转换为S04的潜在失败信号。
- `RUNAWAY`：允许无形态的小仓市价参与，并启用S06执行约束。
- `WEAKENING`：禁止旧swing追价，转S07监控双向交易。
- 评分输出需包括每组贡献，不能只保留不可解释的单一标签。

### TRENDS-C19-S02：Gap 与不重叠突破测试的强度特征

- 类型：特征与延续目标组件。
- 依据，PDF p.339–343：大opening gap、初始breakout gap、measuring gap及micro measuring gap均是强度迹象；大缺口若早盘不反转，常形成趋势并收在极值附近。
- `opening_gap = abs(open - prior_session_close)/ADR20`；初测大gap为 `0.25–1.00ADR`（`PROXY`）。
- bull measuring gap：突破后pullback low仍高于冻结的breakout point；bear对称。
- bull micro gap：强bull bar前一bar high低于后一bar low；相等/1tick容差作为宽松版本。
- 大gap continuation仅在opening range未强势回补、首bar同向且向gap方向突破时加分。
- 测量目标：以gap前推进或opening range高度的 `0.75/1/1.25×` 测试；目标在gap确认时冻结。
- Gap特征不单独成交，必须与S01方向和S05入场结合。

### TRENDS-C19-S03：EMA 单边控制与 20 Gap Bars

- 类型：强度特征与顺势回测策略。
- 依据，PDF p.340–346：连续20bars不触EMA、以及EMA反侧没有连续两个trend-bar收盘，都是强趋势特征；首次EMA回测常有顺势买卖盘。
- `ema_gap_run>=20` 时标记强度事件；严格版本要求极值不触EMA，宽松版本要求收盘不穿EMA。
- 若趋势反侧连续收盘数 `<2`，维持单边控制；连续2bars只是弱化信号，不自动判反转。
- 首次EMA回测入场：limit于EMA顺势侧1tick，或等待High/Low 2 stop。
- 止损：完整回调swing外。
- 目标：趋势旧极值、1R/2R；若出现first MA gap bar后再恢复趋势，标记“潜在最终腿”，减少新增追价仓位。
- 失效：EMA反侧强spike、跟进并突破主要trend line。

### TRENDS-C19-S04：逆势反转失败转换为顺势入场

- 类型：完整顺势失败形态策略。
- 依据，PDF p.339–345、346–347：强趋势中最漂亮的反转bar和大bar常逆势并诱捕交易者；wedge等反转通常无跟进、失败并成为顺势flag。
- Setup：S01为STRONG/RUNAWAY；出现逆势reversal、wedge、trend-line break或两三bar逆向spike。
- 不在第一次逆势signal入场；等待其触发失败或缺少跟进。
- 多头触发：bear signal/逆向spike的保护性止损价被向上突破；空头对称。
- 入场：在逆势交易者理论止损处 `1tick–0.10ATR` 顺势stop entry。
- 止损：失败反转极值外。
- 目标：趋势旧极值、1R/2R、余仓趋势跟踪。
- 逆势spike通常仍可能有第二腿；若第一腿实体总长≥ `1ATR`，优先等待第二腿完成后再入场。

### TRENDS-C19-S05：强趋势的重复两腿回调

- 类型：完整顺势pullback策略。
- 依据，PDF p.341、343–345：强趋势经常反复形成两腿回调；High/Low 1适用于spike，High/Low 2及breakout test提供顺势机会。
- Setup：S01≥STRONG；回调由两个可实时识别的逆向推进组成，整体保持在主要趋势结构内。
- 触发：第二腿结束的High 2/Low 2、double bottom/top flag、wedge第三推进或breakout test失败。
- 入场：signal bar外stop。
- 止损：回调极值外。
- 目标：旧极值、1R/2R；顺势仓位以swing为主，仅小部分scalp。
- tight trading range中的信号降级：等待明确顺势突破或range边缘，不在中部反复下单。

### TRENDS-C19-S06：Runaway Trend 的参与和周期约束

- 类型：执行策略。
- 依据，PDF p.339–341、348–349：runaway趋势可能多bars无回调、bar大小适中且尾部小；等待limit常无法成交，趋势会迫使交易者追价。
- Setup：S01≥RUNAWAY，最近 `3–5bars` 同向且prior close的limit成交率低。
- 入场选择：小仓市价/收盘、pause bar突破、one-bar pullback；仓位 `0.20–0.50` 标准规模。
- 止损：最近spike起点或结构swing外，按风险距离缩仓。
- 可选低周期仅限预先固定的3分钟完整数据，用于增加顺势pause信号；基础模型坚持原周期。
- 禁止临时切到1分钟寻找逆势setup；其速度与双向噪声会干扰主策略。
- 已有swing仓位时，新增scalp不得使总开放风险超过预算。

### TRENDS-C19-S07：强趋势衰减与 Spike→Channel→Range 转换

- 类型：状态转换与退出组件。
- 依据，PDF p.341、344–345、348–349：趋势会由spike转channel再转range；旧极值处由追价变成止盈/逆向scaling，回调加深、双向交易增加。
- 弱化特征：
  - S01跌破0.50或较峰值下降 `0.25+`；
  - pullback持续bar数/深度超过此前中位数 `1.5–2倍`；
  - EMA反侧连续2次收盘；
  - trend-channel-line过冲后不再强跟进；
  - 旧极值两次突破失败；
  - 反向压力bar比例升高。
- 满足 `3/6` 标记`WEAKENING`，停止S06和旧swing breakout追价，已有仓位收紧至最近结构swing。
- 形成双向swing和高重叠后标记`RANGE`；只有反向spike+跟进+结构反转才标相反趋势。
- “crowded trade”不能用事后参与者叙述直接量化，只以上述价格代理实现。

### TRENDS-C19-N01：强趋势中的逆势信号名称与使用限制

- 类型：`NEGATIVE`。
- 依据，PDF p.343–346：强bull trend中的所谓Low 1并不是有效short setup，强bear trend对称；没有先前强逆向腿和重要trend-line break时，只能看作顺势机会。
- STRONG状态中禁止因单个新高/低反转bar、channel overshoot或第一entry逆势。
- 允许逆势swing至少需要：明显反向spike、突破约20bars的主要trend line、跟进、第二信号。
- 即使满足第二信号但仍未翻转Always-In，逆势模型也只按scalp统计，并不得妨碍S04/S05顺势信号。

### TRENDS-C19-N02：弱顺势 Signal Bar 不是趋势弱的证据

- 类型：`NEGATIVE`。
- 依据，PDF p.339–341、346–347：最强趋势中的顺势signal往往很弱，正因交易者等待漂亮信号而持续追价；逆势bar反而常更漂亮。
- 禁止把signal bar外观作为S01的单一否决条件。
- 必须分别记录setup context和signal-bar quality，检验弱signal在高trend-strength下的条件绩效。
- 不得只选图上显眼的大顺势bar回测，这会产生严重选择偏差。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 339–341 | 强趋势特征清单、弱顺势signal、反转失败、20 gap | 第1节、S01–S06、N02 |
| 341 | runaway执行、周期选择、趋势逐步衰减 | S06、S07 |
| 342–345 | 大gap趋势日、两腿回调、EMA与失败反转案例 | S02–S05、N01 |
| 346–347 | 最漂亮bar常逆势、EMA单边控制、弱signal陷阱 | S01、S03、S04、N02 |
| 348–350 | prior-close limit不成交、spike/channel及次日反转 | S06、S07 |

## 4. 回测验收

- 每根bar保存四组原始特征、分组分数和总分；不得用收盘后的当日极值或最终趋势长度。
- 使用滚动训练/验证确定权重，并与等权评分对比，防止多特征过拟合。
- 检查高度相关特征，只在组内聚合，避免“无回调、20 gap、EMA单边”被重复计权。
- S02分别报告opening、measuring和micro gap的增量，不将三者混为一个结果。
- S04统计逆势signal触发、无跟进、失败、成为flag和最终趋势翻转的完整条件概率。
- S05按一腿/两腿/三腿及tight-range上下文分层。
- S06模拟实际未成交limit和追价滑点，不得假设prior close总能成交。
- S07报告状态转换延迟和错误退出成本。
- Figure 19.1–19.3仅作章节例证，不作参数拟合或绩效证据。
