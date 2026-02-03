---
name: wechat-article-image-generator
description: 根据 prompts/cover.md 与 prompts/imgN.md 生成封面与正文配图文件（输出 cover.png 与 imgN.png）。用于“生图/生成封面与配图/批量生成插图”。
allowed-tools:
  - Bash
  - Read
  - Write
---

# 图片生成（Generator）

目标：只负责生成本地图片文件，不负责写作、排版、发布。

## 输入与输出

- 输入：文章目录下的 `prompts/cover.md` 与 `prompts/img1.md..imgN.md`
- 输出：文章目录下的 `cover.png` 与 `img1.png..imgN.png`

## 运行命令

```bash
/opt/homebrew/bin/python3.12 \
  ~/.claude/skills/wechat-article-image-generator/scripts/generate_images.py \
  --article-dir "/path/to/article-dir"
```

## 重要约束

- 严格按顺序生成：`img1` → `img2` → … → `imgN`
- N 通过 `prompts/imgN.md` 自动推断（取最大编号）

