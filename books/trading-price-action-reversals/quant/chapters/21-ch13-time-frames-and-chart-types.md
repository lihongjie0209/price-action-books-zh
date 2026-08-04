# 第 13 章：Time Frames and Chart Types

## 元数据

- 英文来源：`books/trading-price-action-reversals/en/chapters/21-ch13-time-frames-and-chart-types.md`
- PDF 页码：280–291
- 图表：Figure 13.1–13.7；正文与图注已完整说明规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Chart Contract

```text
decision_chart = 唯一产生regime、方向、setup与持仓管理的主图
execution_chart = 仅在预注册条件下细化顺decision方向的entry
bar_type = time | tick | volume
```

- Price action可用于各种市场、周期和bar类型，但不同aggregation产生不同信号、成交频率与执行容量。
- 每个策略必须冻结主图与辅助图职责；不能看到不利信号后临时换周期或bar类型。
- 图表显示样式（bar/candle）不改变OHLC事实，只影响人工识别与屏幕容量。

## 2. 规则卡

### REVERSALS-C13-S01：Five-Minute Default Decision Chart

- 类型：主周期治理。
- 依据，PDF p.280–283：5分钟Emini通常兼顾足够setup、可读速度、精确trend lines和可预知bar close，多数交易者优于1/3分钟。
- 人工日内默认`decision_chart=5m`；所有regime、方向、stop管理与performance attribution基于5m。
- 其他周期只有在walk-forward证明更高净EV且操作错误率不升时替换。
- 不把作者示例中的setup数量/stop ticks当当前常数。

### REVERSALS-C13-S02：Bar-vs-Candle Display Selection

- 类型：人工界面配置。
- 依据，PDF p.280、283：candle便于scalper快速看bar归属/H2变体；窄bar图可在单屏显示更多完整日数据，适合多标的swing。
- Candle用于单市场快速signal识别；bar chart用于多标的swing screen与更长context。
- 自动模型直接读取OHLC，不因render style产生不同特征。
- 人工A/B测试missed signal、late order与错误率后固定一种display。

### REVERSALS-C13-S03：Timeframe Net-Execution Score

- 类型：周期选择。
- 依据，PDF p.280–281、289–291：低周期有更多trade和小stop，但实时处理、漏掉最佳setup、胜率、stress与成本常使净结果更差。
- Score=`netEV - execution_error_cost - missed_best_trade_cost - cognitive/load penalty proxy`。
- 对1m/3m/5m分别报告setup全集、实际可执行率、slippage、commission与capacity。
- 选择walk-forward下界最高而非gross trade count最多的周期。

### REVERSALS-C13-S04：One-Minute Runaway-Trend Entry Aid

- 类型：低周期顺势执行。
- 依据，PDF p.281、283–285：5m runaway trend无pullback时，可在1m寻找H/L1–2或prior-bar limit顺5m趋势入场，成交后只按5m管理。
- 5m strong trend、flat且无合格5m pullback；1m只允许同方向H/L1–2。
- Entry后stop可用1m structure但账户risk固定；target/trailing完全返回5m。
- 1m countertrend orders为零，避免把微反转误当大趋势反转。

### REVERSALS-C13-S05：One-Minute MA-Touch Risk Refinement

- 类型：股票趋势精细入场。
- 依据，PDF p.281–282、284–285：5m趋势股触20EMA时，可在1m等待首次方向反转，用较小signal-bar stop入场。
- 5m trend明确并实时触/穿20EMA；1m出现首个方向reversal/H1–2或L1–2。
- 1m surrogate EMA不硬编码90；以当前5m EMA时间对齐直接投影，90-bar仅作近似基线。
- 成交后按5m管理；与直接5m entry比较净EV、stop-out和漏单。

### REVERSALS-C13-S06：Single-Timeframe Regime Independence

- 类型：多周期冲突处理。
- 依据，PDF p.282：1m、5m、60m、daily、monthly可同时有相反趋势，等待全部一致既罕见也不保证获利。
- 每策略只交易decision timeframe眼前price action；higher timeframe最多提供预注册level/bias overlay。
- Opposite lower-timeframe trend不自动否决主周期setup。
- 保存各周期当时状态用于事后分层，但不得临时挑最支持仓位的周期。

### REVERSALS-C13-S07：Time/Tick/Volume Chart Equivalence Study

- 类型：bar aggregation研究。
- 依据，PDF p.282–287：time、tick、volume及任意bar size均可产生price-action setup；读图与管理能力比数字选择重要。
- 同一tick stream生成多种bars，使用相同母事件/时间区间比较信号与P&L。
- 参数候选以目标每session bars数/信息率选择，不神化Fibonacci或奇数。
- 只有样本外稳定增益才改变production chart；否则保持单一5m。

### REVERSALS-C13-S08：Activity-Bar Time-of-Day Normalization

- 类型：tick/volume chart时段校正。
- 依据，PDF p.285–286：成交活跃bar在首小时和尾盘单位时间产生更多bars，导致形态window对应的钟表时间不恒定。
- Tick/volume策略同时保存bar count和elapsed seconds；lookback以两者双重约束。
- 时段特征使用exchange clock而非activity-bar index。
- 目标/持仓期限按实际时间和ATR同时报告，避免开盘过度交易。

### REVERSALS-C13-S09：Post-Report One-to-Three-Bar Wait

