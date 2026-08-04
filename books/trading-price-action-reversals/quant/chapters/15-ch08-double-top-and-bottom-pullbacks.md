# 第 8 章：Double Top and Bottom Pullbacks

## 元数据

- 英文来源：`books/trading-price-action-reversals/en/chapters/15-ch08-double-top-and-bottom-pullbacks.md`
- PDF 页码：231–237
- 图表：Figure 8.1–8.4；正文与图注已完整说明规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Pattern 统一定义

```text
bottoms: L1 ≈ L2, breakout_up, pullback L3 ≳ L1/L2, reversal_up
tops:    H1 ≈ H2, breakout_down, pullback H3 ≲ H1/H2, reversal_down
```

- 第三个极值可高于、等于或越过前两个极值；double-bottom pullback、triple bottom、triangle、H&S、final flag是同一三推/突破回调行为的不同外观。
- `≈`容差建议`0–0.30ATR`并同时考虑tick/spread；几何名称不产生额外edge。
- Reversal pattern发生在新趋势开端；double bottom/top flag是已建立趋势中的continuation，须分开标注。

## 2. 规则卡

### REVERSALS-C08-S01：Loose Double-Extreme Detector

- 类型：前两次测试检测。
- 依据，PDF p.231–233：double不必精确，第二bottom略低通常可取，严格同tick定义过于稀少且无交易价值。
- 两confirmed pivots间隔`2–30bars`，价格差≤`0.10–0.50ATR`。
- 第二bottom略低/第二top略高作为failed-breakout加分；明显未达第一极值由S06降级。
- Entry-bar extreme也可作为第一个bottom/top，不强求传统swing标签。

### REVERSALS-C08-S02：Intervening Breakout Strength Gate

- 类型：反转前置强度。
- 依据，PDF p.231–234：第二极值后的rally/selloff通常是breakout，强到足以让交易者考虑range或trend reversal；pullback因而是可靠breakout pullback。
- Bull：L2后move突破局部bear trend line/EMA/previous swing high之一，累计≥`0.75–1.5ATR`；bear镜像。
- 仅2bars也可，但需strong bodies/close；弱move使setup只按scalp或等待confirmation。
- Breakout level与strength在L3形成前冻结。

### REVERSALS-C08-S03：Third-Test Pullback Entry

- 类型：核心反转策略。
- 依据，PDF p.231–234、236–237：第三次回调测试double extreme但卖/买方不足，形成breakout pullback与three-push reversal。
- L3/H3在前两极值区域`±0.30ATR`，出现strong reversal bar、outside bar或second signal。
- Entry在signal trigger；stop在L3下/H3上`1tick–0.15ATR`。
- Target1=intervening breakout extreme，Target2=range/pattern measured move或2R。

### REVERSALS-C08-S04：Three-Failed-Extreme Attempts Score

- 类型：形态强度组件。
- 依据，PDF p.231–232：第三次无法延伸旧趋势说明两次/三次突破尝试失败，通常导致反向move。
- 统计每次旧方向extension与follow-through；extension递减、快速收回及strong signal提高score。
- 第三极值不创新低/高不作为必要条件，但“不再延伸”加分。
- 与S03合并，不重复生成交易。

### REVERSALS-C08-S05：Strong-Signal / Shape Reliability Tier

- 类型：质量分层。
- 依据，PDF p.231–232：形状清楚且三个极值的reversal bars强，尤其第三个强时，是较可靠setup。
- Signal score：body/range≥`0.50–0.70`、close末端25%、tail拒绝、next-bar follow-through。
- High tier可first trigger并保留50% swing；medium tier减仓/只取Target1；low tier等second entry。
- 概率必须样本外校准，不直接采用书中60%。

### REVERSALS-C08-S06：Second Bottom/Top Undershoot Downgrade

- 类型：弱形态过滤。
- 依据，PDF p.231、234–236：若第二bottom明显高于第一，可能只是bear trend中的two-legged rally；强趋势首次pullback尤其如此。
- `L2-L1 > 0.20–0.50ATR`且无S02 strong breakout时，降为scalp-only/old-trend flag；top镜像。
- Strong opening-reversal context可作为例外，但仍须signal与成本后EV。
- 不因偶然后续大rally事后把弱setup升格。

### REVERSALS-C08-S07：Double Pullback as MTR / H&S Variant

- 类型：结构共振。
- 依据，PDF p.231–234、236–237：pattern常同时是HL/LH MTR、H&S、triangle或failed final flag。
- 若S02已显著破major trend line且L3/H3为test，增加MTR score及runner比例。
- 共振形态共享同一event ID，不作为多个独立理由相乘概率。
- Target按MTR break extreme/2 legs与S03结构目标较近者分批。

### REVERSALS-C08-S08：Range with Both Double Top and Bottom

- 类型：triangle/breakout-mode状态。
- 依据，PDF p.232、235–237：同一range内同时有double top和bottom通常形成triangle；价格回中部再测试一侧，最终等待breakout。
- Confirmed upper/lower各≥2 tests；range height≥成本后`2R`可边缘scalp，否则只等待breakout。
- Strong breakout+follow-through顺方向交易；failed breakout反向交易。
- Range中部不新开fade，同一母range避免双向样本重复。

### REVERSALS-C08-S09：Strong Breakout Pullback Confirmation Entry

