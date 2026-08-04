# 第 22 章：趋势型交易区间日

## 元数据

- 英文来源：`books/trading-price-action-trends/en/chapters/30-ch22-trending-trading-range-days.md`
- PDF 页码：391–414
- 图表：Figure 22.1–22.10；正文与图注已逐bar说明，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 日内状态定义

```text
opening_range(N) = max(high[session_start:N]) - min(low[session_start:N])
or_ratio = opening_range / ADR20
range_overlap = mean(overlap(bar[t], bar[t-1]) / min(range[t], range[t-1]))
range_slope = robust_slope(mid_price, N) / ATR20
```

- `INITIAL_RANGE`：通常持续首 `12–36` 根5分钟bar（约1–3小时），`or_ratio≈0.33–0.50`。
- `BREAKOUT_BRIDGE`：从第一range到第二range的1–3根方向bar，通常比典型spike小、尾部和重叠更多。
- `SECOND_RANGE`：突破后连续 `5–10+bars` 高重叠、双向bar，且净斜率小。
- `TRENDING_TRADING_RANGE_DAY`：至少两个价格中枢明显错开的range，由短breakout连接。
- `SPIKE_CHANNEL_CANDIDATE`：breakout强、post-breakout pullback仅0–1bar且继续单边channel。
- `PLAIN_RANGE_DAY`：两侧突破均失败，最终价格重新围绕原range中部。

以上标签逐bar更新，不能用当日最终收盘位置回填。`ADR20`只能使用前20个完整session。

## 2. 规则卡

### TRENDS-C22-S01：初始 Range 与第二 Range 候选

- 类型：日型检测组件。
- 依据，PDF p.391–393、396–399：初始range约近期日均range的1/3–1/2，1–3小时后突破，随后常在新价位形成第二range，使当日range近似扩大一倍。
- Setup：session前 `12–36bars` 的`or_ratio=0.30–0.55`，EMA平缓且range内双向成交明显。
- breakout：收盘越过range `0.05–0.25ATR`；bridge持续1–3bars。
- 第二range确认：突破后 `5–10bars` 的净位移/路径长度≤0.35、overlap≥0.50，并出现双向trend bars。
- 输出第一/第二range边界、中点、bridge gap和确认时间。
- 若breakout后pullback短且单边延续，切换第21章spike-and-channel，不强行标为第二range。

### TRENDS-C22-S02：Range 内部倾斜对突破方向的提示

- 类型：方向评分组件。
- 依据，PDF p.394–395、409–410、413：range内若swing highs和lows同时逐步抬高/降低，趋势可能已存在；累计方向压力提示突破方向。
- 在已确认的最近 `3–5` 个swings中，bull要求higher-high率和higher-low率均≥ `0.67`；bear对称。
- 辅助特征：同向body占比、EMA斜率、同向spike数量、对侧失败突破。
- 方向分数只调整breakout先验和仓位 `0.5–1.0×`，不能取消另一方向的可能性。
- Range边界在信号前冻结；不得因真实突破位置事后重新选取更匹配的range。

### TRENDS-C22-S03：突破回测进入新价格区间

- 类型：完整顺势策略。
- 依据，PDF p.392–394、398、402–406：直接交易range breakout通常低概率；更佳选择是breakout pullback或此前从range另一侧的反转。
- Setup：S01 initial range已完成，breakout有至少1根同向trend bar和下一bar非强反转。
- 标准触发：`1–10bars` 内回测breakout point，形成顺突破方向signal；不能强收盘回到旧range深处。
- 入场：signal bar外stop。
- 止损：回测极值或旧range内侧结构位。
- 目标：第一range高度的 `0.75/1.0/1.25×`、ADR扩张目标、1R/2R。
- 激进breakout close版本单独统计，只在breakout body≥ `0.75ATR` 且有跟进时启用。

### TRENDS-C22-S04：测量移动处转为第二 Range 交易

- 类型：状态转换与边缘交易策略。
- 依据，PDF p.393–394：bridge常在第一range高度的测量移动附近停止并形成第二range；交易者应从trend管理切换为buy low/sell high。
- 第一range确认时冻结高度`H`，从breakout edge投射 `0.75/1/1.25H`。
- 到目标zone `±0.10–0.30ATR` 后，若出现重叠、doji、双向bar或第二次失败推进，标记`SECOND_RANGE_CANDIDATE`。
- 原趋势仓位在强势中止盈，不继续把stop机械trail到最近swing后等待被打。
- 新交易：只在新range外侧20–30%区域做反转，目标中点/对侧；中部禁入。
- 大trend bar到达目标只作为潜在exhaustion；逆势必须有失败突破或第二信号。

### TRENDS-C22-S05：第二 Range 回测前一 Range

- 类型：完整逆bridge策略。
- 依据，PDF p.391、393–399、402–405：第二range形成后通常回测早先range；可以进入旧range，若接近但不进入则表示原趋势更强。
- Setup：S04第二range已确认；新range靠趋势侧的突破失败，或两腿反向移动开始。
- 入场：失败突破反转bar，或反向breakout-pullback。
- 止损：第二range最终极值外。
- 目标1：bridge gap；目标2：前一range近侧边界；目标3：前一range对侧。
- 结果分类：`NO_PENETRATION`（距边界≤0.25ATR）、`PARTIAL_ENTRY`、`FULL_TRAVERSE`。
- `FULL_TRAVERSE`并向另一侧突破时转S06 reversal-day候选。

### TRENDS-C22-S06：尾盘跨 Range 反转

