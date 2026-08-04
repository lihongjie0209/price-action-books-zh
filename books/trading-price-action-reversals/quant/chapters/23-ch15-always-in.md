# 第 15 章：Always In

## 元数据

- 英文来源：`books/trading-price-action-reversals/en/chapters/23-ch15-always-in.md`
- PDF 页码：297–318
- 图表：Figure 15.1–15.6；正文与图注已完整说明规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Always-In 状态机

```text
AI(t) ∈ {LONG, SHORT, UNCERTAIN}
spike_score = 同向趋势棒数量、实体/收盘位置、突破距离、重叠度与跟进的组合分数
flip LONG→SHORT = bear spike + downside follow-through + bull structure failure
flip SHORT→LONG = bull spike + upside follow-through + bear structure failure
```

- Always-In表示若必须持仓时应选择的方向，用于日内约`3–10`个重要swing，而不是给每个小反转贴标签。
- `UNCERTAIN`本身是交易区间证据：此时关闭趋势追单，改为区间边缘策略或空仓。
- 作者所称`60%/70%`均只登记为待检验先验，不能写成固定胜率。

## 2. 规则卡

### REVERSALS-C15-S01：Always-In State Classifier

- 类型：三状态分类器。
- 依据，PDF p.297–300：用明显spike、趋势延续、近期收盘相对EMA及进入区间的方向判断当前控制方；无法判断即为range。
- 基准输入：最近`5–20 bars`回归斜率、价格在EMA(20)同侧比例、同向趋势棒数、突破与跟进、最近确认摆动破坏。
- 只有综合分数越过训练期阈值才输出LONG/SHORT；滞回阈值应高于维持阈值，避免每根bar翻转。

### REVERSALS-C15-S02：Two-Bar Spike Flip

- 类型：主要翻转触发器。
- 依据，PDF p.298–301：多数明确flip至少需要两根连续强趋势棒，并使市场相信未来数bars仍有跟进。
- 反向突破最近swing/range boundary后，要求连续`2–3`根同向趋势棒，或突破棒后`1–2`根有效跟进。
- Stop在spike/最近结构极值外；目标测试`1R、2R`及spike/range measured move。

### REVERSALS-C15-S03：Single-Bar Contextual Flip

- 类型：高强度例外。
- 依据，PDF p.301、314：强背景下单根巨大trend/outside bar即可建立共识，例如通道突破失败后的强outside-down。
- 要求大bar≥range滚动`80%–95%`分位、实体≥`60%–75%`、收盘靠近极值，并同时具备opening reversal、climactic reversal或关键结构失败之一。
- 单棒版本单独分层；下一bar收回其`50%`以上则撤销，不与普通两棒样本混合。

### REVERSALS-C15-S04：Follow-Through Quality Gate

- 类型：确认与失败分类。
- 依据，PDF p.301–304：突破后的跟进收盘决定控制强弱；弱跟进宜等pullback，强反向跟进构成失败突破。
- 潜在bear flip后，最低要求下一bar不强bull close；潜在bull flip镜像处理。
- 弱同向bar/doji只允许在反弹/回调处入场；强反向trend bar收回突破则转交failed-breakout策略。

### REVERSALS-C15-S05：Failed Near-Flip With-Trend Entry

- 类型：顺势失败交易。
- 依据，PDF p.298–299、304、315、318：多数翻转尝试失败；尚差一根确认棒时可fade，强趋势中可在逆势trend bar收盘、前低/高及趋势线附近顺势入场。
- 原AI仍有效且反向spike未通过S02/S03时，在失败确认或首个顺势signal入场。
- 对“缺少最后一根确认棒”的fade设更小仓位；若反向结构突破随后获得跟进立即退出。

### REVERSALS-C15-S06：Trading-Range Uncertainty Gate

- 类型：状态禁入。
- 依据，PDF p.299–302、305：range内AI可能只是旧方向残留；紧密区间不适合swing，直到全区间突破并跟进才形成新共识。
- `UNCERTAIN`或tight-range成立时禁止在区间中部AI追单；仅开放边缘fade、突破或失败突破模块。
- 从一侧走到另一侧不能单独flip；要求突破完整range boundary并通过S04。

### REVERSALS-C15-S07：First-Hour Direction Establishment

- 类型：开盘swing扫描器。
- 依据，PDF p.302–306、314：第一小时常建立AI方向，早盘清晰setup可能持续数小时并走出约日均波幅的重要部分。
- 开盘后前`12 bars`（5分钟图约1小时，其他周期按时钟换算）优先扫描opening reversal、gap failure、breakout与连续趋势棒。
- “至少三分之一ADR、持续数小时”只作目标/持仓敏感性假设，不作为入场必然条件。

### REVERSALS-C15-S08：Urgency Market-or-Tiny-Pullback Entry

