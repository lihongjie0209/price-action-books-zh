# 第 25 章：交易数学——该不该做？长期能否盈利？

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/36-ch25-mathematics-of-trading-should-i-take-this-trade-will-i-make-money-if-i-take-this.md`
- PDF 页码：467–523
- 图表：Figure 25.1–25.3；正文与图注已完整说明规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Trader's Equation

每个candidate在入场前计算成本后的期望值：

```text
gross_reward = abs(target - expected_entry)
gross_risk   = abs(expected_entry - stop)
net_reward   = gross_reward - fees - entry_slippage - exit_slippage
net_loss     = gross_risk   + fees + entry_slippage + stop_slippage
EV           = p_win * net_reward - (1 - p_win) * net_loss
breakeven_p  = net_loss / (net_reward + net_loss)
edge_R       = EV / gross_risk
```

- 入场门槛主测：`EV > 0`且`edge_R >= 0.05–0.15R`，为概率误差保留安全边际。
- `p_win`定义为目标先于stop触达的概率；同一事件必须明确bar内路径处理。
- 书中40/50/60/70/80/90%均为启发式，不硬编码为真实胜率；正式系统使用walk-forward校准概率与置信区间。
- Beginners默认`net_reward >= net_loss`；概率不确定时先验取接近50%，并要求目标至少 `1.5–2R`。

## 2. 规则卡

### RANGES-C25-S01：入场前 EV Gate

- 类型：所有策略共用的硬过滤器。
- 依据，PDF p.467–477、489–503：每笔交易必须同时考虑概率、风险和收益；只看risk/reward或胜率都不够。
- Candidate生成后先确定不可随意扩大的结构stop，再计算预计成交与position size。
- 从校准模型获取`p_win(target_before_stop | features)`；低置信度时用保守置信下界。
- 只有`EV_after_cost > 0`且达到安全边际才允许下单，否则记录reject reason。
- 若long与short均无正EV stop-entry方案，标记uncertain/range，等待或交给独立limit模型。
- 每个target/stop组合独立计算，不能用2R概率搭配实际1R退出。

### RANGES-C25-S02：固定账户风险的 Position Sizing

- 类型：仓位算法。
- 依据，PDF p.475–477、490–494、503：先决定stop距离，再用正常美元风险决定shares/contracts；宽spike stop必须缩仓。
- `risk_budget = equity * risk_fraction`，建议研究 `0.10–1.00%`/trade。
- `qty = floor(risk_budget / (gross_risk*point_value + expected_cost_per_unit))`。
- `qty<minimum`则跳过；不得为了维持仓量收窄到无效stop。
- Gap/slippage stress后组合风险不得超过预算的 `1.25–1.50x`。
- Scale-in与多仓相关性使用组合worst-case统一计算，不把每腿视为独立额度。

### RANGES-C25-S03：60% Equidistant Move 快速决策框架

- 类型：简化实时gate。
- 依据，PDF p.473–476、503–509：若可信地判断等距离有约60%方向优势，reward≥risk即可构成正EV，是快速选择交易的实用框架。
- 目标与stop均设为 `1R`；用模型估计`p_equal_move`。
- 只有校准概率下界>`breakeven_p + margin`时执行，不能以主观“看起来好”替代数据。
- 入场后可升级到更远target，但初始1R方案本身必须为正EV。
- Trend pullback、range边缘、强breakout分别校准，禁止混为一个60%模型。

### RANGES-C25-S04：低概率高回报 Basket

- 类型：系统化swing策略框架。
- 依据，PDF p.469–475、477–489、501–503、520–523：40%或更低胜率可凭2–3R+盈利，但必须取完整basket，不能cherry-pick。
- 候选必须由固定规则生成；每笔`net_reward/net_loss >=2`（更低概率需3R+）。
- 对所有合格candidate统一执行，近期盈亏与signal美观度不影响take/skip。
- 至少 `100–300` 个独立/去相关事件评估，并报告最长连败、risk of ruin、drawdown。
- 允许提前退出仅在premise发生可复现变化；不能普遍把2R计划兑现成0.5R。
- Selector新增必须独立训练和样本外比较全量basket。

### RANGES-C25-S05：高概率 Scalp 可选择执行

- 类型：高胜率策略框架。
- 依据，PDF p.469–477、485–497：每个高概率且reward≥risk的交易自身有正EV，可以选择性执行；优势短暂且目标通常小。
- 要求`net_reward >= net_loss`，校准概率下界主测≥`0.55–0.60`。
- 只在明确trend pullback、range edge、strong breakout等预定义context运行。
- 固定target OCO；不把计划1R在执行中缩到0.5R，除非动态EV转负。
- Reward<risk的微scalp单列S13，默认关闭。

### RANGES-C25-S06：动态 EV 更新与 Premise Exit

- 类型：逐bar持仓管理。
- 依据，PDF p.467、491–497、503、519–521：概率、风险、剩余reward每tick变化；原正EV若因TTR/买卖压力转为负，应立即退出。
- 每根完成bar重算`remaining_reward, risk_to_current_stop, p_remaining`。
- `EV_remaining < 0`立即退出；`0 <= EV < margin`尝试最优可成交价退出/减仓。
- Tight range确认、breakout无follow-through、相反pressure累积是模型状态变化，而非P&L理由。
- 若EV仍正，即使价格先逆行也不因恐惧提前退出；stop/premise失效才离场。
- 保存每次更新快照，验证动态退出没有用未来结果。

### RANGES-C25-S07：入场计划与实际管理一致性

- 类型：策略诚信约束与执行器。
- 依据，PDF p.488、493–500：用4R说服自己入场、实际1R退出，或声称小stop后取消并加仓，会把正方程变成负方程。
- 成交前锁定`planned_stop, planned_target, max_scale, early_exit_rules`。
- 实际target不得因轻微盈利而缩小；实际stop不得因亏损扩大。
- 每笔计算`planned_EV`与按真实fills得到的`realized_policy_EV`；持续偏差超过阈值停止模型。
- 所有override带机器可分类reason；“希望回来/觉得该反转”不是合法原因。

### RANGES-C25-S08：强 Breakout 的早期小仓与等幅目标

- 类型：短暂高方向概率策略。
- 依据，PDF p.475、503–512、516–521：强spike使等距离方向概率短暂升高；越早进入，stop可保持而spike/测量目标增长，方程迅速改善。
- Strong spike：`2–4bars` 累计≥`1.5ATR`、同向body≥70%、小tails/overlap、Always-In flip。
- 入场：第二trend bar close/突破或首微pullback；宽stop在spike起点外，仓量缩小至 `25–50%`。
- 目标动态锁定为已完成spike body高度投影；只允许随spike完成向有利方向扩大，不允许回改起点。
- MFE≥1R后可部分止盈/结构trail；保持swing部分到measured move。
- 单根假breakout或已到重大磁力位不适用。

### RANGES-C25-S09：Trend → Channel → Range 的方向概率状态机

- 类型：市场概率框架。
- 依据，PDF p.480–485、512–516：spike中单边性最强，channel中逐渐衰减，到目标/极值会overshoot中性并偏反向，range中部回到约50%。
- 状态：`SPIKE -> CHANNEL -> RANGE_EDGE -> RANGE_MIDDLE`，逐bar因果确认。
- Spike允许S08；channel降低position/缩短目标；到measured magnet及channel top/bottom开启反向range-edge策略；中部不交易等距方案。
- Transition只从结构break、动量衰减、目标到达和双向bars确认，不使用最终日型。
- 输出各状态等距first-passage实证概率，验证定性路径。

### RANGES-C25-S10：Trading Range 边缘的 Directional Probability

- 类型：区间边缘策略框架。
- 依据，PDF p.504–510、513–515：range底部向上等距概率短暂高于50%，顶部向下镜像；靠中点回到中性，TTR虽可有概率但成本吞噬优势。
- Range边界实时确认，entry限外侧25–30%；目标/stop主测相同ATR距离。
- 只有成本后校准下界通过S01才执行；向中点移动时降低`p_remaining`并按S06管理。
- TTR净空间不足时禁用，即使模型给出60–70%。
- Edge突破后按breakout强度切S08或failed-breakout策略，不维持静态range概率。

### RANGES-C25-S11：Measured Move 作为最低可行 Reward

- 类型：目标设定组件。
- 依据，PDF p.503–504、515–520：机构常在最低可使basket正EV的measured move获利；spike body或range height提供目标，但强市场会超过。
- 目标来源优先级预注册：breakout range height、spike open-to-close body、leg1=leg2、明确gap。
- 入场前保存起点/高度；spike继续生长时只能用新完成bar生成新的独立目标版本。
- 第一目标可部分止盈；强follow-through下余仓继续trail。
- 多目标不得事后挑命中者，所有同时存在目标均报告命中/未命中。

### RANGES-C25-S12：坏 Stop Setup 的 Limit Fade 候选

- 类型：反向策略生成器。
- 依据，PDF p.497–500：若某stop entry方程明确为负，例如range底部弱L1 short，则反向limit可能有正EV。
- 原stop setup必须位于错误regime/location且signal弱；计算其目标/stop first-passage概率。
- 反向limit在signal极值处，target与risk至少相等；自身仍必须独立通过S01，不能由“对方差”直接推断必好。
- 模拟limit fill/queue/adverse selection；默认只用于经验型模型。
- Strong trend方向反向fade禁用，除非有独立climax/level模型。

### RANGES-C25-S13：Target 邻近的瞬时高概率管理

- 类型：持仓微观管理，不是新手入场策略。
- 依据，PDF p.488、494–497：距limit仅1tick时可能短暂有80–90%填单概率，即使剩余reward远小于risk；状态仅持续片刻。
- 需要tick-level first-passage与成交队列模型；OHLC数据不生成90%标签。
- 已持仓者若`EV_remaining>0`可短暂等待；回撤 `2–3ticks` 后立即重算。
- Flat trader默认不为最后1–3ticks新开仓，因为成本/延迟通常令EV为负。
- Touch未fill、动量转弱时按S06退出/研究反向failure，不假设必成交。

### RANGES-C25-S14：TTR 的理论 Breakout Swing 仅作高级模型

- 类型：高回报/高压力研究策略。
- 依据，PDF p.471、509–510：TTR边缘以约5ticks风险争取15–20ticks，在约50%方向概率下理论EV很好，但持有压力、反复逆转和执行困难极高。
- Entry必须在边缘20%以内limit，stop在range外，target≥3R；中部禁止。
- 只在成本后空间充分、流动性高、无barbwire queue劣势时研究。
- Range内多次摆动不得改变stop/target；若不能按完整basket执行则禁用。
- 与“完全不交易TTR”基准比较尾部风险、持有时间和实际fill。

### RANGES-C25-S15：弱反转 Signal 只用于退出

- 类型：非对称信号管理。
- 依据，PDF p.502–503：不够清晰的反转不应开启countertrend仓，但可让现有顺趋势持仓减仓/退出。
- Weak reversal score介于退出阈值与入场阈值；阈值在训练集固定。
- 已持仓减 `25–100%`，取决于剩余EV和磁力位；不自动reverse。
- 新反向仓必须等待strong signal或second entry并重新通过S01。
- 评估退出阈值与入场阈值分离是否改善尾部风险。

### RANGES-C25-S16：风险收益概率组合扫描

- 类型：候选参数选择器。
- 依据，PDF p.469–476、489–494：同一setup可能存在70%取1R、60%取1R、40%取2R等多个可行方案，应选择至少一个正EV组合。
- 对预注册target grid `0.5/1/1.5/2/3R`和结构targets估计first-passage probability。
- 只在训练窗口选择EV最高且置信下界>0的组合，随后在下个walk-forward窗口锁定。
- 若所有组合EV≤0则不交易；long/short分别扫描。
- 防止多重选择偏差：nested validation或deflated Sharpe/White reality check。

### RANGES-C25-N01：禁止“高概率 + 大回报 + 小风险”幻想

- 类型：`NEGATIVE`。
- 依据，PDF p.467–469、477–480：高效市场会迅速消除巨大edge；若自认为80%赚3R，概率、target或stop至少一项被误判。
- Flag异常组合：`p>0.70 && reward/risk>2`；必须经过独立大样本验证和保守成本stress，否则拒绝。
- 不用“机构一定怎样”作为概率证据，只用可复现实证。
- 极端edge在样本外衰减时自动停用。

### RANGES-C25-N02：禁止硬编码主观概率

- 类型：`NEGATIVE`。
- 依据，PDF p.473–475、488–516：书中概率是决策直觉，真实值随tick、市场、周期、regime变化且不可精确知道。
- 生产模型只用校准输出；没有模型时`p=0.5`并要求更大reward与安全边际。
- 60/70/80/90%不得作为未经验证的仓位输入。
- 报告Brier score、reliability curve、log loss和分层置信区间。

### RANGES-C25-N03：禁止数据挖掘与小样本日历规律

- 类型：`NEGATIVE`与研究治理。
- 依据，PDF p.501：大量测试必然产生9/10成功的偶然规则，回测80%可能真实仅50%。
- 所有特征/参数实验登记数量；使用时间序列nested walk-forward、purging/embargo和多重检验修正。
- 不以少于30事件的命中率决定生产；关键概率至少100事件并给区间。
- 日历/日期规律需经济机制、跨市场/跨期复现和holdout通过。

### RANGES-C25-N04：禁止 Reward/Stop/Premise 自欺

- 类型：`NEGATIVE`硬约束。
- 依据，PDF p.497–500：用屏幕底部当40tick reward却实际4tick止盈、取消stop后加仓，会使真实方程完全不同。
- 执行器阻止target缩小和stop扩大，合法动态EV退出除外。
- Scale-in必须在初始计划，组合stop/最大风险预先锁定。
- 月度审计计划与真实平均reward/risk、override率；偏差超阈值暂停策略。

### RANGES-C25-N05：禁止 Martingale 与连败后仓位变化

- 类型：`NEGATIVE`风险约束。
- 依据，PDF p.477、485–489及全章basket逻辑：低概率系统需要完整样本，但不能用加倍弥补亏损。
- 仓位不依赖最近trade outcome；相同setup/stop下仅随权益缓慢变化。
- 连败只能触发模型健康检查/暂停，不能放大qty。
- Risk-of-ruin模拟必须包含估计误差、相关亏损和极端slippage。

### RANGES-C25-N06：手续费与 Slippage 不可忽略

- 类型：`NEGATIVE`。
- 依据，PDF p.468、486–497、509：微小edge和1–3tick scalp常被佣金、spread、排队与stop滑点完全吞噬。
- 所有EV使用双边费用、market impact、spread和条件slippage；thin market/report window使用更高stress。
- Limit订单不得touch即假设fill；stop不得假设永远无滑点。
- `gross_EV>0 && net_EV<=0`的candidate必须拒绝并单独统计。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 467–473 | edge、风险收益概率取舍、不同概率setup与交易者方程 | 定义、S01–S05、N01–N02 |
| 473–480 | 方程细节、仓位、对手方、低概率与高概率风格 | S01–S05、S16、N01 |
| 480–487 | 单边/双边市场、scalp与swing对手方、完整basket | S04–S05、S09、N05 |
| 487–493 | 早/晚入场、计划一致、90%瞬时状态、成本示例 | S06–S08、S13、N04、N06 |
| 493–500 | 动态方程、target邻近、limit fade、自欺与双侧正EV | S06–S07、S12–S13、N04 |
| 501–504 | 多重测试陷阱、swing框架、弱signal退出、测量目标 | S11、S15–S16、N03 |
| 504–510 | directional probability、range边缘、中部/TTR与突破 | S03、S09–S10、S14 |
| 510–516 | strong breakout短暂edge、早期入场、channel概率衰减 | S08–S10、N02 |
| 516–523 | spike目标增长、短暂高概率案例、scalper错过低概率趋势 | S04–S06、S08、S11、S13 |

## 4. 回测验收

- 每笔candidate保存`p_win, confidence_interval, stop, target, all_costs, EV, reject_reason`。
- 概率模型按target/stop/context校准，不能把等距概率用于2R目标。
- 使用nested walk-forward并purge重叠label；概率模型与target选择都只在训练期完成。
- 报告Brier/log loss/calibration slope、EV置信区间、profit factor、drawdown和risk of ruin。
- Planned与realized management分别重放；target缩小、stop扩大、非计划scale次数必须为零或有合法S06原因。
- First-passage label在OHLC同bar同时触target/stop时采用保守失败或更细数据，不能假定有利路径。
- 低概率S04按完整candidate basket审计take rate；高概率S05可选择但selector必须固定。
- 成本stress至少基准/2倍/极端三档，微scalp必须通过净EV而非gross EV。
- 所有书中概率和固定点数仅作为研究先验，正式结论以样本外证据为准。
- Figure 25.1–25.3只作章节例证，不作参数拟合或绩效证据。
