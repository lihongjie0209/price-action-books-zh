# 第 18 章：Patterns Related to Yesterday—Breakouts, Breakout Pullbacks, and Failed Breakouts

## 元数据

- 英文来源：`books/trading-price-action-reversals/en/chapters/27-ch18-patterns-related-to-yesterday-breakouts-breakout-pullbacks-and-failed-breakouts.md`
- PDF 页码：359–370
- 图表：Figure 18.1–18.6；正文逐bar说明已完整覆盖规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 昨日结构与开盘状态机

```text
yday_context ∈ {TREND, RANGE, BULL_CHANNEL, BEAR_CHANNEL, OTHER_PATTERN}
open_state ∈ {BREAKOUT, FAILED_BREAKOUT, BREAKOUT_PULLBACK, UNCERTAIN}
reference_levels = yesterday_high/low/close + frozen swings + channel/range boundaries
```

- 所有昨日形态与边界必须在当日开盘前冻结；当日价格只能触发、确认或使其失效，不能回头重画昨日结构。
- 核心状态链为：突破昨日结构→观察跟进→若反转则为失败突破→若反转本身失败，则恢复原突破并形成breakout pullback。

## 2. 规则卡

### REVERSALS-C18-S01：Prior-Day Context Snapshot

- 类型：盘前特征冻结。
- 依据，PDF p.359、369–370：首小时常受昨日末`1–2h`趋势、区间、通道、旗形和摆动高低影响。
- 在RTH open前保存昨日末段AI方向、EMA斜率、range、channel、最近pivots及昨日OHLC。
- 比较`60、90、120min`回看窗；形态分类低置信时保留OTHER而非强行归类。

### REVERSALS-C18-S02：Opening Breakout Detector

- 类型：开盘母事件。
- 依据，PDF p.359–360：多数开盘存在某种突破，包括收盘到开盘gap、昨日channel/flag/range或swing high/low的突破。
- 首`1–3 bars`若open/close越过任一冻结边界≥`0.05–0.20 ATR`，登记breakout方向与层级。
- 多重边界同时突破时共享一个母事件，避免重复下单。

### REVERSALS-C18-S03：EMA Gap Proxy

- 类型：结构缺失代理。
- 依据，PDF p.359：无法辨认突破对象时，首bar完全在EMA上方视为gap up，完全在下方视为gap down。
- 仅当S01无可信结构时启用；`low(first)>EMA`为up、`high(first)<EMA`为down。
- 这是PROXY版本，必须与真实昨日边界版本分开评估，且受第17章盘初EMA冲突门控。

### REVERSALS-C18-S04：Trend-From-Open Follow-Through

- 类型：突破延续。
- 依据，PDF p.359、367–369：大gap后首bar强同向、随后跟进，可形成trend from open；首`5–10 bars`小range突破也常引出trend day。
- 首bar同向趋势棒且后`1–3 bars`不收回/继续同向收盘时，在突破或首pullback顺势入场。
- Stop在开盘spike/小range另一侧；目标`1R、2R`及昨日形态高度measured move。

### REVERSALS-C18-S05：Opening Failed Breakout

- 类型：开盘反转。
- 依据，PDF p.359–362、364–365：无论首bar多强都可能失败；强相反bar或两棒反转收回昨日边界可形成当日极值。
- 突破后`1–5 bars`内收回边界并出现强反向trend/two-bar reversal时，向range内部反向入场。
- 昨日高/低外的失败、第二次失败或major-trend-reversal背景提高分数；保留runner测试当日另一极值。

### REVERSALS-C18-S06：Failed-Failure Breakout Pullback

- 类型：原方向恢复。
- 依据，PDF p.359–361：失败突破若只反向`1–2 bars`便出现原方向强棒，反转本身失败，演化为breakout pullback。
- S05触发后，若反向move无跟进且原方向trend bar重新越过signal extreme/边界，退出反向仓并按原突破方向入场。
- 两腿逐笔计成本；原方向目标为opening extreme、`1–2R`或measured move。

### REVERSALS-C18-S07：Channel-as-Opposite-Flag

- 类型：昨日通道突破。
- 依据，PDF p.360–361、367–369：昨日bull channel是潜在bear flag，bear channel是潜在bull flag；开盘突破常接breakout pullback。
- 冻结通道边界；bull channel下破只找short，bear channel上破只找long，除非S05确认失败。
- Entry采用首次`1–2 legs`回测通道/EMA后的顺势signal；紧密反向channel中不提前抄底/摸顶。

### REVERSALS-C18-S08：Yesterday Extreme Opening Reversal

- 类型：关键极值反转。
- 依据，PDF p.360–366、370：开盘突破昨日高/低后反转，常形成数小时乃至当日高低。
- 越过昨日极值≤`0.05–0.30 ATR`后收回，并有two-bar reversal、wedge/double或channel overshoot之一时入场。
- 首目标opening range另一端/1R；swing目标当日另一swing或measured move，breakeven stop版本并行测试。

### REVERSALS-C18-S09：First-Hour Double Attempt Failure

- 类型：双顶/双底反转。
- 依据，PDF p.364–365：首小时两次尝试突破昨日高/低均失败，常转向相反方向并成为未来数小时极值。
- 两次测试间隔`2–20 bars`、价格容差`0.08–0.25 ATR`；第二次收回并有反向signal时入场。
- 当日range仍小于近期ADR的`40%–70%`时，将range expansion/measured move作为目标候选。

### REVERSALS-C18-S10：Two-Leg Expectation After Strong Reversal

- 类型：持仓与再入场。
- 依据，PDF p.361–363、365–367：强spike、wedge/expanding-triangle second entry或强反转通常带来至少两腿、约10bars修正。
- 强度达标后，在第一腿结束不逆向追单；等待pullback后第二腿entry，持仓窗口测试`8–20 bars`。
- 新的更强反向spike可取消预期；“两腿/10bars”仅作可证伪作者假设。

