#!/opt/homebrew/bin/python3.12
import argparse
import re
import sys
from pathlib import Path


def _die(msg: str, code: int = 1) -> "None":
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _insert_cover(md: str) -> str:
    lines = md.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("# "):
            # 如果标题后已经有 cover，就不重复插入
            for j in range(i + 1, min(i + 6, len(lines))):
                if lines[j].strip() == "![](cover.png)":
                    return "\n".join(lines).rstrip() + "\n"
            insert = [lines[i], "", "![](cover.png)", ""]
            rest = lines[i + 1 :]
            return "\n".join(insert + rest).rstrip() + "\n"
    # 没有标题则放在开头
    return ("![](cover.png)\n\n" + md).rstrip() + "\n"


def _replace_anchors(md: str, *, n: int) -> str:
    out = md
    for i in range(1, n + 1):
        anchor = f"<!-- ILLUS_{i} -->"
        if anchor not in out:
            _die(f"缺少锚点（Planner 输出不完整）：{anchor}")
        out = out.replace(anchor, f"![](img{i}.png)")
    # 清理多余空行：保证图片前后有空行
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.rstrip() + "\n"


def _infer_n(article_dir: Path) -> int:
    nums: list[int] = []
    for p in article_dir.glob("img*.png"):
        m = re.match(r"img(\d+)\.png$", p.name)
        if m:
            nums.append(int(m.group(1)))
    return max(nums) if nums else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="把封面与配图写回 article.md（标准 Markdown 图片引用）")
    parser.add_argument("--article-dir", required=True, help="文章目录")
    args = parser.parse_args()

    article_dir = Path(args.article_dir)
    work_dir = article_dir / ".wechat-ai-publisher"
    plan_md = work_dir / "article.plan.md"
    if not plan_md.exists():
        _die(f"缺少规划文件: {plan_md}")

    cover = article_dir / "cover.png"
    if not cover.exists():
        _die(f"缺少封面图: {cover}")

    n = _infer_n(article_dir)
    if n <= 0:
        _die(f"未找到正文配图 imgN.png: {article_dir}")

    for i in range(1, n + 1):
        p = article_dir / f"img{i}.png"
        if not p.exists():
            _die(f"缺少配图（编号必须连续）：{p}")

    final_md = _read_text(plan_md)
    final_md = _replace_anchors(final_md, n=n)
    final_md = _insert_cover(final_md)

    article_md = article_dir / "article.md"
    if article_md.exists():
        backup = work_dir / "article.original.md"
        if not backup.exists():
            _write_text(backup, _read_text(article_md))

    _write_text(article_md, final_md)
    # 额外保存一份“渲染前、已插图版”到文章目录，便于在 Obsidian 中直接查看
    _write_text(article_dir / "article.with_images.md", final_md)
    print(str(article_md))


if __name__ == "__main__":
    main()
