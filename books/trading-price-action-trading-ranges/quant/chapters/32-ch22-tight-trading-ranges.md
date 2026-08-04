# 第 22 章：Tight Trading Ranges

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/32-ch22-tight-trading-ranges.md`
- PDF 页码：409–438
- 图表：Figure 22.1–22.12；正文与图注已完整说明规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 实时检测器

```text
TTR candidate:
  bars >= 3
  height <= min(0.20–0.35 * ADR, 2.0–3.5 * ATR_bar)
  mean_pairwise_overlap >= 0.60
  direction_flips >= 2 per 5 bars
  doji_ratio >= 0.25 OR tail_ratio >= 0.45

barbwire:
  3+ largely-overlapping bars
  at least one doji
  middle bar overlap with neighbors > 50%
```

- 原文“两根以上”可作为最早candidate，但正式TTR至少等第3根完成bar，避免单个inside bar误判。
- Sloping tight channel使用相同逻辑：先对滚动线性斜率去趋势，再计算残差range与overlap。
- TTR只从确认bar开始生效；边界由当时已知high/low滚动更新。
- 所有书中51–55%、60%、70%、90%为待检验假设，不进入硬编码仓位或信号。

## 2. 规则卡

### RANGES-C22-S01：TTR 确认后的 No-Trade 状态

- 类型：市场状态与交易禁用组件。
- 依据，PDF p.409–417、427–430：重叠、多反转、doji/tails表示双方平衡；stop entries长期亏损，大多数交易者应等待breakout后的清晰机会。
- TTR确认后关闭H/L1–4、ioi、普通reversal bar及range内部breakout stop策略。
- 只保留：S03 failed breakout、S04 breakout pullback、S06强趋势第二entry；高级limit策略S08单独开关。
- 状态退出：边界外strong breakout+follow-through，或range扩大为普通range且内部空间足够≥2R。
- 每次候选被拒绝记录`blocked_by=TTR`，便于验证过滤器价值。

### RANGES-C22-S02：持仓中市场演化为 TTR 时退出

- 类型：持仓管理策略。
- 依据，PDF p.412、414、417、425–426：入场后若小bar重叠发展成TTR，原胜率/收益风险已改变；优先breakeven或小亏退出，而非宽止损死扛。
- 持仓后 `3–6bars` 确认TTR且尚未达到 `0.5R`，在breakeven±`0.10ATR`可成交时退出。
- 无breakeven机会则使用range反向边界/原stop中较近者，禁止扩大原风险。
- Wrong-direction breakout时立即退出；等待更大range形成后再独立重入。
- “持有宽stop”仅作独立对照，不作为默认实施。

### RANGES-C22-S03：单根 Breakout Trend Bar 的 Failure Fade

- 类型：失败突破策略。
- 依据，PDF p.410、413、419–420、431–434：TTR首breakout常在1–2bars内失败；barbwire应先等trend bar，再准备fade。
- Candidate：一根trend bar收盘越边界≥`2ticks / 0.10ATR`，但下一bar无同向follow-through。
- Trigger：价格跌破bull breakout bar低点则short；突破bear breakout bar高点则long。
- 止损：breakout最终极值外。
- 目标：TTR中点、对侧、1R；若failure继续穿过对侧，可保留部分并按新breakout管理。
- 连续2根以上同向trend bars时禁用fade，转S04。

### RANGES-C22-S04：Strong Breakout + Breakout Pullback

- 类型：确认突破策略。
- 依据，PDF p.410、413、419–423、432–435：更安全做法是等强follow-through，再在breakout pullback顺新趋势入场；首次failure也常转为该pullback。
- Strong：连续≥2根trend bars，或单bar≥`1.5ATR`且下一bar保持边界外；close位于方向端25%。
- 等pullback bar完成，bull版在其高点上1tick买，bear版镜像。
- 止损：pullback swing或TTR内侧 `0.25–0.50ATR`。
- 目标：TTR高度、breakout spike高度、1R/2R；强trend-resumption用S07等幅扩展。
- 若pullback穿越TTR对侧，取消并按反向breakout重新分类。

### RANGES-C22-S05：Failed Breakout Fade 失败后的第二 Entry

- 类型：两阶段反手策略。
- 依据，PDF p.419–420、431–433：首trend-bar breakout常被fade；fade本身失败时构成breakout pullback，第二entry很少再失败。
- S03实际触发后未达 `0.5R`，其entry bar被反向突破，且价格仍在原breakout方向边界外。
- 平掉fade仓，并可在entry bar另一端反手；两仓风险独立计算，不加倍追损。
- 止损：第二entry pullback极值外；目标同S04。
- 若价格重新进入TTR而非保持边界外，只退出不反手。

### RANGES-C22-S06：强趋势 MA Pullback Barbwire 的第二顺势 Entry

- 类型：趋势flag例外策略。
- 依据，PDF p.418–421、427、434–438：barbwire若在强趋势中mostly位于EMA顺势侧，常只是pullback；可做H2/L2第二entry，尤其signal方向明确且tails不突出。
- Bull版：strong bull regime，barbwire至少60% bars/close在上升EMA上方，形成H2且bull signal；bear版镜像。
- 入场：第二signal顺趋势极值外stop；首signal仍由S01阻止。
- 止损：barbwire/完整pullback极值外。
- 目标：旧趋势极值、TTR高度、1R/2R。
- Bars mostly位于EMA反侧时，方向跟随进入barbwire前的pullback move，不使用旧大趋势偏见。

### RANGES-C22-S07：Trend-Resumption Day 的 Leg 1 = Leg 2

- 类型：突破swing管理策略。
- 依据，PDF p.413、422–425、434–435：强首腿后数小时TTR常顺原趋势突破并形成第二条约等长腿；相反突破较少但可反转前腿。
- Setup：TTR前有明确trend leg≥`2ATR`，无climactic reversal；S04确认顺原趋势breakout。
- 入场沿用S04；第一目标TTR高度，扩展目标为pre-TTR leg等幅投影。
- 到1R平 `25–50%`，剩余按结构trail；不能把等幅目标当保证。
- 反向strong breakout时不持旧偏见，按S04新方向并以prior leg起点/旧极值作目标。

### RANGES-C22-S08：高级边缘 Limit Scalping

- 类型：高级/研究性limit策略。
- 依据，PDF p.410–415、419–421、426–430：少数持续盈利者可在底部买prior lows、顶部卖prior highs，通常向中点小幅scalp；普通交易者不适合。
- 仅当TTR净高度扣成本后≥`1.0R + min_profit`，且entry位于底/顶20%。
- Bull limit在prior low/边界附近；bear limit镜像；最多2次scale-in，总风险固定。
- 目标中点前1tick；止损range外 `0.25–0.50ATR`。
- 必须模拟queue、partial fill、adverse selection和1–4tick真实成本；与stop策略完全隔离。
- 若range过窄或bar太小，禁用。

### RANGES-C22-S09：Barbwire 相对 EMA 的方向过滤

- 类型：方向评分组件。
- 依据，PDF p.418–421：barbwire mostly在EMA上方倾向向上break，mostly在下方倾向向下；跨EMA时需其他价格行为。
- 计算最近barbwire bars中close与range位于EMA各侧比例。
- ≥60%在上方给予bull score，≤40%给予bear score；40–60%中性。
- 该score只能选择S04/S06优先方向，不能直接入场，也不使用原文概率硬编码。
- 结合进入pattern前一腿：若barbwire已穿到EMA反侧并保持，优先近期pullback方向而非更早趋势。

### RANGES-C22-S10：多次同侧失败后第三 Breakout 候选

- 类型：序列突破增强组件。
- 依据，PDF p.422–423：同一顶部两次breakout失败后，第三次配合H2、EMA顺侧与先前强趋势时成功概率提高。
- 同一边界容差 `0.10ATR` 内记录failed breakout次数；两次失败后第三次只提高score，不预先成交。
- 必须仍满足S04 strong/follow-through或S06第二entry。
- 入场/止损/目标沿用消费策略，同一事件只计一笔。
- 对1/2/3+次尝试分别报告，验证是否真有条件优势。

### RANGES-C22-S11：TTR 向 Larger Trading Range 演化后的重入

- 类型：状态转换策略。
- 依据，PDF p.411–412、425–427：TTR可先逆趋势break并扩大为普通range，随后再顺原趋势突破；早期持仓应先退出，等待新边缘setup。
- Wrong-direction breakout后不满足S04 trend延续、又在 `3–10bars` 形成新对侧swing，确认larger range。
- 新range高度必须容纳≥2R；在新底/顶使用第21章H2、double bottom/top或failed breakout重入。
- 原TTR entry损失与新交易独立，不scale in“救仓”。
- 目标新range中点/对侧，随后真breakout再切换趋势。

### RANGES-C22-S12：TTR / Barbwire 作为 Final Flag

- 类型：趋势末端反转监控。
- 依据，PDF p.418、420、430–431、436–438：趋势20+bars后TTR常是final flag；顺势breakout可能迅速回range并引发至少两腿pullback/反转。
- 候选：趋势持续≥`20bars`或≥3 pushes，TTR位于极值附近，且有climax/减速。
- 不在range内逆势；等待顺势breakout失败并收回TTR，再按S03入场。
- 止损：最终趋势极值外；目标EMA、TTR另一侧、两腿/10bars、1R/2R。
- 若顺势breakout满足S04 strong follow-through，关闭final-flag候选。

### RANGES-C22-N01：TTR Trumps Everything

- 类型：`NEGATIVE`。
- 依据，PDF p.411–417、427–433：任何漂亮signal、bar count、ioi或trapped-trader逻辑都不能覆盖TTR的近乎均衡数学。
- TTR内部纯stop entry数量必须为零，S06明确第二entry例外除外。
- Reversal bar位于range中没有可反转的趋势，不因外观评分提高。
- “下一笔该赢”不是特征；连续亏损不改变信号概率或仓位。

### RANGES-C22-N02：禁止 Martingale / Loss-Chasing

- 类型：`NEGATIVE`与风险硬约束。
- 依据，PDF p.415–417、428–429：连续6–10次失败在barbwire并不罕见；倍增/三倍仓位在现实保证金下不可执行并会毁损账户。
- 每笔风险固定为账户权益预注册比例；任何`position_size`不得依赖最近盈亏符号或连败数。
- 连续 `2–3` 个TTR亏损后只允许停止该regime交易，不允许增加仓位。
- 自动测试断言：相同setup和stop距离下，连败前后仓位一致（除权益自然变化）。

### RANGES-C22-N03：不硬编码书中概率或 Fibonacci

- 类型：`NEGATIVE`与统计约束。
- 依据，PDF p.411–412、424–425、436：51–55%、60–70%、90%和61.8%均依赖上下文；任意pullback都能接近某个Fibonacci值。
- 固定百分比不进入仓位；对每个精确定义按样本外数据估计并给置信区间。
- Fibonacci retracement不作为独立feature；若研究，只与连续retracement基准作严格增量比较。
- 多个measured move只能使用入场前预注册优先级，禁止事后选中命中目标。

### RANGES-C22-N04：不使用无限宽 Stop 持有错误 Breakout

- 类型：`NEGATIVE`。
- 依据，PDF p.411–412、417、425–426：允许TTR扩大所需的宽stop使风险、收益和概率难以评估；更合理是小亏退出后重新入场。
- 初始stop不得在入场后扩大；TTR确认/错误方向breakout按S02退出。
- Scale-in总风险上限与首仓相同，不以“更大range最终会回来”作为持仓理由。
- 宽stop版本仅可作为固定参数对照，并独立报告尾部风险。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 409–413 | TTR定义、机构平衡、breakout/failure、低预测性与continuation先验 | 定义、S01、S03–S04、S09、N01、N03 |
| 413–417 | breakout pullback、持仓退出、期望值、避免过度交易与martingale | S02、S04–S05、N01–N02、N04 |
| 418–421 | barbwire定义、EMA位置、首breakout fade、第二entry与高级limit | S03、S05–S09 |
| 421–425 | 强趋势第二entry、尝试次数、breakout first pullback与等幅腿 | S06–S07、S10 |
| 425–429 | 扩大range、失败突破、stop连败与martingale风险 | S02、S08、S11、N02、N04 |
| 430–433 | sloping TTR、final flag、ioi/barbwire、failed breakout | S03–S05、S12、N01 |
| 433–438 | 中部failure、趋势flag、Low 2、连续climax后的barbwire反转 | S04、S06–S07、S12 |

## 4. 回测验收

- TTR/barbwire检测逐bar保存`candidate_at/confirmed_at/ended_at`，禁止最终形态回填。
- TTR内部被S01/N01阻止的信号与实际交易都要保存；普通stop交易数量应为零。
- S03/S04/S05形成互斥状态机：failure fade、true breakout、fade failure第二entry不能重复计盈。
- Horizontal与sloping TTR分别报告，去趋势算法参数锁定。
- EMA-side score、prior trend strength和climactic reversal分层估计，不硬编码51–55%。
- 高级limit S08报告真实成交、队列、成本、MAE/MFE，并与“完全不交易”基准比较。
- S02验证breakeven退出的真实可成交率，不假定一定获得breakeven。
- Martingale断言、最大总风险、禁止扩大stop必须进入自动回测测试。
- S12按趋势年龄/推进数分层，确认final-flag标签只在失败breakout后成立。
- Figure 22.1–22.12只作章节例证，不作参数拟合或绩效证据。
