# 二次审计与润色记录

**项目：** Trading Price Action TRENDS（Al Brooks）中文译本  
**目录：** `/root/book/trading-price-action-trends-zh/`  
**审计日期：** 2026-07-23  

## 审计范围

1. **完整性：** 37 个 EN 章节单元均有对应 `zh/chapters/*.md`，无一空壳标题文件。  
2. **篇幅：** 各章 ZH 与 EN 字节量同量级（多数 ZH 为 EN 的 70%–100% UTF-8 字节；中文密度更高）。  
3. **页标记：** 各章 `<!-- PDF page N -->` 与 EN 源对齐（图页无正文者保留 figure-only 注释）。  
4. **术语表：** `glossary/glossary.md` 覆盖核心价格行为术语；跨章检索首选译名。  
5. **残留英文：** 扫描正文中成段英文、FIGURE/CHAPTER 装饰标题、「Deeper Discussion」等，并润色。  
6. **冲突译法：** 检索「交易区间 / 信号柱 / 回调 / 测量运动」等非首选译法。  

## 完整性结论

| 项目 | 结果 |
|------|------|
| EN 章节数 | 37 |
| ZH 章节数 | 37 |
| 缺失章 | 无 |
| 明显过薄章 | 无（`36-about-the-website` 因 URL 专名英文比例高，属预期） |
| 图文不可提取页 | 约 27 页（conversion_notes 记录），仅占位注释，不阻塞正文翻译 |

## 术语一致性结论

跨 `zh/chapters` 首选译名命中（审计时点抽样）：

| 首选译名 | 出现文件数（约） | 总命中（约） |
|----------|------------------|--------------|
| 震荡区间 | 29/37 | 600+ |
| 突破 | 34/37 | 1300+ |
| 回撤 | 31/37 | 1000+ |
| 信号K线 | 21/37 | 230+ |
| 趋势K线 | 26/37 | 500+ |
| 始终持仓 | 12/37 | 20+ |
| 微型通道 | 9/37 | 100+ |
| 尖峰与通道 | 17/37 | 130+ |
| 等幅运动 | 19/37 | 130+ |
| 开盘即趋势 | 22/37 | 100+ |

**冲突项处理：**

| 检查项 | 结果 | 处理 |
|--------|------|------|
| 交易区间 | 0 | 无需 |
| 信号柱/信号棒 | 0 | 无需 |
| 测量运动 | 0 | 无需 |
| 回调（应作回撤） | 3 文件 6 处 | 已统一改为「回撤」 |
| FIGURE x.y 英文残留 | 4 文件 | 已改为「图 x.y」 |
| CHAPTER 装饰标题残留 | 若干 | 已剥离 |
| Deeper Discussion… | 0 残留 | 译为「对本图的更深入讨论」 |

## 润色动作摘要

1. 全书 `回调`→`回撤`（pullback 语境）。  
2. `FIGURE n.n`→`图 n.n`。  
3. 剥离 PDF 抽出的 `C H A P T E R` / `CHAPTER N` 英文装饰行。  
4. 运行标题类残留（如 PRICE ACTION、COMMON TREND PATTERNS）改为中文。  
5. 专名（Al Brooks、Emini、TradeStation、合约代码、URL）与 Brooks 编号（High 1/2、Low 1/2、Always-In、ii/iii）按术语表保留。  

## 二次修复（skeptic 复查）

1. **导论截断**：`zh/chapters/04-introduction.md` 曾停在 `<!-- MERGE_MARK -->`（约 19KB）。已从 `zh/chunks/04-introduction.part01–08.md` 完整重合并为约 **75KB**，34 个 PDF 页标记与 EN 对齐，文末内容与 EN 导论结尾一致。  
2. **运行页眉**：对全部 `zh/chapters/*.md` 剥离残留英文 PDF 运行标题（如 `SIGNAL BARS: OTHER TYPES`、`REVERSAL DAY`、`TREND RESUMPTION DAY`、`STAIRS:…`、`P A R T III` 等）。复查时 ALL-CAPS 运行标题命中为 0。  
3. **校验**：`scripts/verify_translation_pipeline.py` 在修复后重新运行为 **PASS**；`{SCRATCH}/verify_run.txt` 与 `chapter_inventory.txt` 已刷新。  

