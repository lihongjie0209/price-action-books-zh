# 第 6 章：缺口

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/13-ch06-gaps.md`
- PDF 页码：159–179
- 图表：Figure 6.1–6.5；另交叉引用Figure 18.4。正文与图注足以定义规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Gap 候选与延迟分类

```text
traditional_bull_gap = low[t] > high[t-1]
open_close_gap = open[t] - close[t-1]
micro_bull_gap = low[t+1] - high[t-1]       # t为trend bar
breakout_test_gap = test_low - breakout_point
```

- `BREAKAWAY_CANDIDATE`：新趋势起点的gap/强trend bar。
- `MEASURING_CANDIDATE`：趋势中段gap保持开放并获得follow-through。
- `EXHAUSTION_CANDIDATE`：成熟趋势末端gap很快回补，随后复杂修正或反转。
- 分类是随新bar更新的状态，不是gap形成当刻的事实；同一gap可能从breakaway/measuring候选转为exhaustion。
- Intraday把所有强trend bars视为功能性gap，但必须记录具体定义，不能把bar body、三barmicro gap和breakout-test gap混成一个数值。

## 2. 规则卡

### RANGES-C06-S01：Traditional/Opening Gap 状态分类

- 类型：跨session状态组件。
- 依据，PDF p.159–162、169–176：传统gap按趋势位置及后续行为分breakaway、measuring、exhaustion；开盘gap失败是常见exhaustion/opening reversal。
- Gap在session open冻结：`gap_size/ATR20`和`gap_size/ADR20`，方向相对prior session high/low/close分别记录。
- Breakaway确认：突破range/趋势结构、Always-In同向且 `2–3bars` 跟进。
- Measuring确认：已有趋势 `5–10+bars`，gap后继续同向且在测量目标前不回补。
- Exhaustion确认：成熟趋势/阻力支撑处gap，`1–5bars` 内回补并出现反向follow-through。
- Ordinary：位于range/spike系列且不满足以上条件。
- 最终标签用于评估；交易只能使用当时的candidate与确认事件。

### RANGES-C06-S02：Trend Bar 作为 Intraday Gap

- 类型：统一breakout组件。
- 依据，PDF p.160–164、171–175：所有trend bars都是spike、breakout、climax和功能性gap；高流动intraday市场虽少传统gap，行为相同。
- 对body/range≥0.60且range≥ `1.0ATR` 的trend bar建立gap event。
- 记录三个边界版本：bar body、bar[t-1] extreme→bar[t+1] extreme、最近被突破swing→首次pullback。
- 若位于新趋势起点，按S03；趋势中段按S04；成熟末端按S07。
- 多个版本并行保留，后续测量目标不能选择事后最准确者。
- 稀疏市场的真实gap与高流动市场trend bar分层，不假定流动性差异无影响。

### RANGES-C06-S03：Breakaway Gap 的趋势参与

- 类型：完整突破策略。
- 依据，PDF p.159、163–167、170：趋势初期开放gap是强度迹象；早期测量目标通常太近，不应据此过早止盈。
- Setup：S01/S02 gap突破已登记range、swing或反转结构，并使Always-In翻转。
- 入场：强breakout close小仓、首次 `0–0.25ATR` pullback或breakout test。
- 止损：breakout bar/新趋势起点外。
- 目标：1R/2R、ADR或更大结构目标；早期micro-gap自身等幅只作强度特征。
- 若首次pullback不回到breakout point，增加trend score；轻微穿越1–2ticks仍保留宽松候选。
- 强势回补bar并有反向跟进则转S07 exhaustion/failure。

### RANGES-C06-S04：Measuring Gap 投射

- 类型：目标与止盈组件。
- 依据，PDF p.159–161、163–168、170–177：趋势中段gap的中点常近似整腿中点；从leg origin到gap midpoint的距离向前投射。
- 确认时冻结：`M=(gap_low+gap_high)/2`，`H=abs(M-leg_origin)`。
- 方向目标：`M + direction * {0.75,1.0,1.25}H`。
- 优先选择趋势已运行约 `5–10bars` 后、仍开放并有follow-through的gap。
- 到目标zone `±0.10–0.30ATR` 分批止盈；只有额外反转setup才逆势。
- 多个gap/起点产生的目标全部保留；目标confluence只统计独立几何来源。

### RANGES-C06-S05：Negative Measuring Gap

- 类型：弱测量目标组件。
- 依据，PDF p.165–166、170–171：pullback略穿breakout point形成数学上的负gap，仍可能准确但可靠性较低；stairs经常如此。
- bull定义：`test_low-breakout_high<0`；bear对称。
- 允许穿越深度 `0–0.25ATR`，更深则不再作为gap模型，只按普通pullback。
- midpoint仍取breakout point与test extreme均值，按S04投射。
- `POSITIVE/ZERO/NEGATIVE`严格分层报告，negative不能与开放gap合并宣传命中率。
- 只作为目标/状态证据，不单独产生入场。

### RANGES-C06-S06：Micro Measuring Gap 与 Open-Close Gaps

- 类型：短结构强度组件。
- 依据，PDF p.163、166–168、178–179：三根trending bars中bar3与bar1不重叠形成micro gap；连续2个以上同向open-close gaps也是强度迹象。
- Micro gap只有`t+1` bar完成后确认；严格版本要求正gap，宽松版允许0或1–2ticks负gap。
- Open-close strength：最近 `2–4bars` 至少2次同向`open-close` gap，且bar bodies同向、非低量doji环境。
- 趋势早期：只上调强度，不以micro等幅过早止盈。
- 趋势中段：可用S04 midpoint目标；目标在确认时冻结。
- Gap被回补只是弱化，不自动反转；需结合S07。

### RANGES-C06-S07：Exhaustion Gap 与两腿修正

- 类型：成熟趋势止盈/反转策略。
- 依据，PDF p.159–161、167–169、171–178：长趋势后异常大gap/trend bar常是climax；回补后通常至少约10bars、两腿修正，偶尔正式反转。
- Setup：趋势持续 `10–30+bars`，gap/trend bar range≥最近20bars中位数 `1.5–2.5倍`，并接近预登记目标/趋势通道线。
- Gap回补并出现强反向bar时，原趋势仓位减 `50–100%`。
- 反向入场：强反向bar、第二信号或breakout pullback；不在gap刚出现时盲目fade。
- 止损：exhaustion极值外。
- 目标：gap另一侧、EMA、两腿且约10bars、1R/2R。
- 若gap后继续强趋势bars且pullback浅，重新分类S04 measuring候选，不坚持顶部/底部判断。

### RANGES-C06-S08：Island Reversal

- 类型：多bar反转组件。
- 依据，PDF p.160–161、169：旧趋势exhaustion gap后出现反向breakout gap，之间bars形成island；回测island边缘失败可形成lower high/higher low。
- 检测：两个相反方向传统gap间隔 `1–12bars`，第二gap收盘后仍开放。
- 入场A：第二gap使Always-In翻转后的首次pullback；入场B：island边界回测失败。
- 止损：island最终极值/回测极值外。
- 目标：10bars两腿、旧趋势起点、island高度、1R/2R。
- Intraday功能性island与传统跨bar island分层，不能仅凭两根相反trend bars强行等同。

### RANGES-C06-S09：Moving-Average Gap Bar

- 类型：趋势/区间双模式组件。
- 依据，PDF p.164、174–177：强趋势首次MA反侧gap bar常测试趋势极值；普通range中的MA gap则可fade回EMA。
- Trend模式：bear trend首次bar low>EMA，sell stop逐bar跟在signal low下直到成交，允许一次second entry；bull对称。
- Trend止损/目标：MA gap swing外；目标旧趋势极值、1R/2R。
- Range模式：价格在EMA一侧约 `10–20bars` 后反向越过，反转bar仍与EMA有gap且到EMA有 `0.5–1R` 空间；向EMA scalp。
- Range止损/目标：signal extreme外；EMA或range中点。
- Trend/range状态必须在信号前确定，不能用同一MA gap同时声称两个方向。

### RANGES-C06-S10：Gap Magnet 的接近交易

- 类型：目标接近/真空效应组件。
- 依据，PDF p.162、168–169：不是“所有gap必填”，而是所有旧价可能被测试；gap作为magnet，在价格靠近时吸引力增强。
- 只有价格距gap边界≤ `0.25–0.75ATR` 且当前推进朝gap、无中间更近结构时启用。
- 顺磁体方向可持仓至边界前 `1tick–0.10ATR`；不因gap存在从远处新开仓。
- 到达边界后依据follow-through决定回补或反转；预设limit止盈与穿越跟踪分别测试。
- 记录未填gap的删失样本和等待时间，禁止只统计最终填补者。

### RANGES-C06-S11：多个 Gap/Breakout Point 的 Confluence

- 类型：目标聚类组件。
- 依据，PDF p.167–168、176–178：大bar可同时突破多个swing，产生多个gap投射；与channel line、高周期line或range高度重合时更可能止盈/反转。
- gap确认时生成所有当时已知、独立的breakout points，最多最近 `3–5` 个。
- 目标在 `0.10–0.30ATR` 内聚为zone；同一bar的高度变体不重复计独立票。
- 顺势仓位在cluster减仓；逆势需强signal或第二入场。
- 报告cluster size与反转/停顿概率的单调性，未证实时不赋主观置信度。

### RANGES-C06-N01：Gap 类型不能在形成时被确定

- 类型：`NEGATIVE`。
- 依据，PDF p.159–162、169–171：gap后来可能从measuring候选变成exhaustion；标签本身不如后续价格含义重要。
- 禁止在gap bar上使用最终`BREAKAWAY/MEASURING/EXHAUSTION`标签入场。
- 只允许candidate与逐bar确认；最终标签仅用于结果评估。
- 分类模型必须保留`ORDINARY/UNRESOLVED`，不能强迫每个gap属于三大类型。

### RANGES-C06-N02：“所有 Gap 都会填补”不是入场策略

- 类型：`NEGATIVE`。
- 依据，PDF p.162、168–169：市场普遍回测旧价，gap只是众多magnet之一；远距离基于必填信念逆势会忽略强趋势。
- 禁止仅因开放gap存在就逆Always-In入场。
- 必须满足S10距离/路径条件，或S07/S08明确反转结构。
- 未在研究窗口内回补的gap必须作为右删失记录，不能删除。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 159–162 | traditional gap分类、intraday exhaustion/island及后续裁决 | 第1节、S01、S07、S08、N01 |
| 162–164 | gap magnet、trend bar等价、三bargap | S02、S06、S10、N02 |
| 164–167 | MA gap、breakaway/measuring/negative/micro gap | S03–S06、S09 |
| 167–169 | late climax、多个breakout points、gap fill | S07、S10、S11 |
| 169–175 | 日线与intraday各类gap的动态分类 | S01–S08、N01 |
| 176–179 | MA gap、测量目标、高潮及open-close gaps | S04、S06、S07、S09–S11 |

## 4. 回测验收

- 每个gap保存具体定义、candidate历史及最终标签；不得覆盖中间状态。
- S01按gap/ATR、gap/ADR、趋势位置和open context分层。
- S02多个边界版本并行，不以最终目标命中选择定义。
- S03/S04验证早期gap只作强度与中段gap作目标的差异。
- S05正/零/负gap独立报告，包含穿越深度敏感性。
- S06严格等到第三bar完成；open-close gap需排除低量/缺失成交造成的伪gap。
- S07建立measuring/exhaustion/range三终态并报告确认延迟。
- S09按预先确认的trend/range状态分流。
- S10采用生存分析或固定观察窗，保留未填gap。
- Figure 6.1–6.5仅作章节例证，不作参数拟合或绩效证据。
