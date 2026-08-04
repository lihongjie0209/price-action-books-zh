# 第 1 章：Example of How to Trade a Reversal

## 元数据

- 英文来源：`books/trading-price-action-reversals/en/chapters/08-ch01-example-of-how-to-trade-a-reversal.md`
- PDF 页码：102–107
- 图表：Figure 1.1；正文与图注已完整说明规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Major Reversal 状态机

```text
OLD_TREND
  -> SIGNIFICANT_TRENDLINE_BREAK
  -> EXTREME_TEST
  -> REVERSAL_SIGNAL
  -> ALWAYS_IN_FLIP / FAILED_REVERSAL
```

- Reversal目标是足以形成swing或相反趋势的move，不是普通逆势scalp。
- 趋势线、极值、signal、stop与目标均须实时冻结；不能用日终图形反画。
- 初始成功率可能≤50%，但可由数倍于risk的reward形成正EV；书中60%与价格距离仅是单一案例。

## 2. 规则卡

### REVERSALS-C01-S01：Significant Trend-Line Break Gate

- 类型：major reversal前置门控。
- 依据，PDF p.102–104：没有先显著突破旧趋势线，不做major reversal；一bar浅回调、未触EMA的break不够。
- Break强度候选：穿线≥`0.20–0.50ATR`、持续≥2–3bars、到达/穿越EMA，并含至少2根方向trend bars。
- Trend line anchors只用break前已确认swings；保存`valid_from`。
- 未过门槛的countertrend signal仅记minor reversal shadow样本。

### REVERSALS-C01-S02：Extreme-Test Lower-High / Higher-Low Entry

- 类型：major trend reversal主策略。
- 依据，PDF p.102–105：强break后等待旧趋势极值测试，在lower high/double top/higher high处出现强bear signal入场；底部镜像。
- Test窗口=`0–0.30ATR`围绕旧extreme；允许lower high、double top或小幅overshoot。
- 需合格reversal bar、second entry或two-bar reversal；stop在test extreme外。
- 第一目标break leg低/高，第二目标measured move或相反趋势runner。

### REVERSALS-C01-S03：Wedge / Two-Leg Test Confluence

- 类型：反转加分组件。
- 依据，PDF p.103–105：旧趋势第三推、测试中的两腿/三腿与double top bear flag增加双向交易和反转概率。
- 特征：old-trend push count≥3、test leg count≥2，或retest形成wedge flag。
- 每项只提高setup score，不单独生成entry；至少仍须S01与S02。
- Push/leg使用在线pivot确认，参数`1–3bars`敏感性测试。

### REVERSALS-C01-S04：Always-In Flip Confirmation

- 类型：状态确认与加仓。
- 依据，PDF p.104–106：多bar bear spike穿越trend line与EMA后，多数交易者会认定Always-In转空；反弹不能越spike起点则bears仍控制。
- Flip候选：连续`3–5bars`方向spike、累计≥`1.5ATR`、EMA穿越且close保持另一侧。
- Flip后允许在weak pullback/retest追加，stop在spike start或lower high外。
- Pullback强穿spike start则取消bear premise；bull镜像。

### REVERSALS-C01-S05：Early Wedge Reversal Swing Management

- 类型：较早反转入场管理。
- 依据，PDF p.103–104：第三推后的second-entry可提前入场，但最初可能只是两腿修正到channel start；swing trader应容忍pullback。
- Early entry仅在S01基本break pressure已出现、wedge/second entry成立时半仓运行。
- Stop保持signal/strong entry bar外，不按每bar收紧；预期至少two legs correction。
- 到channel start/double-bottom区域评估获利；若随后形成S02强retest，可重新入场。

### REVERSALS-C01-S06：Weak Retest Reentry

- 类型：退出后的二次反转入场。
- 依据，PDF p.104–105：完成两腿修正后若反弹测试旧高但缺少连续强bull bars，可在wedge bear flag/double top/lower high再次short。
- Retest rally不能含连续2根强旧趋势bars；其momentum小于先前break leg。
- Entry在reversal signal下/上；stop在retest extreme或break-spike start外。
- 与S02共享reversal episode，分别报告early与reentry结果。

### REVERSALS-C01-S07：Breakout-Level Minimum Target

- 类型：结构目标组件。
- 依据，PDF p.105–106：lower-high short最低预期测试先前break low；若穿越关键higher low，可按double top/range高度measured move延伸。
- Target1=`prior break extreme`前`1tick–0.10ATR`；无pause强穿则保留更多仓位。
- Target2=`breakout_level ± pattern_height`，高度在breakout前冻结。
- 前方空间不足成本后1R则拒单，即使反转形态成立。

