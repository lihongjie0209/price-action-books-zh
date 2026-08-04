# 第 21 章：Spike and Channel 趋势

## 元数据

- 英文来源：`books/trading-price-action-trends/en/chapters/29-ch21-spike-and-channel-trend.md`
- PDF 页码：357–390
- 图表：Figure 21.1–21.10；正文与图注已逐bar完整解释，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 阶段检测与状态机

```text
NEUTRAL -> SPIKE -> POST_SPIKE_PULLBACK -> CHANNEL
POST_SPIKE_PULLBACK -> RANGE | OPPOSITE_SPIKE
CHANNEL -> WITH_TREND_BREAK | COUNTERTREND_BREAK | RANGE
COUNTERTREND_BREAK -> BREAKOUT_PULLBACK -> CHANNEL_START_TEST -> RANGE
```

### Spike 候选

- 由1根或多根trend bars组成，净位移大、实体同向、重叠少，并使Always-In明确翻转或强化。
- 初测：净位移 `0.75–3ATR`，同向bar率 `0.60–1.00`，body overlap `<0.40`，持续 `1–10+bars`；均为`PROXY`。
- spike同时是breakout、gap和climax。opening gap也可作为spike，按 `gap/ADR20=0.20–1.00` 测试。
- spike在第一根pause/pullback前结束；若暂停后1–2bars立即恢复，保留“第二spike”和“更大尺度单一spike”两个标签。

### Channel 候选

- spike后的首次pullback为channel起点候选；趋势恢复后确认channel。
- 相比spike，channel通常斜率更缓、重叠/尾部/逆向bar/回调更多。
- tight channel只顺势；broad channel允许边缘逆势scalp。阈值沿用第15章并记录嵌套层级。
- post-spike pullback超过10bars时同时标记`RANGE_CANDIDATE`；原趋势方向突破略占优，但不得强制。

## 2. 规则卡

### TRENDS-C21-S01：Spike 突破参与

- 类型：完整顺势突破策略。
- 依据，PDF p.357–360、366：spike是突破和breakaway gap，强度越高，越可能随后形成走得更远的channel。
- Setup：spike detector触发，Always-In与spike同向，外层位置不存在立即阻挡的预登记关键位。
- 入场A：第一根强breakout bar收盘/下一bar市价；入场B：spike内 `0–0.25ATR` 小回撤；入场C：第一pause后的顺势stop。
- 止损：spike起点或breakout结构另一侧；按固定账户风险缩小仓位。
- 目标：spike等幅、1R/2R；余仓为预期channel保留。
- 失效：反向spike使Always-In翻转，或post-spike pullback完全回撤spike并有跟进。

### TRENDS-C21-S02：首次 Pullback 后的 Channel 启动

- 类型：趋势延续策略。
- 依据，PDF p.357–362：spike后pullback可仅1bar或数十bars；趋势恢复时通常以较低动能channel延续。
- Setup：S01 spike完成，出现首次pause/pullback，但未确认反向Always-In。
- pullback持续分层：`1–2/3–10/>10bars`；`>10` 同时进入range分支。
- 触发：pullback signal顺spike方向被突破，或breakout point/gap test失败。
- 入场：signal bar外stop；strong spike可在channel确认前小仓limit测试。
- 止损：pullback极值外。
- 目标：spike高/低、spike等幅目标、channel第三推进。
- 三分支必须互斥记账：恢复原趋势、形成range、反向spike翻转。

### TRENDS-C21-S03：Channel 阶段的顺势回调

- 类型：完整顺势channel策略。
- 依据，PDF p.357–361、363–367：channel是倾斜交易区间但仍有主方向；tight版本只顺势，prior bar、trend line和EMA回调均可入场。
- Tight入场：prior bar不利极值limit、High/Low 1/2、trend line/EMA测试、逆势signal失败。
- Broad入场：只在channel下/上边缘的顺势反转；逆势另列S04。
- 入场容差：边界或参考位 `0–0.25ATR`。
- 止损：最近channel swing外。
- 目标：旧趋势极值、对侧channel line、1R/2R。
- 限制：每个原始trend leg最多 `1–3` 个独立swing入场；limit成交必须模拟排队和滑点。

### TRENDS-C21-S04：Broad/Weak Channel 的逆势 Scalp 门控

