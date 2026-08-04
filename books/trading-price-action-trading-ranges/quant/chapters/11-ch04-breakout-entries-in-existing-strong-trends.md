# 第 4 章：既有强趋势中的突破入场

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/11-ch04-breakout-entries-in-existing-strong-trends.md`
- PDF 页码：134–139
- 图表：Figure 4.1–4.2；正文与图注已逐bar说明，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 前置状态

- 本章只适用于`trend_strength>=0.70`且Always-In方向明确；否则转普通breakout/range规则。
- 强趋势代理：连续同向trend bars、trending swings、EMA单边、回调小、旧极值突破可取得scalp profit。
- `new_extreme_event`在价格首次越过已确认swing high/low时冻结，记录突破前趋势强度、推进序号及是否已有主要trend-line break。

## 2. 规则卡

### RANGES-C04-S01：强趋势旧极值 Stop Breakout

- 类型：完整顺势突破策略。
- 依据，PDF p.134–137：强趋势中每次越过prior extreme都是有效顺势入场；极强时可从新高/低持有swing，但一般pullback更优。
- Setup：前置状态成立；当前推进不是S05第三推进/反转高风险分支。
- 入场：prior swing外1tick stop；跳空时按实际成交并重算仓位。
- 止损：最近minor pullback swing外。
- 目标：预冻结scalp target、spike高度等幅、1R/2R。
- 管理：trend score 0.70–0.85以scalp为主；≥0.85且有强breakout bar/follow-through时保留 `50–100%` swing。
- 失效：`1–2bars` 内回到旧极值且未先达scalp目标，转S04。

### RANGES-C04-S02：优先 Pullback 的更优入场

- 类型：顺势pullback策略。
- 依据，PDF p.134、136–138：price-action traders通常在High/Low 1/2、failed wedge、trend-line failure、MA gap等更早入场；风险收益优于在新极值追价。
- Setup：强趋势中从旧极值产生首次/第二pullback，未确认Always-In翻转。
- 入场优先级：prior bar不利极值limit → High/Low 1 → High/Low 2/EMA → S03兜底breakout。
- 入场：signal bar外stop，limit版本按真实排队成交。
- 止损：pullback结构极值外。
- 目标：旧极值、spike测量移动、1R/2R。
- 研究中配对同一趋势腿的pullback与新极值breakout，比较实际风险、MFE和漏单。

### RANGES-C04-S03：错过早期入场的 Worst-Case Stop

- 类型：参与保障策略。
- 依据，PDF p.134–137：极强趋势初期多为High/Low 1而非期望的深High/Low 2；错过limit和首入后，应在spike极值外放兜底stop。
- Setup：由3根以上强同向bars形成spike，首次pullback开始，当前尚未持仓。
- 在spike extreme外1tick放顺势stop；若先通过S02成交则取消。
- 触发bar通常也应为大同向trend bar；若触发后是doji/反向bar，降低持仓为scalp。
- 止损：最近pullback极值外；风险过宽则减仓，不改变结构stop。
- 目标：spike等幅、1R/2R。
- 禁用：第三推进、主要trend-line break后的旧极值测试、final flag或明显two-sided trading。

### RANGES-C04-S04：新极值反应的趋势强度诊断

- 类型：状态转换与失败突破策略。
- 依据，PDF p.135：突破后足够让stop buyer获得scalp，表示买/卖方继续控制；若1–2bars内反转，则更像range，趋势可能正在转弱。
- 在事件前冻结`scalp_target=max(3*costs, 0.25–0.75ATR)`。
- `BUYERS/SELLERS_CONTROL`：先到scalp target再回穿旧极值，维持/提高trend score。
- `FADE_CONTROL`：先回到旧极值内，降低trend score `0.15–0.30`，停止S01/S03追价。
- 失败突破入场：回归signal bar外反向stop；止损在新极值外；目标EMA/range中点/1R。
- 连续2次`FADE_CONTROL`或出现双向trend bars后，切换`TREND_TO_RANGE_CANDIDATE`。

### RANGES-C04-S05：第三推进与 Trend-Line Break 后过滤

- 类型：突破门控。
- 依据，PDF p.137–138：不能盲买每个新高；第三推进以及主要trend-line break后的higher high/lower low测试更可能final flag或反转。
- 推进计数在新的强spike/Always-In重置后从1开始。
- 第三推进新极值：禁止S01，优先止盈；等待失败突破或S02深pullback。
- 主要trend-line break后首次旧极值测试：只有强breakout bar+2bars跟进才恢复顺势breakout；否则候选反转。
- 若failed wedge反而强势顺趋势突破，视为新spike并重置计数，可按S01交易。
- 所有过滤事件保留，以衡量错过延续的机会成本。

### RANGES-C04-S06：弱新极值的高级 Limit Fade/Scale

- 类型：高级逆势scalp。
- 依据，PDF p.135、137–138：非极强趋势中，bears/bulls可在旧高/低或其外limit并加仓，期待数bars内breakout test，使首腿保本、后腿盈利。
- 仅在trend score<0.85、S05风险上下文或已有S04失败证据时启用。
- 入场：old extreme及外侧 `0.10–0.50ATR`，最多2–3腿。
- 共同止损：预定义结构极值外；所有腿最坏损失≤单笔账户预算。
- 退出：weighted average、首入价、EMA依次测试；按scalp管理。
- 若breakout score转STRONG并有follow-through，立即止损；禁止继续逆势scale。

### RANGES-C04-S07：强趋势的次日顺势 Follow-Through

- 类型：跨session延续策略。
- 依据，PDF p.138–139：强trend-from-open日后，次日通常有足够follow-through形成至少名义新极值，即使先pullback。
- Setup：前session trend score≥0.80，收盘位于方向端20%，且无确认反转。
- 次日等待higher low/lower high、High/Low 1–4、double bottom/top或opening pause顺势突破。
- 入场：signal bar外stop；若次日出现新强spike，允许小仓市价参与。
- 止损：次日pullback结构外。
- 目标：前日极值、1R/2R、次日range目标。
- 失效：次日反向opening spike翻转Always-In；跨夜gap按实际价格，不假设前收成交。

### RANGES-C04-N01：不能因为“强趋势可随时入场”而忽略位置

- 类型：`NEGATIVE`。
- 依据，PDF p.134–138：强趋势中任何顺势入场可能盈利，但pullback方程通常更好；第三推进/final flag/趋势线突破后追价仍不明智。
- “任何价都能买卖”只在前置trend state成立且结构stop可承受时使用。
- S05触发时禁止用该口号覆盖反转风险。
- 必须记录实际entry quality，不能只因最终趋势延续把所有追价判正确。

### RANGES-C04-N02：逆势 Scalp 不得妨碍顺势 Swing

- 类型：`NEGATIVE`。
- 依据，PDF p.138–139：强趋势中逆势scalp只适合能立即重新翻回顺势者；否则会退出好仓并错过更大的恢复腿。
- 标准模型在trend score≥0.85时禁用S06及普通逆势signal。
- 若启用高级模型，逆势仓目标≤1R，并在首个顺势bar恢复时强制平仓/反手。
- 独立报告因逆势交易错过的顺势信号和机会成本。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 134–135 | 强趋势新极值有效、早期pullback与兜底stop | S01–S04 |
| 135 | 新极值能否获得scalp诊断trend/range | S04、S06 |
| 136–138 | 多种breakout/pullback、第三推进过滤与limit fade | S01–S06、N01 |
| 138–139 | 强趋势次日跟进及逆势scalp限制 | S07、N02 |

## 4. 回测验收

- trend strength和new extreme均实时确认；不得以未来7连bar等信息回填早期标签。
- S01/S02在同一swing上配对，报告entry差、stop差、漏单和完整期望值。
- S03只统计确实错过早期入场的事件，成交时按gap/slippage重算风险。
- S04用first-passage严格判断scalp target与返回旧极值的先后。
- S05推进计数必须在强spike重置，并报告每个过滤原因的边际效果。
- S06模拟limit队列和共同stop路径，不以最终均价掩盖最大风险。
- S07使用完整隔夜/次日数据，按前日趋势类型和gap方向分层。
- Figure 4.1–4.2仅作章节例证，不作参数拟合或绩效证据。
