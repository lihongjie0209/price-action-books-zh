# 第 20 章：Gap Openings—Reversals and Continuations

## 元数据

- 英文来源：`books/trading-price-action-reversals/en/chapters/29-ch20-gap-openings-reversals-and-continuations.md`
- PDF 页码：389–393
- 图表：Figure 20.1–20.2；正文与图注已完整说明规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Gap 定义与状态

```text
gap = RTH_open - previous_RTH_close
gap_norm = abs(gap) / recent_ADR
large_gap = gap_norm >= threshold OR abs(gap) is largest of prior N sessions
gap_response ∈ {ACCEPT_WITH_GAP, REJECT_GAP, RANGE_UNCLEAR}
```

- Gap是跨session突破，可视为一根不可见的大trend bar；日线是否也形成gap不改变本章的5分钟开盘逻辑。
- 大gap提高“任一方向trend day”的先验，不保证顺gap，也不排除全天区间。

## 2. 规则卡

### REVERSALS-C20-S01：Large-Gap Classifier

- 类型：事件分类。
- 依据，PDF p.389：候选定义为约大于近期ADR一半，或过去约5天最大gap。
- 基准搜索`gap_norm ∈ {0.35,0.50,0.65,0.80}`、回看`N ∈ {3,5,10}`，任一条件满足标记large。
- ADR与排名只能使用开盘前数据；按品种和波动regime独立校准。

### REVERSALS-C20-S02：Gap-as-Invisible-Spike

- 类型：统一结构表示。
- 依据，PDF p.389–391：gap可当作突破和一根巨大不可见trend bar；小pullback后channel即gap spike-and-channel。
- 在状态机中插入`synthetic_spike`，range=`abs(gap)`、方向=gap方向，但不伪造成可交易OHLC bar。
- 其高度可作为channel context/measured-move候选，不得假设gap内可成交。

### REVERSALS-C20-S03：Opening Acceptance Detector

- 类型：顺gap延续。
- 依据，PDF p.389–393：gap越大越可能顺gaptrend；首数bars的方向、数量与强度揭示市场是否接受新价格。
- 前`2–10 bars`若多数同gap趋势棒、低重叠、收盘远离昨收且无强反转，标记ACCEPT_WITH_GAP。
- 在首pullback/EMA test顺gap入场；stop在opening structure外，目标ADR completion、`1–2R`或gap/spike投射。

### REVERSALS-C20-S04：Gap Rejection Reversal

- 类型：逆gap趋势。
- 依据，PDF p.389、392–393：市场可拒绝极端开盘并形成相反全天趋势；首bar方向可能与gap相反。
- 首`1–10 bars`出现强逆gapspike并收回opening breakout/关键结构时标记REJECT_GAP。
- 逆gapbreakout pullback入场，目标opening另一端、昨收方向或`2R`；若只到gap内部不自动视为gap fill必达。

### REVERSALS-C20-S05：Two-Leg Countertrend Setup

- 类型：延迟趋势启动。
- 依据，PDF p.389–390：大gap趋势常延迟约一小时，并从两腿回EMA、double top/bottom或wedge flag后开始。
- Large gap后允许前`6–18`根5分钟bars形成`2–3`腿逆gapmove；在EMA/结构位出现顺gapsecond-entry时入场。
- 若逆gapmove升级为S04强spike则取消顺gap计划。

### REVERSALS-C20-S06：Early Range Fallback

- 类型：不确定性门控。
- 依据，PDF p.390、392–393：多数大gap日前`5–10 bars`有range争夺，部分全天横盘；不明时应低买高卖。
- 若前`5–10 bars`重叠/长尾/双向趋势棒且S03/S04均未确认，标记RANGE_UNCLEAR。
- 关闭中部趋势追单，只在range外三分之一fade/失败突破；强breakout+跟进后切换趋势状态。

### REVERSALS-C20-S07：Aggressive Swing Allocation

