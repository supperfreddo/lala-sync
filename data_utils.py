import gzip
import json
from pathlib import Path

IMPORT_DIR = Path("data/imports")
CATEGORIES_DIR = Path("data/categories")


def import_from_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def get_import_files():
    return list(IMPORT_DIR.glob("*.json*"))


def create_local_files(character_id, categories):
    for category in categories:
        save_category(
            category,
            character_id,
            preprocess_data(import_from_file(CATEGORIES_DIR / f"{category}.json")),
        )


def save_category(category_name, character_id, entries, compression_level=9):
    path = Path(f"data/{character_id}") / f"{category_name}.json.gz"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(
            path, "wt", encoding="utf-8", compresslevel=compression_level
        ) as f:
            json.dump(entries, f, ensure_ascii=False, indent=4)
    else:
        data = load_category(category_name, character_id)
        for entry in entries:
            for i, e in enumerate(data):
                if e["id"] == entry["id"]:
                    data[i] = entry
                    break
        with gzip.open(
            path, "wt", encoding="utf-8", compresslevel=compression_level
        ) as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


def load_category(category_name, character_id):
    path = Path(f"data/{character_id}") / f"{category_name}.json.gz"

    if not path.exists():
        print(f"File {path} does not exist, returning empty list")
        return []

    try:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return preprocess_data(json.load(f))
    except (gzip.BadGzipFile, json.JSONDecodeError):
        print(f"Error loading {category_name}, returning empty list")
        return []


def get_categories():
    return [path.stem.split(".")[0] for path in CATEGORIES_DIR.glob("*.json")]


def preprocess_data(data):
    for entry in data:
        entry.setdefault("id", None)
        entry.setdefault("name", None)
        entry.setdefault("added", False)
    return data
