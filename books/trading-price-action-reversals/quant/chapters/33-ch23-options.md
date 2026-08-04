# 第 23 章：Options

## 元数据

- 英文来源：`books/trading-price-action-reversals/en/chapters/33-ch23-options.md`
- PDF 页码：416–438
- 图表：Figure 23.1–23.9；正文与图注已完整说明规则，未额外查看图片
- 状态：量化研究规格，未经回测；涉及卖出期权的高级结构默认关闭
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Option Execution Model

```text
option_pnl = exit_mark - entry_fill - commissions - exercise/assignment_cost
max_loss_long = premium_paid + costs
edge = scenario-weighted option payoff - theta - spread - slippage - IV_change
```

- 必须使用历史point-in-time option chain：bid/ask、成交、open interest、strike、expiry、IV、Greeks和corporate actions。
- 只回测underlying OHLC无法证明期权收益；缺少chain时仅能生成underlying signal，不能报告option PnL。

## 2. 规则卡

### REVERSALS-C23-S01：Simple Long-Option Wrapper

- 类型：有限风险执行层。
- 依据，PDF p.416–419：60分钟/日线正期望setup可用long call/put限制隔夜风险，简单购买最不干扰day trader。
- Underlying signal复用EMA pullback、range edge、stairs fade、strong spike和弱H/L1–2 failure。
- 方向上涨买call、下跌买put；最大账户风险按premium全损计算，不以underlying stop距离低估风险。

### REVERSALS-C23-S02：Timeframe and Holding-Horizon Gate

- 类型：成本门控。
- 依据，PDF p.416–418：option spread/时间价值使短周期交易困难，通常应基于60m/daily并持有`1–several days`。
- 默认signal timeframe≥60m；5m只开放高流动ATM与极端执行风险场景。
- 预期持仓bars必须使underlying目标对应的option收益覆盖双边spread、theta和slippage。

### REVERSALS-C23-S03：Liquidity and Spread Filter

- 类型：合约准入。
- 依据，PDF p.423：薄合约可能瞬间损失巨大spread；经验下界为OI约1,000或日成交约300份。
- 候选要求`OI≥500–2000`、`volume≥100–500`、relative spread≤`2%–15%`，按价格档校准。
- 不达标默认拒绝；研究版本仅限价并模拟排队、partial/missed fill。

### REVERSALS-C23-S04：ATM/Near-Money Contract Selection

- 类型：合约选择。
- 依据，PDF p.417、419、426：front-month ATM/near-money活跃合约通常spread较窄；强spike也可选OTM以限制成本。
- 基准选择delta绝对值`0.40–0.60`、DTE `20–45`；比较OTM delta `0.20–0.40`。
- 在信号时冻结chain并按最低总成本/目标敏感度选择，禁止事后挑最佳strike。

### REVERSALS-C23-S05：Long Option versus Debit Spread Selector

- 类型：结构选择。
- 依据，PDF p.421–425、431–434：预计`1–2 days`内启动或一周内sharp move偏单腿；需一周以上、愿持至近到期或目标接近阻力时可debit spread减theta。
- `expected_start≤2d`或`expected_hold<1w`默认long option；`hold≥1–2w`且明确target时比较debit spread。
- Short strike放在冻结support/resistance/target附近；强趋势预期越过short strike时不限制上行/下行。

### REVERSALS-C23-S06：Premise Revalidation Exit

- 类型：每日退出判断。
- 依据，PDF p.421–423：每次问“若空仓是否仍会开完全相同仓位”；否则立即退出，不能靠到期等待。
- 每个HTF bar重算signal、target、time-to-move和IV；任一核心前提失效则用可成交limit/market退出。
- 到达目标过快时先兑现大部分/全部，因为range继续和theta可迅速吞噬利润。

### REVERSALS-C23-S07：Trading-Range Edge Options

- 类型：区间fade。
- 依据，PDF p.416、427–430：range顶部买put/退出call，底部买call/退出put；弱H/L2、wedge/double failure提高质量。
- 仅在range外三分之一且有反转signal入场，目标中点/另一边；到中点至少减`50%`。
- 强spike突破+跟进时停止fade并转趋势option模块。

### REVERSALS-C23-S08：Strong-Trend EMA Pullback Options

- 类型：顺势期权。
- 依据，PDF p.416、426、431、433–434：强bull趋势回EMA买call、bear反之，多数反转尝试失败。
- AI强且EMA pullback未破结构，在H/L2或同向signal入场；三推/climax后暂停至两腿修正完成。
- 持有>1–2周比较spread版本，短期用单腿。

### REVERSALS-C23-S09：Stairs Breakout Fade

