# 第 19 章：Opening Patterns and Reversals

## 元数据

- 英文来源：`books/trading-price-action-reversals/en/chapters/28-ch19-opening-patterns-and-reversals.md`
- PDF 页码：371–388
- 图表：Figure 19.1–19.9；正文逐bar说明已完整覆盖规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Opening Regime

```text
opening_window = first 30–90 minutes
OR = robust range/largest directional leg within opening_window
OR_ratio = OR_height / recent_ADR
opening_regime ∈ {SMALL_OR, MEDIUM_OR, LARGE_SPIKE, BARBWIRE, UNCERTAIN}
```

- Opening range边界存在多个合理版本；应同时保存而不是事后挑最准确的measured move。
- 作者概率、时间和点数均为待检验假设；跨品种优先转换为ADR、ATR、R和session比例。

## 2. 规则卡

### REVERSALS-C19-S01：Opening Vacuum Reversal

- 类型：关键位快速反转。
- 依据，PDF p.371：机构等待更优价格会形成sell/buy vacuum；快速移动至EMA、趋势线、measured move或swing后可猛烈反转。
- 前`1–12 bars`出现高速度单向move，触及冻结支撑/阻力后在`1–2 bars`形成强反向棒/两棒反转时入场。
- Stop在vacuum extreme外；首目标`1R`，保留runner测试opening extreme成为当日高低。

### REVERSALS-C19-S02：Early Extreme Candidate

- 类型：早期swing候选。
- 依据，PDF p.372–374：首bar、前5bars及首`1–2h`常形成当日极值，通常来自某种double top/bottom。
- 对首bar趋势棒、前5bars反转、首小时double/wedge及昨日高低反转分别打分。
- 不直接预测极值；只有后续结构未破坏且形成顺向跟进时提升runner持有权重。

### REVERSALS-C19-S03：Opening Reversal Swing Selection

- 类型：精选swing。
- 依据，PDF p.372–373、376–378：多数早期反转只够scalp，double top/bottom或清晰AI后更适合追求约`2R`。
- 基准要求关键位+合格signal bar+double/second entry或AI确认至少两项。
- 不达swing分数仅允许`1R` scalp；达到则目标`2R+`并用结构止损容忍正常pullback。

### REVERSALS-C19-S04：Spike Reversal-Failure Continuation

- 类型：突破回调。
- 依据，PDF p.373：开盘强spike后的弱反转常失败，反向小move转为原趋势breakout pullback并进入channel。
- Spike后首反向signal若实体小、重叠大且未破spike结构，原方向突破其极值时顺势入场。
- 激进limit-at/beyond reversal bar与保守stop-entry分开；目标`1R、2R`或spike measured move。

### REVERSALS-C19-S05：Initial Character Classifier

- 类型：日型早期分类。
- 依据，PDF p.374：首bar doji且在昨日末range中、或首小时重叠长尾多反转，增加range day；连续大趋势棒小尾低重叠增加trend day。
- 使用前`3、6、12 bars`的body、tail、overlap、directional persistence和gap构建point-in-time score。
- 输出概率/分数而非确定标签；后续强breakout允许状态更新。

### REVERSALS-C19-S06：Two-Consecutive-Trend-Bar AI Trigger

- 类型：早期趋势确认。
- 依据，PDF p.374、379–380、383、386–388：首小时连续强同向趋势棒常建立AI；小实体大尾版本需更多验证。
- 两棒均满足趋势棒且平均overlap低、收盘靠近极值时确认；弱版本要求再一强棒或结构突破。
- 入场用首pullback/失败逆势setup，stop在two-bar spike另一侧，先scalp后按跟进决定swing。

### REVERSALS-C19-S07：Opening Range Multi-Anchor Construction

- 类型：范围估计。
- 依据，PDF p.374–375、377–378：OR可取opening trading range或前`30–90min`最大leg，新极值可视作扩大或overshoot。
- 同时维护`OR_30、OR_60、OR_90、largest_leg`与首次双向反转range；所有边界实时冻结版本号。
- Measured move对每个anchor独立投射，禁止事后选择命中者作为唯一OR。

### REVERSALS-C19-S08：Small Opening Range Breakout Mode

- 类型：小OR突破。
- 依据，PDF p.375、377、379–380：OR约近期ADR的`25%`时偏向双向breakout mode，突破后pullback也常很小。
- `OR_ratio`搜索`0.15–0.30`；形成上、下spike/至少两次反转后，在range两侧放OCO stop。
- 一侧成交后另一侧为结构stop或反手触发；风险按完整range高度计，目标OR measured move。

