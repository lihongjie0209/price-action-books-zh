# 第 11 章：首次回调序列——Bar、次级趋势线、均线、均线缺口、主要趋势线

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/20-ch11-first-pullback-sequence-bar-minor-trend-line-moving-average-moving-average-gap-m.md`
- PDF 页码：247–255
- 图表：Figure 11.1–11.2；正文与图注已完整说明，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Weakening Ladder

每个趋势独立维护以下首次事件；顺序通常如此但不强制：

```text
BAR_DETERIORATION
FIRST_1_LEG / FIRST_2_LEG / FIRST_3_PUSH_PULLBACK
FIRST_MINOR_TREND_LINE_BREAK
FIRST_EMA_TOUCH
FIRST_CLOSE_ACROSS_EMA
FIRST_MA_GAP_BAR
FIRST_MAJOR_TREND_LINE_BREAK
LARGE_2_LEG_PULLBACK
TRADING_RANGE
```

- 每层可重复出现，`first_at[level]`只写一次；较浅层可在较深层之后再次出现。
- 方向标准化实现，bull/bear使用同一逻辑。
- 弱化特征还包括实体缩小、逆势尾部/重叠/逆向body增加、推进中pullback变多。
- Major trend-line break前，各类首次回调默认仍是旧趋势顺势候选；之后转入“旧极值测试后可能大修正/反转”的分支。

## 2. 规则卡

### RANGES-C11-S01：弱化阶梯实时状态

- 类型：趋势生命周期组件。
- 依据，PDF p.247–250：趋势逐渐失去动能、双向交易增加，pullback通常越来越大并最终成为range/反向趋势；具体层级不必严格按序。
- 滚动窗口 `5/10/20bars` 计算body缩小率、tail ratio、overlap、逆向bar比例和pullback深度/持续。
- 各first event仅使用已完成bar及当时trend lines/EMA确认。
- 输出`max_depth_level`和最近 `3–5` 个pullback的深度/持续斜率，但不因单项弱化自动翻转Always-In。
- 连续两层更深事件或3项bar-level弱化时，降低trend score `0.10–0.25`。
- Major break/range状态由S06/S07确认。

### RANGES-C11-S02：首次 Bar-Level Pullback / High-Low 1

- 类型：完整顺势策略。
- 依据，PDF p.247–251：强spike后首个1–2bar pullback几乎总被旧极值测试；可stop交易High/Low 1，高级交易者也可在prior bar外limit。
- Setup：趋势spike≥3–4bars，首次bar逆向极值越过prior bar，尚无minor trend-line break。
- 入场A：pullback bar顺势极值外1tick stop；入场B：prior bar不利极值外limit。
- 止损：pullback极值或spike起点外，按固定账户风险缩仓。
- 目标：旧趋势极值、spike等幅、1R/2R。
- 失效：pullback形成强反向spike并突破主要结构。
- Limit版本必须建模未成交和排队，不与stop结果混合。

### RANGES-C11-S03：首次 Minor Trend-Line Break / High-Low 2

- 类型：顺势二腿回调策略。
- 依据，PDF p.248–251、253–254：较后pullback常3–10bars、两小腿并突破minor line，仍通常形成High/Low 2并创新极值。
- Setup：首次突破连接最近 `3–10bars` 的minor trend line；countertrend move持续 `3–10bars`。
- 触发：第二腿结束的High/Low 2；极强趋势允许再次High/Low 1但标低置信度。
- 入场：signal bar外stop。
- 止损：完整pullback极值外。
- 目标：旧极值、1R/2R；新极值后更新结构trail。
- 若已有多次盈利入场后突然恢复浅High/Low 1，转N01 final-flag警戒，不盲目追价。

### RANGES-C11-S04：首次 EMA Touch / 20 Gap Bars

- 类型：完整顺势均线回测策略。
- 依据，PDF p.248–252、255：强趋势可离开EMA两小时以上；首次触EMA通常吸引顺势订单并测试旧极值。
- Setup：严格版连续 `20+bars` 极值未触EMA；宽松版以close未触/穿分别报告。
- 首次EMA触及时等待High/Low 1/2、double top/bottom flag或失败逆向breakout。
- 入场：signal bar外stop或EMA顺势侧limit。
- 止损：EMA pullback swing外。
- 目标：旧趋势极值、1R/2R。
- 若价格在EMA附近 `10–20bars` 仍不能恢复，降级为S07 range/更深pullback候选。

### RANGES-C11-S05：首次 Moving-Average Gap Bar

- 类型：最后趋势腿/转折候选策略。
- 依据，PDF p.248–251、253–255：bull中首次bar high<EMA（bear中low>EMA）通常仍测试趋势极值；常与major line break结合并成为最终腿前的setup。
- Gap bar确认后等待顺旧趋势High/Low 1/2；若第一次失败，允许第二entry。
- 入场：signal bar顺旧趋势极值外stop。
- 止损：MA-gap pullback最终极值外。
- 目标：旧极值；到达后不再自动期待新大腿，启用S06反转监控。
- Gap bar后通常先有第二countertrend leg再回到EMA；对立即V形恢复与两腿版本分别统计。
- 旧极值测试可overshoot、exact或undershoot，三类全部保留。

### RANGES-C11-S06：首次 Major Trend-Line Break 后的 Regime Shift

- 类型：状态转换与条件反转策略。
- 依据，PDF p.248–251、253–255：major line break后通常仍测试旧极值，但随后至少两腿countertrend move，甚至正式反转；此时不应继续机械交易旧趋势。
- Major line至少连接 `20+bars` 或两个prominent swings；突破需收盘越线 `0.10–0.50ATR` 或强反向spike。
- 第一break不立即反转；等待旧极值测试形成higher/lower/equal extreme。
- 入场：测试失败后的lower high/higher low、第二反转或Always-In flip。
- 止损：旧极值测试最终点外。
- 目标：EMA、major-break起点、两腿、1R/2R。
- 若旧趋势强势创新极值并重新建立tight channel，关闭反转候选并重置为新trend leg。

### RANGES-C11-S07：Pullback 扩大至 Trading Range

- 类型：趋势到区间转换组件。
- 依据，PDF p.248–250、252：更大两腿回调持续10bars以上、穿越prominent swing，随后双方bar接近均衡，趋势演化为range；range突破回归会扩大range。
- 候选条件：pullback>10bars、第二腿突破prominent higher/lower swing、bull/bear body压力比在 `0.67–1.5`、overlap≥0.60。
- 满足3/4确认`TRADING_RANGE_CANDIDATE`；两侧各测试/失败后确认range。
- 动作：停止S02/S03旧极值追价，目标缩至range中点/对侧，边缘双向。
- Range突破后返回range时扩大边界，但新边界只从返回确认bar后生效。
- 强breakout+follow-through则转新趋势，不保持range偏见。

### RANGES-C11-S08：递增 EMA 穿透的反转压力

- 类型：渐进弱化评分组件。
- 依据，PDF p.253–255：连续EMA测试越来越深，表示逆势方更积极、顺势方等待更好价格，旧方向entry风险上升。
- 对连续 `3–5` 次EMA pullback记录最大穿越ATR、close反侧bars和恢复时间。
- 若穿透深度单调增加或回归斜率>0，同时恢复旧极值耗时增加，提高`two_sided_score`。
- 只降低S04/S05仓位/评分，不单独逆势入场。
- 与S06 major break、第二信号共振时才启用反转。
- 缺失/不规则session中EMA warm-up不足时不计算。

### RANGES-C11-N01：连续获利后再次浅 Pullback 可能是陷阱

- 类型：`NEGATIVE`。
- 依据，PDF p.250：多个High/Low 1、High/Low 2已成功后突然出现renewed strength，可能是final flag；不应因近期盈利而无条件继续追。
- 第三次以上同类首次腿入场不再称“first”；必须结合推进计数、climax和channel位置。
- 第三推进/测量目标/主要line break后，禁止普通浅pullback追价，等待更大结构。
- 近期盈利亏损不改变仓位或规则。

### RANGES-C11-N02：Sideways Bars 后不在错误边缘追 Breakout

- 类型：`NEGATIVE`。
- 依据，PDF p.252：长期趋势后数根sideways bars已经是range；bull趋势不宜在range高点追买，bear趋势不宜在range低点追空。
- 连续≥5bars、overlap≥0.65、净位移≤0.5ATR时启用range门控。
- 只在range有利边缘做旧趋势setup，或等待强breakout pullback。
- 临时查看15/30/60分钟EMA不是必要条件；多周期模型必须预先固定且只用完成bar。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 247–250 | bull/bear弱化完整序列、顺序非严格、pullback扩大 | 第1节、S01–S03、S07 |
| 250–251 | 首bar、minor line、EMA、MA gap与major line逻辑 | S02–S06、N01 |
| 251–252 | EMA等待、各类first pullback及高周期干扰 | S04–S06、N02 |
| 252–255 | sideways门控、pullback递增、major break后反转 | S06–S08、N02 |

## 4. 回测验收

- 每层first event与重复事件分别编号，不能把后续同类回调伪称首次。
- 弱化顺序不强制；报告实际事件排列和常见跳层。
- S02–S05分别统计旧极值exact/undershoot/overshoot及到达时间。
- Minor/major trend lines只使用当时确认anchors，禁止未来重画。
- S04严格/宽松20-gap定义分开；EMA warm-up固定。
- S06建立major break后旧极值测试→两腿/range/reversal的转移矩阵。
- S07必须实时确认range，最终整段sideways不能回填早期状态。
- S08使用连续pullback配对，不把不同趋势的EMA测试混合。
- Figure 11.1–11.2仅作章节例证，不作参数拟合或绩效证据。
