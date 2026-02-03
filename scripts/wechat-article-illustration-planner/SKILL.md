---
name: wechat-article-illustration-planner
description: 为公众号文章自动规划配图（自动决定 1-6 张正文图的位置与提示词），输出 prompts/imgN.md 与 article.plan.md。用于“给文章配图/生成配图提示词/规划插图”。
allowed-tools:
  - Bash
  - Read
  - Write
---

# 公众号配图规划（Planner）

目标：只做“规划”，不生成图片、不发布。

## 输入与输出

- 输入：文章目录下的 `article.md`（纯文本版，无图片）。
- 输出：
  - `prompts/cover.md`（封面 prompt）
  - `prompts/img1.md..prompts/imgN.md`（正文配图 prompts，N 自动决定，最大 6）
  - `.wechat-ai-publisher/article.plan.md`（插入 `<!-- ILLUS_n -->` 锚点的中间文件）

## 运行命令

```bash
/opt/homebrew/bin/python3.12 \
  ~/.claude/skills/wechat-article-illustration-planner/scripts/plan_illustrations.py \
  --article-md "/path/to/article-dir/article.md" \
  --image-style notion \
  --max-images 6
```

## 重要约束

- N 必须是连续编号（img1..imgN），且 `N<=6`。
- 只写 prompts（溯源只靠 `prompts/`），最终文章不保留 `<!-- IMAGE_n -->`。
- 插图顺序必须与文章出现顺序一致（便于后续严格映射 `imgN.png → __WECHAT_IMG_N__`）。

