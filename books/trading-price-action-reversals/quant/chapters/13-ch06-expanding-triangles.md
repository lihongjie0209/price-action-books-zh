# 第 6 章：Expanding Triangles

## 元数据

- 英文来源：`books/trading-price-action-reversals/en/chapters/13-ch06-expanding-triangles.md`
- PDF 页码：202–206
- 图表：Figure 6.1–6.3；正文与图注已完整说明规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Expanding Triangle 状态

```text
swings = alternating pivots [p1..pN], N in {5,7,9}
upper_i > upper_{i-1} 且 lower_i < lower_{i-1}
triangle_height = latest_upper - latest_lower
```

- 核心是交替的新高与新低不断困住breakout traders，不要求视觉上像三角形或精确触线。
- 5 swings最常见，7次有时出现，9次少见；每增加两腿是在原range上扩张而非新模式。
- Pattern既可反转也可延续，最终须由对侧breakout及follow-through决定。

## 2. 规则卡

### REVERSALS-C06-S01：Online Expanding-Swing Detector

- 类型：形态检测。
- 依据，PDF p.202–203：至少5个交替swings，每个高点更高、低点更低，构成扩张range与三推变体。
- Pivot strength=`1–3bars`；新极值须超前一同类pivot至少`1tick / 0.02–0.10ATR`。
- 允许一端near-miss≤`0.10–0.20ATR`，但记录`shape_quality`降级。
- 保存5/7/9-leg候选及各pivot确认时间；不能以未来leg修改早期可用状态。

### REVERSALS-C06-S02：Five-Leg Reversal Entry

- 类型：反转主策略。
- 依据，PDF p.202–205：旧趋势末端完成第五leg时，最终新低/高是第三push和breakout pullback，可形成MTR反转。
- Bottom：此前bear trend，leg5为lower low并出现bull reversal；top镜像。
- Entry在signal触发；stop在leg5 extreme外`1tick–0.15ATR`。
- 第一目标对侧latest swing；至少保留部分仓位到two legs/strong breakout。

### REVERSALS-C06-S03：Second-Entry in Barbwire / Weak Signal

- 类型：反转确认。
- 依据，PDF p.204–206：第五/第七leg位于barbwire、signal弱或旧趋势强时，first setup易失败，应等待second signal/HL/LH。
- Overlap≥70%、doji占比高或signal body<35%时，首signal只shadow。
- Second entry窗口`2–10bars`，需新方向signal或failed old-direction breakout。
- 时间间隔过长、pattern influence衰减时重分类为double bottom/top或普通MTR。

### REVERSALS-C06-S04：Opposite-Side Initial Target

- 类型：目标组件。
- 依据，PDF p.202–206：反转entry第一目标是突破triangle对侧，市场常在那里再次反转。
- Bottom target=`latest_upper + 0–0.10ATR`；top镜像。
- 接近目标平`50–100%`；只有strong close+follow-through才保留measured runner。
- 对侧breakout前边界必须冻结，不能随新leg扩张目标。

### REVERSALS-C06-S05：Successful Breakout Measured Move

- 类型：扩张range breakout策略。
- 依据，PDF p.202：对侧breakout成功后，下一目标约等于triangle最后一leg/高度的measured move。
- Strong breakout：body≥60%、close near extreme、`1–2bars` follow-through。
- Entry在breakout/first pullback；target测试`0.75–1.25 * last_leg`及full height版本。
- Breakout失败立即退出并交S06/S07，不假设必达测量目标。

### REVERSALS-C06-S06：Reversal-to-Continuation Flip

- 类型：形态角色切换。
- 依据，PDF p.202–205：反转trade到对侧后若breakout失败并转回旧趋势，原triangle成为旧趋势continuation flag。
- 原反转方向突破后`1–5bars`收回range且形成old-trend strong signal，标记flip。
- 在failed breakout/first pullback顺旧趋势入场；目标新旧趋势极值及last-leg measured move。
- 原反转与continuation共享episode但P&L分别记录。

### REVERSALS-C06-S07：Continuation Failure Expands to Seven/Nine Legs

- 类型：形态递归状态。
- 依据，PDF p.202–206：continuation侧再失败会把5-leg扩展为7-leg，随后可到9-leg或更大range。
- 每次对侧failed breakout新增2个alternating legs；超过9腿转`large_trading_range`而非无限计数。
- 第7/9 leg重新通过S02/S03；shape与时间比例差时降低score。
- 最终strong breakout交S05，禁止在range中部预测最后方向。

### REVERSALS-C06-S08：Expanding Triangle as MTR Context

