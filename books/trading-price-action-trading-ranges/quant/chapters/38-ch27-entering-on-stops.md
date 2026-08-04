# 第 27 章：Stop Entry

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/38-ch27-entering-on-stops.md`
- PDF 页码：533–534
- 图表：Figure 27.1；正文已精确说明价格关系，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 订单与 Bar 定义

```text
signal_bar = 完成setup并据此计算entry stop的已完成bar
entry_price_long  = signal_bar.high + 1tick
entry_price_short = signal_bar.low  - 1tick
entry_bar = 市场首次触发entry stop的bar
```

- 若订单未触发，原bar仍为setup candidate；只有实际fill后才正式记录其为该交易的signal bar。
- Stop crossing可能gap-through，成交价应为可获得的下一价格而非理论stop价。
- 同一bar内同时触发entry、stop或target时必须使用更细数据，或采用保守最不利路径。

## 2. 规则卡

### RANGES-C27-S01：Signal Bar 外一 Tick 的 Stop Entry

- 类型：通用执行策略。
- 依据，PDF p.533：stop entry让市场以至少一tick的微趋势动量带入交易，是price-action最可靠的入场方式之一。
- Long：合格long setup完成后，在signal high上1tick放buy stop；short镜像。
- Order有效期主测 `1bar`，延长版 `2–3bars`须要求setup未失效且价格未先突破反端。
- 成交时保存理论stop、实际fill、gap/slippage和entry bar。
- 初始stop由S02设置；target由基础策略和第25章EV gate确定。
- Signal位于TTR错误边缘等被上游否决时，不因stop机制可靠而绕过。

### RANGES-C27-S02：Signal Bar 结构初始止损

- 类型：保护止损策略。
- 依据，PDF p.533：short entry的合理初始stop在signal high上1tick，long在signal low下1tick。
- Long stop=`signal.low-1tick`；short stop=`signal.high+1tick`。
- `initial_risk=abs(actual_fill-stop)`，仓位按第25章固定账户风险缩放。
- Signal bar过大使目标空间不足/qty为零则跳过，不人为收窄stop。
- Gap fill后重新计算真实risk；超过风险上限则在首可成交价取消/退出。

### RANGES-C27-S03：Strong Entry Bar 后收紧止损

- 类型：条件trail策略。
- 依据，PDF p.533：entry bar若有强方向body，收盘后可将stop移至其另一端；否则保留signal-bar stop直到强势推进。
- Strong long entry bar：bull body/range≥`0.60–0.75`、close位于顶部25%、range≥`0.5ATR`；short镜像。
- Entry bar完成后，long stop移至`entry_bar.low-1tick`，short移至`entry_bar.high+1tick`，但绝不向不利方向扩大。
- Entry bar不强则保持S02 stop，直到后续strong direction bar完成，再按该bar另一端trail。
- 比较立即收紧、首strong bar收紧、始终结构stop三版本的MAE/止损后恢复率。

### RANGES-C27-S04：Limit Target 的额外 Tick 成交模型

- 类型：成交与目标换算组件。
- 依据，PDF p.534：Emini中从signal极值外1tick入场，净4tick profit通常需价格越signal极值6ticks；limit target常需再穿1tick才可靠fill。
- 理论long target=`actual_fill + P ticks`；保守OHLC fill要求`bar.high >= target + 1tick`，short镜像。
- 有真实成交/盘口数据时用订单队列与实际fill替代额外tick假设。
- 因而从signal extreme所需总move约为`1 + P + fill_buffer` ticks；`fill_buffer`主测0/1tick。
- Target touch但未穿越标记`touch_no_fill`，交由第24/25章动态EV管理，不伪造盈利。

### RANGES-C27-S05：初学者 Stop-Only 执行模式

- 类型：策略范围限制。
- 依据，PDF p.533：初学者应先仅使用stop entries，直到能够稳定盈利，因为limit/market需要更复杂的逆势判断。
- `execution_mode=STOP_ONLY`时拒绝所有limit fade、scale-in与market-on-close入场；退出limit不受影响。
- 只运行通过regime、两理由和EV gate的stop setups。
- 绩效门槛建议：至少 `100–300` trades、样本外net EV>0、最大回撤在预算内，再研究limit模块。
- 模式切换是研究/治理参数，不因当日亏损临时改变。

### RANGES-C27-N01：Stop Entry 可靠不等于 Setup 有 Edge

- 类型：`NEGATIVE`。
- 依据，PDF p.533–534及前章上下文：stop只保证触发时有一tick动量，不能修复错误regime、TTR或负EV setup。
- 上游`regime_gate, TTR_gate, reason_gate, EV_gate`全部通过后才建立stop order。
- 不把“被触发”当作signal质量或成功概率证据。
- 按setup类别报告stop entry表现，不能把所有stop订单混成一个策略。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 533 | signal/entry bar、stop entry、一tick触发、初始与entry-bar stop | 定义、S01–S03、S05、N01 |
| 534 | 四tick利润需六tick signal-bar外走势、limit需额外tick | S04 |

## 4. 回测验收

- 每笔订单保存signal bar、order creation、trigger、actual fill和entry bar，未触发订单不算交易。
- Gap-through、同barentry/stop/target使用tick数据或保守路径。
- Initial risk从实际fill计算，仓位不得按理论stop价低估风险。
- S03只在entry bar完成后收紧，不能使用其最终close提前操作。
- Limit target分别报告touch、穿越和真实fill；OHLC主结果采用保守fill。
- Order expiry与取消原因固定，并对1/2/3bar有效期做样本外敏感性分析。
- Figure 27.1只作章节例证，不作参数拟合或绩效证据。
