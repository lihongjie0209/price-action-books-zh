# 第 3 章：初始突破

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/10-ch03-initial-breakout.md`
- PDF 页码：124–133
- 图表：Figure 3.1–3.3；正文与图注已逐bar完整说明，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Initial Breakout 状态机

```text
BREAKOUT_ATTEMPT -> STRONG_SPIKE -> FIRST_PAUSE
FIRST_PAUSE -> CHANNEL_CONTINUATION
FIRST_PAUSE -> RETURN_TO_RANGE
FIRST_PAUSE -> OPPOSITE_TREND
```

- `BREAKOUT_ATTEMPT`：首次收盘越过已登记range、flag、swing或trend line。
- `STRONG_SPIKE`：1根大trend bar或多根同向bar；极强版本至少3根、重叠少、尾部小。
- `FIRST_PAUSE`：首根inside/doji/逆向bar或首次不再创新极值的bar。
- 每个终态按确认时间互斥记账，不能从日终趋势向前回填初始突破成功。

## 2. 规则卡

### RANGES-C03-S01：Initial Breakout Spike 入场

- 类型：完整突破策略。
- 依据，PDF p.124–127：显著成功突破通常每天至少数次，从一根较大trend bar开始；最强形态为连续trend bars、低重叠和未能回到prior close的urgency。
- Setup：突破bar range≥过去20bars中位数 `1.2–2.5倍`，body/range≥0.60，close在顺势端25%，并突破结构至少 `0.05–0.25ATR`。
- 强确认：连续2–3bars同向，body overlap≤0.35；prior close的limit未触及作为urgency加分。
- 入场：breakout close小仓、下一bar市价或1–2ticks/`0–0.15ATR` 回撤。
- 止损：spike起点/突破结构另一侧。
- 目标：spike高度 `0.75/1/1.25×`、1R/2R；极强spike保留仓位期待channel。
- 仓位按结构风险反推；止损距离为常态2–3倍时，仓位约缩为1/2–1/3。

### RANGES-C03-S02：首个 Pause 的 High/Low 1

- 类型：第一次pullback延续策略。
- 依据，PDF p.124–127、129：极强breakout后的首个inside/small/逆向bar常是可靠High/Low 1，但也可能返回range或反转。
- Setup：S01确认后首次pause，持续 `1–2bars`，未强势穿回breakout point。
- 入场：pause顺spike极值外1tick stop。
- 止损：pause极值或spike起点外；分别测试。
- 目标：spike极值、spike等幅、1R/2R。
- 若pause为大逆向reversal、持续 `3–10bars` 或回撤spike>0.50，降低评分并等待High/Low 2。
- 若突破失败后原失败反转又失败，按breakout pullback同向入场，不重复计为新initial breakout。

### RANGES-C03-S03：Measured Move 目标的最近优先原则

- 类型：目标/止盈组件。
- 依据，PDF p.127–130、133：spike、opening range、failed wedge等都有多个合理测量点；先看最近目标，越过后再启用更远目标。
- 事件时冻结候选高度：spike open/low→close/high、opening range、flag/wedge高度、leg 1。
- 从对应breakout point投射 `0.75/1.0/1.25×H`。
- 候选按距当前价从近到远排序；触及最近zone `±0.10–0.30ATR` 前，远目标不能成为提前加仓理由。
- 到目标后仅止盈/停止追价；只有强反转setup才允许逆势。
- 不得根据最终high/low选择正好命中的起点。

### RANGES-C03-S04：强 Bar 快速失败的反向交易

- 类型：失败突破策略。
- 依据，PDF p.128–130：看似强的breakout bar若被下一强反向bar迅速吞没，可能是到支撑/阻力的vacuum；必须始终保留双向解释。
- Setup：breakout bar虽大，但下一 `1–2bars` 形成outside reversal或强收盘回到旧range，且未先达到scalp目标。
- 入场：反向bar越过breakout bar另一端，或回测旧边界失败。
- 止损：失败极值外。
- 目标：旧range中点/对侧、突破bar起点、1R/2R。
- 若反向bar后无跟进并再次顺原突破方向，转breakout-pullback，禁止继续fade。
- “机构等待更好价格”的解释不进入模型，实际仅使用价格行为。

### RANGES-C03-S05：强趋势中的大尾部 Candle Trap

- 类型：顺势失败形态策略。
- 依据，PDF p.130–132：tight trend中尚无trend-line break时，大range、小body、长逆势尾部的蜡烛反转形态常诱捕逆势交易者；小bar无跟进后，其stop是顺势入场点。
- Setup：外层trend score≥0.70；无主要trend-line break；逆势bar range≥ `1.5ATR`、body/range≤0.35、尾部≥0.45。
- 不在其反转方向交易；等待下一小bar/doji未能跟进。
- 入场：candle反转交易者理论stop处顺趋势stop entry。
- 止损：trap bar逆趋势极值外。
- 目标：趋势旧极值、1R/2R。
- 若先有主要trend-line break及第二反转信号，则不适用，转S06。

### RANGES-C03-S06：Trend-Line Break 后的新极值失败

- 类型：条件式真正反转策略。
- 依据，PDF p.131–133：强趋势先横向两腿并突破trend line后，交易者才等待一两bar的新极值失败；早期逆势尝试不具备此条件。
- Setup：至少两腿sideways/countertrend move突破连接 `10–20bars` 的主要trend line。
- 等待：旧趋势尝试创新极值，持续 `1–2bars`，但收回旧swing内。
- 入场：失败bar反向极值外stop。
- 止损：最终新极值外。
- 目标：EMA、此前逆势signal bar极值、两腿、1R/2R。
- 若旧趋势新突破走远且未触发，取消订单，等待下一次trend-line break。

### RANGES-C03-S07：Barbwire 的边缘失败突破

- 类型：tight-range/final-flag策略。
- 依据，PDF p.130–132：三个以上重叠bars且至少一个doji构成barbwire；通常为延续，但range边缘可fade，强trend-bar breakout常失败回归。
- 检测：连续≥3bars，overlap≥0.70，至少1个body/range≤0.25，总高度≤ `1–1.5ATR`。
- 中部禁入；边缘limit scalp和突破后返回range的stop reversal分别测试。
- 在成熟趋势/连续climax后标记`POSSIBLE_FINAL_FLAG`，失败突破反转目标为EMA/10bars两腿。
- 顺外层趋势breakout有强follow-through时不fade，转S01。
- 止损：barbwire失败极值外；目标中点/对侧/1R。

### RANGES-C03-S08：强反向 Outside Bar 后重置计数

- 类型：状态重置组件。
- 依据，PDF p.132–133：强outside reversal把市场带入新趋势时，其极值成为新趋势起点，旧High/Low计数全部重置。
- 重置条件：outside bar body≥ `0.75ATR`，收盘在新方向端25%，突破近期结构并使Always-In翻转。
- 该bar low/high保存为`new_trend_origin`；下一次pullback为High/Low 1，而不是沿用旧趋势的Low/High 2。
- 旧breakout事件关闭，后续目标从新origin或新spike计算。
- 若outside bar没有follow-through、仍在旧range中，则不重置，只标为range波动。

### RANGES-C03-N01：新闻叙事不得覆盖 Breakout 强度

- 类型：`NEGATIVE`。
- 依据，PDF p.125–126、130：技术交易者只需评估breakout强弱；新闻解释会增加认知距离，最多只需知道发布时间。
- 入场特征不使用新闻情绪、标题或事后基本面解释。
- 事件bar必须收盘后才用OHLC；若交易发布瞬间，需独立tick模型、真实延迟与滑点。
- 强/弱结论完全由当时价格、成交和可选volume特征决定。

### RANGES-C03-N02：清晰但恐惧或模糊不是量化条件

- 类型：`NEGATIVE`。
- 依据，PDF p.124–125：大行情在实时中常“清晰但可怕”或“不清晰”，这种心理会导致等待、追价或漏单。
- 不使用“感觉紧迫/害怕/难以下单”作为直接特征；以未回撤、limit未成交、bar速度和结构风险代理。
- 只要S01/S02满足且仓位可按风险缩小，就执行预定义订单；若最小单位仍超风险则跳过。
- 不因图表事后显得容易而假设实时可以在最优价成交。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 124–126 | initial breakout、首pause三分支、风险与新闻 | 第1节、S01、S02、N01–N02 |
| 126–127 | 连续trend bars、urgency、spike/channel及测量移动 | S01–S03 |
| 127–130 | follow-through、强bar快速失败、多个测量目标 | S02–S04 |
| 130–133 | barbwire、candle traps、trend-line break及计数重置 | S05–S08 |

## 4. 回测验收

- 每日所有initial breakout attempts都入账，不能只保留最终1–3次成功突破。
- S01按1bar、2bar、3+bar确认比较概率、滑点和延迟。
- S02建立首pause后channel/range/opposite trend的互斥转移矩阵。
- S03所有高度及启用顺序在事件发生时冻结。
- S04用first-passage判断breakout先获scalp还是先失败。
- S05/S06用“是否已有主要trend-line break”严格分组，验证trap与真正反转的差异。
- S07报告barbwire边缘fade、顺势breakout与final flag上下文。
- S08检查每次状态重置后High/Low计数是否从1开始。
- Figure 3.1–3.3仅作章节例证，不作参数拟合或绩效证据。
