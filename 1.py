from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path.cwd()
OUT_FILE = ROOT / "README.md"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


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


def build_table(items, cols=10):
    if not items:
        return ""
    rows = []
    for i in range(0, len(items), cols):
        rows.append(items[i : i + cols])
    out = []
    header = rows[0]
    out.append("| " + " | ".join(header) + " |")
    out.append("| " + " | ".join(["---"] * len(header)) + " |")
    for row in rows[1:]:
        out.append("| " + " | ".join(row) + " |")

    return "\n".join(out)


def table_theme():
    base = ROOT / "Themes" / "theme_pack"
    if not base.exists():
        return "_无主题_"

    items = []
    for item in sorted(base.iterdir()):
        if not item.is_dir():
            continue
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
    base = ROOT / "Themes" / "dial" / "res"
    if not base.exists():
        return "_无表盘_"

    items = []
    for item in sorted(base.iterdir()):
        if not item.is_dir():
            continue

        did = item.name
        preview = item / "preview_main.png"
        aid = anchor("dial", did)
        cell = f'[<img src="{rel(preview)}" width="120"><br>{did}](#{aid})' if preview.exists() else f"[{did}](#{aid})"
        items.append(cell)

    return "## ⌚ 表盘\n\n" + build_table(items)


def table_charge():
    base = ROOT / "Themes" / "charge"
    if not base.exists():
        return "_无充电动画_"

    items = []
    for item in sorted(base.iterdir()):
        if not item.is_dir():
            continue

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
    base = ROOT / "Filp" / "data" / "animations"
    if not base.exists():
        return "_无翻转动画_"

    items = []
    for item in sorted(base.iterdir()):
        if not item.is_dir():
            continue

        aid_name = item.name
        data = read_json(item / "config.json")
        name = get_name(data, aid_name)
        preview = item / "preview.png"
        aid = anchor("filp", aid_name)
        if preview.exists():
            cell = f'[<img src="{rel(preview)}" width="120"><br>{name}](#{aid})'
        else:
            cell = f"[{name}](#{aid})"

        items.append(cell)

    return "## 🔄 翻转动画\n\n" + build_table(items)


def section_theme():
    base = ROOT / "Themes" / "theme_pack"
    out = ["## 🎨 主题", ""]
    if not base.exists():
        return "_无主题目录_"

    for item in sorted(base.iterdir()):
        if not item.is_dir():
            continue

        data = read_json(item / "config.json")
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
        out.append(f"- source: `{source}({tid})`\n")
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
    base = ROOT / "Themes" / "dial" / "res"
    out = ["## ⌚ 表盘", ""]

    if not base.exists():
        return "_无表盘目录_"

    for item in sorted(base.iterdir()):
        if not item.is_dir():
            continue

        did = item.name
        aid = anchor("dial", did)
        out.append("---\n")
        out.append(f'<a id="{aid}"></a>')
        preview = item / "preview_main.png"
        out.append(f"### {did}\n")
        if preview.exists():
            out.append(md_img(preview))
            out.append("")

    return "\n".join(out)


def section_charge():
    base = ROOT / "Themes" / "charge"
    out = ["## ⚡ 充电动画", ""]

    if not base.exists():
        return "_无充电动画目录_"

    for item in sorted(base.iterdir()):
        if not item.is_dir():
            continue

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
        out.append(f"- source: `{source}({cid})`\n")

        if video.exists():
            out.append(md_video(video))
        elif img.exists():
            out.append(md_img(img))

    return "\n".join(out)


def section_filp():
    anim_base = ROOT / "Filp" / "data" / "animations"
    sound_base = ROOT / "Filp" / "data" / "sounds"

    out = ["## 🔄 翻转动画", ""]

    if not anim_base.exists():
        return "_无翻转动画目录_"

    for item in sorted(anim_base.iterdir()):
        if not item.is_dir():
            continue

        fid = item.name
        data = read_json(item / "config.json")
        name = get_name(data, fid)
        aid = anchor("filp", fid)
        out.append("---\n")
        out.append(f'<a id="{aid}"></a>')
        preview = item / "preview.png"
        open_video = item / "open.mp4"
        close_video = item / "close.mp4"
        sound_dir = sound_base / fid
        open_audio = sound_dir / "open.aac"
        close_audio = sound_dir / "close.aac"
        out.append(f"### {name}")
        out.append(f"<sub>{fid}</sub>\n")

        if preview.exists():
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

    OUT_FILE.write_text("\n".join(content), encoding="utf-8")
    print("✅ README 已生成")


if __name__ == "__main__":
    main()
