# 第 9 章：Failures

## 元数据

- 英文来源：`books/trading-price-action-reversals/en/chapters/16-ch09-failures.md`
- PDF 页码：238–264
- 图表：Figure 9.1–9.19；正文与图注已完整说明规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Failure 事件模型

```text
planned_goal = scalp_target | swing_target | breakout_followthrough | structure_target
failure = goal未达且premise失效、退出缩小或反向路径触发
trap_fuel = still_open_qty_at_failure / original_qty
```

- Failure必须相对于入场前冻结的目标定义；达到scalp但未达预期swing，仍可标记`swing_failure/scalp_success`。
- 原setup、失败、反向交易与可能的second signal共享episode ID，但P&L逐笔记录。
- 所有固定tick/cent目标转为R、ATR、spread和品种惯常scalp尺度。

## 2. 规则卡

### REVERSALS-C09-S01：Generic Setup Failure Detector

- 类型：统一失败分类器。
- 依据，PDF p.238–244：H/L1–2、breakout、magnet、final flag、wedge、signal/entry bar、reversal与profit target都可能失败。
- 每类setup注册`trigger, invalidation, minimum_goal, max_horizon`；任一失效条件先于目标即failure。
- 输出`no_fill, small_profit, breakeven, stop_loss, target_miss, opposite_breakout`。
- 不把所有failure自动反手，须通过S02/S03的context和momentum门槛。

### REVERSALS-C09-S02：Signal/Entry-Bar Stop-Flush Reversal

- 类型：被困者反向策略。
- 依据，PDF p.239–240、244、247–248、256–258：价格强穿signal或strong entry bar保护stop时，被迫退出者令市场one-sided，通常足够scalp/two legs。
- Stop level在原entry时冻结；反向entry=`signal/entry extreme ±1tick`，要求failure bar body≥50%或follow-through。
- Stop在failure bar另一端；target`0.5–1R`/next structure，强context保留two-leg runner。
- 若原trade已scalp out多数仓，trap fuel降低并减仓/跳过。

### REVERSALS-C09-S03：One/Two-Tick Failed Breakout Fade

- 类型：小假突破策略。
- 依据，PDF p.240–247：range中1–2tick突破常困住stop entrants并迅速反向；股票尺度可为1–10cents。
- Confirmed range/弱momentum；extension≤`1–2ticks / 0.02–0.10ATR`，`1–2bars`内收回边界。
- Entry在failure bar反向trigger或突破者stop处；stop在false extreme外。
- Target midpoint/opposite edge/1R；strong trend breakout由N02否决fade。

### REVERSALS-C09-S04：Missed Protective Stop With-Trend Entry

- 类型：stop测试未命中策略。
- 依据，PDF p.241–242、247–248：回测signal/entry extreme但差1tick未触stop，形成double bottom/top flag，说明趋势方积极防守。
- Test距原stop=`1tick–0.05ATR`且未成交；随后出现原方向reversal bar。
- 在test bar trigger顺原trade方向入场，stop在test extreme外。
- 原持仓仍在者按add-on风险处理；空仓者作为breakout-test新交易。

### REVERSALS-C09-S05：Stop-Run Recovery Reentry

- 类型：被扫出好交易后的重入。
- 依据，PDF p.241–242、252–253：stop可被1–数ticks扫过后迅速恢复，困住原交易者out与反向者in，随后产生强move。
- Stop hit后`1–3bars`内close恢复原结构且出现strong signal/third push。
- 重入为新交易，stop在stop-run extreme外；episode累计risk受固定上限。
- 未快速恢复、出现follow-through则不重入，承认原setup失败。

### REVERSALS-C09-S06：Rolling Swing-Extreme Breakout Fade

- 类型：range边缘动态stop-entry。
- 依据，PDF p.242、249–252：range day可逐bar移动反向stop，fade新swing high/low；momentum过强时停止并等待trend-line break。
- Range confirmed；新高后sell stop放prior bar low下，未触则逐bar更新；新低镜像。
- 当leg位移≥`1.5–2ATR`、连续strong bars或breakout follow-through时取消。
- Stop在leg extreme外，目标range midpoint/1R；second entry优先。

### REVERSALS-C09-S07：Profit-Target Near-Miss Management

- 类型：目标差一档退出。
- 依据，PDF p.242–244、248–260：价格触limit但未穿越成交所需一tick并反转，未成交获利盘会退出，常推动反向scalp。
- 真实/保守fill模型识别`target_touch_no_fill`；near miss=`0–0.10ATR`或1成交档。
- 原持仓立即把target下调`1–3ticks / 0.05–0.15ATR`并收紧到breakeven/last swing；strong opposite signal可market exit。
- 不允许为多赚最后一tick承担原始8–10tick风险。