## 三次修复（Title Case 多行页眉）

1. **问题**：`polish_zh_chapters.py` 原只匹配 ALL-CAPS 单行；漏掉 Title Case 多行 PDF 章题，如  
   - `09-ch04`: `Bar Basics:` / `Signal Bars,` / `Entry Bars,` / `Setups, and` / `Candle Patterns`  
   - `33-ch25`: `Trend` / `Resumption Day`  
   - `34-ch26`: `Stairs: Broad` / `Channel Trend`  
2. **处理**：从正文剥离上述多行标题（保留 HTML 注释中的英文原题）；扩展 `scripts/polish_zh_chapters.py` 支持已知多行 Title Case 序列 + 页标记后 Title Case 行；`verify_translation_pipeline.py` 增加上述片段的回归断言。  
3. **结果**：正文中无残留（仅 `<!-- English: CHAPTER … -->` 注释保留）；`verify` **PASS**。  


## 抽取限制（非翻译缺陷）

- 源 PDF 约 27 页无文本层（多为纯图），见 `notes/conversion_notes.md`。  
- 连字符断词、页眉页码噪声已在抽取脚本中启发式清理，残留不影响通读。  
- 未重绘图表；图题与环绕正文已译。  

## 验收清单执行情况

- [x] 专用目录含 EN / ZH / glossary / notes  
- [x] PDF→Markdown 抽取与按 TOC 分章  
- [x] 全书 37 单元简体中文译本  
- [x] 术语表建立并在翻译与审计中统一  
- [x] 二次审计记录（本文件）  

## 结论

二次审计通过：章节齐全、术语一致、主要残留英文标题与「回调」冲突已修复。译本达到「可通读的忠实简体中文 Markdown」目标，非商业出版级排版校订。


## 2026-07-23 段落与插图审计（全三书统一 pass）

**范围：** `zh/chapters` 句中错误分段（含 `<!-- PDF page N -->` 空白段切分）+ 图引用完整性 + 疑似整页文字截图重绑。

### 句中分段
- 工具：`scripts/audit_zh_chapters.py`（`detect` / `fix`）
- 规则：上一 prose 块未以句末标点（。！？…」』》）等）结束，且下一块为续写时，合并为一段；页标记改为行内 `<!-- PDF page N -->` 保留可追溯性。
- 结果：TRENDS / RANGES / REVERSALS 三本 `mid_breaks=0`（修复前合计约 1144 处）。
- 回归：`scripts/test_audit_zh_chapters.py` 覆盖 detect/fix/真实章节/图引用。

### 插图
- Markdown `![...](...)` 解析目标文件：**missing=0**（三本合计）。
- RANGES `13-ch06-gaps.md`：补注入图 6.1–6.5 与 图 18.4 的 PNG 引用（资产已有、MD 此前缺失）。
- REVERSALS：重绑疑似整页文字截图为嵌入式图表（landscape）：`fig_4_14`、`fig_5_6`、`fig_7_4`、`fig_20_2`、`fig_24_12`（自 PDF 嵌入图重抽）。
- REVERSALS：ZH「图 19.10」在 EN/PDF 无对应编号，已改为无图题散文；记为残留说明而非虚构插图。

### 残留
- 索引类章节中部分跨页词条列表本身无句号，合并后更连贯；未做全书文学润色。
- 未对全部 ~450 图做人工视觉审阅；自动化筛查后 portrait-textlike=0。
- 英文章节页标记分段未强制修改（非目标）。

### 命令复验
```bash
python3 scripts/audit_zh_chapters.py detect   # expect TOTAL mid_breaks=0
python3 scripts/audit_zh_chapters.py figures  # expect TOTAL missing_figure_refs=0
uv run python scripts/test_audit_zh_chapters.py
```
