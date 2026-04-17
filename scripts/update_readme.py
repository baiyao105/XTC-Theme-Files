from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path.cwd().parent
OUT_FILE = ROOT / "README.md"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
DIAL_TYPE_MAP = {
    1: "SYSTEM_DIAL / CLOCK_TYPE_FILE",
    2: "APP_PHOTO / CLOCK_TYPE_PHOTO",
    3: "APP_MULTI_PHOTO / CLOCK_TYPE_MULTI",
    4: "HUNDRED / CLOCK_TYPE_HUNDRED",
    6: "WATCH_PHOTO / CUSTOMIZE_DIAL",
    7: "WALLPAPER / WALLPAPER_DIAL",
    8: "CUSTOM / CUSTOM_DIAL",
    9: "COMPOSE",
    10: "WALLPAPER2",
    11: "NET_COMPOSE",
    12: "WATCH_FACE_FORMAT_EDITABLE",
    -2: "CLOCK_CODE_WALLPAPER",
}


def _sorted_dirs(base: Path) -> list[Path]:
    if not base.exists():
        return []
    return [p for p in sorted(base.iterdir()) if p.is_dir()]


@lru_cache(maxsize=None)
def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as e:
        print(f"[JSON错误] {path}: {e}")
        return {}


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def get_name(data: dict, fallback: str) -> str:
    for key in ("name", "themeName", "displayName", "title", "chargeName"):
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return fallback


def md_img(p: Path, width=200):
    return f'<img src="{rel(p)}" width="{width}">'


def md_video(p: Path):
    return f'<video src="{rel(p)}" width="240" controls></video>'


def anchor(prefix: str, text: str) -> str:
    return f"{prefix}-{text.lower().replace(' ', '-').replace('_', '-')}"


def build_table(items, cols=7):
    if not items:
        return ""
    rows = [items[i : i + cols] for i in range(0, len(items), cols)]
    out = []
    header = rows[0]
    out.append("| " + " | ".join(header) + " |")
    out.append("| " + " | ".join(["---"] * len(header)) + " |")
    for row in rows[1:]:
        out.append("| " + " | ".join(row) + " |")
    return "\n".join(out)


def _theme_base() -> Path:
    return ROOT / "Themes" / "theme_pack"


def _dial_base() -> Path:
    return ROOT / "Themes" / "dial" / "res"


def _charge_base() -> Path:
    return ROOT / "Themes" / "charge"


def _filp_anim_base() -> Path:
    return ROOT / "Filp" / "data" / "animations"


def _filp_sound_base() -> Path:
    return ROOT / "Filp" / "data" / "sounds"


def table_theme():
    base = _theme_base()
    if not base.exists():
        return "_无主题_"

    items = []
    for item in _sorted_dirs(base):
        data = read_json(item / "config.json")
        tid = item.name
        name = get_name(data, tid)
        preview = item / "preview" / "1_preview_main.png"
        aid = anchor("theme", tid)
        if preview.exists():
            cell = f'[<img src="{rel(preview)}" width="120"><br>{name}](#{aid})'
        else:
            cell = f"[{name}](#{aid})"
        items.append(cell)

    return "## 🎨 主题\n\n" + build_table(items)


def table_dial():
    base = _dial_base()
    if not base.exists():
        return "_无表盘_"

    items = []
    for item in _sorted_dirs(base):
        did = item.name
        preview = item / "preview_main.png"
        aid = anchor("dial", did)
        cell = f'[<img src="{rel(preview)}" width="120"><br>{did}](#{aid})' if preview.exists() else f"[{did}](#{aid})"
        items.append(cell)

    return "## ⌚ 表盘\n\n" + build_table(items)


def table_charge():
    base = _charge_base()
    if not base.exists():
        return "_无充电动画_"

    items = []
    for item in _sorted_dirs(base):
        data = read_json(item / "config.json")
        cid = item.name
        name = get_name(data, cid)
        preview = item / "preview.png"
        aid = anchor("charge", cid)
        if preview.exists():
            cell = f'[<img src="{rel(preview)}" width="120"><br>{name}](#{aid})'
        else:
            cell = f"[{name}](#{aid})"
        items.append(cell)

    return "## ⚡ 充电动画\n\n" + build_table(items)


def table_filp():
    base = _filp_anim_base()
    if not base.exists():
        return "_无翻转动画_"

    items = []
    for item in _sorted_dirs(base):
        aid_name = item.name
        data = read_json(item / "config.json")
        compat_name = data.get("nameCompat", {}).get("def")
        name = compat_name or data.get("name") or aid_name
        preview = item / "preview.png"
        aid = anchor("filp", aid_name)
        if preview.exists():
            cell = f'[<img src="{rel(preview)}" width="120"><br>{name}](#{aid})'
        else:
            cell = f"[{name}](#{aid})"
        items.append(cell)

    return "## 🔄 翻转动画\n\n" + build_table(items, 6)


@lru_cache(maxsize=None)
def parse_3rdparty(text: str) -> str:
    names = []
    for line in text.splitlines():
        m = re.search(r"Signed-off-by:\s*(.+?)\s*<(.+?)>", line)
        if m:
            name, email = m.group(1), m.group(2)
            names.append(f"[{name}](mailto:{email})")

    if not names:
        return ""
    return f">*此资源由第三方提供: {' & '.join(names)}*\n"


@lru_cache(maxsize=None)
def get_3rdparty_info(flag: Path) -> str:
    if not flag.exists():
        return ""
    text = flag.read_text(encoding="utf-8", errors="ignore")
    return parse_3rdparty(text)


