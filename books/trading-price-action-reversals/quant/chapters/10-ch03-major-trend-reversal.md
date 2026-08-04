# 第 3 章：Major Trend Reversal

## 元数据

- 英文来源：`books/trading-price-action-reversals/en/chapters/10-ch03-major-trend-reversal.md`
- PDF 页码：112–138
- 图表：Figure 3.1–3.8；正文与图注已完整说明规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Major Trend Reversal 四阶段状态机

```text
TREND
 -> COUNTERTREND_BREAK
 -> OLD_EXTREME_TEST
 -> SECOND_REVERSAL
 -> CONSENSUS_FLIP | TRADING_RANGE | OLD_TREND_RESUMPTION
```

- 四个必要条件：屏幕上存在趋势；逆向move显著突破trend line且通常越EMA；旧极值被测试并二次反转；二次反转足够远以形成共识。
- Top测试可为higher high、double top或lower high；bottom镜像为lower low、double bottom或higher low，统一视为同一连续结构。
- “Major”相对于交易图周期定义；不能把1分钟结构直接当5分钟MTR。

## 2. 规则卡

### REVERSALS-C03-S01：Visible Old-Trend Gate

- 类型：MTR前置状态。
- 依据，PDF p.112–114：必须先有图上可见的主趋势，而不是任意上下swing。
- Trend候选：≥`20–60bars`方向结构、至少2个HH/HL或LL/LH，EMA斜率与净位移同向。
- 保存old trend start、extreme、major trend-line anchors与last structural pullback。
- 无可识别趋势时转range reversal模型，不产生MTR标签。

### REVERSALS-C03-S02：Significant Countertrend Break

- 类型：第一阶段门控。
- 依据，PDF p.113–118、123–127：逆向move须显著穿trend line，最好穿EMA、旧swing与多个bars；弱break不等于反转。
- Break至少满足2项：持续≥2–3bars、位移≥`1–2ATR`、穿EMA≥`0.20ATR`、破last swing、close跨越≥5个旧bars。
- 强break预期pullback后至少第二腿；弱到未达EMA则继续只做旧趋势方向。
- Trend line只用当时confirmed anchors，禁止事后选择最合适线。

### REVERSALS-C03-S03：Old-Extreme Test Normalization

- 类型：第二阶段结构识别。
- 依据，PDF p.113–118、124–125：break后旧趋势恢复并测试extreme；overshoot、exact test、undershoot经济含义相同。
- Test区域=`old_extreme ± 0–0.50ATR`；分类`overshoot/exact/undershoot`只作特征，不设模式优先级。
- Test通常可有2 legs；保存test momentum、overlap、push count与相对break-leg斜率。
- 只有测试中产生合格second reversal才进入S04。

### REVERSALS-C03-S04：Second-Reversal MTR Entry

- 类型：核心反转策略。
- 依据，PDF p.113–118、122–128：旧极值测试后从LH/DT/HH short，或HL/DB/LL long；早入低概率高reward。
- Entry在合格reversal/second-entry signal触发；stop在test extreme外`1tick–0.15ATR`。
- Target1=countertrend-break extreme；Target2=pattern/range measured move；要求成本后EV>0。
- Early版本允许校准概率`0.40–0.50`、目标≥`2R`；不能把作者比例直接当先验事实。

### REVERSALS-C03-S05：Consensus Always-In Confirmation

- 类型：较晚高概率入场。
- 依据，PDF p.113–114、128–130：二次反转形成多根强trend bars或一系列新方向swings后，市场形成Always-In共识；概率更高但剩余reward较少、stop较宽。
- 确认：`3–5bars`强spike或连续LH/LL（bull镜像），累计≥`1.5–2ATR`且EMA保持新方向。
- 在强close或首次浅pullback入场；qty按结构stop缩小。
- 与S04用同一母事件比较概率、R倍数、净EV和漏失move。

### REVERSALS-C03-S06：Weak-Test Momentum Filter

- 类型：极值测试质量门控。
- 依据，PDF p.118–125、132–133：低斜率、多overlap、反向bars、2–3 pullbacks/wedge的test更可能失败并反转。
- Test overlap≥`0.50–0.70`，净位移/总路径≤`0.40–0.65`，至少2 pushes或旧趋势反向bars≥30%。
- Test斜率小于old trend与break leg的`0.5–0.8倍`加分。
- 弱test允许S04；强test交S07重置。

### REVERSALS-C03-S07：Strong-Test Process Reset

- 类型：旧趋势恢复判别。
- 依据，PDF p.124、130–133：test若以steep tight channel远越旧极值、5bars以上无pause，通常是成功breakout/旧趋势恢复，必须重启流程。
- Strong test：≥5bars、overlap低、方向body占比≥65%、overshoot≥`0.5–1.0ATR`。
- 取消当前MTR候选；等待该新channel被显著突破，再等待新的extreme test。
- 禁止在steep channel第一次breakout时逆势入场。

