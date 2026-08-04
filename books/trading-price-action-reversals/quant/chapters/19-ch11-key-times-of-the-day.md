# 第 11 章：Key Times of the Day

## 元数据

- 英文来源：`books/trading-price-action-reversals/en/chapters/19-ch11-key-times-of-the-day.md`
- PDF 页码：270–277
- 图表：Figure 11.1–11.3；正文与图注已完整说明规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Session Phase

```text
OPENING = session_open .. +90/120min
MIDDAY  = +90/120min .. final_90min
CLOSE   = final_90min .. session_close
```

- 时段边界必须由交易所日历、时区与夏令时换算，不能硬编码服务器时间。
- 同一price-action规则仍适用于全天；时段只调整regime先验、目标、执行与开放门槛。
- 书中PST时刻为当时Emini示例，跨市场需映射本地regular session和已知event calendar。

## 2. 规则卡

### REVERSALS-C11-S01：Opening High-Opportunity Window

- 类型：时段风险/机会门控。
- 依据，PDF p.270：首1–2小时最常出现reward为risk 2–3倍的交易，也是最易快速亏损的时段。
- OPENING允许full strategy set，但每笔仍需成本后EV；目标候选`1–3R`，仓位不因机会多而超账户risk。
- 单独报告opening setup频率、净EV、slippage和最大连续亏损。
- 作者2–3R/50%等只作研究起点，不视为已验证概率。

### REVERSALS-C11-S02：Post-Report Orderly-Market Entry

- 类型：事件后执行。
- 依据，PDF p.270、274：7:00 PST报告/FOMC等发布瞬间计算机具速度优势、slippage大、方向约50%；应等数秒至数分钟有序后再交易。
- Event blackout=`-1min`至`+0.5–5min`，按品种流动性和bar周期测试。
- 重新开放条件：spread/realized slippage回常态、至少1–2bars完成、Always-In或breakout方向明确。
- Entry顺确认趋势/first pullback；不追首个不可成交spike。

### REVERSALS-C11-S03：Opening Reversal Daily-Tail Setup

- 类型：开盘反转策略。
- 依据，PDF p.270：预期strong trend day却先走数bars反向，随后恢复可形成daily bar小tail并给低risk大reward opening reversal。
- Daily/higher-timeframe bias与gap/context支持方向；开盘反向leg=`2–5bars`、未破关键结构。
- 出现strong reversal/Always-In flip后入场，stop在opening extreme外。
- Target opening range measured move、2R/3R或trend-day runner；bias必须由当时数据生成。

### REVERSALS-C11-S04：Midday Two-Sided / Tight-Range Filter

- 类型：时段regime门控。
- 依据，PDF p.270–272：中段更常见channel、TTR、dojis、反转和无follow-through，stop entries尤其差。
- MIDDAY若最近`10–30bars` overlap≥60%、EMA flat、双向break failures≥2，标记tight/two-sided。
- 初学/主策略关闭交易；高级模型只在range外侧20–30%用limit scalp。
- Strong breakout+follow-through/Always-In明确后解除filter。

### REVERSALS-C11-S05：Midday Range-Edge Limit Scalp

- 类型：高级中午区间策略。
- 依据，PDF p.271：机构在range底买、顶卖，并fade弱H/L1–2；stop只在边缘已转向时使用。
- Confirmed range、足够净空间≥`1R`；top sell weak H1/H2 extreme，bottom buy weak L1/L2 extreme。
- Target midpoint/`0.5–1R`；stop在range外`0.10–0.30ATR`。
- 真实queue/保守fill建模；未通过limit策略准入者只shadow。

### REVERSALS-C11-S06：Midday Reversal around Phase Transition

- 类型：首段趋势反转策略。
- 依据，PDF p.271、276–277：首段trend常在约8:00–9:30 PST（常8:30）进入反转或range，随后可走中段trend。
- 在OPENING→MIDDAY边界±`30–60min`，要求old-trend climax/wedge、trend-line break和strong opposite signal。
- Entry在two-bar reversal/Always-In flip；stop在day extreme外。
- Target EMA/open/opposite range edge；无确认只按range，不因时钟自动反转。

### REVERSALS-C11-S07：Three-Phase Trend-Resumption Pattern

- 类型：日内结构策略。
- 依据，PDF p.272–277：首段trend、中段反向/sideways、约11:30 PST附近恢复原trend，形成up-down-up或down-up-down。
- Opening leg明确；midday pullback低momentum/overlap高且未破opening origin。
- Final-phase出现原方向strong signal/breakout pullback时入场；target day extreme/close runner。
- 中段反向move若strong Always-In flip则允许S08 reversal-day路径，不固守resumption。

### REVERSALS-C11-S08：Final-Phase Direction-Agnostic Breakout

- 类型：尾盘方向选择。
- 依据，PDF p.272–273、276–277：最后第三段可恢复早盘trend，也可完成reversal day；交易者应对两方向开放。
- Final phase前冻结midday range；strong break任一侧+follow-through触发。
- 方向由price action决定，不以早盘方向硬编码；stop在breakout/flag结构外。
- Target close、range height measured move；隔夜持仓需独立授权。

### REVERSALS-C11-S09：Relentless Close-Trend Market/Close Entry