- 类型：高级边缘scalp。
- 依据，PDF p.360、363–367：宽摆动channel可双向交易；重叠、逆向bar、doji和更大回调越多，机构越可能逆势，但多数交易者仍应等待明确反转。
- 仅在`BROAD/WEAK_CHANNEL`且two-sided score≥ `0.65`启用。
- 触发：trend-channel-line过冲、第三推进、测量目标/关键位处强反转，最好有第二信号。
- 入场：边缘反转bar外stop或预设limit；仓位为标准的 `0.25–0.50`。
- 止损：channel极值外；禁止无上限逆势scaling。
- 目标：中线、最近swing、`0.5–1R`，按scalp退出。
- 第二半session禁用逆势scale-in；剩余时间不足目标持有期时完全禁入。

### TRENDS-C21-S05：顺趋势方向 Channel Breakout 的失败

- 类型：高潮失败突破策略。
- 依据，PDF p.357–359、368–369：channel很少再次顺趋势强突破；发生后多在约5bars内失败，第二spike通常是climax并引发复杂回调。
- Setup：成熟channel后收盘顺趋势越过channel line `0.05–0.50ATR`。
- 等待窗口：`1–5bars`；突破有连续强跟进则不提前fade，最多延长观察到10bars。
- 失败触发：价格返回channel，形成强反向bar或突破bar后的第二反转信号。
- 入场：反向signal外stop；保守版等待breakout pullback。
- 止损：最终突破极值外。
- 目标：channel trend line、channel起点、两腿/10bars。
- 测量目标首先用于原趋势止盈，不因单独到达目标自动反转。

### TRENDS-C21-S06：反趋势 Channel Breakout Pullback

- 类型：完整反转策略。
- 依据，PDF p.358、360–364：channel最终通常逆原趋势突破；不追第一breakout，应等待pullback的lower high/higher low，目标为channel起点。
- Setup：反趋势breakout穿过channel trend line，至少一根实体≥ `0.5ATR` 或2bars净位移≥ `0.75ATR`。
- 第一breakout只确认候选，不成交。
- 触发：`1–10bars` 内回测形成lower high/higher low，且未重新进入旧channel深处。
- 入场：pullback signal外stop。
- 止损：pullback极值或旧channel极值外。
- 第一目标：channel起点；第二目标：spike gap/breakout point；到达后停止使用本形态预测。
- 失效：回测失败且旧趋势创新极值，转S03/S05。

### TRENDS-C21-S07：Channel 起点测试后的 25% 回摆

- 类型：目标完成后的反向策略。
- 依据，PDF p.358、361、364–365：回撤通常测试channel起点，随后至少向原趋势方向回摆约25%，尝试形成交易区间；常出现double bottom/top flag。
- Setup：S06到达冻结的channel start zone `±0.10–0.30ATR`。
- 触发：double bottom/top、第二信号或强反转bar。
- 入场：原趋势方向signal外stop。
- 止损：channel-start测试极值外。
- 目标：反向下跌/上涨腿的 `0.25/0.50` 回撤、range中点、1R。
- 25%为`AUTHOR`经验值，应与0.20–0.50敏感性比较；不假设恢复旧趋势。
- 完成此回摆后，市场进入普通range/breakout mode，本章状态机终止。

### TRENDS-C21-S08：Spike 与 Channel 的测量移动

- 类型：目标与止盈组件。
- 依据，PDF p.357、362、376、379、385–386：强spike常产生测量移动；可用spike开/低至收/高，或把spike视为leg 1、channel视为leg 2。
- spike完成时冻结四个高度候选：open→close、low→high、breakout point→spike extreme、spike净位移。
- 从spike终点/首次pullback极值投射 `0.75/1.0/1.25×H`。
- 多目标聚集在 `0.10–0.30ATR` 内视为confluence zone，但同源高度不重复加权。
- 用途优先级：顺势止盈 > 停止追价 > 有强反转结构时的逆势入场。
- 报告每个定义的命中率和首次命中时间，不事后选择最贴近最终高低点者。

### TRENDS-C21-S09：连续 Climaxes 变体

- 类型：复杂回调策略。
- 依据，PDF p.364–366、378–380、384–386：pause分隔的连续大趋势bar可视为spike-and-channel变体；两个climax后通常两腿、约10bars回调，三个时更大。
- climax bar：range或body≥最近20bars中位数的 `1.5–2.5倍`，收盘靠顺势端25%；阈值为`PROXY`。
- 连续定义：两个climax间隔 `1–5bars` pause/pullback，方向相同。
- 第一个只标记；第二个后停止顺势追价，等待反向signal或第二入场；第三个进一步提高反转评分。
- 入场：强反向bar外stop，保守版等待第一次回摆后的第二腿触发。
- 止损：最终climax极值外。
- 目标：第二climax起点、首次pause、EMA、两腿且约10bars。
- “10-bar, two-legged”表示比普通pullback更复杂，不要求恰好10bars或恰好两个最小尺度legs。

### TRENDS-C21-S10：反向 Spikes 的累积转向信号