### REVERSALS-C09-S08：Failed-Target Opposite Scalp

- 类型：目标未达反向策略。
- 依据，PDF p.242–244、248–260：惯常scalp目标差一档、两次未达$1等显示momentum丧失，常至少反向scalp。
- 需S07 near-miss后价格穿回target bar反端或形成H/L2 opposite signal。
- Entry反向，stop在near-miss extreme外；target按当前缩小波动尺度`0.5–1R`。
- Strong trend swing仓不机械反手，只管理退出；regime必须允许。

### REVERSALS-C09-S09：Adaptive Scalp-Target Regime

- 类型：日内目标校准。
- 依据，PDF p.243–244、258–260：若多次8–11tick/$1目标失败且市场sideways，应缩短目标；clear trend则减少逆势scalp并保留顺势swing。
- Rolling最近`5–20`同类candidate的MFE分位数估算目标，训练/当日数据严格时间前向。
- 连续≥2 near misses或target fill rate显著下降时，将目标降至原`40–70%`。
- Regime重新扩张/strong trend后重置；不因单笔亏损临时改参数。

### REVERSALS-C09-S10：Flag-Failure With-Trend Trade

- 类型：最可靠failure顺趋势策略。
- 依据，PDF p.239、246–247、253–256、260–262：趋势内逆势reversal/flag多数失败；失败后的H2/L2、breakout pullback是高质量顺趋势entry。
- Higher-timeframe trend强，countertrend setup无significant trend-line break/follow-through。
- 在其signal/entry stop或随后with-trend pullback入场；目标旧极值/1–2R。
- 首次反转spike可等HL/LH确认，尤其channel持续多bars时。

### REVERSALS-C09-S11：Failed Pattern Measured Move

- 类型：结构失败延伸策略。
- 依据，PDF p.238–239、254–256：failed wedge、double-bottom flag、H&S等突破后常产生形态高度measured move/two legs。
- Pattern boundary/height在failure前冻结；strong close越invalidation+follow-through触发。
- Target=`0.75–1.25 pattern_height`，分批在first leg/structure获利。
- Weak breakout可能变成failed failure，交S05/独立反向candidate。

### REVERSALS-C09-S12：First Trend-Line Spike Failure Buy/Sell

- 类型：强趋势折价/溢价策略。
- 依据，PDF p.244、260–262：强趋势首次巨大countertrend spike通常失败，趋势方把markdown/markup视作机会；单一spike不构成反转。
- Old trend强；首次counter spike穿line/EMA但无旧极值test与follow-through。
- Aggressive在spike close/次日open半仓，conservative等weak follow-through+trend signal。
- Stop在spike structure外并缩仓；目标新trend extreme，隔夜gap风险单独建模。

### REVERSALS-C09-S13：Failure as Urgency / Trend Strength

- 类型：未触及价位的强度特征。
- 依据，PDF p.239、261–263：pullback未触prior bar、EMA、swing或signal extreme，可能因趋势方提前limit进入，表示urgency。
- 目标level前`1–2ticks / 0.02–0.10ATR`转向，且higher-timeframe trend同向。
- 在direction signal/next break顺趋势入场；stop在turn extreme外。
- 与S04区分：这里是未达一般magnet，非专门保护stop；不可推断具体机构意图。

### REVERSALS-C09-S14：Magnet Near-Miss Then Retest

- 类型：未完成目标二次尝试。
- 依据，PDF p.239、261–264：若距明显measured target足够近进入磁场但未完成测试，pullback后常再尝试；远超目标则说明市场忽略它。
- Magnet在move前冻结；near zone=`1–3ticks / 0.05–0.20ATR`，complete zone=`0–1tick`。
- Pullback形成顺原方向flag后入场，target magnet前一档；overshoot>`0.20–0.50ATR`关闭该magnet。
- 若near miss伴随S07反向signal，两个candidate按regime/EV互斥选择。

### REVERSALS-C09-S15：Two-Legged Extreme-Test Failure

- 类型：MTR/second-entry策略。
- 依据，PDF p.256–258：major trend-line break后，旧极值two-leg test失败是可靠反向setup；test bar过强/外包bar则等更安全触发。
- Break强，test包含2 pushes；在旧extreme区域形成second entry/reversal。
- Outside/two-bar reversal entry取两bar较远反端，避免inside breakout噪声。
- Barbwire/连续sideways dojis不交易，等其failure方向明确。

### REVERSALS-C09-S16：First-Hour Double-Flag Risk Management

- 类型：开盘range策略。
- 依据，PDF p.253–254：首小时double top/bottom flags多可交易但易连续失败，需部分scalp并移breakeven，最终识别triangle。
- Session前`60–90min`，range edge double setup可入场；Target1=`0.5–1R`平50%，余仓BE。
- 出现上下双方double与连续failure时切triangle/range mode，减少反手仓位。
- Strong breakout pullback后才恢复swing。

