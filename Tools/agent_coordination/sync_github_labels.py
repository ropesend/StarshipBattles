"""Sync .github/labels.yml to the GitHub repository via gh CLI.

Idempotent: creates labels that don't exist, updates labels whose color or
description has drifted, leaves matching labels alone. Does NOT delete labels
that are present on GitHub but absent from labels.yml — that requires the
--prune flag.

Usage:
    python Tools/agent_coordination/sync_github_labels.py
    python Tools/agent_coordination/sync_github_labels.py --prune  # also delete extras
    python Tools/agent_coordination/sync_github_labels.py --dry-run

Requires: gh CLI installed and authenticated, a `repo` remote (origin) on the
repository the labels.yml is for.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml  # type: ignore[import-untyped]

REPO_ROOT = Path(__file__).resolve().parents[2]
LABELS_FILE = REPO_ROOT / ".github" / "labels.yml"


def gh(*args: str, capture: bool = True) -> subprocess.CompletedProcess[str]:
    """Invoke gh; raise on non-zero unless capture=False."""
    return subprocess.run(
        ["gh", *args],
        check=capture,
        capture_output=capture,
        text=True,
    )


def list_remote_labels() -> dict[str, dict[str, str]]:
    """Return current labels keyed by name."""
    out = gh("label", "list", "--limit", "200", "--json", "name,color,description").stdout
    return {row["name"]: row for row in json.loads(out)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prune", action="store_true", help="Delete labels on GitHub that are not in labels.yml")
    parser.add_argument("--dry-run", action="store_true", help="Print what would change without modifying GitHub")
    args = parser.parse_args()

    if not LABELS_FILE.exists():
        print(f"ERROR: {LABELS_FILE} does not exist", file=sys.stderr)
        return 2

    desired = yaml.safe_load(LABELS_FILE.read_text(encoding="utf-8"))
    if not isinstance(desired, list):
        print("ERROR: labels.yml must be a YAML list of {name, color, description} objects", file=sys.stderr)
        return 2

    desired_by_name = {entry["name"]: entry for entry in desired}
    remote = list_remote_labels()

    create: list[dict[str, str]] = []
    update: list[dict[str, str]] = []
    for name, entry in desired_by_name.items():
        if name not in remote:
            create.append(entry)
            continue
        r = remote[name]
        if r.get("color", "").lower() != entry["color"].lower() or r.get("description", "") != entry.get("description", ""):
            update.append(entry)

    delete: list[str] = []
    if args.prune:
        delete = [name for name in remote if name not in desired_by_name]

    print(f"Plan: create {len(create)}, update {len(update)}, delete {len(delete)} (prune={args.prune})")
    if args.dry_run:
        for e in create:
            print(f"  + create {e['name']} (#{e['color']})")
        for e in update:
            print(f"  ~ update {e['name']} (#{e['color']})")
        for n in delete:
            print(f"  - delete {n}")
        return 0

    for entry in create:
        print(f"  + creating {entry['name']}")
        gh("label", "create", entry["name"],
           "--color", entry["color"],
           "--description", entry.get("description", ""))
    for entry in update:
        print(f"  ~ updating {entry['name']}")
        gh("label", "edit", entry["name"],
           "--color", entry["color"],
           "--description", entry.get("description", ""))
    for name in delete:
        print(f"  - deleting {name}")
        gh("label", "delete", name, "--yes")

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
