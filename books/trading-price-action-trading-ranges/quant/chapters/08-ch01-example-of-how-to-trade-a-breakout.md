# 第 1 章：如何交易突破的示例

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/08-ch01-example-of-how-to-trade-a-breakout.md`
- PDF 页码：94–101
- 图表：Figure 1.1–1.2；正文与图注已逐bar完整说明，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 强 Breakout Spike 定义

```text
spike_height = directional_extreme - spike_start
structural_risk = abs(entry - (spike_start -/+ buffer))
directional_bar_rate = mean(bar direction agrees with breakout)
body_overlap = mean(overlap(adjacent bodies) / min(body sizes))
edge = p_win * reward - (1-p_win) * risk - costs
```

- spike从突破结构的第一根有效trend bar开始，到首个pause/反向bar前结束。
- 强候选：至少2根同向trend bars，body/range≥ `0.60`、尾部≤ `0.30`、body overlap≤ `0.35`，并使Always-In翻转；均为`PROXY`。
- 原文给出强spike达到至少自身高度测量移动的主观概率约60%，极强时可更高；实现中必须用训练样本校准`p_win`，不能硬编码80%。
- spike增长时，测量目标更新，但初始成交的风险不能随意扩大；每次新增仓位单独冻结entry与stop。

## 2. 规则卡

### RANGES-C01-S01：强 Breakout Close/Market 参与

- 类型：完整突破策略。
- 依据，PDF p.94–97：可靠breakout移动快、stop需在spike起点外；即使心理困难，至少应以小仓参与，因其交易者方程优良。
- Setup：第1节强spike成立，突破预登记range、swing、trend line或反转结构，Always-In同向。
- 入场：第二根确认trend bar收盘、下一bar市价，或 `0–0.15ATR` 小回撤。
- 止损：spike起点外1tick至 `0.15ATR`；不能仅为扩大仓位把stop收进spike。
- 仓位：`floor(account_risk_budget / (structural_risk*point_value+costs))`。
- 目标：spike高度 `0.75/1.0/1.25×` 投射、1R/2R；余仓进入channel管理。
- 失效：反向spike完全回撤breakout并翻转Always-In。

### RANGES-C01-S02：Spike 增长中的固定总风险 Press

- 类型：加仓与风险组件。
- 依据，PDF p.95–97：experienced traders在spike延伸时追加，但stop远时减小仓位；若风险距离是正常的3倍，仓位约为1/3，总风险不超常规。
- 仅在每根已收盘bar仍满足强spike且当前浮盈允许上移结构stop时考虑加仓。
- 每次加仓前计算所有legs同时打共同stop的最坏损失，总额≤账户预算 `0.25–1.00%`（`PROXY`）。
- 加仓触发：强trend close、prior bar小回撤、或新micro measuring gap确认。
- 最大 `2–4` legs；达到上限后只管理，不因继续上涨无限累计。
- 报告每腿风险贡献和路径最大杠杆；不得以最终盈利掩盖途中超限。

### RANGES-C01-S03：Breakout 强度驱动的 Stop Trail

- 类型：仓位管理组件。
- 依据，PDF p.95–96：spike增长后可把stop上移到关键强trend bar、micro measuring gap或最新结构低/高点外。
- 初始stop在spike起点。
- 若新强trend bar收盘且其被完全反向穿越会否定强度，将stop移至该bar不利极值外。
- bull micro gap：bar[t-1] high < bar[t+1] low；确认到`t+1`收盘后，stop才可移至`t+1` low外；bear对称。
- 只允许收紧，不允许因新目标变大放宽原stop。
- 比较spike-start、strong-bar、micro-gap和最近swing四种trail，报告被提前扫出后的机会成本。

### RANGES-C01-S04：强度不足时等待 Breakout Pullback

- 类型：完整回测策略。
- 依据，PDF p.97–99：直接突破旧swing通常不如pullback具有更好的概率、风险和回报；若顶部spike不够强，应等待pullback。
- Setup：breakout有效但不满足S01极强阈值，或双向交易开始增加、pullback持续超过约5bars。
- 回测窗口 `1–20bars`，目标为breakout point、gap中点、EMA或prior swing。
- 触发：High/Low 1/2、double bottom/top、ii、outside trend bar或失败逆向突破。
- 入场：signal bar顺突破方向外stop；同方向body signal作为高质量子组。
- 止损：回测swing外。
- 目标：breakout极值、spike/第一腿等幅、1R/2R。
- 强度恢复为runaway且无回测时，不伪造成交；由S05兜底。

### RANGES-C01-S05：错过 Pullback 的 Last-Ditch Stop

- 类型：参与保障策略。
- 依据，PDF p.99：强Always-In趋势首次pullback时，应在spike极值外保留最坏情形stop entry，避免等待两腿回调而错过最强趋势。
- Setup：S01强突破后首次pause/pullback，交易者尚未持仓。
- 在spike high上1tick放buy stop（bear对称）；若提前通过High/Low 1或limit成交则取消。
- 触发后止损：最近minor pullback极值或spike起点外，取能否定前提者并按风险缩仓。
- 目标：新spike高度等幅、1R/2R。
- 禁用：连续climax、final flag、明显two-sided trading或session剩余时间不足。
- 必须按stop实际跳空/滑点成交，不能假设精确1tick。

### RANGES-C01-S06：逆向 Spike 无跟进的失败突破

- 类型：顺主趋势失败形态策略。
- 依据，PDF p.100：主趋势中的逆向大trend bar是breakout尝试；成功通常应有下一根同向bar或至少doji，若下一bar反向收盘，失败概率上升。
- Setup：强趋势中出现逆向spike，测试trend line/EMA/突破点。
- 失败定义：下一 `1–2bars` 无逆向跟进，且至少一根收盘恢复主趋势方向。
- 入场：逆向bar收盘的limit研究版，或失败确认bar外stop标准版。
- 止损：逆向spike极值外。
- 目标：逆向bar另一端、趋势旧极值、其高度等幅、1R/2R。
- 若逆向spike获得跟进并翻转Always-In，立即取消，不能以长期基本面叙事否认价格。

### RANGES-C01-S07：连续 Climaxes 后锁定利润

- 类型：止盈/暂停追价组件。
- 依据，PDF p.99–101：第三次连续climax、final flag或无pullback的大幅推进后，常出现约10bars复杂修正；先锁定盈利，再寻找更高/低的重入。
- climax代理：trend bar range/body≥过去20bars中位数 `1.5–2.5倍`，同方向且由 `1–5bars` pause分隔。
- 第2个climax后减少新增仓位；第3个后在强势端减 `25–100%`，停止S01/S02追价。
- 逆势交易不是默认动作；需反向signal或第二入场。
- 修正目标：EMA、最近breakout point、两腿且约10bars。
- 若继续强跟进，只保留既有结构stop，不逆势加仓。

### RANGES-C01-S08：Breakout Gap/Channel 起点测试

- 类型：目标与再入场组件。
- 依据，PDF p.100–101：突破后通常测试breakout gap；tight channel结束后常测试channel起点。
- gap在可确认时冻结：bull中`post_breakout_low - breakout_point_high`，bear对称。
- 回测目标依次为gap中点、breakout point、channel起点；容差 `0.10–0.30ATR`。
- 若回测处形成顺原突破方向第二信号，执行S04再入场。
- 若强收盘穿过channel起点并有跟进，突破前提失效，转range/reversal状态。
- 目标只用已知breakout结构，不得事后挑选bar 作为最吻合的gap端点。

### RANGES-C01-N01：Tight Range 与成熟双向阶段不追 Breakout

- 类型：`NEGATIVE`。
- 依据，PDF p.96、98：强方程出现时应积极；tight trading range没有这种优势，应少交易。趋势越双向，越应等pullback，最终可按range交易。
- overlap≥0.70、EMA平缓、range高度≤ `1ATR` 时，禁止S01 close追价。
- pullback深度/持续增加且双方各有2根以上trend bars时，停止S02 press和S05兜底追入。
- 只有新强spike重新确认Always-In后才恢复breakout模式。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 94–96 | breakout风险、约60%测量移动、spike增长与trail | 第1节、S01–S03 |
| 96–98 | 至少小仓参与、固定风险缩仓、breakout与pullback比较 | S01、S02、S04 |
| 98–99 | two-sided阶段、具体pullback与last-ditch stop | S04、S05、N01 |
| 99–100 | 连续climax、逆向breakout失败 | S06、S07 |
| 100–101 | breakout gap、channel起点测试与高潮止盈 | S07、S08 |

## 4. 回测验收

- spike起点、终点、Always-In翻转和breakout结构均按实时确认时点记录。
- 原文60%/80%主张用训练期校准曲线检验，验证期只应用冻结模型。
- S01比较close、市价、小pullback三种成交，包含滑点和结构stop导致的仓位差。
- S02逐bar计算组合开放风险；任何时点超预算即判策略违规。
- S03的micro gap必须等后一bar收盘确认，不能前移stop。
- S04与S05共用错过突破事件，报告等待pullback的改善与漏失。
- S06统计逆向spike后follow-through/失败/Always-In翻转的完整转移概率。
- S07按climax序号分层，不把普通大bar事后都归为高潮。
- Figure 1.1–1.2仅作章节例证，不作参数拟合或绩效证据。
