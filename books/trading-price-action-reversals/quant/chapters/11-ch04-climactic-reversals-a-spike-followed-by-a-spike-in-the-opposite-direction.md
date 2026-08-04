# 第 4 章：Climactic Reversals

## 元数据

- 英文来源：`books/trading-price-action-reversals/en/chapters/11-ch04-climactic-reversals-a-spike-followed-by-a-spike-in-the-opposite-direction.md`
- PDF 页码：139–176
- 图表：Figure 4.1–4.17；正文与图注已完整说明规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Climax 与 Climactic Reversal

```text
climax = 相对近期不可持续的方向位移，结束于pause/reversal
climactic_reversal = trend_spike -> opposite_spike -> pause/range/channel
```

- 每根trend bar都可视为微型breakout/climax，但只有相对range、body、持续、位置与背景异常时才产生交易候选。
- Climax不保证反转；常见结果是1bar以上range后旧趋势恢复。反向spike也必须获得follow-through。
- Bull/bear镜像实现；固定“10 bars/two legs”解释为比普通pullback更长、更复杂的研究区间，而非确定预测。

## 2. 规则卡

### REVERSALS-C04-S01：Relative Climax Detector

- 类型：不可持续行为检测。
- 依据，PDF p.139–146：单根或连续大trend bars、低overlap、末端加速均是climax；pause/reversal bar标志其结束。
- 单bar候选：range/body≥近`20–50bars`中位数的`1.5–2.5倍`，body/range≥65%。
- Multi-bar候选：`2–5bars`累计≥`2–4ATR`、方向bars≥75%、path efficiency≥0.70。
- 保存trend age、location、target/line、climax count和随后的pause，不能用最终反转筛选climax。

### REVERSALS-C04-S02：Breakout-vs-Exhaustion Classifier

- 类型：大trend bar三态判别。
- 依据，PDF p.140、151–154、172–173：早期support/resistance breakout可成measuring gap；长期趋势末端最大bar更可能exhaustion gap。
- Continuation加分：breakout前base/range、trend age短、follow-through close、前方空间大。
- Exhaustion加分：trend age≥`20–40bars`、第二/第三climax、major target/channel overshoot、late acceleration、下一bar弱化/反向。
- 输出`continuation/exhaustion/uncertain`概率；uncertain先按range管理，不提前假设反转。

### REVERSALS-C04-S03：Opposite-Spike Confirmation

- 类型：climactic reversal确认。
- 依据，PDF p.139–147、158–160：climax很快被相反大bar/多bar spike反转，构成跨周期two-bar reversal；反向spike越大，反转概率越高。
- Opposite spike在climax后`0–5bars`开始，累计≥`1–2ATR`或原spike的`0.5–1.25倍`。
- 至少一根strong opposite close并收回climax midpoint；完全收回/穿越起点进一步加分。
- Entry在strong close/突破反转bar；stop在climax extreme外，qty按宽stop缩小。

### REVERSALS-C04-S04：Consecutive Climax Count

- 类型：连续climax反转方案。
- 依据，PDF p.144–146、152–153、157–164：短修正间隔的第二climax提高correction概率，第三climax通常触发至少two-leg/longer correction。
- 独立climax之间pause/pullback `<10bars`且未穿对侧channel/未充分回撤，计为consecutive。
- 2次视作宽义double top/bottom，3次视作wedge；第三次只在S03或second signal后入场。
- Target=`5–20bars`、至少2 legs、EMA/old range；全区间做敏感性测试。

### REVERSALS-C04-S05：Correction Reset of Climax Count

- 类型：过热重置规则。
- 依据，PDF p.146、157、174：若每次climax后已有约10bars修正、突破channel底/顶或形成range，excess已释放，后续climax不应机械累计。
- Reset条件：correction≥`8–15bars`，或depth≥`0.5–1.0ATR`并破短channel，或confirmed range≥10bars。
- Reset后count归零/衰减，不沿整日无限累积。
- 与指数衰减版本比较，避免固定10bar过拟合。

### REVERSALS-C04-S06：Trend-Channel Overshoot Reversal

