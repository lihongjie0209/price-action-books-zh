# 第 23 章：Triangles

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/33-ch23-triangles.md`
- PDF 页码：439–444
- 图表：Figure 23.1–23.2；正文与图注足以定义规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 因果 Triangle 检测

```text
triangle_candidate:
  至少一侧有3个已确认push，另一侧至少2个
  pattern净位移 <= 0.5 * pattern_height（水平版本）
  上下边界可收敛、平行、轻微倾斜或扩张
```

- 相邻push之间需反向摆动≥`max(2ticks, 0.20ATR)`或间隔≥2bars。
- Contracting、ascending、descending、symmetrical的交易逻辑统一；形状仅保留辅助标签。
- Expanding triangle要求higher highs与lower lows交替形成；`outside-outside`是最小变体。
- `ii`只标记micro-triangle候选，不假定低周期实际pivot顺序。
- 超过5次主要push后主标签改为trading range，但保留triangle起源字段。

## 2. 规则卡

### RANGES-C23-S01：Triangle Breakout-Pullback

- 类型：主要确认突破策略。
- 依据，PDF p.439–443：triangle处于breakout mode但方向不确定；最好等待breakout，成功后在pullback入场。
- Strong breakout：收盘越边界≥`0.20–0.50ATR`，bar≥`1ATR`，且下一bar不完全收回。
- 入场：首次breakout pullback顺突破方向signal极值外stop。
- 止损：pullback swing或triangle内部 `0.25–0.50ATR`。
- 目标：triangle高度measured move、1R/2R；超过测量目标并持续则转trend management。
- 首次穿线不回填为入场，必须从pullback确认时执行。

### RANGES-C23-S02：无 Pullback 的 Strong Spike Breakout

- 类型：强突破追随策略。
- 依据，PDF p.440–441：breakout连续数bar无pullback时，市场可能Always-In翻转，可按强spike交易。
- 条件：连续 `2–4bars` 同向trend bodies、累计位移≥`1.5ATR`、overlap≤0.30，均保持triangle外。
- 入场版本：第二根bar close、prior high/low stop、小pullback limit；三种执行分别报告。
- 止损：spike起点过远时按固定风险缩仓，或置最近breakout swing外。
- 目标：triangle高度、spike高度、1R/2R。
- 单根breakout无follow-through不适用，转S03。

### RANGES-C23-S03：Triangle Breakout Failure 到对侧

- 类型：失败突破反向策略。
- 依据，PDF p.440–442、444：triangle价值区具有磁力，突破常失败并回range，通常测试对侧，甚至两腿修正/反转。
- Failure：breakout后 `1–3bars` 内收回边界且无S01/S02强确认。
- 入场：reclaim bar朝range内部极值外stop；保守版等待第二signal。
- 止损：失败breakout最终极值外。
- 目标：triangle中点、对侧边界、1R；穿越对侧后可用新breakout高度目标。
- 若首次breakout强度达S02，禁止机械fade。

### RANGES-C23-S04：足够高的 Triangle 内部边缘 Fade

- 类型：区间交易策略。
- 依据，PDF p.441–442、444：triangle够高时可像普通range买底卖顶；太紧时应等待breakout。
- 净高度扣除成本后必须容纳 `>=2R`；底部/顶部区域各为外侧25–30%。
- 入场：边缘double bottom/top、H/L2、reversal bar或failed breakout。
- 止损：triangle边界外；目标中点、对侧、1R/2R。
- 中部stop和tight triangle禁用。
- 多条画线解释只能选择实时边界，不得事后挑最盈利版本。

### RANGES-C23-S05：Prior-Trend Continuation Bias

- 类型：方向评分组件。
- 依据，PDF p.440–441：triangle作为pause略偏向此前趋势，但优势不足以单独下单；三推countertrend压力常在趋势后期增大。
- 保存进入pattern前 `5–20bars` 的trend direction/strength；同向breakout score增加 `0.05–0.15`。
- 该偏见只能在S01/S02已确认时选择仓位上限/目标，不提前挂单。
- Pattern前有climactic reversal时bias设中性；屏幕之外假设的更大趋势不作为数据。
- 按prior trend强弱、pattern push数与趋势年龄报告增量效果。

### RANGES-C23-S06：三推 Sloping Tight Channel 的二次确认

- 类型：wedge误判保护策略。
- 依据，PDF p.440–441：三推但线距很窄、channel陡峭时常继续而非立即wedge reversal；不应买/卖第一次逆channel breakout。
- Tight channel：efficiency≥0.65、平均overlap≤0.40、两边界间宽度≤`1.5ATR`。
- 第一逆channel breakout仅标candidate；若强则等待其pullback，若弱并失败则顺旧channel方向交易。
- 入场使用S01 breakout-pullback或S03 failure，不凭第三推直接逆势。
- Channel持续超过第3推不强制重计为reversal。

### RANGES-C23-S07：Triangle / TTR 作为 Final Flag

- 类型：趋势末端失败突破策略。
- 依据，PDF p.440–442、443–444：复杂三推多在趋势/摆动后期，horizontal triangle常成为final flag；顺势breakout失败后可形成两腿修正甚至反转。
- Candidate：prior trend≥`20bars`或3 pushes，triangle位于趋势极值附近，pattern内双向压力增加。
- 不在pattern内逆势；等待顺prior trend breakout后 `1–3bars` 失败收回。
- 入场：按S03逆旧趋势；止损在final extreme外。
- 目标：triangle对侧、EMA、两腿/10bars、1R/2R。
- 顺势breakout满足S02则取消final-flag候选。

### RANGES-C23-S08：Expanding Triangle 的交替 Failure

- 类型：扩张区间策略。
- 依据，PDF p.439、442、444：expanding triangle可反转或延续，突破常失败并扩大到另一侧；top经常演化为bottom，反之亦然。
- 检测交替higher high/lower low至少5legs；每次边界扩张按已确认极值更新。
- 在新极值出现failed breakout/reversal signal时朝内部入场；止损在最新极值外。
- 目标中点/对侧前一边界；不预期一次突破必然major reversal。
- 真breakout+follow-through则转S01/S02，并停止无限fade。

### RANGES-C23-S09：Wedge Breakout 后横盘的原趋势恢复

- 类型：失败反转/continuation策略。
- 依据，PDF p.443–444：rising wedge向下breakout若没有下行动量而横盘，显示bear无法反转，bull常重新买入；bear版镜像。
- 逆prior trend breakout后 `3–8bars` 净位移≤`0.5ATR`、无follow-through、形成TTR。
- 等原趋势方向强bar突破该TTR，再在close或首次pullback入场。
- 止损：TTR另一侧；目标旧极值、TTR/wedge高度、1R/2R。
- 若逆向breakout随后满足S01/S02，关闭恢复候选。

### RANGES-C23-N01：Triangle 类型名称不应改变策略

- 类型：`NEGATIVE`。
- 依据，PDF p.439–442：ascending、descending、symmetrical有相同交易含义；不完美三推也功能等同triangle。
- 不为每个形状训练独立方向规则并挑最好结果；主模型统一，形状只作预注册分层。
- 不要求完美收敛或精确line touches。
- 同一pivot集合只生成一个主事件，多个画法不重复计数。

### RANGES-C23-N02：Prior Trend Bias 不足以在 Triangle 内下注

- 类型：`NEGATIVE`。
- 依据，PDF p.440–442：triangle是双方平衡/不确定区，虽略偏原趋势，但优势不足以单独交易。
- 未出现S01/S02确认前，任何方向breakout stop均禁用；S04边缘fade除外。
- 不把书中“usually/slightly more often”转换成固定胜率。
- 方向概率从样本外估计并与50%及成本后breakeven基准比较。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 439–440 | triangle/expanding/contracting/ii定义、三对二腿、breakout mode | 定义、S01、S08 |
| 440–441 | prior-trend偏见、三推压力、tight-channel误判与确认 | S05–S07、N01–N02 |
| 441–442 | breakout failure、range边缘fade、对侧测试与测量目标 | S01–S04、S07 |
| 442–444 | expanding演化、多种画法、ii、wedge失败横盘恢复 | S08–S09、N01 |

## 4. 回测验收

- Pivot与边界保存确认时点；triangle标签只能从第5条合格leg确认后生效。
- Shape分类统一使用同一母策略，再按contracting/ascending/descending/expanding分层。
- S01/S02/S03互斥：confirmed breakout、spike、failure不能重复计盈。
- S04必须证明扣成本后可容纳2R；中部和tight样本交易数为零。
- Prior-trend bias只在确认后使用，单独量化其相对无bias模型的增量。
- 三推tight channel样本单列，验证S06等待是否降低首反转亏损。
- Measured move高度在breakout时锁定，不因range后来扩大而回改目标。
- Figure 23.1–23.2只作章节例证，不作参数拟合或绩效证据。
