# 第 24 章：Scalping、Swing Trading、Trading 与 Investing

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/35-ch24-scalping-swinging-trading-and-investing.md`
- PDF 页码：446–466
- 图表：Figure 24.1–24.2；正文与图注已完整说明规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 交易类型契约

| 类型 | 预设持有期 | 典型目标/风险 | 回调容忍 | 数据周期 |
|---|---:|---:|---|---|
| intraday scalp | 1–15分钟 | reward约 `1R` | 低 | intraday |
| intraday swing | 15分钟–收盘 | reward主测 `>=2R` | 高 | intraday |
| multi-day trade | 1–数日 | 事件/日线目标 | 中 | daily/intraday execution |
| investment | 6个月–多年 | 基本面估值 | 高 | daily/monthly + fundamentals |

- 每笔订单创建时锁定`trade_type, max_holding, initial_stop, target_policy, scale_policy`。
- 价格行为章节主要实现intraday scalp/swing；investment只作为防止策略漂移的边界，不从本章生成基本面买入。
- 固定点数示例只适用于书中当时Emini/股票环境；正式参数全部用tick、ATR、ADR和交易成本归一化。

## 2. 规则卡

### RANGES-C24-S01：Scalp 模式选择

- 类型：交易管理策略。
- 依据，PDF p.446–451、455–459：scalp捕捉一条小腿，通常R:R约1，要求较高胜率；适用于range、countertrend或趋势即将暂停的判断。
- 仅当目标市场样本外`p_win*(net_reward) - p_loss*(risk+cost)>0`且安全边际≥`0.10R`时启用。
- Setup来源沿用各章；本规则只决定退出：固定目标 `0.75–1.5R`，不容忍目标前深pullback。
- 价格回到entry且尚未显示follow-through，可breakeven/小亏退出；必须模拟真实可成交性。
- Clear Always-In同方向的优质setup优先S02 swing，不应只取微小scalp。
- Reward小于risk的版本独立禁用，除非严格样本外证明所需胜率与成本后优势。

### RANGES-C24-S02：两腿预期的 Intraday Swing

- 类型：核心swing管理策略。
- 依据，PDF p.447–455：swing持有pullback、捕捉每日2–4个大摆动，目标通常≥2R；setup较不确定但大reward补偿低胜率。
- Setup需具备至少两腿理由：strong breakout、major reversal、double top/bottom、opening reversal、trend pullback或measured move空间。
- 初始止损与对应price-action setup相同；仓位按完整stop距离缩放。
- 第一目标 `1–2R` 平 `25–75%`；剩余仓持有至第二腿、结构目标、强反向signal或收盘。
- 允许正常pullback，不因3–4ticks小回撤自动breakeven退出。
- Trading range到另一边优先退出余仓；明确trend中才以反向signal/trail持有。

### RANGES-C24-S03：Scalp + Swing 混合仓

- 类型：分批退出策略。
- 依据，PDF p.450–453、456–460：许多交易者先取scalp、再用breakeven stop swing余仓；强scalper也应在可能4–10点走势时保留1/4–1/2。
- 入场时预分配：scalp portion `25–75%`，swing portion余量；成交后不可因情绪重写比例。
- Scalp在 `1–2R`/首磁力位退出；之后swing stop可移至breakeven或最新结构，但必须遵守S09。
- 后续顺方向setup可重新加入scalp仓，总风险不超过初始预算+已锁定利润的预注册比例。
- 报告全scalp、全swing、混合三种净值，防止用最佳事后退出证明策略。

### RANGES-C24-S04：低概率高回报 Swing Basket

- 类型：组合执行策略。
- 依据，PDF p.453–459：许多major reversal只有40–50%成功率，但若reward≥2R仍有正期望；低概率模型必须系统地取所有合格setup，不能主观cherry-pick。
- 固定候选定义与质量下限；若校准概率<50%且目标≥2R，对所有合格事件按相同规则执行。
- 单笔风险固定，禁止连败后跳过或加倍；按至少 `N>=100` 的basket评估。
- 达不到2R可行空间的candidate拒绝；若早期premise失效允许按S07退出为scalp/小亏。
- 高概率≥60%的模型可以选择性执行，但选择器本身必须预注册和验证。

### RANGES-C24-S05：强趋势中的 Small Starter Swing

- 类型：防止错过趋势策略。
- 依据，PDF p.454–456：大趋势实时总显得不确定，交易者容易等到收盘才确认；若市场持续单向，即使看似弱也应有小仓swing。
- 当Always-In score连续 `3–5bars` 达标且结构性HH/HL或LH/LL持续，建立 `25–50%` 正常风险starter。
- 入场：strong close、prior bar突破或首小pullback；stop在spike/结构另一端，远stop用小仓。
- 后续确认pullback再补至正常风险；不得追到测量目标/末端climax才首次入场。
- Clear opposite signal或Always-In flip退出；普通小pullback持有。

### RANGES-C24-S06：Flat-Test 决定 Swing 是否提前退出

- 类型：动态退出决策。
- 依据，PDF p.453–455：把自己想象成flat；若此刻不会以相同size和stop重新入场，持有现仓在财务上也不合理，应退出。
- 每根完成bar计算剩余`expected_reward_to_target / risk_to_stop`及premise flags。
- 若新入场EV≤0、目标空间<`1R`或出现合格opposite setup，则全部/部分退出。
- 不因未实现盈亏改变判断；算法输入不得包含entry P&L符号，除breakeven/风险约束外。
- 与固定target策略对照，验证动态退出是否在样本外改善而非过拟合。

### RANGES-C24-S07：Swing Premise 失效时降级为 Scalp

- 类型：退出覆盖层。
- 依据，PDF p.453–457：多数swing未达到大目标；若新的合理反向setup出现或走势不按预期，swing trader常以scalp利润退出，而非坚持原目标。
- Premise failure：预期breakout无follow-through、两腿结构被破坏、range对侧到达或strong opposite signal。
- 若当前盈利≥预注册scalp目标，立即limit/market退出；否则按原stop或最近结构退出。
- Exit后反向入场需独立强signal，弱反转只用于获利退出，不自动reverse。
- 记录原计划与实际降级原因，避免事后把所有小赢家称为scalp策略。

### RANGES-C24-S08：不同 Regime 的 Swing 退出

- 类型：regime-aware管理。
- 依据，PDF p.456–457：趋势中余仓可持至opposite signal，range中更应在对侧极值退出；退出signal门槛低于新入场门槛。
- Trend：分批后余仓用structure/EMA trail，直至strong opposite signal。
- Trading range：到range另一侧/内部measured target退出 `75–100%`，再等待独立反向setup。
- Weak reversal可获利退出但不反手；strong reversal且有足够空间才允许反向swing。
- Regime变化只从确认bar生效，不用最终日型重写持仓路径。

### RANGES-C24-S09：Partial Profit 后 Stop 管理

- 类型：止损策略。
- 依据，PDF p.451、456–461：部分止盈后可移breakeven，但最佳趋势有时会扫breakeven后快速恢复；应按结构和标的特性预设缓冲。
- 基准：第一部分达到 `1–2R`后，余仓stop移至entry±`0–0.25ATR`或最近confirmed swing，取预注册方案。
- Strong trend且breakout test常扫stop时允许缓冲 `1–3ticks / 0.10–0.25ATR`，通过缩仓保持美元风险。
- Stop被扫后 `1–2bars` 立即恢复并出现新signal，可按新事件重入，不自动追价。
- 各标的stop-run参数只从训练数据估计，避免用AAPL/GS案例硬编码。

### RANGES-C24-S10：Profit Target Touch 的成交信息

- 类型：微观执行/重入策略。
- 依据，PDF p.460–461：target只touch即成交可能显示激进对手盘与隐藏趋势压力；touch却未成交可能形成5/9-tick failure和反转线索。
- 需要tick/盘口或可靠成交回报；仅OHLC数据不能知道limit是否真实成交，必须标记unknown并采用保守模型。
- Long target在最高tick成交且随后pullback守住结构：允许下一顺势setup重入。
- Target touch未成交且bar反转：stop移breakeven；若context为趋势末端，可在该bar低点下研究反向entry。
- 固定5/9ticks改为目标前后 `0–1tick`，并按标的tick/ATR归一化。

### RANGES-C24-S11：高流动性股票 Swing 选择

- 类型：标的筛选与执行方案。
- 依据，PDF p.459–462：高成交量、数美元日波幅股票更适合swing；选最强趋势标的，等EMA pullback或合格reversal，并用更宽stop/更小shares。
- 流动性门槛用滚动dollar volume、spread≤`0.05–0.10ATR_bar`、日成交量分位数，不硬编码旧时代3/7百万股。
- 在候选池选trend score最高且相关性受限的 `1–5` 个标的。
- 入场：EMA pullback、trend-channel overshoot+prior line break或strong reversal。
- 风险按ATR stop统一；第一目标≥`1R`，余仓持到收盘/strong opposite signal。
- Corporate actions、earnings gap和短卖可用性进入数据清洗。

### RANGES-C24-S12：多次顺势 Signal 的盈利后加仓

- 类型：pyramiding策略。
- 依据，PDF p.451–453：swing已有合理利润后，可在后续顺势signal加同等或更小仓；整个仓位stop随最新结构，早期仓即使最后加仓亏损仍可能总盈利。
- 首仓MFE≥`1R`或已实现部分利润后才允许加仓；最多 `2–3` 次。
- 每次新增风险≤首仓风险的 `25–50%`，组合worst-case不得超过预注册上限。
- 组合stop更新到最新confirmed signal swing；若会把总锁定利润变负则不加仓。
- Opposite strong signal提前退出，不等待机械trail命中。

### RANGES-C24-N01：禁止把亏损 Trade 转成 Investment

- 类型：`NEGATIVE`硬约束。
- 依据，PDF p.446：预定短线亏损后拒绝止损并改称投资，会把原最大亏损放大且干扰其他交易。
- `trade_type`和`max_holding`成交后不可延长；intraday仓最迟session close退出，multi-day按预定日期。
- Stop不得因P&L为负而扩大；任何策略层修改必须在新交易前版本化。
- 自动断言：实际持有期≤契约上限，止损风险≤初始风险（合法trail除外）。

### RANGES-C24-N02：Scalp 不得用不现实胜率掩盖负 R:R

- 类型：`NEGATIVE`。
- 依据，PDF p.449–451、457–461：小目标/大stop需67–95%甚至更高胜率，多数人无法达到；一两tick/HFT式scalp不适合普通执行。
- 计算包含手续费、spread、slippage和limit未成交的breakeven probability。
- 样本外Wilson下置信界未超过breakeven+5个百分点时，策略禁用。
- 不以主观“confidence 60/70/80%”替代校准概率。

### RANGES-C24-N03：低概率 Swing 不可 Cherry-Pick

- 类型：`NEGATIVE`。
- 依据，PDF p.458：低于50%的2R+模型依靠一篮子交易获利，主观跳过难看的setup会破坏期望。
- 所有合格candidate保存take/skip及机器可复现原因；人工情绪/近期亏损不是合法过滤器。
- 若新增selector，须独立训练、走样本外验证并比较全量basket。
- 连败不改变仓位或下一setup执行。

### RANGES-C24-N04：固定点数不可跨市场/时代移植

- 类型：`NEGATIVE`与参数约束。
- 依据，PDF p.449、456–466：书中1–4点、$1–$3、特定ADR都依赖当时Emini与股票价格/波动。
- 所有stop/target保存tick、ATR、ADR和美元四种表达；正式信号用归一化参数。
- 不同市场单独校准成本与滑点，保持相同账户风险而非相同shares/contracts。
- 原文固定数字只作为初始搜索范围，不作为默认生产值。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 446–450 | investor/trader/scalper/swing定义、时间框架纪律、对手方数学 | 定义、S01–S04、N01–N02 |
| 450–454 | 最佳setup应争取更大目标、混合仓、scale-in、swing不确定性 | S02–S05、S12 |
| 454–457 | flat-test、EV、趋势不确定性、trend/range不同退出 | S06–S09 |
| 457–461 | 初学者选择、低概率basket、股票筛选、partial与target fill | S03–S04、S09–S11、N02–N04 |
| 461–466 | 大目标优于微scalp、宽stop小仓、双向swing实例 | S02–S05、S08–S12 |

## 4. 回测验收

- 每笔交易在成交前锁定类型、持有上限、stop、target和scale policy；事后修改次数必须为零。
- Scalp/swing/混合三种退出使用相同入场母样本对照，避免入场差异污染结论。
- 概率必须用walk-forward/out-of-sample校准并含置信区间，不使用主观60/70/80%。
- S04低概率basket保存所有candidate及skip reason，验证没有cherry-picking。
- S06动态退出不能读取未实现P&L方向作为premise feature。
- Partial、breakeven、buffered stop和reentry模拟真实gap/slippage。
- Limit target touch需tick数据证明；OHLC-only结果使用保守成交假设并单列。
- Scale-in/pyramiding报告组合worst-case风险，不能把每腿当独立风险。
- 固定点数全部同时换算ATR/ADR/tick并做跨波动regime敏感性测试。
- Figure 24.1–24.2只作章节例证，不作参数拟合或绩效证据。
