"""
Shard manifest generator for ocode-audit-shrink.

Discovers all .py files under game/, shuffles with a configurable seed,
then distributes into 4 balanced shards using greedy load-balancing.

Excludes: __pycache__/

Usage:
  python Tools/audit_shrink/manifest.py <output_raw_dir> [--seed STR] [--shards N]
"""

import argparse
import json
import os
import random
import sys
from datetime import datetime
from pathlib import Path


def _find_project_root() -> str:
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "data").is_dir():
            return str(current)
        current = current.parent
    raise RuntimeError("Could not find project root")


PROJECT_ROOT = _find_project_root()
GAME_DIR = Path(PROJECT_ROOT) / "game"


def _collect_files() -> list[str]:
    """Return all .py files under game/, excluding __pycache__, as relative paths."""
    files: list[str] = []
    for py_file in sorted(GAME_DIR.rglob("*.py")):
        if "__pycache__" in py_file.parts:
            continue
        rel = str(py_file.relative_to(PROJECT_ROOT)).replace("\\", "/")
        files.append(rel)
    return files


def _estimate_loc(filepath: str) -> int:
    try:
        with open(filepath, encoding="utf-8") as f:
            return sum(1 for _ in f)
    except (OSError, UnicodeDecodeError):
        return 0


def greedy_balance(
    files: list[tuple[str, int]], shard_count: int
) -> list[list[tuple[str, int]]]:
    """Assign each file to the currently smallest shard (greedy).

    Files are processed in the order given — the caller is responsible for
    shuffling before calling to achieve randomized distribution.
    """
    shards: list[list[tuple[str, int]]] = [[] for _ in range(shard_count)]
    totals = [0] * shard_count

    for filepath, loc in files:
        min_idx = min(range(shard_count), key=lambda i: totals[i])
        shards[min_idx].append((filepath, loc))
        totals[min_idx] += loc

    return shards


def _compute_next_shard_id(shard_count: int) -> str:
    """Look at the audit_shrink history to determine which shard to deep-review next.

    Rotates ``01 -> 02 -> ... -> {shard_count:02d} -> 01``. Returns ``"01"`` on
    first run or when history can't be read.
    """
    history_path = os.path.join(PROJECT_ROOT, "Reviews", "results", "shrink_tracker.json")
    try:
        with open(history_path, encoding="utf-8") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return "01"
    runs = history.get("runs", [])
    if not runs:
        return "01"
    last = runs[-1].get("deep_review_shard")
    if not last:
        return "01"
    try:
        next_idx = (int(last) % shard_count) + 1
    except (TypeError, ValueError):
        return "01"
    return f"{next_idx:02d}"


def generate(output_dir: str | None = None, seed: str | None = None, shard_count: int = 4) -> dict:
    """Generate shard manifest. If output_dir is set, write manifest.json there."""
    file_paths = _collect_files()
    files = [(p, _estimate_loc(os.path.join(PROJECT_ROOT, p))) for p in file_paths]

    if seed is None:
        seed = datetime.now().strftime("%Y-%m-%d")

    rng = random.Random(seed)
    rng.shuffle(files)

    shards = greedy_balance(files, shard_count)

    manifest: dict = {
        "seed": seed,
        "shard_count": shard_count,
        "total_files": len(files),
        "total_loc_estimate": sum(loc for _, loc in files),
        "next_shard_id": _compute_next_shard_id(shard_count),
        "shards": {},
    }

    for i, shard in enumerate(shards):
        sid = f"{i + 1:02d}"
        file_paths = sorted(path for path, _ in shard)
        manifest["shards"][sid] = {
            "label": f"Shard {sid}",
            "file_count": len(file_paths),
            "loc_estimate": sum(loc for _, loc in shard),
            "files": file_paths,
        }

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "manifest.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate randomized shard manifest for ocode-audit-shrink."
    )
    parser.add_argument(
        "output_dir",
        nargs="?",
        default=None,
        help="Raw output directory to write manifest.json into",
    )
    parser.add_argument(
        "--seed",
        default=None,
        help="Seed for randomization (default: current date, YYYY-MM-DD)",
    )
    parser.add_argument(
        "--shards",
        type=int,
        default=4,
        help="Number of shards to split into (default: 4)",
    )
    args = parser.parse_args()

    manifest = generate(output_dir=args.output_dir, seed=args.seed, shard_count=args.shards)

    print(f"Manifest: {manifest['total_files']} files across {manifest['shard_count']} shards")
    print(f"Seed: {manifest['seed']}")
    for sid, info in manifest["shards"].items():
        print(f"  Shard {sid}: {info['file_count']} files, ~{info['loc_estimate']} LOC ({info['label']})")


if __name__ == "__main__":
    main()
