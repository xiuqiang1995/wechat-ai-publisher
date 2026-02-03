---
name: wechat-markdown-renderer
description: 将最终带图版 article.md 渲染为公众号发布用 HTML（正文图替换为 __WECHAT_IMG_n__ 占位符，封面图不进入正文占位符序列）。用于“md 转公众号 html/渲染公众号 html”。
allowed-tools:
  - Bash
  - Read
  - Write
---

# Markdown → WeChat HTML（Renderer）

目标：只负责把 `article.md` 转为 `article.html`，供发布步骤使用。

## 输入与输出

- 输入：文章目录下的 `article.md`（最终带图版，包含 `![](cover.png)` 和 `![](imgN.png)`）
- 输出：文章目录下的 `article.html`

## 运行命令

```bash
/opt/homebrew/bin/python3.12 \
  ~/.claude/skills/wechat-markdown-renderer/scripts/render_wechat_html.py \
  --article-dir "/path/to/article-dir" \
  --style purple
```

## style 选项

- 内置：`purple` / `orangeheart` / `github`
- doocs/md 主题：`doocs-default` / `doocs-grace` / `doocs-simple`

说明：doocs 主题通过 CSS + 内联（juice）生成最终 HTML，更接近 doocs/md（微信 Markdown 编辑器）的排版效果。
