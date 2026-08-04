# 第 21 章：Detailed Day Trading Examples

## 元数据

- 英文来源：`books/trading-price-action-reversals/en/chapters/31-ch21-detailed-day-trading-examples.md`
- PDF 页码：395–402
- 图表：Figure 21.1–21.6；正文逐bar说明已完整覆盖规则，未额外查看图片
- 状态：量化研究规格，未经回测；本章主要验证前三本书规则的组合与优先级
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 组合决策框架

```text
setup_score = context + structure + signal_bar + follow_through - conflict - execution_cost
priority: confirmed AI / strong spike > isolated countertrend label
UNCERTAIN: multiple valid anchors or tight range → breakout mode
```

- 同一bar可同时拥有多个标签；策略应保留全部标签并用上下文决定方向，不能事后挑选盈利解释。
- 本章涵盖Treasury volume bars、EUR/USD、soybeans、crude oil和Emini 1m，参数必须按品种/图型独立校准。

## 2. 规则卡

### REVERSALS-C21-S01：Non-Time-Bar Normalization

- 类型：数据适配。
- 依据，PDF p.395：10,000-contract bar按累计成交量闭合，时长从数秒到十余分钟且最后一笔可使volume超过阈值。
- 保存实际volume和bar duration，不强制截断到目标值；ATR、EMA和pattern按bar序计算，时段风险按clock time计算。
- 与时间bar用相同clock-time母样本比较，避免把更多/更少bars误当信号优势。

### REVERSALS-C21-S02：Countertrend Exit on With-Trend Second Entry

- 类型：反趋势风险管理。
- 依据，PDF p.395–397：bear trend中的弱HL long遇到EMA处bear L2应退出/反手，除非趋势已明确翻转；镜像适用。
- Countertrend仓位在原趋势H/L2、同向signal bar及EMA test同时出现时退出。
- 只有强spike已翻AI或该second entry本身高概率失败时允许继续持有。

### REVERSALS-C21-S03：Spike-and-Channel Exhaustion Reversal

- 类型：趋势反转。
- 依据，PDF p.396–399：持续`20–30 bars`的spike-and-channel、三推、channel overshoot/final flag及强反转常带来至少两腿修正。
- 要求三推/加速wedge+channel line overshoot或final flag，再由反向trend/two-bar reversal触发。
- 目标channel起点/`1–2R`；修正bar数候选为原channel长度的`0.33–0.67`，仅作经验搜索。

### REVERSALS-C21-S04：Strong-Spike Priority and Two-Leg Hold

- 类型：冲突消解。
- 依据，PDF p.396–398：强反向spike翻转AI后，即使出现旧趋势MA-gap/second-entry setup，spike方向更可能至少再走一腿。
- Spike满足连续强棒、结构突破与低重叠时提高到最高优先级；首个弱反向signal不得反手。
- 在首H/L2或小pullback加仓/入场，直到出现清晰相反spike或完成两腿。

### REVERSALS-C21-S05：Ambiguity-to-Breakout-Mode

- 类型：不确定性状态转换。
- 依据，PDF p.397–398：triangle有多个合理三推anchor时代表confusion，即tight trading range，应等待breakout。
- 当至少两组相反形态分数接近且overlap/tails达tight-range阈值，输出UNCERTAIN。
- 区间中部关闭stop entries；等待强breakout+pullback，或仅研究边缘fade。

### REVERSALS-C21-S06：Breakout-Pullback Reentry Ladder

- 类型：趋势重复入场。
- 依据，PDF p.398–400、402：range break后small pullback、EMA L/H2、首次pullback与failed countertrend setup均可重复顺势入场。
- AI确认后按`first pullback → H/L2 at EMA → failed opposite setup`登记不同entry tier。
- 每tier单独记账且总风险封顶；目标scalp `1R`与swing `2R/channel projection`并行。

### REVERSALS-C21-S07：Largest-Late-Trend-Bar Exhaustion Alert

- 类型：climax预警。
- 依据，PDF p.398：约20bars趋势末端出现全段最大单棒/两棒spike，可能是最后弱手成交，随后至少两腿约10bars反弹。
- 趋势年龄≥`15–30 bars`且最新range处`90%–99%`分位时标记exhaustion candidate。
- 不立即逆势；需inside reversal/two-bar reversal及结构触发，失败则仍按原趋势。

### REVERSALS-C21-S08：Final-Flag after Opening Climax

- 类型：开盘climax反转。
- 依据，PDF p.399–400：opening buy climax后doji range是差的H1，lower-high L2/final flag可启动大第二腿；bear镜像。
- Opening spike后`1–5`小重叠bars，随后反向second-entry/flag break时入场。
- 若逆向move未跟进并重新突破climax extreme，立即退出并转continuation状态。