### REVERSALS-C19-S09：Medium Opening Range Expansion

- 类型：中OR扩张。
- 依据，PDF p.375、377–378：OR约ADR的`1/3–1/2`时通常尝试扩展至平均日幅，常走约一个OR measured move并可能回测突破位。
- `OR_ratio`搜索`0.30–0.55`；强突破+跟进入场，目标`1×OR`投射。
- 回测边界时区分成功breakout pullback与强收回；强收回可转reversal-day模块。

### REVERSALS-C19-S10：Large Opening Spike Branch

- 类型：大开盘move分支。
- 依据，PDF p.375–376：大opening spike常演化spike-and-channel，也可能在small final flag后climactic reversal。
- `OR_ratio > 0.50–0.75`或spike score高时，不追固定OR目标；等待首pullback顺势或final-flag+强反转。
- 两个分支用实时确认竞争，禁止根据收盘日型事后分类交易。

### REVERSALS-C19-S11：Early Strength Memory

- 类型：日内状态记忆。
- 依据，PDF p.375–376：开盘强move即使随后反转，其力量可能晚些时候重现；不能假定新趋势必持续至收盘。
- 保存opening bull/bear pressure score并随bars指数衰减；相反趋势出现深修正时把旧方向作为flip候选特征。
- 旧强度不得单独入场，需新signal/结构突破确认。

### REVERSALS-C19-S12：Opening Swing Scale-Out

- 类型：仓位管理。
- 依据，PDF p.376：潜在当日极值交易应保留swing；强setup可在`1–2R`减`1/3–1/2`，余仓到强反向signal或breakeven stop。
- 测试`25%–50%`于`0.67R–1.33R`、再减仓于`1.33R–2R`，余仓runner。
- 固定R版本与“首次pause后减仓”版本分开，所有加仓仍受总风险上限。

### REVERSALS-C19-S13：Partial Urgency Entry

- 类型：快速反转执行。
- 依据，PDF p.376：强signal可能立即远行；尚未完全确信时至少用`1/4–1/2`仓位参与，再在首pullback加仓。
- Signal score高但未达满仓阈值时开`25%/50%`风险；只在前提保持且pullback确认时补足。
- 与等待确认版本比较miss rate、滑点、EV和回撤，不把“必须参与”作为绩效假定。

### REVERSALS-C19-S14：Double-Top/Bottom Flag Continuation

- 类型：趋势延续。
- 依据，PDF p.376–377、380–385：趋势开始后两次相近pullback形成double-bottom bull flag或double-top bear flag，功能上是顺势entry。
- Bull版本要求既有uptrend、两个pullback lows近似且第二个未有效破趋势；bear镜像。
- Stop entry越过signal bar；stop在第二次pullback极值外，目标最近trend leg measured move/`1–2R`。

### REVERSALS-C19-S15：Two Failed Attempts Opposite Breakout

- 类型：区间反向突破。
- 依据，PDF p.382–383、385–386：市场同方向尝试两次均失败，随后常尝试另一侧；失败H2可成为L2，反之亦然。
- 两次同侧测试间隔`2–20 bars`且均收回，第二次失败后等待反向range break或second-entry signal。
- Range相对EMA的位置作为方向加权，不单独触发；目标range measured move。

### REVERSALS-C19-S16：Gap Two-Leg Pullback

- 类型：gap延续。
- 依据，PDF p.383–384：大gap down常两腿回EMA后breakout成bear trend；gap up镜像。
- `gap >= 0.5–1.5 ATR`，pullback形成两腿且测试EMA/冻结阻力，随后同gap方向合格signal入场。
- 顶部short优先bear signal bar而非强bull bar；stop在pullback extreme外。

### REVERSALS-C19-S17：Barbwire Trap-and-Fade

- 类型：开盘禁入后失败突破。
- 依据，PDF p.387–388：平EMA、大重叠bars且无边缘小signal为barbwire，应等待趋势棒突破困住一侧，再交易失败。
- Barbwire期间禁止中部新仓；突破昨日极值/range后若无跟进并出现第二次反转signal，向range内入场。
- 若突破由≥`2`强趋势棒组成，等待第二signal而非立即fade。

### REVERSALS-C19-S18：Opening-Time Regime Window

- 类型：时间参数研究。
- 依据，PDF p.372、384、387：当日极值常在首小时或前`1–2h`，趋势也常在约开盘后两小时才开始；名称不影响交易逻辑。
- 以session elapsed time而非固定PST硬编码，测试`30、60、90、120min`opening窗口。
- 超出窗口仍可用相同pattern，但不标记opening-specific先验。

