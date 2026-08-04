# 第 25 章：Trading Guidelines

## 元数据

- 英文来源：`books/trading-price-action-reversals/en/chapters/35-ch25-trading-guidelines.md`
- PDF 页码：505–518
- 图表：无
- 状态：量化研究规格，未经回测；原文78条为guidelines而非绝对规则
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Guideline Engine

```text
decision = regime_gate ∧ direction_gate ∧ setup_gate ∧ equation_gate ∧ execution_gate ∧ operator_gate
operator_state ∈ {READY, DISTRACTED, FATIGUED, UPSET, REVENGE_RISK}
trade_allowed = all gates pass
```

- 主观语言必须转换为可记录的代理并做敏感性检验；“close enough”通过ATR/tick容差表达。
- 行为建议不应伪装为历史alpha；其价值要通过减少坏交易、执行偏差和尾部亏损的增量实验验证。

## 2. 规则卡

### REVERSALS-C25-S01：Dual-Hypothesis Bar Evaluation

- 类型：每bar决策接口。
- 依据，guidelines 8–13，PDF p.506–507：每bar都可双向触发，关键是判断prior high/low上下谁更强，并考虑反向突破困住交易者。
- 每bar同时生成long/short score：趋势、位置、signal quality、突破跟进、trapped-side和空间。
- 只有一侧净EV超过门槛才下单；两侧接近则UNCERTAIN，不强选方向。

### REVERSALS-C25-S02：Calibrated Trader-Equation Gate

- 类型：数学准入。
- 依据，guidelines 3–7、14–15、58–60，PDF p.505–507、515：edge小且概率共存，任何正净EV结构均可，但过度自信会高估概率。
- 使用walk-forward校准概率下置信界计算`p×reward-(1-p)×risk-cost`。
- 主版本要求reward≥risk；高置信/低置信不得使用作者口头概率替代实测分布。

### REVERSALS-C25-S03：Trend/Range Inertia Router

- 类型：状态路由。
- 依据，guidelines 16–18、44–47、54，PDF p.507–508、512–515：trend中多数反转失败，range中多数突破失败；不确定即按range低买高卖。
- Regime基于EMA同侧、斜率、overlap、tails和突破跟进；明确trend只顺AI，range只在边缘。
- Pullback深度/反向spike达到flip阈值则更新状态，不靠情绪继续称为pullback。

### REVERSALS-C25-S04：Price-First Surprise Response

- 类型：预期失效处理。
- 依据，guidelines 10–12、18–21、PDF p.506–508：价格与预期相反且给强setup时应接受并交易实际结构。
- Signal反向破坏premise时先平仓；新方向仍需独立通过S01–S02，不自动报复性反手。
- Fundamentals/news只做已知事件风险标记，不覆盖价格状态。

### REVERSALS-C25-S05：Protective-Stop Invariant

- 类型：硬风险控制。
- 依据，guidelines 24、29、PDF p.509–510：始终有保护stop；宽结构风险通过缩仓而非无stop/窄化。
- 成交时同时提交结构stop/OCO；异常撤单或无保护敞口触发kill switch。
- Qty按固定账户风险和R计算，wide-stop setup可降至`25%`常规仓位。

### REVERSALS-C25-S06：I-Don't-Care Position Sizer

- 类型：行为风险代理。
- 依据，guidelines 27–29，PDF p.509–510：若连续漏掉有效signal、不能承受2–3连亏或等待完美setup，说明仓位过大。
- 记录eligible但未执行率、提前退出和stop干预；超过阈值时下一session size降`50%–75%`。
- 恢复需连续样本外执行合规与正净EV，不因单日盈利扩仓。

### REVERSALS-C25-S07：Strict Countertrend Reversal Gate

- 类型：反趋势准入。
- 依据，guidelines 30–34、56–57、62、73，PDF p.510–511、515–517：多数反转失败，需显著趋势线break、旧极值测试和强反转bar。
- 未满足全部MTR组件时禁止countertrend；亏损月份配置直接关闭全部reversal模块。
- 原趋势setup用于退出反趋势仓，并可在新独立signal下顺势重入。

### REVERSALS-C25-S08：Failure-of-Failure Breakout Pullback

- 类型：高可靠失败策略。
- 依据，guidelines 35–37、67，PDF p.511、516：pattern失败及其失败会形成原方向breakout pullback；stop run后恢复趋势亦可靠。
- 首失败收回结构，随后又被原方向强bar+跟进否定时，按原方向入场。
- 标记trapped-in与trapped-out两类，目标至少`1R`/prior extreme。

### REVERSALS-C25-S09：Reengagement Delay after Inattention

- 类型：操作员状态门控。
- 依据，guideline 38，PDF p.511：离开市场`30–60min`后突然大breakout不应仓促追入。
- Detect inactivity/窗口失焦/无recent annotations；恢复后等待至少`1–3 bars`或首pullback。
- 自动系统不受注意力门控，但仍需execution latency和S02。

### REVERSALS-C25-S10：Single-Chart Simple Workflow

