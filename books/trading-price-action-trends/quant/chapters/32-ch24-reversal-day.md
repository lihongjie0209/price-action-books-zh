# 第 24 章：反转日

## 元数据

- 英文来源：`books/trading-price-action-trends/en/chapters/32-ch24-reversal-day.md`
- PDF 页码：447–454
- 图表：Figure 24.1–24.3；正文与图注已逐bar说明，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 实时状态机

```text
INITIAL_TREND -> COUNTERTREND_PULLBACK
COUNTERTREND_PULLBACK -> OLD_TREND_RESUMES
COUNTERTREND_PULLBACK -> OPPOSITE_SPIKE
OPPOSITE_SPIKE -> RANGE | OPPOSITE_CHANNEL
OPPOSITE_CHANNEL -> REVERSAL_DAY_CANDIDATE
```

- 只有反向Always-In翻转才确认`OPPOSITE_SPIKE`；普通两腿pullback仍归旧趋势。
- `REVERSAL_DAY`必须到session结束才是最终日型，仅用于评估；实盘只使用候选状态。
- 多数候选此前呈trending trading range，因此需保存上下range、bridge和潜在回测目标。

## 2. 规则卡

### TRENDS-C24-S01：中后段强 Spike 的 Always-In 翻转

- 类型：完整反转/突破策略。
- 依据，PDF p.447–448：最强趋势可在日中或尾盘开始；大trend bars、低重叠、小尾部和清晰Always-In flip要求快速进入并swing大部分仓位。
- Setup：已有反向初始趋势或range；session任意时点出现反向净位移 `1–3ATR`，由 `1–4bars` 构成，同向body率≥0.70、overlap≤0.35。
- 确认：突破主要trend line及最近结构swing，并有1bar跟进或breakout pullback守住。
- 入场：breakout close小仓、下一bar stop，或首次小pullback；三种分别回测。
- 止损：spike起点/突破结构另一侧，按固定账户风险缩仓。
- 目标：旧range对侧、初始趋势起点、spike等幅、1R/2R；保留swing至收盘。
- “看起来过度”不能否决入场；只有反向失败和结构stop才失效。

### TRENDS-C24-S02：不断扩大的 Pullback 转为反向 Channel

- 类型：趋势转换策略。
- 依据，PDF p.447–450：有些反转不是单次爆发，而是pullback以反向spike开始并不断扩大，最终形成比原趋势更大的反向channel。
- Setup：旧趋势中的pullback首腿包含反向trend bar/spike≥ `0.75ATR`，强于此前回调中位数 `1.5倍+`。
- 观察：反弹/回撤未恢复旧极值，形成lower high/higher low，随后第二反向推进突破第一腿极值。
- 入场：第二推进breakout，或其breakout pullback。
- 止损：lower high/higher low外。
- 目标：旧趋势起点、原趋势长度的 `0.5/1.0×`、1R/2R。
- 翻转后只交易新方向；禁止继续按“只是旧趋势旗形”反复逆新趋势。

### TRENDS-C24-S03：Trending Trading Range 的尾盘反转

- 类型：跨range反转策略。
- 依据，PDF p.447–452：多数reversal days起初是trending trading range；最后range反向突破可贯穿早先range并形成收盘趋势。
- Setup：已确认两个错位range；最后range趋势侧失败突破、第三推进/连续climax或测量目标完成。
- 触发：反向spike突破最后range，再出现回测守住或第二信号。
- 入场：breakout-pullback；若spike满足S01可先小仓进入。
- 止损：最后range极值外。
- 目标：bridge gap、前一range近边/对侧、当日open、1R/2R。
- 若只回到range中部且无跟进，按range交易退出，不强行持有为reversal day。

### TRENDS-C24-S04：Wedge/Channel 结束后的充分修正

