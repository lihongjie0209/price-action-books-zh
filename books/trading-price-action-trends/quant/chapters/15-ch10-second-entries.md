# 第 10 章：第二次入场

## 元数据

- 英文来源：`books/trading-price-action-trends/en/chapters/15-ch10-second-entries.md`
- PDF 页码：209–212
- 图表：Figure 10.1–10.2；正文已逐项说明，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 第二次入场状态机

```text
IDLE
 -> FIRST_REVERSAL_SETUP
 -> FIRST_TRIGGER_OR_ATTEMPT
 -> OLD_TREND_RESUMES
 -> SECOND_REVERSAL_SETUP
 -> SECOND_TRIGGER
```

“第一次尝试”必须真实可识别，不要求一定成交；但它至少要突破一根prior bar的反转方向极值。旧趋势恢复至少需要一个反向摆动或1–2bars同向收盘。新趋势确认、超过最大间隔或结构被重置后，计数归零。

| 参数 | 宽松 | 基准 | 严格 | 来源 |
|---|---:|---:|---:|---|
| 两次尝试最大间隔 | 20 | 12 | 6 bars | `PROXY` |
| 中间旧趋势恢复 | 0.10 | 0.25 | 0.50 ATR | `PROXY` |
| 最小反转证据 | 突破prior极值 | 同向收盘 | 同向趋势bar | `PROXY` |
| 计数pivot确认 | 1 | 2 | 3 bars | `PROXY` |

## 2. 规则卡

### TRENDS-C10-S01：强动量后的第二次逆势入场

- 类型：完整反转策略。
- 依据，PDF p.209、211：连续2–6根强趋势bars后不做第一次逆势；等待旧趋势恢复，再交易第二次反转。
- Setup：最近 `2–6bars` 至少有 `2–5` 根旧趋势方向趋势bar，净移动 `1–4ATR`。
- 第一次信号：只记录，不成交。
- 等待：旧趋势恢复1–2bars，但恢复强度不得创新大幅极值并继续加速。
- 第二次信号：反转bar、micro double top/bottom或第二次突破prior bar反转极值。
- 入场：第二信号极值外stop entry。
- 止损：第二次测试极值外1tick。
- 目标：EMA、1R、旧趋势spike起点；出现趋势翻转跟进时留至2R/第二腿。
- 失效：第二信号仍处于无反向收盘的tight channel，或旧趋势再次强突破。

### TRENDS-C10-S02：“好成交价，坏交易”过滤

- 类型：禁入过滤器。
- 依据，PDF p.209–210：可靠第二次入场通常与第一次同价或更差；若得到更有利价格，可能说明动量仍强或信号是陷阱。

```text
price_disadvantage = direction * (second_trigger - first_trigger)
```

- 多头 `price_disadvantage≥0` 表示同价/更高；空头经方向调整后同理。
- 若第二次触发比第一次更有利 `0.05–0.50ATR`，要求额外证据：
  - 最近数bars已有反转方向移动>0.25–0.75ATR；
  - 旧趋势线已突破；
  - 第二信号为强趋势bar；
  - 预定义支撑阻力至少一项。
- 无额外证据时跳过；不是自动反向交易。
- 回测必须按价格更好/相同/更差分组，直接检验作者主张。

### TRENDS-C10-S03：第二次入场上下文门控

- 类型：过滤组件。
- 依据，PDF p.210–212：第二次入场本身不够；tight bear channel中的second long、四根bear bars后的High 2以及六根higher lows后的short都应过滤。
- 多头禁止条件：
  - 最近 `4–8bars` 无bull close；
  - 连续 `3–6` 根bear trend bars；
  - highs/lows tight channel向下且未破趋势线。
- 空头对称。
- 通过条件至少一项：反转方向强bar、趋势线突破、旧极值二次失败、micro double、高潮/最终旗形后证据。
- 输出 `second_entry=true` 与 `context_pass=true/false` 两个独立字段，防止回测只保留成功形态。

### TRENDS-C10-S04：二次入场后的跟进与目标

- 类型：交易管理组件。
- 入场后1–3bars出现反转方向强收盘：保留50%–100%仓位寻找第二腿/2R。
- 无跟进但未触及结构止损：首个1R或EMA减仓50%–100%。
- 立即恢复旧趋势：按结构止损，不摊平。
- 成熟高潮后的第二入场另测试作者目标：至少两腿、约10bars；这是 `AUTHOR` 待验证主张，不是保证。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 209 | 第二次入场通常优于第一次 | S01；以条件期望验证 |
| 209–210 | 好的第二次入场通常同价或更差 | S02 |
| 209 | 强动量中等待第一次失败和第二次尝试 | S01 |
| 210 | tight channel中即使second entry也危险 | S03 |
| 211 | 4–6根单向bars/无反向close时等待第二次 | S01、S03 |
| 211–212 | 连续higher lows/bull bars过滤首次short | S03 |
| 212 | 高潮/最终旗形后的反转可预期两腿 | S04 |

## 4. 回测验收

- 同时记录所有第一次和第二次候选，包括未触发、被过滤和失败交易。
- 比较first entry、无条件second entry、动量门控second entry。
- S02按ATR价格差连续分箱，而非只用“好/坏”标签。
- 状态机只用实时bar；不得事后以最终摆动点重新编号。
- 分别报告趋势回撤的顺势第二入场与强趋势末端的逆势第二入场。
- Figure 10.1–10.2仅作章节例证，不作参数拟合或绩效证据。
