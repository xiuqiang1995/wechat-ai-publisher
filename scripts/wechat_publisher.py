#!/opt/homebrew/bin/python3.12
"""
wechat-ai-publisher 编排脚本（build/publish）

该脚本只负责把多个“职责单一”的脚本串起来：
- Planner: 生成 prompts + article.plan.md
- Generator: 生成 cover.png + imgN.png
- Embedder: 把图片写回 article.md（带图版）
- Renderer: 渲染 article.html（正文图占位符 __WECHAT_IMG_n__）
- Publisher: 调用 wechat-draft-publisher 创建公众号草稿

注意：人工确认由上层编排（skill）负责：
1) 先确认纯文本 article.md
2) 不再做本地“确认 2”，最终在公众号草稿箱里验收
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


PYTHON_BIN = "/opt/homebrew/bin/python3.12"
CSS_STYLES = ["purple", "orangeheart", "github", "doocs-default", "doocs-grace", "doocs-simple"]

PLANNER_SCRIPT = Path.home() / ".claude/skills/wechat-article-illustration-planner/scripts/plan_illustrations.py"
GENERATOR_SCRIPT = Path.home() / ".claude/skills/wechat-article-image-generator/scripts/generate_images.py"
EMBEDDER_SCRIPT = Path.home() / ".claude/skills/wechat-article-embedder/scripts/embed_images.py"
RENDERER_SCRIPT = Path.home() / ".claude/skills/wechat-markdown-renderer/scripts/render_wechat_html.py"
WECHAT_DRAFT_PUBLISHER_SCRIPT = Path.home() / ".claude/skills/wechat-draft-publisher/scripts/wechat_draft_publisher.py"


def _die(msg: str, code: int = 1) -> "None":
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def _run(cmd: list[str]) -> str:
    res = subprocess.run(cmd, text=True, capture_output=True)
    if res.returncode != 0:
        print(res.stdout)
        print(res.stderr, file=sys.stderr)
        raise SystemExit(res.returncode)
    return res.stdout.strip()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _sanitize_md_text(md: str) -> str:
    """
    公众号“纯文本”清理：
    - 去掉 Markdown 强调符号 '*'（避免渲染歧义）
    - 去掉中英文双引号 “ ” 和 "

    为避免破坏代码示例：代码块（```）与行内代码（`...`）内不做替换。
    """
    out_lines: list[str] = []
    in_code_block = False

    for line in md.splitlines():
        if line.startswith("```"):
            in_code_block = not in_code_block
            out_lines.append(line)
            continue

        if in_code_block:
            out_lines.append(line)
            continue

        parts = line.split("`")
        for i in range(0, len(parts), 2):
            parts[i] = parts[i].replace("*", "").replace("“", "").replace("”", "").replace('"', "")
        out_lines.append("`".join(parts))

    return "\n".join(out_lines).rstrip() + "\n"


def sanitize(*, article_dir: Path) -> dict:
    article_md = article_dir / "article.md"
    if not article_md.exists():
        _die(f"缺少 article.md: {article_md}")

    work_dir = article_dir / ".wechat-ai-publisher"
    backup = work_dir / "article.before_sanitize.md"
    if not backup.exists():
        _write_text(backup, _read_text(article_md))

    before = _read_text(article_md)
    after = _sanitize_md_text(before)
    changed = before != after
    if changed:
        _write_text(article_md, after)

    return {"article_dir": str(article_dir), "article_md": str(article_md), "backup": str(backup), "changed": changed}


def _extract_title_and_digest(article_md: Path) -> tuple[str, str]:
    md = _read_text(article_md)
    m = re.search(r"^#\s+(.+)$", md, re.MULTILINE)
    title = (m.group(1).strip() if m else "无标题")[:64]

    lines: list[str] = []
    for raw in md.splitlines():
        s = raw.strip()
        if not s:
            continue
        if s.startswith("#"):
            continue
        if s in ("![](cover.png)", "![cover](cover.png)"):
            continue
        if s.startswith("![](") or s.startswith("!["):
            continue
        lines.append(s)
        if len(lines) >= 3:
            break
    digest = (lines[0] if lines else "")[:120]
    return title, digest


def _available_image_styles() -> set[str]:
    roots = [
        Path.home() / ".claude/skills/baoyu-article-illustrator/references/styles",
        Path.home() / ".claude/skills/markdown-image-generator/references/styles",
    ]
    out: set[str] = set()
    for r in roots:
        if not r.exists():
            continue
        for p in r.glob("*.md"):
            if p.is_file():
                out.add(p.stem)
    return out