- 类型：parabolic/channel末端策略。
- 依据，PDF p.140–150、157–158、169–172：加速越channel line后强回归通常测试channel另一侧，且常形成10bar/two-leg correction。
- Channel line在overshoot前用至少2个confirmed swings冻结；overshoot≥`0.10–0.30ATR`。
- 需S03、合格reversal bar或second entry；目标trend line/对侧channel line。
- 第二次overshoot失败可提高分数；无反转momentum则交S14失败策略。

### REVERSALS-C04-S07：Big-Up Big-Down Range State

- 类型：双spike后的regime管理。
- 依据，PDF p.142、146–159、172：big up + big down代表双方强、方向暂不明确，通常先形成trading range，再决定channel方向。
- 两spike各≥`1ATR`且相反，随后进入`BIDIRECTIONAL_RANGE`，默认等待breakout+follow-through。
- Range内边缘fade、中央不交易；bull/bear channel只在强break后确认。
- 不以较大spike自动指定赢家；Figure 4.5显示较大bull bar仍可被bears击败。

### REVERSALS-C04-S08：Climax Range Breakout Channel Follow

- 类型：range后顺势策略。
- 依据，PDF p.142、146–160：反转spike后的range中双方建仓；一侧突破后另一侧cover，形成spike-and-channel。
- Range边界在break前固定；要求directional close+`1–2bars` follow-through或breakout pullback。
- Entry顺break方向，stop在range/新swing另一侧；目标range measured move或channel swing。
- Break失败则退出并允许独立反向candidate，不在range内预测channel方向。

### REVERSALS-C04-S09：Vacuum-to-Magnet Climax

- 类型：目标位衰竭方案。
- 依据，PDF p.140–145、151–153、162–164、172：强手暂缓逆向交易造成vacuum加速至support/resistance，随后双方在短暂价值区反向成交。
- Magnet必须在spike前可见：measured move、prior extreme/range、EMA或trend-channel line。
- Climax在magnet±`0.10–0.30ATR`结束且S03成立才交易；未见反转price action不只凭level接刀。
- 目标旧range/EMA/至少1R；记录overshoot与slippage尾部。

### REVERSALS-C04-S10：Rare V-Reversal Tiered Entry

- 类型：无显著测试的V top/bottom。
- 依据，PDF p.148–149、160–164：真正无测试V反转每月仅少数，常隐含final flag、micro DT/DB或three-push；可按激进/确认分层。
- Aggressive：末端≥2 climaxes+final flag/micro pattern，在climax close/next pause以≤半仓入场。
- Confirmed：strong opposite close、micro double、second signal或Always-In flip后补足。
- 初始stop约climax bar高度/结构外；无相反momentum立即退出，不能把所有尖底顶当V。

### REVERSALS-C04-S11：Spike Test Expectation by Context

- 类型：spike测试分类。
- 依据，PDF p.142–143、148、164–168：顺主趋势的新极值spike和countertrend reversal spike通常会被测试；主趋势内的countertrend spike pullback本身是测试，可能不回测。
- 分类：`with_trend_extreme_spike -> test likely`；`reversal_attempt_spike -> test likely`；`countertrend_pullback_spike -> test optional`。
- Test窗口按周期研究`5–30bars`，容差`0.10–0.30ATR`。
- 该规则只管理target/reentry，不保证测试必达；强新趋势确认会终止旧test expectation。

### REVERSALS-C04-S12：Spike-Pullback Trend Resumption

- 类型：失败逆势spike顺趋势策略。
- 依据，PDF p.142–144、165–168：强趋势中的countertrend spike若缺follow-through，常迅速成为flag；旧趋势交易者在折价/溢价处积极重入。
- Higher-timeframe trend强；countertrend spike后`1–3bars`无法延续并形成原趋势strong signal。
- Entry在failed reversal stop/strong close，stop在pullback extreme外；目标旧极值/measured move。
- 若countertrend获得连续follow-through并破结构，则取消，转S07或MTR。

### REVERSALS-C04-S13：Late-Slope Acceleration Score

