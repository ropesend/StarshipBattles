"""
Migration script: Replace ai_strategy with movement_policy + targeting_policy in ship JSON files.

Scans data/designs/, combat_lab/data/ships/, tests/unit/data/ships/ for JSON files
with an "ai_strategy" key and replaces it with the corresponding movement_policy
and targeting_policy values.
"""

import json
import os
import sys
from collections import OrderedDict

STRATEGY_TO_POLICIES = {
    "standard_ranged": ("kite_max", "standard"),
    "optimal_range": ("kite_optimal", "standard"),
    "sniper": ("kite_max", "sniper"),
    "brawler": ("brawl_close", "brawler"),
    "interceptor": ("kite_medium", "anti_fighter"),
    "hit_and_run": ("strafe_run", "standard"),
    "kamikaze": ("ramming_speed", "brawler"),
    "cautious": ("hold_position", "self_defense"),
    "test_stationary_fire": ("test_stationary", "standard"),
    "test_do_nothing": ("test_do_nothing", "standard"),
    "test_straight_line": ("test_straight_line", "standard"),
    "test_rotate_right": ("test_rotate_right", "standard"),
    "test_rotate_left": ("test_rotate_left", "standard"),
    "test_erratic": ("test_erratic", "standard"),
    "test_erratic_leashed": ("test_erratic_leashed", "standard"),
    # Bare behavior names used in some test JSONs
    "do_nothing": ("test_do_nothing", "standard"),
    "straight_line": ("test_straight_line", "standard"),
    "erratic": ("test_erratic", "standard"),
    "rotate_only": ("test_rotate_right", "standard"),
    "orbit": ("test_erratic", "standard"),
    "stationary_fire": ("test_stationary", "standard"),
    # Additional values found in tests/unit/data/ships/
    "test_orbit_target": ("test_erratic", "standard"),
    "test_erratic_maneuver": ("test_erratic", "standard"),
}

DEFAULT_POLICIES = ("kite_max", "standard")

SCAN_DIRS = [
    "data/designs",
    "combat_lab/data/ships",
    "tests/unit/data/ships",
]


def find_json_files(base_dir):
    """Recursively find all .json files in a directory."""
    results = []
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.endswith(".json"):
                results.append(os.path.join(root, f))
    return results


def migrate_file(filepath):
    """Migrate a single JSON file. Returns (migrated: bool, old_strategy: str or None)."""
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    try:
        data = json.loads(raw, object_pairs_hook=OrderedDict)
    except json.JSONDecodeError as e:
        print(f"  WARNING: Could not parse {filepath}: {e}")
        return False, None

    if "ai_strategy" not in data:
        return False, None

    old_strategy = data["ai_strategy"]

    if old_strategy in STRATEGY_TO_POLICIES:
        movement, targeting = STRATEGY_TO_POLICIES[old_strategy]
    else:
        movement, targeting = DEFAULT_POLICIES
        print(f"  WARNING: Unknown ai_strategy '{old_strategy}' in {filepath}, using default ({movement}, {targeting})")

    # Build new ordered dict with movement_policy and targeting_policy replacing ai_strategy
    new_data = OrderedDict()
    for key, value in data.items():
        if key == "ai_strategy":
            new_data["movement_policy"] = movement
            new_data["targeting_policy"] = targeting
        else:
            new_data[key] = value

    # Detect indent from original file
    indent = 2
    # Check if original uses 4-space indent
    for line in raw.split("\n")[1:5]:
        stripped = line.lstrip()
        if stripped and line != stripped:
            leading = len(line) - len(stripped)
            if leading >= 1:
                indent = leading
                break

    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(new_data, f, indent=indent, ensure_ascii=False)
        f.write("\n")

    return True, old_strategy


def main():
    total_migrated = 0
    total_skipped = 0
    total_files = 0
    warnings = []

    for scan_dir in SCAN_DIRS:
        if not os.path.isdir(scan_dir):
            print(f"WARNING: Directory {scan_dir} does not exist, skipping.")
            continue

        json_files = find_json_files(scan_dir)
        print(f"\nScanning {scan_dir}: {len(json_files)} JSON files found")

        for filepath in sorted(json_files):
            total_files += 1
            migrated, old_val = migrate_file(filepath)
            if migrated:
                total_migrated += 1
                print(f"  MIGRATED: {filepath} ({old_val} -> {STRATEGY_TO_POLICIES.get(old_val, DEFAULT_POLICIES)})")
            else:
                total_skipped += 1

    print(f"\n{'='*60}")
    print(f"Migration Summary:")
    print(f"  Total files scanned: {total_files}")
    print(f"  Files migrated: {total_migrated}")
    print(f"  Files skipped (no ai_strategy): {total_skipped}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
