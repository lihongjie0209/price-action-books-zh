# Al Brooks 价格行为量化约定

本文档是三本书全部章节策略规格的公共接口。章节文档只覆盖差异，不重复定义这些约定。

## 1. 数据与执行模型

- 基础输入为按时间排序的 `timestamp, open, high, low, close, volume`。若市场没有可靠成交量，所有以成交量为条件的策略必须关闭，不能用零值代替。
- 可选元数据为 `tick_size, session_id, session_open, session_close, previous_session_ohlc, contract_multiplier`。
- 下标 `t` 表示刚刚收盘的信号 bar。所有条件只能读取 `t` 及更早的数据；默认最早在 `t+1` 开盘成交。止损单突破入场可使用 `t` 的高低点，但只能在后续 bar 触发。
- 同一根 bar 同时触及止损和目标且没有更细粒度数据时，采用对策略最不利的成交顺序，并在结果中单独统计这种歧义 bar。
- 默认包含手续费、买卖价差和滑点。成本至少测试 `0、0.25、0.5、1.0 × median_spread` 四档。

## 2. 公共变量

```text
range(t)       = high(t) - low(t)
body(t)        = abs(close(t) - open(t))
body_frac(t)   = body(t) / max(range(t), tick_size)
close_pos(t)   = (close(t) - low(t)) / max(range(t), tick_size)
overlap(a,b)   = max(0, min(high(a),high(b))-max(low(a),low(b)))
                 / max(min(range(a),range(b)), tick_size)
TR(t)          = max(high-low, abs(high-close[-1]), abs(low-close[-1]))
ATR(n,t)       = Wilder moving average of TR over n completed bars
NATR_move(a,b) = (price(b)-price(a)) / ATR(n,b)
R              = entry price to initial protective-stop distance
session_pos    = elapsed tradable time / total tradable session time
```

默认 `ATR(20)`，敏感性网格为 `n ∈ {10,14,20,30,50}`。滚动分位数默认窗口 100 bars，搜索范围 50–250 bars。所有除法分母至少为一个 `tick_size`。

## 3. 形态代理

以下阈值不是作者声称的最优参数，而是将主观语言变成可证伪假设的统一起点。

| 概念 | 宽松 | 基准 | 严格 |
|---|---:|---:|---:|
| bull/bear trend bar：`body_frac` | 0.50 | 0.60 | 0.70 |
| 收盘靠近极值：bull `close_pos` / bear `1-close_pos` | 0.65 | 0.75 | 0.85 |
| 大 bar：range 的滚动分位 | 0.70 | 0.80 | 0.90 |
| 小 bar：range 的滚动分位 | 0.40 | 0.30 | 0.20 |
| 强重叠 | 0.50 | 0.65 | 0.80 |
| 有效突破距离 | 0.05 ATR | 0.10 ATR | 0.20 ATR |
| 突破跟进 | 后 3 bars 不收回 | 后 2 bars 同向收盘 | 下一 bar 同向趋势 bar |
| 紧密区间 | 8 bars 内 60% 重叠 | 10 bars 内 70% 重叠 | 12 bars 内 80% 重叠 |
| 局部摆动确认 | 左右各 1 bar | 左右各 2 bars | 左右各 3–5 bars |
| 等高/等低容差 | 0.25 ATR | 0.15 ATR | 0.08 ATR |
| 两段幅度相似 | 0.50–1.50 | 0.67–1.33 | 0.80–1.20 |
| 高成交量 | 70% 分位 | 85% 分位 | 95% 分位 |

趋势状态默认以最近 20 bars 的线性回归斜率除以 ATR 表示，并同时检查价格相对 EMA(20) 的位置。阈值必须在训练样本内估计，禁止使用全样本分位数。

## 4. 订单、仓位与退出

- `stop entry`：多头为信号 bar 高点加 1 tick，空头为低点减 1 tick；若次 bar 跳空越过触发价，按实际可成交价计入滑点。
- `limit entry`：只有后续价格真实触及限价才算成交；触及即成交与排队折损两种模型都要测试。
- 初始止损默认放在形态失效点外 1 tick。若距离大于 2 ATR，策略跳过或按固定账户风险缩小仓位，不得任意收紧至失去结构意义。
- 每笔账户风险默认 0.25%，测试 0.10%–1.00%；仓位为 `floor(account_risk / (R × contract_multiplier))`。
- 通用目标网格为 `0.5R、1R、1.5R、2R、3R`；章节另有测量移动或磁体目标时优先使用章节目标。
- 超时退出默认 20 bars，测试 5–50 bars；日内策略默认不隔夜，除非章节明确研究隔夜市场。
- 加减仓必须分别记录每一腿成交和风险；任何时点总最坏情形风险不得超过初始账户风险上限。

## 5. 参数来源和状态

- `AUTHOR`：英文原文明确给出。保留作者单位，同时给出可迁移的 ATR、bar 数或 session 比例表达。
- `PROXY`：为主观描述设计的可计算代理。必须给出宽松、基准、严格三档，并解释代理可能失效之处。
- `EMPIRICAL`：只能由数据选择。只给搜索空间，使用滚动或 walk-forward 训练选择，不能把全样本最优值写成默认值。
- `NEGATIVE`：作者明确认为亏损、低概率或仅适合专家的做法。作为禁入过滤器或反事实基线测试，不包装为推荐策略。

## 6. 回测与验收协议

每个策略至少报告：信号数、成交数、胜率、平均盈利/亏损、期望值（R）、Profit Factor、最大回撤、MAE/MFE、持仓 bars、换手率和成本敏感性。

- 时间序列按训练/验证/测试顺序切分，或使用 anchored walk-forward；不得随机打乱。
- 至少按趋势/区间、高/低波动、交易时段位置和多空方向分层。
- 少于 200 笔样本时只报告探索性结果，不下稳定性结论。
- 比较宽松/基准/严格参数，以及相邻网格；只有孤立参数点盈利视为过拟合警报。
- 章节中的概率和盈利描述是待验证假设，不是回测结果或实盘承诺。
