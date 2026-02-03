#!/opt/homebrew/bin/python3.12
import argparse
import re
import subprocess
import sys
from pathlib import Path


STYLES = {
    "purple": {
        "title_color": "#8064a9",
        "text_color": "#444444",
        "quote_bg": "#f4f2f9",
        "code_bg": "#f6f8fa",
        "code_color": "#24292e",
        "font": "Open Sans, -apple-system, BlinkMacSystemFont, sans-serif",
    },
    "orangeheart": {
        "title_color": "#ef7060",
        "text_color": "#000000",
        "quote_bg": "#fff5f5",
        "code_bg": "#f6f8fa",
        "code_color": "#24292e",
        "font": "Optima, -apple-system, BlinkMacSystemFont, sans-serif",
    },
    "github": {
        "title_color": "#333333",
        "text_color": "#333333",
        "quote_bg": "#f6f8fa",
        "code_bg": "#f6f8fa",
        "code_color": "#24292e",
        "font": "Open Sans, -apple-system, BlinkMacSystemFont, sans-serif",
    },
}

DOOCS_THEMES = {
    "doocs-default": "default",
    "doocs-grace": "grace",
    "doocs-simple": "simple",
}


def _die(msg: str, code: int = 1) -> "None":
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def _render_doocs(article_md: Path, *, style: str) -> str:
    theme = DOOCS_THEMES[style]
    primary_color = STYLES.get("purple", {}).get("title_color", "#8064a9")

    script = Path(__file__).resolve().parent / "doocs_render.cjs"
    if not script.exists():
        _die(f"缺少 doocs 渲染脚本: {script}")

    cmd = [
        "node",
        str(script),
        "--article-md",
        str(article_md),
        "--theme",
        theme,
        "--primary-color",
        primary_color,
    ]
    res = subprocess.run(cmd, text=True, capture_output=True, cwd=str(script.parent))
    if res.returncode != 0:
        print(res.stdout)
        print(res.stderr, file=sys.stderr)
        raise SystemExit(res.returncode)
    return res.stdout