- 类型：大gap仓位管理。
- 依据，PDF p.389–390：大gap日应让每个合格交易保留swing，单个好swing可抵多次scalp；趋势确认后在pullback加仓。
- 每笔合格setup保留`25%–50%`runner；其余在`1R–2R`分批兑现。
- 只有S03/S04确认且总风险不增加时在顺势pullback加仓；多次swing止损成本单独报告。

### REVERSALS-C20-S08：Trend Pullback Reentry

- 类型：趋势日重复入场。
- 依据，PDF p.390、393：趋势强时持续寻找同向entries，EMA tests在breakout后可成为再入场。
- AI方向明确、pullback未破最近结构且出现H/L1–2或同向trend bar时入场。
- 新腿多数可scalp，至少一腿继续swing；若AI丧失则停止累加。

### REVERSALS-C20-S09：Opening Doji Two-Sided Warning

- 类型：早期区间特征。
- 依据，PDF p.392–393：大gap后的opening doji表明two-sided trading，可能横盘数小时直到真正spike突破。
- 首bar body_frac低/双尾明显时提高RANGE_UNCLEAR分数；不得由gap方向直接确认AI。
- 等待连续强棒或range breakout follow-through，再按S03/S04入场。

### REVERSALS-C20-S10：Gap-Risk Structural Stop Study

- 类型：风险边界研究。
- 依据，PDF p.393：顺gap交易可参考gap中点/结构作为失效位，而非必然承受完整gap回补。
- 比较stop在opening range极值、gap midpoint、gap close三种版本；仓位按最远实际stop缩放。
- Gap midpoint仅是EMPIRICAL候选，必须验证其失效意义和隔夜跳跃尾部风险。

### REVERSALS-C20-N01：Gap 方向不是趋势方向保证

- 类型：`NEGATIVE`方向约束。
- 依据，PDF p.389–393：gap up/down均可产生bull、bear或range day。
- 未通过S03/S04时不得只按gap sign入场或标记最终日型。

### REVERSALS-C20-N02：禁止在不明开盘中坚持趋势信念

- 类型：`NEGATIVE`状态约束。
- 依据，PDF p.390：大gap不保证trend；price action不清晰应按range处理，错误时退出而非希望行情回来。
- RANGE_UNCLEAR期间趋势追单为零；结构失效立即平仓，不扩大stop等待低概率恢复。

### REVERSALS-C20-N03：作者 Gap 概率不得硬编码

- 类型：`NEGATIVE`研究约束。
- 依据，PDF p.389、393：`50/20/30/60%`等仅为指南，定义变化使精确计算不可靠。
- 只将其注册为待检验假设；实际条件概率用walk-forward和置信区间估计。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 389 | gap为突破、大gap定义、任一方向trend先验、首bars决定接受/拒绝、两腿延迟启动 | S01–S05、N01、N03 |
| 390 | gap为不可见spike、普通开盘三路径、积极swing/加仓、前5–10bars range与不确定性 | S02、S05–S08、N02 |
| 391 | 期货gap在现金指数表现为大trend bar | S02 |
| 392 | 大gap可走任一趋势或数小时横盘 | S03–S06、N01 |
| 393 | 四种gap/趋势组合、opening doji、EMA再入场及结构风险收益示例 | S03–S04、S08–S10、N03 |

## 4. 回测验收

- Gap、ADR、近N日排名与昨收全部用开盘前point-in-time数据；synthetic spike不得产生虚假成交。
- 以同一large-gap母样本报告ACCEPT、REJECT、RANGE三状态的实时首次确认时间和最终转移矩阵。
- 按gap方向/大小、首bar类型、前5/10bars结构、波动regime及品种分层报告trend/range日比例。
- 比较立即入场、两腿等待、opening-range breakout及EMA reentry版本的EV、MAE/MFE和机会损失。
- Swing runner、多次pullback加仓及三种stop逐腿模拟，保持相同账户风险并计入gap/slippage尾部。
- 验证作者方向概率、约半ADR/近5日最大gap和趋势延迟假设，均附样本量及置信区间。
- Gap方向非保证、UNCLEAR区间回退和作者概率非硬编码设自动测试。
- Figure 20.1–20.2只作结构解释与案例，不作条件概率或盈利证据。
