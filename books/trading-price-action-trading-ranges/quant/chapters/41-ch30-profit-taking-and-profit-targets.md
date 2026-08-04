# 第 30 章：Profit Taking and Profit Targets

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/41-ch30-profit-taking-and-profit-targets.md`
- PDF 页码：587–595
- 图表：Figure 30.1–30.2；正文与图注已完整说明规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Target 与退出状态

```text
R = abs(entry_price - initial_stop) + expected_cost
net_reward = abs(target_price - entry_price) - expected_cost
EV = p_win * net_reward - (1 - p_win) * R
exit_state = TARGET_WORKING | PARTIAL_1 | PARTIAL_2 | RUNNER | FLAT
```

- 每次入场前冻结初始stop、至少一个获利方案和成本后EV；持仓后可因实时信息降低目标或主动退出，但不能用未来路径抬高历史目标。
- Scalp目标优先用working limit/OCO；swing可用分批limit加反向signal/收盘退出。
- 书中固定tick示例必须按tick size、ATR/ADR和初始R归一化。

## 2. 规则卡

### RANGES-C30-S01：Trend Maturity Profit-Taking Regime

- 类型：趋势生命周期退出组件。
- 依据，PDF p.587–588：强趋势早期交易者在突破旧极值加仓；趋势成熟、双向交易增多后，改为在旧极值附近获利并等待更低/高重入。
- `early_trend`：强breakout+follow-through、pullback浅、overlap低；运行breakout add-on。
- `mature_trend`：至少2–3 pushes、overlap/反向bars增加或新极值推进衰减；在prior swing extreme前后`0–0.20ATR`分批退出。
- Heavy profit taking与强反向spike并存时，升级为range/reversal candidate，不继续追突破。

### RANGES-C30-S02：Large Trend-Bar Strength Exit

- 类型：climax/失败突破获利规则。
- 依据，PDF p.587–588：成熟趋势中会在large trend bar收盘、略越收盘、随后小bar或反向close处获利，并在下一bar反端进一步退出。
- Large bar=`range >= 1.5–2.0 rolling median`且方向body≥60%；只在mature/climactic context启用。
- Exit ladder：bar close附近25–50%，下一小/反向bar close再25%，其反端break清余仓或交runner规则。
- 强趋势早期禁用机械全平，避免把continuation bar误判为climax。

### RANGES-C30-S03：OCO Scalp Bracket

- 类型：scalp执行组件。
- 依据，PDF p.588–589、591：scalper入场后同时放保护stop与profit limit；一边成交自动取消另一边，并须核对账户状态。
- Fill后原子提交`stop + target` OCO；目标默认`1.0–2.0R`，由setup概率与结构空间确定。
- Partial fill时两腿qty实时同步；任一成交后检查position、open orders与预期一致。
- OCO失败或残留孤儿订单触发自动撤单/平仓与风险告警。

### RANGES-C30-S04：Trader's Equation Target Gate

- 类型：成本后交易筛选。
- 依据，PDF p.589–591：入门者优先约60%以上成功率且reward至少等于risk、理想约2R的交易；实际常只能取得约1R。
- 允许条件：训练期校准`p_win >= 0.55–0.65`，成本后`reward/risk >= 1.0`，且EV置信下界≥0。
- 2R优先但不是硬编码；目标必须位于实时可见的support/resistance之前。
- 概率按setup、regime、时段滚动校准，禁止把书中60%直接当回测结果。

### RANGES-C30-S05：Trend Pullback 1R–2R Target

- 类型：顺趋势pullback策略。
- 依据，PDF p.589–592、593–595：EMA、breakout test、H2、wedge、double bottom等趋势回调通常有较高概率，目标可约1–2倍risk。
- Trend确认；pullback低动量，entry在EMA/结构confluence处的方向signal突破。
- Stop在signal/pullback结构外；target=`min(1–2R, next resistance)`，short镜像。
- 结构空间不足1R或已转range时跳过或按S07 scalp，不假设必达2R。

### RANGES-C30-S06：Strong Trend 2R/3R Scale-Out

- 类型：swing分批退出。
- 依据，PDF p.591、594–595：强趋势可在2R退出一半、3R再退出四分之一，余四分之一持有至清晰反向signal或收盘。
- Strong trend须在入场时或达到1R前确认；`50% @ 2R, 25% @ 3R, 25% runner`为基准参数。
- Runner用最近确认swing trail；清晰opposite signal触发或session close强制退出。
- 与全仓2R退出、25/25/50分配比较成本后收益、回撤和偏度。

### RANGES-C30-S07：Trading Range 中整仓 Scalp Exit

- 类型：regime依赖目标。
- 依据，PDF p.589–590、594–595：range内利润潜力有限，breakout多失败；接近对侧/channel top应整仓获利，少量runner只在更强二腿突破条件下保留。
- Confirmed range时目标=`near opposite edge`或成本后`1R`中较近者；默认全平。
- Two-legged correction、double bottom/top flag且强日内趋势背景时，可保留25–50%到新极值。
- Range breakout出现strong follow-through后才切S06，不能事后把失败scalp改称swing。

### RANGES-C30-S08：Dynamic Equation / Flat-Test Exit

- 类型：持仓中EV重估。
- 依据，PDF p.591–592：交易者方程逐tick变化；变弱则收紧/小利退出，边缘则尽快退出，转负立即市价退出。
- 每bar只用当前信息重估`p, remaining_reward, stop_risk, costs`。
- 若空仓状态下不会以当前价格与原stop重新入场，则marketable exit；边缘区可减仓50%并收紧stop。
- 正常趋势pullback不得因单tick噪声频繁触发，设`1–2bars`确认或显著EV阈值。

### RANGES-C30-S09：Working Profit Limit Governance

- 类型：执行纪律。
- 依据，PDF p.588–589、591–592：profit target虽可在脑中，但多数交易者更适合始终有working limit，防止盈利回吐；每次entry/exit后核对账户。
- Scalp必须working target；swing的已计划partial targets必须working，runner允许signal exit。
- 每次订单事件后对账`expected_position == broker_position`及OCO残单；不一致立即进入safe mode。
- 回测模拟limit未成交、差一tick、partial fill、断线与slippage。

### RANGES-C30-S10：Support/Resistance Confluence Target

- 类型：结构目标组件。
- 依据，PDF p.592–593：pullback底/顶常由EMA、H2/wedge、retracement、breakout test、旧swing与breakeven-stop区共同形成；对侧结构可作为逻辑目标。
- 每个level必须在触达前生成；confluence窗口=`0.10–0.30ATR`，至少2类独立结构。
- Entry target放在下一confluence resistance/support前`1tick–0.10ATR`，提高limit成交概率。
- Fibonacci 62%仅作连续retracement特征之一，不单独产生交易或目标。

### RANGES-C30-S11：Exit-and-Reenter on Pullback

- 类型：成熟趋势再入场流程。
- 依据，PDF p.587–588、594–595：在强势/旧极值获利后，等待EMA、flag或新的方向signal再入场，通常优于在成熟突破追价。
- 原仓退出后必须等待独立pullback事件；不得在同bar无条件追回。
- Reentry需趋势仍有效、pullback未破结构、方向signal确认；重新计算stop、qty和EV。
- 原交易与再入场分别计成本和P&L，并共享trend episode ID避免选择性报告。

### RANGES-C30-S12：Opposite-Signal / Session-Close Runner Exit

- 类型：无固定目标swing退出。
- 依据，PDF p.588、591、594：强趋势余仓可持有至相反signal触发或收盘；多数交易者不应同时完成退出并反手。
- Opposite signal需结构位置+合格signal bar+trigger，不能仅凭一根小反向bar。
- Runner在session close前预设窗口平仓；隔夜策略须单独授权并计gap risk。
- Exit默认不自动reverse；反手必须通过独立setup与EV gate。

### RANGES-C30-N01：Strong Trend 中禁止 Countertrend Scalp

- 类型：`NEGATIVE`硬否决。
- 依据，PDF p.589–590：约80%的trend reversal attempts演变为flags；逆势scalp容易亏损并使交易者错过真正的顺势pullback。
- Strong Always-In trend且未转range时，countertrend scalp candidate交易数必须为零。
- 只记录shadow信号及其对随后顺势入场的干扰，不用事后顶底挑选成功样本。

### RANGES-C30-N02：每笔交易必须预有获利计划

- 类型：`NEGATIVE`治理约束。
- 依据，PDF p.590–592：没有获利计划，浮盈最终可能回到breakeven甚至转亏；target用于约束持仓者自身。
- Entry前必须存在固定target、scale schedule或可机读runner exit之一。
- 无计划交易拒单；持仓中不得因贪婪删除所有退出条件。

### RANGES-C30-N03：禁止把 60% 与固定 Tick 当作事实

- 类型：`NEGATIVE`参数约束。
- 依据，PDF p.589–595：60%、10/20ticks等是特定setup与市场波动示例，不是跨市场常数。
- 概率必须由训练/验证数据校准；距离同时以R、ATR/ADR、spread和tick归一化。
- Figure 30.1–30.2中的精确成交不得作为参数拟合标签。

### RANGES-C30-N04：Target 不得忽略前方结构空间

- 类型：`NEGATIVE`。
- 依据，PDF p.592–595：合理目标通常位于旧高、channel top等可见结构前；range中执着更远目标会降低方程。
- 若next obstacle前净空间不足计划reward，缩短目标后重算EV；EV不合格则拒单。
- 不允许因理论2R位于阻力之外而假设必然突破。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 587–588 | 趋势成熟、旧极值获利、large-bar获利、退出后回调再入 | S01–S02、S11 |
| 588–590 | OCO与账户核对、交易者方程、scalp/swing、强趋势逆势失败 | S03–S05、S09、N01 |
| 590–592 | 必须有获利计划、2R/3R分批、动态方程、working target | S04、S06、S08–S09、S12、N02 |
| 592–593 | Figure 30.1：EMA/H2/wedge/retracement/breakout test共振与结构目标 | S05、S10、N03–N04 |
| 593–595 | Figure 30.2：趋势pullback 2R、range scalp、强趋势runner与再入 | S05–S07、S11–S12、N03–N04 |

## 4. 回测验收

- Target、stop、scale schedule和结构level均在入场时带`valid_from`冻结；未来泄漏次数必须为零。
- 同一trade的S01–S12是管理分支，不重复计为多个独立盈利signal。
- OCO测试覆盖partial fill、拒单、孤儿订单、断连和gap-through；每个订单事件后对账。
- 所有结果报告gross/net EV、target fill率、stop先到率、MAE/MFE、盈利回吐与退出后延伸幅度。
- 分批与全平方案保持相同初始账户风险，并完整计算多次成交成本。
- 概率模型做walk-forward calibration，报告Brier score与各regime置信区间。
- Strong trend countertrend禁令、无target拒单、结构空间不足和session close退出设自动测试。
- 固定tick全部映射到R与ATR/ADR，并做跨品种、波动状态和时段敏感性检验。
- Figure 30.1–30.2仅作章节例证，不作绩效证据。