- 类型：趋势衰减与状态转换组件。
- 依据，PDF p.367–368、370–372、387–388：强趋势中的首个反向spike通常只是flag；10–20bars内第二、第三个反向spike具有累积效应，可转range、深回调或反转。
- 记录滚动 `10–20bars` 中反向spike数量、净位移、是否触EMA/破trend line及后续跟进。
- 第1个：维持旧趋势，优先S03；第2个：two-sided score上调；第3个或更大spike：停止追价并启用S06候选。
- 若反向spike后测试旧趋势极值，可为lower high、double top或higher high；三类全部保留，不能只认可标准lower high。
- 两个相反方向强spike相距≤ `2–8bars` 时标记`SPIKE_CONFLICT_RANGE`，等待range突破决定channel方向。
- 只有反向突破和channel跟进完成后才翻转Always-In。

### TRENDS-C21-S11：大 Gap 与小 Opening Range 的突破模式

- 类型：开盘状态策略。
- 依据，PDF p.365–366、381、387–388：gap可作为spike；大gap后前5–10bars区间小于ADR约30%时处于breakout mode，趋势日概率提高。
- Setup：`abs(open-prior_close)/ADR20>=0.25`，前 `5–10bars` range≤ `0.20–0.35ADR20`。
- 双向放置stop的研究版本，gap方向突破赋较高先验但不取消反向订单。
- 入场：opening range外1tick；若假突破后形成double bottom/top，允许反转为gap方向。
- 止损：opening range另一侧或信号结构外。
- 目标：opening range高度、gap-spike等幅、1R/2R。
- 只有opening range完成后才能启用其高低点；不得回填早期成交。

### TRENDS-C21-N01：Tight Channel 内不提前逆势

- 类型：`NEGATIVE`。
- 依据，PDF p.360–364、378：channel会持续得远超预期且不断看似反转；parabolic形态虽不可持续，但climax可能比账户承受时间更长。
- 没有明确反向breakout及pullback前，禁止因ABC、trend-channel-line触及、第三推进或“抛物线不可持续”单独逆势。
- tight channel中的逆势失败应转为S03顺势候选。
- 不得用未来最终channel起点测试来证明早期逆势交易合理。

### TRENDS-C21-N02：多尺度解释不能产生前视选择

- 类型：`NEGATIVE`。
- 依据，PDF p.358–359、366、376–383：低周期spike可能是高周期channel，陡channel也可能是高周期spike；形态可嵌套且起点常有多个合理解释。
- 不要求下钻或上钻周期确认；基础模型只用当前周期可见信息。
- 若测试多周期，所有高周期bar必须等收盘后生效，低周期必须保存完整候选，不得只查看成功案例。
- 对多个合理spike/channel起点并行生成事件ID；不得根据最终测量目标命中情况选择起点。
- 嵌套事件各自计算风险，但同一价格风险敞口不得重复分配账户预算。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 357–360 | 核心特征、spike后pullback/channel及三种分支 | 第1节、S01–S03 |
| 360–364 | channel交易、反向突破回测、起点目标与25%回摆 | S03–S07、N01 |
| 362–363 | spike测量目标、趋势向新价值区间移动 | S08 |
| 364–369 | 弱channel、连续climax、gap/多周期、反向spike累积 | S04、S09、S10、N02 |
| 370–377 | 三推进、起点测试、嵌套与跨日案例 | S05–S10 |
| 378–386 | parabolic channel、gap、陡channel、连续climax | S05、S08、S09、N01–N02 |
| 387–390 | 小opening range、相反spike、spike-and-climax | S09–S11 |

## 4. 回测验收

- 每个事件逐bar记录`SPIKE/PULLBACK/CHANNEL/RANGE/REVERSAL`状态及确认时间，不以收盘后全日形状回填。
- spike阈值、channel宽紧和起点选择做敏感性矩阵；多个合理解释并行保留。
- S02统计post-spike三分支的无条件及按spike强度分层概率。
- S03/S04用同一channel样本比较只顺势、边缘双向和全双向，包含交易成本。
- S05直接验证顺趋势channel breakout在1/3/5/10bars内失败率。
- S06报告反向breakout后等待pullback相对立即追价的MAE、MFE和漏单率。
- S07验证channel-start测试后0.25回摆，并报告未形成range而直接延续的比例。
- S08所有高度和投射基点在事件发生时冻结。
- S09按2个/3个climax分层，报告两腿、10bars、EMA及pause测试的联合与分别命中率。
- S10建立反向spike数量到flag/range/deep correction/reversal的转移矩阵。
- Figure 21.1–21.10仅作章节例证，不作参数拟合或绩效证据。
