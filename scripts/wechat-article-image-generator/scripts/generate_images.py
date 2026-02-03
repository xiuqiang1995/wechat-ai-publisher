#!/opt/homebrew/bin/python3.12
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


PYTHON_BIN = "/opt/homebrew/bin/python3.12"
GENERATE_IMAGE_SCRIPT = Path.home() / ".claude/skills/article-illustrator/scripts/generate_image.py"


def _die(msg: str, code: int = 1) -> "None":
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _max_img_index(prompts_dir: Path) -> int:
    nums: list[int] = []
    for p in prompts_dir.glob("img*.md"):
        m = re.match(r"img(\d+)\.md$", p.name)
        if m:
            nums.append(int(m.group(1)))
    return max(nums) if nums else 0


def _run(prompt: str, output_path: Path, aspect_ratio: str) -> None:
    if not GENERATE_IMAGE_SCRIPT.exists():
        _die(f"缺少生图脚本: {GENERATE_IMAGE_SCRIPT}（请安装 article-illustrator）")
    result = subprocess.run(
        [
            PYTHON_BIN,
            str(GENERATE_IMAGE_SCRIPT),
            "--prompt",
            prompt,
            "--output",
            str(output_path),
            "--aspect-ratio",
            aspect_ratio,
        ],
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        _die((result.stdout or "").strip() + "\n" + (result.stderr or "").strip())


def main() -> None:
    parser = argparse.ArgumentParser(description="根据 prompts 生成封面与正文配图（公众号链路）")
    parser.add_argument("--article-dir", required=True, help="文章目录（包含 prompts/）")
    parser.add_argument("--cover-aspect", default="2.35:1", help="封面宽高比（默认 2.35:1）")
    parser.add_argument("--image-aspect", default="4:3", help="正文配图宽高比（默认 4:3）")
    parser.add_argument("--skip-existing", action="store_true", help="若文件已存在则跳过生成")
    args = parser.parse_args()

    article_dir = Path(args.article_dir)
    prompts_dir = article_dir / "prompts"
    if not prompts_dir.exists():
        _die(f"缺少 prompts 目录: {prompts_dir}")

    cover_prompt_path = prompts_dir / "cover.md"
    if not cover_prompt_path.exists():
        _die(f"缺少封面 prompt: {cover_prompt_path}")

    n = _max_img_index(prompts_dir)
    if n <= 0:
        _die(f"未找到正文 prompts（期望 prompts/img1.md..imgN.md）: {prompts_dir}")

    out: dict[str, str] = {}

    cover_path = article_dir / "cover.png"
    if not (args.skip_existing and cover_path.exists()):
        _run(_read_text(cover_prompt_path).strip(), cover_path, str(args.cover_aspect))
    out["cover"] = str(cover_path)

    for i in range(1, n + 1):
        prompt_path = prompts_dir / f"img{i}.md"
        if not prompt_path.exists():
            _die(f"缺少 prompt（编号必须连续）: {prompt_path}")
        img_path = article_dir / f"img{i}.png"
        if args.skip_existing and img_path.exists():
            out[f"img{i}"] = str(img_path)
            continue
        _run(_read_text(prompt_path).strip(), img_path, str(args.image_aspect))
        out[f"img{i}"] = str(img_path)

    out["n"] = n
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