### REVERSALS-C21-S09：Failed Huge Reversal-Bar Trap

- 类型：失败反转。
- 依据，PDF p.399–400：新低后的巨大bull reversal bar若下一bar不能越过其高点，早入long被困，bear bar下破成为可靠short。
- Huge reversal bar触发失败需后`1–2 bars`不越其signal extreme且出现反向close/突破其另一侧。
- 反向entry stop在failure bar外；目标原趋势新极值/`1–2R`。

### REVERSALS-C21-S10：Trend-Line Break Lower-High Reversal

- 类型：major trend reversal。
- 依据，PDF p.400–401：wedge top后破趋势线/前HL，再形成两腿回测、lower high、EMA拒绝和wedge bear flag，是组合short；镜像适用。
- 要求显著trend-line break+关键swing破坏，再等two-legged test未创新趋势极值。
- Context标签累加但只下一个母事件订单；stop在test extreme外。

### REVERSALS-C21-S11：Signal-Bar Quality Conditionality

- 类型：signal过滤。
- 依据，PDF p.395–400：逆强趋势的doji signal较弱；顺势EMA second entry的同向bar更可靠；强背景可弥补部分bar缺陷。
- Countertrend要求body/close严格档；with-trend可放宽至基准/宽松档。
- Signal quality不得脱离AI、位置和前置spike单独评分。

### REVERSALS-C21-S12：One-Minute Scalp Research Partition

- 类型：低周期研究。
- 依据，PDF p.401–402：1分钟图存在大量标准scalp，但多数人无法足够快且准确地捕捉。
- 复用H/L2、wedge、failed breakout、double、breakout pullback规则，但参数和成本单独训练。
- 生产默认关闭；仅在tick级成交、延迟和queue模拟后评估，不与5分钟swing绩效合并。

### REVERSALS-C21-S13：Multi-Label Event Deduplication

- 类型：信号去重。
- 依据，PDF p.395–402：单一bar常同时是wedge、double、two-bar reversal、breakout pullback、final flag等。
- 同方向、同结构极值、`±1 bar`内信号合为一个event，保留`labels[]`和各分数。
- 仓位不能因标签数量机械倍增；标签组合只影响门槛/置信分层。

### REVERSALS-C21-N01：多个合理形态并存时不在 Tight Range 中强行选择

- 类型：`NEGATIVE`状态约束。
- 依据，PDF p.397–398：多重解释意味着交易区间与breakout mode。
- S05成立时中部方向性订单为零，直到状态确认。

### REVERSALS-C21-N02：低周期图上可见不等于人工可执行

- 类型：`NEGATIVE`执行约束。
- 依据，PDF p.401：多数交易者几乎不可能及时正确读取并捕捉大部分1分钟scalps。
- 禁止使用零延迟、零滑点的理想成交宣称可复制收益。

### REVERSALS-C21-N03：案例命名与结果不得作为标签泄漏

- 类型：`NEGATIVE`研究约束。
- 依据，PDF p.395–402：本章为事后详细案例，同一bar存在多种解释。
- 训练标签只能由当时可见features生成；不得把“high/low of day”“最终trend”或图中编号结果提前输入。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 395 | volume-bar构造、bear trend EMA shorts、弱countertrend signal | S01–S02、S11 |
| 396 | L2迫使countertrend退出、wedge/final flag MTR、长channel修正与目标 | S02–S04 |
| 397 | 强spike优先旧趋势setup、多anchor triangle为breakout mode | S04–S05、N01 |
| 398 | 多次breakout-pullback、parabolic wedge、最大趋势棒exhaustion | S05–S07 |
| 399 | opening climax/final flag、wedge bear flag、巨大反转棒失败 | S08–S09 |
| 400 | failed reversal trap、crude wedge top及TL break lower high | S09–S11 |
| 401 | 1分钟scalp数量多但多数人不可快速执行 | S12、N02 |
| 402 | H/L2、wedge、double、failed breakout等多标签低周期案例 | S12–S13、N03 |

## 4. 回测验收

- 同一信号引擎在各品种与time/volume bars运行，但参数、成本和bar duration分布独立报告。
- 每个event保存全部实时标签、AI状态、优先级与去重结果；抽查冲突signal未产生双重仓位。
- 分别验证spike优先、countertrend退出、三推exhaustion、failed huge bar与TL-break retest策略。
- 两腿、约10bars、channel起点目标和原channel一半时长均作为假设报告到达率与置信区间。
- 1分钟版本使用tick/quote延迟、spread、queue及同bar路径模拟；与5分钟版本不得合并。
- 按品种、bar类型、趋势/区间、顺势/逆势、signal quality和多标签数量分层EV、MAE/MFE。
- Figure 21.1–21.6只作组合逻辑案例，不作参数、胜率或可执行性证据。
