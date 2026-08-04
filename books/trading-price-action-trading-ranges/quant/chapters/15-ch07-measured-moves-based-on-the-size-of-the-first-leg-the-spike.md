# 第 7 章：基于第一腿（Spike）大小的测量移动

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/15-ch07-measured-moves-based-on-the-size-of-the-first-leg-the-spike.md`
- PDF 页码：194–206
- 图表：Figure 7.1–7.5；正文与图注已完整说明，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 基本几何

```text
leg1_height = direction * (leg1_end - leg1_start)
target(k) = leg2_start + direction * k * leg1_height
k ∈ {0.75, 1.00, 1.25}
```

- `leg1`必须在pause/pullback确认后冻结；强spike以首bar open/low/high到末bar close/high/low产生多个候选高度。
- `leg2_start`为pullback最终极值，只有在实时反转确认后可用。
- 强spike常以自身高度形成channel；第一腿也可包含两个更小legs，形成nested measured move。
- 多候选按目标距当前价格由近到远启用；先到最近目标，明显穿越后再关注更远版本。

## 2. 规则卡

### RANGES-C07-S01：Leg 1 = Leg 2 延续

- 类型：完整趋势延续策略。
- 依据，PDF p.194–196、200–204：强第一腿后的pullback通常有第二腿，第二腿常约等于第一腿；也称AB=CD，但无需复杂字母命名。
- Setup：第一腿净位移≥ `0.75–3ATR`，随后有序pullback深度为第一腿的 `0.20–0.70`，Always-In未强势翻转。
- 入场：pullback结束的High/Low 1/2、breakout pullback或第二信号。
- 止损：pullback极值外。
- 目标：`0.75/1.0/1.25×leg1`；在1.0附近分批止盈。
- 失效：pullback完全回撤leg1并在起点外强跟进。
- 结果按最接近目标前是否先触stop的first-passage计算，不用最终极值判定。

### RANGES-C07-S02：Spike 高度测量移动

- 类型：目标与顺势持仓组件。
- 依据，PDF p.196–200、204–206：强spike后channel高度常约等于spike；常用首bar open到末bar close的保守高度，也要观察low/high等版本。
- Spike结束：首个doji、大尾部bar、逆向body或明显pause收盘后，末根momentum bar为spike end。
- 候选高度：
  - first open → final close（默认、通常较保守）；
  - first low/high → final close；
  - first open → final extreme；
  - full first extreme → final extreme。
- 从final close/extreme或first pullback极值分别投射，来源标签不可丢失。
- 顺势仓位持有至最近目标；到达后减仓并预期channel转range/回测起点。
- 极强spike的理论stop在spike起点外，实际仓位按固定账户风险缩小。

### RANGES-C07-S03：目标由近到远的层级管理

- 类型：多目标管理组件。
- 依据，PDF p.197–198、201–205：存在多个合理起终点，先使用最小/最近投射；若市场不停顿，再看下一更远目标。
- 在spike/leg1完成时生成全部合理候选并排序，最多保留最近 `3–6` 个独立目标。
- 到最近目标zone `±0.10–0.30ATR`：减仓或收紧结构stop。
- 若2bars强同向收盘穿越zone，激活下一目标；不得提前用更远目标拒绝合理止盈。
- 多目标聚集为confluence，但同一几何高度的open/low微差不重复加权。
- 全部决策记录当时active target，防止事后挑选命中线。

### RANGES-C07-S04：Pullback 中段 Trading Range 的二腿终点

- 类型：回调结束预测与再入场组件。
- 依据，PDF p.195–196、203–204：强趋势后第一回调腿再形成range时，range近似中点常成为整体pullback中点，可指导第二腿终点及趋势恢复。
- Setup：外层趋势明确；countertrend leg1后形成 `5–20bars` range。
- Range midpoint每bar更新，但每个历史版本只从当时起生效；不能把最终中点回填。
- 投射A：countertrend leg1等幅；投射B：从外层趋势极值到当前range midpoint的对称距离。
- 到目标区等待外层趋势方向High/Low 2、wedge或failed breakout。
- 入场：signal bar外stop；止损在pullback最终极值外。
- 目标：外层趋势旧极值、1R/2R；单独到达投射位不入场。

### RANGES-C07-S05：Spike-and-Channel 到目标后的 Range 转换

- 类型：状态转换与反向候选。
- 依据，PDF p.195–200：spike测量移动常结束channel并开始profit taking；channel通常成为新range第一腿，随后回撤到channel起点并反弹。
- Setup：S02目标到达，同时channel已有overlap、tails、逆向bars或第三推进。
- 顺势动作：减仓 `50–100%`，停止在新极值追价。
- 逆势只在强reversal/第二信号后进入；止损在channel极值外，目标channel起点。
- 到channel起点后，允许double bottom/top flag沿原趋势回摆，目标range中点。
- 若目标处无pause且继续强spike，保持顺势并转S03下一目标，不强行range化。

### RANGES-C07-S06：Spike 向相反方向的测量移动

- 类型：失败spike反转策略。
- 依据，PDF p.196–197、205–206：spike通常顺方向测量，但若缺少channel并反转越过spike起点，也可向相反方向走约spike高度。
- Setup：spike后反向bar完全回撤spike、突破其起点并使Always-In翻转。
- 入场：反向breakout pullback；不在spike刚pause时猜失败。
- 止损：回测极值/原spike另一端。
- 目标：从spike起点反向投射 `0.75/1.0/1.25×spike height`。
- 原方向目标关闭但保留事件历史；两个方向不能同时作为active必达目标。
- 反向突破无跟进时转range，不继续持有到理论目标。

### RANGES-C07-S07：Nested/Alternative Leg Endpoint

- 类型：多尺度测量组件。
- 依据，PDF p.201–203：第一腿可能包含两个小腿；pullback可越过看似第一腿起点，因此多个end point都合理。
- 使用固定zigzag尺度 `0.5/1/2ATR` 并行识别small/medium/large legs。
- 若修正起点存在两个合理swing，两个leg1高度都在形成时登记；先启用较近目标。
- 允许pullback形成lower low/higher high而仍属于复杂修正，但必须保留外层Always-In状态。
- 任何endpoint只有在pivot确认后生效；不得因某目标后来精确命中才选中它。
- 报告不同尺度目标重叠率和增量信息。

### RANGES-C07-S08：Measured Move 与 Trader's Equation 门控

- 类型：概率/风险组件。
- 依据，PDF p.194、197–200：强趋势下作者估计等幅概率约60%，极强可到70%；range中等距方向概率约50%，不能同样交易。
- 只在walk-forward校准`P(target before stop)>0.5+cost_margin`时启用顺势策略。
- 账户期望：`p*reward-(1-p)*risk-costs>0`；reward和risk均由实际entry而非理想leg端点计算。
- Range中部默认p≈0.5先验，禁止仅凭几何等幅入场；range边缘/强spike需独立校准。
- 原文60%/70%/80%均作为验证假设，不硬编码为回测胜率。
- Spike stop过宽导致最小仓位超预算时跳过，不缩短到结构噪声内。

### RANGES-C07-N01：测量目标不是裸 Limit Fade 信号

- 类型：`NEGATIVE`。
- 依据，PDF p.195–196、204–205：目标只是保持顺势及止盈指南；Fibonacci/测量magnet近似，不能单独在目标挂逆势limit。
- 逆势至少需要强reversal bar、第二信号、channel结束或其他独立结构。
- 不增加138%、150%、162%等大量扩展来寻找事后吻合；核心网格保持稀疏。
- 到目标未反转时，不能扩大逆势仓位等待“最终必回”。

### RANGES-C07-N02：早期强 Spike 不应在过近目标全部止盈

- 类型：`NEGATIVE`。
- 依据，PDF p.165–167（第6章承接）、本章p.195–200：早期强spike往往远超其最小投射，太早退出会丢失最佳swing。
- Spike发生于趋势前 `1–5bars` 且score≥0.80时，最近目标最多减 `25–50%`。
- 至少保留余仓至channel形成、2R或结构反转。
- 该限制与S03层级管理同时记录，比较早退成本。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 194–196 | measured move定义、交易者方程、leg1=leg2及range中点 | 第1节、S01、S04、S08、N01 |
| 196–200 | spike多高度、channel目标、概率向50%回归 | S02、S03、S05、S08、N02 |
| 200–204 | nested legs、alternative endpoint与range midpoint案例 | S01、S04、S07 |
| 204–206 | 新闻spike、最近目标优先及反向测量移动 | S02、S03、S06 |

## 4. 回测验收

- leg/spike endpoint仅在pause/pivot确认后冻结；不得用最终最高最低重画。
- S01按pullback深度、外层状态和leg1强度分层。
- S02所有高度版本并行输出，默认open→close不得因表现差被删除。
- S03保存每时刻active target及穿越确认，验证最近优先策略。
- S04每bar midpoint版本有独立`known_at`，最终range中心不能回填。
- S05报告目标处pause/range/continuation三终态和channel-start测试率。
- S06原向/反向目标互斥激活，报告反转确认延迟。
- S08用walk-forward概率校准，验证而非假定60%主张。
- Figure 7.1–7.5仅作章节例证，不作参数拟合或绩效证据。