### REVERSALS-C03-S08：Higher-High then Lower-High Second Chance

- 类型：二次入场方案。
- 依据，PDF p.125–127：higher-high reversal down后通常还有lower-high MTR第二次short机会；lower-low后higher-low long镜像。
- 首次overshoot反转完成至少一腿后，等待weak retracement至`0.40–0.80`首腿或结构resistance。
- Lower-high/higher-low signal重新通过EV，stop在该swing外；目标首腿extreme/新measured move。
- 与首个S04分别计trade，但共享MTR episode防止选择性重复报告。

### REVERSALS-C03-S09：Leg-Count by Test Type

- 类型：目标与持仓期限组件。
- 依据，PDF p.124–129：undershoot LH/HL通常启动countertrend第二腿；overshoot HH/LL通常启动第一腿，之后仍预期pullback+第二腿。
- Overshoot entry：默认保留runner通过first pullback至second leg；undershoot entry：第二腿结构目标处提高退出比例。
- Leg使用在线pivot `1–3bars`确认；不能以最终波形回填。
- 无第二腿视为失败/截断样本，完整纳入统计。

### REVERSALS-C03-S10：Breakout Reaction Three-Way Classifier

- 类型：新极值订单反应分类。
- 依据，PDF p.118–123：旧趋势新极值后可能继续强breakout、sideways获利、或强反转；三者分别代表press、profit taking与反向控制。
- `continuation`：突破后MFE≥scalp target且follow-through强；`sideways`：`3–10bars`低净位移；`reversal`：`1–3bars`强收回breakout。
- 分类只在对应路径出现后生效；用于随后策略切换，不回填breakout时决策。
- Strong reversal进入S04/S05；sideways按range；continuation取消MTR。

### REVERSALS-C03-S11：Mature-Trend Trading-Range Transition

- 类型：趋势衰减状态。
- 依据，PDF p.118–123：pullbacks变大、双向bars增加后，旧flag更像range；首批range通常仍可能trend continuation，但新极值失败率上升。
- 指标：pullback depth/length增加、overlap≥60%、双向swing与EMA crossings≥2。
- 状态从strong trend转`developing_range`后，旧极值不再追breakout，改为range-edge目标和较小runner。
- Strong range breakout再切新trend，不能预判方向。

### REVERSALS-C03-S12：Exhaustive Climax Reversal

- 类型：末端真空climax方案。
- 依据，PDF p.121–122：长期趋势在measured target/channel line及第二或第三climax出现巨大方向bars，可能是强手暂时退出造成的vacuum，随后双方逆向交易。
- Context：protracted trend+major target/line+climax count≥2；末spike range≥`1.5–2.5 median`。
- 在close/极值附近只建立分档小仓或等反向confirmation；目标至少`10bars/two legs` correction。
- 若出现持续强follow-through则止损并转continuation，不把所有大bar当exhaustion。

### REVERSALS-C03-S13：Head-and-Shoulders as MTR Variant

- 类型：形态映射组件。
- 依据，PDF p.114–116：head selloff通常break trend line，right shoulder是LH breakout-pullback；neckline break强则swing，弱则range/triple bottom。
- 不单凭外观入场；必须依次满足S01–S04。
- Neckline在right shoulder前由已完成lows/highs确定；strong close-through允许add-on/measured target。
- Weak neckline test按range处理；突破right shoulder使bear setup失效并可能测量上行。

### REVERSALS-C03-S14：Micro Double Top/Bottom Final-Flag Entry

- 类型：微型反转执行。
- 依据，PDF p.116–117、136–138：多数可交易反转以micro DT/DB或final flag开始；可在预期失败H/L1–2/triangle signal extreme处limit。
- 两极值间隔`1–3bars`，差距≤`0.10–0.30ATR`；必须通过higher-timeframe context gate。
- Bull final flag：在weak L1/L2 signal low及下买；bear镜像；stop在micro structure外。
- 目标scalp、range midpoint或接入S04 swing；形态本身不保证反转。

### REVERSALS-C03-S15：Small-Timeframe With-Trend Execution

- 类型：多周期执行方案。
- 依据，PDF p.125、133–137：大周期强趋势未明确反转前，小周期reversal多失败；小周期仅用于寻找大周期顺势entry或被困逆势者stop位置。
- Higher timeframe regime在低周期signal前冻结；若为strong bear，只允许低周期short，bull镜像。
- 可在首反转signal失败处stop入场，或prior-bar extreme limit顺大趋势。
- 低周期countertrend shadow样本单独保存，不与MTR合并。

