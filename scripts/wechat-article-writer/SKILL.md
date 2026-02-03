---
name: wechat-article-writer
description: 生成微信公众号文章（只负责写 Markdown 正文，不负责配图、生图、发布）。当用户说“写公众号文章/生成公众号文章/公众号写作”时使用。
allowed-tools:
  - Read
  - Write
  - WebSearch
  - WebFetch
  - AskUserQuestion
---

# 公众号文章写作（只写文，不配图）

## 输入与输出

- 输入：用户主题/目标读者/目的 + 英文信源素材（需要时用 WebSearch/Fetch）。
- 输出：一篇 `article.md`（Markdown），保存到 Obsidian 的文章目录（由编排器创建目录）。

## 写作要求

- 使用正常的公众号 Markdown：至少有 `#` 标题，正文用 `##` 分段。
- 不要在正文里插入任何图片引用（`![]()`）或 `IMAGE_n` 注释，占位由后续 Planner/Embedder 负责。
- 只使用英文信源（素材采集阶段禁止中文网站）。
- 保持自然流畅的写作风格，避免过度模板化的表达。

## 与 Humanizer-zh 的衔接（由编排器负责）

在 `wechat-ai-publisher` 流程里，写完 `article.md` 后可能会先用 `humanizer-zh` 做一次“去 AI 味改写”，然后再 `sanitize` 并让用户做确认 1。

因此本 skill 只负责把内容写清楚、写完整、写得像人，不需要在这里额外引入“模板化润色流程”或插入图片占位。

## 纯文本清理（写完后必须做）

写完 `article.md` 后，立刻执行一次“纯文本清理”，把 `*` 与中英文双引号去掉，确保用户在确认 1 看到的内容与最终发布内容一致：

```bash
source ~/.zshrc && /opt/homebrew/bin/python3.12 \
  ~/.claude/skills/wechat-ai-publisher/scripts/wechat_publisher.py \
  sanitize \
  --article-dir "/Users/aqiang/Library/Mobile Documents/iCloud~md~obsidian/Documents/OB-LOCAL/wechat-ai-publisher/YYYY-MM-DD_slug"
```
