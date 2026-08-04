# 第 12 章：形态演化

## 元数据

- 英文来源：`books/trading-price-action-trends/en/chapters/17-ch12-pattern-evolution.md`
- PDF 页码：217–222
- 图表：Figure 12.1–12.2；正文已完整说明演化链，未额外查看图片
- 状态：量化状态机规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 不可回写的形态事件模型

每个bar只更新当时可见的候选，不得在形态完成后把早期bars重标成“显然属于最终形态”。

```text
PatternEvent {
    id, family, direction,
    first_detected_at,
    confirmed_at,
    trigger_price,
    scalp_target,
    invalidation_price,
    status: candidate | armed | triggered | target_hit |
            failed_fast | expired_sideways | superseded
    parent_id | null
}
```

`parent_id` 只表示新形态使用了旧形态结构，不代表可以修改旧交易的实时判断。

## 2. 规则卡

### TRENDS-C12-S01：快速形态失败反向交易

- 类型：通用失败策略。
- 依据，PDF p.217：任何形态都可能失败；未达到scalp利润即快速反转，会迫使原方向交易者止损并推动反向scalp。
- Setup：原形态已真实触发，但在 `1–5bars` 内未达到预先冻结的最低scalp目标 `0.5–1R`。
- 失败确认：价格穿过signal/entry结构的反向失效位，或出现反向强趋势bar并跟进。
- 入场：原交易退出的同一结构位反向stop entry；同bar反转采用最坏成交和滑点。
- 止损：失败后的最终极值外。
- 目标：0.5R、1R、原形态另一侧；有强跟进时留至2R。
- 失效：失败后没有跟进而进入横盘，转S02。

### TRENDS-C12-S02：横盘后新形态独立化

- 类型：信号去关联规则。
- 依据，PDF p.217：原形态失败后若横盘若干bars才产生新形态，被困交易者大多已退出，应将新形态视为独立。
- 若失败后横盘 `5–20bars`，且价格至少两次穿越原入场、波动压缩、原方向持仓估计衰减，则旧事件标记 `expired_sideways`。
- 新形态不继承“被困者燃料”加分；按其自身regime、位置、signal和目标重新计算。
- 参数 `5–20bars`、穿越次数2–4、压缩20%–60%均为 `PROXY`。

### TRENDS-C12-S03：演化链状态库

- 类型：组合规则。
- 依据，PDF p.217–219给出的常见演化：
  - expanding triangle 5腿→7腿；
  - micro trendline breakout失败→breakout pullback；
  - final flag反转失败→顺势breakout pullback；
  - 形态扩大为wedge或更大range/final flag；
  - spike-channel→range→double-bottom/top flag。
- 实现：每个子形态独立发事件；新事件可引用parent，但只在自己确认后触发。
- 冲突路由：
  - 当前最新已确认事件优先于数bars前已完成标签；
  - 同时有相反方向事件且分差<0.10–0.20时进入breakout mode或不交易；
  - 强突破/跟进权重大于形态名称。
- 测试：比较独立策略、固定优先级状态机、学习型概率路由，防止手工挑选演化解释。

### TRENDS-C12-S04：首小时双顶—双底 Breakout Mode

- 类型：首小时双向策略。
- 依据，PDF p.218、220–221：首小时double-top bear flag常演化为double-bottom bull flag，反之亦然；第一或第二形态可能产生大移动。
- 窗口：session前 `10%–25%` 或固定前 `6–15bars`。
- 建立上下两个实时确认摆动边界；先出现的一侧形态允许首笔交易。
- 首笔失败：按S01退出/反向；第二个相反形态确认后允许第二笔，但两笔总风险分别独立且当日风险不超上限。
- 若两侧同时接近、没有方向优势：在边界外放OCO，保守处理同bar双触发。
- swing管理：首目标减仓，强breakout保留25%–50%至2R或趋势跟踪。
- 方向先验：比较bull/bear spike的净移动、趋势bar数量和跟进；更强一侧只用于调分，不禁止另一侧。

### TRENDS-C12-N01：禁止事后形态命名优化

- 类型：`NEGATIVE`。
- 同一走势可被合理称作不同spike/channel或更大形态；名称不是收益来源。
- 每个检测器、参数和优先级在训练阶段冻结；不得在失败后改称另一个形态并删除原失败。
- 可靠形态约40%失败是 `AUTHOR` 待验证主张；必须保留所有触发样本才能检验。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 217 | 形态频繁演化；应交易当前价格行为而非旧标签 | 事件模型、S03 |
| 217 | 未达scalp目标的快速失败可反向交易 | S01 |
| 217 | 横盘后新形态应独立处理 | S02 |
| 217–218 | 常见final flag、wedge、spike-channel演化链 | S03 |
| 219 | 可靠形态约40%失败并可扩大 | N01；作为待验证主张 |
| 220–221 | 首小时double top可变double bottom并进入breakout mode | S04 |
| 221 | 多种spike/channel解释都可能合理，强弱更重要 | S03、N01 |

## 4. 回测验收

- 保存逐bar事件日志，证明检测器没有回写 `first_detected_at/confirmed_at`。
- S01按失败发生1–5bars及原目标距离分层，计入反手滑点。
- S02验证横盘时间越长，被困者反向优势是否衰减。
- S04分别报告第一笔、第二笔、两笔组合及未触发OCO。
- 所有失败交易保留；不得只展示最终演化成功形态。
- Figure 12.1–12.2仅作章节例证，不作拟合或绩效证据。
