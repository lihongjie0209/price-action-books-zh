# 第 19 章：Dueling Lines——回调 Wedge 与趋势线交汇

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/28-ch19-dueling-lines-wedge-pullback-to-the-trend-line.md`
- PDF 页码：344–347
- 图表：Figure 19.1–19.3；正文与图注足以定义规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 定义

`Dueling Lines`是短期逆势回调的边界，与长期主趋势支撑/阻力在相近时间和价格交汇：

```text
short_line = pullback trend-channel line / wedge boundary
long_level = major trend line / trend-channel line / EMA / prior swing / measured-move level
price_confluence = abs(short_line(t)-long_level(t)) <= 0.10–0.30ATR
time_confluence = 预计交点距离当前 <= 0–5bars
```

- Bull趋势寻找支撑交汇，bear趋势寻找阻力交汇；方向镜像。
- “所有回调都在某种支撑/阻力结束”不可验证且容易事后解释，策略只接受入场前已明确记录的level。
- Trend lines只用当时已确认swing anchors；允许来自前一趋势的swing，但不得按未来反转效果挑线。

## 2. 规则卡

### RANGES-C19-S01：Wedge Pullback + 主趋势线交汇

- 类型：完整顺势策略。
- 依据，PDF p.344–346：最可靠版本是三推/wedge回调的channel line与主趋势line交汇，signal刺穿支撑/阻力后反转。
- Setup：明确trend regime；逆势回调完成3个push，且第三推进入`price_confluence`。
- Signal：bar穿过交汇level `1tick–0.20ATR`后收回，并以顺趋势body收盘；或下一bar形成H/L3。
- 入场：signal顺趋势极值外1tick stop。
- 止损：刺穿/第三推最终极值外。
- 目标：旧趋势极值、1R/2R、pullback channel起点。
- 强逆势breakout及follow-through使交汇失效，不继续机械fade。

### RANGES-C19-S02：Dueling Lines 的第二入场

- 类型：陡峭回调保守策略。
- 依据，PDF p.346–347：回调或反弹太陡时，交汇首反转后常需higher/lower-low/high breakout pullback，第二入场更合理。
- 强回调：最近 `3–6bars` countertrend位移≥`1.5ATR`、方向bodies≥60%或channel efficiency≥0.70。
- 首signal只标记candidate；等待短期channel被突破，并出现higher/lower-low（bear镜像higher/lower-high）第二信号。
- 入场：第二signal顺主趋势极值外stop；止损放第二测试最终极值外。
- 目标：旧极值、channel另一端、1R/2R。
- 若首breakout极强且Always-In已恢复，可用首次pullback而不强求固定形状。

### RANGES-C19-S03：主 Trend Line + 逆势 Channel Line 双线交汇

- 类型：两斜线共振策略。
- 依据，PDF p.344–347：上升bull trend line与下降bear channel line、或下降bear trend line与上升bull channel line相交，双重支撑/阻力提高交易价值。
- 两条线斜率符号相反，且均由至少两个已确认anchors构建。
- 交汇必须在当前至未来5bars内，价格距两线均≤`0.30ATR`。
- 入场使用S01或S02，不因存在两线额外重复开仓。
- 输出anchor年龄、line残差和交点距离，检验真正增量，不以线数量主观加仓。
- 一条线被强收盘突破并follow-through后，交汇candidate取消。

### RANGES-C19-S04：水平 Swing / Double Bottom-Top 变体

- 类型：水平支撑阻力策略。
- 依据，PDF p.344–345、347：长期level可为prior swing水平线，第三推在那里形成double bottom/top并恢复趋势或在range边缘反转。
- Level必须是入场前已确认prominent swing；测试容差 `max(1–3ticks, 0.10–0.30ATR)`。
- Trend版按S01顺势；trading-range版只在range外侧25%以内fade，目标range中点/对侧。
- Signal：第二测试收回、double-bottom/top signal或第二entry。
- 止损：水平level假突破最终极值外；目标旧极值、range中点、1R/2R。
- New low/high of day不是独立优势，必须与range位置及回收确认共存。

### RANGES-C19-S05：EMA / Measured Move 作为第二 Level

- 类型：可替代共振组件。
- 依据，PDF p.344–346：长期支撑阻力也可由EMA、measured move或其他预先可见关键价位提供。
- EMA使用固定20-period；measured move起点与高度必须在回调到达前保存。
- 第三推到任一level的 `0.10–0.30ATR` 范围且出现反转signal，生成候选。
- 多个level同时出现只提高score `0.05–0.15`，不生成重复交易；止损/目标沿用S01/S02。
- 对trend line、swing、EMA、measured move四类分别报告，防止大量候选level导致数据挖掘。

### RANGES-C19-S06：Containment-Line Penetration 后反转

- 类型：line reaction执行组件。
- 依据，PDF p.344–347：先选择能大致包含price action的channel line，再观察价格穿线后的反应；线不必完美。
- Line在signal前固定；penetration范围主测 `0–0.25ATR`。
- 穿线后 `0–2bars` 收回且方向close，触发S01；无收回或连续强收盘越线则判失败。
- Best-fit版本必须使用滚动历史残差最小化并锁定，不得手工选择事后最贴合的anchors。
- 保存overshoot大小与reclaim延迟，检验是否存在最佳反应区间。

### RANGES-C19-N01：不可用事后“任何支撑”解释所有回调

- 类型：`NEGATIVE`与防数据挖掘约束。
- 依据，PDF p.344–345：原文说明所有pullback都因某个level结束，但术语只保留给交易者能提前看见的支撑/阻力。
- 每个candidate在触线前保存`level_type, anchors, value, valid_from`；缺任一字段则不得入样本。
- 不允许反转后再从EMA、swing、trend line、measured move中选择最接近者。
- 报告每根bar平均活跃levels数；若过多，采用预注册优先级或多重检验修正。

### RANGES-C19-N02：线条共振不能覆盖强反向 Momentum

- 类型：`NEGATIVE`。
- 依据，PDF p.346–347：陡峭move即使到dueling lines也应等第二entry；首反转只适合动量较弱的pullback。
- Strong countertrend momentum满足S02时禁用S01首signal。
- 若突破long level≥`0.50ATR`并连续2根收盘在外侧，取消旧趋势方向交易并重判regime。
- 不能因两条以上线重合而扩大逆强动量仓位。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 344–345 | dueling lines定义、wedge三推、可见trend/swing/EMA等level | 定义、S01、S03–S05、N01 |
| 345–346 | 两条相反斜率线、历史swing anchors、陡峭回调第二entry | S02–S03、S06、N02 |
| 346–347 | containment line选择、overshoot反应、水平double-bottom变体 | S02、S04、S06 |

## 4. 回测验收

- 所有line/level保存`valid_from`，入场时核验已经可见；未来anchor使用数量必须为零。
- 同一事件只选择预注册优先级最高的主level，其余作为辅助特征。
- `price_confluence=0.10/0.20/0.30ATR`和`time=0/2/5bars`做样本外敏感性测试。
- S01/S02按countertrend momentum互斥分流。
- Penetration、exact touch、near miss分别统计，不删除没有完美相交的形态。
- Trend与trading-range样本分开；S04的新日内极值不得混入顺趋势S01结果。
- 手工线与算法线若并存，只以算法线作正式绩效，手工案例仅作质检。
- Figure 19.1–19.3只作章节例证，不作参数拟合或绩效证据。
