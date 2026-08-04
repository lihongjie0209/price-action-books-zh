# 第 9 章：反转常终止于先前失败反转的信号 Bar

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/17-ch09-reversals-often-end-at-signal-bars-from-prior-failed-reversals.md`
- PDF 页码：215–218
- 图表：Figure 9.1；正文与图注已完整说明，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Failed-Reversal Magnet Registry

每个逆当前趋势的signal在确认后登记：

```text
signal_extreme = high(signal_bar) for failed bull reversal in bear trend
signal_extreme = low(signal_bar)  for failed bear reversal in bull trend
theoretical_entry = signal_extreme +/- 1 tick
failed = entry triggered and price subsequently makes a new trend extreme
```

- 同时保留signal极值和理论entry；实际成交不可知时不能声称某群交易者精确持仓。
- 每个magnet记录方向、形成时间、趋势层级、失败后最大延伸、是否已测试及`known_at`。
- 未触发的signal单独标记，不能与已触发且失败的反转合并。

## 2. 规则卡

### RANGES-C09-S01：先前失败 Signal 的目标注册

- 类型：目标数据组件。
- 依据，PDF p.215–218：趋势中的早期失败反转entry和signal bar极值，是后来成功反转的重要目标；最早/最高层signal常成为首次大pullback终点。
- 只登记实时可识别且已触发的逆势signal，随后旧趋势创新极值才确认失败。
- Registry按当前价距离、时间新旧和趋势层级排序；相距 `0.10–0.30ATR` 合并为zone。
- 新反转方向若与magnet一致，将最近 `3–10` 个未测试zone交给S02。
- 价位被穿越并在外侧保持2–3bars后标记tested，不重复作为首目标。

### RANGES-C09-S02：成功反转后的 Magnet-to-Magnet 持仓

- 类型：反转持仓/目标策略。
- 依据，PDF p.215–217：新反转通常试图建立range，其潜在另一边常是早期失败反转的entry/signal extreme。
- Setup：反向spike、follow-through及higher low/lower high确认Always-In翻转。
- 入场：该反转自身的breakout pullback/第二信号；registry不能单独产生入场。
- 第一目标：最近未测试failed-signal zone；穿越并有强跟进后启用下一zone。
- 止损：新反转结构swing外；目标到达前仍服从结构失效。
- 到zone分批止盈；若形成反向signal/double top-bottom，转S03。
- 目标距离不足 `0.5–1R` 时不新开仓，但可用于已有仓位退出。

### RANGES-C09-S03：旧 Signal Zone 的 Range-Edge 反应

- 类型：条件式反向scalp/状态转换。
- 依据，PDF p.216–217：反转腿到达旧失败signal区域时，方向概率可能再次偏向旧卖/买方，常形成double top/bottom并开始新range回摆。
- Setup：S02到达zone，同时新反转腿已延伸、动能下降或达到其他测量目标。
- 触发：double top/bottom、强reversal bar或第二信号。
- 入场：回摆方向signal外stop。
- 止损：zone测试极值外。
- 目标：新range估计中点、最近swing、1R；默认按range leg而非新大趋势管理。
- 若强势穿越zone，不fade；该zone关闭并启用下一目标。

### RANGES-C09-S04：技术位 Confluence 提高反转候选评分

- 类型：目标聚类组件。
- 依据，PDF p.216：真正反转点无法预知，但多个测量目标、trend line、高周期EMA/趋势线和failed signals靠近时，足够订单可能改变方向。
- 独立来源：failed-signal zone、measured move、trend/channel line、已完成高周期EMA/swing。
- 相距 `0.10–0.30ATR` 聚类；至少2类独立来源才标`CONFLUENCE`。
- Confluence只增加S02止盈/S03反转评分，不允许裸limit入场。
- 高周期特征必须等bar收盘后可用；无需为了寻找confluence临时打开多个周期。

### RANGES-C09-S05：多尺度 Failed-Signal 目标

- 类型：跨周期研究组件。
- 依据，PDF p.217–218：该现象可跨月、年或intraday出现；任何早期失败反转都可能成为后续修正磁体。
- 基础周期与预先固定的高一层周期分别维护registry，不混用确认时间。
- 高周期zone在其signal bar收盘及失败确认后才下发基础周期。
- 同价位多周期重合视为confluence，但同一基础事实聚合而成的bar不重复计票。
- 目标等待窗分别设 `20–200bars` 或 `1–20sessions`，未到达者作为右删失保存。

### RANGES-C09-N01：Failed-Signal Magnet 不是必达价

- 类型：`NEGATIVE`。
- 依据，PDF p.218：任何目标都不必到达，只是经常吸引价格。
- 禁止因为registry存在就逆当前Always-In开仓，或在目标未达时放宽stop。
- 目标命中率必须包含未命中及观察窗结束样本，不能只展示历史上显眼的精确测试。
- “被套者保本退出”只作机制假设；实现依据价格与signal事件，不假定实际持仓分布。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 215–216 | 失败反转entry/signal extreme成为后来目标 | 第1节、S01、S02 |
| 216–217 | 新反转形成range、旧价位处概率重新偏移 | S02–S04 |
| 217–218 | 月线实例、多个目标及不保证到达 | S05、N01 |

## 4. 回测验收

- Signal形成、触发、失败和magnet启用四个时间分别保存，禁止未来信息回填。
- S01比较signal extreme与theoretical entry哪个更常被首次测试。
- S02使用生存分析或固定窗口，保留未达目标和趋势先失效事件。
- S03报告zone处pause、穿越、range回摆和新趋势四种终态。
- S04做独立来源消融，防止高度相关目标重复提高分数。
- S05检查高周期bar收盘延迟，基础周期不得提前知道聚合极值。
- Figure 9.1仅作章节例证，不作参数拟合或绩效证据。