- 类型：强趋势即时入场。
- 依据，PDF p.303、306、310–311、316：多根强spike表明机构以市价或微小回调成交，等待深pullback可能错失runaway trend。
- S02确认且spike_score处于训练期高分位时，允许`10%–50%`常规仓位市价入场，或在前bar高/低内`1–3 ticks`限价。
- 结构止损过宽时按`qty ∝ 1/R`缩仓；不得为维持仓位而任意收紧止损。

### REVERSALS-C15-S09：Structural Risk Sizing

- 类型：仓位控制。
- 依据，PDF p.303、306、309、311、316：高周期或大spike需要更宽止损；风险为常规`3/4`倍时仓位降至`1/3、1/4`，恐惧时可用`10%`试仓。
- Stop候选为signal/spike extreme、最近HL/LH或大趋势棒极值；采用能保持交易前提的最远必要结构位。
- 总账户风险固定；记录`0.10、0.25、0.50、1.00 ×`常规风险的离散仓位实验。

### REVERSALS-C15-S10：Pullback Hold and Breakeven Rule

- 类型：持仓管理。
- 依据，PDF p.303–305：趋势pullback不可避免；第一次触及入场附近后若又顺势运行数bars，第二次回到入场价可用breakeven stop退出。
- 首次回撤后若价格顺势推进`2–5 bars`或≥`0.5R`，允许止损移至breakeven；第二次回测被打掉后保持空仓，直到新清晰setup。
- 单根猛烈逆向bar若未触发AI flip，不单独强平；仍以结构止损、目标或清晰反转退出。

### REVERSALS-C15-S11：Scale-Out and Runner

- 类型：分批退出。
- 依据，PDF p.302、306–307：可在`1–2R`或股票`0.5%–1%`兑现部分，余仓持有至明确反转、breakeven stop或收盘。
- 测试首批`1/3–1/2`在`1R/2R`退出；潜在反转但尚未flip时再减`1/4–1/3`，至少保留`1/4`runner。
- Runner目标为measured move、支撑阻力或session close；所有比例须按品种独立校准。

### REVERSALS-C15-S12：Exit Threshold Below Reverse Threshold

- 类型：非对称状态管理。
- 依据，PDF p.307、315–316：退出原仓所需证据少于反手；多数交易者方向丧失时先平仓，只有清晰强setup才反向建仓。
- 设置`exit_score < flip_score`：反向signal达到exit阈值先平仓，达到S02/S03阈值才反手。
- 严格always-in版本与`exit-flat-reenter`版本并行回测，禁止把二者成交混记。

### REVERSALS-C15-S13：Reverse Position Atomically

- 类型：反手执行。
- 依据，PDF p.307：清晰反转触发时，原方向一份余仓加两份新仓可用三份反向订单完成平仓与开仓。
- 订单拆成`close old`与`open new`两腿记账；新方向首份在`1–2R`兑现，第二份swing。
- 任一腿未成交时重新计算净敞口；不得假定复合订单无滑点或全部成交。

### REVERSALS-C15-S14：Higher-Timeframe Decision Reduction

- 类型：周期选择版本。
- 依据，PDF p.298、308–309：15分钟/高tick图减少噪声和翻转次数，但bar更大、stop更宽、仓位更小。
- 5m、15m及等成交量/tick bar分别运行完整状态机；每个版本参数与交易成本独立冻结。
- 不在单笔交易中事后切周期确认；用相同账户风险比较信号数、翻转数、EV和回撤。

### REVERSALS-C15-S15：Trend-Pullback Scaling-In (Advanced)

- 类型：专家级加仓研究。
- 依据，PDF p.307–308、313：强趋势可依据近期ADR和既往最大pullback分层限价加仓，例如约`10%–20% ADR`间距。
- 仅当AI清晰、最近`2h`pullback稳定且总风险可封顶时启用；候选层级为`0.05、0.10、0.20 ADR`及最近pullback幅度。
- 所有腿共用结构失效止损；flip时全退并转交S13，主结果与不加仓版本分开。

### REVERSALS-C15-S16：Final-Flag Transition Exit

- 类型：趋势末段防守。
- 依据，PDF p.311–313：长趋势中的连续climax、三推、长期横盘破趋势线及迟迟未测EMA可预示至少两腿、约10bars修正。
- 趋势持续≥`20 bars`后，若出现final-flag候选+第三推/大climax+反向两棒结构，先按S12减仓或退出。
- 只有强反向spike与结构确认才flip；普通深回调不能自动反手。

### REVERSALS-C15-S17：Measured-Move Reprojection

- 类型：动态目标。
- 依据，PDF p.302、305、307、316：确认突破常指向range/spike measured move；趋势推进并上移止损后可重新投射更远目标。
- 初始目标取`max(1R, spike height, range height)`的可达阻力/支撑版本；每次确认新swing后只用当时信息更新。
- 目标更新不得扩大账户初始风险；报告固定目标与动态目标的独立结果。

