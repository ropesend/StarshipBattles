"""
Shard generator for ocode-test-review.

Discovers all test files under tests/, shuffles with a configurable seed,
then distributes into balanced shards using greedy load-balancing (by LOC).

Exclusions:
  - tests/unit/combat_lab/ (all files)
  - __init__.py
  - __pycache__/
  - tests/infrastructure/

Includes:
  - All test_*.py files under tests/
  - Standalone repro_*.py scripts at tests/ root level

Usage:
  python Tools/test_review/generate_shards.py [--seed STR] [--shards N] [--output DIR]

Default: seed from current date, 6 shards, output to Reviews/results/<timestamp>_test-review/
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
TESTS_ROOT = os.path.join(PROJECT_ROOT, "tests")

EXCLUDE_PREFIXES: list[str] = [
    os.path.join("tests", "unit", "combat_lab"),
    "tests" + os.sep + "unit" + os.sep + "combat_lab",
]

EXCLUDE_NAMES: set[str] = {"__init__.py"}
EXCLUDE_DIR_PATTERNS: set[str] = {"__pycache__", "infrastructure"}


def _estimate_loc(filepath: str) -> int:
    """Fast LOC estimate from file line count."""
    try:
        with open(filepath, encoding="utf-8") as f:
            return sum(1 for _ in f)
    except (OSError, UnicodeDecodeError):
        return 0


def _is_excluded(rel_path: str, filename: str) -> bool:
    """Check if a file or directory should be excluded from sharding."""
    if filename in EXCLUDE_NAMES:
        return True
    if not filename.endswith(".py"):
        return True
    if filename == "conftest.py":
        return False
    if not (filename.startswith("test_") or filename.startswith("repro_")):
        return True
    norm = rel_path.replace("\\", "/")
    for prefix in [p.replace("\\", "/") for p in EXCLUDE_PREFIXES]:
        if norm.startswith(prefix):
            return True
    for pattern in EXCLUDE_DIR_PATTERNS:
        if pattern in norm.split("/"):
            return True
    return False


def discover_test_files(tests_root: str) -> list[tuple[str, int]]:
    """Walk tests/ recursively, return [(relative_path, loc_estimate), ...]."""
    results: list[tuple[str, int]] = []
    for dirpath, dirnames, filenames in os.walk(tests_root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIR_PATTERNS]
        rel_dir = os.path.relpath(dirpath, PROJECT_ROOT)
        for filename in filenames:
            rel_path = os.path.join(rel_dir, filename)
            if _is_excluded(rel_path, filename):
                continue
            full_path = os.path.join(dirpath, filename)
            loc = _estimate_loc(full_path)
            rel_path = rel_path.replace(os.sep, "/")
            results.append((rel_path, loc))
    return results


def greedy_balance(
    files: list[tuple[str, int]], shard_count: int
) -> list[list[tuple[str, int]]]:
    """Assign each file to the currently smallest shard (greedy).

    Files are processed in the order given — the caller is responsible for
    shuffling (or sorting by LOC) before calling to achieve the desired
    distribution strategy.
    """
    shards: list[list[tuple[str, int]]] = [[] for _ in range(shard_count)]
    totals = [0] * shard_count

    for filepath, loc in files:
        min_idx = min(range(shard_count), key=lambda i: totals[i])
        shards[min_idx].append((filepath, loc))
        totals[min_idx] += loc

    return shards


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate randomized test-file shards for ocode-test-review."
    )
    parser.add_argument(
        "--seed",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Seed for randomization (default: current date, YYYY-MM-DD)",
    )
    parser.add_argument(
        "--shards",
        type=int,
        default=6,
        help="Number of shards to split into (default: 6)",
    )
    parser.add_argument(
        "--max-loc-per-shard",
        type=int,
        default=None,
        help="If set, auto-increases shard count to keep per-shard LOC under this ceiling",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Override output directory (default: auto-create timestamped under Reviews/results/)",
    )
    args = parser.parse_args()

    if args.shards < 2:
        print("ERROR: --shards must be at least 2", file=sys.stderr)
        sys.exit(1)

    files = discover_test_files(TESTS_ROOT)
    if not files:
        print("ERROR: No test files found under", TESTS_ROOT, file=sys.stderr)
        sys.exit(1)

    total_loc = sum(loc for _, loc in files)

    shard_count = args.shards
    rng = random.Random(args.seed)
    rng.shuffle(files)

    if args.max_loc_per_shard is not None:
        max_single_file = max(loc for _, loc in files) if files else 0
        if max_single_file > args.max_loc_per_shard:
            print(f"WARNING: Largest test file is {max_single_file} LOC, "
                  f"exceeds --max-loc-per-shard={args.max_loc_per_shard}. "
                  f"Some shards will overshoot the cap.")

        for attempt in range(50):
            shards = greedy_balance(files, shard_count)
            max_shard_loc = max(sum(loc for _, loc in shard) for shard in shards)
            if max_shard_loc <= args.max_loc_per_shard:
                break
            shard_count += 1
        else:
            print(f"WARNING: Could not satisfy --max-loc-per-shard={args.max_loc_per_shard} "
                  f"after 50 attempts. Final shard_count={shard_count}, "
                  f"max shard LOC={max_shard_loc}")

        if shard_count > args.shards:
            print(f"NOTE: --max-loc-per-shard={args.max_loc_per_shard} increased shards "
                  f"from {args.shards} to {shard_count} (total LOC: {total_loc})")
    else:
        shards = greedy_balance(files, shard_count)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_dir = args.output or os.path.join(
        PROJECT_ROOT, "Reviews", "results", f"{timestamp}_test-review"
    )
    os.makedirs(output_dir, exist_ok=True)

    shard_data: dict[str, dict[str, object]] = {}
    for i, shard in enumerate(shards):
        sid = f"{i + 1:02d}"
        file_paths = [path for path, _ in shard]
        shard_data[sid] = {
            "files": file_paths,
            "file_count": len(file_paths),
            "loc_estimate": sum(loc for _, loc in shard),
        }

    config = {
        "seed": args.seed,
        "shard_count": shard_count,
        "timestamp": datetime.now().isoformat(),
        "total_files": len(files),
        "total_loc_estimate": total_loc,
        "shards": shard_data,
    }

    config_path = os.path.join(output_dir, "SHARD_CONFIG.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    print(f"Output directory: {output_dir}")
    print(f"Seed: {args.seed}  |  Shards: {shard_count}")
    print(f"Total files: {len(files)}  |  Est LOC: {total_loc}")
    for sid, sdata in shard_data.items():
        fc = sdata["file_count"]
        loc = sdata["loc_estimate"]
        print(f"  Shard {sid}: {fc} files, ~{loc} LOC")


if __name__ == "__main__":
    main()
