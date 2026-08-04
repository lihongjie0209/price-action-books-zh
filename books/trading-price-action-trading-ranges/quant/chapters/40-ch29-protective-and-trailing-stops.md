# 第 29 章：Protective and Trailing Stops

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/40-ch29-protective-and-trailing-stops.md`
- PDF 页码：565–586
- 图表：Figure 29.1–29.5；正文与图注已完整说明规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Stop 状态与风险模型

```text
initial_risk = abs(entry_price - initial_stop) + expected_cost
qty = floor(account_risk_budget / (initial_risk * point_value))
stop_state = INITIAL | TIGHTENED | BREAKEVEN | SWING_TRAIL | EXITED
```

- 每笔真实持仓必须在成交同时提交服务器端保护止损；保存`stop_price, valid_from, reason, replaced_stop`。
- 止损只能收紧或由策略退出取代，不得因浮亏放宽；宽止损通过减仓保持固定账户风险。
- Price-action stop位于使交易前提失效的结构之外；money-management stop由最大可承受风险决定。两者冲突时，若结构stop超预算则缩仓或放弃，不把止损放在随机位置。
- 固定8–14 tick等书中示例仅作原市场说明；实现同时用tick、ATR/ADR与结构距离归一化。

## 2. 规则卡

### RANGES-C29-S01：强制 Working Protective Stop

- 类型：组合级风险约束。
- 依据，PDF p.565–567：每笔交易必须始终有实际working stop；mental stop在快速行情、断线或犹豫时不可靠。
- Entry fill确认后同一事件周期提交stop；无保护状态容忍≤一个订单往返延迟。
- Stop拒单、断连或剩余qty不匹配时，优先重提；超过预设超时则marketable exit。
- 回测加入stop slippage和gap-through，不假设总能按stop价成交。

### RANGES-C29-S02：Signal-Bar / Structure Initial Stop

- 类型：初始止损组件。
- 依据，PDF p.565–572、574–578：通常把stop放在signal bar或使setup失效的swing另一侧一tick。
- Long stop=`min(signal.low, invalidation_swing.low)-buffer`；short镜像。
- Buffer候选=`max(1tick, 0.05–0.15ATR)`；若bar特别大，交S03。
- Entry、stop与qty必须在signal close后、下单前冻结，禁止事后选更有利结构。

### RANGES-C29-S03：Large-Bar Money-Management Stop

- 类型：大信号bar风险适配。
- 依据，PDF p.568–570、574：signal bar过大时，可用约其range的60–70%作为money stop；安静pullback仍可用常规money stop。
- Large bar=`range >= 1.5–2.0 * rolling_median_range`；候选风险=`0.60–0.70 * signal_range`。
- 只有候选stop仍位于合理微结构之外才交易；否则缩仓采用完整结构stop或跳过。
- 对`0.5–1.0 signal range`和`0.5–1.5ATR`做敏感性测试，不把60–70%当普适常数。

### RANGES-C29-S04：Strong Entry-Bar Tightening

- 类型：早期止损收紧。
- 依据，PDF p.567–569、574–578、585–586：强entry bar及明确follow-through后，可把stop移到entry bar另一侧；doji不能触发。
- Strong entry bar：方向body≥60–70%、close位于末端20–25%、range≥rolling median，且下一bar没有强反转。
- Long新stop=`entry_bar.low-buffer`；short镜像，且只能改善原stop。
- 可选确认延迟`0–1bar`；用净EV比较立即收紧、follow-through后收紧和保持原stop。

### RANGES-C29-S05：Doji / One-Bar Range 保持原 Stop

- 类型：短期噪声过滤。
- 依据，PDF p.567–569、578、585–586：入场后数bar内的小doji是一bar区间，常被穿越1–2ticks；前提未失效时不应据此收紧。
- Entry后前`1–3bars`若body/range≤25–35%且无结构破坏，维持S02 stop。
- 不把stop移到doji另一侧，也不因单次微小反向突破退出。
- 若出现strong opposite bar或原setup失效，交S09而不是机械等待stop。

### RANGES-C29-S06：Swing-Low / Swing-High Trailing

- 类型：趋势swing跟踪止损。
- 依据，PDF p.565–568、570–573、579–581、583：swing trader容忍pullback；创新高后把long stop移到最近已确认swing low下，short镜像。
- Swing确认只能使用当时已有右侧bars；默认pivot strength `1–3bars`。
- Long仅在`new swing high`后更新到最近higher low下；short仅在new swing low后更新。
- Strong channel预期会多次回撤，禁止按每根bar或未确认pivot跟踪。

### RANGES-C29-S07：Trend 转 Range 的主动获利退出

- 类型：regime切换退出。
- 依据，PDF p.566–568、571、579–581：climax后若预计形成range，旧swing lows/highs很可能被穿越，应在range顶部/底部强势退出而非等stop。
- 转换候选：第三推、连续climax、两bar反转、达到measured move后失去follow-through。
- Long在潜在range上沿/反转signal退出；short镜像；之后切换scalp/range模型。
- 与S06互斥：一旦实时range概率越过阈值`0.55–0.65`，取消旧trend trail并主动平仓。

### RANGES-C29-S08：Wide Stop + Fixed-Risk Sizing

- 类型：仓位管理组件。
- 依据，PDF p.566–574、576–580、582：spike、weak channel scale-in、stairs、final flag和climax reversal可能需要宽stop，代价是更小仓位。
- Wide stop候选：结构外、`0.5–0.75 ADR`上限研究区间，或普通scalp risk的`2–3倍`。
- `qty`严格按initial risk反比缩放；最小可交易qty仍超预算则跳过。
- 单独报告gap loss、MAE、尾部损失和宽/窄stop的机会成本。

### RANGES-C29-S09：Premise / Flat-Test Exit

- 类型：前提失效退出。
- 依据，PDF p.569–570、572–573、582–583：如果当前空仓不会在此价格重入同方向，则继续持有缺乏依据，应退出并寻找下一笔。
- 每bar用原setup特征重新计算`entry_eligible_now`，但不使用未来信息。
- 强反向spike、预期突破未发生、趋势反转为channel或目标显著下降时触发marketable exit。
- 轻微正常pullback与doji由S05/S06保护，避免把flat test实现成逐bar过拟合退出器。

### RANGES-C29-S10：Stop Hit 后的条件反手

- 类型：失败突破反手策略。
- 依据，PDF p.569–570、574–578：某些reversal/Low2失败会表明相反方向更强，可在原stop附近反手；tight range中不适用。
- 仅当原stop hit同时构成strong breakout、Always-In flip或独立相反signal；新交易重算stop、qty和EV。
- 原交易与反手共享failure event ID，但P&L分别记录；禁止用反手掩盖原亏损。
- Tight trading range、barbwire或双向假突破率高时禁用。

### RANGES-C29-S11：Breakeven Stop 的目标进度条件

- 类型：目标式持仓保护。
- 依据，PDF p.581–583、585：使用固定profit target者，价格到目标约一半后可把stop移到不差于breakeven；强entry bar也可提前允许。
- 触发=`MFE >= 0.5 * target_distance`或S04成立；BE=`entry + costs + 0–1tick`。
- 目标必须入场前固定；未达到触发前不能利用未来最高/最低价决定。
- 比较0.33、0.50、0.67进度，报告被BE退出后最终到目标的比例。

### RANGES-C29-S12：Risk-Equals-Reward Profit Reference

- 类型：动态目标研究方案。
- 依据，PDF p.570、581–583：市场在形成可识别pullback后，后续move常接近交易实际必须承受的risk；示例用risk少一tick获利。
- 在pullback完成且stop收紧后冻结`realized_required_risk = entry - validated_swing`，目标=`entry ± (risk-buffer)`。
- 仅在range底/顶或至少约60%成功概率的高质量context测试，不作为无条件规律。
- 与固定1R、2R和结构目标比较；严格区分入场前可知risk与事后MAE，后者只作分析。

### RANGES-C29-S13：First-Trade Stop Calibration

- 类型：日内波动校准方案。
- 依据，PDF p.570–571、583–585：首笔有效setup在顺向前的最大逆行可提示当日最小stop；bar变小时可调整，但日后仍可能再需较宽stop。
- 只用已完成的首个合格事件MAE加1tick生成`day_stop_floor`，从其完成后生效。
- Floor按`0.25–1.0ATR`截尾并随rolling bar range衰减；不能回填到早先交易。
- 与纯ATR stop比较；样本需按开盘gap、news和volatility regime分层，避免单日偶然值支配。

### RANGES-C29-S14：Timeframe-Consistent Stop

- 类型：多周期治理约束。
- 依据，PDF p.574–578：基于5分钟setup的交易不能因1分钟噪声把stop放到过近位置。
- Stop结构、失效条件与signal timeframe一致；低周期仅用于成交，不得改变风险逻辑。
- 若使用低周期确认，必须预注册且同样本比较，不得看到逆行后临时切周期。
- 报告不同bar aggregation下的stop-out率与最终目标到达率。

### RANGES-C29-S15：Climax 后分批获利与 Swing 保留

- 类型：混合持仓退出。
- 依据，PDF p.579–581、585：长趋势第三推/两bar climax后，部分交易者获利，余仓等待新极值；强趋势pullback后仍常测试高/低。
- Climax确认后平`50–75%`，余仓用S06或S11；若转range条件成立则S07清仓。
- 可选退出后在低动量flag/EMA test重新入场，必须作为新交易处理。
- 比较全平、半平和纯swing，计入额外成本。

### RANGES-C29-N01：禁止 Mental Stop 与无保护持仓

- 类型：`NEGATIVE`硬约束。
- 依据，PDF p.565–567：mental stop容易因速度、希望或操作失败而不执行。
- 生产与回测的每个持仓时段必须有可审计stop/退出订单；缺口时段计为风险违规。
- 不以“密切观察”或人工值守替代保护订单。

### RANGES-C29-N02：禁止因亏损放宽 Stop

- 类型：`NEGATIVE`风险约束。
- 依据，PDF p.565–570：入场后市场证明交易较弱时不能扩大预设风险以逃避止损。
- `new_stop`必须单调降低long风险/short风险；任何放宽需先退出，再按独立新setup重入。
- Gap穿越属于执行损失，不得改写initial risk掩盖超损。

### RANGES-C29-N03：不要过早逐 Bar Trailing

- 类型：`NEGATIVE`。
- 依据，PDF p.565–568、575–581、585–586：swing需要容忍正常pullback，doji和首个小swing很容易被测试。
- S04未成立、未创新极值或pivot未确认时，禁止移动到最近一bar之外。
- Strong trend/channel和预期two-legged correction中用S06/S15，不用机械one-bar trail。

### RANGES-C29-N04：不存在针对个人订单的 Stop Run 信号

- 类型：`NEGATIVE`建模约束。
- 依据，PDF p.573–574、584：市场测试明显价位与一tick穿越常见，但机构并非在追踪某个个人stop。
- 只建模公开结构、流动性与stop clustering，不使用不可观察的“有人看到我的订单”变量。
- One-tick overshoot可进入buffer敏感性测试，不能成为报复性重入理由。

### RANGES-C29-N05：固定 Tick Stop 不可跨市场照搬

- 类型：`NEGATIVE`参数约束。
- 依据，PDF p.568–571、574、583–585：8、9、14ticks等取决于当时E-mini波动、bar大小和setup。
- 所有固定值必须同时按tick size、ATR、ADR、spread和结构归一化。
- 参数选择只用训练期；Figure 29.1–29.5中的精确距离不得当成优化标签。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 565–570 | working stop、price-action与money stop、强entry/doji、宽stop、flat test与反手 | S01–S10、N01–N03 |
| 570–574 | 所需risk与reward、首小时校准、spike/channel宽stop、公开stop位 | S08、S12–S13、N04–N05 |
| 574–578 | Figure 29.1：signal/entry stop、周期一致、失败setup与反手 | S02–S05、S10、S14 |
| 579–581 | Figure 29.2：swing trailing、climax、trend转range、分批获利 | S06–S07、S15、N03 |
| 581–583 | Figure 29.3：risk≈reward、breakeven、premise变化与2R目标 | S09、S11–S12 |
| 583–586 | Figure 29.4–29.5：日内stop校准、doji不早收紧、强bar后收紧 | S04–S05、S13、N04–N05 |

## 4. 回测验收

- 每次stop新增/替换/撤销均有时间戳；同bar OHLC无法判定先后时采用不利成交顺序并另报上下界。
- Initial stop、目标、pivot、regime与climax只使用当时数据，未来重画和事后MAE设目标的次数必须为零。
- S02–S15是同一持仓的状态组件或退出分支，需共享trade/event ID，不能重复计为独立盈利机会。
- 分别报告stop-out率、MAE/MFE、退出后目标到达率、slippage、gap loss、净EV及尾部风险。
- 宽stop实验保持账户risk一致；禁止用不同仓位风险比较表面胜率。
- Strong entry、doji、swing、range transition等阈值做walk-forward和跨品种敏感性测试。
- Stop-hit反手必须计双份成本并在tight range中通过零交易硬测试。
- Mental-stop、stop widening、跨周期临时收紧与不可观察personal stop-run特征均设自动违规检查。
- Figure 29.1–29.5仅作规则例证，不作参数拟合或绩效证据。
