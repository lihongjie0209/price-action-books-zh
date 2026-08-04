# 第 17 章：Patterns Related to the Premarket

## 元数据

- 英文来源：`books/trading-price-action-reversals/en/chapters/26-ch17-patterns-related-to-the-premarket.md`
- PDF 页码：356–358
- 图表：Figure 17.1–17.2；正文与图注已完整说明规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 双 Session 数据定义

```text
RTH = regular day-session bars
GLOBEX = continuous overnight + RTH bars
gap_size = abs(RTH_open - previous_RTH_close) / ATR_RTH
ema_conflict = sign(close-EMA_RTH) != sign(close-EMA_GLOBEX)
opening_momentum = point-in-time slope/ATR + directional trend-bar score
```

- RTH与Globex可以在同一时刻以不同形态给出同方向信号；二者是并行解释，不应事后拼成一个更强信号。
- Tick/volume bar含开盘前成交，必须用交易所时间戳标注RTH open，不能靠bar外观猜测开盘。

## 2. 规则卡

### REVERSALS-C17-S01：Session Boundary Annotation

- 类型：数据完整性规则。
- 依据，PDF p.356：Globex tick/volume图的RTH开盘不明显，包含开盘时刻的bar通常也含开盘前ticks。
- 用交易所calendar、时区与DST标记`RTH_open_timestamp`；跨界bar标记`mixed_session=true`。
- 跨界bar不得被错误视为纯RTH首bar；测试拆bar与保留原bar两种版本。

### REVERSALS-C17-S02：Globex Extreme Magnet Overlay

- 类型：可选关键位覆盖层。
- 依据，PDF p.356：Globex high/low倾向在day session被测试，overnight形态也可能在开盘后完成。
- 在RTH open前冻结Globex high/low；距离现价`0.1–1.0 ADR`时加入magnet/target特征。
- 极值不得单独触发入场，必须与RTH或预先冻结的Globex setup结合。

### REVERSALS-C17-S03：Single-Chart Execution Policy

- 类型：执行复杂度控制。
- 依据，PDF p.356–357：开盘快速，多数交易者无法同时正确分析两张图；宁可漏掉偶发交易也不要因混乱亏损。
- 生产版本在session开始前冻结为`RTH-only`或`Globex-only`，盘中不得按结果切换。
- 双图版本仅作自动化研究，并显式计入信号冲突、决策延迟和订单错误代理成本。

### REVERSALS-C17-S04：Equivalent-Signal Mapping

- 类型：跨图信号对应研究。
- 依据，PDF p.356–357：大多数Globex交易在RTH-only图上也有同时发生的price-action理由，但形态名称可能不同。
- 以相同clock-time窗口`±0–1 bars`匹配两图信号，比较方向、触发价与实际成交，不要求pattern label相同。
- 输出`both/same-direction`、`conflict`、`Globex-only`、`RTH-only`四类，验证单图漏失成本。

### REVERSALS-C17-S05：Large-Gap Opening EMA Suppression

- 类型：盘初指标门控。
- 依据，PDF p.356–358：大gap回补时RTH与Globex EMA可方向相反，RTH EMA在前`30–90min`甚至`1–2h`不可靠。
- 当`gap_size`超过训练期阈值（搜索`0.5–1.5 ATR`）且`ema_conflict=true`时，RTH EMA方向特征权重置零或降至`0–25%`。
- EMA恢复需两图斜率/价格位置一致，或RTH至少积累`6–24`根5分钟bars；阈值walk-forward选择。

### REVERSALS-C17-S06：Opening Momentum Overrides EMA

- 类型：方向优先级规则。
- 依据，PDF p.356、358：大gap后若市场强势回补，实际动量比盘初RTH EMA更能反映价格行为；两图动量向上时应找多头setup。
- S05生效时，方向由连续趋势棒、收盘位置、回补速度、摆动HL/LH与突破跟进组成的momentum score决定。
- 只有score越过训练期阈值才顺动量入场；低分时保持UNCERTAIN，不能简单反向使用EMA。

### REVERSALS-C17-S07：First-Bar Failure Reversal

- 类型：开盘反转策略。
- 依据，PDF p.357：首bar若为trend bar通常可作scalp setup；若失败，尤其出现相反trend bar，则形成反向setup。
- 首RTH纯bar为趋势棒时按其方向stop entry；目标`1R`，超时`1–3 bars`。
- 若未达目标且相反强趋势棒收回首bar突破/穿越其另一端，退出并允许反向入场；两腿独立计成本。

### REVERSALS-C17-S08：Premarket Pattern Completion

- 类型：隔夜形态延续研究。
- 依据，PDF p.356–357：Globex中的final flag等形态可在RTH初段完成，同时RTH图会给出独立breakout-pullback等理由。
- 开盘前冻结未完成形态及失效点；仅允许RTH开盘后实时触发，不事后重画overnight pivots。
- 比较必须要求RTH独立确认与只凭Globex触发两个版本，主策略优先前者。

### REVERSALS-C17-N01：禁止盘中机会驱动切换图表

- 类型：`NEGATIVE`执行约束。
- 依据，PDF p.356–357：快速在两图间切换会减慢反应并增加entry、stop和target下单错误。
- Session内chart regime保持不变；任何切换只能次日生效并记录配置版本。

### REVERSALS-C17-N02：盘初不得机械服从 RTH EMA

- 类型：`NEGATIVE`特征约束。
- 依据，PDF p.356–358：大gap时RTH EMA可能持续下倾，而真实/Globex动量已明显向上。
- S05条件成立时，EMA不得单独否决强顺动量交易，也不得单独批准逆动量交易。

### REVERSALS-C17-N03：Globex 信息不是必需条件

- 类型：`NEGATIVE`依赖约束。
- 依据，PDF p.356–357：day session本身提供优良price action，大多数同一交易有RTH-only理由。
- 维持可独立运行的RTH-only基线；无overnight feed不得导致核心系统停止。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 356 | Globex bar开盘边界、overnight极值测试、单图选择、大gap下EMA冲突与动量优先 | S01–S06、N01–N03 |
| 357 | 两图同刻不同形态、首bar scalp及失败反转、EMA可给不同有效setup | S03–S08、N01 |
| 358 | 大gap前30–90分钟RTH EMA无帮助，Globex EMA与共同上行动量 | S05–S06、N02 |

## 4. 回测验收

- Session calendar、DST、RTH边界及跨界tick/volume bar全部point-in-time；人工抽查开盘bar归属。
- RTH-only、Globex-only和双图研究使用相同clock-time母样本，禁止按bar序号直接错配。
- 报告双图信号同向率、冲突率、单图漏失率、延迟、净EV及订单错误/成本敏感性。
- 大gap阈值、EMA抑制时长和momentum score用walk-forward选择，并按gap方向、大小和开盘30/60/90分钟分层。
- 首bar失败策略必须模拟实际stop触发、反手双份成本及同bar路径歧义。
- Globex high/low和未完成形态只能使用RTH open前已知值；禁止事后修订极值或pivots。
- Figure 17.1–17.2只作跨图对应案例，不作为EMA窗口、成功率或收益证据。