def _choose_css_style(md: str) -> tuple[str, str]:
    text = md.lower()

    github_hits = 0
    github_terms = [
        "github",
        "cli",
        "codex",
        "claude",
        "mcp",
        "api",
        "sdk",
        "websocket",
        "daemon",
        "server",
        "encryption",
        "encrypt",
        "key",
        "npm",
        "node",
        "typescript",
        "javascript",
        "python",
        "docker",
        "k8s",
    ]
    for t in github_terms:
        if t in text:
            github_hits += 1
    if "```" in md or "`" in md:
        github_hits += 2

    orange_hits = 0
    orange_terms = [
        "生活",
        "情绪",
        "成长",
        "关系",
        "焦虑",
        "自律",
        "幸福",
        "疗愈",
        "温暖",
        "亲密",
        "父母",
        "孩子",
        "健康",
        "睡眠",
    ]
    for t in orange_terms:
        if t in md:
            orange_hits += 1

    purple_hits = 0
    purple_terms = [
        "产品",
        "商业",
        "策略",
        "增长",
        "运营",
        "转化",
        "roi",
        "数据",
        "方法论",
        "框架",
        "系统",
    ]
    for t in purple_terms:
        if t in text:
            purple_hits += 1

    scores = {"github": github_hits, "orangeheart": orange_hits, "purple": purple_hits}
    best = max(scores.items(), key=lambda kv: kv[1])[0]
    if scores[best] == 0:
        return "purple", "未检测到强指示词，使用默认 purple"
    return best, f"命中统计：github={scores['github']} purple={scores['purple']} orangeheart={scores['orangeheart']}"


def _pick_first_available(prefer: list[str], available: set[str]) -> str:
    for s in prefer:
        if s in available:
            return s
    return "notion" if "notion" in available else (sorted(available)[0] if available else "notion")


def _choose_image_style(md: str, *, css_style: str, available: set[str]) -> tuple[str, str]:
    text = md.lower()

    if css_style == "github":
        prefer = ["blueprint", "scientific", "minimal", "notion", "vector-illustration", "sketch-notes"]
        if any(k in text for k in ["mcp", "cli", "daemon", "server", "api", "encryption", "websocket"]):
            prefer = ["blueprint", "scientific", "notion", "minimal", "vector-illustration"]
        picked = _pick_first_available(prefer, available)
        return picked, f"css=github，优先 {', '.join(prefer[:3])}"

    if css_style == "orangeheart":
        prefer = ["warm", "watercolor", "nature", "playful", "notion", "minimal"]
        picked = _pick_first_available(prefer, available)
        return picked, f"css=orangeheart，优先 {', '.join(prefer[:3])}"

    prefer = ["notion", "editorial", "minimal", "scientific", "vector-illustration", "retro"]
    if any(k in text for k in ["产品", "商业", "增长", "运营", "转化", "roi", "strategy", "framework"]):
        prefer = ["editorial", "notion", "minimal", "scientific", "vector-illustration"]
    picked = _pick_first_available(prefer, available)
    return picked, f"css=purple，优先 {', '.join(prefer[:3])}"