- 类型：结构共振。
- 依据，PDF p.203：最终反转总在一段强leg之后，前一反向rally/selloff已突破某条重要trend line，因此是lower-low/higher-high MTR变体。
- 至少要求leg3/4反向move突破局部旧趋势线；若同时越EMA/major line则加分。
- S02 signal与MTR strength score共同决定swing fraction，不重复生成独立交易。
- 无反向strength时只按range scalp或等待S03。

### REVERSALS-C06-S09：Post-Completion Opposite Triangle Candidate

- 类型：连续形态管理。
- 依据，PDF p.203–205：一个反转expanding triangle完成目标后，常尝试形成相反方向的continuation triangle，反之亦然。
- 到S04目标后保留原pivot序列，若新增extreme使相反5-leg序列成立则生成新candidate。
- 新candidate仍独立通过regime、signal和EV；不能因历史模式自动反手。
- 使用linked episode ID评估频繁反转成本与重复暴露。

### REVERSALS-C06-S10：Range-Leg Scalp then Swing Transition

- 类型：持仓期限切换。
- 依据，PDF p.204–205：前几leg各为range新极值，可scalp；第五leg完成后可能发展较大趋势，应swing部分。
- Legs1–4只在range edge以`0.5–1R`目标scalp；leg5+合格S02后保留`25–50%`到S04/S05。
- Strong trend背景下逆势leg scalp须更高门槛；barbwire由S03过滤。
- 同一leg不得同时作为scalp与swing两笔完整仓位重复计风险。

### REVERSALS-C06-S11：Shape / Proportionality Quality Score

- 类型：形态可信度。
- 依据，PDF p.203–206：不必完美或触line，但极端不成比例、leg间距差异过大时较少交易者信任，模式变弱。
- 计算相邻leg bar-count ratio、amplitude growth与line residual；建议quality区间`0–1`。
- 任一time-spacing ratio>`3–5倍`或多次near-miss使score下降，但不硬删除有其他range/level理由的setup。
- Shape只作增量特征，不能覆盖明确price-action breakout。

### REVERSALS-C06-N01：Triangle 名称与完美外形不是入场条件

- 类型：`NEGATIVE`模型约束。
- 依据，PDF p.202–204：模式常不像三角形，也不必接触channel lines；关键是更高高点、更低低点与陷阱。
- 不使用人工视觉标签作唯一特征；以可审计pivots和breakouts实现。
- 不因轻微near-miss删除样本，也不事后移动line制造完美形状。

### REVERSALS-C06-N02：Strong New Trend 中不抢第一次反向 Setup

- 类型：`NEGATIVE`。
- 依据，PDF p.205：强bull momentum下triangle top的first short/second entry仍可能只是breakout pullback；无先前trend-line break不应short。
- Strong breakout状态未出现bear/bull strength前，逆势实际交易数为零。
- 等LH/HL与trend-line break，或按S05顺新趋势。

### REVERSALS-C06-N03：固定 Tick 与 Leg Count 不作普适常数

- 类型：`NEGATIVE`参数约束。
- 依据，PDF p.202–206：一tick failure及5/7/9 legs受品种tick和实时结构影响。
- Breakout距离按tick、ATR和spread归一化；leg count作为分类而非成功保证。
- SPY/Emini案例差异不得外推为固定fill或signal质量。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 202–203 | 5/7/9 swings、交替新极值、traps、反转/continuation切换与measured targets | S01–S09、N01 |
| 203–204 | MTR变体、Figure 6.1反转后bear flag、两腿与不完美形态 | S06–S09、S11、N01 |
| 204–205 | Figure 6.2第五/第七leg、barbwire second entry、scalp转swing及强趋势反例 | S02–S04、S07、S10、N02–N03 |
| 205–206 | Figure 6.3 second chance衰减、double bottom、目标后反向triangle与比例质量 | S03–S07、S09、S11 |

## 4. 回测验收

- 所有pivot、leg和边界带确认时间；同时保留5/7/9-leg候选，未来重画次数为零。
- 反转、continuation flip、expanded triangle与large range结果全部报告，不能只筛最终趋势。
- S02–S10共享triangle episode ID；range scalp、reversal swing和flip trade按实际风险分别核算。
- Conservative OHLC fill要求穿越1tick；不同tick品种以ATR/spread版本复核。
- 报告各leg count/shape quality的样本数、净EV、MAE/MFE、对侧到达率和measured move完成率。
- Strong-trend逆势、barbwire首signal及无trend strength反转设自动测试。
- 参数做walk-forward、跨品种/周期/volatility sensitivity。
- Figure 6.1–6.3仅作章节例证，不作参数或绩效证据。
