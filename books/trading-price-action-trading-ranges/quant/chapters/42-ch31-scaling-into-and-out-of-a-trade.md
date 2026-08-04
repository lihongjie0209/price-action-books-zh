# 第 31 章：Scaling Into and Out of a Trade

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/42-ch31-scaling-into-and-out-of-a-trade.md`
- PDF 页码：596–617
- 图表：Figure 31.1–31.8；正文与图注已完整说明规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 组合级 Scale 状态

```text
avg_entry = sum(fill_price_i * qty_i) / sum(qty_i)
portfolio_risk = sum(qty_i) * abs(avg_entry - final_stop) * point_value + costs
remaining_risk = sum(qty_i * abs(fill_price_i - active_stop_i)) * point_value + costs
scale_state = INITIAL | SCALE_2 | SCALE_3 | FULL | PARTIAL_EXIT | RUNNER | FLAT
```

- 首笔下单前冻结最大加仓次数、每档价格/触发器、每档qty、最终stop、最大组合风险和退出方案。
- 加仓可作为一个组合管理，也可把后续独立信号当独立交易；两种会计方式必须预先选择，禁止按结果切换。
- 所有固定点数/美分示例换算为tick、ATR/ADR、prior-pullback size与账户风险。

## 2. 规则卡

### RANGES-C31-S01：Preplanned Scale-In Risk Budget

- 类型：组合风险治理。
- 依据，PDF p.596–603：允许加仓时首仓必须更小，且最终仓位到最终stop的总风险不超过平常容忍度。
- 基准为2–3档等qty，每档`33–50%`常规仓；也可变qty，但所有档位在entry前冻结。
- `worst_case_portfolio_risk <= account_risk_budget`，包含全部成交、gap/slippage和佣金。
- 任一档成交后重算均价与风险；超预算则取消未成交档，不得移动stop扩大容量。

### RANGES-C31-S02：Strong-Trend Pullback Scale-In

- 类型：顺趋势逆行加仓。
- 依据，PDF p.597–601、605–611：最佳场景是明确Always-In趋势中的增长回调，可在EMA、结构支撑或固定间隔分批建立小仓。
- Trend强且高周期同向；pullback为低动量channel，无强反向breakout。
- Entry1在首个合格signal/EMA test；Entry2–3在更优结构或每`0.5–1.0 prior_pullback / 0.25–0.75ATR`。
- Final stop在使trend premise失效的swing外；目标旧极值、1R/2R或组合首档breakeven以上。

### RANGES-C31-S03：Trading-Range Edge Scale-In

- 类型：区间边缘fade。
- 依据，PDF p.596、599–601、607–608、614–617：机构在range底部逐步买、顶部逐步卖，预期短腿失败并回到range内。
- Confirmed range；仅在外侧20–30%，禁止中部加仓。
- Entry档位可用旧swing、range edge及外扩`0.10–0.30ATR`；最多3档。
- Stop在range明确失效处；目标首档entry、midpoint及对侧分批退出。
- Strong breakout+follow-through立即取消余单并按S09退出。

### RANGES-C31-S04：Strong Spike Pressing

- 类型：顺盈利方向加仓。
- 依据，PDF p.596–597、603–604、608–609、611–614：强spike中可在强close或微pullback持续press，直到pause、明显tail或反向body出现。
- Spike要求连续≥2bars、方向body≥65%、overlap低且无临近major target的climax否决。
- 在close/next-bar breakout加仓；每次仅当旧仓stop已收紧使`remaining_risk`仍≤预算。
- 首个large tail、opposite body或pause bar停止新加仓；已有仓按swing/scale-out管理。

### RANGES-C31-S05：Strong Channel With-Trend Adds

- 类型：channel顺势加仓。
- 依据，PDF p.596–597、608–610：强bull channel可在每次pullback继续买，bear镜像；首回调通常被买并测试新极值。
- Channel方向一致、pullbacks浅、EMA斜率强；在micro pullback、first EMA gap或合格signal加仓。
- 每次加仓须有到旧极值至少1R空间或提升组合EV。
- 第三推/climax后停止press，交S11减仓，不继续追成熟channel。

### RANGES-C31-S06：Second-Signal Separate-Trade Scaling

- 类型：低风险后续入场。
- 依据，PDF p.602–604：最稳妥的scale方式是原前提仍有效且出现第二/第三个独立好signal，每笔各自有良好交易者方程。
- 后续signal必须完成自身entry、stop、target与成本后EV gate；不能只因首仓亏损而触发。
- 子交易可有不同stop/target，但总账户风险仍受S01约束。
- 默认最多3个并行子交易；复杂度超过上限则拒绝新增。

### RANGES-C31-S07：Half-Size at Original Stop Level

- 类型：两档结构加仓方案。
- 依据，PDF p.602、605–606：可先以半仓入场，把原本单笔stop位置作为第二档entry，再在同等距离外设置组合stop。
- Entry1=`signal trigger`，Entry2=`conventional_stop_level`，各50%；final stop再外扩原风险`0.75–1.25倍`。
- 必须确认Entry2处trend/range premise仍有效；强breakout穿越则不成交或立即退出。
- 目标先在Entry1附近退出部分，使首档breakeven、第二档盈利；余仓到结构目标。

### RANGES-C31-S08：Average-Entry Breakeven Scale-Out

- 类型：逆行加仓后的组合退出。
- 依据，PDF p.597–598、605–611、614–617：两档成交后反弹到首档可使首档breakeven、后档获利；可在那里全平或保留runner。
- Conservative target=`entry_1 ± costs`；到达时平50–100%。
- 若regime/target已弱化，全部退出；若趋势恢复且旧极值空间充足，余`25–50%`跟踪。
- 不把组合均价回归误称每个子交易均盈利，逐fill报告P&L。

### RANGES-C31-S09：Premise-Invalidation Forced Exit

- 类型：组合止损/状态切换。
- 依据，PDF p.597–599、601、617：big picture改变、原目标不现实或Always-In翻转时必须退出；逆趋势第二次推进应退出并可独立反手。
- 触发：strong breakout through final level、Always-In flip、合格H/L2顺原趋势或剩余EV<0。
- 立即撤销未成交scale orders并marketable exit全部相关qty。
- 反手必须是新交易，不得以“继续摊平”规避已失效前提。

### RANGES-C31-S10：Broad-Channel / Stairs Countertrend Scale

- 类型：高级逆channel策略。
- 依据，PDF p.596–597、600–601、614–617：非强趋势的broad channel、trending range或stairs可在新极值逆向分档，目标测试channel起点/breakout point。
- 仅two-sided broad channel；至少2 pushes，推进衰减，非session末小时。
- Entry在swing extremes或固定`0.5–1.0ATR`间隔，最多3档，首仓≤常规33%。
- Stop在最终结构外；目标prior breakout point/channel start/首档价。
- Tight/strong channel由N02硬禁用。

### RANGES-C31-S11：Scale-Out Winning Position

- 类型：盈利仓分批退出。
- 依据，PDF p.596、602、606–607、610、614–615：可在2R、固定间隔、旧swing、强trend-bar close及第三推逐步获利，余仓跟踪。
- 基准档：`25% @ 2R, 25% @ 4R, 25% at climax/opposite signal, 25% runner`；按品种最小qty调整。
- 或使用固定`0.5–1.0ATR`间隔，但只能预注册一种主方案。
- Stop随确认swing移动；第三推/大回调风险时停止加仓并提高退出比例。

### RANGES-C31-S12：Scale-Out Losing Position

- 类型：风险递减退出。
- 依据，PDF p.602：若预期反转弱于原判断，可先回补部分亏损仓，价格继续不利再减仓，并可能在更佳位置按新signal重建。
- 当remaining EV降级但未到S09硬失效时，分批减`25–50%`，同步缩小风险。
- 后续重建必须出现独立signal且总episode风险不恢复到已损失前的超额水平。
- 禁止用scale-out隐藏完整止损；报告episode累计亏损与最大暴露。

### RANGES-C31-S13：Risk-Neutral Spike Re-Add

- 类型：盈利保护后的加仓。
- 依据，PDF p.613–614：旧swing仓移到breakeven后，可在新spike close增加scalp/swing仓，使合计风险不超过平常风险，即使名义qty变大。
- 只有已成交仓的active stop已到成本后breakeven，才释放risk budget。
- 每次新add按自身stop计风险；`remaining_risk <= normal_risk`始终成立。
- Pause bar停止re-add；强反向signal退出对应新仓，旧runner按独立规则管理。

### RANGES-C31-S14：Prior-Pullback / ADR Scale Spacing

- 类型：加仓网格参数化。
- 依据，PDF p.599–602、610–611、616–617：档距可依据先前pullback、当日平均range、明显stop位置或后续reversal signal，而非固定绝对点数。
- 候选spacing=`0.5–1.0 prior_pullback`, `0.10–0.25 ADR`, `0.25–0.75ATR`。
- 训练期选择后walk-forward冻结；每档需满足最小tick与spread倍数。
- Fixed-grid与structure-trigger版本分别报告fill率、平均档数、MAE和净EV。

### RANGES-C31-S15：Near-Obvious-Stop Limit Entry

- 类型：高级流动性/假突破方案。
- 依据，PDF p.615–617：明显2–5点stop有时被精确触及后反转，scale trader可在其前一tick加仓，但必须有range/channel大背景。
- Obvious stop必须由入场时可见结构与波动推导；limit在其前`1tick–0.05ATR`。
- 仅S03/S10合格时开放，final stop仍在结构失效位且S01风险不变。
- 与真正stop fill的基线比较；不能把每次触stop后反转事后选为样本。

### RANGES-C31-N01：新手默认禁止逆行加仓

- 类型：`NEGATIVE`治理约束。
- 依据，PDF p.596–603：scale-in复杂、压力大，错误会造成巨大亏损，多数交易者应止损后等待新entry。
- 开放门槛：单仓策略样本外稳定、至少`100–300` trades、订单/风险审计零违规。
- 未达门槛只做shadow simulation，不实际增加仓位。

### RANGES-C31-N02：Strong Trend 禁止逆势 Scale-In

- 类型：`NEGATIVE`硬否决。
- 依据，PDF p.599–601、608–609、614：若相信强趋势会继续，就应等待更佳逆势价；唯一允许的是顺趋势press。
- Strong spike/tight channel/Always-In strength达标时，countertrend add数量必须为零。
- 逆势首仓若已存在，按S09退出，不因价格更差增加。

### RANGES-C31-N03：禁止无上限 Dollar-Cost Averaging

- 类型：`NEGATIVE`尾部风险约束。
- 依据，PDF p.598–602：强bear spike中不断买入会使仓位巨大，并常在sell climax底部被迫退出；低价不等于价值。
- Scale次数、最终stop和最大loss必须硬编码；任何一项缺失则拒绝首单。
- 不使用martingale倍增；默认等qty或递减qty，增长qty需独立尾部风险批准。

### RANGES-C31-N04：Final Hour 禁止逆势 Scale-In

- 类型：`NEGATIVE`时间约束。
- 依据，PDF p.601：临近收盘没有足够时间等待反转，容易被迫在大亏时平仓。
- 正常日内策略在session最后`45–90分钟`关闭新countertrend scale；只允许减仓/平仓。
- Overnight授权是独立策略，不能绕过该约束。

### RANGES-C31-N05：加仓不得源于 Hope 或 Breakeven 执念

- 类型：`NEGATIVE`前提约束。
- 依据，PDF p.597–599：市场逐tick变化；原目标不现实时应接受亏损，不能希望回到旧均价。
- 每次add前必须重新通过regime、location、signal与EV gate；“降低均价”本身不是理由。
- S09触发后任何同episode追加订单均视为违规。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 596–599 | scale定义、顺势/逆势、初仓缩小、前提变化、机构加仓与危险摊亏 | S01–S06、S09、N01、N03、N05 |
| 599–603 | 合格场景、变量与EV、第二推进退出、末小时、组合计划与独立second entries | S01–S03、S06、S09–S10、S14、N02–N04 |
| 603–604 | Figure 31.1：强trend中的第二/第三独立signal及spike press | S04、S06、N01 |
| 605–607 | Figure 31.2：半仓在原stop加仓、组合均价、旧高目标与分批退出 | S02、S07–S08、S11 |
| 607–608 | Figure 31.3：trending range底部机构分档防守与失效位 | S03、S09 |
| 608–610 | Figure 31.4：强channel顺势加仓、EMA回调及组合退出 | S05、S07–S08、N02 |
| 610–611 | Figure 31.5：陡EMA回调网格、首档breakeven与低档盈利 | S02、S08、S14 |
| 611–614 | Figure 31.6：spike close加仓、pause停止、breakeven释放风险预算 | S04、S11、S13 |
| 614–615 | Figure 31.7：非强channel逆势分档、第三推获利、固定/信号档位 | S10–S12、S14、N02 |
| 615–617 | Figure 31.8：明显stop前入场、stairs新低、L2强制退出 | S09–S10、S14–S15 |

## 4. 回测验收

- 对每个scale episode保存全部计划档位、订单/成交时间、组合均价、最终stop、最大计划风险和取消原因。
- 最坏路径假设所有档位成交后立即gap到stop；组合风险超预算的episode必须为零。
- 后续独立signal只用当时数据计算EV；不得因为首仓亏损降低signal门槛。
- 报告逐fill P&L及episode P&L、平均/最大档数、最大名义qty、MAE/MFE、尾部损失和risk of ruin。
- Scale-in与single-entry基线保持相同账户风险；scale-out方案完整计多次佣金和limit未成交。
- Strong trend逆势、末小时逆势、无stop/无上限网格、premise失效后追加均设自动硬测试。
- Spacing、档数和qty做walk-forward及跨品种敏感性测试，不用图例固定点数拟合。
- OHLC同bar多档成交与stop先后不明时使用最不利顺序，并另报可行上下界。
- Figure 31.1–31.8仅作章节例证，不作参数或绩效证据。
