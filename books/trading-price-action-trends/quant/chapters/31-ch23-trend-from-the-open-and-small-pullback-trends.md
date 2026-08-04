# 第 23 章：开盘即趋势与小回调趋势

## 元数据

- 英文来源：`books/trading-price-action-trends/en/chapters/31-ch23-trend-from-the-open-and-small-pullback-trends.md`
- PDF 页码：415–446
- 图表：Figure 23.1–23.11；正文与图注已逐bar完整说明，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 实时日型定义

```text
gap_ratio = abs(session_open - prior_close) / ADR20
opening_range_ratio = range(first N bars) / ADR20
distance_from_open = abs(close - session_open) / ADR20
pullback_size = countertrend distance from running trend extreme
pullback_ratio = pullback_size / ADR20
```

- `TREND_FROM_OPEN_CANDIDATE`：前1–5bars形成日内一侧极值，价格随后持续远离open，Always-In方向明确。
- `OPENING_SPIKE`：至少2根大trend bars，或4根以上无有效pullback的同向推进；净位移 `0.75–3ATR`（`AUTHOR` + `PROXY`）。
- `SMALL_PULLBACK_TREND`：趋势确立后的所有有效回调主要小于 `0.10–0.30ADR20`，且价格持续在EMA同一侧。
- 首回调必须在opening spike/第一趋势腿之后；spike内部的短pause不应事后误标为首回调。
- 日型标签只在条件首次满足时生效；“open/close接近日极值”只能用于事后评估。

## 2. 规则卡

### TRENDS-C23-S01：开盘即趋势的早期确认

- 类型：市场状态组件。
- 依据，PDF p.415–419：趋势日的一侧极值常在前几bar形成；前4bars以上无回调或2根大trend bars构成强spike，显著提高开盘即趋势概率。
- 评分特征：opening spike强度、首1–5bars的同向高低点、EMA单边、突破昨日/开盘range、距open持续扩大、逆向跟进缺失。
- 初测：至少4/6项成立且Always-In一致时确认；阈值为`PROXY`。
- 确认后只启用顺势S03–S07；普通逆势signal转S08失败候选。
- 若强反向spike越过opening range另一侧，取消原标签并重新分类，不锁定首个观点。
- 事后报告首次确认时间、日内极值是否已形成及方向正确率。

### TRENDS-C23-S02：小 Opening Range 的 Breakout Mode

- 类型：开盘突破策略。
- 依据，PDF p.415–418、443–445：opening range小于约25% ADR时可能先形成double top/bottom再出现强趋势；约50% ADR更像trending trading range。
- Setup：前 `3–10bars` range≤ `0.20–0.30ADR20`，出现两侧测试或double top/bottom。
- 入场：range外1tick stop；方向压力明确时允许较高评分，但保留反向可能。
- 传统stop-and-reverse模型与“先交易range边缘反转、失败后反手”模型分别测试。
- 止损：range另一侧或触发结构外；反手订单大小只需平旧仓并建立正常新仓，不能机械double后超过风险预算。
- 目标：range高度 `1/2/3×`、ADR扩张、1R/2R。
- 若range约 `0.40–0.60ADR`，转第22章模型，不假设small-pullback day。

### TRENDS-C23-S03：Opening Spike 的第一次 Pullback

- 类型：完整顺势策略。
- 依据，PDF p.415、419–420、422–424、436–437：开盘趋势持续3bars以上后，第一次pullback通常至少提供scalp；强移动通常有第二腿并测试旧极值。
- Setup：S01 opening spike确认；出现首次价格回撤或首次明确sideways pause。
- sideways pause也算pullback：连续 `1–5bars` 净逆向位移小，但突破前进停滞。
- 触发：High/Low 1、micro-channel失败、EMA前提前反转、或pause顺势突破。
- 入场：signal bar外stop；激进版在prior bar不利极值limit。
- 止损：pullback极值外或spike起点，按结构距离缩仓。
- 目标：spike极值、第一腿等幅、1R/2R；至少持有部分仓位期待第二腿。
- 失效：pullback形成反向spike、翻转Always-In，或演化为长时间range。

### TRENDS-C23-S04：Small Pullback Trend 检测

- 类型：强趋势状态组件。
- 依据，PDF p.416–418、424–428：所有回调小于约ADR的20–30%，且持续同样大小或缩小时，是最强趋势类型。
- 从S01确认时起在线保存每个pullback的深度、持续bars、是否触EMA及是否破主要trend line。
- 严格候选：至少3个已完成pullbacks，最大深度≤ `0.20–0.30ADR20`，中位持续≤ `3–5bars`，EMA反侧连续收盘<2。
- 早期候选：仅1–2个回调时使用低置信度标签，不得用后续小回调回填早期信号。
- pullback深度相对第一/此前最大回调的比例也要输出，避免ADR regime变化掩盖结构。
- 状态成立后，弱顺势signal不能单独降级，逆向trend bars也不能单独判反转。