def build(
    *,
    article_dir: Path,
    css_style: str,
    image_style: str,
    max_images: int,
    skip_existing_images: bool,
    cover_type: str,
    cover_text: str,
    cover_mood: str,
) -> dict:
    article_md = article_dir / "article.md"
    if not article_md.exists():
        _die(f"缺少 article.md: {article_md}")

    work_dir = article_dir / ".wechat-ai-publisher"
    original_md = work_dir / "article.original.md"
    # 若之前已生成过带图版，则优先用 original 作为 build 输入，避免重复回填导致图片重复
    if original_md.exists():
        _write_text(article_md, _read_text(original_md))

    for p in (PLANNER_SCRIPT, GENERATOR_SCRIPT, EMBEDDER_SCRIPT, RENDERER_SCRIPT):
        if not p.exists():
            _die(f"缺少脚本: {p}")

    if not os.environ.get("REPLICATE_API_TOKEN"):
        _die("缺少环境变量: REPLICATE_API_TOKEN（用于生图）")

    raw_md = _read_text(article_md)
    available_styles = _available_image_styles()
    auto_cfg: dict[str, str] = {}

    resolved_css = css_style
    resolved_img = image_style

    if cover_type not in ("auto", "hero", "conceptual", "typography", "metaphor", "scene", "minimal"):
        _die(f"未知封面构图类型: {cover_type}")
    if cover_text not in ("auto", "none", "title-only", "title-subtitle", "text-rich"):
        _die(f"未知封面文字密度: {cover_text}")
    if cover_mood not in ("auto", "subtle", "balanced", "bold"):
        _die(f"未知封面情绪强度: {cover_mood}")

    if css_style == "auto":
        resolved_css, reason = _choose_css_style(raw_md)
        auto_cfg["css_style"] = resolved_css
        auto_cfg["css_reason"] = reason
    elif css_style not in CSS_STYLES:
        _die(f"未知 CSS 风格：{css_style}（支持：auto / {', '.join(CSS_STYLES)}）")

    if image_style == "auto":
        resolved_img, reason = _choose_image_style(raw_md, css_style=resolved_css, available=available_styles)
        auto_cfg["image_style"] = resolved_img
        auto_cfg["image_reason"] = reason

    style_record = {
        "css_style": resolved_css,
        "image_style": resolved_img,
        "auto": auto_cfg,
    }
    _write_text(work_dir / "style.json", json.dumps(style_record, ensure_ascii=False, indent=2) + "\n")

    planner_cmd = [
        PYTHON_BIN,
        str(PLANNER_SCRIPT),
        "--article-md",
        str(article_md),
        "--image-style",
        resolved_img,
        "--max-images",
        str(max_images),
        "--cover-type",
        cover_type,
        "--cover-text",
        cover_text,
        "--cover-mood",
        cover_mood,
    ]
    planner_out = _run(planner_cmd)
    try:
        planner_data = json.loads(planner_out)
    except json.JSONDecodeError:
        _die("解析 Planner 输出失败（期望 JSON）")

    gen_cmd = [PYTHON_BIN, str(GENERATOR_SCRIPT), "--article-dir", str(article_dir)]
    if skip_existing_images:
        gen_cmd.append("--skip-existing")
    generator_out = _run(gen_cmd)
    try:
        generator_data = json.loads(generator_out)
    except json.JSONDecodeError:
        _die("解析 Generator 输出失败（期望 JSON）")

    _run([PYTHON_BIN, str(EMBEDDER_SCRIPT), "--article-dir", str(article_dir)])
    renderer_out = _run([PYTHON_BIN, str(RENDERER_SCRIPT), "--article-dir", str(article_dir), "--style", resolved_css])

    build_data = {
        "article_dir": str(article_dir),
        "style": style_record,
        "planner": planner_data,
        "images": generator_data,
        "html": renderer_out,
    }
    _write_text(work_dir / "build.json", json.dumps(build_data, ensure_ascii=False, indent=2) + "\n")
    return build_data


