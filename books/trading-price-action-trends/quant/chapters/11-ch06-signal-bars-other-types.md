# 第 6 章：信号 Bar——其他类型

## 元数据

- 英文来源：`books/trading-price-action-trends/en/chapters/11-ch06-signal-bars-other-types.md`
- PDF 页码：133–186
- 图表：Figure 6.1–6.19；正文逐图给出量化所需关系，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. 总体原则

本章列出的形态都不是脱离上下文的入场信号。同一形态在强趋势中可能是延续，在趋势末端可能是反转，在紧密区间中可能没有优势。

统一路由顺序：

```text
regime -> location -> trend maturity -> pattern -> trigger -> follow-through
```

若 `regime/location` 未确定，pattern 只能登记为候选，不得下单。

## 2. 规则卡

### TRENDS-C06-S01：强趋势 Bar 紧迫入场

- 类型：完整顺势策略。
- 依据，PDF p.133–134：spike 阶段的强趋势 bar 可在收盘买卖，或在其极值外 stop entry。
- Setup：重要位置突破；`body_frac≥0.60–0.80`、同向收盘位置≥`0.75–0.95`、range为历史70%–95%分位。
- 入场：比较 signal bar 收盘、下一bar极值外1 tick、首次回撤三种版本。
- 止损：signal bar另一端或spike起点；风险>2ATR时等待回撤。
- 目标：新极值、1R/2R、spike等幅。
- 失效：下一bar收回signal bar 60%以上且反向强收盘。

### TRENDS-C06-S02：二 Bar / 三 Bar 反转

- 类型：完整反转框架。
- 依据，PDF p.134–136、149–153：相反方向趋势 bars 构成反转；若第二bar与第一bar重叠约75%以上，触发应越过整个两bar区间。
- 两bar候选：相反方向趋势 bars，实体幅度比 `0.5–1.5`；允许中间间隔，但实时版本最多 `0–10 bars`。
- 三bar候选：第一与第三bar相反，中间为小bar/doji。
- 触发：越过整个组合的反转方向极值，不只越过最后一bar。
- 止损：整个组合另一端。
- 目标：1R/2R；与固定高周期收盘对齐时单独分层，但不跨周期寻找事后完美形态。
- 禁入：组合处于3根以上大幅重叠bars、区间中部或强趋势第一次逆势尝试。

| 参数 | 范围 | 基准 | 来源 |
|---|---:|---:|---|
| 两bar实体幅度比 | 0.5–1.5 | 0.67–1.33 | `PROXY` |
| 高重叠警示 | 60%–85% | 75% | `AUTHOR` 约75% |
| 非连续反转最大间隔 | 3–10 bars | 10 | `AUTHOR` 约10 bars |
| 触发缓冲 | 1–3 ticks或0.02–0.10ATR | 1 tick | `AUTHOR/PROXY` |

### TRENDS-C06-S03：Small / Inside / ii / iii / ioi 状态机

- 类型：压缩突破与末端旗形策略族。
- 定义：inside bar允许一端与prior bar相等；`ii/iii`为连续嵌套；`ioi`为inside-outside-inside。
- 顺势：强趋势回撤中的小bar只做顺势突破，signal body同向更佳。
- 区间：小bar只在大区间边缘fade；中部doji不交易。
- breakout mode：ioi或中性ii在可能突破位置放OCO双向stop，一侧成交后另一侧成为/接近保护止损；同bar双触发用最坏顺序。
- 末端旗形：趋势运行 `10+ bars`、已有趋势线破坏或高潮时，ii顺势突破只按scalp管理；失败后反向突破可做swing。
- 止损：ii/iii必须越过最外层组合另一端，而非只越过最后inside bar。
- 参数：小bar range分位10%–40%；嵌套容差0–1 tick；OCO有效期1–5bars，均为 `PROXY`。

### TRENDS-C06-S04：Micro Double Top/Bottom 上下文路由

- 类型：延续或反转策略。
- 定义：相邻或近相邻 highs/lows 差值≤`0–0.20 ATR`，间隔 `1–3 bars`。
- 强bear spike中的micro double bottom：若bear bar近低收盘后接bull bar近低开盘，视为one-bar bear flag，向下突破做空。
- 强bull spike中的micro double top：对称做多。
- 其他上下文：默认作为小型反转候选，必须结合第二次入场、水平位或趋势破坏。
- 止损：两bar组合另一端；目标1R/2R或spike新极值。
- 失效：三根以上大重叠bars时转为区间，不按micro double形态交易。

### TRENDS-C06-S05：反转 Bar 失败的顺势交易

- 类型：完整失败信号策略。
- 依据，PDF p.138、146、173–175：强趋势中反转bar错误一侧被突破，提前逆势者退出会增强原趋势。
- Setup：强趋势中出现逆势reversal bar，但没有触发反转，或触发后1–2bars迅速失败。
- 入场：突破reversal bar的原趋势方向极值；若为两bar结构则突破整个结构。
- 止损：失败结构另一侧。
- 目标：趋势新极值、1R/2R、spike-channel目标。
- 禁入：趋势已成熟且同时存在高潮、通道过冲、测量目标和第三推进；此时失败信号可能是真反转前兆。

### TRENDS-C06-S06：Shaved Bar 仅在强趋势启用

