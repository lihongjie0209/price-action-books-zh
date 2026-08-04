# 第 16 章：Extreme Scalping

## 元数据

- 英文来源：`books/trading-price-action-reversals/en/chapters/24-ch16-extreme-scalping.md`
- PDF 页码：319–333
- 图表：Figure 16.1；正文逐bar说明已完整覆盖规则，未额外查看图片
- 状态：量化研究规格，未经回测；极端剥头皮默认仅作负面/专家级基线
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 研究边界

```text
net_edge = target × P(win) - stop × P(loss) - fees - spread - slippage
room_to_target = distance(entry, nearest opposing magnet)
executable = room_to_target >= target + cost_buffer
```

- 本章描述5分钟图上一天约`30–40`个潜在scalp，但反复强调绝大多数交易者不应执行。
- `1 point target / 2 point stop`、约`70%`胜率等是作者示例，不可跨品种硬编码；生产候选默认`reward >= risk`。
- 同一价格多空都可能盈利依赖不同持仓管理，并不意味着方向无关或可忽略交易成本。

## 2. 规则卡

### REVERSALS-C16-S01：Scalp Candidate Enumerator

- 类型：研究信号枚举器。
- 依据，PDF p.319–321：平均5分钟图约半数bars可能有合理scalp setup，其中约`1/3` stop entry、`2/3` limit entry。
- 枚举stop-entry reversal/breakout、limit fade、failed breakout、breakout pullback、H/L1–3、double/wedge与magnet test。
- 每个候选保存实时可见context、订单类型和被否决原因；数量描述只作覆盖率审计，不作交易频率目标。

### REVERSALS-C16-S02：Target-Room Gate

- 类型：空间过滤器。
- 依据，PDF p.321、324–327：信号到EMA、昨日收盘/高低及其他磁体距离不足时，即便方向正确也没有足够净利空间。
- `room_to_target`须覆盖目标、spread、slippage及至少`1 tick`安全垫；stop entry还须计入越过signal bar的距离。
- 不满足空间时跳过，或只允许退出既有仓位，不得缩小成本假设强行成交。

### REVERSALS-C16-S03：Stop-Entry Fill-Distance Model

- 类型：成交模型。
- 依据，PDF p.321–323：Emini以stop入场、赚4 ticks，通常需价格越过signal bar约6 ticks；差1 tick即无法成交目标。
- 从实际触发价计量target，不从signal close计量；bar内同时触及按最不利顺序，优先使用tick数据验证。
- 单独报告`missed_by_1_tick`、触发未达目标、breakeven和被迫小亏样本。

### REVERSALS-C16-S04：Immediate-Follow-Through Exit

- 类型：快速失败管理。
- 依据，PDF p.321–324、327–333：窄目标scalp若entry bar弱、未迅速延续或结构变差，应在breakeven或`1–2 ticks`损失退出。
- 入场后`1–3 bars`未产生≥`0.25–0.5 target` MFE，或反向收盘/磁体拒绝出现，则触发scratch exit。
- 与坚持到宽结构止损的版本分开回测，真实计入重复进出成本。

### REVERSALS-C16-S05：Trend-Bar Dual-Hypothesis Test

- 类型：双向事件研究。
- 依据，PDF p.320、322、326–328：大趋势棒既可能延续也可能climax；顺势者等跟进，逆势者在通道超调/阻力处fade并用不同管理。
- Continuation版本要求既有趋势+突破空间；exhaustion版本要求成熟趋势、channel overshoot、磁体或wedge/climax背景。
- 两个版本不得同账户互相掩盖损益；按context score决定是否开放，而非事后选择赢家。

### REVERSALS-C16-S06：Failed One-Tick Breakout Trap

- 类型：失败突破scalp。
- 依据，PDF p.323–326、330–333：一至数tick突破迅速收回会困住突破交易者，其止损可推动反向短程移动。
- 突破结构极值`1–3 ticks`后在`1–2 bars`内收回，并出现反向close/stop trigger时入场。
- Target先取`1R`或range中点；stop在失败极值外，若成本占目标过高则拒绝。

### REVERSALS-C16-S07：Second-Leg Context Filter

- 类型：形态方向过滤。
- 依据，PDF p.322–325、327–330：climax/wedge或强spike后常需第二腿；因此首个逆向L1/H1可能很差，失败后形成HL/LH机会。
- 识别spike/climax、wedge或channel overshoot后，抑制与预期第二腿相反的首入场，优先交易其失败或第二次入场。
- 第二腿窗口测试`5–15 bars`；只有新强spike改变状态才提前取消。

### REVERSALS-C16-S08：Magnet Completion Rule

- 类型：关键价位处理。
- 依据，PDF p.324–327、329–331：离EMA/昨日高低仅一tick时，市场常先完成测试；精确触及与差一tick的订单行为不同。
- 距磁体≤`1–3 ticks`时，不把pullback/test视为完成；先等待触及、明确拒绝或强突破。
- 触及磁体后的fade须有空间门控；突破版本要求收盘距离和跟进，避免把磁体本身当必反转点。

### REVERSALS-C16-S09：Trend Pullback Reentry

- 类型：精选顺势scalp/swing。
- 依据，PDF p.320、325–326、329–333：强趋势中逆势setup常成为顺势entry，EMA/突破位pullback和失败bear/bull setup可重建仓位。
- 既有趋势未flip、pullback达EMA/旧突破位/最近pullback尺度，且反向breakout失败时顺势入场。
- Scalp部分≥`1R`，swing部分沿最近swing trail；本规则作为可生产候选，优先级高于逐bar极端scalp。

### REVERSALS-C16-S10：Barbwire Edge-Only Filter

