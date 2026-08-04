# 第 8 章：Bar 收盘的重要性

## 元数据

- 英文来源：`books/trading-price-action-trends/en/chapters/13-ch08-the-importance-of-the-close-of-the-bar.md`
- PDF 页码：201–204
- 图表：Figure 8.1；正文已完整解释周期与止损差异，未额外查看图片
- 状态：量化执行与管理规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 规则卡

### TRENDS-C08-N01：禁止用未完成 Bar 确认信号

- 类型：`NEGATIVE` 执行约束。
- 依据，PDF p.201–202：早入偶尔改善约1tick，但一次形态在最后数秒失败可能损失约8ticks；作者认为所需成功比率不现实。
- 规则：所有依赖实体、收盘位置、影线、inside/outside或反转bar的条件，只在bar正式收盘后计算。
- 允许例外：完全不依赖最终OHLC的独立tick级策略；必须另建信号、延迟和成交模型，不能与收盘策略混合统计。
- 反事实回测：
  - bar时间进度50%、75%、90%、98%的快照入场；
  - 正式收盘后入场；
  - 比较改善价格、形态失败率、期望R及决策次数。

```text
if strategy_requires_final_bar_shape:
    prohibit_signal_until(timestamp >= scheduled_bar_close)
    compute_features_from_final_ohlc()
    submit_order_for_future_execution()
```

### TRENDS-C08-S01：最终收盘后的 Stop Entry

- 类型：通用入场框架。
- Setup：bar收盘后按最终OHLC重新计算signal质量、结构止损、目标空间和交易者方程。
- 入场：反转/延续方向极值外 `max(1 tick, 0–0.10ATR)` 的stop entry。
- 止损：最终signal结构另一侧，不使用bar进行中更小的临时range。
- 订单有效期：1–3bars；信号失效或新bar提供更好位置时取消。
- 优点必须通过S08-N01的快照版本实证，而非假定等待必然更优。

### TRENDS-C08-N02：Entry Bar 收盘前不得提前收紧止损

- 类型：`NEGATIVE` 持仓约束。
- 依据，PDF p.202：未完成entry bar一度呈反转形状可能触发过紧止损，随后最终收盘恢复并到达目标。
- 基准：至少等entry bar正式收盘，期间保留入场前冻结的结构止损。
- 收盘后才允许根据最终bar执行：保持原止损、结构性提高止损、减仓或scratch。
- 禁止把止损移到未完成bar极值外；这同时引入未来形态误判和不一致风险。
- 回测比较：原始结构止损、每tick移动、entry收盘后移动、第二个bar收盘后移动。

### TRENDS-C08-S02：收盘质量驱动的 Swing 比例

- 类型：动态减仓/持有规则。
- 依据，PDF p.202：entry bar及后1–2bars收盘增强时，应减少scalp退出数量并保留更多swing仓位；弱收盘则相反。

```text
close_strength(direction, t) = mean(
    directional_close_position,
    body_frac,
    close_vs_prior_extreme,
    normalized_close_improvement
)
```

- 观察：entry bar及后续 `1–2bars`。
- swing比例：
  - 分数 `<0.40`：保留0%–25%，其余在首目标/scratch退出。
  - `0.40–0.70`：保留25%–50%。
  - `>0.70`：保留50%–100%，沿结构跟踪。
- 上述阈值和比例均为 `EMPIRICAL`，搜索相邻网格；不得用未来bar补标entry质量。
- 初始总风险不变，收盘质量只控制退出，不能在未经计划时扩大仓位。

### TRENDS-C08-S03：结构止损与固定风险减仓

- 类型：仓位规则。
- 依据，PDF p.203–204：重要反转的5分钟结构止损可能较宽；合理做法是减半仓位，而不是切换3分钟图把止损缩到噪声内。
- 初始止损：执行周期signal/结构极值外1tick。
- 仓位：`floor(account_risk / structural_stop_value)`；当止损为近期常态的 `1.25–2.5` 倍时自然缩仓。
- 若最小合约仍超过账户风险，跳过交易。
- 对照：
  - 执行周期结构止损+风险等额仓位；
  - 小周期止损+同等账户风险；
  - 任意固定点数止损。
- 报告stop-out率、重新入场率、净期望和尾部损失，不能只比较单笔止损大小。

### TRENDS-C08-N03：禁止交易中临时切换周期

- 类型：`NEGATIVE` 数据与决策约束。
- 依据，PDF p.203–204：同时协调3分钟和5分钟冲突信号会使交易者被困出场；重要反转中小周期stop run更常见。
- 执行周期在开盘前冻结；持仓期间不得因为不利小周期bar临时改变止损。
- 合法多周期模型必须事前定义周期、更新时间和优先级；高周期未收盘数据不可使用。
- 回测不得为每笔交易事后选择能避开止损的周期。

## 2. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 201 | 等待bar收盘；早入收益不足以补偿偶发大损失 | N01、S01 |
| 201–202 | 最后1–5秒反转bar可能完全失败 | N01 |
| 202 | 未完成bar导致提前移动止损并被困出 | N02 |
| 202 | entry及后1–2bars强收盘支持保留更多swing仓位 | S02 |
| 202 | 机构也使用基于close的line chart | close_strength特征的研究依据 |
| 203–204 | 小周期止损更小但成功概率下降 | S03、N03 |
| 203–204 | 宽结构止损应通过减仓控制风险 | S03 |
| 204 | 只看并交易一个固定图表，避免实时冲突 | N03 |

## 3. 回测验收

- 需要bar内快照的数据源才能检验N01；仅有最终OHLC时不得模拟提前形态。
- 所有最终bar特征只能在官方收盘时间后生效，并加入实际计算/下单延迟。
- N02统计提前止损节省的损失与错误stop-out后错失的MFE。
- S02必须做阈值和仓位比例的walk-forward选择，报告换手与成本变化。
- S03在相同账户风险下比较不同周期，不能用相同合约数造成虚假结论。
- Figure 8.1仅作章节例证，不作拟合样本。
