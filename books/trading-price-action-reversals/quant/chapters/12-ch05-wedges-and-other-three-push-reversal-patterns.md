# 第 5 章：Wedges and Other Three-Push Reversal Patterns

## 元数据

- 英文来源：`books/trading-price-action-reversals/en/chapters/12-ch05-wedges-and-other-three-push-reversal-patterns.md`
- PDF 页码：177–201
- 图表：Figure 5.1–5.12；正文与图注已完整说明规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Three-Push 统一表示

```text
push_i = 从confirmed pullback结束到新方向极值的位移
wedge_height = abs(pattern_extreme - pullback_after_push_1_extreme)
success_target_1 = pattern_start
success_target_2 = target_1 ± wedge_height
failure_target   = pattern_extreme ± wedge_height
```

- Wedge、parabolic wedge、shrinking stairs、triple top/bottom、H&S、final flag与失败double breakout均可映射为三次同向尝试。
- Lines可平行、收敛或发散；几何名称不决定交易，regime、momentum、signal与breakout结果才决定。
- Push与目标仅用当时confirmed pivots构建，禁止日终重数。

## 2. 规则卡

### REVERSALS-C05-S01：Online Three-Push Detector

- 类型：基础形态检测。
- 依据，PDF p.177–184：三个同向push后触发反向setup，趋势交易者第三次失败常让反转方获得控制。
- Pivot strength=`1–3bars`；相邻push之间至少有`1bar`反向/sideways pullback。
- 每个新extreme允许距离前一极值为正、近似相等或略回撤，容差`0.10–0.30ATR`。
- 保存push start/end、pullback、breakout extension与确认时间；第四推可能性由S08管理。

### REVERSALS-C05-S02：Wedge Reversal Entry and Targets

- 类型：countertrend主策略。
- 依据，PDF p.177–182：第三推后合格reversal signal触发，第一目标pattern start，第二目标按height measured move，通常预期two legs。
- 要求pattern在旧趋势末端，长度通常≥`20bars`或有major channel overshoot/climax背景。
- Entry在reversal signal触发；stop在third-push extreme外`1tick–0.15ATR`。
- Target1=第一推后pullback底/顶；Target2=再延伸`0.75–1.25 wedge_height`。

### REVERSALS-C05-S03：Second-Signal Countertrend Filter

- 类型：反转安全门控。
- 依据，PDF p.177–185、191–192：wedge reversal是逆势交易，除极强setup外应等待second entry、HL/LH或strong breakout pullback。
- Strong old trend或signal score不足时，首signal只shadow；等待`2–10bars`内第二attempt。
- Bull second signal可为HL/LL breakout pullback；bear镜像；需独立EV和结构stop。
- 首breakout连续强bars时可按新趋势直接入场，不强求pullback。

### REVERSALS-C05-S04：Wedge Pullback With-Trend Entry

- 类型：顺主趋势flag策略。
- 依据，PDF p.177–178、182–183：wedge pullback通常10–20bars、朝主趋势反向指向；因顺势可取first signal且不必完美。
- Higher-timeframe trend明确；pullback含3个小push、无强regime flip。
- 在方向signal/flag breakout入场；stop在wedge extreme外；目标旧极值及measured move。
- 与S02互斥：依据pattern方向相对主趋势而非形状判定。

### REVERSALS-C05-S05：Parabolic Wedge Score

- 类型：斜率加速反转组件。
- 依据，PDF p.178–179、192–196：后两push连线比前两push更陡代表parabolic urgency/climax，反转后常two legs/约10bars。
- `abs(slope_23/slope_12) >= 1.25–2.0`加分，且第三push path efficiency≥0.60。
- 需S02/S03 signal；斜率本身不逆势下单。
- 目标channel另一侧/5–20bars correction，参数连续敏感性测试。

### REVERSALS-C05-S06：Trend-Channel Overshoot / Near-Miss

- 类型：line背景组件。
- 依据，PDF p.181–182、191–194：多数三推在channel line附近反转；overshoot提高概率，但因逆方紧迫而略未触线仍可成立。
- Line在第三推前以push1/2或独立swings冻结；distance归一为ATR。
- Overshoot `0–0.30ATR`加分；near-miss≤`0.20ATR`不否决，但要求second signal/双向背景。
- Pattern明显而line需过度操纵时保留push特征，line score记missing。

### REVERSALS-C05-S07：Shrinking-Stairs Momentum Decay

