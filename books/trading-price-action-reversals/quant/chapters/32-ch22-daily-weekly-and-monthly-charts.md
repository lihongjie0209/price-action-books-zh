# 第 22 章：Daily, Weekly, and Monthly Charts

## 元数据

- 英文来源：`books/trading-price-action-reversals/en/chapters/32-ch22-daily-weekly-and-monthly-charts.md`
- PDF 页码：403–415
- 图表：Figure 22.1–22.8；正文逐bar说明已完整覆盖规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 多周期研究边界

```text
HTF ∈ {daily, weekly, monthly}
HTF_R = entry - structural_stop on the signal timeframe
overnight_gap_risk = adverse open beyond prior close/stop
qty = floor(account_risk / (HTF_R + gap_risk_buffer))
```

- Price action形态可跨周期复用，但bar、持仓时间、流动性和隔夜gap完全不同，参数与绩效不可混合。
- Day trader默认只使用昨日高低等可见于5分钟图的长期信息，避免低频HTF仓位干扰日内执行。

## 2. 规则卡

### REVERSALS-C22-S01：Higher-Timeframe Strategy Partition

- 类型：策略与注意力隔离。
- 依据，PDF p.403：日周月信号低频且易分散day trader，昨日高低已可在5分钟图看到。
- HTF仓位、风险预算、订单簿和绩效独立于intraday策略；盘中不得因HTF浮盈亏改变日内信号门槛。
- 比较完全隔离与共享账户版本的机会成本，生产默认隔离。

### REVERSALS-C22-S02：Bar-Size and Overnight Risk Sizing

- 类型：仓位控制。
- 依据，PDF p.403–404：HTF signal bar大、结构stop宽且有overnight风险，应显著缩仓或采用有限风险options。
- Qty按HTF结构R加历史隔夜gap的`90%–99%`分位buffer计算；单股事件风险另加jump haircut。
- 若最小交易单位仍超账户风险，则跳过或转有限风险结构，不收紧结构stop。

### REVERSALS-C22-S03：Strong-Trend Countertrend Scalp Cap

- 类型：逆趋势目标限制。
- 依据，PDF p.403–404：强HTF趋势中的countertrend多数只是pullback，目标应限制为约`1%–2%`。
- 逆HTF AI版本目标搜索`0.5%–2.0%`或`0.5–1R`，超时退出；顺势entry使用独立swing目标。
- 若需隔夜承受的风险大于目标则拒绝，不以高胜率假设弥补。

### REVERSALS-C22-S04：Daily Signal Gap-Pullback Entry

- 类型：HTF信号的盘中执行。
- 依据，PDF p.403–404、406–407：日线buy setup次日gap above trigger时，不追开盘；等5分钟回测gap后opening reversal恢复上涨，bear镜像。
- 无gap时按实际stop穿越daily trigger；有gap时等待RTH pullback测试昨高/trigger/gap并形成反向恢复signal。
- Stop在当日pullback extreme外；若无法盘中监控则gap日跳过。

### REVERSALS-C22-S05：Second-Chance Limit

- 类型：单标的损失控制。
- 依据，PDF p.404：gap-pullback entry失败后应转移注意力，最多只在第二个独立setup再试一次。
- 每个HTF母信号每日最多`2`次entry；第二次需新second-entry/结构确认而非报复性重入。
- 第二次失败后当日锁定该母事件，不影响其他标的扫描。

### REVERSALS-C22-S06：Uncertain Daily Pullback Scaling

- 类型：分批建仓。
- 依据，PDF p.404：daily pullback常无经典reversal bar，较高不确定性应小仓，并可在更低价或恢复后HL加仓。
- 初始`25%–50%`风险；仅在趋势未flip且更低价出现支撑确认，或恢复后形成HL/LH时补仓。
- 全部腿共享总风险上限，向亏损加仓与确认后加仓分开报告。

### REVERSALS-C22-S07：Daily Trigger Intraday Basket