### REVERSALS-C18-S11：Yesterday-Level Breakout Pullback

- 类型：延续回测。
- 依据，PDF p.361、363、365、367–370：突破昨日高低、昨日close或冻结trend line后，H/L2、HL/LH或EMA test可提供回调入场。
- 突破有跟进后，等待`1–2 legs`回测边界容差`0.05–0.25 ATR`且不有效收回。
- Signal可为同向bar、H/L2、failed countertrend setup；stop放在pullback结构外。

### REVERSALS-C18-S12：Tight-Range Breakout-Failure Bias

- 类型：barbwire过滤器。
- 依据，PDF p.364–366：多根大幅重叠、反复反转的tight range代表强双向交易，边界突破常被拉回。
- Barbwire成立时关闭中部entry；首次边界突破默认只观察/做失败版本，除非强trend bar+跟进改变状态。
- 顺趋势且明确需要第二腿时，可交易边缘L2 breakout pullback，不机械fade所有突破。

### REVERSALS-C18-S13：Cumulative Pressure Score

- 类型：多spike证据累积。
- 依据，PDF p.366–367：不同交易者会选择不同bear spike起点，但每根强趋势棒都代表累计压力，达到临界量后市场才推进。
- 在滚动`10–30 bars`累计同向body、close-at-extreme、结构突破和跟进，随时间衰减。
- 分数越过阈值用于确认AI/放宽顺势entry，不要求唯一主观spike anchor。

### REVERSALS-C18-S14：Exact Test and Close-Reversal

- 类型：昨日close/精确价位测试。
- 依据，PDF p.367–370：开盘可精确测试昨日low/close或昨日趋势线突破位后快速反转。
- 距冻结level≤`1 tick–0.10 ATR`且当bar/次bar收回时登记test；需反向signal才入场。
- 将exact touch、near miss和overshoot分层，禁止事后调整level使其看似精确。

### REVERSALS-C18-N01：昨日趋势不能直接决定今日方向

- 类型：`NEGATIVE`偏见约束。
- 依据，PDF p.361–362：昨日收盘虽可能延续，但今日gap可使昨日突破本身失败；强首bar也可能下一bar反转。
- S01仅提供prior，不得绕过S04–S06的当日确认。

### REVERSALS-C18-N02：紧密反向通道中禁止提前逆势

- 类型：`NEGATIVE`入场约束。
- 依据，PDF p.367：陡峭tight bear channel即使出现三推也不宜立即买，应等突破后pullback；bull版本镜像。
- 未先有效破channel时，countertrend stop entry数量必须为零。

### REVERSALS-C18-N03：弱逆势 Scalp 不得分散主趋势交易

- 类型：`NEGATIVE`方向约束。
- 依据，PDF p.363、365–366：AI明确且第二腿未完成时，小反向setup通常只够scalp，应优先等待顺势再入。
- 主策略关闭逆AI交易；反事实版本独立报告且目标不得冒充swing。

### REVERSALS-C18-N04：图例的当日极值与 Measured Move 不是保证

- 类型：`NEGATIVE`研究约束。
- 依据，PDF p.360–370：章节案例多次形成当日极值、两腿和measured move，但均为情境判断。
- 目标只作候选；必须报告未到达、先止损及超时比例，不能用图例结果标注训练标签。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 359 | 盘前冻结昨日形态、开盘突破、EMA代理、突破/失败/再失败状态链 | S01–S06、N01 |
| 360 | 状态链完成、昨日bull channel为bear flag、昨日低点失败突破 | S05–S08 |
| 361 | 失败突破后第二腿、breakout pullback、昨日趋势可被gap推翻 | S06–S11、N01 |
| 362 | 强首bar失败、wedge修正至少两腿/10bars、昨日低点测试 | S05、S08、S10 |
| 363 | failed L2、HL MTR、强趋势pullback及两边交易 | S10–S11、N03 |
| 364 | 首小时双顶底、连续失败突破、barbwire | S05、S09、S12 |
| 365 | 两次昨日高点失败、range expansion、AI翻空与低点磁体 | S09–S13 |
| 366 | 顺势L2、趋势线破坏后强低点反转、累计卖压 | S10–S13、N03 |
| 367 | 昨日channel开盘突破、tight channel不提前反转、昨日低点精确测试 | S07、S11、S14、N02 |
| 368 | double-top bear flag与多种breakout-pullback short | S07、S11 |
| 369 | bear channel为bull flag、首5–10bars range突破、两腿pullback | S04、S07、S10–S11 |
| 370 | 昨日close/趋势线/昨日低点测试与H2 breakout pullback | S11、S14 |

## 4. 回测验收

- 昨日形态、trend line、pivots与reference levels全部在RTH open前冻结并保存版本；禁止使用当日数据回画。
- 为每个opening母事件输出BREAKOUT→FAILED_BREAKOUT→BREAKOUT_PULLBACK完整状态轨迹和触发证据。
- 分别报告昨日高低、close、channel、range和EMA-proxy样本；多重结构事件去重但保留标签。
- 按gap大小/方向、昨日context、首bar强度、首小时/其后及当日range占ADR比例分层。
- 验证两次失败、两腿/10bars、当日极值和measured move到达率，全部附置信区间且不使用作者案例作先验成功标签。
- 反手交易逐腿模拟stop触发、gap、同bar路径、费用和滑点；比较只退出与直接反手版本。
- Tight-channel、barbwire、逆AI及昨日趋势非决定性约束设自动测试。
- Figure 18.1–18.6只作章节案例和规则来源，不作参数最优性或绩效证据。