def md2html(md_content: str, style_name: str) -> str:
    style = STYLES.get(style_name, STYLES["purple"])

    def _md_links_to_html(text: str) -> str:
        return re.sub(
            r"\[([^\]]+)\]\((https?://[^)]+)\)",
            r'<a href="\2" style="color:#576b95;text-decoration:none">\1</a>',
            text,
        )

    lines = md_content.split("\n")
    html_parts: list[str] = []
    in_code_block = False
    code_content: list[str] = []
    in_table = False
    table_rows: list[list[str]] = []

    for line in lines:
        stripped = line.strip()

        # 跳过封面（封面单独作为 thumb_media_id 上传，不进入正文占位符序列）
        if stripped in ("![](cover.png)", "![cover](cover.png)"):
            continue

        # 图片：![](imgN.png) / ![alt](imgN.png)
        m = re.match(r"!\[([^\]]*)\]\((img(\d+)\.png)\)", stripped)
        if m:
            alt = m.group(1).strip()
            n = m.group(3)
            url = f"__WECHAT_IMG_{n}__"
            alt_attr = f' alt="{alt}"' if alt else ""
            html_parts.append(
                '<p style="text-align:center;margin:20px 0">'
                f'<img src="{url}"{alt_attr} style="max-width:100%;border-radius:8px">'
                "</p>"
            )
            continue

        # 代码块
        if line.startswith("```"):
            if in_code_block:
                code_html = "<br>".join(code_content)
                html_parts.append(
                    f'<pre style="background:{style["code_bg"]};padding:16px;border-radius:8px;'
                    f'overflow-x:auto;font-size:14px;line-height:1.6;color:{style["code_color"]};'
                    f'margin:16px 0;white-space:pre-wrap"><code>{code_html}</code></pre>'
                )
                code_content = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_content.append(line.replace("<", "&lt;").replace(">", "&gt;"))
            continue

        # 表格
        if line.startswith("|"):
            if not in_table:
                in_table = True
                table_rows = []
            if "---" not in line:
                cells = [c.strip() for c in line.split("|")[1:-1]]
                table_rows.append(cells)
            continue
        elif in_table:
            table_html = '<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:14px">'
            for i, row in enumerate(table_rows):
                if i == 0:
                    table_html += "<tr>" + "".join(
                        f'<th style="background:{style["quote_bg"]};padding:12px;border:1px solid #ddd;'
                        f'text-align:left;font-weight:600">{c}</th>'
                        for c in row
                    ) + "</tr>"
                else:
                    table_html += "<tr>" + "".join(
                        f'<td style="padding:12px;border:1px solid #ddd">{c}</td>' for c in row
                    ) + "</tr>"
            table_html += "</table>"
            html_parts.append(table_html)
            in_table = False

        if not stripped:
            continue

        # 标题
        if line.startswith("# "):
            title = line[2:]
            html_parts.append(
                f'<h1 style="color:{style["title_color"]};font-size:24px;font-weight:700;'
                f'margin:24px 0 16px;line-height:1.4">{title}</h1>'
            )
        elif line.startswith("## "):
            title = line[3:]
            html_parts.append(
                f'<h2 style="color:{style["title_color"]};font-size:20px;font-weight:600;'
                f'margin:24px 0 12px;border-left:4px solid {style["title_color"]};'
                f'padding-left:12px;line-height:1.4">{title}</h2>'
            )
        elif line.startswith("### "):
            title = line[4:]
            html_parts.append(
                f'<h3 style="color:{style["title_color"]};font-size:17px;font-weight:600;'
                f'margin:20px 0 10px">{title}</h3>'
            )
        # 引用
        elif line.startswith(">"):
            quote = line[1:].strip()
            html_parts.append(
                f'<blockquote style="background:{style["quote_bg"]};'
                f'border-left:4px solid {style["title_color"]};padding:15px 20px;'
                f'margin:16px 0;color:#666;font-style:italic">{quote}</blockquote>'
            )
        # 列表
        elif line.startswith("- "):
            item = line[2:]
            item = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", item)
            item = _md_links_to_html(item)
            html_parts.append(
                f'<p style="margin:8px 0;padding-left:20px;position:relative;'
                f'color:{style["text_color"]}"><span style="position:absolute;left:0;'
                f'color:{style["title_color"]}">•</span>{item}</p>'
            )
        elif re.match(r"^\d+\. ", line):
            item = re.sub(r"^\d+\. ", "", line)
            item = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", item)
            item = _md_links_to_html(item)
            html_parts.append(
                f'<p style="margin:8px 0;padding-left:24px;color:{style["text_color"]}">{item}</p>'
            )
        # 分隔线
        elif stripped == "---":
            html_parts.append('<hr style="border:none;border-top:1px solid #eee;margin:24px 0">')
        # 普通段落
        else:
            para = line
            para = re.sub(r"\*\*(.+?)\*\*", r'<strong style="color:#333">\1</strong>', para)
            para = _md_links_to_html(para)
            para = re.sub(
                r"`([^`]+)`",
                rf'<code style="background:{style["code_bg"]};padding:2px 6px;'
                rf'border-radius:4px;font-size:14px;color:{style["code_color"]}">\1</code>',
                para,
            )
            html_parts.append(
                f'<p style="margin:16px 0;line-height:1.8;color:{style["text_color"]}">{para}</p>'
            )

    return (
        f'<section style="font-family:{style["font"]};line-height:1.8;color:{style["text_color"]};'
        f'padding:20px;max-width:100%">{chr(10).join(html_parts)}</section>'
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="渲染公众号 HTML（正文图占位符 __WECHAT_IMG_n__）")
    parser.add_argument("--article-dir", required=True, help="文章目录")
    parser.add_argument(
        "--style",
        default="purple",
        help=f"CSS 风格：{', '.join(list(STYLES.keys()) + list(DOOCS_THEMES.keys()))}",
    )
    args = parser.parse_args()

    article_dir = Path(args.article_dir)
    article_md = article_dir / "article.md"
    if not article_md.exists():
        _die(f"缺少 article.md: {article_md}")

    style = str(args.style)
    if style in DOOCS_THEMES:
        html = _render_doocs(article_md, style=style)
    else:
        if style not in STYLES:
            _die(f"未知 style: {style}（支持：{', '.join(list(STYLES.keys()) + list(DOOCS_THEMES.keys()))}）")
        html = md2html(_read_text(article_md), style)
    out_path = article_dir / "article.html"
    _write_text(out_path, html)
    print(str(out_path))


if __name__ == "__main__":
    main()
