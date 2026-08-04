# 第 18 章：Wedge 与其他三推回调

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/27-ch18-wedge-and-other-three-push-pullbacks.md`
- PDF 页码：333–343
- 图表：Figure 18.1–18.9；正文与图注足以定义规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 三推定义

方向标准化后，bull trend中的wedge bull flag为三次向下push：

```text
push_i = 新的countertrend swing extreme
separation = 两push间反弹 >= max(2ticks, 0.20ATR) 或 >=2bars
three_push = 三个已确认push，允许第2/3推undershoot、overshoot或failure swing
```

- Bear flag镜像；形态可收敛、平行、扩张、横向或不规则，三推比画出完美wedge线更重要。
- 典型flag持续 `10–20bars`；大于约20bars且方向同原趋势末端的wedge更可能是reversal候选。
- Triangle通常至少五小腿；实现可将三次同侧push作为交易摘要，同时保存全部pivot序列。
- Swing只从确认bar后可用；best-fit line仅作辅助评分，不得未来重画触发。

## 2. 规则卡

### RANGES-C18-S01：趋势中的三推 Wedge Flag 第一信号

- 类型：完整顺势策略。
- 依据，PDF p.333–335、341–343：下倾三推是bull flag、上倾三推是bear flag，通常顺大趋势突破；顺势flag可在第一信号入场且不必完美。
- Setup：明确trend regime；countertrend完成3个push，持续主测 `8–25bars`，未形成强Always-In反转。
- Signal：第三推后出现顺趋势reversal bar、H/L3、micro-line breakout或double top/bottom。
- 入场：signal顺趋势极值外1tick stop。
- 止损：第三推/完整flag最终极值外。
- 目标：旧趋势极值、1R/2R、flag高度；强恢复可保留swing。
- Tight countertrend channel或第三推仍强时交给S02，不机械首信号入场。

### RANGES-C18-S02：陡峭 Wedge / 强两推后的第二入场

- 类型：保守breakout-pullback策略。
- 依据，PDF p.333–337、339–340：wedge较陡、连续下跌bar多或前两推动量都强时，首信号风险高，应等channel breakout及higher/lower-low pullback。
- 强度门槛：最近两push各≥`0.8ATR`，countertrend bodies≥60%，或tight channel overlap≤0.35。
- 等待顺大趋势breakout；要求breakout bar≥`0.5ATR`且不立即完全回撤。
- 入场：breakout后的higher low/lower low（bear镜像higher/lower high）第二信号。
- 止损：pullback最终极值外；目标channel起点、旧趋势极值、1R/2R。
- 若breakout弱并重新进入channel，停止追价并重新判断range/reversal。

### RANGES-C18-S03：Spike-and-Channel Wedge Pullback

- 类型：结构变体策略。
- 依据，PDF p.333–335、339–342：pullback可由countertrend spike加两次channel push组成；平行channel同样是可靠三推flag。
- Countertrend spike：`1–4bars >=1.0ATR`；随后channel至少两次同方向push，合计视为三推。
- 第三个push到trend-channel line/EMA/旧swing附近并出现signal时按S01入场。
- 若前两段动量强则使用S02第二入场。
- 最低目标：countertrend channel起点；扩展为leg1=leg2及旧趋势极值。
- 同时保存“几何wedge/平行channel”标签，检验形状是否提供增量，而非硬性筛选。

### RANGES-C18-S04：Trading Range 内三推边缘 Fade

- 类型：区间反转策略。
- 依据，PDF p.334、336–337：range中的wedge兼具flag/reversal特征；两边交易清楚且位置好时第一信号可盈利，有疑问等第二信号。
- Setup：range已确认；三推到达顶部/底部25%，且有two-sided bars。
- 强signal版本在第一reversal signal入场；重叠高、channel陡或signal弱时等待第二entry。
- 止损：range边界外或第三推极值外。
- 目标：range中点、对侧、1R。
- Middle-third或tight range禁用，除非已有强spike明确方向。

### RANGES-C18-S05：Wedge Reversal 的 Breakout-Pullback

- 类型：逆势确认策略。
- 依据，PDF p.333–334、336：wedge reversal逆主趋势，通常应等第二入场；有效大反转一般≥20bars并有清晰trend-channel line。
- 候选：顺旧趋势方向三推、持续≥`20bars`，第三推测试/越过trend-channel line并出现climax迹象。
- 不在首reversal signal直接逆势；等待强breakout（≥`1ATR`或连续2bars）及higher/lower-high breakout pullback。
- 入场：第二信号；止损在旧趋势最终极值外。
- 目标：EMA、channel起点、两腿、1R/2R。
- Weak breakout预期失败并恢复旧趋势，转S06。

### RANGES-C18-S06：Weak Wedge-Reversal Breakout Failure

- 类型：旧趋势恢复策略。
- 依据，PDF p.333–334：逆势wedge breakout若弱，交易者应预期失败并按旧趋势恢复入场。
- Weak定义：breakout<`0.5ATR`、无方向close、`1–3bars` 内返回wedge/旧channel。
- 入场：failed breakout的reclaim signal顺旧趋势极值外stop。
- 止损：failed breakout最终极值外。
- 目标：旧极值、1R/2R、wedge高度。
- 与S05互斥：一旦strong breakout确认，本规则关闭。

### RANGES-C18-S07：第三推 Failure Swing

- 类型：不规则wedge变体。
- 依据，PDF p.333、337、342：第三推无需超过第二推；failure swing仍可完成wedge，第二腿也常越过先前swing。
- 第3个pivot未创新countertrend极值但距第2极值≤`0.10–0.30ATR`，且其后顺趋势breakout，标记failure-swing wedge。
- 入场/止损沿用S01或S04，具体取决于regime。
- 单独报告创新极值、equal和failure swing三类结果。
- 不因线条不收敛而剔除；必须仍满足三个时间分离push。

### RANGES-C18-S08：Gap Spike + 三推回调的 Trend Resumption

- 类型：开盘/跨日趋势恢复策略。
- 依据，PDF p.335–338：大gap可视作首个bull/bear spike，随后三推sideways pullback形成channel并恢复趋势，目标可用gap高度测量。
- Gap归一化：`abs(open-prior_close) >= 0.5–1.0ATR_daily`；方向与预期trend一致。
- 开盘后完成三次countertrend push，第三推不必创新极值。
- 入场：第三推后的顺gap方向signal或breakout pullback；若开盘直接越过stop价，不在gap上追单，等待可成交触发。
- 止损：pullback极值外；目标为gap spike高度投影、leg1=leg2、1R/2R。
- Corporate action与session discontinuity清洗后才生成gap。

### RANGES-C18-S09：Wedge Flag Failure → Measured Move

- 类型：失败形态顺新方向策略。
- 依据，PDF p.343：wedge bull flag无可靠signal、进入tight range并向下突破，说明形态失败；breakout可成为spike并走形态高度measured move。
- Failure确认：第三推后无合格顺趋势signal，形成≥3bar tight range；随后反向breakout≥`0.75ATR`并follow-through。
- 入场：breakout close或首次pullback；止损在tight range内部/另一侧。
- 目标：wedge或tight-range高度measured move、1R/2R；强breakout允许trail channel。
- 只有实际突破确认后才切换方向，不能因signal弱提前逆势。

### RANGES-C18-N01：Exact Shape 与完美 Trend Lines 非必要

- 类型：`NEGATIVE`。
- 依据，PDF p.333–335、339–342：三推可以不规则、平行或扩张，trend line允许穿越；标签与精确计数不是交易核心。
- 不以两条线必须收敛作为硬条件；line fit仅输出斜率、残差和穿越次数。
- 至少三push的时间顺序和regime方向才是硬条件。
- 多种解释可保存辅助标签，但同一事件只计一次主交易。

### RANGES-C18-N02：强 Countertrend Channel 中不抢首反转

- 类型：`NEGATIVE`。
- 依据，PDF p.336–340：七根连续下跌、紧channel或两推强动量时，即使已到三推，首signal仍可能不足。
- 连续countertrend bodies≥4、最近push≥`1ATR`或channel efficiency≥0.70时，禁用S01首signal。
- 必须等待S02 breakout-pullback或明确Always-In flip。
- 该门控从当下强度计算，不因后来成功反转回填解除。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 333–335 | wedge/triangle定义、三推、flag与reversal、首/第二信号 | 定义、S01、S05–S07、N01 |
| 335–337 | 低动量三推、range wedge、陡峭/连续bar等待 | S02、S04、N02 |
| 337–339 | gap spike、failure swing、跨尺度bear flag | S07–S08 |
| 339–341 | higher-high breakout pullback、spike-channel、最低channel起点目标 | S02–S03 |
| 341–343 | 多重三推解释、不精确线条、failed wedge measured move | S03、S07、S09、N01 |

## 4. 回测验收

- Pivot保存发生与确认时点；第三推只能从确认时刻产生signal。
- 三推检测至少比较固定ATR pivot与固定bar-count算法，主版本样本外锁定。
- Wedge flag、range wedge、wedge reversal互斥主标签，并按regime分别报告。
- S01与S02按动量门槛分流，不能让同一事件同时贡献两笔盈利。
- S05 strong/weak breakout标准在入场前确定；S05/S06样本互斥。
- Failure swing、equal、overshoot/undershoot分别报告。
- S08 gap订单模拟不得假设跨价stop成交在原stop价。
- S09测量高度来源在入场前固定，不从多个候选中事后挑命中者。
- Figure 18.1–18.9只作章节例证，不作参数拟合或绩效证据。
