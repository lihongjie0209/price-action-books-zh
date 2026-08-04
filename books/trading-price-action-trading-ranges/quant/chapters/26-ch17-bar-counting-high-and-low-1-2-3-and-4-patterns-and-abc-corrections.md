# 第 17 章：Bar Counting——High/Low 1、2、3、4 与 ABC 修正

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/26-ch17-bar-counting-high-and-low-1-2-3-and-4-patterns-and-abc-corrections.md`
- PDF 页码：290–332
- 图表：Figure 17.1–17.13；正文与图注已完整说明规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 因果 Bar Counter

方向标准化后，在bull/range中的向下或横向pullback计High计数：

```text
high_event(t) = high[t] > high[t-1] + tick_epsilon
H1 = pullback开始后的第一次high_event
H2 = H1未产生bull swing、价格再向下/横向推进后的第二次high_event
H3/H4 = 同理的第三/第四次尝试
```

- Bear/range中镜像：`low[t] < low[t-1] - tick_epsilon`依次为L1–L4。
- 新attempt要求前一次之后至少发生一根同pullback方向bar，或极值继续 `>=1tick`；连续无分隔的突破不重复计数。
- H1与H2间最好有minor trend-line break/可见反弹；若没有，多个小计数可能仍是tight channel中的复杂第一腿。
- Outside bar的盘中先后顺序若无更细数据不可知：保守算法只按完成bar更新，另做lower-timeframe可得样本，不推测路径。
- 计数是识别两腿修正的工具，不是脱离regime、位置、动量的独立信号。

## 2. 规则卡

### RANGES-C17-S01：强趋势 Spike 中 High/Low 1

- 类型：完整顺势策略。
- 依据，PDF p.292、298–302、307–311：最佳H1/L1来自强趋势spike中的micro trend-line假突破；必须有强趋势、强spike、且没有显著climax。
- Bull版：bull regime明确；最近 `3–6bars` 净上涨≥`1.5ATR`、bull bodies≥70%、overlap≤0.35；首次1–4bar pullback形成H1。
- 排除：range顶部、buy climax、sideways≥5bars/多doji、仍低于显著旧高的vacuum spike。
- 入场：H1 signal高点上1tick stop；可同时在prior swing high放灾备stop，任一成交后取消另一单。
- 止损：signal/pullback低点下；目标1R/2R、旧极值；第3个连续H1仅按scalp或禁用。
- Bear版镜像；不得在bull trend卖L1或在bear trend买H1。

### RANGES-C17-S02：Bull/Bear Trend 中标准 High/Low 2（ABC）

- 类型：核心顺势策略。
- 依据，PDF p.290–291、302–307、328–332：H2/L2是两次修正尝试/ABC结束，趋势中通常在EMA附近，趋势方入场与逆势持仓退出共同增强延续。
- Bull版：bull regime；H1后pullback恢复向下/横向，再形成H2，且H1–H2之间存在minor-line break或可区分B腿。
- 入场：H2 signal高点上1tick；bear版L2低点下。
- 止损：完整ABC极值外。
- 目标：旧趋势极值、1R/2R、leg1=leg2；EMA接近度 `0–0.30ATR`作为评分而非硬条件。
- Signal为大doji、连续bear bars或第二腿明显过小则等待S08第二机会。

### RANGES-C17-S03：Trading Range 边缘的 H2/L2 反转

- 类型：区间边缘策略。
- 依据，PDF p.291–294、305：range中的H2是底部反转而非顶部延续，L2是顶部反转；错误位置的stop entry常被limit trader反向fade。
- H2仅在range底部25–35%、通常EMA下方考虑买；L2仅在顶部25–35%、通常EMA上方考虑卖。
- 入场：signal极值外stop，或保守等待第二信号；止损在range外/形态极值外。
- 目标：range中点、对侧、1R；tight range门控N01优先。
- H2在range顶部、L2在range底部不执行本策略，交给S04。

### RANGES-C17-S04：错误边缘 H1/H2/L1/L2 的 Failure Fade

- 类型：反向limit/失败突破策略。
- 依据，PDF p.291–292、298–302、310–311、325–326：range顶部H1/H2或底部L1/L2常由vacuum触发后立刻失败，适合经验型交易者反向fade。
- Setup：range已确认；buy count signal位于顶部20–30%，或sell count signal位于底部20–30%；signal为doji/大重叠加分。
- 激进入场：buy signal高点处/上方limit short；镜像limit long。保守入场：触发后 `0–2bars` 无follow-through并收回signal，按failure stop入场。
- 止损：range外或signal外 `0.5–1.0ATR`；目标range中点/1R。
- Limit版必须建模队列、未成交与穿透；普通研究默认保守failure版。

### RANGES-C17-S05：High/Low 2 Failure → 3 或 4

- 类型：形态演化状态机。
- 依据，PDF p.295–296、302–304、318、323–325：H2/L2若未获scalp即穿越形态另一端，通常再产生1–2推，演化为H/L3 wedge或H/L4复杂修正。
- Failure定义：stop entry触发后未达到预注册scalp `0.5–1.0R`，在 `1–3bars` 内越过signal/完整形态反端。
- 弱/普通breakout（bar<`1ATR`、无follow-through）：保持原regime，下一次计作H/L3，优先S06 wedge。
- 强breakout（≥`1ATR`或连续2根trend bars）：重置局部count，预期至少两推，等待H/L4或channel breakout pullback。
- H/L4也失败并突破完整形态极值时，重新判定Always-In，禁止第五次机械顺旧趋势入场。

### RANGES-C17-S06：High/Low 3 作为 Wedge Flag

- 类型：三推顺势/区间反转策略。
- 依据，PDF p.295–297、303–307：H3/L3功能上是wedge/triangle；命名取决于regime，关键是三推及动量。
- Bull/range中的三推下跌形成H3；bear/range中的三推上涨形成L3。
- 若H2失败后的下破动量未显著增强、到trend-channel line并出现reversal signal，买H3；bear版镜像。
- 入场：signal顺预期方向极值外stop；止损在第三推极值外。
- 目标：至少scalp/1R、旧极值、wedge高度。
- 强breakout/紧channel使H/L3禁用，等待S07或breakout pullback。

### RANGES-C17-S07：High/Low 4 复杂两腿修正

- 类型：四推/高周期H2策略。
- 依据，PDF p.292–298、303–304、317–320：H/L4常是两条大腿各分两小腿的高周期H/L2，或spike-and-channel；只在整体背景仍支持原趋势时交易。
- Setup：H/L2失败后完成两条额外push；整体非强反向trend，至少曾有minor-line break/原趋势强度证据。
- 入场：H4高点上买/L4低点下卖；更安全版等待tight countertrend channel breakout及pullback。
- 止损：完整四推形态极值外；小doji signal使用 `max(2–3ticks, 0.20ATR)` 缓冲，但总止损不得超过风险上限。
- 目标：旧极值、完整形态高度measured move、1R/2R。
- L4/H4形成时regime已翻转，或完全无原方向强度，禁止交易。

### RANGES-C17-S08：不完美 H2/L2 Variant 与第二机会

- 类型：宽松两腿识别策略。
- 依据，PDF p.294–295、304–305、307–315、325–330：两腿可隐藏在bar内部、bull/bear close、outside/inside bar或高周期结构；目标是识别修正而非追求完美编号。
- 若标准counter未产生H2，但存在两个方向一致的pivot pushes，中间有反向close/内部摆动≥`0.15ATR`，标记variant。
- Variant score：两腿大小比 `0.5–2.0`、第二信号方向body、EMA/区间边缘、minor-line break各加分。
- 首signal质量差时等待下一根方向bar或第二次同类signal再入场；止损为完整两腿极值。
- 低周期验证仅能使用实时同步数据；没有低周期数据时不得假定bar内顺序。
- 标准与variant结果分开报告，避免扩大定义后伪造稳定性。

### RANGES-C17-S09：Failed Countertrend Count 的顺势 Reversal

- 类型：被困交易者驱动的顺势策略。
- 依据，PDF p.302–307、309、314–315、320–324：强趋势中的逆势L2/H2大多失败；触发点迫使逆势仓退出并吸引顺势方，常成为强入场。
- Bull版：bull regime中L1/L2 short触发但未达scalp，随后突破其signal/entry bar高点；bear版镜像。
- 入场：failure breakout或首次pullback；止损在失败结构极值外。
- 目标：旧趋势极值、failure结构高度、1R/2R。
- 若此前已有major trend-line break和强反向动量，则countertrend setup可能有效，不自动fade。

### RANGES-C17-S10：强 H2/L2 触发时退出并可反转早期逆势仓

- 类型：持仓管理/反手覆盖层。
- 依据，PDF p.306–307：在强bear中早买者应在L2/L3触发时退出，强bull中早空者在H2/H3触发时退出；强signal时可反手。
- 若持有逆regime仓位且未达目标，对侧顺势H/L2或3触发时强制退出。
- 反手仅在signal方向body≥`0.5`、位置合理且剩余空间≥1R时执行；否则只平仓。
- 原仓亏损不影响反手仓位，仍按固定账户风险计算。
- 回测分别报告“只退出”与“退出+反手”，不得合并掩盖执行差异。

### RANGES-C17-S11：计数失败引发 Regime Flip

- 类型：市场状态转换。
- 依据，PDF p.292–293、295–296、303–304、319–321：L4失败表示bear失控，H4失败表示bull失控；强channel breakout后应停止寻找旧方向pullback。
- H/L4实际触发后，若 `1–3bars` 内突破完整pattern另一端且有strong breakout/follow-through，发出`count_regime_failure`。
- 至少转为two-sided；若同时突破major swing、EMA并形成同向spike，则Always-In翻转。
- 翻转后只运行新regime允许的H/L规则，旧counter清零。
- 单tick stop-run且立即恢复不构成flip，特别是小signal bar缓冲范围内。

### RANGES-C17-S12：Spike-and-Channel 作为两腿修正

- 类型：替代分段组件。
- 依据，PDF p.292、317–318、326–332：gap/spike可作第一腿，后续channel作第二腿；channel内部的两推仍可只是第二大腿的细分。
- Spike要求 `2–5bars >=1.5ATR`；channel至少两个同向push且平均斜率/动量低于spike。
- 输出`macro_leg_count=2`，同时保留channel内micro count；后续交易使用宏观结束位置。
- Channel第三推、trend-channel overshoot、double top/bottom或第二signal共振时提高结束评分。
- 不因“已两腿”直接逆势，仍需S06/S07或breakout failure确认。

### RANGES-C17-N01：Tight Trading Range 禁用 Bar-Count Stop Entry

- 类型：`NEGATIVE`。
- 依据，PDF p.293–295、310–318、321–323、330–331：tight range内H/L1–4密集互相矛盾，stop entry位于错误边缘，机械全交易会快速累积亏损。
- 连续≥5bars、overlap≥0.65、净位移≤`0.5ATR`、doji≥2时确认tight-range候选。
- 除非它是强趋势spike后的small flag，否则禁用所有纯bar-count stop entries，等待breakout+follow-through/pullback。
- 强趋势small flag只允许顺trend breakout，不运行双向计数。
- 经验型limit fade属于S04独立实验，不与普通counter结果合并。

### RANGES-C17-N02：Bar Count 不能覆盖 Regime 与 Momentum

- 类型：`NEGATIVE`。
- 依据，PDF p.292–304、312–324：bull trend不卖L1/L2，bear trend不买H1/H2；没有趋势线break/方向强度时，即使H/L4也不足以入场。
- 每笔候选必须先通过`allowed_direction(regime)`；不允许的方向直接拒绝。
- Countertrend只在已发生强trend-line break、second attempt和合格reversal背景下开放。
- 若对是否足够强需要额外寻找罕见视图来证明，默认跳过；不以inverse ETF或高周期事后确认替代当前信号。

### RANGES-C17-N03：Climax 后禁用首个 H1/L1

- 类型：`NEGATIVE`。
- 依据，PDF p.298–301、307–308、320：H1/L1需要strong trend而非exhaustion；climax/final flag后通常至少两腿、约10bars修正。
- Climax：趋势已持续且末端bar≥`1.5ATR`、三推加速、连续扩大body或trend-channel overshoot，任两项。
- Climax后首H1/L1禁用，直到完成两腿/≥10bars修正或新strong breakout重建趋势。
- Range边缘vacuum spike同样禁用，即使连续出现3–4根trend bars。

### RANGES-C17-N04：小 Doji H/L4 的单 Tick 技术失败

- 类型：执行约束。
- 依据，PDF p.297–298、304、318–320：小H/L4 signal常先越界1tick扫止损再按预期运行，机械1tick止损会产生whipsaw。
- Signal range≤`0.35ATR`或doji时，结构止损缓冲测试 `2–3ticks / 0.15–0.25ATR`。
- 总初始风险超过预注册上限（如`0.8–1.0ATR`）则缩仓或跳过，不扩大账户风险。
- 缓冲参数必须跨市场用tick/ATR归一化，不能直接移植书中Emini固定点数。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 290–294 | H/L1–4定义、ABC、趋势与range位置差异、regime限制 | 定义、S01–S04、N01–N02 |
| 294–298 | variant、H/L2失败扩展、H/L3 wedge、H/L4及小bar止损 | S05–S08、N04 |
| 298–302 | spike阶段H/L1、climax/vacuum过滤、range边缘fade | S01、S04、N03 |
| 302–307 | H/L2失败、动量决定3或4、趋势中可靠性与反手 | S02、S05–S10 |
| 307–312 | 案例中的H/L1–2质量、强趋势与range对照 | S01–S04、S08–S10 |
| 312–318 | 无minor break的假计数、复杂两腿、tight range、强度门控 | S05–S08、N01–N02 |
| 318–324 | failed L2/L4、small signal stop、regime flip、强channel | S05–S07、S09–S11、N04 |
| 324–328 | exhaustion与measuring breakout、variant、wedge和第二信号 | S05–S08、S12 |
| 328–332 | H/L2多种bar内结构、EMA背景、tight range与spike-channel | S02、S08、S12、N01 |

## 4. 回测验收

- Counter逐bar保存状态、attempt编号、触发bar和失效原因；不得用最终pivot回填。
- Outside bar无法获知盘中路径时采用保守单次事件；有1分钟数据的子样本单独验证。
- 标准H/L2、variant、H/L3、H/L4样本互斥主标签，同时可保存辅助解释。
- Regime至少使用两种预注册分类器稳健性验证，所有方向违规交易数量必须为零。
- H/L2 failure的scalp阈值、观察窗与strong-breakout阈值在训练集锁定。
- S01按第1/第2/第3+次H/L1分层，验证随趋势成熟度变化的期望值。
- S04 limit与failure-confirmation版本独立报告成交率、滑点、MAE/MFE。
- S05记录weak breakout→3、strong breakout→4/flip的条件转移矩阵。
- Tight-range与climax门控必须从确认bar开始，不能事后回填。
- 所有固定tick示例按标的tick size与ATR归一化，并计入手续费/滑点。
- Figure 17.1–17.13只作章节例证，不作参数拟合或绩效证据。
