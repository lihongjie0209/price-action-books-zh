# 第 26 章：一笔交易至少需要两个理由

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/37-ch26-need-two-reasons-to-take-a-trade.md`
- PDF 页码：524–532
- 图表：Figure 26.1–26.6；正文与图注足以定义规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Reason Engine

每个candidate生成结构化理由，不允许自由文本重复计分：

```text
families = {
  REGIME, SIGNAL_BAR, PULLBACK, LEVEL, PATTERN,
  FAILURE, SECOND_ENTRY, MOMENTUM, TIMEFRAME
}
eligible = regime_gate_passed
           AND distinct_reason_families >= 2
           AND no_veto
```

- 同一事实的同义标签只算一个family。例如double bottom、H2和两腿底若来自相同pivots，只计`PATTERN`一次。
- 第二入场本身隐含第一次失败，可同时提供`SECOND_ENTRY`和原始setup family，但必须有真实first entry事件。
- 每个理由保存`known_at, source_rule_id, feature_values`，只用已完成bar。

## 2. 规则卡

### RANGES-C26-S01：Two Independent Reasons Gate

- 类型：全策略确认过滤器。
- 依据，PDF p.524–526：通常任意两个合理理由足以准备入场；满足后按既定stop/target执行，避免临场犹豫。
- Candidate先通过方向/regime gate，再要求至少两个不同families。
- 合格例：趋势+EMA两腿pullback、wedge+support、double bottom+good reversal bar、failed breakout+second entry。
- 入场、stop、target由基础setup规则提供；本规则不改变风险收益。
- 同一family内多个描述只提高质量score，不增加reason count。
- 回测比较1/2/3+独立理由的增量，不预设理由越多必然越好。

### RANGES-C26-S02：强趋势 Pullback 的单理由例外

- 类型：例外顺势策略。
- 依据，PDF p.524–525：强趋势中每个非climax/final-flag后的pullback都应考虑顺势，即使只是spike里的H1/L1。
- Strong trend：Always-In score达标、最近 `3–6bars` 同向位移≥`1.5ATR`、方向bodies≥70%、overlap低。
- Pullback形成H1/L1或EMA/previous-bar测试即允许一条理由触发。
- Climax、final flag、major trend-channel overshoot为硬否决，恢复普通双理由/第二entry要求。
- 止损与目标沿用趋势pullback策略，远stop按固定账户风险缩仓。

### RANGES-C26-S03：Trend-Channel Overshoot + Good Reversal Bar 单理由例外

- 类型：条件fade策略。
- 依据，PDF p.524–525：trend-line/channel overshoot并出现良好reversal bar可单独fade；陡峭channel仍优先第二entry。
- Overshoot≥`1tick–0.20ATR`，signal body方向占range≥50%、close在方向端25%。
- 普通/成熟channel允许首signal；tight/steep channel交给S04。
- 入场：reversal bar极值外stop；止损在overshoot最终极值外。
- 目标：channel中线/另一侧、EMA、1R/2R。
- 仅bar count而没有overshoot/reversal质量不能使用此例外。

### RANGES-C26-S04：第二 Entry 单理由例外

- 类型：第二信号策略。
- 依据，PDF p.525、527–531：second entry内含第一次尝试，尤其强来势、陡峭channel和countertrend reversal中更可靠。
- 必须保存第一次signal与实际trigger/failure；随后价格恢复原move并产生独立第二signal。
- 入场：第二signal预期方向极值外stop；强bear/bull signal优先。
- 止损：两次尝试完整结构极值外。
- 目标：旧极值、1R/2R、两腿。
- TTR/barbwire中的第二entry仍受S08否决，除非为强趋势EMA顺势例外。

### RANGES-C26-S05：Support/Resistance + Pattern Confluence

- 类型：通用两理由策略。
- 依据，PDF p.524–528：major swing、trend/channel line、EMA、breakout test、measured move、dueling lines等level与H/L2、double top/bottom、wedge、expanding triangle结合。
- Level必须入场前已知，测试容差 `0.10–0.30ATR`。
- Pattern由独立pivots确认；signal bar可作为第三family。
- 入场：pattern signal极值外stop；止损在level假突破/形态极值外。
- 目标：旧极值、range另一侧、measured move、1R/2R。
- 多个事后level不得任选；使用预注册优先级。

### RANGES-C26-S06：Failure + Signal/Location

- 类型：失败形态策略。
- 依据，PDF p.525–526、528–529：breakout、flag、overshoot reversal或profit target failure均可成为理由，但需要位置/signal等第二依据。
- Failure在 `1–3bars` 内实时确认；固定5/9tick failure改为目标前 `1–2ticks` 未fill并反转。
- 第二理由为range edge、support/resistance、good reversal bar或second entry。
- 入场：reclaim/反向signal极值外；止损在failed move最终极值外。
- 目标：原结构另一侧、1R/2R。
- OHLC无法判target fill时采用保守unknown，不伪造failure。

### RANGES-C26-S07：预期 Setup Watchlist

- 类型：事件前准备组件。
- 依据，PDF p.524：提前预判可减少犹豫，例如major swing break+两腿、channel overshoot、ii overdone、outside/barbwire extreme、首次EMA事件。
- 每bar生成未来 `1–10bars` 候选watch events：`expected_setup, required_second_reason, invalidation, expiry`。
- Watchlist不下单；条件完成后才交S01–S06。
- 到期/失效自动删除，不因后来出现形态回填早期预判。
- 对比有/无watchlist的漏单率与延迟，但不把预判准确率当交易收益。

### RANGES-C26-S08：Regime-Consistent Bar Counting

- 类型：方向门控。
- 依据，PDF p.524–525、528：H2只在bull/range底部买，L2只在bear/range顶部卖；陡峭反趋势中H/L2/4不是reversal理由。
- Bull trend禁止L1–4 countertrend，bear trend禁止H1–4，除非先有significant line break/overshoot reversal。
- Significant break需强momentum≥`1ATR`或连续2方向bars；sideways drift不足。
- Direction gate先于reason count；两个非法理由仍不能触发。
- Countertrend开放后仍需第二entry或两条独立反转理由。

### RANGES-C26-S09：强趋势首次 EMA 测试的执行选择

- 类型：多周期执行方案。
- 依据，PDF p.529–530：强趋势前两次EMA测试可limit，或在低周期做第二entry；传统主周期stop entry通常更简单且风险差异有限。
- 主版本：5分钟EMA测试signal顺趋势端stop；备选：1分钟第二entry、首次close跨EMA market、EMA limit。
- 四种执行使用相同setup母样本，分别模拟stop距离、slippage、fill和注意力成本。
- 默认选择主周期stop，只有样本外显著改善才采用低周期版本。
- 低周期数据必须时间同步且只用当时完成bar。

### RANGES-C26-S10：高级 Countertrend Scale-In 研究方案

- 类型：高级limit/scaling策略。
- 依据，PDF p.531–532：经验交易者可在强bear新低按prior swing low买半仓，再低一档加仓，回原entry整体退出；不适合初学者。
- 仅作为独立高级模型，禁止与新手/主策略合并。
- Entry1在prior swing low，Entry2低 `0.5–1.0ATR`；两腿各半仓。
- Stop在Entry2下 `0.5–1.0ATR`，组合总风险不超过普通一笔预算。
- Exit：仅Entry1成交取预注册scalp；两腿成交则回Entry1全部退出。
- Strong trend acceleration/close附近禁用或缩小；必须评估尾部gap与连续无反弹风险。

### RANGES-C26-N01：Steep Trend 中两个 Countertrend 理由也无效

- 类型：`NEGATIVE`硬否决。
- 依据，PDF p.524、527–531：陡峭trend/channel中即使有wedge、H/L2/4或reversal bar，首countertrend entry仍低概率。
- 未有strong line break、channel overshoot+reversal或Always-In flip时，countertrend order数量必须为零。
- Tight channel首break只标candidate，等待S04 second entry。
- “理由数量≥2”不能覆盖该否决。

### RANGES-C26-N02：TTR/Barbwire Trumps Reason Count

- 类型：`NEGATIVE`。
- 依据，PDF p.524、528–529：多bar高度重叠的TTR里，L2、两bar reversal和大signal仍可能是trap；应等强breakout失败或边缘小bar fade。
- TTR确认后禁用普通S01–S06 stop entries。
- 仅允许：强trend bar越界≥`3ticks/0.20ATR`后的failure、breakout pullback，或高级边缘小bar limit。
- Large signal迫使在range错误边缘成交时拒绝。

### RANGES-C26-N03：理由数量不可替代 Trader's Equation

- 类型：`NEGATIVE`。
- 依据，PDF p.524–532与第25章承接关系：两条理由提高执行一致性，但每笔仍须有正EV与合理stop/target。
- 所有通过S01的candidate继续经过第25章EV gate；`reason_count>=2 && EV<=0`必须拒绝。
- 不因5个相关理由扩大仓位；仓位仍按stop距离与账户风险。
- 按理由family组合报告样本外增量，淘汰无贡献/高度共线理由。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 524–526 | 双理由规则、强趋势/overshoot/second-entry例外、理由清单 | 定义、S01–S08、N01、N03 |
| 526–528 | MA/20-gap共振、failure、expanding triangle、陡势第二entry | S04–S07、N01 |
| 528–530 | H/L2位置、TTR trap、bar内时机与多周期EMA执行 | S08–S09、N02 |
| 530–532 | tight-channel第二signal、wedge/final flag、逆势scale-in案例 | S03–S04、S10、N01 |

## 4. 回测验收

- 每笔candidate保存独立reason families及`known_at`，同义理由去重。
- Regime/TTR否决优先于count；违反方向或TTR的主策略交易数必须为零。
- 比较1、2、3+理由的样本外EV，控制regime/setup，验证双理由是否提供增量。
- 单理由例外S02–S04分别报告，不与普通双理由样本混合。
- Second entry必须有真实第一signal/trigger/failure事件，不能由最终两腿形状回填。
- Level在触达前保存；failure依赖成交时使用tick数据或保守假设。
- S09各执行版本共享同一母样本并计真实成本；低周期不得前视。
- S10报告组合MAE、gap stress、最大连续加仓亏损和risk of ruin。
- 所有candidate最终仍通过第25章成本后EV gate。
- Figure 26.1–26.6只作章节例证，不作参数拟合或绩效证据。
