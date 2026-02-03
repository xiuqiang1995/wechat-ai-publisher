---
name: wechat-article-embedder
description: 将生成的封面与正文配图写回 article.md（标准 Markdown 图片引用），并移除中间锚点。用于“把图片插回文章/生成带图版文章”。
allowed-tools:
  - Bash
  - Read
  - Write
---

# 图片回填（Embedder）

目标：把 `cover.png` 和 `imgN.png` 插回 `article.md`，让 Obsidian 里可直接预览。

## 输入与输出

- 输入：
  - `.wechat-ai-publisher/article.plan.md`（包含 `<!-- ILLUS_n -->` 锚点）
  - `cover.png`、`img1.png..imgN.png`
- 输出：
  - 覆盖写入 `article.md`（最终带图版）
  - 备份：`.wechat-ai-publisher/article.original.md`

## 运行命令

```bash
/opt/homebrew/bin/python3.12 \
  ~/.claude/skills/wechat-article-embedder/scripts/embed_images.py \
  --article-dir "/path/to/article-dir"
```

