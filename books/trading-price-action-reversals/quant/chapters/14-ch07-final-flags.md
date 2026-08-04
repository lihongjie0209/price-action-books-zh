# 第 7 章：Final Flags

## 元数据

- 英文来源：`books/trading-price-action-reversals/en/chapters/14-ch07-final-flags.md`
- PDF 页码：207–230
- 图表：Figure 7.1–7.11；正文与图注已完整说明规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Final-Flag Episode

```text
MATURE_TREND -> FLAG_CANDIDATE
 -> WITH_TREND_BREAK_FAILED -> REVERSAL
 -> DIRECT_COUNTER_BREAK    -> REVERSAL
 -> REVERSAL_FAILED         -> TREND_RESUMPTION
 -> SMALL_FLAG_EVOLVES      -> LARGER_FLAG
```

- Final flag只能实时标记为candidate；只有随后较大修正/反转后才成为结果标签。
- Flag可为1–2bars、micro pattern、5–10bar horizontal range、triangle/wedge或增长中的channel。
- 反转通常先按two-leg correction交易，不预设一定形成相反趋势。

## 2. 规则卡

### REVERSALS-C07-S01：Mature-Trend Final-Flag Score

- 类型：候选评分。
- 依据，PDF p.207–210：趋势持续几十bars后，获利盘与逆势方增强，horizontal/two-sided flag更可能成为最后一个flag。
- Trend age候选=`20–100bars`；flag overlap≥50%、方向相反bodies/tails/reversals增加、EMA推进衰减。
- 评分组：maturity、climax、two-sidedness、major level、prior countertrend strength，各组封顶。
- Candidate不直接下单，需S03/S04/S05路径之一触发。

### REVERSALS-C07-S02：Horizontal-Flag Magnet Detector

- 类型：range形态组件。
- 依据，PDF p.207–210、216–218：多数final flag横向且至少5–10bars，双方认同价值使中点具有磁力，breakout多被拉回。
- Flag：`5–20bars`、net displacement/range path≤0.35、median overlap≥50%，双向bars均≥20%。
- 保存upper/lower/midpoint与valid_from；break后回range目标优先midpoint/对侧。
- Tight range成交需保守limit/stop模型及成本门槛。

### REVERSALS-C07-S03：With-Trend Breakout Failure Reversal

- 类型：经典final-flag反转。
- 依据，PDF p.208–213、215–221：成熟趋势顺势break只吸引scalpers，1–数bars后从HH/DT/LH（底部镜像）强收回flag。
- Break extension=`0–0.50ATR`，在`1–5bars`内close返回range并出现opposite signal。
- Entry在reversal bar触发；stop在breakout extreme外；Target1=flag midpoint/对侧，Target2=two legs/measured move。
- Flag内已有强反向leg/trend-line break则提高swing fraction。

### REVERSALS-C07-S04：Direct Countertrend Breakout

- 类型：无顺势break的反转路径。
- 依据，PDF p.208、212–213、221–225、228–229：final flag可不先顺势突破，直接以强反向bar/channel增长完成Always-In flip。
- Counter breakout close须越flag边界≥`0.10–0.30ATR`、body≥60%，最好有`1–2bars` follow-through。
- Entry在strong close/first pullback；stop在flag/entry bar另一侧。
- Target=flag height measured move、opening range target或结构support/resistance。

### REVERSALS-C07-S05：One/Two-Bar Post-Climax Final Flag

- 类型：微型climax反转。
- 依据，PDF p.208、210–212、221–227、229–230：连续大trend bars后一个pause/doji/tail/opposite-body可成为1–2bar final flag，随后最后一次顺势spike失败。
- Context：spike≥`3–5bars`、末端range/body异常，或consecutive climax≥2。
- Flag span=`1–2bars`；等待最后顺势break失败、ii/second signal或strong opposite breakout。
- 目标较长修正`5–20bars / 1–3legs`；强旧momentum使极值在`10–20bars`内仍可能复测。

### REVERSALS-C07-S06：Micro Trend-Line Breakout-Pullback Flag

- 类型：micro final flag。
- 依据，PDF p.207、211–214、217–219：微趋势线break后1–2bar恢复旧趋势若迅速失败，原小break/pause成为micro final flag。
- 使用`3–10bars`micro line；counter break后old-trend pullback只延续`1–2bars`且形成LL/DB/HL（top镜像）。
- Entry在second reversal；目标scalp/EMA/更大flag边界。
- Strong trend中只作minor correction，不能自动升级major reversal。

### REVERSALS-C07-S07：Final-Flag Evolution to Larger Pattern

