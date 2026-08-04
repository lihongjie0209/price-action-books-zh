# 第 15 章：容易形成突破与反转的日内关键时点

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/24-ch15-key-inflection-times-of-the-day-that-set-up-breakouts-and-reversals.md`
- PDF 页码：281–285
- 图表：Figure 15.1–15.3；正文与图注足以定义规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 时间与事件定义

- 原文时刻为美国太平洋时间：07:00、07:30、11:00、11:30、12:00，核心窗口为11:00–11:30附近。
- 数据必须保存带IANA时区的时间戳；默认使用`America/Los_Angeles`重建当地钟点，自动处理PST/PDT。禁止把全年固定UTC偏移称为PST。
- 每个锚点主窗口为前后1根bar；5分钟数据即 `±5min`，稳健性测试 `±10/15min`。
- 时间仅是条件变量，不是独立信号；必须与trend/range、stop run、failed breakout和实际signal bar结合。

```text
key_time_window(t, h) = local_time(t) within h ± K bars
late_window = 11:00–12:00 local, primary_center = 11:30
stop_run = 突破关键结构后在1–3bars内收回
```

## 2. 规则卡

### RANGES-C15-S01：强趋势日午间 Countertrend Stop Run Fade

- 类型：完整顺势恢复策略。
- 依据，PDF p.281–283：强趋势日常在11:00–11:30出现猛烈逆势panic/stop run，突破重要trend line后失败，随后旧趋势恢复并测试/突破极值。
- Setup：11:00–12:00窗口前已确认strong trend；逆势spike `1–4bars` 位移≥`1.0–2.0ATR`，突破minor/major line、EMA或prominent swing。
- 确认：突破在 `1–3bars` 内失败，出现顺旧趋势reversal bar、第二入场、double top/bottom flag或MA-gap fade。
- 入场：确认signal顺趋势极值外1tick stop；禁止只因到11:30而limit猜反转。
- 止损：stop-run最终极值外；按完整距离缩仓。
- 目标：旧趋势极值、1R/2R；强恢复保留部分仓至收盘。
- Clear Always-In reversal及follow-through成立时不fade，转S03。

### RANGES-C15-S02：Trading Range 日午间对侧假突破

- 类型：区间边缘失败突破策略。
- 依据，PDF p.281–282、284–285：价格在一侧停留数小时后，午间可能突然扫过另一侧并失败，陷入新突破者、洗出原持仓；range日多收于中部。
- Setup：11:00–12:00前确认range，持续≥`20bars`，价格此前 `8–24bars` 多在range一半区域。
- Trigger：突破对侧边界≥1tick/`0.10ATR`后 `1–3bars` 收回；优先第二次失败或High/Low 2。
- 入场：reclaim/第二信号朝range内部极值外stop。
- 止损：假突破最终极值外。
- 目标：range中点为第一目标，对侧边缘为扩展目标；接近收盘时不强制期待完整跨越。
- 若强breakout+follow-through并形成新Always-In方向，停止fade。

### RANGES-C15-S03：关键时点的真实反转 / Breakout Follow-through

- 类型：真假突破分类器与策略。
- 依据，PDF p.282–283：07:00附近的反转有时失败并成为首次顺势pullback，有时成功形成三bar spike和channel；时间本身不决定方向。
- 候选窗口：07:00、07:30及预注册经济事件时刻 `±1bar`。
- 真突破条件：breakout bar≥`1ATR`、收盘位于方向端25%，随后1–2bars至少一根follow-through且不收回结构。
- 入场：首个breakout pullback或第二入场；止损在breakout结构另一侧。
- 目标：spike高度measured move、1R/2R、后续channel。
- 无follow-through并迅速回结构内则归S04，不得事后用新闻解释重新分类。

### RANGES-C15-S04：关键时点首次 Pullback / Failed Reversal

- 类型：顺原趋势策略。
- 依据，PDF p.282–283、285：trend-from-open在07:00的一bar反转可能只是当天首次pullback，失败后产生spike/channel。
- Setup：关键时点前为trend-from-open，尚无已确认pullback；逆势breakout在 `1–2bars` 内失败。
- 入场：顺原趋势reclaim bar极值外stop，或首次High/Low 1/2。
- 止损：关键时点stop-run极值外。
- 目标：日内旧极值、opening spike高度、1R/2R。
- 若关键时点逆势spike满足S03真反转，不执行本规则。

### RANGES-C15-S05：首次 MA Gap Bar 与 Late Stop Run 共振

- 类型：共振过滤策略。
- 依据，PDF p.282–284：午间stop run常在多次EMA测试后形成首个错误侧MA gap bar；首个此类突破往往失败并恢复趋势。
- 使用第14章实时定义的first MA gap bar；不得因本章案例修改定义。
- 当first gap事件落在11:00–12:00且同时满足S01 stop run，signal score增加但只生成一笔交易。
- 第一入场失败允许第二入场；最多两次，止损为完整stop-run极值。
- 目标仍按S01；单独报告有/无时间共振，以检验时点是否提供增量信息。

### RANGES-C15-S06：双向 Trap 后的下一信号

- 类型：条件scalp/swing策略。
- 依据，PDF p.284–285：range先向一侧假突破再向另一侧假突破，套住/洗出双方后，下一合格信号常至少产生scalp。
- 在最多 `10bars` 内确认两侧边界均发生failed breakout；事件顺序可互换。
- 下一信号必须位于range有利边缘，或为第二次突破失败/强breakout pullback。
- 入场：signal bar极值外stop；止损在对应range边界外。
- 目标：至少1R或range中点；强signal与足够空间时扩展到对侧。
- 两侧假突破事件确认前不得回填“双向trap”标签。

### RANGES-C15-S07：Late Stop Run 后的次日首小时反向候选

- 类型：跨日条件反转研究方案。
- 依据，PDF p.281–283：午间stop run常突破主要trend line，随后旧趋势创新极值；这组合可能为次日首小时反向交易铺垫。
- Day D条件：S01成功、major trend line被破坏、之后测试/形成新旧趋势极值。
- Day D+1仅在开盘首 `6–12bars` 寻找该极值附近的major reversal、second entry或strong opposite breakout。
- 入场：次日独立确认signal；不得隔夜仅凭Day D形态预埋逆势仓。
- 止损：次日reversal最终极值外；目标为opening range另一侧、EMA、1R/2R。
- 跨日corporate action、session gap与合约换月必须清洗；与普通次日反转基准比较增量。

### RANGES-C15-N01：时钟不是因果入场信号

- 类型：`NEGATIVE`。
- 依据，PDF p.281–285：原文描述“often/less often”，并反复以价格失败与趋势背景确认；谣言或新闻内容不重要。
- 禁止在07:00、07:30、11:30自动反手或自动开仓。
- 不使用无法复现的“机构制造谣言”作为特征；只使用可观察的价格、成交量（若有）和预先记录的事件时间。
- 时点效果必须与同一日内位置的随机/邻近窗口基准比较，并做多重检验修正。

### RANGES-C15-N02：Late Tight Range 后降低趋势腿目标

- 类型：退出约束。
- 依据，PDF p.283–284：午后趋势恢复若起得晚且此前为大重叠、长尾的tight range，后续腿往往小于开盘趋势腿。
- 若11:00后启动且此前≥`10bars` overlap≥0.65、平均tail ratio≥0.45，则标记`late_tight_range`。
- 第一目标缩为range高度或1R，至少平仓 `50–75%`；剩余仓才追踪至收盘。
- 不把开盘腿高度机械投影为最低目标；只作为扩展统计。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 281–282 | 关键时点、强趋势panic、major-line stop run、range对侧假突破 | 定义、S01–S02、S07 |
| 282–283 | late MA-gap fade、07:00真假反转、spike/channel | S03–S05 |
| 283–284 | late bull trap、first gap、弱动量trap与追赶 | S01、S05、N02 |
| 284–285 | range日11:30 trap、两次失败、双向trapped traders | S02、S06 |

## 4. 回测验收

- 原始UTC时间转换为`America/Los_Angeles`并逐日验证DST；输出每年PST/PDT样本数。
- 时点窗口至少测试 `±5/10/15min`，主参数在样本外固定。
- 每笔交易保存触发它的价格条件；只有时间、没有价格确认的记录必须为零。
- S01/S02/S03互斥分类：trend stop-run fade、range fade、true breakout只能有一个主标签。
- 对比关键窗口与相邻非关键窗口的条件胜率/期望值，控制trend strength、时段和波动率。
- 经济事件数据若不可得，策略仍应可由价格运行；若使用事件日历，只用当时已公布时间。
- 跨日S07单独报告隔夜gap影响，不与日内S01收益合并。
- Figure 15.1–15.3只作章节例证，不作参数拟合或绩效证据。
