# 第 11 章：迟到与错过的入场

## 元数据

- 英文来源：`books/trading-price-action-trends/en/chapters/16-ch11-late-and-missed-entries.md`
- PDF 页码：213–216
- 图表：Figure 11.1；正文已说明仓位和止损关系，未额外查看图片
- 状态：量化执行规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 规则卡

### TRENDS-C11-S01：原计划 Swing 仓位复制

- 类型：迟到入场策略。
- 依据，PDF p.213–214：若原始入场后按计划仍会持有swing部分，则现在以相同剩余仓位和相同trailing stop入场，在经济上等价。
- 前置：必须存在可复现的“原始策略”，且能从历史bars机械重放其入场、减仓和当前止损。
- 入场条件：
  - 原始策略状态仍为持仓；
  - 当前Always-In方向与其一致；
  - 原始策略尚未到最终目标或退出条件；
  - 当前入场到原计划止损的交易者方程仍通过。
- 仓位：`min(original_remaining_qty, account_risk / current_stop_distance)`；绝不恢复原始满仓。
- 入场：当前下一可成交价。
- 止损：原始策略当前trailing stop，而非为迟到者单独收紧。
- 目标：完全继承原始swing计划。
- 失效：若无法确定“现在本应剩余多少仓位/止损在哪里”，不得使用本规则。

```text
shadow = replay_original_strategy(bars_through_t)
if shadow.is_open and shadow.direction == always_in_direction:
    qty = min(shadow.remaining_qty,
              floor(account_risk / distance(market, shadow.stop)))
    if qty > 0 and traders_equation_passes:
        enter_market(qty, shadow.direction)
        stop = shadow.stop
```

### TRENDS-C11-S02：四根以上非高潮趋势 Bar 的最小参与

- 类型：强趋势迟到入场触发器。
- 依据，PDF p.214：出现四根以上连续、但并非大到疑似高潮的bull trend bars时，应以小仓位市价参与；bear对称。
- Setup：连续 `4–8` 根同向趋势bar，其中至少75%满足方向实体，累计移动 `1–4ATR`。
- 非高潮过滤：
  - 单bar range低于滚动95%分位；
  - 总移动低于 `4–6ATR`；
  - 未在预定义测量目标/通道过冲处出现末端加速。
- 入场：按S01计算的剩余swing仓位市价入场。
- 止损：原始趋势策略trailing stop；距离>2–4ATR导致最小合约超风险则跳过。
- 加仓：只在后续暂停/回撤形成独立顺势signal后，且总风险仍在上限内。
- 失效：连续bars本身被判定为高潮，等待回撤而不追入。

### TRENDS-C11-S03：迟到仓位的统一止损推进

- 类型：多批次管理规则。
- 依据，PDF p.214：后续pullback加仓后，可将整个仓位止损推进到新signal bar外并继续跟踪。
- 所有批次共享一个“当前趋势前提失效”的结构止损，分别记录每批风险和成本。
- 新回撤确认且顺势恢复后，止损只能沿盈利方向推进至新signal/摆动点外1tick。
- 推进前重新计算所有批次的最坏损失；不得因加仓扩大账户初始风险。
- 比较：统一结构止损、分批独立止损、只持有迟到swing不加仓。

### TRENDS-C11-N01：禁止情绪化追满仓

- 类型：`NEGATIVE`。
- 错过原始入场不是扩大仓位的依据；追入量不得超过原策略此时应剩余的仓位。
- “已有浮盈像在冒别人的钱风险”不成立；迟到入场和原持仓都按当前市值及同一未来损失衡量。
- 若当前止损距离和剩余目标使期望不再为正，即使趋势很清晰也不得迟到入场。

## 2. 参数与来源

| 参数 | 搜索范围 | 基准 | 来源 |
|---|---:|---:|---|
| 连续趋势bars | 4–8 | 4 | `AUTHOR` 为4根以上 |
| 方向bar占比 | 75%–100% | 100% | `PROXY` |
| 非高潮单bar上限 | range 85%–99%分位 | 95% | `PROXY` |
| 原始剩余仓位 | 初始仓位25%–50% | 33% | `AUTHOR` 示例300剩100；范围为 `EMPIRICAL` |
| 迟到最大止损 | 2–4ATR | 3ATR | `EMPIRICAL`；受最小合约约束 |

## 3. 原文覆盖与验收

| PDF | 主张 | 映射 |
|---:|---|---|
| 213 | 当前买入swing剩余量等价于继续持有原swing | S01 |
| 213 | 使用相同trailing stop并以减仓保持美元风险 | S01 |
| 214 | 四根以上非高潮趋势bars应小仓位参与 | S02 |
| 214 | pause/pullback可加仓并统一推进止损 | S03 |
| 215 | 极强tight channel可能在高周期仍是spike | S02的高潮/结构分层 |

- 回测必须先独立运行原始策略，再从其真实状态生成迟到信号，禁止凭最终趋势构造影子持仓。
- 比较原始按时入场、S01迟到复制、等待下一回撤、完全错过四组。
- 报告迟到后剩余MFE、止损距离、仓位、成本后R和错过末端高潮的比例。
- Figure 11.1仅作章节例证，不作参数拟合或绩效证据。
