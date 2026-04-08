"""Lines of code counter for Starship Battles.

Usage:
    python scripts/loc.py             # simple summary
    python scripts/loc.py --detailed  # JSON output with per-section, per-type breakdowns
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"__pycache__", ".git", "venv", ".venv", "node_modules", ".VSCodeCounter"}
SKIP_FILES = {"test_history.json"}

# -- Production sections (subdirs of game/) ----------------------------------
PROD_SECTIONS = ["ai", "assets", "core", "data", "engine", "research", "simulation", "strategy", "ui"]

# -- Additional source dirs/files outside game/ ------------------------------
EXTRA_SOURCE_DIRS = ["scripts"]
EXTRA_SOURCE_FILES = ["launcher.py"]

# -- Test sections ------------------------------------------------------------
TEST_SECTIONS = {
    "tests/unit": "tests/unit",
    "tests/integration": "tests/integration",
    "tests/regression": "tests/regression",
    "tests/performance": "tests/performance",
    "tests/repro_issues": "tests/repro_issues",
    "tests/fixtures": "tests/fixtures",
    "tests/infrastructure": "tests/infrastructure",
}
EXTRA_TEST_DIRS = ["combat_lab"]
EXTRA_TEST_FILES = ["conftest.py"]

# -- File type groups ---------------------------------------------------------
PY_EXTS = {".py"}
JSON_EXTS = {".json"}


def _should_skip(path: Path) -> bool:
    """Return True if the file should be excluded from counting."""
    if any(part in SKIP_DIRS for part in path.parts):
        return True
    if path.name in SKIP_FILES:
        return True
    if path.suffix == ".pyc":
        return True
    # Skip output directories under test paths
    if "output" in path.parts:
        return True
    return False


def count_lines_by_type(path: Path) -> dict[str, tuple[int, int]]:
    """Count lines under path grouped by file type.

    Returns dict with keys 'py', 'json', 'other', each mapping to (lines, files).
    """
    counts: dict[str, list[int]] = {"py": [0, 0], "json": [0, 0], "other": [0, 0]}

    if path.is_file():
        if _should_skip(path):
            return {k: tuple(v) for k, v in counts.items()}
        bucket = "py" if path.suffix in PY_EXTS else "json" if path.suffix in JSON_EXTS else "other"
        try:
            lines = sum(1 for _ in path.open(encoding="utf-8", errors="replace"))
            counts[bucket] = [lines, 1]
        except OSError:
            pass
        return {k: tuple(v) for k, v in counts.items()}

    for f in path.rglob("*"):
        if not f.is_file() or _should_skip(f):
            continue
        bucket = "py" if f.suffix in PY_EXTS else "json" if f.suffix in JSON_EXTS else "other"
        try:
            lines = sum(1 for _ in f.open(encoding="utf-8", errors="replace"))
            counts[bucket][0] += lines
            counts[bucket][1] += 1
        except OSError:
            pass

    return {k: tuple(v) for k, v in counts.items()}


def count_py_lines(path: Path) -> tuple[int, int]:
    """Return (lines, file_count) for all .py files under path."""
    c = count_lines_by_type(path)
    return c["py"]


def count_single_file(path: Path) -> tuple[int, int]:
    """Return (lines, 1) for a single .py file, or (0, 0) if missing."""
    if not path.exists():
        return 0, 0
    try:
        lines = sum(1 for _ in path.open(encoding="utf-8", errors="replace"))
        return lines, 1
    except OSError:
        return 0, 0


def count_top_level_files(directory: Path) -> dict[str, tuple[int, int]]:
    """Count lines for files directly in directory (not subdirs)."""
    counts: dict[str, list[int]] = {"py": [0, 0], "json": [0, 0], "other": [0, 0]}
    for f in directory.iterdir():
        if not f.is_file() or _should_skip(f):
            continue
        bucket = "py" if f.suffix in PY_EXTS else "json" if f.suffix in JSON_EXTS else "other"
        try:
            lines = sum(1 for _ in f.open(encoding="utf-8", errors="replace"))
            counts[bucket][0] += lines
            counts[bucket][1] += 1
        except OSError:
            pass
    return {k: tuple(v) for k, v in counts.items()}


def fmt(n: int) -> str:
    return f"{n:,}"


def _add_counts(a: dict[str, tuple[int, int]], b: dict[str, tuple[int, int]]) -> dict[str, tuple[int, int]]:
    """Sum two count dicts together."""
    return {k: (a[k][0] + b[k][0], a[k][1] + b[k][1]) for k in ("py", "json", "other")}


def _zero_counts() -> dict[str, tuple[int, int]]:
    return {"py": (0, 0), "json": (0, 0), "other": (0, 0)}


def _total_lines(c: dict[str, tuple[int, int]]) -> int:
    return c["py"][0] + c["json"][0] + c["other"][0]


def _total_files(c: dict[str, tuple[int, int]]) -> int:
    return c["py"][1] + c["json"][1] + c["other"][1]


def build_detailed() -> dict:
    """Build full detailed breakdown and return as a dict."""
    result: dict = {"production": {}, "tests": {}}

    # Production: game/ subsections
    for section in PROD_SECTIONS:
        p = ROOT / "game" / section
        if p.is_dir():
            result["production"][f"game/{section}"] = count_lines_by_type(p)

    # game/ top-level files
    result["production"]["game/ (top-level)"] = count_top_level_files(ROOT / "game")

    # Extra source dirs
    for d in EXTRA_SOURCE_DIRS:
        p = ROOT / d
        if p.is_dir():
            result["production"][f"{d}/"] = count_lines_by_type(p)

    # Extra source files
    for f in EXTRA_SOURCE_FILES:
        p = ROOT / f
        if p.exists():
            result["production"][f] = count_lines_by_type(p)

    # Tests: tests/ subsections
    for label, relpath in TEST_SECTIONS.items():
        p = ROOT / relpath
        if p.is_dir():
            result["tests"][label] = count_lines_by_type(p)

    # tests/ top-level files
    result["tests"]["tests/ (top-level)"] = count_top_level_files(ROOT / "tests")

    # Extra test dirs
    for d in EXTRA_TEST_DIRS:
        p = ROOT / d
        if p.is_dir():
            result["tests"][f"{d}/"] = count_lines_by_type(p)

    # Extra test files
    for f in EXTRA_TEST_FILES:
        p = ROOT / f
        if p.exists():
            result["tests"][f] = count_lines_by_type(p)

    return result


def print_detailed():
    """Print detailed JSON breakdown for the /loc skill."""
    data = build_detailed()
    print(json.dumps(data, indent=2))


def print_simple():
    """Print the original simple summary."""
    rows_source = []
    rows_test = []

    for d in ["game"] + EXTRA_SOURCE_DIRS:
        p = ROOT / d
        if p.is_dir():
            lines, files = count_py_lines(p)
            rows_source.append((f"Source ({d}/)", lines, files))

    for f in EXTRA_SOURCE_FILES:
        lines, files = count_single_file(ROOT / f)
        if files:
            rows_source.append((f"Source ({f})", lines, files))

    for d in list(TEST_SECTIONS.values()) + EXTRA_TEST_DIRS:
        p = ROOT / d
        if p.is_dir():
            label = d.replace("tests/", "") if d.startswith("tests/") else d
            lines, files = count_py_lines(p)
            if lines:
                rows_test.append((f"Tests ({label}/)", lines, files))

    # tests/ top-level
    tl_lines, tl_files = 0, 0
    for f in (ROOT / "tests").iterdir():
        if f.is_file() and f.suffix == ".py":
            try:
                tl_lines += sum(1 for _ in f.open(encoding="utf-8", errors="replace"))
                tl_files += 1
            except OSError:
                pass
    if tl_lines:
        rows_test.append(("Tests (tests/ top-level)", tl_lines, tl_files))

    for f in EXTRA_TEST_FILES:
        lines, files = count_single_file(ROOT / f)
        if files:
            rows_test.append((f"Tests ({f})", lines, files))

    src_lines = sum(r[1] for r in rows_source)
    src_files = sum(r[2] for r in rows_source)
    test_lines = sum(r[1] for r in rows_test)
    test_files = sum(r[2] for r in rows_test)
    grand_lines = src_lines + test_lines
    grand_files = src_files + test_files

    col_w = 40
    num_w = 10
    file_w = 12

    def row(label, lines, files):
        f_label = "file" if files == 1 else "files"
        print(f"  {label:<{col_w}} {fmt(lines):>{num_w}}  {fmt(files):>{file_w}} {f_label}")

    bar = "=" * (col_w + num_w + file_w + 12)
    thin = "-" * (col_w + num_w + file_w + 12)

    print()
    print("  Starship Battles - Lines of Code")
    print(f"  {bar}")

    for r in rows_source:
        row(*r)
    print(f"  {thin}")
    row("Total source code", src_lines, src_files)

    print()
    for r in rows_test:
        row(*r)
    print(f"  {thin}")
    row("Total test code", test_lines, test_files)

    print(f"\n  {bar}")
    row("GRAND TOTAL", grand_lines, grand_files)

    if src_lines:
        ratio = test_lines / src_lines
        print(f"\n  Test:Source ratio  {ratio:.2f}:1")
    print()


def main():
    if "--detailed" in sys.argv:
        print_detailed()
    else:
        print_simple()


if __name__ == "__main__":
    main()