- 类型：parabolic情绪代理。
- 依据，PDF p.148–150、157–158、161–164、171–173：连续更陡channel lines/末段近垂直推进表示情绪与潜在exhaustion。
- 用rolling regression slope或swing slope比较连续3段；`abs(slope_i/slope_{i-1}) >= 1.25–2.0`加分。
- 同时要求trend age、低overlap和climax bar，单独斜率不产生逆势交易。
- S03后入场；无momentum按S14旧趋势继续。

### REVERSALS-C04-S14：Failed Climax-Reversal With-Trend Entry

- 类型：失败反转顺势策略。
- 依据，PDF p.149–150、159、170–175：逆势signal小、follow-through弱或wedge横盘不涨时，说明excess判断错误；其失败常困住早入者并产生强顺势breakout。
- Reversal触发后`1–3bars`无推进、entry bar小/doji，或signal收盘前转成旧趋势bar。
- 在signal extreme/早入者stop处顺旧趋势入场；stop在failed setup另一端。
- 强trend中优先此策略；尤其不front-run未收盘bar。

### REVERSALS-C04-S15：Second-Entry / Higher-Low Safety Filter

- 类型：steep channel反转确认。
- 依据，PDF p.148–150、160–161、170–174：逆强trend首反转多失败；多数交易者应等待strong trend-line break后HL/LH或second signal。
- Strong/steep old trend要求S03后再有`second attempt`，或先break channel再breakout pullback。
- Signal需方向body≥50–60%，doji/overlap环境提高门槛。
- Second entry失败预期旧趋势至少两腿，允许转S14。

### REVERSALS-C04-S16：Climax Scale-Out and Reentry Window

- 类型：旧趋势仓位管理。
- 依据，PDF p.140–145、151–153、172–173：强趋势持仓者在末端climax获利，预期较深修正；约two-leg/longer correction后若弱可恢复旧趋势仓。
- Context+S01 exhaustion高分时平`50–100%`旧趋势仓；反向交易另过EV gate。
- 最早重入窗口`8–20bars`且完成2 legs；若新趋势S08已确认则不重入旧方向。
- 比较持有、减半、全平/再入的净EV和成本。

### REVERSALS-C04-S17：Price-Action-First Volume Overlay

- 类型：可选研究特征。
- 依据，PDF p.150–151、163–164、175–176：巨大volume有时增强底部follow-through，但多数大市场反转无可靠volume模式，1分钟divergence无额外必要性。
- 主模型完全由price action触发；volume仅作预注册overlay。
- Extreme volume=`10–20x rolling median`且range≥`5x median`可加分，但低volume不得否决合格反转。
- 比较with/without volume的样本外增量Brier、EV和漏单；无稳定提升则删除。

### REVERSALS-C04-S18：Confluence-Enhanced Climactic Reversal

- 类型：背景加分组件。
- 依据，PDF p.158、169–173：opening reversal、prior day extreme、measured move、多个channel overshoot、final flag、micro double和MTR共振提高可靠性。
- 至少2类独立结构位于`0.10–0.30ATR`窗口；level均需事前冻结。
- Confluence只调score/swing fraction，不扩大账户最大risk。
- 两腿预期时至少保留`25–50%` runner；无follow-through仍按S14退出。

### REVERSALS-C04-N01：Climax 不等于自动反转

- 类型：`NEGATIVE`硬约束。
- 依据，PDF p.139–150：多数climax后是range且旧趋势常恢复；不可持续状态可持续得比账户更久。
- 无S03/S15时不得仅凭large bar、第三推或channel line逆势。
- Climax detector必须报告全部continuation样本，禁止只选择反转案例。

### REVERSALS-C04-N02：Steep Channel 禁止逐 Line 接刀

- 类型：`NEGATIVE`。
- 依据，PDF p.149–150、170–175：steep channel中买每次bear channel-line test/卖bull镜像是亏损策略；反复画线反映偏见。
- Strong channel未出现break+HL/LH前，countertrend实际交易数为零。
- 每个episode允许的channel line候选预先限制，禁止随价格不断重画以合理化入场。

