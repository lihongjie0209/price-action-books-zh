# 第 15 章：通道

## 元数据

- 英文来源：`books/trading-price-action-trends/en/chapters/21-ch15-channels.md`
- PDF 页码：251–280
- 图表：Figure 15.1–15.8；正文已逐项说明，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 通道状态分类

```text
channel_slope = robust_regression_slope(mid_price, N) / ATR20
channel_width = median(upper_line - lower_line) / ATR20
overlap_rate  = mean(overlap(t,t-1) >= 0.5)
pullback_depth = median(countertrend_swing / prior_trend_swing)
```

- `TIGHT_TREND_CHANNEL`：斜率大、宽度小、回撤多为1bar或极浅，只顺势。
- `BROAD_TREND_CHANNEL`：斜率中等、5–10bar摆动和双向交易，允许边缘双向。
- `WEAK_SLOPING_RANGE`：斜率小、高重叠，按倾斜交易区间处理。
- `TRANSITION`：前两腿尚不能确认channel，只记录候选；第二次回撤完成、第三推进开始后确认。

| 参数 | Tight | Broad | Sloping range | 来源 |
|---|---:|---:|---:|---|
| `abs(slope)` | >0.10 | 0.03–0.10 | <0.03 ATR/bar | `PROXY` |
| width | <1.5 | 1.0–4.0 | 1.0–5.0 ATR | `PROXY` |
| overlap rate | <0.45 | 0.35–0.70 | >0.65 | `PROXY` |
| median pullback | <0.35 | 0.30–0.80 | >0.60 | `PROXY` |

## 2. 规则卡

### TRENDS-C15-S01：通道早期顺势回撤

- 类型：完整顺势策略。
- 依据，PDF p.252–255：channel早期优先顺势；tight channel代表强趋势，初学者只应顺势。
- Setup：第二次回撤完成并确认channel；价格位于顺势可接受区域，不靠近上层关键阻力/支撑。
- Tight：买/卖首次小回撤、prior bar不利极值或High/Low 1/2失败。
- Broad：在trend line侧等待顺势reversal或第二入场。
- 入场：stop entry；limit版本只在趋势分数≥0.75且排队模型可用时测试。
- 止损：最近channel swing外。
- 目标：对侧channel line、趋势新极值、1R/2R。
- 失效：反向spike突破channel和EMA并跟进，转S06。

### TRENDS-C15-S02：宽通道边缘双向交易

- 类型：边缘scalp策略。
- 依据，PDF p.254、263、275–280：宽channel是倾斜交易区间，可在两侧交易；中部有磁性。
- 仅限 `BROAD_TREND_CHANNEL/WEAK_SLOPING_RANGE`。
- 顺势：lower/upper trend-line带的回撤反转。
- 逆势：trend-channel-line带、已有selling/buying pressure且出现第二信号。
- 入场：边缘反转bar stop，或预设limit；距边界 `0–0.30ATR`。
- 止损：边界外 `0.15–0.75ATR` 或结构极值。
- 目标：中线第一目标、对侧第二目标；逆势至少在中线减仓。
- 禁入：通道中间40%、第二半交易时段逆势加仓、或强Always-In方向尚无反向spike。

### TRENDS-C15-S03：第三推进/通道过冲反转

- 类型：完整反转策略。
- 依据，PDF p.252–253、259–260：channel通常至少三腿，第三推进及trend-channel-line过冲后反转概率提高。
- Setup：实时识别3–5个同向推进；第三推进触及/越界 `0.05–0.50ATR`，并接近预定义目标。
- 触发：强反向bar、第二次反转，或回到channel内。
- 入场：反向stop；tight channel必须等第二信号或lower high/higher low。
- 止损：最终推进极值外。
- 目标：trend line、channel起点、两腿/10bars、1R/2R。
- 失效：通道外突破获得2bars强跟进，转S05。

### TRENDS-C15-S04：Channel Breakout Failure

- 类型：完整失败突破策略。
- 依据，PDF p.258–265：倾斜区间两侧多数突破失败；突破后重新进入通常测试另一侧并常轻微越界。
- Setup：收盘越过边界 `0.05–0.50ATR`，随后 `1–5bars` 回到channel。
- 入场：回归方向突破反转bar；止损在失败极值外。
- 目标：对侧channel line；若对侧成功突破，追加channel height测量移动。
- 对比突破bar与反转bar强度：
  - 反转明显更强：立即失败分支。
  - 反转弱：等待其失败形成breakout pullback。
  - 力量接近：下一bar决定，不提前入场。