- 类型：结构反转与目标组件。
- 依据，PDF p.451–452：大型wedge或spike-and-channel结束后，通常至少两腿回到wedge顶部/channel起点；修正bars常至少约为原wedge的三分之一。
- Setup：原趋势形成三个推进、channel过冲或连续climax，随后反向突破主要trend line。
- 标准入场：首次反转后的higher low/lower high或失败的第二顺旧趋势信号；激进首信号单列。
- 止损：最终wedge/channel极值外。
- 目标：channel起点/wedge首推进极值、两腿、修正持续 `0.25–0.50×` 原结构bars。
- 若反向第一腿本身是tight channel且持续不足，视为复杂第一腿，不能过早认定修正完成。
- 失败wedge顺原趋势突破时，目标为wedge高度等幅，不执行反转。

### TRENDS-C24-S05：尾盘反转后的次日 Follow-Through

- 类型：跨session延续策略。
- 依据，PDF p.447：最后数小时开始且强劲的反转，通常在次日、甚至随后数日有延续。
- Setup：前一session反向趋势起于session fraction≥ `0.60`，收盘前净反向位移≥ `0.5–1.0ADR`，并收在反转方向端20%。
- 次日不在隔夜阶段回填；开盘后等待首次顺前日反转方向pullback或opening breakout。
- 入场：High/Low 1/2、breakout pullback或EMA测试。
- 止损：次日pullback结构外。
- 目标：前日反转极值、1R/2R、当日收盘。
- 若次日强gap反向并Always-In翻转，立即取消；原文“通常延续”需按市场隔夜制度重新估计。

### TRENDS-C24-S06：反转后 Swing 管理

- 类型：仓位管理组件。
- 依据，PDF p.449–450：强反向channel中频繁pullback会扫掉scalp stop；swing通常优于反复scalp，应把stop跟在新趋势swing外。
- S01/S02确认后冻结`SWING`计划；第一目标前不因小pullback变为scalp。
- 每次创新趋势极值后，将stop移至最近已确认lower high/higher low外。
- 允许在1R/2R减 `25–50%`，余仓至明确反转或收盘。
- 连续 `2–3` 个顺新趋势setup亏损或Always-In重新翻转是模型诊断/退出事件，不把“我在亏钱”本身作为新入场信号。
- 与固定money stop和每bar极值trail比较完整路径。

### TRENDS-C24-N01：不能用最终日线形状识别盘中反转

- 类型：`NEGATIVE`。
- 依据，PDF p.447–452：日终可能成为带长尾doji或反转bar，但盘中必须根据spike、结构突破和channel形成交易。
- 禁止使用当日最终high/low/close、最终range或“收盘会在极值附近”作为入场特征。
- 单个countertrend spike通常仍可能只是flag；至少需要S01确认或S02第二推进。
- 小周期3分钟可增加runaway趋势顺势信号，但仅限预先固定且完整保存的数据；不得事后下钻寻找成功入场。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 447–448 | reversal-day特征、中后段runaway spike、pullback转channel | 第1节、S01、S02、S05 |
| 449–450 | 原强趋势失败、反向spikes累积、lower highs/lows与swing | S02、S03、S06 |
| 451–452 | 多数源于trending range、wedge/channel充分修正 | S03、S04 |
| 453–454 | runaway趋势的低周期顺势机会 | N01 |

## 4. 回测验收

- 每个状态保存首次确认bar；最终`REVERSAL_DAY`标签只能用于结果分层。
- S01报告按session fraction、spike bars、净ATR和原市场状态的校准结果。
- S02比较“第一反向spike立即反转”与“等待第二推进”的收益、延迟和假信号。
- S03建立回到最后range/前一range/穿越全日range的条件概率。
- S04按原结构bars与修正bars比例、两腿完成度和起点测试分别报告。
- S05采用完整隔夜与次日session数据，计入gap滑点，不把未成交价格当成交。
- S06使用逐笔完整路径验证swing优于scalp的主张。
- Figure 24.1–24.3仅作章节例证，不作参数拟合或绩效证据。
