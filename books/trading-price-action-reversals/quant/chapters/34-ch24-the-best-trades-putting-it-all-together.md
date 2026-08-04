# 第 24 章：The Best Trades—Putting It All Together

## 元数据

- 英文来源：`books/trading-price-action-reversals/en/chapters/34-ch24-the-best-trades-putting-it-all-together.md`
- PDF 页码：439–504
- 图表：Figure 24.1–24.24；正文逐bar说明已完整覆盖规则，未额外查看图片
- 状态：量化研究规格，未经回测；本章是前三本书的组合路由与精选层
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Best-Trade Router

```text
regime ∈ {SPIKE, STRONG_TREND, CHANNEL, TRADING_RANGE, TIGHT_RANGE, REVERSAL_TRANSITION}
gross_EV = p_target × reward - (1-p_target) × risk
net_EV = gross_EV - commissions - spread - slippage
best_trade = net_EV > margin AND setup_score >= threshold AND execution_feasible
```

- 市场按`range → breakout/spike → channel → range → breakout/reversal`循环；同一pattern只有在正确regime和位置中才是best trade。
- 作者的`50/60/70/80/90%`均作为待检验置信档，不是模型输入事实。

## 2. 规则卡

### REVERSALS-C24-S01：Point-in-Time Regime Router

- 类型：母状态机。
- 依据，PDF p.439–443、448–450：市场在趋势、通道、区间和突破/反转间循环，交易方法必须随状态改变。
- 用AI、斜率、同侧EMA比例、trend-bar persistence、overlap、tails及range boundary实时分类。
- 状态不明输出UNCERTAIN并降频；不得用最终日型回填早期状态。

### REVERSALS-C24-S02：Trader-Equation Admission Gate

- 类型：全局准入。
- 依据，PDF p.439–440、446–448、452–464、481–483、502–504：任何交易必须满足概率×收益大于失败概率×风险和成本。
- 主版本要求`net_EV≥0.05–0.20R`；概率由训练期同类样本校准，未知时使用保守下界。
- 初学者子集要求`reward≥2R`且校准胜率约≥50%，或`reward≥1R`且约≥60%。

### REVERSALS-C24-S03：Strong-Spike Urgency Entry

- 类型：高动量入场。
- 依据，PDF p.439–445、454–455、466–472：成功强breakout中机构以市价、收盘及小pullback急迫进入；宽stop需缩仓。
- 连续`2–4`强趋势棒、低重叠、小尾和结构突破成立时，在close/market或H/L1入场。
- Stop在spike起点或可证伪结构外，qty按R反比；climactic超大bar触发S12而非追单。

### REVERSALS-C24-S04：Strong-Trend EMA Second-Entry Pullback

- 类型：最高优先级顺势策略。
- 依据，PDF p.443–456、466–481、486–490：清晰AI趋势中EMA H2/L2、wedge/triangle及首pullback是最可靠交易之一。
- AI明确、绝大多数bars在EMA同侧，pullback`1–3 legs`触及EMA/突破位且同向signal bar触发。
- Stop在pullback extreme外；首目标`1R`，保留runner至`2R+`/新趋势极值。

### REVERSALS-C24-S05：First Pullback after Strong Spike

- 类型：趋势早期再入场。
- 依据，PDF p.443–445、455、468–473、486–490：强spike后的首H/L1–2或micro-channel breakout pullback通常高质量。
- Spike未climax且AI未flip时，首个小pullback/EMA test的同向signal触发。
- Pullback过深、强逆向spike或final-flag背景则取消。

### REVERSALS-C24-S06：Major Trend Reversal Strict Checklist

- 类型：强反转精选。
- 依据，PDF p.443、453–454、474、484–497：MTR需强趋势线破坏、第一反向腿有动量，再测试旧极值形成HL/LL、LH/HH/double且signal强。
- 清单全部满足才入场；缺一项降为scalp/观察，不包装为MTR swing。
- Stop在test extreme外；目标`2R`、旧channel起点或range另一端。

### REVERSALS-C24-S07：Strong Final-Flag Reversal