- 类型：顺势信号及负向过滤器。
- 依据，PDF p.138、142、166–167、184–185：无影线只在runaway趋势中代表强度；区间/低量环境的成簇shaved bars没有意义。
- bull：强bull趋势中shaved top优先于仅shaved bottom；bear对称。
- Setup：趋势分数≥0.70–0.85，bar `body_frac≥0.60`，同方向一端影线≤1tick或≤0.02ATR。
- 入场：顺势极值外stop、收盘或1–2tick回撤。
- 止损：bar另一端；目标1R/2R。
- 禁用：最近一小时/`12–30 bars` 出现≥3个双向shaved bars且regime=range。

### TRENDS-C06-S07：异常大趋势 Bar 衰竭

- 类型：严格反转策略。
- 依据：PDF p.147称运行10+bars后的异常大趋势bar通常至少修正10bars；p.161–163说明连续高潮后可交易强两bar反转。
- 上下文：趋势年龄 `AUTHOR≥10 bars`；range处于滚动85%–99%分位；预定义支撑/阻力、通道过冲或测量目标至少一项。
- 触发：强两bar反转、inside反向趋势bar突破，或第二次反转信号。
- 止损：高潮极值外。
- 目标：EMA、至少10bars、两腿、channel起点、1R/2R分别统计。
- 失效：异常bar后仍有强同向跟进；高潮不自动等于反转。
- 分层：第一次、第二次、第三次连续高潮；作者认为第二/第三次后修正概率上升，必须作为待验证假设。

### TRENDS-C06-S08：20 Gap Bar 均线回归后顺势恢复

- 类型：完整顺势回撤策略。
- 依据，PDF p.139、144–145：强趋势中约20bars未触及EMA，首次轻微穿越后可顺势入场。
- Setup：bull版本过去 `15–30 bars` lows均在上升EMA上方；价格横向回到EMA，首根小bear bar仅低于EMA `0–0.15ATR`。bear对称。
- 入场：signal bar收盘或顺势极值外stop；强反向spike时等待第二信号。
- 止损：回撤极值；目标原趋势极值、1R/2R。
- 失效：EMA趋平、价格多次穿越，或反向突破有跟进。

### TRENDS-C06-S09：Channel Bar 订单框架

- 类型：订单研究。
- 依据，PDF p.139：强channel中顺势方在prior bar不利极值附近limit，双方也在边缘放突破/逆势订单。
- 窄强channel：只允许顺势stop和顺势pullback limit；不做第一次逆势。
- 宽channel：在边缘分别测试顺势回撤和逆势scalp；中部不交易。
- limit成交必须测试“触及即成交”和排队折损；最多2腿、总风险固定。
- channel分类参数：宽度 `1–6ATR`、年龄 `10–100bars`、边界距离 `0.05–0.30ATR`，均为 `PROXY`。

### TRENDS-C06-N01：混乱小 Doji 与复杂反手禁入

- 类型：`NEGATIVE`。
- 依据，PDF p.140、142、148：中部、平EMA附近的小doji及复杂双向反手令人困惑且失败率高；E-mini约10–11 PST只是特定示例。
- 禁入：regime=range、距EMA≤0.15ATR、距区间中点≤0.25区间宽度、无第二信号。
- 跨市场只使用session比例与统计基率，不照搬固定PST钟点。
- 若OCO/反手逻辑无法在回测中保守确定成交顺序，则该交易标记为不可检验。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 133–134 | 强趋势bar紧迫入场；弱pullback signal在强趋势仍有效 | S01、沿用第4章S03 |
| 134–136 | 两/三bar反转及约75%重叠时的整个结构触发 | S02 |
| 137–142 | inside、ii/iii、ioi、小bar、final flag | S03 |
| 138、159–160 | micro double top/bottom按spike上下文可为延续 | S04 |
| 138、146、173–175 | reversal bar failure成为顺势陷阱交易 | S05 |
| 138、142、166–167、184 | shaved bar只在强趋势有意义 | S06 |
| 139、144–145 | 约20 gap bars后的EMA测试 | S08 |
| 139–140 | channel中各类stop/limit订单与小bar上下文 | S09 |
| 142、147–148、161–163 | 异常大bar及连续高潮后的修正 | S07 |
| 149–153 | 高周期反转可由固定低周期组合表达 | S02；禁止跨图挑选 |
| 154–158 | 首小时反转、ii、tiny bar仍需位置和第二信号 | S03、S04 |
| 168–172、176–183 | 多种signal示例反复强调regime、位置、动量 | 全部规则的上层路由 |
| 140、142、148、184–185 | 中部doji、紧密区间和低量shaved bars应避开 | N01、S06 |

## 4. 回测验收

- 每种形态按 trend/range、顺势/逆势、区间位置、趋势年龄分层；不得汇总成一个胜率。
- S02直接比较“最后bar极值触发”与“整个组合极值触发”的陷阱率和成交损失。
- S03分别统计inside、ii、iii、ioi；OCO使用最不利同bar成交顺序。
- S04验证完全相同的micro double形态在spike与非spike上下文中方向是否相反。
- S07单独检验作者的10+bars、修正10+bars、两腿以及连续高潮主张。
- 所有高周期确认只能在高周期收盘后生效；所有limit订单计入排队、滑点和未成交。
- 19张图只作为原文章节例证，不作为拟合或绩效证据。