- 类型：扫描与执行联动。
- 依据，PDF p.404：日线setup触发后常形成可供多次5分钟顺势entry的intraday trend；约500万股以上流动性可临时加入观察篮子。
- EOD冻结次日HTF candidates；触发后只运行标准5分钟顺势模块`1–2 sessions`。
- 流动性阈值改用median dollar volume、spread和depth搜索；无法short时不得伪生成成交。

### REVERSALS-C22-S08：Round-Number Vacuum and Overshoot

- 类型：磁体策略。
- 依据，PDF p.404–405、412–413：显著整数可吸引价格形成vacuum，常越过约`5%–10%`后回测并至少一次穿回整数。
- Round level按价格数量级预定义；进入其`2%–10%`磁场且趋势同向时可顺势至level上方分批止盈。
- 越过后需climax/reversal setup才逆向交易，目标回测整数；百分比只作AUTHOR搜索范围。

### REVERSALS-C22-S09：HTF Pattern Reuse Engine

- 类型：跨周期形态复用。
- 依据，PDF p.405–412：H/L2、wedge、final flag、breakout pullback、MTR、spike-and-channel和double均同样出现在日周月图。
- 复用统一pattern接口但ATR窗口、持仓bar数和成本按HTF重新校准。
- 同一HTF event多标签去重；目标可用channel起点、measured move或`1–3R`。

### REVERSALS-C22-S10：Large-Range Uncertainty Regime

- 类型：周/月区间状态。
- 依据，PDF p.408–409、412：大幅retrace削弱旧trend影响并形成large trading range；大涨常接大跌，顶部/底部形态多数失败。
- 当价格深度回撤旧trend且双向swings持续，输出RANGE而非沿用旧AI。
- 区间底部只做有利risk/reward long、顶部short；中部降仓，突破需强bar+跟进。

### REVERSALS-C22-S11：Measured-Move Profit Reaction

- 类型：目标与停顿研究。
- 依据，PDF p.409–410、412：机构常在reward≈risk的measured move减仓，价格可能精确停顿，但多数target最终被趋势突破。
- Measured move只作为partial exit/反转观察区；到达后减`25%–50%`，余仓按趋势trail。
- 反向entry仍需signal，不能因精确触及自动fade。

### REVERSALS-C22-S12：Trend-Line Crowding Break Alert

- 类型：长期趋势线预警。
- 依据，PDF p.410：`5–10 bars`贴近trend line时不久后穿线概率上升；wedge/channel target附近可能两腿修正。
- 最近`5–10 HTF bars`到趋势线距离≤`0.1–0.5 ATR`且反复测试时标记vulnerable。
- 仅降低追趋势仓位；break后需pullback/reversal确认才反向。

### REVERSALS-C22-S13：Cross-Timeframe Trend Conflict

- 类型：周期冲突处理。
- 依据，PDF p.413–414：daily可强涨但monthly仍是bear rally，在月线EMA/旧range阻力形成double-top flag。
- 每个周期保持独立AI；低周期交易目标/仓位在更高周期阻力附近收缩，但不得由HTF单独逆转LTF。
- 输出`aligned/conflicted`并分别报告表现；禁止选图直到方向一致。

### REVERSALS-C22-S14：Late Parabolic-Climax Pullback

- 类型：成熟趋势修正。
- 依据，PDF p.413–414：长`10–20 bars` bull spike后再出大bull bars为parabolic climax，强手多等两腿pullback或逆向布局。
- 趋势年龄+加速斜率+大trend bars达到阈值时停止追高，等待两腿修正的顺势再入或确认MTR。
- 新闻叙事不改变技术触发；只有价格结构解除climax警报。

### REVERSALS-C22-S15：Event-Jump Risk Filter

- 类型：小盘/新闻特殊风险。
- 依据，PDF p.403、415：低机构持有的小公司可因审批/收购新闻暴涨暴跌，坏成交和注意力成本使多数人不应参与。
- 用market cap、median dollar volume、spread、历史overnight jump和single-product/event flags构建jump-risk score。
- 高风险默认禁入；研究版本最多极小仓/有限风险options，并进行停牌与gap-through-stop压力测试。