- 类型：较晚高概率入场。
- 依据，PDF p.232–233：可在outside-up trigger、随后strong close/high或连续trend bars确认新趋势后入场。
- S03错过/质量中等时，等待`1–3bars`方向follow-through或first shallow pullback。
- Stop在L3/H3或confirmation swing外，qty按更宽risk缩小。
- 与early S03比较胜率、剩余reward和净EV。

### REVERSALS-C08-S10：Bear/Bull Flag Reclassification

- 类型：premise切换。
- 依据，PDF p.234–236：弱double-bottom setup在strong bear trend常只是bear flag；失败后L2/EMA short更合理，bull镜像。
- Tight old trend、首次pullback、S02未成立或entry未触发时，标记continuation candidate。
- 出现old-trend L2/H2 strong signal时撤销反转order并顺趋势入场。
- 反转与continuation路径共享episode，不能按结果只保留赢家。

### REVERSALS-C08-S11：Accumulation / Repeated Defense Feature

- 类型：重复低点防守代理。
- 依据，PDF p.234：多次测试低点而无法跌破可视为accumulation；顶部镜像distribution。
- 在`5–30bars`内≥3次test，penetration≤`0.10ATR`，每次close回range且downside follow-through弱。
- 只作S03/S05加分，不推断不可观察的机构意图。
- Strong break+follow-through立即取消，转S10/新趋势。

### REVERSALS-C08-S12：Failed Pullback Reversal / Five-Tick Failure

- 类型：反转失败切换。
- 依据，PDF p.236–237：double-top pullback short等可能只走小幅后失败，并形成moving-average反向setup。
- Entry后MFE<`0.5–1R`且`1–3bars`强穿signal另一端/stop，定义failed event。
- 等独立opposite reversal/MA test signal后反手；新交易重算EV、stop与qty。
- 固定5ticks改用`0.10–0.30ATR`，原亏损与反手分开记录。

### REVERSALS-C08-S13：Inside-Bar Completion of Small Pullback

- 类型：微型pattern执行。
- 依据，PDF p.235–236：double bottom/top之后inside bar本身是pause/pullback，可完成小型double pullback setup。
- Pattern span可小至`3–8bars`；inside bar需位于range edge/顺新趋势pullback。
- Entry在inside break顺setup方向，stop在mother bar/third extreme外。
- Strong old trend逆势时只scalp或由S06/S10否决。

### REVERSALS-C08-N01：禁止要求三极值精确同 Tick

- 类型：`NEGATIVE`检测约束。
- 依据，PDF p.231–232：精确triple定义稀有且人为；相似模式按相似行为交易更有用。
- 使用连续距离与shape-quality，不能因1–数ticks差异删除样本。
- 同时禁止过宽容差把任意三低点都标成pattern。

### REVERSALS-C08-N02：Strong Tight Trend 中不盲目 Bottom/Top Picking

- 类型：`NEGATIVE`硬否决。
- 依据，PDF p.234–236：无prior strong trend-line break时，tight bear channel的double-bottom pullback多为bear flag，top镜像。
- S02未成立且old-trend strong时，countertrend实际交易数为零或仅预注册opening scalp例外。
- 等strong breakout+pullback或final-flag/MTR confirmation。

### REVERSALS-C08-N03：形态名称不得重复放大置信度

- 类型：`NEGATIVE`模型约束。
- 依据，PDF p.231–237：triangle、triple、H&S、MTR、flag等常描述同一价格行为。
- 同一event内相关shape features组内封顶，不能把五个名称当五个独立证据。
- 报告统一三推母样本与各外观子组。

### REVERSALS-C08-N04：固定 60% / 70% 与 Tick 距离不作常数

- 类型：`NEGATIVE`参数约束。
- 依据，PDF p.232、235–237：概率与美分/tick为案例近似。
- 概率需walk-forward calibration；距离按ATR/spread/tick归一。
- Figure 8.1–8.4精确路径不得作为拟合标签。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 231–232 | double pullback定义、三推统一、breakout pullback、强shape、reversal/flag区别与triangle | S01–S08、N01、N03–N04 |
| 233 | Figure 8.1：outside/confirmed entries、略低第二bottom、breakout pullback、bear flag区别 | S01–S03、S07、S09–S10 |
| 234 | Figure 8.2：weak first reversal、double defense/accumulation、MA gap、HL MTR | S03、S07、S10–S11、N02 |
| 235–236 | Figure 8.3：明显higher second low降级、strong trend否决、inside-bar微型setup与triangle | S06、S08、S10、S13、N02 |
| 236–237 | Figure 8.4：entry-bar extremes、三次stop test、double top pullback failure与MA reversal | S01–S04、S07、S11–S12 |

## 4. 回测验收

- L1/L2/L3或H1/H2/H3均保存pivot确认与valid_from；未来重画次数为零。
- 统一事件下的double/triple/triangle/H&S/MTR名称不得重复计交易或概率证据。
- 分开报告reversal trend、trading range、old-trend flag、entry-not-triggered和failed reversal。
- Early S03、confirmed S09、continuation S10及failure S12在同一母样本比较净EV、MAE/MFE。
- Strong-tight-trend无break禁令、精确tick强制和相关形态重复计分设自动测试。
- OHLC同bar触发/止损顺序用不利路径，全部计slippage、gap和成本。
- 价格容差、bar窗口与probability model做walk-forward、跨品种/周期/volatility sensitivity。
- Figure 8.1–8.4仅作章节例证，不作参数或绩效证据。
