# 第 13 章：Twenty Gap Bars

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/22-ch13-twenty-gap-bars.md`
- PDF 页码：272–276
- 图表：Figure 13.1–13.2；正文与图注足以定义规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 定义

以20-period EMA为默认均线，方向标准化后按bull描述：

```text
gap_bar_bull(t) = low[t] > EMA[t]
untouched_bull(t) = low[t] > EMA[t]
twenty_gap_ready = 连续N根completed bars未触EMA，N默认20
first_touch = ready后首根 low <= EMA 的bar
MA_gap_bar_other_side = high[t] < EMA[t]
```

- Bear趋势镜像：`high < EMA`为未触线，首次`high >= EMA`为touch，首根`low > EMA`为另一侧gap bar。
- “20”只是强趋势的经验阈值而非自然常数；主测 `N=20`，稳健性测试 `15/20/25/30`。
- 每个session与连续合约如何衔接必须预注册；EMA warm-up不足时不生成事件。

## 2. 规则卡

### RANGES-C13-S01：20 Gap Bars 首次 EMA Touch 顺势交易

- 类型：完整顺势策略。
- 依据，PDF p.272–274：连续20bars不触EMA说明趋势很强也已过度延伸；若此前没有清晰反转，首次触线高概率回测趋势极值。
- Setup：`twenty_gap_ready=true`，旧趋势仍有效，无S04/S05否决；等待首次EMA touch。
- 首选触发：touch后出现顺趋势reversal bar、High/Low 1或第二入场，在signal bar顺势端外1tick stop入场。
- 激进版本：EMA附近limit/market；必须与stop版本分组，并建模未成交与 adverse excursion。
- 止损：EMA pullback swing极值外；若距离过大则按固定账户风险缩仓。
- 第一目标：旧趋势极值；另报1R/2R，并保留部分仓位追踪潜在大幅延续。
- Touch前若已确认反转，禁止把旧趋势极值作为默认目标。

### RANGES-C13-S02：未触 EMA 的 Near Miss 作为积极顺势测试

- 类型：提前回测候选策略。
- 依据，PDF p.273–274：趋势方可能在EMA前2–3ticks提前挂单，导致两腿回调在均线前转向；大同向trend bar表示防守积极。
- Ready后，两腿pullback距离EMA不超过 `max(1–3ticks, 0.05–0.15ATR)` 且未触线，标记near miss。
- 必须出现顺势reversal signal；signal bar外stop入场，不凭接近EMA直接成交。
- 止损：两腿pullback极值外；目标为旧极值、1R/2R。
- Near miss与真正first touch作为互斥事件报告，避免同一行情重复计数。

### RANGES-C13-S03：首次 Moving-Average Gap Bar 的第一/第二入场

- 类型：较深回调后的顺势策略。
- 依据，PDF p.272–273：一次或多次EMA测试后常出现完全位于均线另一侧的gap bar；应fade首个gap bar，首入失败可做第二入场，第三次不值得。
- Bull版：20-gap背景后首次`high < EMA`；等待其后High 1，失败后允许High 2。Bear版镜像。
- 入场：prior/signal bar顺势极值外1tick stop。
- 止损：gap-bar pullback最终极值外。
- 目标：EMA、旧趋势极值、1R/2R；至少一部分允许swing。
- 每个first-gap事件最多两次尝试；两次失败后视为channel/range或regime变化，禁止第三次机械重入。
- 若gap bar出现在强趋势反转之后，交给S04并禁用旧趋势方向。

### RANGES-C13-S04：Clear Trend Reversal 否决门

- 类型：状态否决组件。
- 依据，PDF p.272–273：市场可在长时间远离EMA后直接反转；强反转后出现的first gap bar属于已结束的旧趋势，通常失败。
- 以下任两项确认clear reversal：逆势spike `2–4bars >=1.5ATR`、突破major trend line、突破最近prominent swing、Always-In翻转且有follow-through。
- 否决必须在S01/S03触发前用已完成bar确认，不得因后来失败而回填。
- 否决后重置旧方向gap计数；仅在新趋势积累自己的N个未触线bars后重新启用。
- 单根弱reversal bar或无follow-through的line break不足以否决。

### RANGES-C13-S05：Climax 后一腿触 EMA 不买/卖

- 类型：条件禁用与二腿等待策略。
- 依据，PDF p.275–276：parabolic spike是climax，通常至少产生两腿、持续10bars以上的修正，甚至反转；第一腿触EMA的顺旧趋势交易风险高。
- Climax候选：连续 `3–6bars` 净位移≥`2ATR`、重叠≤0.25、收盘靠近极值比例≥0.70，或三推加速结构。
- Climax后首次touch不执行S01的limit版本；stop版本也需第二腿或强reversal signal才可触发。
- 优先等待：修正≥2legs且≥10bars、double bottom/top、第二入场。
- 若相反方向spike突破形态并有follow-through，按反转/range处理，不继续期待旧极值测试。

### RANGES-C13-S06：Touch 后强 Countertrend Rally 的快速止盈

- 类型：持仓管理覆盖层。
- 依据，PDF p.273–274：即使首次touch顺势有效，若到EMA的逆势腿很强，交易者仍预期higher low/lower high和第二次测试，顺势仓多在旧极值附近快速退出。
- 若touch前逆势连续trend bars≥`4/6`、净位移≥`1.5ATR`，标记`strong_counter_leg`。
- S01入场后第一目标改为最近旧极值/逆势腿起点附近；到达1R或结构目标平掉 `70–100%`，不默认大swing。
- 只有顺势恢复形成strong breakout+follow-through，才保留/重新建立swing仓。
- 此规则只影响退出，不使用未来第二腿判断当下仓位。

### RANGES-C13-N01：Sideways 20–30 Bars 后 First Gap 不再可靠

- 类型：`NEGATIVE`。
- 依据，PDF p.275–276：趋势演化为20–30bars trading range后，另一侧first gap bar不再是可靠旧趋势setup。
- 最近20bars若净位移≤`1ATR`、overlap≥0.60、EMA双侧收盘各≥3bars，确认range候选；两侧测试后确认range。
- Range确认后禁用S01/S03，直到强breakout及follow-through建立新trend regime。
- 不能因最终看见横盘而回填最初几根bar的range状态。

### RANGES-C13-N02：20 不是固定胜率承诺

- 类型：`NEGATIVE`与研究约束。
- 依据，PDF p.272：20只是提醒趋势很强的任意大数；任何周期适用，极强趋势也可能常触EMA，长时间不触也可能直接反转。
- 不得把第20根bar本身作为入场信号；它只开启等待touch的状态。
- 不得宣称特定小时数必要；以bar count表达并跨周期测试。
- 参数选择必须在训练样本完成，样本外锁定；报告N变化下事件数、胜率、期望值与最大回撤。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 272–273 | 20-gap定义、首次touch、stop优于limit、first gap与两次入场 | 定义、S01、S03、N02 |
| 273–274 | 首touch案例、near miss、强逆势腿后的快速退出 | S01–S02、S06 |
| 274–275 | 趋势线/形态背景、强反转否决、climax风险 | S04–S05 |
| 275–276 | parabolic climax、至少二腿、range后gap失效 | S05、N01 |

## 4. 回测验收

- EMA只用当根及历史数据；触线比较明确使用bar high/low，不用close替代。
- `N=15/20/25/30`分别报告，主结果固定20，禁止看完绩效后改名为最佳N策略。
- First touch、near miss、first opposite-side gap分别建立唯一事件ID，避免重复样本。
- S01按“无反转 / clear reversal”分层，S05按“有/无climax”分层。
- Limit与stop entry独立报告成交率、滑点、MAE/MFE；不得假设触线limit必然成交。
- 第二入场必须由第一次实际触发并失败后实时计数；最多两次。
- Session gap、休市和合约换月不得伪造连续gap bars；数据清洗规则预注册。
- Figure 13.1–13.2只作章节例证，不作参数拟合或绩效证据。
