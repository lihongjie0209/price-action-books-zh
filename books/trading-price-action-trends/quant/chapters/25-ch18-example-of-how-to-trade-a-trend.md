# 第 18 章：如何交易趋势的示例

## 元数据

- 英文来源：`books/trading-price-action-trends/en/chapters/25-ch18-example-of-how-to-trade-a-trend.md`
- PDF 页码：321–338
- 图表：Figure 18.1；正文已逐bar完整解释案例，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 执行框架

本章的首要变量不是某一种形态，而是`Always-In`趋势状态。所有入场共享以下约束：

```text
direction ∈ {BULL, BEAR, NONE}
structural_risk = abs(entry - worst_case_stop)
position_size = floor(account_risk_budget / (structural_risk * point_value + costs))
trade_plan ∈ {SWING, SCALP}  # 入场时冻结
```

- BULL状态只允许`LONG/FLAT`，BEAR状态只允许`SHORT/FLAT`；反向交易必须进入独立研究组。
- 趋势确立但没有理想回撤时，允许用正常仓位的 `0.20–0.50` 建立初始小仓；止损仍放在结构失效点。
- 结构止损扩大为正常距离的 `m` 倍时，仓位缩至约 `1/m`，账户最坏风险不变。
- 一次趋势最多选择 `1–3` 个独立swing入场；其他信号作为管理事件，不得无限累计仓位。

## 2. 规则卡

### TRENDS-C18-S01：趋势确认后的最小顺势参与

- 类型：趋势状态与基础入场策略。
- 依据，PDF p.321、323–324、336–338：趋势本身就是至少小仓入场的理由；确认bull trend后只能long/flat，bear trend后只能short/flat。
- Setup：Always-In翻转并满足至少两项：强breakout bar、1–2bars跟进、突破opening range/主要swing、同向EMA斜率、连续同向高低点。
- 入场：优先等待下一次小回撤；若 `3–5bars` 无回撤，以市价/收盘或1–2ticks回撤进入 `0.20–0.50` 标准仓位。
- 止损：spike起点、翻转signal极值或最近结构swing外，取最能否定趋势前提者。
- 加仓：只有价格有利移动并能上移结构止损后，才补到标准仓位；总风险始终≤预算。
- 目标：按SWING计划管理至S07/S08退出。
- 失效：Always-In反转或结构止损触发。

### TRENDS-C18-S02：趋势中的 Stop-Entry 入场族

- 类型：统一顺势拉回策略。
- 依据，PDF p.321、326、330–332、336：合理stop entries包括EMA High/Low 2、wedge flag、flag breakout pullback、强spike中的High/Low 1及强趋势swing breakout。
- 候选形态：
  - EMA附近High 2/Low 2；
  - 三推进wedge flag；
  - flag突破后的首次回测；
  - 非climax强spike的High 1/Low 1；
  - S05的旧swing突破。
- 入场：signal bar顺势极值外 `1tick–0.10ATR`。
- 止损：pullback swing外；若仍处初始spike，允许使用spike起点并相应缩仓。
- 目标：旧趋势极值、2R第一管理点、趋势跟踪余仓。
- 排名：有EMA/水平位重合、第二入场或强signal加分；tight range中的普通High/Low 2降级，等待第三推进或明确突破。
- 禁用：High/Low 1发生在明确buy/sell climax之后，转S08等待复杂回调。

### TRENDS-C18-S03：强趋势中的高级 Limit-Entry 入场族

- 类型：高级成交研究。
- 依据，PDF p.321–324、330–334：强spike中可买bull close、第一根bear close、prior bar低点、trend line、旧swing及安静EMA flag；这些入场逆着当前一小段波动，难度更高。
- 仅在trend score≥ `0.70` 且S01方向未失效时启用。
- 限价候选：prior bar低/高、bar midpoint、trend line、EMA、prior swing、弱High/Low 1/2 signal极值、breakout test。
- 距参考位网格：`0/0.10/0.25/0.50ATR`；固定点数例子必须转换为ATR或当日range比例。
- 成交模型：同时报告触价即成交、穿越1tick成交和排队折损模型。
- 止损：共同结构失效点，不得为提高仓位把stop放到limit噪声内。
- 目标：旧极值、1R/2R；spike close入场需允许宽止损并按S06缩仓。
- 禁用：趋势已出现明显双向交易、成熟channel连续selling/buying pressure，或limit加仓会超过总风险。

