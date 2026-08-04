# 第 8 章：基于缺口与交易区间的测量移动

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/16-ch08-measured-moves-based-on-gaps-and-trading-ranges.md`
- PDF 页码：207–214
- 图表：Figure 8.1–8.5；正文与图注已完整说明，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 四种投射

```text
gap_mid = (gap_lower + gap_upper) / 2
gap_target = gap_mid + direction * abs(gap_mid - leg_origin)
range_target = breakout_edge + direction * range_height
thin_area_mid = (breakout_point + first_pullback_extreme) / 2
```

- 传统gap：相邻bars价格不重叠。
- Intraday thin area：breakout point与首次pause/pullback极值之间的低重叠区域。
- Negative gap：pullback轻微穿过breakout point，数学gap为负。
- Trading range：冻结上下边界后的垂直高度投射。
- 所有目标为近似zone而非精确价格；默认容差 `0.10–0.30ATR`。

## 2. 规则卡

### RANGES-C08-S01：Traditional Gap Midpoint 测量移动

- 类型：目标与持仓组件。
- 依据，PDF p.207–209、211–212：方向确信较强时，传统gap中点常成为趋势腿中点；接近投射处常有止盈、pause或反转。
- Gap确认时冻结上下边界和midpoint；leg origin取gap前当前趋势腿已确认起点。
- 从origin到midpoint的距离向趋势方向投射 `0.75/1/1.25×`。
- 已有顺势仓位至少持有部分至最近目标；到zone分批止盈。
- 目标反复差1–3ticks不视为不同模型；按ATR/tick容差统一判定。
- 若gap先被强势回补并Always-In翻转，关闭原方向目标。

### RANGES-C08-S02：Intraday Thin-Area Measuring Gap

- 类型：breakout测量目标组件。
- 依据，PDF p.207–210、213–214：intraday常无传统gap，但breakout point至首pause/pullback的thin area同样可用；若边界不清，可用breakout bar中点。
- Breakout point在事件前冻结；依次等待首个small trend bar、doji、逆向bar或pullback，其逆向extreme为thin-area另一边。
- 多根连续breakout bars时，首pause前不得提前固定gap上/下边界。
- 边界不清版本：breakout bar body midpoint，必须单独标记`FALLBACK_MIDPOINT`。
- 目标按第1节gap公式；顺势入场沿breakout pullback规则，gap本身只管理目标。
- 首pullback更新thin area后冻结，不得随每次后续pullback重画同一事件。

### RANGES-C08-S03：Negative Gap 与 Range-Height 备选

- 类型：弱目标/备选层级组件。
- 依据，PDF p.207–210：pullback略穿breakout point仍可投射negative gap，但可靠性较低；这种情况下range height目标往往更常用。
- Negative定义：方向标准化的`test_extreme-breakout_point<0`，允许穿越 `0–0.25ATR`。
- 同时生成：negative-gap midpoint目标、breakout前range height目标、当前leg起点目标。
- 启用顺序按距离从近到远；默认range-height优先级高于negative-gap精确投射，但两者均保存。
- 超过0.25ATR或强回到旧range时，关闭gap模型，仅保留range/reversal状态。
- 分别报告positive/zero/negative gap命中率，不能合并。

### RANGES-C08-S04：Trading Range Height Breakout

- 类型：完整顺势突破/目标策略。
- 依据，PDF p.208、210–214：多数交易者用prior range高度；突破flag/range后应swing部分顺势仓位至等高目标。
- Range至少由两个上边界和两个下边界测试确认；确认时冻结`H=upper-lower`。
- 入场：强breakout follow-through或breakout pullback，不在range内预判方向。
- 止损：回测极值/range内侧结构外。
- 目标：breakout edge外 `0.75/1/1.25H`，最近版本先启用。
- 到目标后减仓；若继续强spike，转更远目标/第7章spike模型。
- Breakout失败并返回range中部时关闭投射，不等待“最终必达”。

### RANGES-C08-S05：Developing Range Midpoint 的动态估计

- 类型：实时目标组件。
- 依据，PDF p.207–208、212–214：fat area/range中部代表两侧认可的价格，常近似整个腿的中点，但range展开时估计会变化。
- 每根bar用当前已知range high/low、成交时间中位价或volume profile POC三个版本估计中心。
- 每个版本带`known_at`，只从该bar后用于投射；最终range中心不得回填。
- Range确认突破后冻结最后实时midpoint，并从leg origin对称投射。
- 三种中心版本并行回测，若volume不可用则不伪造POC。
- 仅作目标，不在range中部产生交易。

### RANGES-C08-S06：目标到达后的 Countertrend 门控

- 类型：止盈与条件反转策略。
- 依据，PDF p.207–208、211–213：测量区适合顺势止盈；只有此前反向move已强到突破trend line且当前有好setup，才考虑逆势。
- 最低条件：目标zone到达 + 主要trend-line break已发生 + strong reversal/第二信号。
- 入场：反向signal bar外stop。
- 止损：最终趋势极值外。
- 目标：breakout point、EMA、两腿、1R/2R。
- 若无先前反向强度，只减仓并继续顺势，不裸fade目标。
- 高周期两腿完成可提高swing比例，但必须由已完成高周期bar确认。

### RANGES-C08-S07：目标的时段可达性过滤

- 类型：目标选择/退出组件。
- 依据，PDF p.214：尾盘巨大thin area可能来不及完成测量移动；仍应顺趋势交易，但不能把不可达目标用于持仓越过收盘。
- 估计目标距离与最近 `20–50bars` 顺势速度分布，计算预计到达bars。
- 若预计bars > session剩余bars的 `0.75–1.25倍`，标记`SESSION_INFEASIBLE`。
- 日内策略改用1R/2R、旧极值或收盘退出；不自动隔夜。
- 目标仍保存用于跨session研究，但隔夜版本独立计算gap风险。
- 不用日终已知低/高判断可达性。

### RANGES-C08-N01：Measured Move 只能提供方向指南

- 类型：`NEGATIVE`。
- 依据，PDF p.208、211–213：投射经常undershoot/overshoot，只是让交易者保持正确方向；单独到目标不足以反转。
- 禁止以“精确到tick”作为必要条件或策略优势证明。
- 禁止在没有S06反转证据时于目标挂裸逆势limit。
- 新闻叙事不参与目标选择；几何参数必须在事件时冻结。

### RANGES-C08-N02：强趋势中不能因近目标放弃顺势交易

- 类型：`NEGATIVE`。
- 依据，PDF p.211–214：强trend仍应只顺势，目标可被大幅overshoot；尤其没有trend-line break时，逆势只能scalp或不做。
- trend score≥0.80且未破主要trend line时，目标最多减 `25–50%`，保留余仓结构跟踪。
- 多个远目标不得成为无限持仓借口；止损和session退出仍有效。
- 反向交易若会妨碍顺势入场，完全过滤。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 207–208 | 传统gap、thin area、negative gap及range中点 | 第1节、S01–S05 |
| 208–210 | 目标指南、trend-line门控、最近目标优先 | S03、S06、N01 |
| 211–212 | 长周期止盈、gap回测及climax上下文 | S01、S06、N02 |
| 212–214 | range/flag投射、多个起点及尾盘不可达 | S02–S07、N02 |

## 4. 回测验收

- Gap/range边界、leg origin和midpoint均带`known_at`；最终图形不得回填。
- S01/S02/S03按传统、thin、fallback、negative定义独立报告。
- S03比较negative-gap与range-height在同一事件上的配对误差。
- S04 range必须在breakout前确认，不能用breakout后扩大的边界。
- S05保存每根bar的动态中心版本并做样本外比较。
- S06报告只止盈与止盈后反转的增量，验证trend-line门槛。
- S07只用当时速度分布和剩余bars判断可达性。
- Figure 8.1–8.5仅作章节例证，不作参数拟合或绩效证据。