- 类型：形态扩张状态。
- 依据，PDF p.207–208、219–223、226–228：小final flag常先给scalp反转，再增长为triangle/wedge/channel和新signal。
- 首反转MFE达到scalp但未破结构、随后重回flag时，不删除原事件，建立parent-child pattern。
- Larger flag重新计算边界/score并等待独立breakout；最多`2–4`层，之后转large range。
- 每层交易分别计成本但共享episode，防止同一move多计。

### REVERSALS-C07-S08：Failed Final Flag Trend Resumption

- 类型：反转失败顺旧趋势策略。
- 依据，PDF p.207、215、218–220、229：final-flag reversal触发后几bars内失败，反向bar成为原breakout的pullback，旧趋势恢复。
- Reversal MFE<`0.5–1R`且`1–3bars`内strong old-trend close穿回entry/flag extreme。
- 在failed reversal/first pullback顺旧趋势入场；target旧极值和flag height measured move。
- 若只走1–2bars再反转，生成S09 second-entry而非继续持有。

### REVERSALS-C07-S09：Second-Entry after Failed Resumption

- 类型：最终旗形第二次反转。
- 依据，PDF p.215、217–218：首次reversal失败并短暂恢复旧趋势后若再次转向，原candidate得到second-entry，成功时可形成更大修正。
- S08 breakout缺follow-through，在`1–5bars`内重新收回并形成合格opposite signal。
- Entry顺reversal方向，stop在new extreme外；目标S03同款。
- 与S08路径共享episode且风险累计受上限约束。

### REVERSALS-C07-S10：Failed H/L1–2 Limit Fade after Reversal

- 类型：新方向pullback limit策略。
- 依据，PDF p.212–215、217–223：wedge/climax反转后旧方向L1/L2或H1/H2多成为final flag并失败，可在signal extreme反向limit。
- 先确认reversal pattern/Always-In flip；旧方向signal弱、无强follow-through。
- Bull新方向在L1/L2 signal low及下`0–3ticks / 0.10ATR`买；bear镜像。
- Stop在新趋势结构外；目标旧swing、1R/2R；旧趋势spike阶段禁用。

### REVERSALS-C07-S11：Final-Flag Breakout Strength Transition

- 类型：Always-In确认。
- 依据，PDF p.222–224、228–229：反向break必须以strong trend bar越flag数ticks并有连续方向bars，才使旧方放弃并确认新趋势。
- Score：body≥60–70%、close末端20%、越界≥`0.15ATR`、next2 bars至少1根follow-through。
- 达标后停止range fades，运行新趋势pullback/runner；不达标仍为range/failure candidate。
- 保存flip确认bar，禁止回填到flag形成期。

### REVERSALS-C07-S12：First-Leg / Second-Leg Exit Plan

- 类型：反转持仓管理。
- 依据，PDF p.208–212、215–218：final flag通常至少产生两腿修正；强第一腿后可获利/保本并保留second-leg仓。
- Target1=flag midpoint/opposite edge/EMA，平`25–50%`；余仓等待pullback+second leg。
- Tight two-leg channel可整体视为第一大腿，runner stop置于确认swing外。
- 若原趋势强势恢复则S08退出/反手，不强求第二腿。

### REVERSALS-C07-S13：Strong Reversal Multi-Bar Displacement

- 类型：windfall swing加分。
- 依据，PDF p.215–216：entry bar close穿越此前6 highs/7 closes等多结构，困住大量旧趋势仓，使市场one-sided并支持更长swing。
- 计算first reversal bar/leg的`close_reversal_count`与`extreme_reversal_count`，回看`5–20bars`。
- Close跨越数权重大于wick；达到训练阈值时保留`50–100%`至S12第二腿。
- 数字仅作案例，必须样本外选择。

### REVERSALS-C07-S14：Opening Small-Flag Reversal

- 类型：开盘climax策略。
- 依据，PDF p.220–227：开盘连续climax后1–2bar flag、ii或second attempt可引发当日大反转，即使flag极小。
- Session前`30–90min`，gap/previous-day extreme或trend-line break背景，consecutive climax≥2。
- Entry在ii/opposite breakout/second signal；stop可为climax bar height但固定账户risk缩仓。
- 目标EMA、climax high/low、measured move与two legs；分时段独立验证。

### REVERSALS-C07-S15：Two-Attempt Failure Opposite Trend

- 类型：重复失败状态。
- 依据，PDF p.220–222：市场两次尝试突破同一方向均失败，通常向相反方向趋势。
- 两次break attempts在`3–20bars`内、极值距离≤`0.30ATR`，各自无scalp follow-through。
- 第二次failure的strong opposite signal触发；target flag/range height。
- Strong trend下仍需反向strength，不能只凭“第二次”逆势。

### REVERSALS-C07-S16：Climax Extreme Retest Expectation

