# 第 10 章：其他磁体价位

## 元数据

- 英文来源：`books/trading-price-action-trading-ranges/en/chapters/18-ch10-other-magnets.md`
- PDF 页码：219–221
- 图表：Figure 10.1；正文与图注已完整说明，未额外查看图片
- 状态：量化研究规格，未经回测
- 公共定义：[统一量化约定](../../../../quant/conventions.md)

## 1. Magnet Registry

统一登记以下价位及其`known_at`：

- trend/trend-channel lines、leg1=leg2与其他measured moves；
- spike-and-channel起点、breakout point、各种gap；
- 昨日及高周期OHLC、近期swings、EMA；
- 早先trading range的上下边界/中点、tight range、barbwire、final flag；
- signal/entry bar stops、理论entry/breakeven、巨大trend bar另一端；
- 预定义scalp/swing targets、结构stop的1R、round numbers。

每条记录包含`source_type`、方向、价格/动态线、有效起止时间、是否已测试。相距 `0.10–0.30ATR` 的不同来源聚为zone；同一几何事实不重复计票。

## 2. 规则卡

### RANGES-C10-S01：顺趋势向 Magnet 持仓

- 类型：目标/持仓策略。
- 依据，PDF p.219：市场朝magnet趋势移动时，应保持顺势，直到测试且最好略微overshoot。
- Setup：Always-In方向与最近未测试magnet一致，距离 `0.5–3ATR`，中间无更近反向结构。
- 新入场必须来自pullback/breakout setup；magnet自身只提供目标。
- 顺势仓位持有到zone前 `1tick–0.10ATR`，比较预先止盈、触价止盈和overshoot trail。
- 到达后减仓；若强穿越并有follow-through，关闭该magnet并启用下一目标。
- 剩余空间不足 `0.5–1R` 时不新开仓。

### RANGES-C10-S02：Countertrend Magnet 门控

- 类型：条件反转策略。
- 依据，PDF p.219：不能只因到达magnet逆势；必须已有反向强度，如trend-line break，或该move是高周期趋势中的pullback。
- 最低条件：magnet测试 + 主要trend-line break/反向spike + strong signal或第二入场。
- 高周期pullback例外必须由已完成高周期bar确认方向。
- 入场：反向signal外stop。
- 止损：magnet overshoot最终极值外。
- 目标：最近swing、EMA、range中点、1R/2R。
- 无反向证据时只止盈，不fade。

### RANGES-C10-S03：多 Magnet Confluence 排序

- 类型：目标评分组件。
- 依据，PDF p.219–220：多类技术价位都可能吸引测试；靠近的独立目标比孤立目标更值得监控。
- 每个zone评分：独立来源数、距价格、是否顺当前动量、时间新鲜度、是否来自高周期。
- 推荐权重只作`PROXY`：来源数40%、距离25%、方向20%、新鲜度10%、高周期5%。
- 动态线每bar更新，但历史决策使用当时版本；水平价位形成后冻结。
- 同源衍生（如同一range的height与midpoint投射）不得伪装为多个独立来源。
- 输出排名前3个zone，不同时假设所有目标必达。

### RANGES-C10-S04：巨大 Trend Bar Stop-Run Reversal

- 类型：失败回测策略。
- 依据，PDF p.220–221：巨大trend bar后的交易者常把stop放在其另一端；市场有时穿越该端触发stop，再恢复bar原方向。
- Setup：bar range≥ `1.5–2.5ATR`、body/range≥0.70、尾部小；后续pullback朝bar另一端。
- 不预判必然触及；只有价格进入极值 `0.10–0.30ATR` 内才启用。
- 触发：穿越极值 `1tick–0.15ATR` 后收回，并形成bar原方向reversal。
- 入场：reversal bar外stop。
- 止损：stop-run最终极值外。
- 目标：巨大bar中点/另一端、1R/2R。
- 若强穿越且有follow-through，取消反转；该bar成为failed breakout/exhaustion候选。

### RANGES-C10-S05：常见 Profit Target 与 1R Magnet

- 类型：资产特定目标组件。
- 依据，PDF p.220：常见scalp/swing目标及与required stop等距的1R会吸引止盈订单。
- 不硬编码书中旧资产点数；从过去 `50–250` 笔/日的MFE、tick size和波动分布估计常见聚集目标。
- 固定候选：`0.5R/1R/2R`、`0.25/0.5/1ATR`及市场最小常见tick倍数。
- 仅用训练窗口识别目标峰值，验证期冻结。
- 与结构magnet重合时提高止盈优先级；不因1R存在改变结构stop。

### RANGES-C10-S06：Round-Number Magnet

- 类型：心理价位目标组件。
- 依据，PDF p.220：股票百位、指数千位等round numbers常被测试并可能overshoot后pullback。
- 自动生成与价格尺度匹配的 `1/2/5 × 10^k` 网格，选择最近 `0.5–3ATR` 的上/下层。
- 用历史成交密度/转折率选择有效粒度，避免任意整数都成为magnet。
- 顺趋势持有至round number，并测试overshoot `0.1–0.5ATR` 后止盈。
- 反转仍需S02门槛；“通常到105/110”仅作待验证例子，不硬编码百分比。

### RANGES-C10-N01：Magnet 不是价格保证

- 类型：`NEGATIVE`。
- 依据，PDF p.219–221：这些价位只是倾向被测试；巨大bar stop也并非总被立即触发。
- Registry中的目标不得扩大stop、逆Always-In摊平或删除未到达样本。
- 所有magnet使用固定观察窗或生存分析，保留右删失。
- 目标命中后若无反转结构，不得把pause自动标成成功逆势交易。

## 3. 原文覆盖表

| PDF | 主张 | 映射 |
|---:|---|---|
| 219–220 | magnet完整清单、顺势持有与逆势门槛 | 第1节、S01–S03、S05–S06 |
| 220–221 | 巨大trend bar另一端的stop magnet与恢复 | S04、N01 |

## 4. 回测验收

- 每条magnet保存来源与`known_at`；动态线不得用未来anchor重画。
- S01报告按距离、来源和趋势强度的首次测试概率/时间。
- S02比较有/无prior countertrend strength，验证门控增量。
- S03做来源消融和去重审计。
- S04包含未触及巨大bar另一端、强穿越和stop-run恢复三类样本。
- S05/S06只在滚动训练期估计粒度，验证期冻结。
- Figure 10.1仅作章节例证，不作参数拟合或绩效证据。
