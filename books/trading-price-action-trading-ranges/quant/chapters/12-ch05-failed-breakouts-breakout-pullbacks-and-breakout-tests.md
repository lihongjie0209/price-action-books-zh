# 第 5 章：失败突破、突破回调与突破测试

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/12-ch05-failed-breakouts-breakout-pullbacks-and-breakout-tests.md`
- PDF 页码：140–158
- 图表：Figure 5.1–5.10；正文与图注已逐bar完整说明，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 统一事件状态机

```text
BREAKOUT -> PULLBACK_ATTEMPT
PULLBACK_ATTEMPT -> BREAKOUT_FAILURE -> REVERSAL
PULLBACK_ATTEMPT -> FAILURE_OF_FAILURE -> BREAKOUT_RESUMPTION
BREAKOUT_RESUMPTION -> BREAKOUT_TEST -> CONTINUATION | FINAL_FAILURE
```

- 原文把pullback开始视为breakout暂时“失败”；量化上用`PULLBACK_ATTEMPT`避免与最终失败混淆。
- `BREAKOUT_TEST`可在下一bar或20+bars后发生，同一breakout允许多个test，但共享唯一`event_id`。
- breakout对象可为range、flag、swing、trend line、日高低或信号bar；检测逻辑统一，仅context不同。
- 方向标准化实现，bull/bear完全镜像。

## 2. 规则卡

### RANGES-C05-S01：Breakout、Failure 与 Pullback 事件账本

- 类型：基础状态组件。
- 依据，PDF p.140–144：breakout最终都会pullback测试重要价位；失败若真正反转则breakout失败，反转若仅1–2bars又失败则成为breakout pullback。
- Breakout：收盘越过冻结结构 `0.05–0.25ATR`。
- Pullback attempt：首次bar逆向极值超过prior bar，或价格从breakout极值回撤 `0.15–0.50ATR`。
- Final failure：回到breakout point内并形成反向follow-through/Always-In翻转。
- Failure-of-failure：反向signal被原方向突破，或breakout point回测守住并恢复。
- 保存每个状态时间、价格、强度、测试层级和互斥终态；未完成事件保持open。

### RANGES-C05-S02：强弱 Breakout 与 Reversal 的裁决

- 类型：双分支决策策略。
- 依据，PDF p.140–143：breakout明显强于reversal时顺突破；reversal明显强时反向；两者接近时下一bar决定。
- 使用第2章breakout score与对称reversal score。
- `score_diff>=0.15`：顺breakout，等待S04；`<=-0.15`：按S03反转；中间区间等待下一bar。
- 下一bar强反向trend close提高failure概率；强原方向bar使反转signal成为S04 signal。
- 不在同一bar假设两个互斥stop都以理想顺序成交；路径未知用次bar确认。
- 所有阈值为`PROXY`，按校准概率替代固定差值作为正式模型。

### RANGES-C05-S03：最终 Failed Breakout 反转

- 类型：完整反转策略。
- 依据，PDF p.140–144、146–150：弱breakout后强反向bar、第三推进、channel overshoot或连续climax可形成可交易failure。
- Setup：S01 breakout后 `1–5bars` 返回结构内，且未先取得预定义scalp target。
- 加分：第三推进、突破仅1tick、强反向signal、final flag、多个climax、外层range边缘。
- 入场：反向signal bar外stop。
- 止损：失败breakout极值外。
- 目标：旧range中点/对侧、breakout起点、两腿、1R/2R。
- 若下一bar为强原方向reversal，立即退出/反手S04。

### RANGES-C05-S04：Failure-of-Failure Breakout Pullback

- 类型：完整顺突破策略。
- 依据，PDF p.140–145、148–155：所有未能反转市场的failed breakouts都会成为breakout pullback；连续失败是第二入场，属于最可靠顺势setup之一。
- Setup：S03反转signal没有跟进，或回测breakout area后原方向买卖盘重新占优。
- 入场：failure signal原方向极值外stop；若先形成High/Low 2或wedge flag，以其signal为准。
- 止损：breakout test极值外。
- 目标：breakout极值、至少第二腿、measuring gap/第一腿等幅、1R/2R。
- 强breakout可接受test不触breakout point；stairs等宽channel允许更深test，但必须保留trending swing结构。
- 触发后breakout bar通常成为measuring gap；若最终反转则标exhaustion gap。

### RANGES-C05-S05：Breakout Test 价位阶梯

- 类型：目标与信号组件。
- 依据，PDF p.142–144：pullback常依次测试breakout point、signal high/low、entry bar、spike/channel起点、stairs swing、旧range和一般支撑阻力。
- 事件发生时登记并按距离排序：
  1. signal bar extreme / theoretical entry；
  2. breakout point / gap midpoint；
  3. recent swing / stairs breakout；
  4. channel start / spike top；
  5. lower/upper range边界；
  6. EMA、trend line、trend-channel line、leg origin。
- zone容差 `0.05–0.30ATR`；到达近层后才启用远层。
- 每一层的test bar都可成为S04 signal，但必须满足方向性反转，单纯触价不入场。
- 若强势穿透并有follow-through，关闭该层并移向下一层。

### RANGES-C05-S06：近似 Breakout Pullback

- 类型：near-miss等价策略。
- 依据，PDF p.144–145、149：强推进接近旧极值但未实际越过，随后1–4bars安静pullback，通常与真正breakout pullback同样交易。
- `near_miss_distance<=max(1–3ticks, 0.10ATR)`，且推进净位移≥ `0.75ATR`。
- pullback持续 `1–4bars`、不强势反转推进。
- 入场：顺推进方向signal外stop。
- 止损：pullback极值外。
- 目标：旧极值、真正breakout后的scalp target、1R/2R。
- near-miss与actual breakout分层报告，验证“close is close enough”而非预设等价。

### RANGES-C05-S07：Breakeven Stop Run 的持有/再入场

- 类型：止损校准与再入场组件。
- 依据，PDF p.145、150–153：不同品种可能精确尊重entry，也可能经常穿越数ticks后恢复；可留buffer持有，或被扫后在test bar外再入。
- 对每个资产滚动估计过去 `50–250` 次成功test的最大穿越分布，不使用未来数据。
- buffer候选：穿越分布50/75/90分位，且上限 `0.05–0.25ATR`。
- 持有版：stop放entry外buffer；再入版：breakeven退出，test bar原方向极值外stop重入。
- test成功后才把stop移至test bar外。
- 比较额外风险与再入滑点；账户总风险包含buffer，不能称“近似保本”后忽略真实亏损。

### RANGES-C05-S08：Major Reversal 的宽容 Breakout Pullback

- 类型：大级别反转延续策略。
- 依据，PDF p.145–146、153–158：major reversal也可视为trend-line breakout pullback；回调可形成lower low、higher low、higher high或lower high，甚至越过旧极值仍有效。
- Setup：主要trend line已被强反向breakout，随后回测旧趋势极值。
- 不要求标准higher low/lower high；记录`LL/HL/HH/LH`四类，只要breakout方向结构未被强反向follow-through否定。
- 入场：第二信号、failed old-trend breakout或强breakout-pullback bar。
- 止损：回测最终极值外。
- 目标：此前flag极值、旧趋势起点、两腿、1R/2R。
- 旧极值越界深度按ATR分层，不能无限宽容；完全回撤breakout并恢复旧趋势则失效。

### RANGES-C05-S09：Late Breakout 是 Exhaustion 还是新 Leg

- 类型：高潮双分支策略。
- 依据，PDF p.146–148：趋势末端大bar既可能是最后投降形成exhaustion，也可能是强势新breakout并形成channel；sideways修正表示原趋势仍强。
- Event：成熟趋势中出现range/body≥最近20bars中位数 `1.5–2.5倍` 的同向bar。
- 新leg分支：pullback仅1–3bars、回撤bar≤0.50、横向、随后High/Low 1恢复；按S04顺势。
- Exhaustion分支：连续2–3 climaxes、强反向signal、回撤bar>0.67或Always-In翻转；按S03。
- 止损/目标分别沿S03/S04；事件共享ID且终态互斥。
- 新强spike确认后重置旧climax计数，避免旧小高潮压倒市场性质变化。

### RANGES-C05-S10：Final Flag 兼作新趋势第一腿

- 类型：反转结构与持仓目标组件。
- 依据，PDF p.145–146、156–158：旧趋势最后flag有时在事后也是新趋势第一腿；最后climax可成为其深pullback，突破flag后常少回调并走得远。
- Setup：低动能flag持续 `10–30bars`，随后旧趋势最后推进失败，并出现强反向spike突破flag高/低。
- 入场：最后推进失败或flag极值反向breakout-pullback。
- 止损：最终旧趋势极值外。
- 目标：flag长度/高度投射、两腿、1R/2R；突破flag极值后保留较多swing仓位。
- 可选研究：final flag robust slope与新趋势slope之比 `0.5–2.0`；仅作目标/先验，不直接入场。
- final flag可在旧极值之前/之后结束，不能要求lower low/higher high教科书形态。

### RANGES-C05-N01：不能只看最近 Spike 忽视更强大局

- 类型：`NEGATIVE`。
- 依据，PDF p.150、152–153：强主趋势中的逆向spike常只是discount/flag；最近三根漂亮bar不能压过稍左侧更强spike和Always-In状态。
- 特征窗口同时保留短 `3–5bars` 与背景 `20–50bars`；背景强度≥0.75时，单个逆向spike不翻转状态。
- 反转至少需要主要trend-line break、follow-through和结构测试。
- 新闻造成的日线逆向bar也只按价格强度处理，不以新闻严重性判断持续性。

### RANGES-C05-N02：不要为微小 Scalp 忽略大转折

- 类型：`NEGATIVE`。
- 依据，PDF p.149–155：小周期存在大量精确test和tiny scalps，但多数交易者应聚焦更大turning points；频繁切周期会分散注意。
- 基础策略使用固定交易周期，不为单个候选临时下钻寻找perfect test。
- 只有完整低周期数据与预先固定规则时才做多周期版本。
- 小目标交易若会错过S03/S04/S08大级别signal，则过滤并记录机会成本。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 140–142 | breakout→failure→reversal或breakout pullback序列 | 第1节、S01–S04 |
| 142–144 | breakout test价位、强弱裁决与深回调 | S02–S05 |
| 144–146 | 近似breakout、breakeven run及major reversal | S06–S08 |
| 146–148 | 末端breakout的exhaustion/new leg双分支 | S09 |
| 148–155 | 多种pullback/test、品种buffer、强弱大局 | S04–S07、N01–N02 |
| 156–158 | failed flags、final flag兼新趋势第一腿及斜率 | S08、S10 |

## 4. 回测验收

- 所有breakout对象统一生成事件ID；同一事件多个test不得被计作独立breakout样本。
- S01终态互斥且允许open event；不得把未完成样本删除。
- S02做score差与实际终态的校准曲线，下一bar只在收盘后生效。
- S03/S04比较立即fade、等待反转、failure-of-failure三种路径和bar内不确定性。
- S05测试层级在breakout时冻结，并报告各层首次到达率/时间。
- S06 actual/near-miss严格分层；S07 buffer只由过去样本滚动估计。
- S08按LL/HL/HH/LH四类和回撤深度报告。
- S09建立new leg/exhaustion/range三终态；不能只保存两种成功叙事。
- S10的final flag标签按实时候选生成，事后解释不得回填交易。
- Figure 5.1–5.10仅作章节例证，不作参数拟合或绩效证据。