- 无足够空间达到至少0.5–1R时不交易，即使目标方向正确。

### TRENDS-C15-S05：成功突破与 Channel Height 测量移动

- 类型：突破延续与目标规则。
- 依据，PDF p.258、261、264、267：成功突破最低目标约为突破处channel高度；明显超越目标可能进入新趋势。
- 在突破bar时冻结垂直于时间轴的 `H=upper_line-lower_line`，不得事后改用更宽channel。
- 成功条件：边界外1–3bars跟进、或breakout pullback守住边界。
- 入场：跟进或pullback顺势stop。
- 止损：边界内/回测极值外。
- 目标：`0.75H/1.0H/1.25H`，再比较1R/2R。
- 到1H后：弱化则止盈；强收盘继续远超1H则切换新趋势跟踪。
- 多个独立测量目标集中在 `±0.10–0.30ATR` 时作为confluence分层，不重复计算同一几何事实。

### TRENDS-C15-S06：Tight Channel 第一次反向突破过滤

- 类型：反转门控。
- 依据，PDF p.260–261、262–263：steep tight channel第一次反向突破常失败；等待breakout pullback及反向强度。
- 第一次越线只记录，不逆势成交。
- 允许反转需满足：
  - 反向2–3根趋势bar；
  - 穿越EMA；
  - 第一次pullback保持在EMA反向一侧；
  - higher low/lower high及第二入场。
- 若直接race反向，等待通常 `≤5bars` 的首次回撤。
- 若反向突破失败并恢复旧趋势，顺势入场，目标旧极值及初始反转尝试高度等幅。

### TRENDS-C15-S07：Channel Limit Scaling 风险约束

- 类型：高级订单/仓位研究。
- 依据，PDF p.255–257、275–280：channel中机构可能在prior bar外、固定间隔或边界limit加仓；第一腿保本、后腿盈利。
- 只在已确认channel启用；最多 `2–3` 腿，间距 `0.25–1ATR`。
- 每腿下单前按共同结构止损计算总最坏损失，总风险≤账户上限。
- 第二半session只允许顺势scaling；逆势scaling最晚在session 0.5–0.67前停止。
- 退出：加权均价0.5–1R、中线、原始首入价分别测试。
- 成交：触及即成交和排队折损两模型；无上限摊平禁止。

### TRENDS-C15-N01：通道中逆势信号不等于反转

- 类型：`NEGATIVE`。
- 依据，PDF p.254–255、274–276：channel一直尝试反转，很多看似反转的signal只是flag起点；Always-In翻转前只顺势。
- Tight bull channel中的Low1/Low2默认作为买入失败信号候选，而非short；bear对称。
- 真正方向翻转至少需要反向spike突破channel/EMA、跟进和lower high/higher low。
- 禁止以“趋势看起来不可持续”作为入场条件。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 251–252 | channel类型、位置和第三腿后才易确认 | 第1节、S01 |
| 252–255 | early channel顺势；宽channel可双向 | S01、S02 |
| 252–253 | 三推进和真空效应边缘反转 | S03 |
| 255–257 | 成熟channel压力累积、时段与加仓 | S07 |
| 258–261 | channel为倾斜range；突破失败/成功三分支 | S04–S06 |
| 261 | 成功突破目标约channel height | S05 |
| 262–270 | nested/tight channels、各种市场上下文及测量移动 | S01、S04、S05 |
| 271–273 | 线边缘真空、止盈和反转 | S02、S03 |
| 274–276 | channel反转信号常只是旗形 | N01 |
| 277–280 | channel中的limit、stop及双向scaling | S07 |

## 4. 回测验收

- 通道只在第二次回撤确认后生效；之前bars不得回填channel标签。
- 按tight/broad/sloping range、早/中/晚期、session位置和Always-In方向分层。
- S03报告三推进、过冲和第二信号各自增量。
- S04直接统计回归后触及对侧概率、时间、MAE/MFE。
- S05冻结breakout时H，并报告0.75/1/1.25H命中率。
- S07使用固定总风险和真实limit成交，不得以最终均价掩盖途中最大风险。
- Figure 15.1–15.8仅作章节例证，不作参数拟合或绩效证据。
