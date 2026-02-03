#!/opt/homebrew/bin/python3.12
import argparse
import json
import os
import sys
from pathlib import Path


def _die(msg: str, code: int = 1) -> "None":
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _get_access_token(*, appid: str, secret: str) -> str:
    import requests

    resp = requests.get(
        "https://api.weixin.qq.com/cgi-bin/token",
        params={"grant_type": "client_credential", "appid": appid, "secret": secret},
        timeout=30,
    )
    data = resp.json()
    token = data.get("access_token")
    if not token:
        _die(f"获取 access_token 失败: {data}")
    return token


def _upload_cover(*, token: str, cover_path: Path) -> str:
    import requests

    with cover_path.open("rb") as f:
        resp = requests.post(
            f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image",
            files={"media": ("cover.png", f, "image/png")},
            timeout=120,
        )
    data = resp.json()
    media_id = data.get("media_id")
    if not media_id:
        _die(f"上传封面失败: {data}")
    return media_id


def _upload_images(*, token: str, image_paths: list[Path]) -> list[str]:
    import requests

    urls: list[str] = []
    for idx, path in enumerate(image_paths, 1):
        with path.open("rb") as f:
            resp = requests.post(
                f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={token}",
                files={"media": (f"img{idx}.png", f, "image/png")},
                timeout=120,
            )
        data = resp.json()
        url = data.get("url")
        if not url:
            _die(f"上传配图{idx}失败: {data}")
        urls.append(url)
    return urls


def _create_draft(*, token: str, title: str, digest: str, html_content: str, thumb_media_id: str) -> str:
    import requests

    payload = {
        "articles": [
            {
                "title": title[:64],
                "digest": digest[:120],
                "content": html_content,
                "thumb_media_id": thumb_media_id,
                "need_open_comment": 1,
                "only_fans_can_comment": 0,
            }
        ]
    }
    resp = requests.post(
        f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        timeout=60,
    )
    data = resp.json()
    draft_id = data.get("media_id")
    if not draft_id:
        _die(f"创建草稿失败: {data}")
    return draft_id


def main() -> None:
    parser = argparse.ArgumentParser(description="发布 HTML 到微信公众号草稿箱（上传封面/配图/创建草稿）")
    parser.add_argument("--html", required=True, help="HTML 文件路径")
    parser.add_argument("--title", required=True, help="文章标题（微信限制 64 字符）")
    parser.add_argument("--digest", default="", help="文章摘要（微信限制 120 字符）")
    parser.add_argument("--cover", required=True, help="封面图片路径（PNG）")
    parser.add_argument("--image", action="append", default=[], help="正文配图路径（可重复传入）")
    args = parser.parse_args()

    try:
        import requests  # noqa: F401
    except Exception:
        _die("缺少 requests 库，运行: pip install requests")

    appid = os.environ.get("WECHAT_APPID")
    secret = os.environ.get("WECHAT_SECRET")
    if not appid:
        _die("缺少环境变量: WECHAT_APPID")
    if not secret:
        _die("缺少环境变量: WECHAT_SECRET")

    html_path = Path(args.html)
    if not html_path.exists():
        _die(f"HTML 文件不存在: {html_path}")
    cover_path = Path(args.cover)
    if not cover_path.exists():
        _die(f"封面图片不存在: {cover_path}")

    image_paths = [Path(p) for p in args.image]
    for p in image_paths:
        if not p.exists():
            _die(f"正文配图不存在: {p}")

    html_content = _read_text(html_path)

    token = _get_access_token(appid=appid, secret=secret)
    thumb_media_id = _upload_cover(token=token, cover_path=cover_path)
    img_urls = _upload_images(token=token, image_paths=image_paths) if image_paths else []

    for idx, url in enumerate(img_urls, 1):
        html_content = html_content.replace(f"__WECHAT_IMG_{idx}__", url)

    draft_id = _create_draft(
        token=token,
        title=args.title,
        digest=args.digest,
        html_content=html_content,
        thumb_media_id=thumb_media_id,
    )

    print(
        json.dumps(
            {"draft_id": draft_id, "thumb_media_id": thumb_media_id, "img_urls": img_urls},
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