### TRENDS-C23-S05：按既有回调尺度的顺势 Limit Entry

- 类型：高级limit策略。
- 依据，PDF p.417–420、424–427：若此前最大回调很小，交易者会在最近极值下/上按既有pullback尺度挂单，并在prior bar极值附近持续顺势参与。
- 仅在S04确认或早期分数≥0.75时启用。
- 参考距离：过去 `3–10` 个pullback深度的 `0.6–1.2×median`，同时限制在 `0.05–0.25ADR`。
- 其他limit：prior bar low/high、其外1–2ticks、EMA顺势侧。
- 止损：最近结构swing或opening spike起点；不得把stop压进历史回调正常噪声。
- 目标：趋势新极值、1R/2R，余仓按S09管理。
- 成交模型必须包含触价不一定成交、滑点和未成交后追价成本。

### TRENDS-C23-S06：第一次主要 Trend-Line Break 后的第二腿

- 类型：顺势延续策略。
- 依据，PDF p.419–420、428：趋势有惯性，第一次结束尝试通常失败；首次有意义trend-line break和较大回调后，通常仍有第二趋势腿及新极值。
- Setup：S01/S04趋势已确认，第一次收盘突破至少连接 `10–20bars` 的主要trend line。
- 第一break只记录，不逆势；等待回调结束的higher low/lower high或第二信号。
- 入场：顺原趋势signal bar外stop。
- 止损：首次主要回调极值外。
- 目标：旧极值、第一腿 `0.5/1.0×` 投射、1R/2R。
- 新极值后降低趋势评分：首次MA gap bar/明显两侧交易可能意味着最后一腿，停止盲目追加。

### TRENDS-C23-S07：尾盘放大 Pullback 后恢复趋势

- 类型：高潮退出与顺势再入场。
- 依据，PDF p.416–418、424–425、443–445：约三分之二small-pullback days在较晚时段出现此前最大回调的150–200%，常由顺势高潮引发，随后趋势恢复至收盘。
- 时间用session fraction `0.55–0.80`，原书11:00–12:00仅为美股日盘案例。
- Setup：S04成立；出现1–2根异常大顺势bar，range/body≥近期中位数 `1.5–2.5倍`，随后反向移动。
- 原趋势仓位：高潮强势处减仓；不把高潮当新追价信号。
- 回调目标候选：此前最大pullback的 `1.5/2.0×`、EMA、两腿且约10bars。
- 再入场：第二腿结束的High/Low 2、EMA失败突破或强顺势反转。
- 止损：放大回调极值外；目标旧极值、收盘、1R/2R。
- 原文比例均需按市场/时段验证，不作为固定发生率。

### TRENDS-C23-S08：逆向 Trend Bar/Spike 失败的顺势入场

- 类型：失败形态策略。
- 依据，PDF p.416、420–426、440–442：最强趋势中有许多漂亮逆向bar和2–3bar spikes，但它们往往成为弱旗形并失败；弱顺势signal反而可成功。
- Setup：S01或S04成立；出现逆向signal/spike，但未突破主要结构且无第二次EMA反侧收盘。
- 首个逆向signal不交易；等待其entry失败或其保护性止损价被顺趋势突破。
- 入场：逆势交易者理论stop处顺势stop entry。
- 止损：逆向尝试极值外。
- 目标：趋势旧极值、1R/2R。
- 若wedge后的修正只横向不逆向，进一步提高旧趋势评分并停止寻找反转。

### TRENDS-C23-S09：结构 Stop、入场回测与延迟保本

- 类型：仓位管理组件。
- 依据，PDF p.416、420–421、440–442：tight channel常在5–10bars内回测入场价甚至略穿，过早移保本会被强趋势扫出；应在回测后再创新极值才移动stop。
- 初始stop：最近swing或交易前提失效点；固定money stop仅以ATR/ADR归一化的独立模型测试。
- 禁止因达到小幅浮盈立即移至breakeven。
- 只有“价格回测原entry zone `±0.10ATR` 后又创新趋势极值”时，才把stop移至breakeven或最新结构swing外。
- 此后每次创新趋势极值，将stop跟至最近已确认higher low/lower high外。
- 比较结构stop、固定 `0.5–2ATR` stop和过早breakeven三种完整路径。

### TRENDS-C23-S10：Gap 日首 Bar 突破与失败反手

