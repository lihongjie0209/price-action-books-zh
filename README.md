# Brooks 价格行为译丛（price-action-books-zh）

Al Brooks 价格行为系列图书的**简体中文**开源翻译仓库，支持：

- 按书分目录管理（可继续添加 Reversals、Trading Ranges 等）
- 统一**术语表**与**二次审计**流程（见下方 Skill）
- **GitHub Pages 中英对照阅读**

## 在线阅读

- GitBook 风格：左侧**分层目录**（前言 / 各部分 / 附录）
- **默认中文**；右上角可按需开启「英文对照」
- Tailwind CSS 构建 UI

## 在线阅读

部署后地址（启用 Pages 后）：

**https://lihongjie0209.github.io/price-action-books-zh/**

本地预览：

```bash
cd price-action-books-zh
python3 -m http.server 8080
# 打开 http://127.0.0.1:8080/
```

## 仓库结构

```text
price-action-books-zh/
├── index.html / reader.html   # GitHub Pages 阅读站
├── css/ js/ catalog.json
├── books/
│   └── trading-price-action-trends/   # 第一本：TRENDS
│       ├── en/chapters/               # 英文 Markdown（按章）
│       ├── zh/chapters/               # 中文译本
│       ├── glossary/glossary.md       # 术语表
│       ├── assets/figures/            # 共享图（fig_*.png）
│       ├── notes/                     # 抽取/审计记录
│       └── scripts/                   # 可选工具脚本
└── .grok/skills/book-translation/     # 图书翻译 Skill
```

## 当前书目

| ID | 书名 | 状态 |
|----|------|------|
| `trading-price-action-trends` | Trading Price Action TRENDS | 已译 + 对照站 |

## 添加下一本书

1. 按 Skill 流程：`/book-translation` 或说明「翻译某某 PDF」
2. 在 `books/<book-id>/` 建立与 TRENDS 相同的布局
3. 更新根目录 `catalog.json` 的 `books` 数组
4. 提交并推送，Pages 自动更新

## 翻译 Skill

路径：[`.grok/skills/book-translation/SKILL.md`](.grok/skills/book-translation/SKILL.md)

覆盖：PDF→Markdown、分章、术语表、逐章翻译、二次审计与润色、图片抽取、对照站注册。

## 版权声明

原书 © Al Brooks / John Wiley & Sons。本仓库译本与图示提取**仅供学习交流**，请勿用于商业出版或再分发原书扫描件。请支持正版纸质书/电子书。

## License（译本编排）

仓库内原创编排脚本、站点代码与 Skill 文档采用 MIT（见 `LICENSE`）。译文文本权利仍受原书版权约束，仅限个人学习使用。