### REVERSALS-C09-S17：Trap-Fuel Position Sizing

- 类型：failure强度/仓位组件。
- 依据，PDF p.239：原trade若已实现scalp并将余仓移BE，后续原stop failure可供驱动的被困者更少。
- 估算仍未退出比例：由是否达scalp target、partial schedule与breakeven stop位置确定。
- `trap_fuel < 0.25–0.50`时反向size降至25–50%或跳过；full-stop failure可正常size。
- 只用可复现标准订单方案估算，不声称观察到真实全市场持仓。

### REVERSALS-C09-N01：每个 Pattern 都会失败

- 类型：`NEGATIVE`治理约束。
- 依据，PDF p.238–244：没有形态保证成功，failure约束是正常交易成本而非异常。
- 禁止为“完美setup”删除stop或放宽risk；每类必须有明确failure path。
- 样本报告所有触发候选，不能只选反向成功者。

### REVERSALS-C09-N02：Trading Range Fade 不可用于 Strong Breakout

- 类型：`NEGATIVE`硬否决。
- 依据，PDF p.242、245–252：range breakout多失败，但strong trend中应顺breakout；momentum过强需等pullback。
- Strong close+follow-through/Always-In flip时S03/S06交易数为零。
- 只在break失败后重新开放fade。

### REVERSALS-C09-N03：High/Low 1–2 不是脱离 Context 的 Signal

- 类型：`NEGATIVE`。
- 依据，PDF p.246–247、253–258：range顶部H2、barbwire、旧trend已反转后的H2可能是trap；形态编号本身不够。
- 每个H/L signal必须通过regime、location、momentum与EV gate。
- Outside bar/barbwire breakout默认禁用或要求second entry。

### REVERSALS-C09-N04：Target Touch 不等于 Fill

- 类型：`NEGATIVE`执行约束。
- 依据，PDF p.242–244、248–260：limit价被触及通常仍需多一档成交，假设touch fill会消除本章failure现象。
- OHLC主结果要求穿越1tick；L2/tape按queue模拟；partial fill按实际qty。
- 未成交target不得记利润，必须继续模拟持仓与退出。

### REVERSALS-C09-N05：固定 Tick/Cent Failure 不可跨市场照搬

- 类型：`NEGATIVE`参数约束。
- 依据，PDF p.240–244：Emini 5/9/17ticks、股票金额取决于波动、spread和惯常scalp行为。
- 同时用ATR、R、spread multiples和rolling MFE分位数实现。
- 作者数字仅作参数起点，不作标签或已验证edge。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 238–244 | failure定义与清单、trap fuel、signal/entry stops、one-tick、stop tests、target failures、trend-line spike | S01–S14、S17、N01、N04–N05 |
| 245–248 | Figure 9.1–9.3：range小假突破、各种one-tick traps、bar stops穿越/未穿越 | S02–S06、S10、N02–N03 |
| 248–249 | Figure 9.4：5/9/13/17/21tick target failures与trailing处理 | S07–S09、N04–N05 |
| 249–252 | Figure 9.5–9.7：two-sided range breakout fades、second entries、small-day假break | S03、S06、N02 |
| 252–256 | Figure 9.8–9.11：stop-run recovery、first-hour doubles、failed DB/H&S measured moves | S05、S10–S11、S16、N03 |
| 256–260 | Figure 9.12–9.15：two-leg test、barbwire failure、five-tick failure与缩target | S07–S09、S15、N03–N05 |
| 260–263 | Figure 9.16–9.18：强趋势bear spikes失败、failure作为urgency/strength | S10、S12–S13 |
| 263–264 | Figure 9.19：magnet near miss、pullback后再测及higher-timeframe临时trap | S14、N05 |

## 4. 回测验收

- 每个原setup在entry前冻结goal、invalidation和horizon；failure标签不得由事后主观目标生成。
- 原trade、failure、reverse、second signal与reentry共享episode ID，逐笔P&L及累计risk均报告。
- Touch-as-fill与穿越1tick保守模型并列，主结论使用保守/L2 queue结果。
- 分开报告full-trap、partial-scalp trap、stop-miss、stop-run recovery和target near-miss。
- Range-fade、trend-failure、magnet-retest与opposite-scalp在regime上设互斥测试。
- 报告净EV、MAE/MFE、failure后两腿比例、trap-fuel分层与执行slippage。
- 固定tick/cent、目标缩放与窗口做walk-forward、跨品种/周期/volatility sensitivity。
- Figure 9.1–9.19仅作章节例证，不作参数拟合或绩效证据。
