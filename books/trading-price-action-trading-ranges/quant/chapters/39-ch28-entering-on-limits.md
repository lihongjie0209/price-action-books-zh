# 第 28 章：Limit Entry

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/39-ch28-entering-on-limits.md`
- PDF 页码：535–564
- 图表：Figure 28.1–28.5；正文与图注已完整说明规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Limit 执行模型

```text
limit_buy_fill 需要 ask/trade <= limit_price
limit_sell_fill 需要 bid/trade >= limit_price
OHLC保守模型：价格至少穿过limit 1tick才假设成交
marketable_limit：价格跨过当前offer/bid，按可成交簿价模拟
```

- Limit entry通常逆至少短期动量，允许更好价格但增加未成交、adverse selection和先逆行风险。
- 每笔保存`submit_time, limit_price, queue_ahead, first_touch, fill_time, fill_qty, cancel_reason`。
- 初学者默认禁用limit入场；只有stop策略样本外稳定后才开放本章高级模块。
- 所有固定tick/point示例改用`tick + ATR/ADR`双重归一化。

## 2. 规则卡

### RANGES-C28-S01：错过强 Stop Entry 后的 Original-Price Limit

- 类型：迟到补入策略。
- 依据，PDF p.535–537、546–547：错过极强stop entry数秒后，可在原价或差1–2ticks挂limit；普通好交易很少回来让迟到者入场。
- 仅限strong setup：regime一致、signal score高、breakout未到 `0.5R`、提交延迟≤`1bar`。
- Limit=`original_stop_price`或不利 `0–2ticks`；价格若先到目标的25–50%则取消，不追。
- 止损保持原结构stop，按实际fill重新计算qty。
- 与原stop candidate共享事件ID，不能把未成交/迟成交作为独立交易重复统计。

### RANGES-C28-S02：Strong Spike 的 Close / Tiny Pullback Limit

- 类型：顺势动量策略。
- 依据，PDF p.535–538、552–559：强spike中可在prior strong close、bar内回撤1–3ticks或prior-bar反端limit顺势入场；宽stop用小仓。
- Strong spike：连续 `2–4bars` 同向body≥70%、累计≥`1.5ATR`、无climax/resistance否决。
- Entry grid：prior close、current extreme回撤 `0.10–0.30ATR`、prior low/high；最多一主仓一加仓。
- 止损：spike起点/最近结构外；总风险固定。
- 目标：spike body measured move、1R/2R。
- Spike位于range极值或末端climax时禁用，交S08/S15。

### RANGES-C28-S03：Micro Gap / Breakout Point Limit

- 类型：breakout continuation策略。
- 依据，PDF p.536–538、556–557：breakout bar可能留下micro/measuring gap，可在breakout前一bar极值附近limit，期待gap保持。
- Bull limit=`pre_breakout_bar.high + 1tick`；bear镜像。
- Breakout需flip Always-In或strong body，但bar不能过度climactic。
- Stop在breakout structure另一侧；小gap版本允许 `2–4ticks / 0.15ATR` risk。
- 目标：breakout spike/形态高度measured move。
- 收盘穿回breakout point并follow-through则失效，不继续defend gap。

### RANGES-C28-S04：Strong Trend 中 Prior Bar / Micro-Channel Pullback

- 类型：顺势channel limit策略。
- 依据，PDF p.535、538–540、547、556–559：强bull/bear中首个prior-bar反向突破与micro-channel breakout常失败，可在prior low/high limit顺势交易。
- Trend score强；channel早期主测≤`10bars`或micro channel连续≥3bars无反向break。
- Bull在prior low及下 `0–2ticks`买；bear镜像。
- 止损：最近higher low/lower high或micro-channel起点外。
- 目标：旧极值、1R/2R；late channel转S07或停止追趋势。
- Climax/final flag/major resistance否决。

### RANGES-C28-S05：Opening Two-Bar Spike 的 Prior-Bar Test

- 类型：开盘顺势scalp/swing。
- 依据，PDF p.537：opening range形成时连续两根强trend bars，可在prior bar低/高limit，期待spike底/顶守住。
- 前 `3–6bars` 内连续2根同向body≥60%、small tails，累计≥`1ATR`。
- Bull limit在第二bar前一bar低点附近；bear镜像。
- Stop在opening spike起点外；目标旧极值、opening spike高度、1R。
- Gap/news slippage与首小时波动单独stress；第二bar为climax且触重大level时跳过。

### RANGES-C28-S06：Breakout Test / Breakeven-Stop Run Limit

- 类型：顺趋势回测策略。
- 依据，PDF p.538、540–541、545–546、551–552、559–561：强breakout后回测原signal high/low或breakout point，机构常在同一区域重新入场，reward/risk良好。
- Level在breakout时保存；测试容差 `1–2ticks / 0.10–0.20ATR`。
- Limit顺breakout方向；若测试动量强≥`1ATR`则等待stop confirmation而非limit。
- Stop在entry/signal bar另一端或最近swing外。
- 目标旧极值、breakout height、1R/2R。
- 同一level重复测试次数分层，第三次以上降低评分。

### RANGES-C28-S07：Channel Early/Late Phase Limit 切换

- 类型：趋势生命周期策略。
- 依据，PDF p.535、538–539、550–551：channel早期顺势在prior bar不利端入场；持续10–20bars并接近level后逐渐改为在外侧fade/获利。
- `channel_age<10bars`：只运行S04顺势limit。
- `10–20bars`：顺势size降至50–75%，要求EMA/line/support共振。
- `>=20bars`或第三推+resistance/support：停止新顺势limit，允许S15逆势candidate但需second signal。
- Age阈值以推进数/ATR稳健性分层，不单靠固定bars。
- Regime强breakout后重置新channel age。

### RANGES-C28-S08：Trading Range 边缘 Spike / Swing-Level Fade

- 类型：区间limit策略。
- 依据，PDF p.537–539、541–543、547–550、552–555：range底部买bear spike/旧swing low，顶部卖bull spike/旧swing high；可用ledge、weak H/L1–2等细化。
- Confirmed range；entry只在外侧20–30%，level测试≥2次更佳。
- Limit在prior swing/ledge/weak signal extreme，允许假突破缓冲 `0.10–0.30ATR`。
- Stop在range外；目标中点、对侧、1R。
- Spike若strong breakout+follow-through则取消fade并转breakout策略。
- Tight/barbwire版本只供高级模型且需真实queue/cost。

### RANGES-C28-S09：新趋势中 Failed H/L1–2 的 Limit

- 类型：反转后pullback策略。
- 依据，PDF p.539、547–549、555–559：wedge/double bottom等强反转后，旧趋势方向L1/L2或H1/H2多失败；可在其signal extreme limit顺新趋势。
- New regime需strong reversal、Always-In flip或second entry确认。
- Bull在L1/L2 signal low及下 `0–3ticks`买；bear镜像。
- Stop在新趋势起点/最终reversal极值外。
- 目标：新swing旧极值、measured move、1R/2R。
- 未确认flip或强旧趋势仍在时禁用。

### RANGES-C28-S10：Quiet EMA Flag / 20-Gap Limit

- 类型：均线顺势limit策略。
- 依据，PDF p.540、551–553：quiet bull/bear flag、20-gap/首几次EMA test可在prior bar、bear/bull close或EMA附近limit，股票尤其适用。
- Trend明确；pullback低动量、overlap适中、逆势bars小，EMA斜率同trend。
- Limit在EMA、prior bar反端或逆向bar close；多个level只选预注册优先者。
- Stop在pullback swing外；目标旧极值、1R/2R。
- Pullback强spike/穿EMA并follow-through则等待stop/second entry。

### RANGES-C28-S11：Spike-and-Channel 起点测试

- 类型：channel-base limit策略。
- 依据，PDF p.539、559–561：spike+channel结束后低动量测试channel底/顶，常形成double bottom/top flag，可limit恢复方向。
- 先确认spike和至少2个channel pushes；测试channel start容差 `0.10–0.30ATR`。
- Test必须低动量或出现buying/selling pressure；强breakout不fade。
- Limit在channel start/旧pullback swing；stop在最终test极值外。
- 目标25% bounce、channel中点、旧极值、1R/2R。

### RANGES-C28-S12：Trend Pullback 60–70% Reward/Risk Entry

- 类型：深回调limit方案。
- 依据，PDF p.542–543、559：趋势中约60–70% retracement可使新高/低目标约为risk两倍；不是Fibonacci魔法，而是结构与EV选择。
- 只在trend structure未破坏、无强反向spike时，按首腿幅度计算连续retracement `0.60–0.70`。
- Limit入场；stop在100% retracement外 `0.05–0.20ATR`。
- 目标旧极值/新极值，要求成本后reward/risk≥1.5–2。
- 与连续retracement grid比较，不把61.8%单独神化。

### RANGES-C28-S13：Countertrend Channel Scale-In

- 类型：高级channel fade与scale策略。
- 依据，PDF p.538–539、550–551：成熟bear channel可在prior swing lows下买并更低加仓，bull channel镜像；若第二次顺势setup触发必须退出/反手。
- 仅broader/two-sided channel，禁用strong spike/tight channel和临近收盘。
- Entry1在新swing extreme，Entry2再不利 `0.5–1.0ATR`；各 `50%` size。
- Stop在Entry2外 `0.5–1.0ATR`；总风险固定。
- 一次成交取scalp；两次成交回Entry1附近整体退出。
- Bear中L2/bull中H2触发时强制退出，允许按独立EV反手顺势。

### RANGES-C28-S14：Trending Trading Range 的 Measured-Move Fade

- 类型：趋势区间limit策略。
- 依据，PDF p.541–542、552–555：trending range新range常在前range等幅处结束，可在目标附近逆当前腿入场，测试前一range边界。
- 先实时确认upper/lower range及breakout；高度在breakout前固定。
- Entry在measured target前 `0–0.20ATR`，需末端pressure/climax或多次failure作第二理由。
- Stop=`0.5–1.0` range height外；目标breakout point/前range边界。
- Strong breakout无反向pressure时禁用，等待第二signal。
- 固定4–6点示例全部按range height比例实现。

### RANGES-C28-S15：Trend Line / Channel Line / Wedge Test Limit

- 类型：line fade策略。
- 依据，PDF p.542–543、559–564：可在trend line/channel line/wedge边界limit，但stop-confirmed entry通常更确定；strong bear中不断重画底线买入是亏损策略。
- Line在触达前由confirmed anchors固定；limit仅当regime支持方向或已有overshoot/climax。
- Entry在line±`0.10ATR`；stop在线外 `0.20–0.50ATR`。
- Tight/strong countertrend move禁用首limit，等待reversal bar/second entry。
- 将limit与stop-confirmed版本共享母样本比较净EV、MAE和漏单。

### RANGES-C28-S16：Failed Scalp Target 的顺趋势 Limit

- 类型：被困countertrend scalper策略。
- 依据，PDF p.539–540、547–551：强趋势中逆势scalp多失败；可在其目标前2–3ticks顺势limit，期待其无法取得所需完整move。
- 先由固定countertrend scalp定义计算其entry/target；在目标前 `0.10–0.30ATR` 放顺趋势limit。
- Stop在countertrend目标外 `0.20–0.40ATR`；目标旧趋势极值/1R。
- 仅strong trend且无climax；普通range中双方scalp均可能有效，禁用。
- 不能使用未观察订单，只用可复现的标准signal/target推断。

### RANGES-C28-S17：Marketable Limit / Strong Close Entry

- 类型：主动成交执行组件。
- 依据，PDF p.543、552–559：market order可视为穿过盘口的marketable limit；strong close/failed follow-through时交易者会在close主动成交。
- 只在S02/S08/S09等基础setup确认后使用，不单独生成方向。
- Buy limit价格≥current ask、sell limit≤bid，按实际盘口VWAP/slippage成交。
- Close数据回测用next-bar open+slippage，不能假设以已知close无延迟成交。
- 与被动limit比较fill、adverse selection和opportunity cost。

### RANGES-C28-N01：Limit Entry 不适合未稳定盈利者

- 类型：`NEGATIVE`治理约束。
- 依据，PDF p.535–536、545–547：limit逆短期方向、判断与情绪要求更高；初学者应先只用stop。
- 开放条件：stop-only策略至少 `100–300` 样本外trades、净EV>0、风险纪律通过。
- 未满足时limit candidate只记录不成交，用于shadow evaluation。
- 不因一次错过stop或当日亏损临时开启limit模式。

### RANGES-C28-N02：Strong Spike Alone 不是 Pullback Limit 理由

- 类型：`NEGATIVE`。
- 依据，PDF p.545–547、553–554：range顶部bull spike/趋势末端buy climax可能反转至少两腿10bars；bear镜像。
- Spike处于range外侧、third push、major target或连续climax时，禁止S02/S04逆回撤买卖。
- 需等待context确认、second entry或stop reversal signal。
- 不使用Fibonacci/band单独接下落/上涨中的当前趋势。

### RANGES-C28-N03：禁止盲目 Fade 每次 Breakout

- 类型：`NEGATIVE`。
- 依据，PDF p.543–545：多数breakout失败不意味着每次limit fade有edge；盲做stop或盲fade都会亏损。
- 每个limit仍须regime/location/reason/EV gate；单纯越prior high/low不够。
- Strong breakout+follow-through关闭fade，切顺势。
- 报告所有breakout candidate，避免只选成功失败样本。

### RANGES-C28-N04：Strong Always-In 趋势中不逆 Line 买卖

- 类型：`NEGATIVE`硬否决。
- 依据，PDF p.562–564：强bear中反复画channel line买入是错误方向；只有sell climax后strong reversal stop scalp才可考虑，bull镜像。
- Always-In强度达标且无major line break/overshoot reversal时，逆势line-limit交易数必须为零。
- Line被强bar穿越不自动成为更好fade价，而是trend strength证据。
- Countertrend只从第二signal或明确regime flip重新开放。

### RANGES-C28-N05：Limit Touch 不等于 Fill

- 类型：`NEGATIVE`执行约束。
- 依据，PDF p.545–546、551、558–559：limit通常需要价格穿越才成交；未成交本身可能体现urgency并迫使追价。
- OHLC主结果要求穿越1tick；真实L2/tape则按queue模拟。
- 未fill订单不能产生P&L；取消后stop chase视为新执行路径。
- Partial fill按实际qty计风险和收益，不假定整单成交。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 535–543 | stop/limit环境切换、强trend与channel、完整limit场景清单 | S01–S16、N01–N02 |
| 543–547 | marketable limit、breakout test、buy/sell vacuum、fill与context | S01、S06、S17、N03、N05 |
| 547–551 | failed H/L1–2、range/channel fade、scale-in与强制顺势退出 | S08–S09、S13、S16 |
| 551–555 | scalp fill、breakout tests、EMA、measured move/TTR实例 | S06、S10、S14、N05 |
| 555–559 | strong trend prior-bar buys、micro gap、quiet-day执行与retracement | S03–S05、S12、S17 |
| 559–564 | double bottom、dueling lines、line fades、强trend反例 | S06、S11、S15、N04 |

## 4. 回测验收

- 所有limit订单建模submit/queue/touch/penetration/fill/cancel，touch-as-fill与保守结果同时报告。
- S01–S17共享基础setup事件ID，同一price move不能因多种解释重复计盈。
- Passive limit、marketable limit、market和stop-confirmed版本用同一母样本比较。
- Strong trend、channel age、range edge、climax等状态逐bar确认，不得最终回填。
- Scale-in S13报告组合worst-case、gap stress、MAE、最大连续亏损和risk of ruin。
- 所有固定tick/point参数映射ATR/ADR并按波动regime敏感性测试。
- Line/level在提交前保存anchors与valid_from；未来重画数量必须为零。
- Limit策略仍需第25章成本后EV gate；gross edge被queue/slippage吞噬者拒绝。
- Strong spike/context否决和Always-In逆势否决必须有自动测试。
- Figure 28.1–28.5只作章节例证，不作参数拟合或绩效证据。
