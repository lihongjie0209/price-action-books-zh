# 第 12 章：双顶熊旗与双底牛旗

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/21-ch12-double-top-bear-flags-and-double-bottom-bull-flags.md`
- PDF 页码：256–271
- 图表：Figure 12.1–12.7；正文与图注足以定义规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 形态定义与方向标准化

以下规则先按多头定义，空头完全镜像：

```text
double_bottom = 两个已确认swing low位于同一价格带
same_price_band = abs(low_2 - low_1) <= max(2*tick, 0.10–0.30*ATR)
double_bottom_bull_flag = bull regime中的double bottom / 两腿回调
double_top_bear_flag = bear regime中的镜像结构
```

- 两底/顶不必相等，允许轻微undershoot或overshoot；容差必须在回测前固定。
- 两个swing之间至少有 `2bars` 且中间反弹/回落≥`0.5ATR`；最长间隔主测 `5–60bars`，另报更长周期。
- Bull flag本质上是High 2或failed Low 2；bear flag本质上是Low 2或failed High 2。
- 相同几何结构在趋势中是continuation，在相反趋势末端才是reversal；策略必须先判regime，不能只按形状交易。

## 2. 规则卡

### RANGES-C12-S01：Double Bottom Bull Flag 顺势买入

- 类型：完整顺势策略。
- 依据，PDF p.256–259：bull pullback是小bear trend，常以double bottom结束；强bull会在最近higher low附近保护结构，形态是可靠High 2。
- Setup：`bull regime=true`；两腿下跌形成两个同价带swing lows，第二底没有被强势收盘跌破。
- Signal质量：bull reversal bar、第二入场、failed Low 2、EMA/前higher low共振各加分。
- 入场：signal bar高点上1tick stop；保守版等待向上breakout及首次pullback。
- 初始止损：第二底或整个形态最低点下1tick；按固定账户风险缩仓。
- 目标：pullback起点/旧高、1R/2R、形态高度measured move。
- 若强bear breakout收于两底下方并有follow-through，立即失效并交给S07。

### RANGES-C12-S02：Double Top Bear Flag 顺势卖出

- 类型：S01镜像完整策略。
- 依据，PDF p.256–259：bear pullback是小bull trend；强bear在最近lower high附近卖出并保护其上方止损，形成double top。
- Setup：`bear regime=true`；两腿上涨形成两个同价带swing highs，第二顶未被强势收盘突破。
- 入场：signal bar低点下1tick stop；保守版等待向下breakout pullback。
- 止损：第二顶或整个形态最高点上1tick。
- 目标：pullback起点/旧低、1R/2R、形态高度measured move。
- 强bull breakout及follow-through使形态失效，转S07镜像逻辑。

### RANGES-C12-S03：最近 Swing 的防守与 Lower-High / Higher-Low 测试

- 类型：结构测试组件。
- 依据，PDF p.256–258：趋势方常在最近higher low/lower high附近集中交易；对手方也会在两腿回调的lower high/higher low作最后防守。
- 记录最近prominent swing及其容差带 `1–2ticks / 0.10ATR`。
- 第二腿反弹测试lower high后转跌，标记double-top bear-channel候选；第二次下探测试旧低后转涨，标记double-bottom bull-flag候选。
- 突破结构但在 `1–2bars` 内返回属于stop-run，不立即改变regime；突破后连续2次收盘且follow-through才升级结构破坏。
- 此组件只产生level/event，不单独下单，由S01/S02/S07消费。

### RANGES-C12-S04：小 Trading Range 的 Breakout Mode 判向

- 类型：条件突破策略。
- 依据，PDF p.257、260–261：同一pullback可同时是double bottom和double top；此前动量决定更可能的continuation方向，突破目标至少为range高度。
- Setup：两个方向的旗形同时有效，range持续 `5–30bars`、overlap≥0.60、两侧各至少一次测试。
- Bias：入range前 `3–10bars` 净位移≥`1.5ATR` 或同向trend bars≥60%，则偏向原动量方向；否则保持中性。
- 入场A：偏向方向边缘的reversal signal；入场B：range外强收盘后首个breakout pullback。
- 止损：range另一侧或signal swing外。
- 第一目标：range高度measured move；中性版本可在两侧放条件stop，但一侧触发即取消另一侧。
- 弱breakout、无follow-through或立即回range转S07，禁止继续按首次突破追价。

### RANGES-C12-S05：Spike-and-Channel 底部测试旗形

- 类型：趋势延续策略。
- 依据，PDF p.259、261–264：spike后channel通常回测channel起点/底部，并与早先低点形成double bottom bull flag；bear方向镜像。
- 识别spike：`2–5bars` 同向位移≥`1.5ATR`；随后channel至少两个同向swings。
- Channel结束后，价格进入起点/首pullback的 `0.10–0.30ATR` 容差带并形成第二反转时触发候选。
- 入场/止损沿用S01/S02。
- 最低目标：回弹原sell-off高度的 `25%`；扩展目标为channel中点、旧极值和形态measured move。
- 若回测前形成强反向spike，则不挂limit猜底/顶，等待实际反转signal。

### RANGES-C12-S06：Failed Low 2 / High 2 转化为双底/双顶旗

- 类型：失败信号策略。
- 依据，PDF p.258、262、267：趋势延续尝试在同一价位失败两次，市场常尝试相反方向；failed Low 2常成为double bottom bull flag。
- Bull版：bull/range regime中Low 2 short触发后 `0–2bars` 无follow-through，价格突破其signal/entry bar高点，且两次低点同价带。
- 在失败确认bar高点上1tick买；bear版镜像。
- 止损置于两次尝试的最终极值外；目标为range另一侧、旧趋势极值、1R/2R。
- 强反向trend已经确认时禁用：High 2只适用于bull/range，Low 2只适用于bear/range。

### RANGES-C12-S07：旗形错误方向突破后的 Wedge Variant

- 类型：失败突破反转策略。
- 依据，PDF p.259–260、270–271：double bottom跌破或double top突破后若在1–2bars内失败，原两推加假突破构成三推wedge；关键是三推而非完美外形。
- Bull版：两个bottom后向下突破，`1–2bars` 内重新收回形态低点，并突破prior bar高点；计为第三推。
- 入场：reclaim bar/prior bar高点上1tick；bear版镜像。
- 止损：失败突破最终极值外。
- 目标：range中点/另一侧、1R/2R、wedge高度；至少要求预期收益≥风险。
- 若错误方向breakout有连续2次强收盘或follow-through，不做反转，转S08。

### RANGES-C12-S08：旗形真失败与反向 Measured Move

- 类型：失败形态顺突破策略。
- 依据，PDF p.258、260、264–266：有效跌破double bottom可触发保护止损并走形态/range高度等幅；多次假突破后真突破往往产生swing。
- 确认：收盘越界≥`0.10–0.30ATR`，下一bar未收回且有同向follow-through，或breakout bar位移≥`1.0ATR`。
- 入场：确认收盘或首次pullback；不回填到最初越界时点。
- 止损：breakout pullback极值外或range内部 `0.25–0.50` 高度。
- 目标分别测试：double-pattern高度、wedge高度、完整range高度；不得事后挑最吻合测量。
- 形态突破尺度采用ATR/tick归一化，不能把高价股票的固定1tick直接套到所有市场。

### RANGES-C12-S09：Sharp Reversal + Breakout Pause 强趋势延续

- 类型：强度过滤与加仓策略。
- 依据，PDF p.266–269：第二底后快速上涨且breakout后横盘而不回调，常引出强趋势；强spike应有follow-through，并可用多个预先定义目标止盈。
- 第二底后 `2–5bars` 上涨≥`1.5ATR`，bull-body比例≥0.70，且每bar OHLC大体抬升，定义sharp reversal。
- 突破中间swing high后连续 `3–8bars` 横盘，最大回撤≤`0.5ATR` 且无收盘回range，定义pause-not-pullback。
- 首仓用S01，加仓在pause上沿突破或首次High 1/2；统一总风险，不把每次加仓当独立满仓。
- 目标按预注册顺序：形态高度、spike高度、已确认measuring gap；剩余仓以结构/EMA trail。
- 强tight channel中不因Low 3/Low 4标签逆势卖出，除非先有强breakout再有pullback。

### RANGES-C12-S10：Head-and-Shoulders 与 Double Bottom 的竞争情景

- 类型：情景树组件。
- 依据，PDF p.259、263–264：同一结构可被解释为head-and-shoulders或double bottom；多数趋势内reversal形态失败，必须按实际breakout更新。
- 同时维护：`bull_case=double_bottom`、`bear_case=neckline_break/head_shoulders`，禁止主观提前删除一方。
- Neckline强势跌破并follow-through时启用bear case；right shoulder向上失败突破时启用failed-H&S bull case。
- Double-bottom bounce最低统计sell-off高度的25%；failed H&S目标统计bar6-low到right-shoulder高度的上投影，参数化为结构高度。
- 趋势先验进入评分但不能覆盖价格确认；每种解释的触发、止损和目标分别记账。

### RANGES-C12-N01：Range 中的大反转 Bar 不是充分入场理由

- 类型：`NEGATIVE`。
- 依据，PDF p.270–271：高大bull reversal bar若位于range顶部附近，并没有真正“可反转”的趋势；直接买会在range高处成交。
- 当range已确认且signal bar高度≥`1.5ATR`、entry位于range顶部25%时，禁止stop追多；底部追空镜像。
- 等待breakout pullback和second entry，或回到有利边缘再评估。
- 大bar只能提高方向评分，不能绕过位置与regime门控。

### RANGES-C12-N02：强趋势中不机械逆势数 Low/High

- 类型：`NEGATIVE`。
- 依据，PDF p.267–270：强bull channel会以bear bars诱空，但没有好的breakout pullback；若错过后续多单，逆势scalp的数学期望更差。
- Tight bull channel条件：最近6bars bull bodies≥5、EMA上方无收盘、pullback≤2bars；此时禁用Low 2/3/4空，bear镜像。
- 只有强逆势breakout≥`1ATR`且随后形成第二入场pullback，才解除门控。
- Countertrend scalp必须单独回测，不能用随后顺势重入的收益掩盖亏损。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 256–259 | 趋势防守、双底/双顶旗、High/Low 2、两次失败 | 定义、S01–S03、S06 |
| 259–261 | continuation与reversal区别、错误突破转三推、入场止损 | S01–S02、S07–S08 |
| 261–264 | 动量判向、spike-channel回测、25%最低反弹、竞争形态 | S04–S05、S10 |
| 264–266 | failed bottom、双侧假突破、wedge/range等幅目标 | S07–S08 |
| 266–270 | sharp reversal、pause、强channel、测量目标与止损 | S09、N02 |
| 270–271 | failed breakout wedge、range位置门控、regime限制 | S06–S08、N01–N02 |

## 4. 回测验收

- S01/S02必须按当时regime分类；同一几何形态分别报告continuation与reversal结果。
- `same_price_band`至少网格测试 `max(1/2/3ticks, 0.10/0.20/0.30ATR)`，训练期选择后锁定。
- Swing确认只能在右侧确认bar以后生效；不得用最终图形回填第二底/顶。
- 分别统计exact、undershoot、overshoot，不删除“不完美”形态。
- S04入range前动量、range边界及breakout必须实时生成。
- S07的 `1–2bars` reclaim与S08的真突破互斥，每个事件只能进入一个主样本。
- 所有measured move在入场前固定来源；并列测量分别报告，不事后选择命中者。
- Stop entry计入gap/slippage，limit/stop-run逻辑计入未成交；风险按完整形态止损距离缩放。
- Figure 12.1–12.7只作章节例证，不作参数拟合或绩效证据。