- 类型：末段反转。
- 依据，PDF p.443–444、469、475、482–486、498–501：成熟swing/弱channel后的H/L1–2、ii/triangle小flag突破失败可成为高质量final flag。
- 要求成熟move+climax/三推/累积反向压力+强反向signal或二次入场。
- 目标至少两腿/`2R`；强趋势中弱final flag只减仓，不逆势。

### REVERSALS-C24-S08：Stairs Third/Fourth-Push Fade

- 类型：阶梯回测。
- 依据，PDF p.443–444、486–490：bear stairs第三/四次下破买回前一阶低点，bull镜像。
- 至少三次同向push且新breakout缺跟进，在反向signal触发。
- 目标前一push extreme；若强spike确认新趋势则立即取消。

### REVERSALS-C24-S09：Measured-Move Weakening Reversal

- 类型：目标区反转。
- 依据，PDF p.443–444、483–500：spike/channel或trending-range到measured move且动能衰减、三推/final flag时可反转。
- Measured level仅作context；需selling/buying pressure、channel overshoot及signal确认。
- 先目标channel底/顶或`1R`，只有AI flip才保留大swing。

### REVERSALS-C24-S10：Trading-Range Edge Second Entry

- 类型：区间fade。
- 依据，PDF p.440–443、444、457–459、481、499–504：区间顶部short、底部long，尤其second entry/wedge/double；强边缘spike多数失败。
- Range外三分之一且出现第二次失败/微型double/反向signal时入场；中部关闭。
- 目标中点后另一边，至少`reward≥risk`；强breakout+跟进转S11。

### REVERSALS-C24-S11：Confirmed Breakout Pullback

- 类型：区间转趋势。
- 依据，PDF p.442–445、457–459、467–488：初学者不追range breakout，等强突破和首次pullback/失败反向setup。
- Breakout bar强、收盘越界且`1–2 bars`跟进后，回测边界未收回时顺势入场。
- Target range measured move/`2R`，stop在pullback失效点。

### REVERSALS-C24-S12：Climax-to-Two-Leg Correction

- 类型：趋势末段管理。
- 依据，PDF p.469、482–485、498：长期趋势后的巨大bar、连续climax、channel overshoot通常引出至少两腿修正。
- 趋势年龄`10–30 bars`+最新bar range高分位+反向压力时停止追趋势并减仓。
- 反向新仓仍需S06/S07；否则等两腿完成后恢复S04。

### REVERSALS-C24-S13：Actual-Risk Dynamic Management

- 类型：止损与目标重算。
- 依据，PDF p.467–469、474、477–480：新HL/LH形成后结构stop收紧，实际risk下降，最低正EV目标随之重算。
- 初始stop在signal/pullback/spike结构外；entry bar强时可移至其另一端。
- 达`0.5–1R`且趋势恢复后才移breakeven；首次回测入场价前不得过早收紧。

### REVERSALS-C24-S14：Scale-Out and Swing Runner

- 类型：仓位管理。
- 依据，PDF p.454–457、467–480、497–504：best swing可在`1R–2R`减仓，余仓沿swing极值/AI持有。
- 测试`25%–50%`于1R、再减于2R，余仓到premise失效/AI flip/session close。
- 多次顺势setup默认只补回scalp部分，避免runner累积超风险舒适度。

### REVERSALS-C24-S15：Limit-Order Expert Contexts

- 类型：高级执行层。
- 依据，PDF p.444–446、468–480、486–490：limit只宜顺AI、quiet EMA flag、弱逆势H/L1–2、预期breakout pullback或按既往pullback尺度加仓。
- 仅当AI/即将flip方向与订单一致，最多`1–3`层且总风险封顶。
- 与stop-entry版本分开，模拟queue/partial fill；初学者配置关闭。

### REVERSALS-C24-S16：Failed Near-AI-Flip Fade

- 类型：趋势延续失败策略。
- 依据，PDF p.445：AI flip只差一根确认bar但breakout弱时，fade该bar并押跟进失败。
- 原AI强、反向breakout score低且未破关键结构，下一bar未确认时顺原趋势入场。
- 若确认bar出现立即退出/反手，不允许希望原trend恢复。

