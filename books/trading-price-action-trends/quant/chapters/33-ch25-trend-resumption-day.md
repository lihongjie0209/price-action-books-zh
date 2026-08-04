# 第 25 章：趋势恢复日

## 元数据

- 英文来源：`books/trading-price-action-trends/en/chapters/33-ch25-trend-resumption-day.md`
- PDF 页码：455–462
- 图表：Figure 25.1–25.4；正文与图注已完整说明，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 状态序列

```text
MORNING_TREND -> MIDDAY_CONSOLIDATION -> LATE_BREAKOUT
LATE_BREAKOUT -> RESUMPTION | REVERSAL_DAY | FAILED_BREAKOUT_RANGE
```

- `MORNING_TREND`：前约1小时出现净位移≥ `0.5–1.0ADR20` 或 `1.5–3ATR`，Always-In明确。
- `MIDDAY_CONSOLIDATION`：随后至少 `12–36bars` 的tight range或低动能逆向channel，净逆向位移不足以确认Always-In翻转。
- `LATE_BREAKOUT`：session fraction `0.60–0.90` 突破consolidation；原书最后1–2小时需转换为各市场时段比例。
- 最佳形态较少出现，检测器必须保留所有候选，不能以收盘结果筛选。

## 2. 规则卡

### TRENDS-C25-S01：趋势恢复日实时检测

- 类型：日型状态组件。
- 依据，PDF p.455–457：早盘约1小时强趋势，随后数小时区间，最后1–2小时恢复；中段常很窄并使交易者误以为行情结束。
- 顺序要求：morning trend必须在consolidation开始前确认，consolidation至少占session的 `0.25–0.50`。
- Tight range代理：range≤ `0.25–0.50ADR`、overlap≥0.60、EMA斜率接近0；宽松版允许三推进的低动能反向channel。
- 保存早盘腿起终点、中段range边界、原趋势方向和各状态首次确认bar。
- 状态只提示等待late breakout，不在range中部新增仓位。
- 若中段反向spike及channel确认，转第24章reversal候选。

### TRENDS-C25-S02：中段 Range 内的原趋势 Flag 入场

- 类型：提前顺势策略。
- 依据，PDF p.456–458：中段可有三次懒散逆向推进形成wedge/head-and-shoulders flag；多数反转形态失败并恢复早盘趋势。
- Setup：S01成立，中段range出现2–3个逆早盘方向推进，但斜率/实体弱于早盘腿。
- 触发：第三推进失败、High/Low 2、micro trend-line失败、首次MA gap bar或range原趋势侧的第二入场。
- 入场：signal bar外stop；range中部禁入。
- 止损：flag最终极值或range对侧。
- 目标：range原趋势侧、早盘趋势极值、S05等幅目标。
- 若反向推进突破早盘起点并有强跟进，取消flag解释。

### TRENDS-C25-S03：反方向假突破陷阱

- 类型：失败突破反手策略。
- 依据，PDF p.455–456、459–460：异常tight range常在尾盘先以1–2根强bar向早盘趋势反方向突破，随后失败并朝原趋势突破。
- Setup：S01 tight consolidation；late window首次breakout方向与morning trend相反。
- 第一breakout不逆早盘趋势追入，等待 `1–3bars` 跟进。
- 失败：价格返回range，反向breakout bar无法获得跟进，或其breakout pullback被反向突破。
- 入场：失败bar的保护性stop处顺早盘趋势入场。
- 止损：假突破极值外。
- 目标：range另一侧、早盘极值、leg 1=leg 2。
- 若反向breakout有2–3根强跟进并守住回测，转S06，不机械反手。

### TRENDS-C25-S04：尾盘顺势 Breakout Pullback

- 类型：标准趋势恢复策略。
- 依据，PDF p.455–457：未能提前入场者通常可交易late breakout或breakout pullback；最终腿可能快速加速至收盘。
- Setup：中段range顺morning trend方向突破，breakout body≥ `0.5ATR` 或2bars净位移≥ `0.75ATR`。
- 入场A：强breakout close小仓；入场B：`1–5bars` 回测range边界的标准stop。
- 止损：回测极值/range内侧结构位。
- 目标：morning extreme、S05等幅、1R/2R、session close。
- 时间约束：剩余bars必须≥回测策略历史中位持有期；否则只用breakout close/收盘退出模型。
- 若breakout后立即进入新tight range，减少目标并按失败突破管理。