### REVERSALS-C01-S08：Pause/Climax Scale-Out and Runner

- 类型：反转趋势获利管理。
- 依据，PDF p.105–106：强反转trend中可press；无pause时不急于获利，在sell climax+final flag后的pause减半，余仓到收盘。
- 无pause且trend score强时用swing trail；首个climax pause平`40–60%`。
- Runner在strong opposite signal或session close退出；gap overnight需独立授权。
- 比较固定1R/2R、结构退出和pause-based方案的净EV与回撤。

### REVERSALS-C01-S09：Third Buy-Climax Two-Leg Correction

- 类型：非major reversal的climax scalp/swing。
- 依据，PDF p.106–107：连续第三次buy climax后的large bull bar更可能是exhaustion gap，预期至少两腿修正到EMA下；bear镜像。
- Climax count≥3且之间无显著pullback；末bar range≥`1.5 median`并位于延伸趋势末端。
- 可在close/高点/随后bear confirmation分档退出long或建立小short；stop小于完整climax range需独立测试。
- 目标EMA及two-leg completion；只有后续S02测试成立才升级为major reversal。

### REVERSALS-C01-S10：Fixed-Risk Wide-Stop Entry

- 类型：仓位适配组件。
- 依据，PDF p.102：反转follow-through常为快速大spike，pullback entry可能需平常2–3倍ticks风险；应缩仓保持美元风险不变。
- Stop必须位于结构失效处；`qty=floor(account_risk/(stop_distance+cost))`。
- 若最小qty仍超预算则跳过，不因害怕宽tick stop改用噪声stop。
- 报告normal/wide stop的stop-out、MAE、尾部风险和机会成本。

### REVERSALS-C01-N01：No Trend-Line Break, No Major Reversal

- 类型：`NEGATIVE`硬否决。
- 依据，PDF p.102–104：旧趋势线未显著突破时，bar 3/bar 7式反转bar不足以支持major reversal。
- S01未成立时S02/S04/S06实际交易数必须为零。
- 可做独立scalp模型，但不得与major reversal绩效混合。

### REVERSALS-C01-N02：禁止日终图形确认与情绪性追价

- 类型：`NEGATIVE`无未来函数约束。
- 依据，PDF p.102：日终反转显得明显，实时却模糊、快速且容易因先前亏损错过或追逐。
- 所有状态只在bar close/订单事件后生效；不得使用未来spike证明早先entry。
- 错过entry后只能等待预注册pullback/retest，不能因“新趋势已清晰”在临近收盘追价。

### REVERSALS-C01-N03：禁止把案例概率与金额外推

- 类型：`NEGATIVE`参数约束。
- 依据，PDF p.105–106：10美分risk、50美分reward与60%是CAT当天示例。
- 概率必须在训练/验证数据校准；价格距离转为R、ATR/ADR、tick和spread。
- Figure 1.1不得作为参数拟合或绩效证据。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 102 | reversal的低概率高reward方程、实时执行困难、宽stop缩仓与pullback | S02、S10、N02 |
| 103–104 | Figure 1.1：显著trend-line break、wedge/second entry、两腿修正、Always-In flip | S01、S03–S05、N01 |
| 104–105 | weak retest、lower high/double top、spike控制位与disappointed bulls | S02、S04、S06 |
| 105–106 | breakout/measured-move目标、press、pause/climax分批及案例方程 | S07–S08、N03 |
| 106–107 | 第三buy climax、exhaustion gap与two-legged correction | S09 |

## 4. 回测验收

- Trend line anchors、break、extreme test、push/leg、Always-In flip和目标全部有`valid_from`，未来重画次数为零。
- S01–S10共享reversal episode ID；early entry、reentry和add-on不得重复计同一move。
- 报告major reversal成功率、到Target1/2比例、MAE/MFE、净EV、失败后旧趋势恢复幅度和尾部风险。
- 低成功率策略以成本后期望和置信区间验收，不以胜率单独淘汰。
- Wide-stop与normal-stop保持相同账户risk；所有成交计slippage、gap和佣金。
- No-break禁令、前方空间门槛、临近收盘追价及未来信息设自动测试。
- 所有阈值做walk-forward、跨品种、时段与波动状态敏感性检验。
- Figure 1.1仅作章节例证，不作参数或业绩证据。