### REVERSALS-C24-S17：Beginner Safety Profile

- 类型：简化生产配置。
- 依据，PDF p.445–452、459–465、475–480：初学者只用stop entry、同向signal bar、固定小仓、固定bracket、每日少量清晰交易。
- 只开放S04、S06、强opening reversal、S11和非climax S03；每日`1–5`笔，`reward≥2R`优先。
- 入场后不得随意把swing改scalp或把target降到risk以下。

### REVERSALS-C24-S18：Setup Frequency and Candidate Funnel

- 类型：精选与容量控制。
- 依据，PDF p.448–465：单图可见大量setup但多数不可实时执行；关注一个市场/周期和少数best trades。
- 输出`raw candidate → context eligible → equation passed → executable → filled`漏斗。
- 初学者每日上限`1–5`，经验版本`5–10`；数量不是盈利目标。

### REVERSALS-C24-S19：I-Don't-Care Risk Scaling

- 类型：心理风险代理。
- 依据，PDF p.445–446、451、464–466、496：仓位过大造成违背计划，应从常规认知规模降到`20%–33%`或更小。
- 账户风险默认`0.10%–0.25%`，若出现提前平仓/移动stop等行为代理则自动降档。
- 只有连续数周/月样本外盈利且执行偏差稳定，才能逐级增加容量。

### REVERSALS-C24-S20：Volatility-Normalized Position Sizing

- 类型：极端波动风险。
- 依据，PDF p.440、452–455、490、495–497：bar异常大时stop扩大、仓位反比缩小；2008案例用约20%常规规模。
- Risk distance取结构stop且不得小于噪声下界`0.5–1 ATR`；qty按固定账户风险计算。
- 比较常规、`0.2–0.5×`size和跳过版本，纳入slippage/limit风险。

### REVERSALS-C24-S21：Low-Probability Basket Consistency

- 类型：策略一致性约束。
- 依据，PDF p.446–447：低概率高回报策略只有作为完整basket才有数学意义，随意挑选会破坏期望。
- 若校准胜率<50%且reward≥2–4R，必须对所有预先定义合格信号一致执行或全部关闭。
- 报告missed-signal反事实；不能根据主观“更好看”事后筛选。

### REVERSALS-C24-S22：No-Clear-Trend New-Extreme Fade

- 类型：双向日策略。
- 依据，PDF p.499–501：非clear trend日，优先fade新极值，尤其second entry、wedge和final flag。
- S01为TRADING_RANGE/UNCERTAIN，new high/low突破失败并有合格signal时反向。
- 强move到极值时等待第二signal；目标prior swing/range opposite side。

### REVERSALS-C24-N01：禁止 Tight Trading Range Stop Entries

- 类型：`NEGATIVE`硬约束。
- 依据，PDF p.442–443、458、464、475–476：tight range压倒其他理由，stop entry长期亏损。
- Tight-range状态下submitted stop entries为零，直到breakout和后续判断完成。

### REVERSALS-C24-N02：禁止逆明确趋势 Scalp

- 类型：`NEGATIVE`方向约束。
- 依据，PDF p.449–450、467、472–480：弱channel反转棒诱人但多数只是flag，逆势scalp风险收益差。
- AI明确时普通配置只顺势；只有S06/S07严格反转可逆向。

### REVERSALS-C24-N03：禁止 Reward 小于 Risk 的普通 Scalp

- 类型：`NEGATIVE`数学约束。
- 依据，PDF p.445–448、459–463：高胜率小target仍可能负EV，多数交易者无法达到所需约80%–90%。
- 主系统强制净reward≥risk；低于1R只作隔离专家基线。

### REVERSALS-C24-N04：禁止用一分图寻找逆五分趋势反转

- 类型：`NEGATIVE`周期约束。
- 依据，PDF p.450：1m反转频繁，多数成为5m flag并使交易者错过主趋势entry。
- 5m主策略不得由1m反向signal触发；1m仅可改善同方向执行。

### REVERSALS-C24-N05：Setup 存在不等于应交易