### TRENDS-C18-S04：20 Gap Bar 首次均线回测

- 类型：完整顺势策略。
- 依据，PDF p.323、332–334、338：趋势连续20bars以上未触及EMA后，首次EMA回测通常形成顺势机会并测试趋势极值。
- Setup：bull中连续 `20+` 已完成bars的低点在EMA上方；bear对称。宽松版本允许极值触及但收盘未穿越，单独报告。
- 入场A：EMA顺势侧1tick的limit。
- 入场B：首次反向trend bar收盘穿越EMA后按收盘入场。
- 入场C：两腿回调结束的High/Low 2 stop entry。
- 止损：完整回调swing外；可预设最多 `2–3` 腿limit，但总风险固定。
- 目标：旧趋势极值、首次入场价整体退出、1R/2R分别测试。
- 失效：反向spike穿越EMA和主要trend line并有跟进，不能把所有深回调都归为20-gap延续。

### TRENDS-C18-S05：极强趋势的旧 Swing 突破追随

- 类型：突破入场策略。
- 依据，PDF p.321、334–335：趋势很强时可在旧swing high上方买、旧swing low下方卖，以避免等待不存在的完美回撤；但回撤入场通常风险收益更好。
- Setup：trend score≥ `0.80`，最近突破仍有跟进，且尚未出现S08成熟climax或明显双向交易。
- 入场：旧swing外1tick stop；该swing必须实时确认。
- 止损：突破signal bar或最近pullback swing外；高周期旧swing导致止损更宽时按S06缩仓。
- 目标：1R/2R、测量移动、趋势跟踪。
- 降级条件：回撤持续时间和深度增大、反向bar增多、旧高/低处开始反复失败；此后旧极值用于止盈而非新开仓。

### TRENDS-C18-S06：结构止损与固定账户风险仓位

- 类型：风险组件。
- 依据，PDF p.322–323、325–328、332–337：止损可能需要放在spike起点或最坏情形失效位；风险距离越大，仓位必须越小，scaling总风险不能扩大。
- 每次交易先冻结`worst_case_stop`，再计算仓位；禁止先定合约数再迁就止损。
- 单笔预算初测为权益的 `0.25–1.00%`（`PROXY`），滑点和佣金计入。
- 宽止损上限研究：当日平均range的 `0.50–0.75`，这是`AUTHOR`的经验范围，不代表统一止损。
- Scaling：最多 `2–4` 腿；在每个候选价格上计算全部腿同时持有且打共同止损的损失，必须≤原预算。
- 若计算仓位低于市场最小单位，则跳过交易，不得缩短结构止损。
- 所有固定ticks、点数或美元案例统一转换为ATR、ADR和R，避免资产/年代过拟合。

### TRENDS-C18-S07：Swing 持仓、2R减仓与结构跟踪

- 类型：仓位管理策略。
- 依据，PDF p.324–329、333、335–338：swing trader需要大盈利覆盖低胜率；强趋势应至少持有一部分，常在2R减半，其余至明确反转或收盘，并把stop跟到最新higher low/lower high外。
- `trade_plan=SWING`在入场时冻结；初始目标不得因恐惧改成scalp。
- 第一减仓比较：`1R/2R/3R`；本章主模型为2R减 `25–50%`。
- 余仓止损：每次创新趋势极值后，移至最近已确认higher low/lower high外。
- 入场价被首次回测后又创新极值，可把stop至少移到breakeven或该回测swing外；此前不自动保本。
- 最终退出：clear opposite signal、Always-In翻转、S09状态转换或session收盘。
- 若重新加回已减仓部分，必须把它标为新trade leg并重新检查总风险，不能掩盖路径风险。

### TRENDS-C18-S08：成熟 Spike-and-Channel 高潮退出与回调