- 类型：阶梯失败策略。
- 依据，PDF p.416、426–427：stairs中新高/低突破常回到前一阶，可在确认反转bar后买put/call。
- 新极值越过前swing后在`1–3 HTF bars`收回，且此前pullback曾侵入旧swing，触发fade。
- 目标前阶边界/`1R`；强breakout跟进取消。

### REVERSALS-C23-S10：Spike Participation with IV Gate

- 类型：强突破期权。
- 依据，PDF p.416、424–426：强spike可买方向性期权，但晚入时IV同步spike会使之后quiet channel中option不涨。
- 早期spike且IV percentile不过高可直接入；晚入或IV急升时等pullback/IV回落。
- 报告underlying正确但option不盈利的比例，不能用标的方向替代期权收益。

### REVERSALS-C23-S11：Catalyst IV-Crush Filter

- 类型：事件禁入/结构切换。
- 依据，PDF p.420、437–438：earnings等催化剂前premium膨胀，方向判断正确仍可能因IV crush亏损。
- 已知catalyst前`1–5 sessions`，若IV percentile/expected move显著高于历史，禁止裸买long option。
- 可研究defined-risk spread但需完整vol-surface情景；事件后待新chain和price action稳定再开仓。

### REVERSALS-C23-S12：Extreme-Market Defined-Risk Day Trade

- 类型：系统过载保护。
- 依据，PDF p.418–419、434–437：free fall/接近limit、报价与订单系统不可信时，long option可把灾难损失限制在premium。
- 仅用long call/put、合理小仓、limit order；underlying反转signal仍需成立。
- Exit优先监控underlying失效价并主动limit卖出，不能依赖option stop自动保护。

### REVERSALS-C23-S13：Underlying-Price Alert Exit

- 类型：期权退出执行。
- 依据，PDF p.418–419、434–437：option无成交时last-price stop不会触发，即使bid/ask已越过；应按underlying alert主动退出。
- Stop condition绑定underlying结构价；触发后按option NBBO/可成交limit逐步退出。
- 模拟alert latency、stale quote、无成交和系统中断，最大损失仍按premium全损压力测试。

### REVERSALS-C23-S14：Windfall Profit Capture

- 类型：异常盈利退出。
- 依据，PDF p.425–426、435–436：期权意外快速大赚时通常应兑现，随后range/IV下降会迅速减少利润。
- 若`1–3 days`内option PnL达到预期总目标的`75%–125%`或≥`1.5–3R`，减`50%–100%`。
- 余仓仅在underlying强趋势与IV风险仍可接受时持有，隔夜重新按premium风险计量。

### REVERSALS-C23-S15：Extreme-Sequence Mean Reversion Put/Call

- 类型：统计异常回归。
- 依据，PDF p.431–433：多年罕见的连续gap bars/同色bars是climactic，可用期权押EMA测试和两腿修正。
- 先用滚动历史估计run length分位；达到`95%–99.5%`后仍需channel overshoot/reversal context。
- 目标EMA/`1–3 HTF days`，绝不把案例中的`30 bars/10 bars`固定为普遍规律。

### REVERSALS-C23-S16：Spread Leg-Out Research

- 类型：高级持仓调整。
- 依据，PDF p.421–424、430–431：市场逆向至EMA但原premise有效时，可获利买回short leg并保留long leg；需要经验。
- 仅研究模式：short leg已盈利、long directional premise仍有效、裸long余下风险≤账户上限时允许leg out。
- 每腿按独立bid/ask成交并纳入assignment、margin和legging gap风险。

### REVERSALS-C23-S17：Expiration Strike Magnet Overlay

- 类型：可选磁体特征。
- 依据，PDF p.424：高OI strike在临近到期可能增强support/resistance与pinning。
- 使用当时可见OI，在expiry前`1–5 days`将最高OI附近strike加入target/context。
- 不作为独立entry，且必须验证不同到期、0DTE占比和市场制度下的增量稳定性。

### REVERSALS-C23-S18：End-of-Day Call/Put Trend Trade

- 类型：简化日内期权。
- 依据，PDF p.434–436：5分钟大gap后强spike可买方向期权，失效时按underlying alert退出，否则收盘前平仓。
- 只选S03高流动合约；强trend确认后入场，日内不加复杂spread。
- 默认RTH close前全部退出，避免overnight IV/theta和注意力风险。

### REVERSALS-C23-N01：保护性 Option Stop 不保证保护

- 类型：`NEGATIVE`执行约束。
- 依据，PDF p.418–419、435：无last trade时stop不触发，bid/ask可远越stop。
- 风险引擎按premium全损，不按stop价计算最大损失；退出采用S13。

### REVERSALS-C23-N02：薄期权禁止交易

