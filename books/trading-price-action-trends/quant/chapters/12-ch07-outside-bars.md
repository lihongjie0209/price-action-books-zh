# 第 7 章：Outside Bars

## 元数据

- 英文来源：`books/trading-price-action-trends/en/chapters/12-ch07-outside-bars.md`
- PDF 页码：187–200
- 图表：Figure 7.1–7.4；正文完整描述相关bar关系，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 定义与分类

```text
outside(t) = high[t] > high[t-1] and low[t] < low[t-1]
outside_up = outside(t) and close[t] > open[t]
outside_down = outside(t) and close[t] < open[t]
oo = outside(t) and outside(t-1)
ioi = inside(t-2) and outside(t-1) and inside(t)
```

相等极值版本作为独立宽松定义测试。outside bar 必然完全覆盖 prior bar，因此首先是一段两bar交易区间；只有上下文和收盘强度足够时才按趋势/反转bar处理。

| 特征 | 宽松 | 基准 | 严格 | 来源 |
|---|---:|---:|---:|---|
| 趋势型 `body_frac` | 0.50 | 0.65 | 0.80 | `PROXY` |
| 同向收盘位置 | 0.65 | 0.80 | 0.90 | `PROXY` |
| 中性收盘带 | 35%–65% | 40%–60% | 45%–55% | `PROXY` |
| 大bar range分位 | 70% | 85% | 95% | `PROXY` |
| 边缘inside bar相对range | ≤50% | ≤35% | ≤25% | `PROXY` |

## 2. 规则卡

### TRENDS-C07-N01：裸 Outside Breakout 禁入

- 类型：`NEGATIVE` 基线。
- 依据，PDF p.187：作者认为5分钟大outside bar两端直接突破通常不值得交易，因为止损远且是在一bar区间顶部买/底部卖。
- 默认禁止：仅因 `outside(t)` 就在其两端放OCO并在成交后双倍反手。
- 允许研究的对照：触发价、完整bar另一端止损、固定资金止损、固定账户风险缩仓；同bar双触及时按最坏成交顺序。
- 若结构止损>2ATR，只能缩小仓位或等待回撤，不能用任意小资金止损掩盖形态失效位。

### TRENDS-C07-S01：Outside Bar 作为已有信号的 Entry Bar

- 类型：完整入场框架。
- 依据，PDF p.188、195–196、198–199：outside bar 可作为entry bar，前提是prior bar已经是合格signal，或出现第二次反转/趋势线过冲。
- Setup：在 outside bar 形成前已经有有效挂单：
  - prior bar为方向一致的合格signal；或
  - 趋势线突破/通道过冲后的第二次入场；或
  - 强趋势两段回撤结束。
- 入场：原挂单被bar内反转触发；不因bar后来变成outside而取消正确逻辑。
- 质量确认版本：等待outside收盘，要求方向实体和收盘位置达标，再突破其极值入场。
- 止损：完整outside bar另一端，或原setup结构失效位；按较合理的结构位计算固定风险仓位。
- 目标：1R/2R、前趋势极值和第二腿。
- 失效：outside在区间中部收盘、实体弱或后续无跟进。

### TRENDS-C07-S02：反转第一腿中的 With-Trend Outside

- 类型：完整趋势启动策略。
- 依据，PDF p.188–190：旧趋势强、反转后形成更高低点/更低高点时，同向outside可能代表一方突然接管；被困旧趋势交易者推动至少1–2bars和第二腿。
- Setup：
  1. 旧趋势线已突破并出现强反向第一腿。
  2. 首次回撤形成更高低点/更低高点。
  3. 回撤突破先诱发旧趋势入场，随后同一bar反转为新方向outside。
- 入场：新方向突破prior bar极值时，或outside收盘确认后。
- 止损：outside极值或更高低点/更低高点结构外。
- 目标：第一腿新极值；余仓寻找第二腿和2R。
- 失效：后续1–2bars无跟进并收回outside 60%以上。
- 计数：功能上的新趋势起点是outside前的higher low/lower high，而非图上绝对极值，防止腿数错误。