### REVERSALS-C19-N01：普通早期反转不得默认 Swing

- 类型：`NEGATIVE`选择约束。
- 依据，PDF p.372、377–378：多数opening-range reversals只够scalp，只有少数形成≥2R swing。
- 未通过S03的候选不保留无限runner；报告全部反转与精选反转的条件成功率。

### REVERSALS-C19-N02：支撑阻力或 Measured Move 不单独反转

- 类型：`NEGATIVE`触发约束。
- 依据，PDF p.377–378：多数支撑投射不会导致反转，市场具有惯性；真正反转虽发生于某支撑，但仍需强setup。
- 触及level只能提升context score，不能直接下单。

### REVERSALS-C19-N03：Opening Range 不得事后唯一化

- 类型：`NEGATIVE`前视约束。
- 依据，PDF p.374–375、377：多个OR定义都合理且常无一个精确预测目标。
- 保存S07全部实时版本；禁止用最终行情挑选最贴合边界或投射。

### REVERSALS-C19-N04：Barbwire 内无安全信号时保持空仓

- 类型：`NEGATIVE`执行约束。
- 依据，PDF p.387：开盘barbwire若没有边缘小bar，需耐心等待一侧被困。
- S17触发前submitted orders必须为零，OCO breakout研究版本除外且单独报告。

### REVERSALS-C19-N05：作者概率与 Emini 点数不得硬编码

- 类型：`NEGATIVE`研究约束。
- 依据，PDF p.372–375：`20/30/50/60/90%`、2/4/6点等均为经验指南且精确概率不可知。
- 概率作为待验证假设；价格参数转R/ATR/ADR，并用walk-forward估计置信区间。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 371 | 机构订单与vacuum effect、关键位opening reversal及潜在当日极值 | S01–S02 |
| 372 | opening反转概率指南、保护止损、早期极值与double top/bottom | S02–S03、N01、N05 |
| 373 | opening swing方程、spike反转失败成为breakout pullback、关键位列表 | S03–S04 |
| 374 | 初始price action揭示range/trend character、连续趋势棒与OR作用 | S05–S07 |
| 375 | OR多定义及小/中/大三档、measured move与reversal day | S07–S11、N03 |
| 376 | 早期强度记忆、swing减仓、急迫小仓、double flags | S11–S14 |
| 377 | double flags entry、小opening range突破选择 | S08、S14、N01–N03 |
| 378 | OR投射非精确支撑、普通反转多为scalp、极值常来自double | S02–S03、S09、N01–N02 |
| 379 | 约四分之一ADR range进入breakout mode及OCO反手 | S08 |
| 380 | 小OR突破后小pullback、连续趋势棒确认AI | S06、S08 |
| 381 | 昨日level breakout pullback与early failed breakout | S01、S04、S14 |
| 382 | final flag、climactic reversal、两次失败后反向 | S10、S15 |
| 383 | gap双向可反转、两腿反趋势move、outside-up确认 | S01、S06、S14–S16 |
| 384 | 大gap两腿回EMA、double-top flag、约两小时开始趋势 | S16、S18 |
| 385 | double-bottom/top flags | S14 |
| 386 | 两次上破失败、H2失败成L2、连续bear bars建立AI | S06、S15 |
| 387 | 时间标签不重要、开盘barbwire应等待trap | S17–S18、N04 |
| 388 | 强breakout后等第二signal、lower-low breakout pullback及AI翻多 | S06、S17 |

## 4. 回测验收

- Opening window、OR anchors、ADR和所有关键位仅用当时数据；逐bar保存regime与边界版本。
- 分别报告vacuum reversal、普通反转、double/second-entry、spike continuation、gap pullback和barbwire failure。
- 验证首bar/前5bars/首小时极值、两次失败、两腿、OR measured move等作者假设，附置信区间而非固定概率。
- 按OR_ratio、小中大regime、gap大小、初始trend/range character、时段和多空分层。
- OCO与反手策略按完整range风险逐腿模拟；同bar双触及采用tick路径或最不利假设。
- 比较固定1R scalp、2R swing、分批runner及小仓后加仓版本，保持账户风险一致并计成本。
- Barbwire空仓、level非独立触发、OR不可事后唯一化及参数非硬编码设自动测试。
- Figure 19.1–19.9只作规则来源与案例，不作成功率、目标精度或收益证据。