- 类型：`NEGATIVE`流动性约束。
- 依据，PDF p.423：宽spread和长时间不成交可吞噬大部分收益。
- 未过S03的合约submitted orders为零，除隔离研究版本。

### REVERSALS-C23-N03：催化剂前高 IV 不裸买期权

- 类型：`NEGATIVE`事件约束。
- 依据，PDF p.420、437–438：earnings方向正确仍可能因premium crush亏损。
- S11高IV状态下long call/put订单为零。

### REVERSALS-C23-N04：Straddle 默认禁用

- 类型：`NEGATIVE`结构约束。
- 依据，PDF p.419–420：双腿theta、spread和commission使straddle很少值得。
- 不因“不知道方向但预期大move”直接开straddle；只作为完整IV/realized-vol研究基线。

### REVERSALS-C23-N05：复杂卖方结构默认关闭

- 类型：`NEGATIVE`复杂度/尾部风险约束。
- 依据，PDF p.417、419、422、428–429、433–434：risk reversal、short puts、covered calls、collars等涉及assignment、margin和注意力，超出简单day-trader方案。
- 生产默认仅long option/debit spread；任何short leg必须defined-risk、完整assignment模拟并单独授权。

### REVERSALS-C23-N06：Underlying 方向正确不代表 Option 盈利

- 类型：`NEGATIVE`绩效约束。
- 依据，PDF p.420、424–425、437–438：theta、IV crush/skew可使标的按预期移动而option/spread收益很小或亏损。
- 绩效只能来自真实chain重估与成交，禁止用delta常数或underlying return代替。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 416 | HTF简单put/call场景、EMA/range/stairs/spike setup | S01–S02、S07–S10 |
| 417 | 5m高流动option、极端行情有限风险、复杂策略分心 | S02–S04、S12、N05 |
| 418 | theta/spread、精选setup、系统过载与option stop失效 | S02、S12–S13、N01 |
| 419 | ATM day trade限定风险、short put/covered call/straddle/delta-neutral | S01、S04、N04–N05 |
| 420 | catalyst premium crush、VIX/put购买解释不确定 | S10–S11、N03、N06 |
| 421 | hedge调整、短期单腿/长期spread及short strike目标 | S05–S06、S16 |
| 422 | spread风险收益随价格变化、买spread优于裸卖方、持有期选择 | S05–S06、N05 |
| 423 | premise复核、快速目标兑现、OI/volume/spread流动性 | S03、S06、S14、N02 |
| 424 | spread leg-out、expiry strike magnet、VIX抬升option成本 | S10、S16–S17 |
| 425 | skew使spread收益低于直觉、接近到期/远越short strike才接近上限 | S05、S10、N06 |
| 426 | 快速move偏单腿、及时兑现、bull spike call | S05、S10、S14 |
| 427 | stairs breakout fade与broad channel反向期权 | S09 |
| 428 | trading-range edges买put/call | S07 |
| 429 | risk reversal示例及裸short put尾部 | S07、N05 |
| 430 | SPY多类daily option setup、巨大bar后spread | S05、S07–S10、S16 |
| 431 | EMA test、wedge/double反转与持有期决定spread | S05、S07–S10 |
| 432 | 长channel极端run均值回归、历史分位验证 | S15 |
| 433 | 罕见连续bull bars、强趋势EMA calls及climax暂停 | S08、S15 |
| 434 | 强趋势EMA call、5m gap spike日内call | S08、S18 |
| 435 | runaway fade、underlying alert、option stop不触发 | S12–S14、S18、N01 |
| 436 | windfall退出、系统过载时有限风险call | S12–S14 |
| 437 | 高VIX下premium收缩、option隔夜风险 | S10–S14、N06 |
| 438 | earnings后标的下跌但put因IV crush亏损 | S11、N03、N06 |

## 4. 回测验收

- 必须用无幸存者偏差的point-in-time chain、NBBO、OI/volume、IV surface、Greeks、expiry与corporate actions。
- 每笔合约选择在signal时冻结；不得事后挑strike、expiry、单腿/spread或最佳成交价。
- 按signal、DTE、delta、IV percentile、relative spread、流动性、单腿/spread和catalyst分层真实option PnL。
- 模拟theta、vega/skew、bid/ask、limit queue、partial fill、assignment/exercise及stale/no-trade stop失效。
- 与直接underlying交易保持相同最大风险比较EV、回撤、capital usage及方向正确但期权亏损比例。
- 高IV catalyst、薄合约、复杂卖方、straddle及option stop非保护性设自动测试。
- 作者金额、OI/volume门槛、DTE、VIX换算与概率均作历史假设，不作为当前市场事实硬编码。
- Figure 23.1–23.9只作策略案例，不作IV、成交、收益或可复制性证据。
