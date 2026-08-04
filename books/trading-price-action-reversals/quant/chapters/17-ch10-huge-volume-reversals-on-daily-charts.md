# 第 10 章：Huge Volume Reversals on Daily Charts

## 元数据

- 英文来源：`books/trading-price-action-reversals/en/chapters/17-ch10-huge-volume-reversals-on-daily-charts.md`
- PDF 页码：265–267
- 图表：Figure 10.1–10.2；正文与图注已完整说明规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Daily Capitulation Candidate

```text
volume_ratio = daily_volume / median(volume, 20–60 sessions)
selloff_return = close / close_N_days_ago - 1
reversal_score = volume_extreme + gap_down + channel_overshoot + bull_close
```

- 巨量只是climax候选，必须与daily price action结合；无bullish reversal时禁止fade强bear trend。
- 目标通常是持续数日至数周的two-leg rally/EMA test，不预设公司基本面已恢复或长期牛市反转。

## 2. 规则卡

### REVERSALS-C10-S01：Daily Huge-Volume Sell-Climax Detector

- 类型：日线候选检测。
- 依据，PDF p.265–267：steep daily bear trend后成交量约近期平均5–10倍可能表示capitulation；案例也涵盖3倍前日、10倍月均及15倍常态。
- Old trend：`10–60sessions`负斜率、价格低于EMA且drawdown显著。
- `volume_ratio >= 5–10`为high tier，`3–5`为medium；同时报告相对前一日volume ratio。
- 只生成candidate，不因volume独立下单。

### REVERSALS-C10-S02：Gap-Down Strong Bull-Close Entry

- 类型：climactic daily reversal主策略。
- 依据，PDF p.265–266：巨大gap down、bear channel overshoot后强bull trend close显著提高可盈利long概率。
- Gap≤`-1–3ATR / -3%至-10%`，当天bull body≥60%、close位于range上25%、从low反弹≥`1ATR`。
- Aggressive在close入场；conservative在次日突破signal high或5分钟gap-close失败反转入场。
- Stop在climax low外；qty按gap/overnight风险缩小。

### REVERSALS-C10-S03：Two-Leg / EMA Rally Target

- 类型：持仓管理。
- 依据，PDF p.265–266：合格daily climax reversal通常至少two legs up并穿/测EMA，持仓数日至数周。
- Target1=daily EMA/1R，平`25–50%`；余仓等待pullback+second leg或2R。
- Pullback形成HL/gap test可追加；stop移至确认HL外。
- Horizon测试`3–30sessions`、legs `1–3+`，不把two legs当保证。

### REVERSALS-C10-S04：Next-Day Gap Execution Paths

- 类型：次日执行方案。
- 依据，PDF p.266：climax day后gap up，可买open、等test后新intraday high，或在5分钟gap-close attempt失败时买reversal。
- 三个execution版本预注册并共享daily event；open版计full gap slippage。
- Test版要求回撤不破daily signal low，5分钟形成bull reversal/failed gap close。
- 每个版本独立stop/成本，不从事后最佳entry择优。

### REVERSALS-C10-S05：Relative-Volume plus Price-Action Ranking

- 类型：多标的选择。
- 依据，PDF p.266–267：同一时期LEH与BSC均巨量，强bull reversal close的LEH明显优于close near low的BSC。
- Cross-sectional score优先`close_location, bull_body, recovery_from_low, channel_reentry`，volume ratio仅辅助。
- 同日多个candidate按score排序并保持组合risk上限；不得因公司规模/“不可能再跌”加分。
- 样本外比较volume-only与price+volume的增量表现。

### REVERSALS-C10-S06：Lower-Volume Retest / Divergence Overlay

- 类型：可选确认特征。
- 依据，PDF p.265：1分钟强bear trend的巨量bar常非最终低点，可能再有1–2个lower lows且volume较低；daily也可研究类似路径。
- 仅作overlay：climax candidate后`1–5bars/sessions`创新低而volume下降、并有bull signal。
- 不查看intraday volume作为5分钟主入场依据；不同周期分开验证。
- 无稳定增量校准/EV则从生产模型删除。

### REVERSALS-C10-S07：Channel-Overshoot Reentry Strength

- 类型：结构确认。
- 依据，PDF p.266–267：跌破bear channel后若强收回line支持反转；close远低于line说明channel breakout强。
- Channel line在climax前以confirmed lows冻结；计算close相对line距离。
- Close重回line上且S02成立加分；仍在line下`>0.20–0.50ATR`则由N01否决。
- 不要求线条完美，line仅作price-action score之一。

### REVERSALS-C10-N01：Huge Volume 无 Bullish Price Action 禁止抄底

- 类型：`NEGATIVE`硬否决。
- 依据，PDF p.266–267：BSC巨量bear barclose near low、无channel reversal，次日仍可再跌80%；volume不能保证rally。
- Bull-close/reversal条件未达时，long实际交易数必须为零。
- 不以“已跌很多”“大型机构不可能倒”或基本面直觉替代stop与price action。

### REVERSALS-C10-N02：Intraday Volume 不作主要反转信号

- 类型：`NEGATIVE`周期约束。
- 依据，PDF p.265：1/5分钟volume预测不可靠，主交易图应依赖price action。
- Intraday model不能由volume threshold单独入场；仅允许S06研究overlay。
- Daily与intraday结论分开，禁止跨周期外推5–10倍阈值。

### REVERSALS-C10-N03：生存者偏差与公司事件必须保留

- 类型：`NEGATIVE`数据治理。
- 依据，PDF p.266–267：LEH、BSC后来破产/被收购，短期成功rally不代表长期安全。
- 数据集必须包含退市、破产、并购、停牌与极端gap，不得只用当前成分股。
- 回测标记corporate actions并使用当时可交易价格，不能用后见基本面过滤。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 265 | daily steep bear trend、5–10x volume、gap/bull close、two-leg EMA rally与intraday volume限制 | S01–S03、S06、N02 |
| 266 | Figure 10.1：channel overshoot、strong bull day、close/high/next-day entries与HL second leg | S02–S04、S07 |
| 266–267 | Figure 10.2：巨量无bull action仍暴跌、相对标的选择与长期公司风险 | S05、S07、N01、N03 |

## 4. 回测验收

- Candidate在daily close按当时volume与price生成；最终破产、反弹或退市不得进入信号特征。
- 使用含退市证券的point-in-time universe与corporate-action-adjusted/raw执行双数据。
- Volume-only、price-only、price+volume和channel overlay在同一母样本比较校准与净EV。
- Aggressive close、next-open、daily-high break及5分钟test版本逐一计gap/slippage/成本。
- 报告two-leg/EMA到达率、最大隔夜gap、MAE/MFE、持仓天数与尾部损失。
- No-bull-action禁令、intraday-volume-only禁令及生存者偏差检查设自动测试。
- Volume/gap/body/horizon阈值做walk-forward、跨市场和volatility sensitivity。
- Figure 10.1–10.2仅作章节例证，不作参数或绩效证据。
