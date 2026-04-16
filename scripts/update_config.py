import json
from pathlib import Path

ROOT = Path.cwd().parent
BASE = ROOT / "Themes" / "theme_pack"
CONFIG = BASE / "config.json"


def read_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def write_json(p: Path, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def collect_folders():
    return [f.name for f in BASE.iterdir() if f.is_dir()]


def replace_all_values(obj, value):
    if isinstance(obj, dict):
        return {k: replace_all_values(v, value) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_all_values(i, value) for i in obj]
    else:
        return value


def main():
    if not CONFIG.exists():
        print("config.json 不存在喵")
        return

    folders = collect_folders()
    print("主题:", folders)
    data = read_json(CONFIG)
    if not isinstance(data, dict):
        print("config.json 不是合法 JSON")
        return
    new_data = replace_all_values(data, ",".join(folders))
    write_json(CONFIG, new_data)
    print("完成喵")


if __name__ == "__main__":
    main()