- 类型：复杂度控制。
- 依据，guidelines 28、40、42，PDF p.510–512：只看一张5分钟图、少指标，初始策略用EMA顺势pullback和stop entry。
- 生产信号源冻结为单market/timeframe；额外周期只能离线研究，不作为实时共同确认必需项。
- 初学者模板：bull EMA bull-bar H2 long / bear镜像，prior extreme减仓，余仓BE。

### REVERSALS-C25-S11：Opening Swing Discipline

- 类型：时段策略。
- 依据，guideline 49，PDF p.513–514：首`1–2h`swings大但反转多，初学者等待潜在≥2R swing而非过度scalp。
- Opening窗口只开放强reversal、trend-from-open pullback和second entry；普通候选降级。
- 若首小时违规/亏损，不在后半日提高频率或风险追平。

### REVERSALS-C25-S12：Daily-Loss Style Lock

- 类型：追损保护。
- 依据，guidelines 50、65–66，PDF p.514、516：亏损日后半段不能改风格、加仓或降门槛；疲劳/报告时电脑优势更强。
- Session内参数、setup whitelist和risk tier冻结；drawdown后只允许保持或缩小。
- Report blackout、fatigue/distraction标记或连续执行错误触发停止新仓。

### REVERSALS-C25-S13：Tight-Range Kill Switch

- 类型：硬环境禁入。
- 依据，guidelines 51–53、69，PDF p.514、517：日中、range中部、flat EMA、prominent tails的tight range是stop-entry最差环境且压倒其他setup。
- Tight-range classifier成立时所有方向stop entries关闭，直到强breakout+跟进/回调。
- Edge limit-fade只在专家隔离版本开放。

### REVERSALS-C25-S14：With-Trend Pullback Core

- 类型：核心生产策略。
- 依据，guidelines 42、54–57、61，PDF p.512、514–516：清晰趋势中同向EMA pullback/H2/L2是初学者与多数交易者核心。
- 最近`7/10`bars多数在EMA同侧可作保守方向代理；结合AI和结构确认。
- 只用同方向trend signal bar stop entry；目标≥1R，strong swing版本≥2R。

### REVERSALS-C25-S15：Signal-Bar Quality Gate

- 类型：触发质量。
- 依据，guideline 55、69，PDF p.515、517：同方向trend bar最佳；doji是一bar range，通常不宜在其上下追突破。
- Countertrend与range-middle要求严格趋势棒；顺强趋势可适度放宽但仍需context。
- Doji只能在多重强context下作为次级signal，单独不触发。

### REVERSALS-C25-S16：Two-Leg and Double-Failure Engine

- 类型：结构期望。
- 依据，guideline 67，PDF p.516：持续寻找两腿；同一方向两次尝试失败，倾向相反方向成功。
- Pivot legs用`1–5 bars`确认与ATR容差；第二失败后需反向触发bar。
- 新强spike可覆盖两腿预期，避免机械计数。

### REVERSALS-C25-S17：Consistent Selection Policy

- 类型：防cherry-pick。
- 依据，guideline 68，PDF p.516：要么只做每日最好的2–3个swing，要么执行所有预定义scalp；不可随意挑选。
- 预先冻结`mode ∈ {SELECTED_SWING, SYSTEMATIC_SCALP}`；session中不可切换。
- 记录所有eligible/missed signals，评估选择偏差和漏单成本。

### REVERSALS-C25-S18：Premise Revalidation Exit

- 类型：持仓复核。
- 依据，guideline 70，PDF p.517：假装空仓，若此刻不会建立完全相同仓位则退出。
- 每bar重算regime、direction、stop/target和time validity；净EV或核心premise失效即退出。
- 该规则不能把正常swing pullback误判，需与初始持仓窗口/结构stop共同测试。

### REVERSALS-C25-S19：Plan-Preserving Bracket Execution

- 类型：防风格漂移。
- 依据，guidelines 71–72，PDF p.517：不得把低概率swing临时变成小scalp，或把scalp利润降至risk以下。
- Entry时冻结`SCALP/SWING`、stop和target；修改必须由预定义market-state事件触发。
- 行为版本可提交bracket后禁用人工修改`30–60min`，但保留紧急kill switch。

### REVERSALS-C25-S20：Review-and-Scale Process

- 类型：研究治理。
- 依据，guidelines 63–64、74–78，PDF p.516–518：长期逐图标注、只做best trades、纪律优先，稳定后增加规模而非setup数量。
- 每session保存信号、拒绝原因、执行偏差和复盘标签；每周与规则引擎差异审计。
- 只有rolling OOS净EV、回撤和合规同时达门槛才逐级扩仓；策略白名单保持不变。

### REVERSALS-C25-N01：禁止 News/Pundit/额外图表覆盖主信号

- 类型：`NEGATIVE`信息约束。
- 依据，guidelines 20、25–26、28、40，PDF p.508–512：外部观点、指标和多图会干扰自身分析。
- 核心策略只读冻结价格数据；news仅用于event risk，不作方向。

### REVERSALS-C25-N02：禁止明确趋势中的普通逆势 Scalp