- 类型：大幅逆势swing策略。
- 依据，PDF p.394、398、400–405：双向交易日常在最后1–2小时回穿至少一个range；多数reversal days起初是trending trading range days。
- 时间窗用session fraction `0.65–0.90`，避免硬编码市场时钟。
- Setup：已有≥2个range；最后range的趋势侧突破失败，并出现强反向spike或第二反转信号。
- 入场：反向spike后的pullback，或旧range边界突破。
- 止损：最后range极值外。
- 目标：前一range近边、中点、对侧；收盘退出。
- 若进入前一range并保持 `2–3bars`，提高测试其对侧的评分；若最终收在反向极值附近，事后分类为reversal day，但该标签不参与入场。

### TRENDS-C22-S07：多重 Range 时升级为顺势日

- 类型：市场状态门控。
- 依据，PDF p.391、393、403–404：少数日形成3–4个阶梯range；这时更像强趋势日，应主要或完全顺势交易。
- 当确认第三个同方向错位range，且各range中点单调、bridge未被完全回撤，标记`MULTI_RANGE_TREND`。
- 之后禁用普通双向fade，只保留顺势breakout pullback和最终range的S06反转候选。
- 入场：最近range的顺势边界突破回测。
- 止损：回测极值/该range对侧。
- 目标：最近range高度等幅、下一ADR分位、1R/2R。
- 任一bridge被完全回穿后取消升级，恢复range模式。

### TRENDS-C22-S08：历史分位驱动的 Late Breakout

- 类型：尾盘波动扩张策略。
- 依据，PDF p.395、413–414：若临近最后一小时日内range仍约为ADR一半且历史上极少以如此小range收盘，晚盘常扩张，但时间可能不足形成第二range。
- 在session fraction `0.70–0.85` 计算`current_range`在过去 `60–250` sessions最终range中的分位。
- 若分位≤ `0.10` 且当前range≤ `0.40–0.60ADR20`，标记`LATE_EXPANSION`。
- 方向由S02压力分数决定；无明显方向时双向stop，首个成交后取消另一侧。
- 入场：range外1tick或strong breakout close。
- 止损：breakout bar/最近pullback极值；不使用整个range另一侧的超宽stop。
- 目标：最小range高度、历史最终range的25/50分位、收盘退出。
- 原文“约90%会扩大”必须在各市场重估，不作为固定胜率。

### TRENDS-C22-S09：两侧突破失败的普通 Range 分支

- 类型：失败突破与日型降级策略。
- 依据，PDF p.395、411–412：约三分之一初始range并不形成趋势型range，而是先扩一侧、再扩另一侧并返回中部；直接追breakout长期不利。
- 第一次breakout若 `1–5bars` 返回range，记录`FAIL_SIDE_1`；随后相反边界也失败，确认`PLAIN_RANGE_DAY`。
- 入场：第二次失败突破反转，目标range中点；允许第一侧失败但需更小仓位。
- 止损：失败极值外。
- 第二信号优先于第一次反转；tight channel内的逆势信号禁用。
- 一旦降级，取消测量移动必达假设，采用range边缘目标和更短持有期。

### TRENDS-C22-N01：不得把 ADR 当作必达目标

- 类型：`NEGATIVE`。
- 依据，PDF p.394–395、411–413：初始range约半个ADR只提示可能扩张；约三分之一会两侧假突破，明显测量目标也可能不达。
- 禁止因“今日range尚小”在没有breakout结构时入场。
- ADR和range height只提供目标/先验，不可覆盖价格行为失效条件。
- 多个可能opening range高度按从小到大预先排列；价格不停顿才启用下一目标，不能事后选择命中的高度。

### TRENDS-C22-N02：第二 Range 中不能沿用强趋势管理

- 类型：`NEGATIVE`。
- 依据，PDF p.392–394、397–399：trending trading range包含显著双向交易，应更多scalp和双向操作；若继续把stop跟在每个swing外，通常会在range内被扫出。
- S04确认后禁止继续追逐每个同向breakout或把所有仓位当swing。
- 应在range强势端止盈，而不是等待弱势stop退出；这条管理变化必须预先由状态触发。
- 只有S07多重range升级或新强spike-and-channel确认后，才恢复单边trend管理。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 391–393 | 日型特征、初始range比例、与spike-channel区别 | 第1节、S01–S03 |
| 393–395 | 测量移动、新range、回测旧range及尾盘反转 | S04–S06、N01–N02 |
| 395 | 约三分之一普通range分支、极小range晚突破 | S08、S09 |
| 396–399 | range间单bar突破、gap测试和双向交易案例 | S01–S05 |
| 400–406 | 多range、尾盘回穿、顺势与逆势管理 | S05–S07 |
| 407–410 | 首小时后弱趋势、range内trending swings | S02、S03、S06 |
| 411–414 | 两侧失败、目标选择和late breakout | S08、S09、N01 |

## 4. 回测验收

- 每个range保存首次确认时的边界、中心、高度和`known_at`；不得用后续bars扩大原range后回填信号。
- S01建立`TRENDING_RANGE/SPIKE_CHANNEL/PLAIN_RANGE`互斥终态及实时混淆矩阵。
- S02报告方向评分对breakout方向的校准曲线，而非只报告分类准确率。
- S03配对比较直接breakout与breakout-pullback，计入漏单、滑点和信号延迟。
- S04在测量目标触发时冻结管理切换，比较trend trail与range强势止盈。
- S05报告不进入、部分进入、完全穿越前range的概率和时间。
- S06只用入场时已知的range结构，reversal-day标签仅用于事后评估。
- S08必须使用当时可用的历史最终range分布，并按年份滚动更新。
- S09验证原文约三分之一的基准，按资产、波动状态和session分别报告。
- Figure 22.1–22.10仅作章节例证，不作参数拟合或绩效证据。