- 类型：推进衰减特征。
- 依据，PDF p.183、188–189：连续breakout extension变小表示获利更早、逆方更积极，提高two-leg reversal概率。
- Extension=`extreme_i-extreme_{i-1}`；要求`ext_3/ext_2 < 0.5–0.9`，可扩展到4–5 steps。
- 与ATR缩减、bar count与overlap共同建模，防止tick rounding伪衰减。
- 合格reversal signal后入场；强第三extension改交S06 overshoot或S08 reset。

### REVERSALS-C05-S08：Momentum-Based Push-Count Reset

- 类型：计数状态修正。
- 依据，PDF p.182–183、188–189：第二push特别强时交易者会把它视为新第一push，第四push才是可交易第三推。
- 若push2位移≥push1的`1.5–2.5倍`、breakout≥`1ATR`且pullback浅，则原count衰减/重置。
- 同时维护`count_no_reset`与`count_reset`两个candidate，实时score选择而非事后唯一解释。
- 第三/第四推结果均报告，禁止只保留成功计数。

### REVERSALS-C05-S09：Wedge Failure Measured-Move Breakout

- 类型：形态失败顺原趋势策略。
- 依据，PDF p.182–186、189、197–201：反转entry触发后迅速越过wedge extreme即失败，常按wedge height measured move。
- Failure：反向MFE不足`0.5R`且`1–5bars`内strong close越pattern extreme。
- 在failure breakout/first pullback顺原趋势入场；stop在breakout structure另一侧。
- Target=`0.75–1.25 wedge_height`；weak breakout交S10二次反转而非追。

### REVERSALS-C05-S10：Failed Failure / Fourth-Push Reversal

- 类型：wedge第二次反转。
- 依据，PDF p.182–184、189：wedge先失败创新极值后立刻反转，可视第四push或higher-high/lower-low breakout pullback，通常走至少10bars/two legs。
- S09 breakout缺follow-through并在`1–5bars`强收回extreme，生成second-attempt signal。
- Entry顺原反转方向；stop在new extreme外；目标pattern start及two legs。
- 与S09共享episode且路径互斥，不能同时计盈。

### REVERSALS-C05-S11：Opening-Reversal Steep-Wedge Exception

- 类型：时段例外。
- 依据，PDF p.185、187–188：第一小时强三推可形成可靠opening reversal，即使channel很陡、pause很小；午后同形态通常不应fade。
- 仅session前`30–90min`、触previous-day range/major level、第三push有failed breakout/reversal signal。
- 初始半仓或等second signal；stop在opening extreme外。
- 分时段样本验证，开盘例外不得扩展到全天。

### REVERSALS-C05-S12：Micro-Wedge Scalp

- 类型：微型三推策略。
- 依据，PDF p.185、200–201：连续3bars或3/4–5bars形成micro wedge，通常只带来minor correction；强趋势中不是反转setup。
- Pattern span=`3–5bars`、三个tail/extreme pushes；只在range edge或trend pullback顺势开放。
- 目标`0.5–1R`/EMA/range midpoint；不保留major reversal runner。
- Strong countertrend environment由N02禁用。

### REVERSALS-C05-S13：Successive Tiny-Breakout Expansion

- 类型：micro三推失败突破策略。
- 依据，PDF p.185–186、200–201：range中连续1–2tick新极值并各自回撤，第三次再突破常产生显著breakout/measured move。
- 保存两次tiny breakout (`1–2ticks`或`0.02–0.08ATR`)及其`3–20bars`回撤。
- 第三次strong break顺方向入场；stop在micro range内/对侧，目标range height。
- Tick与spread归一化；同bar顺序不明采用保守路径。

### REVERSALS-C05-S14：Failed Double-Top/Bottom as Three Pushes

- 类型：range failed-breakout映射。
- 依据，PDF p.185–188：double的两个极值加第三次外侧失败break构成三推，通常至少scalp，可能穿range对侧并measured move。
- Third push越double extreme`0–0.30ATR`后`1–5bars`收回。
- 在failure bar触发反向entry；target midpoint/opposite edge，strong opposite breakout保留measured runner。
- Confirmed range可first signal；strong trend逆势需S03。

### REVERSALS-C05-S15：First-Hour / Trend-Resumption Three-Push Rally

- 类型：日内trend resumption。
- 依据，PDF p.183：首小时趋势后数小时range常有三推低动量反向leg，随后恢复早盘趋势至收盘。
- 先确认opening trend；中段correction≥`10bars`，3 pushes但momentum递减/overlap高。
- 在第三push后的方向signal顺opening trend入场；target旧极值/close runner。
- 若range strong breakout相反，则取消，不以“应该恢复”硬扛。

### REVERSALS-C05-S16：Acceptance-vs-Rejection Wedge Filter