### REVERSALS-C15-N01：不对每个小反转翻转状态

- 类型：`NEGATIVE`频率约束。
- 依据，PDF p.297：AI用于每日少数重要swing，不是每个minor reversal。
- 状态机设置滞回和最短确认；报告每session flip数，异常高频版本判为概念失真。

### REVERSALS-C15-N02：明确 AI 时禁止逆势 Scalp

- 类型：`NEGATIVE`方向约束。
- 依据，PDF p.305：逆势scalp常面临约风险两倍于收益，并要求不现实的高胜率；等待顺势pullback更合理。
- `AI ∈ {LONG,SHORT}`时普通策略只允许同向新仓；逆势模块必须隔离为反事实基线。

### REVERSALS-C15-N03：弱突破不得直接认定 Flip

- 类型：`NEGATIVE`确认约束。
- 依据，PDF p.301–304、311–313：小反向棒、无此前压力或无跟进的区间突破通常不足以改变AI。
- 缺少S04跟进或结构破坏时维持原状态/转UNCERTAIN，不得仅凭颜色或单次EMA穿越反手。

### REVERSALS-C15-N04：作者概率不是回测常数

- 类型：`NEGATIVE`研究约束。
- 依据，PDF p.302、305–307、316–318：清晰AI常被描述为约`60%`，最强setup可达`70%`，但原文明确概率无法确定。
- 阈值只表达主观置信级别；实际胜率、到达1R/2R概率须walk-forward估计并给置信区间。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 297 | Always-In定义、重要swing而非每个反转、常用作swing entry | S01、S11、N01 |
| 298 | 既有方向、两根强棒改变方向、高周期选择 | S02、S14 |
| 299 | 前日方向、失败反转、range中维持旧方向 | S01、S05–S06 |
| 300 | tight range危险、等待突破/失败突破、区间边缘 | S06 |
| 301 | spike通常至少两棒、单棒例外、突破跟进质量 | S02–S04 |
| 302 | measured move、首小时setup、退出与持有 | S07、S11、S17 |
| 303 | 长pullback、结构止损、小仓市价入场 | S08–S10 |
| 304 | 清晰方向中把反转尝试视作顺势机会 | S04–S05 |
| 305 | breakeven二次回测、禁止逆势scalp、早盘AI swing | S07、S10、N02 |
| 306 | 强spike紧迫性、宽止损缩仓、股票分批退出 | S08–S11 |
| 307 | 持有pullback、清晰setup才反手、动态目标与加仓 | S10、S12–S15、S17 |
| 308 | ADR加仓示例、Figure 15.1 swing结果为例证 | S15 |
| 309 | 高周期减少决策、宽止损配小仓 | S09、S14 |
| 310 | gap后弱bear跟进、breakout mode及强bull breakout | S04、S06–S08 |
| 311 | breakout小仓、climax与无卖压的弱下破 | S08–S09、S16、N03 |
| 312 | final flag、三推、两腿约10bars修正预期 | S12、S16 |
| 313 | 强bear spike后仍待确认、随后结构翻空、ADR scale-in | S02、S12、S15–S16 |
| 314 | 单根强棒可flip、spike被反向spike抹除、第二腿 | S03–S04 |
| 315 | 缺最后确认棒时fade、已有压力提高第二次翻转质量 | S05、S12 |
| 316 | 退出门槛低于反手、runaway trend小仓参与 | S08–S09、S12 |
| 317 | 激进与保守flip阈值、对称风险收益示例 | S01–S04、N04 |
| 318 | 强setup目标、趋势中逆向强棒收盘可顺势买卖 | S05、S11、S17、N04 |

## 4. 回测验收

- 状态仅使用当时已收盘数据；摆动、EMA、ADR与滚动分位全部point-in-time，禁止居中摆动泄漏。
- 输出逐bar的AI状态、状态分数、exit/flip原因和版本号；人工抽查跨gap、range、climax及session close。
- 分别评估两棒flip、单棒例外、failed near-flip、开盘setup与final-flag退出，不能只报告合并绩效。
- 报告每session flip数、UNCERTAIN占比、入场延迟、MAE/MFE、1R/2R到达率、净EV及成本敏感性。
- 比较always-in反手、先退为空再重入、高周期、即时小仓及等待pullback版本，并保持相同风险预算。
- 加仓、分批退出和复合反手逐腿模拟真实成交、滑点与最大组合风险；主策略默认关闭高级加仓。
- `60%/70%`、`3–10 swings/day`、`20 bars`、`10-bar correction`及ADR比例均做跨品种walk-forward敏感性检验。
- Figure 15.1–15.6只作章节案例与规则来源，不作为参数最优性或盈利能力证据。
