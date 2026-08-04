# 第 2 章：突破强度的迹象

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/09-ch02-signs-of-strength-in-a-breakout.md`
- PDF 页码：102–123
- 图表：Figure 2.1–2.3；正文与图注已逐bar完整说明，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 可解释 Breakout Strength Score

不要把相互重叠的迹象直接相加。先计算五个0–1分组，再聚合：

```text
breakout_score = weighted_mean(
    breakout_bar_quality,
    follow_through_quality,
    context_quality,
    first_pullback_quality,
    displacement_quality
)
```

| 分组 | 主要特征 | 初始参数 | 来源 |
|---|---|---:|---|
| Breakout bar | 大方向实体、小尾部、收在极值附近、形成时回撤小 | body/range 0.6–0.9 | `AUTHOR` + `PROXY` |
| Follow-through | 后2–3bars同向、spike达5–10bars、低重叠 | 2–3 / 5–10 bars | `AUTHOR` |
| Context | 顺既有趋势、range内压力、突破多个关键位 | 2–5个关键位 | `AUTHOR` + `PROXY` |
| First pullback | 3bars后才出现、仅1–2bars、不触breakout/entry | 见S04 | `AUTHOR` |
| Displacement | 足够scalp、micro gap、反转多个近期极值/收盘 | 5–20bars回看 | `AUTHOR` |

- 初测标签：`score>=0.75 STRONG`、`0.55–0.75 UNCERTAIN`、`<0.55 WEAK`，均为`PROXY`。
- 方向完全对称；代码应以方向标准化坐标实现，禁止维护两套逐渐漂移的bull/bear逻辑。
- 每组保留原始特征和贡献，用训练期校准概率；原文强突破约60–70%跟进、最强仍约30%失败，均只作待验证基准。

## 2. 规则卡

### RANGES-C02-S01：Breakout Bar 质量

- 类型：评分组件。
- 依据，PDF p.102–107：成功突破bar通常实体大、尾部小、收在突破端；形成过程中大部分时间靠近极值且回撤少于增长bar约1/4。
- 收盘特征：`body/range=0.60–0.90`、顺势尾部/range≤0.20、逆势尾部≤0.30、close位于顺势端10–25%。
- 若有tick/intrabar数据：最大逆向回撤≤当时最大bar高度的0.25为强；超过2/3为弱；两次以上回撤≥1/3进一步扣分。
- 只有OHLC时不得推断bar内路径；intrabar特征标记missing并重新归一化权重。
- bar大小用 `range/ATR20=1.0–3.0` 分层；极端大bar也标记`POSSIBLE_CLIMAX`，不假定越大越好。

### RANGES-C02-S02：Follow-Through、Micro Gap 与 Urgency

- 类型：评分与参与组件。
- 依据，PDF p.102–106、108–112：后2–3bars同向、5–10bars少回调、相邻bar几乎不回到prior close及micro gap都是强度迹象。
- 后2–3bars同向body不小于此前20bars实体中位数，且无强反向bar则加分。
- spike在首次超过1bar的pullback前持续 `5–10bars` 为runaway子组。
- bull micro gap：bar[t-1] high≤bar[t+1] low；bear对称；严格不重叠和1tick容差分别报告。
- urgency代理：prior close limit未触及、open跳过prior close、close靠极值、连续新高/低。
- `STRONG`确认后按第1章S01小仓参与；风险到spike起点，仓位按固定账户风险缩小。

### RANGES-C02-S03：Context 与 Range 内累积压力

- 类型：方向先验组件。
- 依据，PDF p.103–109：顺趋势flag恢复、主要trend-line break后的结构测试、近期同向趋势日和range中显著同向压力提高成功率；多年range与区间边缘降低成功率。
- 正向context：外层Always-In同向、breakout pullback恢复、同向大bar数/总实体显著高于反向、突破EMA+swing+trend line多个层级。
- 压力比：`sum(directional bodies)/sum(opposite bodies)`，初测≥1.5强、≤0.67弱。
- 负向context：过去 `2–5sessions` 仍为大range、目标是range远端、趋近过程高重叠/大尾部/多次pullback。
- 多关键位突破按独立结构计数；同一swing同时被称为trend line和range edge时只算一次。
- context只影响score，不覆盖实时失败条件。

### RANGES-C02-S04：首次 Pullback 质量与入场

- 类型：完整breakout-pullback策略。
- 依据，PDF p.103–107、113–114：强突破首次pullback通常在至少3bars后、只持续1–2bars，不到breakout point或entry；深且持续多bars则失败概率上升。
- 强pullback：在第3bar以后开始、持续1–2bars、深度≤spike的0.25–0.50，不触breakout point/entry，signal不是强逆向bar。
- 入场：High/Low 1；若深回调或进入约10bars小range，等待High/Low 2或两腿结束。
- 止损：pullback极值外。
- 目标：pullback range高度、spike高度测量移动、1R/2R。
- 弱化：回撤越过breakout point、spike第一bar不利极值或breakeven entry，每项扣分；强反向跟进则转S06。

### RANGES-C02-S05：位移与“可获得 Scalp”最低成功标准

- 类型：结果标签与执行门槛。
- 依据，PDF p.102–107：成功breakout最低标准是stop entry后能获得scalper's profit；越过重要swing但连scalp空间都没有，是失败迹象。
- 在事件前冻结`scalp_target=max(estimated_costs*3, 0.25–0.75ATR)`；不同资产需按tick和成本校准。
- 成功位移：breakout trigger后先到`scalp_target`再触结构stop。
- 强位移附加：突破bar的close反转最近 `5/10/20` 个closes与extremes；close越过的权重大于仅wick越过。
- 输出first-passage结果、到达bars、MAE/MFE，不用最终趋势标签替代。
- 该规则用于标签和score校准，不因达到scalp目标强制退出swing仓位。

### RANGES-C02-S06：Weak Breakout 的快速 Fade

- 类型：完整失败突破策略。
- 依据，PDF p.104–107、109–110、114：小实体、大突破端尾部、下一bar强反向/inside、仅轻微越界及无可得scalp常导致回到range或反转。
- Setup：score<0.55；越界仅 `1tick–0.20ATR`，或下一bar强反向收盘；context为range边缘。
- 失败确认：`1–3bars` 内回到breakout point内，且未先达到S05 scalp目标。
- 入场：返回range的signal bar外stop；高级版本可fade breakout close/其外limit，必须单独统计。
- 止损：失败极值外。
- 目标：range中点、对侧、1R/2R；在外层趋势逆向时只取scalp。
- 若反转自身失败，立即转S07，不能在旧失败观点上scale无限仓位。

### RANGES-C02-S07：失败突破的再失败——Breakout Pullback

- 类型：失败后的延续策略。
- 依据，PDF p.114、117–120：任何结构的突破都同样处理；breakout失败可fade，而该反转若失败，就成为原突破方向的breakout pullback。
- 状态：`BREAKOUT -> FAILED_BREAKOUT -> FAILURE_OF_FAILURE`。
- 触发：S06反转signal被原突破方向越过，或回测形成higher low/lower high并守住breakout point。
- 入场：反转signal极值外stop或首次回测。
- 止损：失败反转极值外。
- 目标：breakout极值、measuring gap投射、1R/2R。
- 每个事件终态互斥，bar内先后顺序不明时使用保守路径或次bar确认。

### RANGES-C02-S08：Flag 向“较不可能方向”突破

- 类型：反预期突破策略。
- 依据，PDF p.115、121–123：bear flag上破或bull flag下破会困住顺flag交易者，常形成measuring gap和测量移动；失败wedge/Low 2是典型载体。
- Setup：已确认flag及预期延续方向；预期signal触发失败，随后1–2根强bar向相反方向突破flag。
- 确认：Always-In翻转，或突破bar+follow-through总位移≥ `0.75ATR`。
- 入场：反预期breakout close小仓或首次小pullback。
- 止损：flag最终极值外。
- 目标：flag高度、breakout spike高度、measuring gap对称投射、1R/2R。
- 旧方向交易者预计至少等待两腿再入场只作机制假设；退出/重入以价格状态决定。

### RANGES-C02-S09：Small Breakout Bar 的渐进确认

- 类型：弱初始信号延续策略。
- 依据，PDF p.108、122–123：breakout bar可以很小；若随后横向不回到breakout point并稳步同向移动，仍可形成持久趋势。
- Setup：bar range≤ATR且越过已确认结构，score初始处于0.45–0.65。
- 确认窗口 `2–5bars`：多数bar同向/中性、breakout point未被收盘穿回、净位移≥ `0.5ATR`。
- 入场：确认bar外stop或首次breakout test；不在小bar刚形成时盲目追价。
- 止损：breakout point另一侧/小range极值外。
- 目标：小range高度、第一腿等幅、1R/2R。
- 若窗口内返回旧range，转S06。

### RANGES-C02-S10：Spike→Channel→Range 的强度衰减

- 类型：市场状态与退出组件。
- 依据，PDF p.108–113、118–120：成功breakout先成spike，随后动能减慢为channel；channel通常被回撤到起点并成为新range第一腿。
- spike结束：首次pause/回调；channel确认：斜率降低、overlap/tails/逆向bars增加且仍有trending swings。
- channel内继续顺势但停止S02式追价；在第三推进/测量目标处减仓。
- 反向breakout后目标：channel起点、首个合理逆向signal、breakout gap。
- 到channel起点后停止用原breakout预测，切换普通range状态。
- 大强spike出现时重置此前climax计数；不能让较小旧高潮压过已改变市场性质的新breakout。

### RANGES-C02-S11：尾盘强制平仓型 Spike

- 类型：尾盘止盈/短动量研究。
- 依据，PDF p.115–116：趋势日最后一小时可能因逆势持仓被迫平仓出现1–2根大bar或持续channel，通常后续有限。
- 时间窗：session fraction `0.80–1.00`；已有强趋势同方向突然加速。
- 顺势旧仓：在异常spike强势处减仓，不把其自动视为跨日新腿。
- 新动量仓：仅用 `0.25–0.50` 标准规模，目标0.5–1R或收盘，禁止隔夜延伸假设。
- 若仍有足够时间且breakout pullback守住，可按普通S04；否则收盘强制退出。
- “risk manager forced liquidation”不可直接观察，仅以时间、方向、加速度代理，需明确标为机制推断。

### RANGES-C02-N01：不得交易每一次 Breakout

- 类型：`NEGATIVE`。
- 依据，PDF p.108–114、117：每个trend bar、每次越过prior bar都可称breakout，但多数失败；无筛选追所有breakout是亏损策略。
- 只有S01–S05证据足以确认强度时才顺突破close入场；range中普通trend bar优先等待S06/S07。
- 单一大bar不能覆盖range context、climax位置或糟糕follow-through。
- 图中最终形成大趋势不能作为早期所有微小breakout都有效的证据。

### RANGES-C02-N02：Volume 只能作为可选特征

- 类型：`NEGATIVE`。
- 依据，PDF p.102、105、112：10–20倍近期均量提高跟进概率，但高量失败也会发生，价格bar本身通常已表达信息，volume可能分散注意。
- volume ratio `volume/median(volume,20)` 作为独立可选组，不与bar size重复加分。
- 必须比较price-only与price+volume的样本外增量；没有可靠集中成交量的市场直接禁用。
- 不得因高volume忽略S06的明确失败行为。

### RANGES-C02-N03：局部反转形态不能压过强 Breakout 大局

- 类型：`NEGATIVE`。
- 依据，PDF p.118–120：四bar强spike改变市场性质后，局部channel overshoot、第二反转或climax多半只是flag；强趋势有惯性。
- STRONG breakout确认后，普通逆向signal不交易，直到主要trend-line break、反向spike跟进和第二信号。
- countertrend scalp若会妨碍顺势swing则完全过滤。
- 允许反转只依据当前价格结构，不以新闻、基本面或Elliott标签覆盖。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 102–107 | bull/bear成功与失败迹象完整清单 | 第1节、S01–S06 |
| 108–112 | breakout本质、多数失败、60–70%强breakout及spike/channel | S01–S03、S05、S10、N01–N02 |
| 113–116 | 深浅pullback、fade/reentry、unexpected flag与尾盘spike | S04、S06–S08、S11 |
| 117–121 | 各类breakout、失败后的失败、measuring gap和大局 | S07、S10、N03 |
| 121–123 | flag反向突破、反转多bar closes、小bar突破 | S05、S08、S09 |

## 4. 回测验收

- 五个分组特征逐bar保存，组内先去相关再聚合；不得简单把长清单当独立票数。
- 概率用walk-forward校准，并分别检验原文60–70%成功、最强约30%失败的基准。
- intrabar回撤特征只有真实tick数据时启用；OHLC回测不得猜测路径。
- S04按首回调开始bar、持续和深度建立三维条件概率。
- S05的scalp target在事件前按成本/ATR冻结，报告first-passage而非最终方向。
- S06/S07/S09共享事件ID并保持`success/failure/failure-of-failure`终态互斥。
- S08按flag类型、预期方向和Always-In翻转分层。
- S10从spike确认时冻结channel起点，报告其最终测试率和时间。
- Volume做消融实验；无增量则从正式模型删除。
- Figure 2.1–2.3仅作章节例证，不作参数拟合或绩效证据。