- 类型：失败预警。
- 依据，PDF p.197–200：bottom setup后连续overlap/sideways表示接受低价而非拒绝，反转较差；强reversal spike表示拒绝。
- 第三push后`2–4bars` overlap ratio≥70%、净反向位移<`0.25ATR`则`acceptance=true`。
- Acceptance取消首反转entry并等待S03；向旧趋势break时转S09。
- Rejection需strong opposite body、close穿多bar或快速离开extreme。

### REVERSALS-C05-S17：Dynamic Premise / Smaller-Profit Exit

- 类型：反转交易管理。
- 依据，PDF p.195–197：预期two legs的setup若缺urgency、在EMA遇获利或higher low未形成，应降低目标并接受小利/亏损。
- 每bar重估follow-through、remaining structure space和regime；无第二腿证据时在1R/EMA/反向signal退出。
- 不因最初60%/two-leg叙述继续持有已转负EV仓位。
- 计划改变必须记录reason code，禁止事后美化目标。

### REVERSALS-C05-N01：Three Pushes Alone 不是反转理由

- 类型：`NEGATIVE`硬约束。
- 依据，PDF p.184–185、190–191：小三推在强tight trend中通常继续到第四/第五push；无先前countertrend strength时反转多失败。
- S02须有trend-line break、major channel overshoot、range edge或exceptional signal之一。
- 缺失时只运行S04/S09旧趋势方向。

### REVERSALS-C05-N02：Tight Channel 禁止首个 Wedge Fade

- 类型：`NEGATIVE`。
- 依据，PDF p.184–185、190–191、197–200：tight channel里的wedge与弱signal不是逆势setup，首breakout多数失败。
- Tightness：overlap低、pullbacks≤1–2bars/`0.25ATR`、方向bars≥70%；首countertrend交易数为零。
- 等strong break+HL/LH；失败signal可在其stop处顺势。

### REVERSALS-C05-N03：不要强迫线条或完美几何

- 类型：`NEGATIVE`模型约束。
- 依据，PDF p.178–182、186–192：wedge很少完美，可用bodies或略未触line；名称与精确形状不重要。
- 主检测以pivots/pushes为准，line只作辅助score。
- 禁止事后移动anchors使所有赢家成为wedge。

### REVERSALS-C05-N04：固定 60% / 10 Bars / Two Legs 不作事实

- 类型：`NEGATIVE`参数约束。
- 依据，PDF p.177、193–197：概率与时长是教学近似，现实有大量未达目标案例。
- 概率样本外校准；horizon测试`5–20bars`，legs标注`0–3+`。
- 所有未完成two-leg样本保留，不能按定义排除。

### REVERSALS-C05-N05：Support/Resistance Target 不能单独入场

- 类型：`NEGATIVE`。
- 依据，PDF p.194–196：所有reversal都在某个level，但多数measured targets不导致反转，未知level不能事后补理由。
- Level必须在signal前可见，且仍需price-action setup/EV gate。
- 超过明显target不自动产生逆势订单。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 177–182 | 三推统一行为、wedge reversal/pullback、parabolic、two-leg、second signal、目标 | S01–S06、N03–N04 |
| 182–186 | wedge失败/第四推、count reset、trend resumption、shrinking stairs、tiny breakouts | S07–S10、S13、S15 |
| 185–186 | opening exception、micro wedge、failed double breakout | S11–S14 |
| 186–194 | Figure 5.1–5.7：不完美wedge、首小时、stairs、LH、near-miss、parabolic | S02–S11、N01、N03 |
| 194–197 | Figure 5.8：bull/bear parabolic wedge、early/confirmed概率、动态premise | S03、S05、S10、S17、N04–N05 |
| 197–200 | Figure 5.9–5.11：acceptance、failed wedge measured move、tight-channel否决 | S09、S16、N01–N02 |
| 200–201 | Figure 5.12：successive one-tick breakouts与micro wedge continuation | S12–S13 |

## 4. 回测验收

- 每个push/pullback/pattern保存pivot确认时间；同时保留reset与no-reset计数，未来重画次数为零。
- S02–S17共享wedge episode ID；首signal、second entry、failure与failed failure路径互斥计盈。
- 分开报告reversal、minor correction、sideways acceptance、old-trend continuation与measured failure。
- Tight-channel、three-push-alone、support-only和未来线条操纵设自动硬测试。
- Early、second-entry与confirmed-breakout版本比较净EV、MAE/MFE、stop-out及剩余reward。
- Measured targets按`0.75–1.25 height`敏感性测试；固定tick按ATR/spread归一化。
- Bull/bear、reversal/pullback和opening/non-opening做镜像与分层验证。
- Figure 5.1–5.12仅作章节例证，不作参数拟合或绩效证据。
