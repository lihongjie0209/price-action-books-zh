# 第 21 章：如何交易 Trading Range 的完整示例

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/31-ch21-example-of-how-to-trade-a-trading-range.md`
- PDF 页码：398–408
- 图表：Figure 21.1；正文逐bar说明足以定义规则，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 实时 Range 状态

```text
range_candidate = 双向spikes/reversals、重叠与EMA反复测试累积
range_confirmed = 两侧各有至少一次已确认swing，且无breakout follow-through
location = (close - range_low) / (range_high - range_low)
bottom_zone <= 0.30; middle = 0.30–0.70; top_zone >= 0.70
```

- 边界仅用当时已确认swings滚动更新；扩大range只从新极值被确认后生效。
- 原文“80% breakout失败”只作研究假设，不作为固定概率。实盘/回测从目标市场估计。
- Range策略默认scalp；最低预期净收益≥初始风险，除非另有经验证的高胜率limit模型。

## 2. 规则卡

### RANGES-C21-S01：早盘 Trading-Range Day 评分

- 类型：regime分类器。
- 依据，PDF p.400–402：首bar doji、tails/overlap、弱follow-through、首小时4–5次反转、EMA处stall以及相反spikes提高range日概率。
- 首 `6–12bars` 计算：doji数、overlap均值、tail ratio、方向flip次数、EMA双侧close、strong bar后follow-through失败。
- 建议score：每项命中 `+1`；≥4为candidate，≥6且两侧swing形成则confirmed。权重须训练后锁定。
- Confirmed后启用S02–S09并禁用中部stop；strong breakout+follow-through触发S10退出range状态。
- 分类只从证据完成时生效，不把最终range day标签回填开盘。

### RANGES-C21-S02：底部 High 2 / Double Bottom Stop Buy

- 类型：初学者友好完整策略。
- 依据，PDF p.398–399、404–407：range底部第二次反转、H2、double bottom及bear-line break后的第二entry是最佳stop buys之一。
- Setup：`location<=0.30`；两次下探/High 2，优先有bull reversal bar、旧swing测试或bear channel breakout。
- 入场：signal高点上1tick stop；陡峭下跌时等待higher/lower-low breakout pullback。
- 止损：第二底/完整bottom structure下。
- 目标：range中点为最低，顶部为扩展；1R达成前没有足够空间则跳过。
- Strong downside breakout+follow-through使策略失效。

### RANGES-C21-S03：顶部 Low 2 / Double Top Stop Short

- 类型：S02镜像完整策略。
- 依据，PDF p.398–401、406–408：range顶部第二次反转、L2、double top及bull-line break后的第二entry是优质short。
- Setup：`location>=0.70`；两次上探/Low 2，优先bear reversal bar、buy climax或bull channel break。
- 入场：signal低点下1tick；止损在第二顶/完整top structure上。
- 目标：range中点、底部、1R/2R。
- Strong upside breakout+follow-through则失效并转S10。

### RANGES-C21-S04：Range 边缘 Wedge / Final-Flag Reversal

- 类型：三推与假突破策略。
- 依据，PDF p.398–399、404–408：底部wedge bull flag或跌破swing low后的final flag买入；顶部镜像卖出。
- 边缘完成3个push，第三推允许overshoot/undershoot；或突破边界后 `1–3bars` 收回。
- 入场：第一合格reversal signal；tight channel/强spike使用第二entry。
- 止损：第三推/假突破最终极值外。
- 目标：range中点、对侧、1R；多个triangle解释只生成一笔交易。

### RANGES-C21-S05：边缘 Breakout-Pullback 向 Range 内交易

- 类型：局部breakout恢复策略。
- 依据，PDF p.399、404–407：底部开始向上并pullback时买，顶部开始向下并pullback时卖；强bar后未成交limit也可体现方向紧迫性。
- Bull版：bottom structure上方breakout≥`0.5ATR`，随后pullback守住breakout point/形成higher low。
- 入场：pullback signal高点上stop，或预注册limit于breakout point；bear版镜像。
- 止损：pullback/底部结构外。
- 目标：range中点、顶部、1R/2R。
- 若breakout发生在大range中部，目标缩至下一内部swing，不当作trend breakout。

### RANGES-C21-S06：边缘 Exhaustion Spike / Large Trend Bar Fade

- 类型：高级limit/market策略。
- 依据，PDF p.399–401、403–407：range底部bear spike/大bear bar常是exhaustion，顶部bull spike镜像；需要宽止损和较强读盘能力。
- Setup：confirmed range边缘；末端bar≥`1.2–2.0ATR`、close靠近极值，且没有突破follow-through或下一bar出现hesitation。
- 保守版本等待reclaim/reversal bar；高级版本在bar close/旧swing外limit，必须单独回测。
- 止损：spike外 `0.25–0.50ATR` 或range外；按宽止损缩仓。
- 目标：range中点/1R；高级scale-in版本限制最多2次且总风险固定。
- 未确认range或strong trend day禁用。

### RANGES-C21-S07：弱 H/L1–2 Signal Bar 的 Limit Fade

- 类型：高级反向限价策略。
- 依据，PDF p.399–400、403、405–408：底部弱L1/L2可在低点附近买，顶部弱H1/H2可在高点附近卖；利用stop setup大概率失败。
- Weak signal：doji、body≤35%、与前2bars overlap≥60%，且位置在range外侧30%。
- 入场：底部signal低点处/下方limit long，顶部镜像short。
- 止损：range外或 `0.75–1.0ATR`；目标1R/中点。
- Limit fill、队列、穿透和未成交必须模拟；默认只供高级策略研究，不与S02/S03混合。

### RANGES-C21-S08：顺 Range Swing 的 Bear/Bull Close Entry

- 类型：方向恢复策略。
- 依据，PDF p.400、405–407：强bull swing起点可买bear close，强bear swing起点可卖bull close；失败countertrend信号会困住交易者并加速恢复。
- 必须先有边缘reversal与一根方向breakout bar；随后一根逆向bar不跌破/突破起点结构。
- 入场：逆向bar close、limit或其顺swing端stop；三种执行分开。
- 止损：swing起点外；目标中点/对侧、1R。
- Swing已到range中部后不新增close entry，避免追价。

### RANGES-C21-S09：盈利退出后再寻找反向 Setup

- 类型：持仓管理流程。
- 依据，PDF p.398、400–401：range交易按scalp，在另一边/目标处止盈；多数交易者不应直接reverse，而应平仓后等待独立反向signal。
- Long从底部入场：中点平 `50–75%`，顶部/1–2R退出其余；short镜像。
- Exit完成后清除旧仓，只有S02–S04等独立反向signal才开新仓。
- 不持仓“等待breakout”；到目标后若breakout真发生，由S10另行入场。
- 直接reverse版本只能作为独立高级实验，风险与滑点单独统计。

### RANGES-C21-S10：Range Breakout 的状态切换

- 类型：regime transition。
- 依据，PDF p.401–408：强bar本身不足，必须有immediate follow-through；若到边缘后hesitate/回到旧value区，仍是range。
- True breakout：close越界≥`0.25ATR`、bar≥`1ATR`，未来1–2bars有同向follow-through且回撤≤50%。
- 确认后关闭fade策略，等待breakout pullback顺突破入场；止损回range内。
- 无follow-through、ii/doji或迅速回range内，保持/恢复range并按S02–S04处理。
- 旧tight range具有magnet效应只能作特征；不得覆盖真breakout确认。

### RANGES-C21-N01：中部不做 Stop Entry

- 类型：`NEGATIVE`。
- 依据，PDF p.398、405–406：range中部赔率差，强局部breakout也可能只是大range内部摆动；很少应在那里stop入场。
- `0.30<location<0.70`时禁用纯H/L1–2、局部triangle和breakout stop。
- 仅允许已有边缘仓管理，或S10真突破确认后的pullback。
- Middle limit策略若研究，必须有独立价值/短目标模型，不纳入主策略。

### RANGES-C21-N02：不能用固定 80% 或低盈亏比替代验证

- 类型：`NEGATIVE`与风险约束。
- 依据，PDF p.398、400–401：书中80%与高手70–80%属于经验描述；初学者不应为1单位利润冒2单位风险。
- 不硬编码胜率；按固定breakout/failure定义样本外估计并给置信区间。
- 主策略要求净reward≥risk；若使用`reward<risk`，必须用独立样本证明成本后胜率超过breakeven并留安全边际。
- 仓位按完整止损距离计算，scale-in不得扩大总账户风险。

### RANGES-C21-N03：不要试图捕获全部信号

- 类型：`NEGATIVE`与组合约束。
- 依据，PDF p.400：range中信号很多，盈利不需要抓住全部；过度交易会累积成本和相关风险。
- 同一方向在同一range swing最多1个主仓+1次预注册加仓；辅助形态只加标签。
- 平仓后至少等待独立反向signal或 `1–2bars`，禁止无条件翻仓。
- 每日/每range设置最大交易次数、总风险与手续费预算，并报告边际交易的增量期望。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 398–400 | buy low/sell high、scalp、stop与limit setup清单 | S02–S08、N01–N02 |
| 400–402 | 经验型scale-in、利润/风险、早盘range线索、spike-channel | S01、S06、S09、N03 |
| 402–404 | EMA stall、双向spikes、失败信号与边缘价值 | S01、S06–S08 |
| 404–406 | 底部多次signal、wedge/H2、tight-range magnet、局部breakout | S02、S04–S05、N01 |
| 406–408 | 顶部climax/double top、底部H2、follow-through与退出 | S03、S06、S09–S10 |

## 4. 回测验收

- Range candidate/confirmed及边界逐bar保存，最终日型不得回填早期状态。
- 所有交易记录入场时`location`，主策略中部stop交易数量必须为零。
- Stop、market、limit与scale-in四类执行独立报告成交率、滑点、MAE/MFE。
- S02–S08同一range swing只分配一个主信号，避免重复计入同一价格运动。
- Breakout/failure固定定义后重新估计概率，不使用书中固定80%。
- 报告按range宽度、日内时段、波动率、首次/后续边缘测试分层的结果。
- Profit target与stop均从预计成交价计算并扣成本；reward<risk版本独立验收。
- S10只从follow-through确认bar切换regime，不能回填至breakout bar。
- Figure 21.1只作章节例证，不作参数拟合或绩效证据。
