# 第 12 章：Markets

## 元数据

- 英文来源：`books/trading-price-action-reversals/en/chapters/20-ch12-markets.md`
- PDF 页码：278–279
- 图表：无
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Market Eligibility Score

```text
capacity_cost = spread + expected_market_impact(qty) + fees
net_edge = gross_expected_move - capacity_cost
eligible = entries_per_session足够 AND net_edge > 0 AND slippage在预算内
```

- Price action规则可跨市场，但交易可行性由流动性、波动、信号频率、tick、成本与仓位容量决定。
- 书中价格、合约换算、佣金和标的清单是历史示例，必须从当前point-in-time数据动态计算。

## 2. 规则卡

### REVERSALS-C12-S01：Five-Minute Market Eligibility Filter

- 类型：市场准入。
- 依据，PDF p.278：日内交易者偏好5分钟图每天有多个entry且能承受所需仓位而不显著slippage的市场。
- Rolling `20–60sessions`统计合格setup数、spread、top-of-book depth、成交额与impact。
- 最低候选频率建议`2–5 setups/session`，净edge置信下界>0。
- 不满足时降频/swing-only或移出universe，而非改变signal定义凑交易。

### REVERSALS-C12-S02：Position-Size Capacity Gate

- 类型：执行容量。
- 依据，PDF p.278–279：Emini/大型期货可容纳较大仓位，较薄合约/DIA/Dow futures扩大仓位后slippage成为问题。
- 下单qty不得超过可见/估计5分钟成交量的`0.1–1%`或盘口深度的预设比例。
- 预测impact+spread+fees不得超过gross target的`10–30%`。
- 超限时缩仓、拆单或迁移更深市场；禁止用无slippage回测证明容量。

### REVERSALS-C12-S03：Small-Size Training Instrument Path

- 类型：实盘准入阶梯。
- 依据，PDF p.278：初学可用SPY等小单位产品降低美元风险并练习scale-out，再在规模上升时迁移更深合约。
- 初始每笔account risk≤`0.10–0.50%`，instrument须支持最小qty下的结构stop。
- 达到预注册样本外/实盘`100–300 trades`、净EV>0和风险零违规后才扩大size。
- 迁移产品前做tick、point value、session和tracking差异的平行shadow test。

### REVERSALS-C12-S04：ETF/Futures Normalized Equivalence

- 类型：跨产品映射。
- 依据，PDF p.278–279：SPY/Emini、QQQ/Nasdaq futures跟踪相同underlying，但tick/乘数/stop触发与成本不同。
- 用`notional, beta, point_value, tick_value, volatility`换算等风险仓位，不硬编码500 shares等历史比例。
- 同一信号分别模拟各产品fill；ETF多触1tick stop的差异由真实quotes/保守OHLC反映。
- 选择成本后EV更高且capacity足够的执行载体。

### REVERSALS-C12-S05：Scalp-vs-Swing Cost Gate

- 类型：持仓期限选择。
- 依据，PDF p.278–279：小目标scalp只有在佣金极低、执行快且slippage小才可盈利；否则优先swing。
- Scalp准入：round-trip all-in cost≤target的`10–20%`，保守fill后EV>0。
- 未达准入时该市场只运行swing strategies；盈利稳定后才开放scalp模块。
- 佣金、rebates、borrow和tax均用当期账户实际费率。

### REVERSALS-C12-S06：Trend-Frequency Market Style Mapping

- 类型：市场—策略匹配。
- 依据，PDF p.278–279：currency/forex/notes/bonds容量大但Emini日盘信号较少；债券趋势可持数小时。
- 按rolling trend persistence、setup frequency、ATR与session liquidity分`scalp-rich / swing-trending / sparse`。
- Swing-trending市场优先较长runner和较少entries；sparse市场不因等待而降低门槛。
- Mapping仅用训练/前向数据，并按regime定期更新。

### REVERSALS-C12-S07：Single-Market Attention Budget

- 类型：操作治理。
- 依据，PDF p.279：主动交易Emini时同时关注低机会forex会分散注意力；减少无关市场可改善执行。
- 人工交易默认同时active markets≤`1–3`；自动系统仍受监控/风险容量限制。
- 只有主市场无position/无near-term candidate时才允许次市场alert。
- 记录missed/late orders与认知错误，若多市场显著恶化执行则自动收缩universe。

### REVERSALS-C12-S08：Dynamic Stock Liquidity/Range Screen

- 类型：股票universe构建。
- 依据，PDF p.279：适合日内的股票应有足够daily range、成交量和低slippage，使scalp及数倍更大的swing均有空间。
- Point-in-time筛选：median dollar volume、quoted spread、ATR dollars/percent、price与halt risk。
- 建议阈值按分位数：dollar volume前10–30%、spread≤`0.05–0.20ATR_5m`、ADR足够覆盖≥`3–5`倍成本。
- Universe每日/每周更新；书中AAPL等名单不硬编码。

### REVERSALS-C12-N01：禁止照搬历史价格、佣金与合约换算

- 类型：`NEGATIVE`参数约束。
- 依据，PDF p.278–279：1100/110、20c、$1佣金、500 SPY等均依赖当时产品规格和市场。
- 从交易所reference data、broker fee schedule和当期quotes读取参数。
- Backtest按历史point-in-time multiplier/tick/corporate actions处理。

### REVERSALS-C12-N02：低成本是假设时禁止宣称 Scalp 可行

- 类型：`NEGATIVE`执行约束。
- 依据，PDF p.278：scalp利润极易被佣金、速度与slippage吞噬。
- 无真实/保守cost model的scalp结果一律不通过验收。
- Touch-as-fill、零impact和当前佣金回填历史均不得作为主结果。

### REVERSALS-C12-N03：禁止静态幸存者标的清单

- 类型：`NEGATIVE`数据治理。
- 依据，PDF p.279：好交易标的可随时增删；书中公司/ETF只是当时例子。
- Universe必须point-in-time，包含退市、改名、并购和流动性衰退标的。
- 不用今天最活跃股票回填历史筛选。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 278 | 跨市场price action、5分钟信号/容量、SPY与Emini换算、初始risk、commission与scalp/swing | S01–S05、N01–N02 |
| 278–279 | futures/forex/notes容量与频率、thin markets、注意力、股票range/volume筛选及动态名单 | S02、S06–S08、N03 |

## 4. 回测验收

- 所有instrument specs、fees、universe membership与liquidity使用point-in-time数据。
- 报告每市场setup频率、fill率、spread、impact、gross/net EV和capacity curve。
- ETF/futures等风险映射以notional/volatility验证，禁止只比较名义qty。
- Scalp主结果采用穿越/queue保守fill与完整成本；与swing版本同母样本比较。
- Universe screen做walk-forward并包含退市/并购证券，幸存者偏差检查必须通过。
- Capacity、cost ratio、active-market count和strategy-style mapping做敏感性测试。
- 本章具体产品、金额与公司仅作历史例证，不作当前推荐或固定参数。
