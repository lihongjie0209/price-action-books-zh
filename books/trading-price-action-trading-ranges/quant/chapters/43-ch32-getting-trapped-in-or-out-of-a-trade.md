# 第 32 章：Getting Trapped In or Out of a Trade

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/43-ch32-getting-trapped-in-or-out-of-a-trade.md`
- PDF 页码：618–620
- 图表：Figure 32.1；正文与图注已完整说明规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Trap 事件定义

```text
entry_trap = setup触发后在N bars内越过signal另一端或触发相反breakout
exit_trap  = protective stop成交后在N bars内恢复原方向并达到原scalp目标
trap_window = 1–5 bars（按setup预注册）
```

- “被困”是价格路径的事后标签；实盘决策只能使用触发前的regime、location、signal quality和已完成breakout。
- 机构动机不可观察，不作为特征；只量化公开OHLC、成交、结构与订单执行。

## 2. 规则卡

### RANGES-C32-S01：Weak Stop-Entry Trap Classifier

- 类型：失败setup分类器。
- 依据，PDF p.618–620：entry stop会把交易者带入坏交易；在错误方向背景、弱signal或range中部的H/L1–2更易失败。
- 输入：Always-In方向、spike/channel强度、range位置、signal body/tails、setup序号、前方结构空间。
- Weak candidate至少满足2项：逆强趋势、signal doji/大tail、range中部、第三推、连续climax后的旧方向setup、陡channel的首次反转。
- 分类器只生成`failure_probability`，达到训练期阈值`0.60–0.70`才交反向策略。

### RANGES-C32-S02：Failed Signal Extreme Limit Fade

- 类型：反向limit策略。
- 依据，PDF p.619–620：若H/L1–2或首反转大概率失败，可在其signal high/low挂相反方向limit，期待被困者退出推动scalp。
- Weak long setup：sell limit=`signal.high ± 0–1tick`；weak short setup：buy limit=`signal.low ± 0–1tick`。
- Stop在signal/局部结构外`0.10–0.30ATR`；目标range midpoint、prior extreme或成本后`0.5–1.0R` scalp。
- Strong breakout穿过limit并follow-through则立即退出，不继续逆行加仓。

### RANGES-C32-S03：Strong Spike First-Reversal Failure

- 类型：趋势延续fade。
- 依据，PDF p.619–620：强bear move后的首次bull attempt通常失败并再创新低；强bull镜像，陡channel的首H2也宜等待breakout pullback。
- Spike需连续≥2–3同向bars、累计≥`1.5ATR`、body占比≥60%、overlap低。
- 在首个反向signal extreme按S02顺原spike方向入场，或等待其stop-entry失败后确认。
- 目标旧极值/second leg；若出现强reversal+follow-through则取消。

### RANGES-C32-S04：Consecutive Climax Failed Continuation

- 类型：climax后逆旧趋势scalp。
- 依据，PDF p.620：连续sell climaxes后预计至少约10bars correction，随后weak L1/L2 shorts易失败；buy climax镜像。
- Climax：至少2次large trend bar/加速推进，第二次位于第三推或final flag之后。
- 在后续weak continuation signal extreme逆旧趋势limit；目标EMA、range midpoint或1R。
- Correction horizon测试`5–15bars`，不把10bars当确定值；新强旧趋势breakout使规则失效。

### RANGES-C32-S05：Trapped-Entry Breakout Follow

- 类型：确认后顺失败方向交易。
- 依据，PDF p.619–620：弱short触发后迅速outside-up会困住bears并迫使未入场bulls追价；gap强bull背景下失败short同理。
- 先观察原setup触发，再要求`1–2bars`内强穿signal另一端，breakout body≥60%且close near extreme。
- 在breakout stop/首次pullback顺失败方向入场；stop在trap extreme外。
- 目标measured move、旧极值或1–2R；若breakout发生在range对侧则降为scalp。

### RANGES-C32-S06：Mature Three-Push / Range-Middle Fade

- 类型：成熟推进失败策略。
- 依据，PDF p.620：第三推、small bars/tails、横盘后的failed L2/H1，以及range中部的大doji setup容易失败。
- Candidate：push_count≥3，或最近`5–10bars` overlap高且signal在range中间40–60%。
- 在弱方向signal extreme反向limit；target中点/近侧edge，stop在局部swing外。
- 若强spike已建立新Always-In方向则禁用，转S03/S05。

### RANGES-C32-S07：Protective-Stop Exit-Trap Reentry

- 类型：被止损后的条件重入方案。
- 依据，PDF p.618：保护stop可能把交易者赶出好交易；小幅stop run常与更大模型、hedging或scale行为无关。
- 原stop hit后不立即报复性重入；等待价格在`1–3bars`内恢复结构并出现原方向strong signal/failed breakout。
- 重入作为新交易，重新计算stop、qty、target与EV；episode累计风险不得超过预设上限。
- 与更宽初始stop基线比较成本、漏单和尾部风险。

### RANGES-C32-S08：Trap Location Context Gate

- 类型：所有trap策略的共用门控。
- 依据，PDF p.619–620：同一H/L1–2在gap/open trend、强spike、climax correction、channel或range中部的结论不同。
- 每个candidate必须预先归入`strong_trend, weak_spike, mature_channel, climax_correction, trading_range`之一。
- S02–S07只有在对应regime和location映射成立时允许下单；无法分类则跳过。
- 报告各状态混淆矩阵，防止用trap标签替代真实市场状态判断。

### RANGES-C32-N01：禁止推断机构“被困”或个人 Stop Hunting

- 类型：`NEGATIVE`特征约束。
- 依据，PDF p.618：机构模型、客户订单、hedging、获利与scale原因众多且不可知，多数与5分钟chart或个人订单无关。
- 特征集中不得出现“机构犯错”“知道我的stop”等不可观察变量。
- 只能用订单簿可见量、公开价格路径及预先定义的结构代理。

### RANGES-C32-N02：Strong Context 中不做首次逆势 Stop Entry

- 类型：`NEGATIVE`硬否决。
- 依据，PDF p.619–620：强gap bull bar、陡bear channel或强down move后的首个反转signal胜率不足。
- S03条件成立时，逆spike的first-entry交易数必须为零；等待second entry或breakout pullback。
- 不能因stop距离小把低概率trade误判为好方程。

### RANGES-C32-N03：Range 中部 Weak Signal 不追 Stop

- 类型：`NEGATIVE`。
- 依据，PDF p.620：range中部的H1/H2、large doji和small-tail spike提供差位置，容易被反向limit交易者fade。
- Location位于range中间40–60%且signal score低时，禁止方向stop entry。
- 可运行S02/S06的反向shadow/实盘版本，但仍需成本后EV与空间门槛。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 618 | entry/protective stop陷阱、机构动机不可知、HFT关注小波动 | S01、S07、N01 |
| 619 | gap强势失败short、第三bar spike、陡channel首反转、强move首rally失败 | S02–S03、S05、S08、N02 |
| 620 | 连续climax、failed L1/L2、outside trap、弱spike、第三推与range中部 | S01–S06、S08、N02–N03 |

## 4. 回测验收

- Trap标签仅在评估阶段用未来`1–5bars`生成，不得进入下单时特征。
- 所有signal、regime、range边界和push count带`valid_from`；未来重画次数必须为零。
- S02–S07共享原setup/trap event ID，同一失败move不能重复计盈。
- Limit fill采用穿越1tick保守模型；stop-entry、limit-fade与confirmation版本在同一母样本比较。
- 报告原setup失败率、反向策略fill率、净EV、MAE/MFE、slippage及stop后重入的episode累计风险。
- Strong trend首次逆势和range中部弱stop-entry必须通过零交易硬测试。
- Regime阈值、trap window与range-middle范围做walk-forward及跨品种敏感性测试。
- Figure 32.1仅作章节例证，不作参数拟合或绩效证据。