### TRENDS-C25-S05：Morning Leg = Late Leg 测量移动

- 类型：目标与止盈组件。
- 依据，PDF p.455、459–462：趋势恢复的第二腿常与早盘第一腿等长；spike本身也可提供测量目标。
- morning leg确认后冻结四种高度：open→extreme、spike open→close、spike low→high、结构起点→早盘极值。
- 从midday consolidation的反趋势极值或late breakout point投射 `0.75/1.0/1.25×H`。
- 优先用于顺势止盈和停止追价，不在没有反转结构时单独fade。
- 多定义同时保留；不得以最终收盘挑选最准确的高度或起点。

### TRENDS-C25-S06：反向 Breakout 成功的 Reversal-Day 分支

- 类型：反向趋势策略。
- 依据，PDF p.455–460：late breakout通常恢复旧趋势，但有时相反方向成功并回撤部分或全部早盘腿；任何最佳形态仍可能约40%走反。
- Setup：S03反向breakout后有2–3bars跟进，breakout pullback守住range，Always-In翻转。
- 入场：反向breakout pullback；若spike极强可先小仓close入场。
- 止损：回测极值/range另一侧。
- 目标：早盘腿50%、session open、早盘起点、1R/2R。
- 翻转后不得继续持有“趋势恢复”仓位；平仓与反手分别记录。
- 原文40%是风险提醒而非固定条件概率，需按信号强度重估。

### TRENDS-C25-S07：跨日 Trend Resumption

- 类型：多session延续策略。
- 依据，PDF p.457、462：中段range可跨两天以上；在高周期只是ABC，突破仍通常沿原趋势，并可在数日后形成第二腿。
- Setup：过去 `1–5sessions` 存在强方向腿，之后range未强势突破其起点，日内/60分钟趋势状态未翻转。
- 所有高周期特征必须等bar/session收盘后生效；基础周期保存range边界。
- 入场：range顺原趋势breakout后的首次pullback，不直接假设跨日gap成交。
- 止损：跨日range对侧或回测结构外；按隔夜gap风险缩仓。
- 目标：第一腿 `0.75/1/1.25×`、旧极值、1R/2R。
- 最大等待5sessions为`PROXY`；按资产持仓周期做敏感性测试。

### TRENDS-C25-N01：中段无聊不能作为停止监控依据

- 类型：`NEGATIVE`。
- 依据，PDF p.455–457：数小时quiet range会诱使交易者放弃，但最佳尾盘趋势可能正由此产生。
- 禁止因波动率低或连续无交易bars自动关闭策略；进入S01后必须监控到收盘或状态失效。
- 同时禁止在tight range中部过度交易；等待边缘或breakout事件。
- 形态名称不能覆盖反向证据：S06条件满足必须允许与预期相反的趋势。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 455–457 | 核心特征、反向假突破、flag与尾盘恢复 | 第1节、S01–S04、N01 |
| 457 | breakout pullback、跨日ABC与多日恢复 | S04、S07 |
| 458 | gap测试、tight range及微趋势线失败入场 | S02 |
| 459–460 | 完美bear setup失败、约40%反向结果与测量移动 | S03、S05、S06 |
| 461–462 | 弱trend resumption与数日后第二腿 | S05、S07 |

## 4. 回测验收

- 状态序列按确认时点记录；不得以“最终确实恢复”筛选中段range。
- S01分别测试tight range与低动能逆向channel，报告候选频率和确认延迟。
- S03统计反向late breakout在1/2/3/5bars内失败或成功的条件概率。
- S04配对比较breakout close与pullback entry，包括尾盘无回测的漏单。
- S05从morning leg完成时冻结高度，从consolidation完成时冻结投射基点。
- S06与S03共用事件ID并保持终态互斥。
- S07包含隔夜gap、交易成本和未成交情形，高周期bar不得前视。
- Figure 25.1–25.4仅作章节例证，不作参数拟合或绩效证据。