### REVERSALS-C22-N01：Day Trader 不因低频 HTF 信号分心

- 类型：`NEGATIVE`执行约束。
- 依据，PDF p.403：小HTF仓位造成的注意力损失可能超过收益。
- 日内生产流程不得显示非必要HTF浮盈亏或触发临时人工干预。

### REVERSALS-C22-N02：无法盘中监控时不交易 Gap Trigger

- 类型：`NEGATIVE`准入约束。
- 依据，PDF p.403–404：gap使日线stop entry复杂，不能监控时最好跳过。
- S04 gap条件成立且无intraday执行能力时submitted orders为零。

### REVERSALS-C22-N03：Round Number 与 Measured Move 不独立反转

- 类型：`NEGATIVE`触发约束。
- 依据，PDF p.404–405、409、413：磁体常overshoot，measured move多仅停顿且随后失效。
- Level只能做目标/context，逆向必须有price-action signal。

### REVERSALS-C22-N04：新闻观点不得覆盖价格结构

- 类型：`NEGATIVE`信息约束。
- 依据，PDF p.413–415：看多新闻/专家观点可出现在parabolic top；特殊新闻股跳跃不可预测。
- 策略不以电视评论或事后新闻情绪作为技术entry；已知事件只用于风险/blackout。

### REVERSALS-C22-N05：高跳跃小盘股默认禁入

- 类型：`NEGATIVE`风险约束。
- 依据，PDF p.403、415：仓位缩小、坏成交、压力和注意力占用抵消大波动收益。
- S15高风险状态下普通股票策略订单为零。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 403 | HTF信号分心、宽stop/隔夜风险、小盘新闻跳跃、逆趋势目标 | S01–S03、S15、N01、N05 |
| 404 | gap pullback、最多第二次尝试、daily不确定加仓、盘中篮子与整数磁体 | S04–S08、N02 |
| 405 | 整数vacuum/overshoot、历史daily图标准price action | S08–S09 |
| 406 | 多种HTF wedge、MTR、breakout pullback与AI冲突 | S09、S13 |
| 407 | 日线buy trigger gap后5分钟回补反转执行 | S04 |
| 408 | weekly趋势深回撤后成为large range | S10 |
| 409 | climax/wedge、range中top失败、measured move停顿与突破 | S10–S11 |
| 410 | monthly wedge及5–10bars贴趋势线的break风险 | S11–S12 |
| 411 | monthly spike/channel、lower-high MTR与AI翻转 | S09、S13 |
| 412 | sell climax、second signal、区间底部double/wedge及风险收益 | S06、S09–S11 |
| 413 | 整数磁体越过与回测、多周期相反趋势 | S08、S13、N03 |
| 414 | daily强涨处于monthly bear rally、parabolic climax与新闻无关 | S13–S14、N04 |
| 415 | 新闻型小公司巨幅跳跃、极小仓仍难弥补风险 | S15、N05 |

## 4. 回测验收

- Daily/weekly/monthly bars使用point-in-time复权与真实交易日历；公司行动不得制造假gap或假round-level突破。
- HTF与intraday策略分账户/风险/绩效报告，量化注意力成本可用冲突订单和漏失日内信号代理。
- Gap-pullback使用5分钟真实成交路径；无法short、停牌、gap-through-stop和options spread纳入执行模型。
- 按周期、趋势/大区间、aligned/conflicted、signal类型、流动性和jump-risk分层。
- Round-number `5%–10%` overshoot、5–10bar趋势线拥挤及10–20bar climax全部walk-forward验证。
- 比较一次/二次entry、初始部分仓、有限风险options及直接HTF stop entry，保持相同最坏风险。
- Figure 22.1–22.8只作规则案例，不作跨时代稳定性、概率或盈利证据。