- 类型：区间位置过滤。
- 依据，PDF p.331–333：重叠大bars或小bars带长尾构成range/barbwire，中部breakout易失败；应在底部买失败下破、顶部卖失败上破。
- tight-range成立时关闭中部stop breakout；只在外侧三分之一执行edge fade/failed breakout。
- 强突破并有跟进后才退出edge模式，随后等待breakout pullback。

### REVERSALS-C16-S11：Session-Time Frequency Control

- 类型：时段门控。
- 依据，PDF p.320、331–333：高强度scalping最多可能只适合`1–2h`；中间三分之一更常range且动能弱。
- 将open、middle、close分层；middle默认降低仓位/频率并提高空间与信号门槛。
- 限制每日/每小时候选成交数，报告连续决策导致的成本和绩效衰减。

### REVERSALS-C16-S12：Scale-In Recovery Sandbox

- 类型：专家级反事实研究。
- 依据，PDF p.320、326–327：多空scalper可按大bar尺度逆向加仓，在首入场breakeven处让后续腿盈利，但作者未给完整风险细节。
- 仅沙盒测试：最多`2–3`腿，层距`0.25–0.50 × signal_bar_range`，全仓stop≤`1.0 × signal_bar_range`外加滑点。
- 总最坏风险不得超过账户预算；必须与单次入场版本比较tail loss、成交依赖和保证金占用。

### REVERSALS-C16-N01：多数交易者禁止 Extreme Scalping

- 类型：`NEGATIVE`生产约束。
- 依据，PDF p.319–320、333：高频读图和执行对绝大多数人几乎不可行，章节目的主要是展示信息密度。
- 默认生产配置关闭S01逐候选交易；只有独立样本、真实成本后达到验收门槛才可解锁。

### REVERSALS-C16-N02：禁止 Reward 小于 Risk 的常规策略

- 类型：`NEGATIVE`风险收益约束。
- 依据，PDF p.319、333：风险大于收益通常需约70%胜率，多数人不现实；至少1:1、最好2:1更稳健。
- 主策略强制`target >= stop + costs`；低于1:1只作为隔离的专家反事实，不得并入推荐结果。

### REVERSALS-C16-N03：潜在 Setup 数不等于可交易数

- 类型：`NEGATIVE`选择偏差约束。
- 依据，PDF p.319–320、333：5分钟图可见数十setup并不是执行它们的理由，经验交易者只取一小部分。
- 报告candidate→eligible→submitted→filled漏斗；禁止用事后标注的全部机会计算可实现收益。

### REVERSALS-C16-N04：不可假定 Limit Touch 即全量成交

- 类型：`NEGATIVE`微观结构约束。
- 依据，PDF p.323–326：精确低点/高点常有大量排队，交易者可能只能在下一tick成交或完全错过。
- Limit版本必须测试queue haircut、partial fill和missed fill；大仓位不得使用零冲击模型。

### REVERSALS-C16-N05：未披露的加仓止损不可推定安全

- 类型：`NEGATIVE`模型约束。
- 依据，PDF p.319–320：作者的极端scalper案例未披露保护止损和加仓损失上限。
- 不以收入/房产轶事作绩效证据；任何S12实验必须显式封顶风险并展示最坏尾部情景。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 319 | 高频机构不可复制、极端scalp少数人可行、风险收益与所需胜率 | N01–N02、N05 |
| 320 | 数十setup但不应全做、stop/limit比例、同价双向管理与scale-in | S01、S05、S12、N03 |
| 321 | 1点目标/2点stop、stop entry需额外行程、磁体空间不足 | S02–S04 |
| 322 | breakout pullback、趋势延续与climax双重解释 | S05、S07、S09 |
| 323 | wedge后第二腿、差一tick失败、limit排队与坏L1 | S03、S06–S07、N04 |
| 324 | 一tick失败、outside-up/expanding triangle、磁体未触及 | S06–S08 |
| 325 | 强breakout、失败L2转breakout-pullback long | S05、S07–S09 |
| 326 | 不同深度limit、trapped bears、micro-wedge与climax | S05–S08、S12 |
| 327 | 昨高阻力、趋势棒exhaustion、双向scalp管理 | S02、S05、S12 |
| 328 | ii/iii bull trap、两腿修正、lower-high limit shorts | S06–S07 |
| 329 | 横向修正是bull strength、弱EMA下破、旧AI未翻转 | S04、S08–S10 |
| 330 | breakout failure、止损簇与wedge bull flag重入 | S06、S09 |
| 331 | 昨高处反转、重叠大bars形成range、顶部不追多 | S02、S10–S11 |
| 332 | 日中range、barbwire、边缘breakout fade | S10–S11 |
| 333 | 日中低动能但形态可用、极端scalp多数亏损、只取少数 | S09–S11、N01–N03 |

## 4. 回测验收

- 主报告以`reward >= risk`的精选版本为准；极端scalp、逆势和scale-in结果全部隔离并标红风险等级。
- 使用tick/quote数据重建stop触发、limit排队、partial fill、同bar路径和真实滑点；只有OHLC时采用最不利成交。
- 报告candidate、eligible、submitted、filled、target、scratch、stop逐层数量以及missed-by-one-tick比例。
- 胜率必须附置信区间；验证净盈亏平衡胜率是否覆盖费用，不得把作者`60%/70%`当输入事实。
- 按趋势/区间、open/middle/close、stop/limit、顺势/逆势及磁体距离分层报告EV、MAE/MFE和尾部损失。
- 做延迟、spread、slippage、queue haircut、仓位规模与每日最大交易数压力测试；零成本只作上界。
- Scale-in版本逐腿记账、限制总风险并报告最坏gap；任何依靠无限加仓或未定义stop的版本直接拒绝。
- Figure 16.1仅用于规则覆盖，不作为可复制的40笔机会、成交质量或盈利证据。
