---
name: wechat-draft-publisher
description: 发布 skill：将 HTML 文章发布到微信公众号草稿箱（上传封面与正文图片，替换 __WECHAT_IMG_n__ 占位符，创建草稿）。当用户说“发布到公众号/发布到微信草稿箱/上传到公众号草稿箱/WeChat draft publish”时触发。
allowed-tools:
  - Bash
  - Read
  - Write
---

# WeChat Draft Publisher

该 skill 只负责“上传素材并创建公众号草稿”，不负责写作/排版/生图。

## 前置条件

- 环境变量：
  - `WECHAT_APPID`
  - `WECHAT_SECRET`
- Python 依赖：`pip install requests`

## 输入约定

- HTML 内容通过 `--html` 指定文件路径。
- 正文图片占位符：`__WECHAT_IMG_1__`、`__WECHAT_IMG_2__`… 会按 `--image` 的顺序替换为微信返回的 URL。

## 使用示例

```bash
source ~/.zshrc && /opt/homebrew/bin/python3.12 \
  ~/.claude/skills/wechat-draft-publisher/scripts/wechat_draft_publisher.py \
  --html /tmp/wechat_publish/article.html \
  --title "标题" \
  --digest "摘要" \
  --cover /tmp/wechat_publish/cover.png \
  --image /tmp/wechat_publish/img1.png \
  --image /tmp/wechat_publish/img2.png
```

输出：JSON（包含 `draft_id` / `thumb_media_id` / `img_urls`）。

