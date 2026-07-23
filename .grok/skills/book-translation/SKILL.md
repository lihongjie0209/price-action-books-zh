---
name: book-translation
description: >
  Translate trading/technical books (especially Al Brooks price-action series)
  from PDF into chapter Markdown with a living glossary, secondary audit, figure
  extraction, and registration into the price-action-books-zh bilingual reader.
  Use when the user says translate a book/PDF, add another Brooks book, 翻译图书,
  术语表, 二次审计, EN-ZH bilingual site, or runs /book-translation.
---

# Book Translation Skill（图书翻译流水线）

面向本仓库 `price-action-books-zh`（及同结构多书项目）的 **PDF → 分章 Markdown → 简体中文 → 术语统一 → 二次审计 → 图片 → 对照站** 全流程。

## 何时启用

- 用户提供新 PDF（如 Trading Ranges / Reversals）要求翻译  
- 要求建立/更新术语表、做全书审计润色  
- 要求把书挂到 GitHub Pages 中英对照阅读  

## 目录约定（每本书）

在仓库根下：

```text
books/<book-id>/
  en/chapters/*.md      # 英文章节（TOC 边界拆分）
  zh/chapters/*.md      # 中文同名文件
  glossary/glossary.md  # 术语表：English | 首选译名 | 备注
  assets/figures/       # fig_X_Y.png 等，中英共用
  notes/
    conversion_notes.md
    chapter_inventory.md
    audit_record.md
    images_notes.md
    TRANSLATION_GUIDE.md
  scripts/              # 可选：extract / inject / verify
```

`book-id` 使用小写短横线，例如 `trading-price-action-trends`。

根目录 `catalog.json` 的 `books[]` 必须登记新书，站点才能显示。

## 阶段 0 — 立项

1. 确认源 PDF 路径与页数；**只译用户点名的书**，不擅自开多本。  
2. 创建 `books/<book-id>/` 目录树。  
3. 工具：优先 **PyMuPDF** 抽 PDF 文本与图；`pandoc` 适合 docx/html，**不要**指望 pandoc 直接读 PDF。  
4. 复制或延伸本系列既有 `glossary`（Brooks 术语保持跨书一致）。

## 阶段 1 — 抽取与分章

1. 用 PDF outline/`get_toc` 或 Contents 页确定章节边界（**禁止**随意按固定页数切）。  
2. 输出 `en/chapters/NN-slug.md`，保留 `<!-- PDF page N -->` 便于回溯。  
3. 记录 `notes/conversion_notes.md`（工具版本、空页/纯图页、抽取缺陷）。  
4. 写 `notes/chapter_inventory.md`（文件名、页码范围、字符数）。

成功标准：早/中/晚抽样章节有实质英文正文，非空壳。

## 阶段 2 — 术语表（翻译前就要有）

1. 维护 `glossary/glossary.md` 表格：`English | 首选译名 | 备注`。  
2. **先写入再使用**；禁止同一书内多译名并存。  
3. Brooks 核心首选（跨书锁定，除非用户改）：  

| English | 首选译名 |
|---------|----------|
| price action | 价格行为 |
| bar | K线 |
| trading range | 震荡区间 |
| breakout | 突破 |
| pullback | 回撤 |
| signal bar | 信号K线 |
| entry bar | 入场K线 |
| trend bar | 趋势K线 |
| always-in | 始终持仓 / Always-In |
| channel | 通道 |
| spike and channel | 尖峰与通道 |
| measured move | 等幅运动 |
| doji | 十字星 |
| High 1 / Low 2 等 | 保留英文编号 |

4. 专名、软件、合约代码、URL 保留英文。  
5. 若系列已有书，**先合并旧术语表**再译新书。

## 阶段 3 — 逐章翻译

1. **一章一文件**，输出 `zh/chapters/<与 en 同名>.md`。  
2. 通顺简体中文完整句子；保留标题层级、列表、页注释、图题（Figure → 图）。  
3. 大章可 `en/chunks/*.partNN.md` 分块译后合并，禁止留下 `MERGE_MARK` 半成品。  
4. 禁止标题-only 空壳；篇幅与 EN 同量级（UTF-8 字节通常 ≳ EN 的 35–40%）。  
5. 翻译中新出现的稳定术语：**先改 glossary，再继续译**。

## 阶段 4 — 图片（可选但推荐）

1. `extract_images.py`：导出嵌入图 + 纯图页渲染；`fig_X_Y.png` 与书中 Figure 对齐。  
2. `inject_figure_refs.py`：在 Figure/图 标题后插入  
   `![…](../../assets/figures/fig_X_Y.png)`（相对 `en|zh/chapters`）。  
3. 仓库可只提交 `fig_*.png`（体积小）；`page*.png` 可 gitignore。  
4. 记录 `notes/images_notes.md`。

## 阶段 5 — 二次审计（全书译完后必须做）

写 `notes/audit_record.md`，至少执行：

1. **完整性**：每个 en 文件有对应 zh；无缺失/过薄章。  
2. **术语 grep**：首选译名多章命中；冲突译法（如「交易区间」「回调」「信号柱」）清零或统一。  
3. **残留英文**：去掉正文中 PDF 运行页眉（ALL-CAPS 与 **Title Case 多行** 章题）；保留 `<!-- English: … -->` 注释即可。  
4. **润色**：明显机翻碎句、不通顺长句。  
5. **图片链接**：引用文件存在。  
6. 跑 `scripts/verify_translation_pipeline.py`（若该书有）须 PASS。

## 阶段 6 — 注册对照站

1. 更新根目录 `catalog.json`：  
   - `id`, `title_en`, `title_zh`, `author`, `path`, `chapters[]`（`id/file/title_en/title_zh`）, `glossary`, `figure_count`  
2. 本地 `python3 -m http.server` 打开 `reader.html?book=<id>` 抽查对照与出图。  
3. 提交推送；GitHub Pages 从仓库根目录提供静态站。

## 阶段 7 — Git 提交建议

```text
books/<id>: add EN extract, ZH translation, glossary, audit, figures
catalog: register <id>
```

不要提交 `.venv/`、巨型 `page*.png` 全集、PDF 原书二进制（除非用户明确要求）。

## 质量红线

- 不缩成「试译几章」却声称完成（除非用户只要样章）。  
- 不把 Skill 或脚本当成译文的唯一存放处。  
- 不擅自重新制图冒充原图；缺图在 notes 标明。  
- 尊重版权：学习用途说明写在 README。

## 本仓库参考实现

- 书：`books/trading-price-action-trends/`  
- 站：`index.html`, `reader.html`, `js/app.js`  
- 术语：`books/trading-price-action-trends/glossary/glossary.md`  
- 审计范例：`books/trading-price-action-trends/notes/audit_record.md`  

## 检查清单（复制到 PR/提交说明）

- [ ] `books/<id>/en/chapters` 与 `zh/chapters` 一一对应  
- [ ] `glossary/glossary.md` 已更新且全书统一  
- [ ] `notes/audit_record.md` 已写且问题已处理  
- [ ] 图片 `fig_*.png` + MD 引用（如有）  
- [ ] `catalog.json` 已登记  
- [ ] 本地 http 站中英对照可打开  