- 类型：`NEGATIVE`过度交易约束。
- 依据，PDF p.463–465：每几bars都有setup，事后可见数十机会，但多数太快或不清晰。
- 未通过S02与S18漏斗的candidate不得成交或计为可实现利润。

### REVERSALS-C24-N06：作者概率和收入案例不得作为绩效证据

- 类型：`NEGATIVE`研究约束。
- 依据，PDF p.443–504：章节大量经验概率、点数和收入示例只是指南。
- 全部概率由样本外估计并给置信区间；收入/规模示例不得进入回测假设。

### REVERSALS-C24-N07：不得过早移动 Breakeven Stop

- 类型：`NEGATIVE`持仓约束。
- 依据，PDF p.454–457、477–485、503–504：swing常回测entry并扫breakeven后恢复，premise有效应容忍pullback。
- 未达到S13恢复条件不得移BE；被扫后不得因情绪拒绝下一合格entry。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 439 | 市场为range/breakout竞争、edge与trader equation | S01–S02 |
| 440 | Spike宽risk、channel难入、range中强spike诱导追高杀低 | S01–S03、S10 |
| 441 | Bull trend从breakout到channel再到range的交易行为 | S01、S03–S05 |
| 442 | 趋势衰减、range edge、micro-channel breakout pullback、tight range | S01、S10–S11、N01 |
| 443 | Range突破重启循环与best-trade总清单 | S01、S06–S12 |
| 444 | EMA H/L2、wedge、breakout pullback、range edge与limit经验要求 | S04–S11、S15 |
| 445 | 专家limit contexts、near-flip失败fade与初学者规则起点 | S15–S17 |
| 446 | 初学者stop/bracket/小仓/少交易与高概率swing | S02、S17–S19 |
| 447 | 低概率basket一致性、交易数学与tight range误判 | S02、S21、N01、N03 |
| 448 | 1-tick scalp负数学、聚焦单市场/单周期 | S02、S18、N03 |
| 449 | 状态循环、等待best trade、逆势scalp危险 | S01、S18、N02 |
| 450 | EMA同侧顺势、禁逆势scalp及低周期反转陷阱 | S01、S04、N02、N04 |
| 451 | 简化决策、stop entry、固定计划、小仓及每日三笔 | S17–S19 |
| 452 | Opening/强反转/强趋势pullback、合理stop范围 | S02–S06、S17、S20 |
| 453 | 正EV组合、best-trade概率/回报两档、严格MTR | S02、S06 |
| 454 | MTR持有pullback、opening-range强setup与spike entry | S03、S06、S13–S14 |
| 455 | Spike后EMA L2、强trend MA pullback、分批与BE | S04–S05、S13–S14 |
| 456 | Pullback心理困难、两腿EMA setup和runner | S04、S14 |
| 457 | 多数反转成flag、trend/range转换及强趋势H2管理 | S01、S04、S10、S13–S14 |
| 458 | 不明时选spike pullback、禁tight range、range突破等pullback | S05、S10–S11、N01 |
| 459 | Range edge second entry、无趋势新极值fade、stop entry与保护止损 | S10、S17、S22 |
| 460 | 小scalp不可持续、swing与always-in风格比较 | S02、S14、S18、N03 |
| 461 | 中间风格、1R高概率/2R swing、OCO与趋势加仓 | S02、S14、S17–S18 |
| 462 | Trader equation、scalper dilemma、channel难交易 | S02、S04–S05、N03 |
| 463 | Tight channel等breakout、每天精选1–3笔、premise有效持有 | S05、S13、S18、N01、N05 |
| 464 | 大量setup不可执行、tight range禁入、初始极小仓 | S18–S19、N01、N05 |
| 465 | 扩仓前稳定盈利、I-don't-care size、无需等待完美pattern | S18–S19 |
| 466 | 强bull AI中pullback为best trade | S04 |
| 467 | 多标签bottom、强趋势忽略countertrend、actual risk重算 | S04、S13、N02 |
| 468 | Treasury强trend pullback、H1防错失stop与breakout pullback | S04–S05、S11 |
| 469 | Final flag后两腿、MA ii与宽spike/窄pullback风险权衡 | S04、S07、S12–S13 |
| 470 | EUR/USD AI pullback与strong reversal second entry | S04、S06 |
| 471 | 两腿MTR管理、AI H1/H2与EMA safer entry | S04、S06、S14 |
| 472 | Micro-channel breakout pullback与IBM强bear MA L2 | S04–S05、S11 |
| 473 | 强bear首MA rally仍为flag | S04、N02 |
| 474 | Daily bull H2、MTR多成range、BE stop | S04、S06、S13 |
| 475 | Trend-from-open H2及tight range停手 | S04、N01 |
| 476 | Tight range stop entries与scale-in风险 | S15、N01 |
| 477 | AAPL 20-gap short、entry-bar stop与BE条件 | S04、S13 |
| 478 | 部分止盈、BE扫损及breakout-test reentry | S13–S14 |
| 479 | Small-pullback bear只short、固定风险缩仓 | S04、S19–S20、N02 |
| 480 | 趋势日反转禁入及first-pullback extreme test | S04–S05、N02 |
| 481 | Daily bull breakout-bar low limit与buy-low/sell-high例外 | S04、S10、S15 |
| 482 | 1R/60% best trade、wedge EMA与reward≥risk | S02、S04 |
| 483 | 长trend巨大bar climax、两次失败、强反向two-bar reversal | S07、S12 |
| 484 | Selling pressure累计、AI强bear spike与lower-high short | S01、S06 |
| 485 | 不过早tighten、range转bear breakout的windfall | S11、S13–S14、N07 |
| 486 | CX强bear spike、EMA first pullback和L2 | S04–S05 |
| 487 | MTR需再一次TL break/test、bull spike后H2 | S04、S06 |
| 488 | GOOG TL break后测试bear low与second attempt | S06 |
| 489 | Stop-running breakout test、two-leg预期、bear spike pullbacks | S04–S06、S13 |
| 490 | 弱bottom先scalp、AAPL lower-high breakout test | S06、S14 |
| 491 | AMZN两腿lower-high MTR多重confluence | S06 |
| 492 | GS expanding-triangle reversal与vacuum到range edge | S06、S10 |
| 493 | Expanding triangle目标及MSFT HL/HH MTR | S06、S10 |
| 494 | ORCL range-top buy vacuum、三推short | S06、S10 |
| 495 | Emini多周期opening reversal组合 | S06、S17 |
| 496 | 极端bar缩至20%仓、channel overshoot和等待HL | S19–S20 |
| 497 | 两腿后5m HL确认、2R减仓与trail | S06、S14 |
| 498 | Treasury final flags、连续climax后两腿 | S07、S12 |
| 499 | 未触发signal不成交、two-sided day范围扩张 | S10、S22 |
| 500 | Bear flag弱于spike、measured-move处强parabolic reversal | S09、S22 |
| 501 | 无clear trend fade new extremes/second entries | S22 |
| 502 | Trading range中约50%方向、reward需显著大于risk | S02、S10 |
| 503 | 小当日range扩张假设、4R target与AI转short | S02、S11 |
| 504 | Holiday ADR与差一tick目标的保守退出 | S02、S13–S14 |

## 4. 回测验收

- Regime、AI、pattern、概率、risk和target全部逐barpoint-in-time输出；禁止用最终日型或图例编号做标签。
- 每种best-trade类型单独报告candidate、eligible、filled、胜率、净EV、MAE/MFE、持仓和成本，不只报告精选汇总。
- 概率用anchored walk-forward校准并给置信区间；作者的概率、日频和点数仅作待检验假设。
- 比较beginner stop-only、expert limit、1R scalp、2R swing、scale-out runner和low-probability basket版本。
- 所有版本保持相同账户风险；spike/极端波动按结构stop缩仓并模拟slippage、gap和同bar路径。
- 审计tight-range零stop-entry、明确AI零普通逆势scalp、净reward≥risk、无未来状态泄漏和candidate漏斗完整性。
- Figure 24.1–24.24只作章节覆盖和组合案例，不作为参数、概率、绩效或可执行性证据。