def get_dial_type_info(data):
    if not data:
        return None
    dt = data.get("dialType", None)
    if dt is None:
        return ""
    dt = int(dt)
    name = DIAL_TYPE_MAP.get(dt)
    return f"- 类型: `{dt} ({name})`"


def section_theme():
    base = _theme_base()
    out = ["## 🎨 主题", ""]
    if not base.exists():
        return "_无主题目录_"

    for item in _sorted_dirs(base):
        data = read_json(item / "config.json")
        dial_data = read_json(item / "dial" / "config.json")
        tid = item.name
        name = get_name(data, tid)
        source = data.get("sourceName", tid)
        aid = anchor("theme", tid)

        out.append("---\n")
        out.append(f'<a id="{aid}"></a>')
        preview_dir = item / "preview"
        main = preview_dir / "1_preview_main.png"
        extras = []

        if preview_dir.exists():
            for f in preview_dir.iterdir():
                if f.suffix.lower() in IMAGE_EXTS and f.name != "1_preview_main.png":
                    extras.append(f)

        out.append(f"### {name}  ")
        out.append(f"- source: `{tid}({source})`")
        out.append(get_dial_type_info(dial_data))
        out.append(get_3rdparty_info(item / "_3rdpartyasset"))

        if main.exists():
            out.append(md_img(main))
            out.append("")
        if extras:
            out.append("<details>")
            out.append("<summary>预览</summary>\n")
            for img in extras:
                out.append(md_img(img, 160))
            out.append("\n</details>\n")

    return "\n".join(out)


def section_dial():
    base = _dial_base()
    out = ["## ⌚ 表盘", ""]

    if not base.exists():
        return "_无表盘目录_"

    for item in _sorted_dirs(base):
        did = item.name
        aid = anchor("dial", did)
        out.append("---\n")
        out.append(f'<a id="{aid}"></a>')
        preview = item / "preview_main.png"
        out.append(f"### {did}\n")
        out.append(get_3rdparty_info(item / "_3rdpartyasset"))

        extras = []
        for f in item.iterdir():
            if f.is_file() and f.suffix.lower() in IMAGE_EXTS and f.name != "preview_main.png":
                extras.append(f)

        if preview.exists():
            out.append(md_img(preview))
            out.append("")
        if extras:
            out.append("<details>")
            out.append("<summary>预览</summary>\n")
            for img in extras:
                out.append(md_img(img, 160))
            out.append("\n</details>\n")

    return "\n".join(out)


def section_charge():
    base = _charge_base()
    out = ["## ⚡ 充电动画", ""]

    if not base.exists():
        return "_无充电动画目录_"

    for item in _sorted_dirs(base):
        data = read_json(item / "config.json")
        cid = item.name
        name = get_name(data, cid)
        source = data.get("sourceName", cid)
        aid = anchor("charge", cid)
        out.append("---\n")
        out.append(f'<a id="{aid}"></a>')
        img = item / "preview.png"
        video = item / "preview.mp4"
        out.append(f"### {name}  ")
        out.append(f"- source: `{cid}({source})`\n")
        out.append(get_3rdparty_info(item / "_3rdpartyasset"))

        if video.exists():
            out.append(md_video(video))
        elif img.exists():
            out.append(md_img(img))

    return "\n".join(out)


def section_filp():
    anim_base = _filp_anim_base()
    sound_base = _filp_sound_base()

    out = ["## 🔄 翻转动画", ""]

    if not anim_base.exists():
        return "_无翻转动画目录_"

    for item in _sorted_dirs(anim_base):
        fid = item.name
        data = read_json(item / "config.json")
        compat_name = data.get("nameCompat", {}).get("def")
        name = compat_name or data.get("name") or fid
        aid = anchor("filp", fid)
        bindSound = data.get("bindSound", False)
        out.append("---\n")
        out.append(f'<a id="{aid}"></a>')
        preview = item / "preview.png"
        open_video = item / "open.mp4"
        close_video = item / "close.mp4"
        out.append(get_3rdparty_info(item / "_3rdpartyasset"))
        sound_dir = sound_base / bindSound if bindSound else fid
        open_audio = sound_dir / "open.aac"
        close_audio = sound_dir / "close.aac"
        out.append(f"### {name}")
        out.append(f"<sub>{fid}</sub>")
        if compat_name:
            out.append(f"- source: `{fid}`")

        if preview.exists():
            out.append("")
            out.append(md_img(preview))
            out.append("")
        out.append("<details>")
        out.append("<summary>预览</summary>\n")
        if open_video.exists():
            out.append("**open.mp4**  ")
            out.append(md_video(open_video))
            out.append("")
        if close_video.exists():
            out.append("**close.mp4**  ")
            out.append(md_video(close_video))
            out.append("")
        if open_audio.exists():
            out.append(f'**open.aac**  \n<audio src="{rel(open_audio)}" controls></audio>\n')
        if close_audio.exists():
            out.append(f'**close.aac**  \n<audio src="{rel(close_audio)}" controls></audio>\n')
        out.append("\n</details>\n")

    return "\n".join(out)


def main():
    content = [
        "## 一些资源",
        "",
        "- [🎨 主题](#🎨-主题)",
        "- [⌚ 表盘](#⌚-表盘)",
        "- [⚡ 充电动画](#⚡-充电动画)",
        "- [🔄 翻转动画](#🔄-翻转动画)",
        "",
        "---",
        "",
        table_theme(),
        "",
        table_dial(),
        "",
        table_charge(),
        "",
        table_filp(),
        "",
        "---",
        "",
        section_theme(),
        "",
        section_dial(),
        "",
        section_charge(),
        "",
        section_filp(),
    ]

    OUT_FILE.write_text("\n".join(content), encoding="utf-8", newline="\n")
    print("✅ README 已生成")


if __name__ == "__main__":
    main()