- 类型：`NEGATIVE`方向约束。
- 依据，guidelines 32–34、54、56–57、73，PDF p.510–517：大多数逆势setup失败并变顺势entry。
- 除S07严格MTR外，AI明确时反向新仓为零。

### REVERSALS-C25-N03：禁止 Reward 小于 Risk

- 类型：`NEGATIVE`数学约束。
- 依据，guidelines 57–59、71–72，PDF p.515–517：风险2赚1通常需极高胜率，多数交易者不具备。
- 主策略净目标必须≥R；任何小于R版本隔离且不得进入推荐结果。

### REVERSALS-C25-N04：禁止 Tight Range Stop Entry

- 类型：`NEGATIVE`环境约束。
- 依据，guidelines 51–53、PDF p.514：tight range压倒一切正向理由。
- S13状态下stop-entry订单数必须为零。

### REVERSALS-C25-N05：禁止追损与后半日放宽标准

- 类型：`NEGATIVE`行为约束。
- 依据，guidelines 50、65–66，PDF p.514、516：亏损、疲劳或烦躁时改变风格只会扩大损失。
- 当日drawdown后不得增加size、frequency、setup whitelist或降低score阈值。

### REVERSALS-C25-N06：禁止因无聊或漏单而追突然 Breakout

- 类型：`NEGATIVE`注意力约束。
- 依据，guidelines 38–39、76，PDF p.511、518：目标是赚钱而非交易，长时间无信号后仓促决定负EV。
- 未过S09恢复门槛不得下单；漏掉赢家不触发补偿交易。

### REVERSALS-C25-N07：Guideline 概率不得当作常数

- 类型：`NEGATIVE`研究约束。
- 依据，guidelines 1–17、58–60，PDF p.505–508、515：规则非绝对，edge小且概率随stop/scale/context共存。
- `60/80%`等全部由数据估计；参数、scale-in和宽stop每个版本独立校准。

### REVERSALS-C25-N08：不得把稳定前的扩展当进步

- 类型：`NEGATIVE`治理约束。
- 依据，guidelines 63–64、74–77，PDF p.516–518：先精通少数best setups，稳定后扩规模而非增加交易和形态。
- 未满足S20门槛时新增setup、市场、周期与风险档全部关闭。

## 3. 原文覆盖表

| PDF | Guidelines | 主张 | 映射 |
|---:|---:|---|---|
| 505 | 1–5 | 主观gray fog、edge小、理解不等于会执行 | S02、S20、N07 |
| 506 | 6–12 | 数学优势、每bar上下双向、反向突破、breakout评估 | S01–S04 |
| 507 | 13–17 | 强弱、反过度自信、共存概率、talk-out bad trades与惯性 | S01–S03、N07 |
| 508 | 18–23 | Pullback可能已flip、价格优先、无公平/新闻方向、跨市场行为 | S03–S04、N01 |
| 509 | 24–27 | 保护stop、自主分析、漏信号说明仓位过大 | S05–S06、N01 |
| 510 | 28–32 | I-don't-care、宽stop缩仓、反手困难、严格countertrend gate | S05–S07 |
| 511 | 33–39 | 反转退出、晚于早、failure-of-failure、stop run、等待与不必交易 | S07–S09、N02、N06 |
| 512 | 40–44 | 单图简单流程、5m EMA pullback、buy low/sell high例外 | S03、S10、S14、N01 |
| 513 | 45–49 | Urgency=trend、uncertainty=range、good fill警报与首小时纪律 | S03、S11 |
| 514 | 50–54 | 追损禁令、日中tight range、AI只顺势 | S11–S14、N04–N05 |
| 515 | 55–60 | Signal bar、禁逆势scalp、reward≥risk、trader equation与scale | S02、S07、S14–S15、N02–N03 |
| 516 | 61–68 | 顺势pullback、严格MTR、复盘/个性/纪律、两腿与防cherry-pick | S07、S14、S16–S17、S20 |
| 517 | 69–74 | 避免losers、premise复核、plan不可漂移、7/10 EMA方向代理 | S13–S19、N02–N03 |
| 518 | 75–78 | 纪律、等待、稳定后扩仓而非扩交易 | S20、N06、N08 |

## 4. 回测验收

- 每bar保存六道gate、双向score、regime、operator state、拒绝原因和最终订单，确保规则可审计。
- 概率与阈值使用anchored walk-forward；所有作者比例、bar数、时间和仓位缩放均做敏感性测试。
- 报告raw candidates、eligible、missed、filled、规则违规、提前退出、追损和operator kill-switch次数。
- 对比无行为门控与完整门控的净EV、最大回撤、尾部损失和机会成本，证明纪律规则的增量价值。
- 按trend/range/tight range、时段、顺逆势、SCALP/SWING、operator state及连亏状态分层。
- 自动测试保护stop、reward≥risk、tight-range零stop entry、AI零普通逆势、session内不扩风险及无未来泄漏。
- Guideline 1–78是章节来源和研究假设，不是盈利保证或固定规则。
