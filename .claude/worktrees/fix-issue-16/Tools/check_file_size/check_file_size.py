"""Enforce the 500-LOC ceiling on production-source files under `game/`.

Established by PROJ-309 (2026-04-27). See `CLAUDE.md` "Code Quality" and
`docs/03_CONVENTIONS.md` §2.3 File Size for the rule.

Usage::

    python Tools/check_file_size.py            # run from repo root
    python Tools/check_file_size.py --max 600  # custom ceiling
    python Tools/check_file_size.py --quiet    # only print on violations

Exits with code 0 when every production source file is at or under the
ceiling, code 1 when any file exceeds it. Test files (anything under
`tests/`, `combat_lab/`, `simulation_tests/`) are exempt — long test files
are often legitimate per the convention.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


DEFAULT_MAX_LOC = 500
PRODUCTION_ROOT = "game"


def count_loc(path: Path) -> int:
    """Return the line count of ``path`` (matches ``wc -l``)."""
    with path.open("r", encoding="utf-8", errors="replace") as fp:
        return sum(1 for _ in fp)


def find_violations(repo_root: Path, max_loc: int) -> list[tuple[Path, int]]:
    """Return [(path, loc)] for every production .py file over the ceiling."""
    production_dir = repo_root / PRODUCTION_ROOT
    if not production_dir.is_dir():
        raise SystemExit(
            f"error: production directory {production_dir} does not exist; "
            f"run this script from the repo root."
        )

    violations: list[tuple[Path, int]] = []
    for path in production_dir.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        loc = count_loc(path)
        if loc > max_loc:
            violations.append((path.relative_to(repo_root), loc))
    violations.sort(key=lambda pair: pair[1], reverse=True)
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--max",
        type=int,
        default=DEFAULT_MAX_LOC,
        help=f"line ceiling (default: {DEFAULT_MAX_LOC})",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="only print on violations",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    violations = find_violations(repo_root, args.max)

    if not violations:
        if not args.quiet:
            print(f"OK: every file under {PRODUCTION_ROOT}/ is at or below {args.max} LOC.")
        return 0

    print(f"FAIL: {len(violations)} file(s) over {args.max} LOC:")
    for path, loc in violations:
        print(f"  {loc:5d}  {path}")
    print(
        "\nSee docs/03_CONVENTIONS.md §2.3 File Size and PROJ-309 for the rule. "
        "Split into single-responsibility sub-modules; use a re-export shim if many "
        "callers exist."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