- 类型：尾盘无回调momentum策略。
- 依据，PDF p.273–275：最后30–60min风险平仓、基金orders和momentum programs可制造relentless trend，等pullback会踏空。
- 连续`2–4bars`方向body、浅tails、无反向break、累计≥`1ATR`，且距close≤60min。
- 在bar close/marketable limit入场，stop在entry bar另一端；每次风险固定并计冲击成本。
- Exit session close；首个momentum loss/strong opposite bar提前退出。

### REVERSALS-C11-S10：Daily-Trend Close Bias Overlay

- 类型：跨周期尾盘先验。
- 依据，PDF p.272–275：daily bull trend更常收open上方/近high，bear镜像；尾盘反向rally转折可恢复daily方向。
- Daily trend score在当日open前冻结；只作为S07–S09方向加分，不单独交易。
- 当日strong contrary Always-In覆盖daily bias。
- 样本外校准close-above-open/near-extreme条件概率，不能直接采用21/32案例。

### REVERSALS-C11-S11：Wide-Stop Close-Trend Swing

- 类型：尾盘两面波动管理。
- 依据，PDF p.273–276：尾盘trend可伴随大bars、tails和2–3次stop runs；前提仍有效时要用初始wide stop，pullback完成后再收紧。
- 入场stop在signal/spike另一端；position size按wide risk缩小。
- Doji/tail阶段不移到逐bar tight stop；确认pullback后移至pullback extreme外。
- Tight end-of-day range只供高级模型，普通策略退出/不入场。

### REVERSALS-C11-S12：Middle-Third Strategy Kill Switch

- 类型：个体/策略分时治理。
- 依据，PDF p.271–272：许多交易者中段亏掉首段利润，应把时段视作独立业务并关闭负EV部分。
- Walk-forward按OPENING/MIDDAY/CLOSE分别统计至少`100–300` trades、净EV与置信区间。
- MIDDAY下界≤0或损失显著吞噬opening收益时自动关闭实盘，仅shadow。
- 不因当天已盈利而放宽中段门槛，也不为“必须全天交易”开仓。

### REVERSALS-C11-S13：Final-Flag Failure into Close

- 类型：尾盘反转日策略。
- 依据，PDF p.274–275：中段range尝试恢复早盘trend却失败，可成为final flag，随后反向越open并relentless close trend。
- Midday range old-trend breakout在`1–5bars`失败并strong close穿对侧/日open。
- 在failed breakout/first pullback反向入场；stop在failure extreme外。
- Target opposite day extreme/close，和S08共享episode不重复计盈。

### REVERSALS-C11-N01：报告发布瞬间禁止竞争速度

- 类型：`NEGATIVE`执行硬约束。
- 依据，PDF p.270、274：自动系统在分析/下单速度上占优，瞬间slippage扩大使EV恶化。
- Blackout内新方向订单数必须为零，保护性stop/风险退出除外。
- 不以OHLC理想价模拟新闻bar成交。

### REVERSALS-C11-N02：Midday Tight Range 禁止追 Spike Stop Entry

- 类型：`NEGATIVE`。
- 依据，PDF p.271–272：range顶部buy stop/底部sell stop正好与机构buy-low/sell-high相反。
- S04成立时，range中部及错误边缘的stop-entry交易数为零。
- 只在边缘反转确认或strong breakout后重新开放。

### REVERSALS-C11-N03：时间点不是独立 Signal

- 类型：`NEGATIVE`模型约束。
- 依据，PDF p.270–277：任何price action可在任何时段发生，8:30/11:30只是倾向。
- Clock feature只能调整prior/门槛，仍须结构、signal和EV。
- 禁止看到时钟即反转或恢复早盘方向。

### REVERSALS-C11-N04：疲劳时禁止交易

- 类型：`NEGATIVE`操作风险约束。
- 依据，PDF p.273：个人会疲劳、无聊或分心，而edge很小；非正常状态不应与计算机竞争。
- 实盘提供manual readiness/最大连续时长/错误率kill switch；触发后只允许平仓。
- 回测不声称量化心理状态，但生产审计必须记录禁用原因。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 270 | 三时段、首段2–3R机会、报告速度劣势、opening reversal/daily tail | S01–S03、N01、N03 |
| 270–272 | 中段range/channel/TTR、limit scalp、stop trap、8:30 reversal与时段kill switch | S04–S06、S12、N02–N03 |
| 272–274 | 三段trend resumption、11:30双向准备、daily close bias与两类尾盘trend | S07–S11、N03–N04 |
| 274–275 | Figure 11.1：risk-manager close trend、midday final flag failure与daily bias | S09–S10、S13 |
| 275–276 | Figure 11.2：scary close trend、doji/tails、wide stop与trend resumption | S07、S09、S11 |
| 276–277 | Figure 11.3：midday reversal、final-phase resumption/failed resumption | S06–S08、S13 |

## 4. 回测验收

- 使用交易所point-in-time calendar、DST与half-day close生成phase；无硬编码PST偏移。
- 每个phase分别报告样本数、净EV、MAE/MFE、slippage、target R和最大回撤。
- Event blackout使用当时已知经济日历；新闻bar成交按tick/L2或保守gap模型。
- S07、S08、S09、S13共享session episode ID，避免同一尾盘move重复计盈。
- Daily bias只用前一日及更早数据；当日最终daily bar不得泄漏。
- Midday kill switch、tight-range stop禁令、event blackout和session-close退出设自动测试。
- 时段边界、event cooldown、range阈值及尾盘窗口做walk-forward、跨市场/季节敏感性检验。
- Figure 11.1–11.3仅作章节例证，不作参数或绩效证据。
