import json
import os
import sys
from pathlib import Path


def _find_project_root():
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "data").is_dir():
            return str(current)
        current = current.parent
    raise RuntimeError("Could not find project root")


PROJECT_ROOT = _find_project_root()
sys.path.insert(0, PROJECT_ROOT)

from game.core.paths import Paths

GAME_DIR = Path(Paths.GAME_DIR)

SHARDS = [
    {
        "id": "UI",
        "label": "UI Layer",
        "dirs": ["ui"],
    },
    {
        "id": "SIM",
        "label": "Simulation Layer",
        "dirs": ["simulation"],
    },
    {
        "id": "STR",
        "label": "Strategy Layer",
        "dirs": ["strategy"],
    },
    {
        "id": "FND",
        "label": "Foundation Layer",
        "dirs": ["core", "engine", "ai", "research"],
    },
]


def _collect_files():
    all_files = []
    for py_file in sorted(GAME_DIR.rglob("*.py")):
        if "__pycache__" in py_file.parts:
            continue
        rel = str(py_file.relative_to(GAME_DIR)).replace("\\", "/")
        all_files.append(rel)
    return all_files


def _assign_to_shards(files):
    shard_files = {s["id"]: [] for s in SHARDS}

    for file_path in files:
        top_dir = file_path.split("/")[0]
        assigned = False
        for shard in SHARDS:
            if top_dir in shard["dirs"]:
                shard_files[shard["id"]].append(file_path)
                assigned = True
                break

        if not assigned:
            shard_files["FND"].append(file_path)

    return shard_files


def _get_current_rotation(output_dir):
    """Determine which shard should be deep-reviewed this run based on rotation history."""
    tracker_path = os.path.join(output_dir, "..", "shrink_tracker.json")
    try:
        with open(tracker_path, "r", encoding="utf-8") as f:
            tracker = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

    runs = tracker.get("runs", [])
    shard_ids = [s["id"] for s in SHARDS]

    if not runs:
        return 0

    if len(runs) < len(shard_ids):
        return len(runs)

    last_reviewed = {}
    for shard_id in shard_ids:
        last_reviewed[shard_id] = -1

    for i, run in enumerate(reversed(runs)):
        shard = run.get("deep_review_shard", "")
        if shard and shard not in last_reviewed:
            last_reviewed[shard] = len(runs) - 1 - i
        elif shard and (last_reviewed.get(shard, -1) == -1 or last_reviewed[shard] < len(runs) - 1 - i):
            last_reviewed[shard] = len(runs) - 1 - i

    oldest_shard = min(last_reviewed, key=last_reviewed.get)
    return shard_ids.index(oldest_shard)


def generate(output_dir=None):
    files = _collect_files()
    shard_files = _assign_to_shards(files)

    rotation_index = _get_current_rotation(output_dir) if output_dir else 0
    deep_review_shard = SHARDS[rotation_index]["id"]

    manifest = {
        "total_files": len(files),
        "shards": {},
        "deep_review_shard": deep_review_shard,
        "deep_review_label": SHARDS[rotation_index]["label"],
        "rotation_index": rotation_index,
        "rotation_total": len(SHARDS),
    }

    for shard in SHARDS:
        sfiles = shard_files[shard["id"]]
        manifest["shards"][shard["id"]] = {
            "label": shard["label"],
            "file_count": len(sfiles),
            "files": sorted(sfiles),
        }

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "manifest.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    return manifest


if __name__ == "__main__":
    import sys

    output_dir = sys.argv[1] if len(sys.argv) > 1 else None
    manifest = generate(output_dir)
    deep = manifest["deep_review_shard"]
    print(f"Manifest: {manifest['total_files']} files across {len(SHARDS)} shards")
    print(f"Deep review shard this run: {deep} ({manifest['shards'][deep]['file_count']} files)")
    for shard_id, info in manifest["shards"].items():
        marker = " <<< DEEP REVIEW" if shard_id == deep else ""
        print(f"  {shard_id}: {info['file_count']} files{marker}")