### TRENDS-C07-S03：交易区间 Outside Fade

- 类型：区间边缘反转策略。
- 依据，PDF p.188、193–197：区间中部outside无意义；其后在outside高/低附近形成小bar时可fade，失败突破常在数bars内发生。
- 上下文：`regime=RANGE`。
- 禁入：outside中心位于大区间中间50%，或形成oo/多根大尾重叠bars。
- Setup：outside后 `1–5bars` 在其上/下25%边缘形成小bar，且小bar实体指向区间内部。
- 入场：区间内部方向突破小bar。
- 止损：outside极值外或失败突破最终极值外。
- 目标：outside中点、大区间中点、对侧边缘。
- 若市场直接突破outside，不追；等待失败突破fade或成功突破回撤。

### TRENDS-C07-S04：IOI Breakout / Failed IOI

- 类型：双分支策略。
- 依据，PDF p.188、193–194：ioi可按第二inside bar突破交易，但大inside或barbwire中容易失败；区间高位小bear inside向下突破更合理。

#### 有方向版本

- ioi位于区间边缘、趋势回撤或第二次入场位置。
- inside bar range≤outside range的25%–50%，收盘方向与计划一致。
- 触发：inside bar方向极值外1tick；止损为outside另一端或结构位。

#### 中性 breakout mode

- 只有目标空间两侧均≥1R才放OCO。
- 一侧成交立即取消另一侧；不自动双倍反手。
- 在barbwire/中部禁止。

#### 失败分支

- 触发后1–3bars回到ioi内，突破entry bar反方向极值。
- 向失败方向反向入场，止损放失败极值外，目标ioi另一端/1R。

### TRENDS-C07-S05：强收盘 Outside 作为趋势 Bar

- 类型：顺势延续或区间边缘反转。
- 依据，PDF p.196、198–199：outside若大实体、收在极值并困住错误方向交易者，可像强趋势bar而非区间bar运作。
- Setup：`body_frac≥0.65–0.80`、收盘位置≥0.80–0.95，并满足：
  - 与现有强趋势一致；或
  - 区间边缘/趋势末端反向，且突破重要水平；或
  - 失败High/Low 1/2造成陷阱。
- 入场：收盘后或突破outside方向极值；风险>2ATR等待回撤。
- 止损：outside另一端或陷阱结构外。
- 目标：新极值、1R/2R、被突破区间高度。
- 禁入：最近3–6bars大幅重叠且长影；这类oo/outside通常只是更大区间。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 187 | outside定义、双向控制及裸突破风险 | 第1节、N01 |
| 188 | prior signal合格时outside可作entry bar | S01 |
| 188 | 区间中部outside无意义；边缘小bar可fade | S03 |
| 188 | ioi只有在有足够目标空间时才交易 | S04 |
| 188–190 | 反转第一腿with-trend outside及被困交易者 | S02 |
| 190 | 不确定时等待更多价格行为 | 全部规则的禁入默认 |
| 191–192 | 强bear趋势outside up只考虑向下；横盘outside不突破 | N01、S05 |
| 193–194 | 大ioi突破易失败；边缘小bar失败突破可交易 | S03、S04 |
| 195–197 | oo和大尾重叠bars是区间；barbwire突破常失败 | S03、S05 |
| 198–200 | 两段回撤后的outside entry及失败High2 outside down | S01、S02、S05 |

## 4. 回测验收

- 按趋势、区间边缘、区间中部、反转第一腿、趋势成熟度分层。
- 比较outside极值突破、prior signal触发、outside收盘确认和回撤入场。
- S02报告第一新极值、第二腿、达到目标前MAE和所需bars。
- S03/S04必须使用实时区间边界；不得事后挑选outside所在位置。
- OCO与反手策略使用保守同bar顺序并计入滑点；无法确定时标记歧义交易。
- 大outside风险采用固定账户风险缩仓，同时报告因合约最小单位无法成交的信号。
- Figure 7.1–7.4仅作为章节例证，不作为参数拟合或绩效证据。
