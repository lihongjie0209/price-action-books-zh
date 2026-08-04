# 第 20 章：“反转”形态——双顶/双底与头肩顶/底

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/29-ch20-reversal-patterns-double-tops-and-bottoms-and-head-and-shoulders-tops-and-bottom.md`
- PDF 页码：348–353
- 图表：Figure 20.1–20.3；正文与图注足以定义规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 形态与先验

- Double top/bottom：两个同侧已确认swings位于 `max(2ticks, 0.10–0.30ATR)` 价格带，中间反向摆动≥`0.5ATR`。
- Head-and-shoulders top：三个高点，中间为head，左右shoulders允许不对称；neckline连接中间两个低点。Bottom镜像。
- 几何形态只是trading range/flag的描述。Bull regime中的H&S top默认按triangle/wedge bull flag处理；bear regime中的H&S bottom默认按bear flag处理。
- “大多数breakout失败”等原文定性比例不是硬编码胜率；所有先验须用目标市场样本重新估计。

## 2. 规则卡

### RANGES-C20-S01：Bull Trend 中 Head-and-Shoulders Top 作为 Bull Flag

- 类型：顺势延续策略。
- 依据，PDF p.348–352：bull趋势中的H&S top通常是横向triangle或wedge bull flag，neckline向下突破常失败，随后向上突破right shoulder。
- Setup：bull regime；三个高点/三次向下push构成H&S-like range，尚无clear bear reversal。
- 首选入场：neckline假突破后 `1–3bars` 收回，并出现bull signal；次选为right shoulder上方强breakout pullback。
- 止损：neckline假突破最终低点或完整flag低点下。
- 目标：head/形态高点、flag高度measured move、1R/2R。
- Neckline强breakout+follow-through时关闭并转S05。

### RANGES-C20-S02：Bear Trend 中 Head-and-Shoulders Bottom 作为 Bear Flag

- 类型：S01镜像顺势策略。
- 依据，PDF p.348–353：bear趋势中的H&S bottom通常是triangle/wedge bear flag，反转尝试失败后应向下突破right shoulder。
- Setup：bear regime；三个低点/三次向上push形成H&S-like range，无clear bull reversal。
- 入场：neckline向上假突破收回后卖，或right shoulder/flag下沿强breakout pullback卖。
- 止损：假突破最高点或完整flag高点上。
- 目标：旧bear low、flag高度measured move、1R/2R。
- 强bull breakout及follow-through时交给S05镜像。

### RANGES-C20-S03：Double Top/Bottom 先按 Trading Range 处理

- 类型：状态与边缘交易策略。
- 依据，PDF p.348–350：大型double top/bottom常先形成可持续很久的range；标准neckline stop entry可能多年后才触发且仍失败。
- 两次同价带测试后不立即声明major reversal；确认range边界与中点。
- Range内：顶部double top signal只取到中点/底部，底部double bottom镜像；避免在中间交易。
- 真breakout需S04 follow-through确认；失败breakout按range fade或S01/S02处理。
- 长周期样本的持有期、融资、corporate action和指数成分变动单独建模。

### RANGES-C20-S04：Neckline Breakout + Follow-through

- 类型：确认突破策略。
- 依据，PDF p.348–352：仅跌破/突破neckline不足以证明反转；经验交易者要求follow-through，否则把强breakout bar视为反向机会。
- Strong breakout：收盘越neckline≥`0.20–0.50ATR`且bar range≥`1ATR`。
- Follow-through：未来1–2根完成bar至少一根同向close，且未收回breakout的50%以上。
- 入场：follow-through close或首次breakout pullback；不得回填到neckline首次穿越。
- 止损：pullback另一侧或neckline内 `0.25–0.50ATR`。
- 目标：pattern height measured move、1R/2R；无follow-through转S06。

### RANGES-C20-S05：Continuation Pattern 真失败后的 Major Reversal 候选

- 类型：条件反转策略。
- 依据，PDF p.348–352：这些形态通常延续，只有顺趋势延续失败时才可能真正反转；需要其他反转证据并保持选择性。
- 候选条件任三项：major trend-line break、old extreme测试失败、Always-In flip、neckline强breakout+follow-through、第二入场、climax。
- 入场：breakout pullback的lower high/higher low或second reversal。
- 止损：旧趋势最终极值/右肩外。
- 目标：EMA、range对侧、pattern height、1R/2R。
- 只形成几何top/bottom而无上述证据时禁止逆势。

### RANGES-C20-S06：Neckline Breakout Failure Fade

- 类型：失败突破顺原趋势策略。
- 依据，PDF p.348、351–352：H&S top向下breakout常无follow-through，强bull在弱bear追空时买入，使形态恢复为bull flag；bear版镜像。
- Breakout触发但不满足S04 follow-through，并在 `1–3bars` 收回neckline。
- 入场：reclaim bar顺原趋势极值外stop；保守版等待第一次pullback。
- 止损：失败breakout最终极值外。
- 目标：right shoulder、head/旧极值、1R/2R。
- 与S04/S05互斥；强breakout已确认时不fade。

### RANGES-C20-S07：Right Shoulder 作为 Breakout Pullback

- 类型：结构解释与入场组件。
- 依据，PDF p.348、352–353：从head的move常突破trend line，right shoulder是lower/higher-high breakout pullback；在bear flag中可同时是两腿rally终点/MA-gap setup。
- Right shoulder必须出现在head后结构break之后，且形成lower high（top）或higher low（bottom）；允许轻微overshoot。
- 方向由regime决定：bear flag中right shoulder下破卖，bull flag中镜像买。
- 与first MA gap、Low/High 2或wedge第三推共振提高评分但不重复开仓。
- 止损置于right shoulder极值外；目标旧趋势极值、1R/2R。

### RANGES-C20-N01：不可机械交易每个 Top/Bottom

- 类型：`NEGATIVE`。
- 依据，PDF p.348、350–352：趋势持续制造反转形态，除最终一个外都失败；全做逆势会让多数交易亏损。
- 几何detector输出candidate而非order；必须先通过regime和S05反转证据。
- 不以形态名称改变方向先验；bull中的“top”默认仍偏多，bear中的“bottom”默认仍偏空。
- 报告所有candidate，包括未反转者，避免只标最终成功顶部/底部的幸存者偏差。

### RANGES-C20-N02：不硬编码“80% Breakout Failure”

- 类型：`NEGATIVE`与统计约束。
- 依据，PDF p.350的80%是书中概括，未限定标的、周期、突破定义与成本。
- 不把0.8作为策略概率或仓位输入；在每个市场按S04固定定义重新估计。
- 输出置信区间、样本数、regime/timeframe分层，并与朴素range breakout基准比较。
- 若样本外概率不同，执行以实证结果为准，同时保留原文假设字段。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 348–349 | 反转形态多为continuation、H&S是triangle/wedge flag | 定义、S01–S02、N01 |
| 349–350 | 大型double top形成range、neckline标准入场常失败 | S03–S04、N02 |
| 350–352 | top失败、H&S bull flag、breakout必须follow-through | S01、S04–S06 |
| 352–353 | bear趋势H&S bottom失败、right shoulder/MA-gap bear flag | S02、S07 |

## 4. 回测验收

- Swing、neckline、head和shoulder均保存确认时点，不能用最终形态回填早期交易。
- Bull/bear/range三类regime分别报告；几何相同但方向先验不同。
- 所有candidate进入母样本，成功反转与失败延续均保留。
- S04 breakout/follow-through阈值在训练集锁定；S04与S06事件互斥。
- S05每项反转证据只用当时已完成bar，并输出满足条件组合。
- Pattern-height目标在入场前固定，不事后选择neckline/shoulder中最优测量。
- 固定“80%”不得出现在仓位或信号代码中；用样本外估计和置信区间替代。
- Figure 20.1–20.3只作章节例证，不作参数拟合或绩效证据。