### REVERSALS-C03-S16：Context-Dependent Range Outcome Management

- 类型：MTR结果管理。
- 依据，PDF p.113–125、128–130：多数MTR先形成trading range而非相反趋势，但仍可产生可交易countertrend swing。
- 到break extreme/旧range对侧先平`50–100%`；只有S05确认才保留相反trend runner。
- Early setup若失去momentum并进入overlap，切range stop/target，不继续假设大反转。
- 分别报告small profit、swing profit、small loss、range与opposite trend标签。

### REVERSALS-C03-N01：Trend-Line Break Alone 不是反转

- 类型：`NEGATIVE`硬约束。
- 依据，PDF p.117–118、124、130–132：break只是countertrend strength首个迹象，仍应等待旧极值测试和second reversal。
- S02成立但S03/S04未成立时，MTR交易数必须为零；旧趋势setup仍可交易。
- 仅climactic channel overshoot reversal可走S12独立路径。

### REVERSALS-C03-N02：禁止无 Overshoot 的 V Top/Bottom 假设

- 类型：`NEGATIVE`。
- 依据，PDF p.117：没有trend-channel overshoot的真实V reversal极罕见，不值得作为常规策略。
- 无S02且无S12背景时，single-bar V signal只记录不交易。
- 错过罕见V后等待新趋势pullback，不追价。

### REVERSALS-C03-N03：小周期小 Stop 不等于好交易

- 类型：`NEGATIVE`多周期约束。
- 依据，PDF p.133–137：1分钟countertrend stop较小，但成功率下降更多，交易者方程反而为负。
- Higher timeframe强趋势中低周期逆势实际交易数为零，直到higher timeframe完成反转确认。
- 不以降低risk距离替代概率与成本后EV分析。

### REVERSALS-C03-N04：Double Top/Bottom 不可脱离 Context

- 类型：`NEGATIVE`形态约束。
- 依据，PDF p.136–138：多数反转有micro DT/DB，但形成DT/DB本身不意味着应该交易。
- S14必须同时满足regime、location与EV gate；range中部或强trend continuation环境禁用。
- 禁止仅以几何相似度产生高置信度标签。

### REVERSALS-C03-N05：固定概率与 Fibonacci 不作常数

- 类型：`NEGATIVE`参数约束。
- 依据，PDF p.125–130：40/30/30、60%和61.8%为教学近似；60、63、67% retracement可能无本质差别。
- 概率在样本外校准；retracement使用连续变量及`0.40–0.80`敏感性区间。
- Figure 3.1–3.8精确路径不得作为拟合标签。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 112–114 | MTR定义、四条件、early/confirmed方程、range与opposite trend结果 | S01–S05、S16 |
| 114–118 | trend-line break、H&S、极值测试等价、micro DT/DB/final flag、break非反转 | S02–S04、S13–S14、N01–N02 |
| 118–123 | 新极值三种反应、成熟趋势双向化、climax vacuum、breakout强弱判别 | S10–S12 |
| 123–125 | swing-low breakout反应、channel overshoot、第二腿、test动量与周期相对性 | S06–S09、S15 |
| 125–130 | Figure 3.1–3.2：HH→LH、LL→HL、early/confirmed入场、range结果与概率 | S04–S09、S16、N05 |
| 130–132 | Figure 3.3：break alone不足、steep HH恢复旧趋势、过程重置 | S07、N01 |
| 132–133 | Figure 3.4：过强test等待channel break和breakout pullback | S06–S07 |
| 133–137 | Figure 3.5–3.7：小周期只作大周期顺势执行、逆势小stop负EV | S15、N03 |
| 136–138 | Figure 3.8：micro DT/DB、final flag、higher-timeframe context | S14、N04 |

## 4. 回测验收

- 四阶段状态均保存触发bar与`valid_from`；趋势线、极值、test和leg不得未来重画。
- Top/bottom镜像测试，HH/DT/LH与LL/DB/HL均用连续距离特征而非离散偏好。
- S04、S05、S08及S14共享MTR episode ID，防止同一反转重复计盈。
- 分开报告old-trend resumption、trading range、small countertrend swing和opposite trend结果。
- Early与confirmed方案比较成本后概率、reward/risk、净EV、MAE/MFE和剩余move。
- Strong-test reset、break-alone禁令、小周期逆势禁令及context-free double禁令设自动测试。
- OHLC同bar顺序不明使用不利路径；limit/stop执行计slippage、gap与佣金。
- 所有bar/tick/retracement阈值做walk-forward、跨品种、周期与volatility sensitivity。
- Figure 3.1–3.8仅作章节例证，不作参数或绩效证据。
