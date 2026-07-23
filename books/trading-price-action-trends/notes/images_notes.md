# 图片资源说明

## 目录
- `assets/figures/` — 从 PDF 抽取的图表 PNG（中英共用）
- `assets/figures_manifest.json` — 页码 / Figure 编号 / 文件映射

## 抽取方式
- 工具：PyMuPDF（`scripts/extract_images.py`）
- 嵌入图：按页导出足够大的 pixmap（过滤小装饰图）
- 纯图/空白页：整页 1.5x 渲染为 `pageNNN_fullpage.png`
- 命名：
  - `page087.png` — 该页主图别名
  - `fig_1_1.png` — 按书中 Figure 1.1 稳定命名（中英 MD 引用此路径）

## Markdown 引用
从 `en/chapters/` 或 `zh/chapters/`：

```markdown
![Figure 1.1](../../assets/figures/fig_1_1.png)
![图 1.1](../../assets/figures/fig_1_1.png)
```

注入脚本：`scripts/inject_figure_refs.py`（在 Figure/图 标题后插入，已插入则跳过）

## 重跑
```bash
cd trading-price-action-trends-zh
.venv/bin/python scripts/extract_images.py
# 若改进了映射，可再运行 inject（幂等，不重复插入）
.venv/bin/python scripts/inject_figure_refs.py
```

## 说明
- 全书约 121 个 Figure 标签已映射；EN/ZH 各约 121 处图片引用
- 部分页仅有讨论无独立嵌入图时，会使用邻页主图或 fullpage 渲染
- 原始 PDF 版权仍属作者/出版社；图片仅供本译本学习阅读配套使用
