# 二次审计 — Trading Price Action REVERSALS

**日期：** 2026-07-23  
**ID：** `trading-price-action-reversals`

## 完整性
- EN/ZH 章节：38/38 一一对应
- 篇幅：各章 ZH/EN 量级相当，无空壳
- 源 PDF：535 页，经 wslpath 从 Downloads 复制

## 术语
- 继承系列术语表；补充主要趋势反转、最后旗形、高潮反转、扩散三角形等
- 统一：震荡区间、突破、回撤、信号K线、始终持仓、反转

## 图片
- 约 177 张 fig_*.webp（pyvips 压缩约 3.7MB）
- EN/ZH 注入图引用

## 结论
通过；已注册 catalog 层级目录。


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