- 类型：目标/再入场管理。
- 依据，PDF p.208、211–212、225–227：小final flag后虽有大修正，原spike momentum常使trend extreme在10–20bars或一两日内被测试。
- 仅在reversal未形成S11强flip、且first correction弱时保留retest state。
- Retest目标在旧extreme前获利；测试后failure可生成更大反转candidate。
- Horizon测试`5–30bars`，未测试样本完整保留。

### REVERSALS-C07-S17：Premise-Based Flag Reclassification

- 类型：动态状态更新。
- 依据，PDF p.212–215、222–224：bull/bear flag若不按预期突破而逐渐形成反向channel，交易者须放弃原premise并切新趋势。
- 每bar评估flag breakout、follow-through、channel HH/HL或LL/LH与EV。
- Strong opposite close触发撤销旧方向orders/退出，并按S04/S11决定新交易。
- 不使用名称固守仓位；所有重分类保存reason/time。

### REVERSALS-C07-N01：Final Flag 只能事前称 Candidate

- 类型：`NEGATIVE`标签约束。
- 依据，PDF p.207：趋势结束后任何最后flag都显而易见，实时却无法确定。
- 训练特征不得包含“这是最终flag”的未来标签；只使用S01 score。
- Candidate全集包括普通flag、failed final flag、larger flag及真正reversal。

### REVERSALS-C07-N02：Strong Momentum 中不抢弱 Final-Flag Short/Long

- 类型：`NEGATIVE`硬否决。
- 依据，PDF p.218–220：exceptionally strong momentum下短小flag和单根反向bar不足，通常sideways后再创新极值。
- 未见significant opposite strength/S11时，countertrend weak-signal交易数为零。
- 优先S08旧趋势breakout pullback。

### REVERSALS-C07-N03：Final Flag 不要求顺趋势 Breakout

- 类型：`NEGATIVE`检测约束。
- 依据，PDF p.208、212–213、221–225、228–229：许多final flag直接反向break或长成反向channel。
- 检测器不得以“先创新高/低”为必要条件；S03与S04均纳入全集。
- 不能因无顺势break事后排除成功反转。

### REVERSALS-C07-N04：固定 Tick、10 Bars、Two Legs 不作保证

- 类型：`NEGATIVE`参数约束。
- 依据，PDF p.208–230：1–3ticks、4ticks、10–20bars与two legs为案例/近似。
- 距离按ATR/spread/tick归一；horizon测试`5–30bars`，legs报告`0–3+`。
- 未达目标或极值复测失败的样本不能删除。

### REVERSALS-C07-N05：Volume 不能单独批准 Final Flag

- 类型：`NEGATIVE`特征约束。
- 依据，PDF p.221、225–226：极端volume可支持climax解释，但price action与context才决定交易。
- Volume只作overlay；低volume不否决，high volume不单独生成entry。
- 样本外无增量校准/EV则删除volume特征。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 207–210 | final flag特征、mature trend、horizontal magnet、micro/扩张flag与事后标签问题 | S01–S07、N01 |
| 210–215 | climax后微flag、三种break路径、failed H/L1–2、failed final flag与动态重分类 | S03–S12、S16–S17、N02–N04 |
| 215–219 | Figure 7.1–7.2：强反转位移、tight range、嵌套final flags与micro scalp | S02–S03、S05–S07、S10、S12–S13 |
| 219–224 | Figure 7.3–7.5：强momentum失败、LH final flag、无顺势break、channel与follow-through | S04、S07–S11、S15–S17、N02–N03 |
| 224–227 | Figure 7.6–7.8：direct bear break、opening small flag、ii、two-bar flag及极值复测 | S04–S05、S14、S16 |
| 227–230 | Figure 7.9–7.11：小flag扩张、无顺势break、climax后成功/失败final flags | S04–S09、N01、N03–N05 |

## 4. 回测验收

- Candidate在flag形成时保存；最终`ordinary/final/failed/evolved`标签仅供评估，不进入特征。
- Flag边界、trend age、climax、breakout与flip均带`valid_from`，未来回填次数为零。
- S03–S17共享final-flag episode ID；nested patterns使用parent-child关系，禁止重复计同一move。
- 分开报告direct counter break、with-trend failed break、reversal failure、larger flag与old-trend resumption。
- Early、second-entry、confirmed flip及failed-reversal版本比较净EV、MAE/MFE与成本。
- Strong-momentum弱逆势、future-final标签、with-trend-break必要化及volume-only entry设自动测试。
- Tick/bar/leg参数做walk-forward、跨品种/周期/时段/volatility sensitivity。
- Figure 7.1–7.11仅作章节例证，不作参数拟合或绩效证据。