- 类型：开盘双分支策略。
- 依据，PDF p.415–417、421–423、429–435：大gap提高趋势日概率但方向可正可反；首bar强trend bar的突破通常有跟进，若下一bars失败，可反手捕捉相反趋势。
- Setup：`gap_ratio>=0.20`，首bar body/range≥0.60、尾部总和≤0.40；阈值为`PROXY`。
- 入场A：首bar方向极值外1tick；初始仓位≤0.5，因首bar策略无条件胜率不高。
- 确认：第二bar同向follow-through或前3bars形成opening spike后补仓。
- 失败反手：价格穿越首bar另一端并形成强反向bar/突破回测时，平旧仓并按正常风险反手。
- 止损：首bar另一端或结构极值；反手后重新计算，不把首笔亏损加到第二笔风险。
- 目标：gap closure/昨日极值、opening range等幅、1R/2R。
- gap越大只提高波动与趋势先验；原文约60/40方向比例必须样本外重估。

### TRENDS-C23-S11：Opening Spike 后三种终态

- 类型：事件状态机。
- 依据，PDF p.418–420、438–439：强opening spike之后可能高潮反转、长时间tight range后趋势恢复，或最常见地转spike-and-channel。
- `REVERSAL`：spike过大、第三/四bar仍不停顿，随后反向突破opening range并Always-In翻转。
- `RESUMPTION`：spike后range持续 `10–40bars`，最终顺原方向突破。
- `SPIKE_CHANNEL`：首次pullback后较缓channel延续。
- 三分支逐bar互斥记录；未确认前按`UNRESOLVED`处理，不把最常见分支当确定事实。
- 各分支调用第21、25或反转书相应规则，本规则本身不新增入场。

### TRENDS-C23-N01：强趋势中禁止以“好看的逆势 Bar”猜顶底

- 类型：`NEGATIVE`。
- 依据，PDF p.416、420–426、430–431、440–442：逆向bar和spike会诱使初学者反复逆势，既累积亏损又错过顺势swing。
- S01/S04状态中禁止普通逆势signal；必须先有主要trend-line break、反向follow-through及第二信号。
- 单纯小stop不是正期望依据；必须同时评估胜率、目标和成本。
- 所有被过滤逆势signal保存用于反事实评估。

### TRENDS-C23-N02：新闻 Bar 未收盘前不得交易其形状

- 类型：`NEGATIVE`。
- 依据，PDF p.418、440–442：报告发布瞬间计算机具有速度优势，盘中看似巨大trend bar可能在收盘时变为doji或反转bar。
- 事件窗口 `[-1,+1] bars` 禁止用未完成bar的OHLC形状触发策略。
- 基础模型等待事件bar收盘及后续1bar确认Always-In；不依赖新闻文本或人工解释。
- 若测试tick级事件策略，必须作为独立数据集，包含真实延迟、盘口、滑点和全部发布事件，不能与本章bar策略混合。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 415–418 | TFO特征、gap概率、小回调定义与较晚放大回调 | 第1节、S01、S02、S04、S07、S10 |
| 418–421 | opening spike、三种结果、首回调、弱signal与stop | S03、S05、S08、S09、S11 |
| 422–428 | 首回调、小回调日、20-gap及首次trend-line break | S03–S09 |
| 429–435 | 首bar诱捕、反手、gap双向结果与上下文 | S08、S10、N01 |
| 436–439 | open即日极值、首回调和初始趋势反转 | S03、S10、S11 |
| 440–445 | 弱setup、结构stop、报告bar、opening double top | S02、S04、S08–S10、N02 |
| 446 | 图表延续，无新增可提取文字规则 | 已由对应图注覆盖 |

## 4. 回测验收

- S01/S04保存首次满足时点，后续成为强趋势不得回填开盘标签。
- 使用过去完整sessions计算ADR；按gap、opening-range比例和确认bar数分层。
- S03严格区分spike内部pause与第一趋势腿后的首pullback，并报告两种定义敏感性。
- S04在早期候选与3个pullback确认版之间报告信号延迟和漏失收益。
- S05使用真实limit成交；按此前pullback中位数生成价格，不能使用本次最终深度。
- S06验证首次主要trend-line break后创新极值概率及到达时间。
- S07按市场和session fraction重估“约三分之二”与1.5–2倍回调主张。
- S09比较全路径止损结果，不能用最终趋势方向替代途中被扫事实。
- S10建立gap方向/反方向、首bar成功/失败的完整2×2事件表。
- S11终态必须互斥，未完成日/缺失尾盘数据不得强行分类。
- Figure 23.1–23.11仅作章节例证，不作参数拟合或绩效证据。
