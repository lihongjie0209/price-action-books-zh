# 第 2 章：Signs of Strength in a Reversal

## 元数据

- 英文来源：`books/trading-price-action-reversals/en/chapters/09-ch02-signs-of-strength-in-a-reversal.md`
- PDF 页码：108–111
- 图表：无
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Strong Reversal Score

```text
score = context + signal_bar + follow_through + displacement
      + pullback_quality + structure_break + second_signal
score_norm = score / 当时可观察项的最大分值
```

- Bull与bear完全镜像实现；以下阈值均在signal完成后逐bar更新，不使用最终趋势结果。
- 建议把特征分成7组，每组0–2分；`score_norm >= 0.65–0.80`为strong reversal候选。
- 高相关特征（例如close-on-high与small upper tail）同组封顶，避免重复计分制造虚假置信度。

## 2. 规则卡

### REVERSALS-C02-S01：Strong Reversal Signal Bar

- 类型：信号bar评分。
- 依据，PDF p.108–110：强反转起始bar有大方向body、小或无tails，形成时大部分时间靠近方向极值，bar内回撤小于约四分之一。
- Bull：`body/range >= 0.60–0.75`、upper tail≤`0–0.20 range`、close percentile≥`0.80`；bear镜像。
- Range至少为近`20bars`中位range的`1.0–1.5倍`，防止tiny bar高body比误判。
- 有intrabar数据时要求最大回撤≤25% growing range；仅OHLC时该项记missing，不做推断。

### REVERSALS-C02-S02：Two-to-Three-Bar Follow-Through

- 类型：反转确认。
- 依据，PDF p.108–110：随后2–3bars继续有至少平均大小的方向body，是强度证据。
- Signal后3bars中至少2根同向body；body≥近`20bars`全部body中位数，累计推进≥`1.0–1.5ATR`。
- Opposite close、强反向bar或收回signal midpoint降低评分；穿回signal另一端使候选失效。
- Entry版本比较signal stop、首follow-through close和首次小pullback。

### REVERSALS-C02-S03：Five-to-Ten-Bar Reversal Spike

- 类型：持续动量状态。
- 依据，PDF p.108–110：spike可延长5–10bars，最多仅一bar左右pullback，并反转旧趋势的多个bars、swings和flags。
- Rolling窗口`5–10bars`；方向bars占比≥70%，最大连续逆向bars≤1–2。
- 累计位移≥`2–4ATR`，穿越至少一个旧swing/flag；每多穿一个结构提高score但设置封顶。
- Spike确认后按新Always-In趋势管理，首个正常pullback优先顺新方向。

### REVERSALS-C02-S04：Gap-Like Urgency Features

- 类型：微观连续性评分。
- 依据，PDF p.108–110：强bull spike可出现low接近prior close、open高于prior close、close近high；bear镜像，并产生“等不到pullback”的紧迫感。
- Bull每bar特征：`low >= prior.close-1tick`、`open > prior.close`、`close >= high-1tick`；bear镜像。
- 用ATR版本容差`0.02–0.05ATR`跨品种测试；5–10bar窗口出现≥1–3次加分。
- “紧迫感”仅由连续成交与浅回撤代理，不使用主观人工标签。

### REVERSALS-C02-S05：Multi-Level Displacement

- 类型：结构突破强度。
- 依据，PDF p.108–111：强反转远距离穿越EMA、trend lines、prior swing与多根旧bar，且收盘穿越比仅极值刺穿更强。
- 统计首2bars的`close_reversal_count`与`extreme_reversal_count`，回看`5–20bars`。
- Close跨越多个旧close/high/low、EMA及确认swing，每类独立计分；净穿越距离需≥`0.20–0.50ATR`。
- `close_reversal_count`权重大于仅high/low跨越数，例如2:1；level必须在break前已知。

### REVERSALS-C02-S06：Delayed and Shallow First Pullback

- 类型：首次回调质量。
- 依据，PDF p.108–110：首pullback在至少3bars后才出现，仅持续1–2bars、横向而小、前bar不是强反向reversal，且不触breakeven stop。
- `bars_to_pullback >= 3`；pullback bars=`1–2`，depth≤`0.25–0.50 spike`且overlap高。
- Pullback low/high不越首entry成本后breakeven；若越过则强度降级但不事后删除candidate。
- 合格H1/H2或L1/L2 signal bar方向body强，可作为顺新趋势add-on。

### REVERSALS-C02-S07：Context and Second-Signal Score

- 类型：反转背景门控。
- 依据，PDF p.108–110：强trend-line break后的higher/lower-low test、second attempt、channel-line overshoot及重要swing假突破提高反转概率。
- Context至少一项：显著旧trend-line break+极值测试；channel overshoot；重大swing假突破；近几bar第二次反转尝试。
- Second signal窗口`3–10bars`；第一次失败极值与第二次signal在`0–0.50ATR`区域内。
- Strong old trend要求至少2项背景；two-sided/range环境可降低门槛。