- 类型：新闻后price-action策略。
- 依据，PDF p.287–289：报告后big/outside bars与多次reversal，计算机速度占优；等1–3bars后small bar/second entry仍可可靠交易。
- Event blackout至首`1–3 decision bars`完成且spread/slippage恢复。
- 避免range顶部买large reversal；优先trapped-trader failure、small signal和second entry。
- 合格breakout可保留runner并用BE stop，因为event trend可能远超预期。

### REVERSALS-C13-S10：Report-Day Second-Entry Swing

- 类型：事件反转确认。
- 依据，PDF p.288–289：第二次反转旧low/high、合格inside/reversal bar后常至少two legs，适合swing部分。
- First reversal失败/overlap后，second attempt位于major extreme且方向bar质量合格。
- Entry在second trigger；initial stop在signal合理结构（大bar可用中点/entry bar后收紧）。
- Target1=1R/EMA，余仓BE/trail；同bar路径保守处理。

### REVERSALS-C13-S11：Low-Timeframe Capacity Gate

- 类型：规模限制。
- 依据，PDF p.281：低周期频繁scalp在大qty下会暴露盘口、产生1–2tick slippage并破坏risk/reward。
- `qty/depth`、participation rate与target/cost ratio超阈值时关闭1m/3m scalp，迁移5m swing。
- Capacity curve逐size报告，不用小仓回测外推大仓。
- Entry/target partial fill与queue position完整模拟。

### REVERSALS-C13-S12：Multi-Chart Attention Gate

- 类型：操作复杂度治理。
- 依据，PDF p.281–285：同时读第二图容易被微move吸引、过度交易、过早退出并失去5m大局。
- 只有S04/S05触发时临时打开1m；成交后自动返回/隐藏1m。
- 人工同时active charts上限`1–6`按策略类型预设；记录miss/late/error。
- 若辅助图使5m执行质量下降，自动关闭其production使用。

### REVERSALS-C13-S13：Simple-Bar Swing Strategy

- 类型：基础price-action方案。
- 依据，PDF p.283：简单bar chart足以做趋势pullback与trend-line break后的extreme test反转。
- Trend中做H2/L2 pullback；strong line break后只在HL/LL或LH/HH test+strong reversal bar入场。
- Stop在signal/structure外，target旧极值/2R；不依赖indicator或candle coloring。
- 作为所有复杂chart方案的基准模型。

### REVERSALS-C13-N01：低周期小 Stop 不代表更高盈利

- 类型：`NEGATIVE`。
- 依据，PDF p.280–283、289–291：更多trade与小risk被更低胜率、漏单、选择偏差、stress和成本抵消。
- 未通过S03/S11时，1m/3m独立scalp禁止上线。
- 不以gross trades/day或stop ticks作为周期优越证据。

### REVERSALS-C13-N02：低周期只允许主周期顺势用途

- 类型：`NEGATIVE`硬约束。
- 依据，PDF p.281、283–285：打开1m是为了找5m runaway trend顺势entry，不是发现逆势short/long。
- S04/S05模式中所有逆decision-direction订单必须为零。
- 主周期明确flip后才更新允许方向。

### REVERSALS-C13-N03：禁止追求神奇 Bar Size

- 类型：`NEGATIVE`参数约束。
- 依据，PDF p.282–287：Fibonacci ticks、8/13分钟或随机数字都能画出好setup，没有特殊数字保证edge。
- Bar size必须用walk-forward执行表现选择并计multiple-testing。
- 不用最佳历史aggregation事后展示而隐去其余尝试。

### REVERSALS-C13-N04：报告瞬间与大 Outside Bar 不追单

- 类型：`NEGATIVE`执行约束。
- 依据，PDF p.287–289：event后速度/滑点劣势，大overlap/outside bar常是range而非可靠方向signal。
- S09 blackout内新仓为零；range顶部large bull reversal long/底部bear short禁止。
- 等small/second entry或strong orderly breakout。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 280–283 | bar/candle、1/3/5m trade-off、capacity、1m两种用途、周期冲突与chart types | S01–S08、S11–S13、N01–N03 |
| 283–285 | Figure 13.1–13.3：simple bar swing、runaway 1m顺势entry、1m MA refinement | S04–S05、S12–S13、N02 |
| 285–287 | Figure 13.4–13.5：activity bars时段偏斜与不同aggregation可交易 | S07–S08、N03 |
| 287–289 | Figure 13.6：报告后等待、traps/second entry与event swing | S09–S10、N04 |
| 289–291 | Figure 13.7：1m大量scalp、实时难度和context依赖 | S03、S11、N01–N02 |

## 4. 回测验收

- 所有bar types从同一无缺口tick stream生成，记录bar close time与实际elapsed time。
- Decision/execution chart角色在entry前冻结；临时换周期支持持仓的次数必须为零。
- 1m执行与5m直接entry共享母事件，比较净EV、MAE/MFE、fill、miss和stop-out。
- Time/tick/volume比较计multiple-testing、queue、slippage、fees和capacity curve。
- Event calendar point-in-time，报告bar采用保守成交；blackout自动测试通过。
- 报告每周期setup全集、可执行率、实际/模拟错误proxy、最大trade count和风险。
- Bar size、EMA surrogate、event wait与attention limits做walk-forward、跨市场敏感性测试。
- Figure 13.1–13.7仅作章节例证，不作参数或绩效证据。