### REVERSALS-C04-N03：禁止 Front-Run 未收盘 Reversal Bar

- 类型：`NEGATIVE`无未来/执行约束。
- 依据，PDF p.173–174：盘中bull reversal bar可在最后数秒塌成bear breakout，早入者被困。
- Signal bar必须close后才确认；intrabar策略须使用真实tick数据并单独验证。
- OHLC回测不得假设以最终形态形成前的有利价格成交。

### REVERSALS-C04-N04：Measured Move/Volume/Divergence 不能单独反转

- 类型：`NEGATIVE`特征约束。
- 依据，PDF p.150–151、168–170、175–176：目标位本身不够；volume/divergence在大市场通常无可靠增益且会使交易者错过price-action setup。
- S09/S17/S18均须有price-action confirmation；单一indicator candidate只shadow。
- 不读取1分钟volume divergence来批准5分钟逆势交易。

### REVERSALS-C04-N05：10 Bars / Two Legs 不是硬保证

- 类型：`NEGATIVE`参数约束。
- 依据，PDF p.152：该短语表示修正比小pullback更长更复杂。
- Horizon、leg count与target作为连续结果报告，测试`5–20bars`及`1–3legs`。
- 未达10bars不能事后删除失败交易，超过20bars也不自动认定新趋势。

### REVERSALS-C04-N06：小周期形态不能覆盖交易周期 Context

- 类型：`NEGATIVE`多周期约束。
- 依据，PDF p.148–151、160–164：higher/lower timeframe可显示two-bar reversal或micro pattern，但当前图已足以交易；强大周期趋势优先。
- 小周期仅作执行/解释，不得用其逆转大周期regime。
- 多周期level必须在当前signal前可见，禁止事后寻找完美形态。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 139–147 | climax定义、vacuum、opposite spike、连续climax、range与channel争夺 | S01–S09、S16、N01 |
| 148–151 | V形稀有、parabolic/channel overshoot、失败反转、volume局限、failed breakout本质 | S02、S06、S10、S13–S17、N01–N04 |
| 152–154 | Figure 4.1：measuring与exhaustion、连续sell climax、10bar/two-leg修正 | S02、S04、S09、S16、N05 |
| 154–158 | Figure 4.2–4.4：双spike后range、channel方向不明、第三climax与多magnet | S04–S09、S13 |
| 158–160 | Figure 4.5：opposite bars、range后赢家、弱首反转与MTR | S03、S07–S08、S14–S15 |
| 160–164 | Figure 4.6–4.7：V反转稀有、测试、final flag/micro double、极端volume | S04、S10、S17、N04 |
| 164–168 | Figure 4.8–4.10：spike reversal与spike pullback的不同测试概率 | S11–S12 |
| 168–171 | Figure 4.11–4.13：inverted V、多重理由、steep channel等待second entry | S06、S10、S15、S18、N02 |
| 171–175 | Figure 4.14–4.16：斜率加速、真空测试、反转需momentum、失败wedge与画线偏见 | S09、S13–S15、N02–N03 |
| 175–176 | Figure 4.17：volume divergence无稳定必要性 | S17、N04 |

## 4. 回测验收

- Climax candidate全集在发生时保存，continuation/range/reversal三类结果全部报告。
- Spike、pause、climax count、channel anchors、magnet和confluence均带`valid_from`，未来重画次数为零。
- S02–S18共享climax episode ID；opposite-spike、second-entry、range breakout不得重复计算同一move。
- 报告breakout/exhaustion分类校准、净EV、MAE/MFE、测试概率、range持续和最终channel方向。
- Aggressive V、confirmed V、failed-reversal与旧趋势continuation版本在同一母样本比较。
- Strong-channel接刀、未收盘front-run、indicator-only反转和climax-alone反转设零交易硬测试。
- Wide stop按固定账户risk缩仓；所有limit/stop计gap、slippage、partial fill和佣金。
- Bar数、腿数、ATR倍数、斜率与volume阈值做walk-forward、跨品种/周期/volatility sensitivity。
- Figure 4.1–4.17仅作章节例证，不作参数或绩效证据。
