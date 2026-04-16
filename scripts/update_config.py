import json
from pathlib import Path

ROOT = Path.cwd().parent


def read_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def write_json(p: Path, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def collect_folders(path: Path):
    return [f.name for f in path.iterdir() if f.is_dir()] if path.exists() else []


def replace_all_values(obj, value):
    if isinstance(obj, dict):
        return {k: replace_all_values(v, value) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_all_values(i, value) for i in obj]
    return value


TASKS = [
    {
        "name": "theme",
        "dir": ROOT / "Themes" / "theme_pack",
        "config": ROOT / "Themes" / "theme_pack" / "config.json",
        "mode": "fill_all",
    },
    {
        "name": "anim",
        "dir": ROOT / "Filp" / "data" / "animations",
        "config": ROOT / "Filp" / "data" / "animations" / "hallAnimConfig.json",
        "mode": "fill_all",
    },
    {
        "name": "sound",
        "dir": ROOT / "Filp" / "data" / "sounds",
        "config": ROOT / "Filp" / "data" / "sounds" / "hallSoundConfig.json",
        "mode": "fill_all",
    },
]


def run_task(task):
    folders = collect_folders(task["dir"])
    print(task["name"], ":", folders)

    if not task["config"].exists():
        print(task["name"], "config 不存在喵")
        return

    data = read_json(task["config"])
    if not isinstance(data, dict):
        print(task["name"], "config 不是 dict")
        return

    value = ",".join(folders)
    new_data = replace_all_values(data, value)

    write_json(task["config"], new_data)
    print(task["name"], "完成喵")


def main():
    for t in TASKS:
        run_task(t)

    print("全部完成喵")


if __name__ == "__main__":
    main()
