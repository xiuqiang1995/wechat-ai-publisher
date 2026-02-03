#!/opt/homebrew/bin/python3.12
import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path


BAOYU_STYLE_DIR = Path.home() / ".claude/skills/baoyu-article-illustrator/references/styles"
FALLBACK_STYLE_DIR = Path.home() / ".claude/skills/markdown-image-generator/references/styles"


def _die(msg: str, code: int = 1) -> "None":
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _extract_title(md: str) -> str:
    m = re.search(r"^#\s+(.+)$", md, re.MULTILINE)
    return m.group(1).strip() if m else "无标题"


def _strip_md_noise(text: str) -> str:
    s = re.sub(r"```.*?```", "", text, flags=re.S)
    s = re.sub(r"`[^`]+`", "", s)
    s = re.sub(r"\!\[[^\]]*\]\([^)]+\)", "", s)
    s = re.sub(r"\[[^\]]+\]\([^)]+\)", "", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _first_meaningful_snippet(text: str, *, max_len: int = 180) -> str:
    in_code = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if line.startswith("<!--") or line.startswith("#"):
            continue
        if line.startswith(">"):
            continue
        # 跳过图片引用（避免把 ![](cover.png) 之类当成主题摘要）
        if re.match(r"^!\[[^\]]*\]\([^)]+\)$", line):
            continue
        if line.lower().startswith("<img"):
            continue
        line = re.sub(r"^\s*[-*]\s+", "", line)
        line = re.sub(r"^\s*\d+\.\s+", "", line)
        line = re.sub(r"\s+", " ", line).strip()
        if not line:
            continue
        return (line[:max_len] + "…") if len(line) > max_len else line
    return ""


def _load_style_snippet(style_id: str, *, max_chars: int = 320) -> str:
    for base in (BAOYU_STYLE_DIR, FALLBACK_STYLE_DIR):
        p = base / f"{style_id}.md"
        if p.exists():
            content = _read_text(p)
            lines = [ln.rstrip() for ln in content.splitlines()]
            keep: list[str] = []
            in_aesthetic = False
            in_background = False
            for ln in lines:
                if ln.startswith("## "):
                    in_aesthetic = ln.strip() == "## Design Aesthetic"
                    in_background = ln.strip() == "## Background"
                    continue
                if ln.startswith("#"):
                    continue
                if in_aesthetic and ln.strip():
                    keep.append(ln.strip())
                if in_background and ln.strip().startswith("-"):
                    keep.append(ln.strip().lstrip("-").strip())
                if len(" ".join(keep)) >= max_chars:
                    break
            snippet = " ".join(keep).strip()
            if not snippet:
                snippet = " ".join([ln.strip() for ln in lines[:40] if ln.strip() and not ln.startswith("#")])
                snippet = snippet[:max_chars].strip()
            return snippet
    _die(f"未找到风格文件: {style_id}.md（在 {BAOYU_STYLE_DIR} 或 {FALLBACK_STYLE_DIR}）")

def _choose_cover_type(md: str) -> tuple[str, str]:
    """
    封面 Type（版式/构图类型），参考 baoyu-cover-image 的信号规则做简化自动选择。
    """
    t = _strip_md_noise(md).lower()
    rules: list[tuple[str, list[str]]] = [
        ("hero", ["launch", "announcement", "release", "reveal", "发布", "上线", "官宣", "发布会", "重大"]),
        ("conceptual", ["架构", "architecture", "framework", "system", "api", "pipeline", "workflow", "自动化", "方法论", "系统设计"]),
        ("typography", ["quote", "opinion", "观点", "金句", "洞见", "headline", "statement"]),
        ("metaphor", ["philosophy", "growth", "meaning", "reflection", "隐喻", "心智", "增长", "复利", "意义"]),
        ("scene", ["story", "journey", "travel", "lifestyle", "故事", "经历", "旅程", "生活", "手机端"]),
        ("minimal", ["zen", "focus", "essential", "minimal", "极简", "本质", "聚焦", "只做", "最小"]),
    ]
    scores: dict[str, int] = {k: 0 for k, _ in rules}
    for k, keywords in rules:
        scores[k] = sum(1 for w in keywords if w in t)
    best = max(scores.items(), key=lambda kv: kv[1])[0]
    if scores[best] == 0:
        return "conceptual", "未检测到强指示词，默认 conceptual"
    return best, f"命中统计：{', '.join([f'{k}={scores[k]}' for k, _ in rules])}"


def _choose_cover_mood(md: str) -> tuple[str, str]:
    """
    Mood（情绪强度/视觉重量），参考 baoyu-cover-image 做简化：
    - subtle：专业、技术、文档感
    - bold：发布、促销、活动、强刺激
    - balanced：默认
    """
    t = _strip_md_noise(md).lower()
    subtle = ["professional", "corporate", "academic", "documentation", "技术", "架构", "系统", "流程", "规范", "工具"]
    bold = ["launch", "announcement", "promo", "event", "重大", "发布", "爆款", "一键", "立即", "增长"]
    subtle_hits = sum(1 for w in subtle if w in t)
    bold_hits = sum(1 for w in bold if w in t)
    if bold_hits > max(0, subtle_hits):
        return "bold", f"bold={bold_hits} subtle={subtle_hits}"
    if subtle_hits > 0:
        return "subtle", f"subtle={subtle_hits} bold={bold_hits}"
    return "balanced", "未检测到强指示词，默认 balanced"


def _choose_cover_text(md: str) -> tuple[str, str]:
    """
    Text（封面文字密度）。
    基于 nano-banana-pro 对中文更友好的假设，默认允许封面包含短标题（title-only）。
    若你更偏好“纯视觉封面”，可通过 CLI 指定 --cover-text none。
    """
    _ = md
    return "title-only", "默认允许封面短标题（nano-banana-pro 中文可读性较好）"


def _cover_icon_hints(md: str) -> list[str]:
    """
    从内容抽取“可画成抽象图标/物件”的线索，避免品牌/商标。
    """
    t = md.lower()
    hints: list[str] = []
    if "手机" in md or "mobile" in t or "phone" in t:
        hints.append("a smartphone")
    if "icloud" in t or "云" in md:
        hints.append("a cloud sync folder")
    if "obsidian" in t or "笔记" in md:
        hints.append("a generic note app / notebook")
    if "草稿箱" in md or "draft" in t:
        hints.append("a draft inbox")
    if "发布" in md or "publish" in t:
        hints.append("a publish button")
    if "流程" in md or "pipeline" in t or "workflow" in t:
        hints.append("a clean pipeline diagram (arrows and steps)")
    # 去重并限制长度
    seen: set[str] = set()
    out: list[str] = []
    for h in hints:
        if h in seen:
            continue
        seen.add(h)
        out.append(h)
    return out[:5]


def _choose_visual_type(text: str) -> str:
    t = text.lower()
    if re.search(r"(流程|步骤|第.+步|step|how to|tutorial|guide|pipeline)", t):
        return "flowchart"
    if re.search(r"(对比|比较|vs|versus|pros|cons|trade-?off)", t):
        return "comparison diagram"
    if re.search(r"(架构|architecture|system|infrastructure|stack)", t):
        return "architecture diagram"
    if re.search(r"(时间线|timeline|history|evolution|roadmap)", t):
        return "timeline"
    if re.search(r"(清单|checklist|要点|summary|key points)", t):
        return "structured key-points infographic"
    return "concept map"


def _score_section(text: str) -> float:
    t = text.lower()
    score = float(len(_strip_md_noise(text)))
    score += 450.0 * len(re.findall(r"(流程|步骤|第.+步|how to|tutorial|guide)", t))
    score += 350.0 * len(re.findall(r"(对比|比较|vs|versus|trade-?off)", t))
    score += 300.0 * len(re.findall(r"(架构|architecture|system|infrastructure)", t))
    score += 180.0 * len(re.findall(r"\|\s*---\s*\|", text))  # table
    score += 120.0 * len(re.findall(r"^\s*[-*]\s+|^\s*\d+\.\s+", text, flags=re.M))  # list
    return score


def _decide_n(md: str, *, max_images: int) -> int:
    body = _strip_md_noise(md)
    total = len(body)
    if total < 600:
        return 1
    if total < 1800:
        return min(2, max_images)
    n = round(total / 900)
    n = max(2, n)
    return min(max_images, n)


@dataclass(frozen=True)
class Candidate:
    insert_at: int  # line index in original lines
    section_idx: int
    heading: str
    section_text: str
    score: float


def _extract_sections(lines: list[str]) -> list[tuple[int, int, str]]:
    heading_idxs: list[tuple[int, str]] = []
    in_code = False
    for idx, line in enumerate(lines):
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if line.startswith("## "):
            heading_idxs.append((idx, line[3:].strip()))
    sections: list[tuple[int, int, str]] = []
    for i, (start, heading) in enumerate(heading_idxs):
        end = heading_idxs[i + 1][0] if i + 1 < len(heading_idxs) else len(lines)
        sections.append((start, end, heading))
    return sections


def _find_first_block_end(lines: list[str], *, start: int, end: int) -> int:
    i = start
    while i < end:
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("<!--"):
            i += 1
            continue
        if stripped.startswith("```"):
            i += 1
            while i < end and not lines[i].startswith("```"):
                i += 1
            if i < end:
                i += 1
            continue
        if stripped.startswith("|"):
            i += 1
            while i < end and lines[i].strip().startswith("|"):
                i += 1
            return i
        if stripped.startswith(("- ", "* ")) or re.match(r"^\d+\.\s+", stripped):
            i += 1
            while i < end and lines[i].strip():
                if lines[i].strip().startswith("```"):
                    break
                if lines[i].strip().startswith("<!--"):
                    break
                i += 1
            return i
        i += 1
        while i < end and lines[i].strip():
            if lines[i].strip().startswith("```"):
                break
            i += 1
        return i
    return start


def _build_candidates(md: str) -> list[Candidate]:
    lines = md.splitlines()
    sections = _extract_sections(lines)
    candidates: list[Candidate] = []
    for idx, (s_start, s_end, heading) in enumerate(sections, 1):
        section_text = "\n".join(lines[s_start + 1 : s_end]).strip()
        insert_at = _find_first_block_end(lines, start=s_start + 1, end=s_end)
        candidates.append(
            Candidate(
                insert_at=insert_at,
                section_idx=idx,
                heading=heading,
                section_text=section_text,
                score=_score_section(f"{heading}\n{section_text}"),
            )
        )
    if not candidates:
        candidates.append(
            Candidate(
                insert_at=len(lines),
                section_idx=1,
                heading="正文",
                section_text=md,
                score=_score_section(md),
            )
        )
    return candidates


def _cover_prompt(*, title: str, md: str, style_snippet: str, cover_type: str, cover_text: str, cover_mood: str) -> str:
    intro = md.split("## ", 1)[0]
    intro_snippet = _first_meaningful_snippet(intro)

    type_hint = {
        "hero": "hero composition with a strong focal visual (leave whitespace for title area)",
        "conceptual": "conceptual infographic composition with clear zones and structure",
        "typography": "typography-led layout (but keep text minimal/optional)",
        "metaphor": "visual metaphor expressing the core idea",
        "scene": "clean scene illustration with narrative cues",
        "minimal": "minimal composition with a single focal element and lots of whitespace",
    }.get(cover_type, "conceptual infographic composition")

    mood_hint = {
        "subtle": "subtle mood: muted colors, low contrast, calm visual weight",
        "balanced": "balanced mood: medium contrast and saturation",
        "bold": "bold mood: higher contrast and saturation, stronger visual weight",
    }.get(cover_mood, "balanced mood")

    text_hint = {
        "none": "No text elements in the image.",
        "title-only": "Include a short Chinese headline (<= 10 characters), hand-drawn lettering style.",
        "title-subtitle": "Include Chinese headline + short subtitle (hand-drawn lettering), keep them concise.",
        "text-rich": "Include Chinese headline + subtitle + 2-4 keyword tags (hand-drawn lettering), keep them concise.",
    }.get(cover_text, "No text elements in the image.")

    icons = _cover_icon_hints(md)
    icon_hint = f"Suggested visual elements: {', '.join(icons)}. " if icons else ""

    base = f"Create a WeChat article cover image (2.35:1) for the article titled '{title}'."
    if intro_snippet:
        base += f" Theme: {intro_snippet}."

    safety_tail = (
        "If any text is included, ensure it is legible Chinese characters, short and clean, "
        "hand-drawn lettering style. Do not include long sentences."
    )
    if cover_text == "none":
        safety_tail = "Do not include any text elements in the image."

    return (
        f"{base} {icon_hint}"
        f"Cover type: {type_hint}. {mood_hint}. {text_hint} "
        f"Illustration style guide: {style_snippet}. "
        "Hand-drawn / vector illustration feel (no photorealism). Clean composition, ample whitespace. "
        "Main visual centered or slightly left; keep the layout uncluttered. "
        "No logos, no real-person portraits, no copyrighted characters. "
        f"{safety_tail}"
    )


def _img_prompt(*, title: str, heading: str, section_text: str, style_snippet: str) -> str:
    snippet = _first_meaningful_snippet(section_text)
    visual_type = _choose_visual_type(f"{heading}\n{section_text}")
    base = f"Create a clean infographic ({visual_type}) explaining the section '{heading}' in the article '{title}'."
    if snippet:
        base += f" Focus on this key idea: {snippet}."
    return (
        f"{base} "
        f"Illustration style guide: {style_snippet}. "
        "Use abstract shapes, icons, arrows, and simple blocks. Clean composition, ample whitespace. "
        "No logos, no real-person portraits, no copyrighted characters. "
        "If labels help understanding, use short legible Chinese labels (hand-drawn lettering). "
        "Avoid long sentences."
    )


def _insert_anchors(md: str, picks: list[Candidate]) -> str:
    lines = md.splitlines()
    inserts: list[tuple[int, list[str]]] = []
    for num, cand in enumerate(picks, 1):
        block: list[str] = []
        if cand.insert_at > 0 and lines[cand.insert_at - 1].strip():
            block.append("")
        block.append(f"<!-- ILLUS_{num} -->")
        block.append("")
        inserts.append((cand.insert_at, block))

    for idx, block in sorted(inserts, key=lambda x: x[0], reverse=True):
        lines[idx:idx] = block

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="为公众号文章自动规划插图（输出 prompts + article.plan.md）")
    parser.add_argument("--article-md", required=True, help="article.md 路径")
    parser.add_argument("--image-style", default="notion", help="配图风格 ID（references/styles/<style>.md）")
    parser.add_argument("--cover-type", default="auto", choices=["auto", "hero", "conceptual", "typography", "metaphor", "scene", "minimal"], help="封面构图类型（默认 auto）")
    parser.add_argument("--cover-text", default="auto", choices=["auto", "none", "title-only", "title-subtitle", "text-rich"], help="封面文字密度（默认 auto；建议 none）")
    parser.add_argument("--cover-mood", default="auto", choices=["auto", "subtle", "balanced", "bold"], help="封面情绪强度（默认 auto）")
    parser.add_argument("--max-images", type=int, default=6, help="最大正文配图张数（默认 6）")
    args = parser.parse_args()

    article_md = Path(args.article_md)
    if not article_md.exists():
        _die(f"文件不存在: {article_md}")

    article_dir = article_md.parent
    md = _read_text(article_md)
    title = _extract_title(md)

    max_images = max(1, min(int(args.max_images), 6))
    n = _decide_n(md, max_images=max_images)
    candidates = _build_candidates(md)
    candidates_sorted = sorted(candidates, key=lambda c: c.score, reverse=True)
    picks = candidates_sorted[: min(n, len(candidates_sorted))]
    picks = sorted(picks, key=lambda c: c.insert_at)

    # 强制连续编号 + 最多 6
    picks = picks[:max_images]

    style_snippet = _load_style_snippet(str(args.image_style))

    cover_type, cover_type_reason = _choose_cover_type(md)
    cover_text, cover_text_reason = _choose_cover_text(md)
    cover_mood, cover_mood_reason = _choose_cover_mood(md)
    if str(args.cover_type) != "auto":
        cover_type = str(args.cover_type)
        cover_type_reason = "由 --cover-type 指定"
    if str(args.cover_text) != "auto":
        cover_text = str(args.cover_text)
        cover_text_reason = "由 --cover-text 指定"
    if str(args.cover_mood) != "auto":
        cover_mood = str(args.cover_mood)
        cover_mood_reason = "由 --cover-mood 指定"

    prompts_dir = article_dir / "prompts"
    cover_prompt_path = prompts_dir / "cover.md"
    _write_text(
        cover_prompt_path,
        _cover_prompt(
            title=title,
            md=md,
            style_snippet=style_snippet,
            cover_type=cover_type,
            cover_text=cover_text,
            cover_mood=cover_mood,
        )
        + "\n",
    )

    img_prompt_paths: list[str] = []
    for i, cand in enumerate(picks, 1):
        p = prompts_dir / f"img{i}.md"
        _write_text(p, _img_prompt(title=title, heading=cand.heading, section_text=cand.section_text, style_snippet=style_snippet) + "\n")
        img_prompt_paths.append(str(p))

    work_dir = article_dir / ".wechat-ai-publisher"
    plan_md_path = work_dir / "article.plan.md"
    _write_text(plan_md_path, _insert_anchors(md, picks))

    print(
        json.dumps(
            {
                "article_dir": str(article_dir),
                "n": len(picks),
                "plan_md": str(plan_md_path),
                "cover": {
                    "type": cover_type,
                    "type_reason": cover_type_reason,
                    "text": cover_text,
                    "text_reason": cover_text_reason,
                    "mood": cover_mood,
                    "mood_reason": cover_mood_reason,
                },
                "cover_prompt": str(cover_prompt_path),
                "img_prompts": img_prompt_paths,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