def publish(*, article_dir: Path) -> dict:
    article_md = article_dir / "article.md"
    html_path = article_dir / "article.html"
    cover_path = article_dir / "cover.png"
    if not html_path.exists():
        _die(f"缺少 article.html（请先 build）：{html_path}")
    if not cover_path.exists():
        _die(f"缺少 cover.png（请先 build）：{cover_path}")
    if not article_md.exists():
        _die(f"缺少 article.md: {article_md}")

    if not WECHAT_DRAFT_PUBLISHER_SCRIPT.exists():
        _die(f"缺少发布脚本: {WECHAT_DRAFT_PUBLISHER_SCRIPT}")

    if not os.environ.get("WECHAT_APPID"):
        _die("缺少环境变量: WECHAT_APPID")
    if not os.environ.get("WECHAT_SECRET"):
        _die("缺少环境变量: WECHAT_SECRET")

    title, digest = _extract_title_and_digest(article_md)

    imgs: list[Path] = []
    nums: list[int] = []
    for p in article_dir.glob("img*.png"):
        m = re.match(r"img(\d+)\.png$", p.name)
        if not m:
            continue
        nums.append(int(m.group(1)))
    n = max(nums) if nums else 0
    for i in range(1, n + 1):
        p = article_dir / f"img{i}.png"
        if not p.exists():
            _die(f"缺少正文配图（编号必须连续）：{p}")
        imgs.append(p)

    cmd = [
        PYTHON_BIN,
        str(WECHAT_DRAFT_PUBLISHER_SCRIPT),
        "--html",
        str(html_path),
        "--title",
        title,
        "--digest",
        digest,
        "--cover",
        str(cover_path),
    ]
    for p in imgs:
        cmd += ["--image", str(p)]

    out = _run(cmd)
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        _die("解析 wechat-draft-publisher 输出失败（期望 JSON）")

    _write_text(
        article_dir / "publish.json",
        json.dumps(
            {
                "title": title,
                "digest": digest,
                "article_dir": str(article_dir),
                "cover": str(cover_path),
                "images": [str(p) for p in imgs],
                "result": data,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="wechat-ai-publisher pipeline")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_sanitize = sub.add_parser("sanitize", help="清理纯文本 article.md（去除 * 与中英文双引号）")
    p_sanitize.add_argument("--article-dir", required=True, help="文章目录（包含 article.md）")

    p_build = sub.add_parser("build", help="规划配图 + 生图 + 回填 + 渲染（不发布）")
    p_build.add_argument("--article-dir", required=True, help="文章目录（包含 article.md）")
    p_build.add_argument("--style", default="auto", choices=["auto", *CSS_STYLES], help="CSS 风格")
    p_build.add_argument("--image-style", default="auto", help="配图风格（references/styles/<style>.md）或 auto")
    p_build.add_argument("--max-images", type=int, default=6, help="最大正文配图张数（默认 6）")
    p_build.add_argument("--skip-existing-images", action="store_true", help="图片存在则跳过生成")
    p_build.add_argument("--cover-type", default="auto", choices=["auto", "hero", "conceptual", "typography", "metaphor", "scene", "minimal"], help="封面构图类型（默认 auto）")
    p_build.add_argument("--cover-text", default="auto", choices=["auto", "none", "title-only", "title-subtitle", "text-rich"], help="封面文字密度（默认 auto；推荐 title-only；纯视觉用 none）")
    p_build.add_argument("--cover-mood", default="auto", choices=["auto", "subtle", "balanced", "bold"], help="封面情绪强度（默认 auto）")

    p_pub = sub.add_parser("publish", help="发布到公众号草稿箱（需要先 build）")
    p_pub.add_argument("--article-dir", required=True, help="文章目录")

    p_ship = sub.add_parser("ship", help="build 后直接发布到公众号草稿箱（跳过本地确认 2）")
    p_ship.add_argument("--article-dir", required=True, help="文章目录（包含 article.md）")
    p_ship.add_argument("--style", default="auto", choices=["auto", *CSS_STYLES], help="CSS 风格")
    p_ship.add_argument("--image-style", default="auto", help="配图风格（references/styles/<style>.md）或 auto")
    p_ship.add_argument("--max-images", type=int, default=6, help="最大正文配图张数（默认 6）")
    p_ship.add_argument("--skip-existing-images", action="store_true", help="图片存在则跳过生成")
    p_ship.add_argument("--cover-type", default="auto", choices=["auto", "hero", "conceptual", "typography", "metaphor", "scene", "minimal"], help="封面构图类型（默认 auto）")
    p_ship.add_argument("--cover-text", default="auto", choices=["auto", "none", "title-only", "title-subtitle", "text-rich"], help="封面文字密度（默认 auto；推荐 title-only；纯视觉用 none）")
    p_ship.add_argument("--cover-mood", default="auto", choices=["auto", "subtle", "balanced", "bold"], help="封面情绪强度（默认 auto）")

    args = parser.parse_args()
    article_dir = Path(args.article_dir)

    if args.cmd == "sanitize":
        data = sanitize(article_dir=article_dir)
        print(json.dumps(data, ensure_ascii=False))
        return

    if args.cmd == "build":
        data = build(
            article_dir=article_dir,
            css_style=str(args.style),
            image_style=str(args.image_style),
            max_images=int(args.max_images),
            skip_existing_images=bool(args.skip_existing_images),
            cover_type=str(args.cover_type),
            cover_text=str(args.cover_text),
            cover_mood=str(args.cover_mood),
        )
        print(json.dumps(data, ensure_ascii=False))
        return

    if args.cmd == "publish":
        data = publish(article_dir=article_dir)
        print(json.dumps(data, ensure_ascii=False))
        return

    if args.cmd == "ship":
        build_data = build(
            article_dir=article_dir,
            css_style=str(args.style),
            image_style=str(args.image_style),
            max_images=int(args.max_images),
            skip_existing_images=bool(args.skip_existing_images),
            cover_type=str(args.cover_type),
            cover_text=str(args.cover_text),
            cover_mood=str(args.cover_mood),
        )
        publish_data = publish(article_dir=article_dir)
        print(json.dumps({"build": build_data, "publish": publish_data}, ensure_ascii=False))
        return

    _die(f"未知命令: {args.cmd}")


if __name__ == "__main__":
    main()