- 类型：止盈与条件反转策略。
- 依据，PDF p.331–334、338：成熟趋势中第三推进、第三次climax和异常大趋势bar常结束channel，随后预期至少两腿、约10bars并测试EMA。
- Setup：已有spike-and-channel；出现第三推进或第三个climax，最终bar range/body≥ `1.5–2ATR`，并测试trend-channel line/测量目标。
- Swing多头/空头：在最终bar收盘、其外真空测试或下一反转signal分批止盈。
- 逆势scalp仅为高级分支：需强反转bar，目标EMA/第一腿，仓位≤标准的0.5。
- 原趋势再入场：等待 `2legs`、约 `10bars`、EMA测试或High/Low 2；这些为候选而非全部强制。
- 失效：高潮后继续出现强同向跟进，则不逆势加仓，等待新的结构极值。

### TRENDS-C18-S09：趋势向交易区间的状态转换

- 类型：市场状态转换与退出规则。
- 依据，PDF p.328、334–335、337–338：回调跌破最近结构低/高、双向交易增强且新推进缺少趋势bar时，趋势可能转为区间；管理方式必须随之改变。
- 转换分数候选：
  - 最近结构swing被突破；
  - trend line被明显突破并在外侧停留；
  - 新趋势推进无强trend bar；
  - overlap rate≥0.65；
  - 两侧各出现至少2次有效交易压力。
- 满足 `3/5` 标记`TREND_TO_RANGE_CANDIDATE`；反向spike及lower high/higher low确认才标`OPPOSITE_TREND`。
- 动作：停止S03/S05追价，余仓减持或按结构stop；后续采用区间较小目标。
- 从long直接reverse short或反向操作作为独立高级模型；标准模型先平仓、重新评估。

### TRENDS-C18-N01：禁止逆趋势反复猜顶底

- 类型：`NEGATIVE`。
- 依据，PDF p.323–324、329–330：强趋势中约80%的反转尝试会失败并演化为旗形；反复逆势scalp会累积小亏损并妨碍真正的顺势入场。
- BULL状态禁止普通bear reversal short，BEAR对称；只有S08高级高潮分支或正式Always-In翻转例外。
- 每个被过滤的逆势信号仍需记录，以验证过滤价值，不能只陈列成功旗形。
- “价格已到屏幕顶部/看起来过度延伸”不是可测试的入场条件。

### TRENDS-C18-N02：入场后不得切换 Scalp/Swing 计划

- 类型：`NEGATIVE`。
- 依据，PDF p.324–326：swing因近期亏损而过早scalp会失去必要的大盈利；scalp达到目标后临时改成swing又会把高概率小盈利变成止损。
- 入场必须写入`trade_plan`、初始stop、目标和管理算法，并在平仓前保持不变。
- `SCALP`要求单独估计足够高的胜率和全部成本；不允许仅因上一笔后来走远而取消本笔目标。
- 参数变化只能发生在预定义状态事件上，并记录为新策略分支，不能由浮盈亏或近期交易结果触发。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 321–323 | stop/limit入场清单、20-gap、scaling、只顺势 | S01–S06 |
| 323–326 | spike风险、channel困难、scalp与swing计划/期望值 | S06、S07、N01、N02 |
| 326–329 | swing入场、trail、宽止损、趋势转区间 | S06、S07、S09 |
| 329–332 | GS趋势日逐bar入场、微通道、High 2及高潮 | S01–S05、S08 |
| 332–334 | 20-gap、固定回撤、风险仓位、两腿回调 | S04、S06–S08 |
| 334–336 | 趋势线、旧swing突破、分批止盈和仓位上限 | S05–S09 |
| 336–338 | 早期趋势确认、小仓参与、结构跟踪与第三推进 | S01、S02、S07–S09 |

## 4. 回测验收

- Always-In和trend score逐bar生成；不得用当日收盘后标签挑选“趋势日”。
- S01比较立即小仓、只等High/Low 2和完全不追价三种参与模型。
- S02各形态分别报告，不能把所有顺势入场合并后只展示总体绩效。
- S03必须使用真实limit成交模型，并与S02 stop-entry在相同事件上配对比较。
- S04严格核验连续20bars计数，报告第一次EMA触及后的旧极值测试概率和时间。
- S06逐bar重估开放风险，报告最大合约数、最大不利路径和所有scaling腿共同止损损失。
- S07用完整交易路径比较1R/2R/3R减仓与全仓trail，不能只比较最终最高浮盈。
- S08报告第三推进、第三climax和大bar各自的边际预测力。
- S09建立trend→range→opposite trend状态转移矩阵并报告确认延迟。
- Figure 18.1仅作章节案例，不作参数拟合或绩效证据。
