# 二次审计记录 — Trading Price Action TRADING RANGES

**日期：** 2026-07-23  
**书目 ID：** `trading-price-action-trading-ranges`

## 完整性
- EN 章节单元：46
- ZH 章节单元：46（一一对应）
- 篇幅：各章 ZH/EN 字节比约 0.75–1.1；无标题空壳
- 中文主导：正文汉字比例多数 >0.75（术语表/索引除外）

## 术语
- 继承 TRENDS 系列术语表并补充 Ranges 专用词（磁铁、窄幅震荡、交易者公式、方向概率等）
- 首选译名：震荡区间 / 突破 / 回撤 / 信号K线 / 始终持仓 / 等幅运动 / 缺口

## 润色
- 剥离常见 PDF 运行页眉（PRICE ACTION、PART/CHAPTER 装饰行、FIGURE 等）
- 图注统一为「图 x.x」，并注入 WebP 图引用

## 图片
- 从 PDF 映射 Figure 标签 → `assets/figures/fig_*.webp`（约 152 张，pyvips 压缩）
- EN/ZH 各约 155 处图片引用

## 结论
通过二次审计，可挂载对照站阅读。


## 2026-07-23 段落与插图审计（全三书统一 pass）

**范围：** `zh/chapters` 句中错误分段（含 `<!-- PDF page N -->` 空白段切分）+ 图引用完整性 + 疑似整页文字截图重绑。

### 句中分段
- 工具：`scripts/audit_zh_chapters.py`（`detect` / `fix`）
- 规则：上一 prose 块未以句末标点（。！？…」』》）等）结束，且下一块为续写时，合并为一段；页标记改为行内 `<!-- PDF page N -->` 保留可追溯性。
- 结果：TRENDS / RANGES / REVERSALS 三本 `mid_breaks=0`（修复前合计约 1144 处）。
- 回归：`scripts/test_audit_zh_chapters.py` 覆盖 detect/fix/真实章节/图引用。

### 插图
- Markdown `![...](...)` 解析目标文件：**missing=0**（三本合计）。
- RANGES `13-ch06-gaps.md`：补注入图 6.1–6.5 与 图 18.4 的 WebP 引用（资产已有、MD 此前缺失）。
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