### REVERSALS-C02-S08：Weak Retest of Old Extreme

- 类型：测试腿质量评分。
- 依据，PDF p.109–110：测试旧低/高的pullback若momentum弱、overlap多、含较多新方向bars，并在EMA或旧trend line失败，支持反转。
- Retest leg overlap ratio≥`0.50–0.70`，old-direction body累计小于break leg的`0.5–0.8倍`。
- 至少30–50% bars为新方向close；在EMA/旧线前`0–0.20ATR`停止或反转加分。
- 强旧方向spike穿越极值则取消retest setup，不继续fade。

### REVERSALS-C02-S09：Regime-Adaptive Reversal Threshold

- 类型：评分阈值调节。
- 依据，PDF p.111：旧趋势越强，逆势交易需要越强反转；two-sided趋势可接受较弱setup，range边缘甚至不一定需要reversal bar。
- Strong old trend：`score_norm >= 0.75–0.85`且S05/S07必须成立。
- Two-sided trend：阈值`0.60–0.75`；confirmed range edge：`0.45–0.60`，但只取scalp目标。
- Trend-continuation方向（如wedge flag恢复大趋势）可接受方向不佳signal bar，但仍须结构与EV合格。

### REVERSALS-C02-S10：Score-Based Swing Fraction

- 类型：仓位与目标管理。
- 依据，PDF p.111：强度特征越多，countertrend获利概率越高，可更积极保留swing；强trend-line break通常带来更远、更多腿的move。
- 初始账户risk保持固定，不用高分扩大最大loss；只调节退出结构。
- `score 0.60–0.70`：全仓scalp/1R；`0.70–0.80`：保留25–50%；`>0.80`：保留50–75%至2 legs/结构目标。
- 分数区间必须训练期校准；与固定退出比较净EV、回撤与尾部风险。

### REVERSALS-C02-S11：Trending-Anything Composite

- 类型：序列一致性特征。
- 依据，PDF p.109–110：trending closes、highs、lows或bodies均为新方向强度迹象。
- 在`3–10bars`窗口分别计算方向单调比例；例如bull higher closes/highs/lows比例≥`0.60–0.80`。
- 至少2类序列达标加分，4类同时达标封顶；容许1tick/`0.03ATR`相等噪声。
- 与S03/S04相关，组合模型需正则化或组内封顶。

### REVERSALS-C02-N01：Strong Trend 未破坏前禁止普通逆势交易

- 类型：`NEGATIVE`硬否决。
- 依据，PDF p.111：强趋势中必须先有trend-line break，或至少从channel overshoot发生climactic reversal。
- 两者均不成立时，countertrend reversal实际交易数必须为零。
- Range双向reversal是独立regime，不受此禁令误杀。

### REVERSALS-C02-N02：禁止将相关特征当作独立证据相乘

- 类型：`NEGATIVE`模型约束。
- 依据：本章多个强度描述来自同一根bar或同一spike，量化时高度相关。
- Body ratio、tail、close location归为signal组；gap-like、trending序列归为continuity组，各组封顶。
- 概率由样本外校准，不以“命中N项”直接宣称固定胜率。

### REVERSALS-C02-N03：反转强度不保证 Trend Reversal

- 类型：`NEGATIVE`标签约束。
- 依据，PDF p.110–111：部分反转只形成小countertrend swing，另一些才形成相反趋势。
- 分开标注`scalp_success, two_leg_success, always_in_flip, opposite_trend`，不得只保留最终大反转。
- 仓位和target由实时score决定，不能用最终标签回填早期置信度。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 108–109 | bull reversal bar、follow-through、5–10bar spike、gap-like连续性、背景、浅首回调与多level突破 | S01–S08、S11 |
| 109–110 | bear镜像特征、second signal、overshoot、重要swing、trending-anything与弱retest | S01–S08、S11 |
| 110–111 | swing与trend reversal区分、旧trend强度门槛、break强度决定腿数/距离 | S09–S10、N01、N03 |
| 111 | strong/two-sided/range/continuation环境的不同反转要求 | S09、N01 |

## 4. 回测验收

- Bull/bear实现逐字段镜像测试；相反价格序列的score误差应为零或仅来自tick rounding。
- 每项特征保存计算窗口、阈值、`valid_from`和missing状态；intrabar未知项不得由OHLC臆造。
- Score使用分组封顶，并通过walk-forward probability calibration报告Brier score、可靠性曲线与置信区间。
- 候选全集同时报告scalp、two-leg、Always-In flip和opposite-trend四类结果，避免只选择大赢家。
- 不同old-trend strength与regime分别报告样本数、净EV、MAE/MFE和退出后延伸。
- Strong-trend无break/overshoot禁令及未来信息禁令必须有自动测试。
- 固定bar/tick阈值映射ATR/ADR并做跨品种、周期和波动状态敏感性测试。
- 本章为特征假设清单，不把作者描述当作已验证概率或绩效证据。
