"""Lines of code counter for Starship Battles.

Usage:
    python Tools/loc/loc.py             # simple summary
    python Tools/loc/loc.py --detailed  # JSON output with per-section, per-type breakdowns
"""

import json
import sys
from pathlib import Path

try:
    import tiktoken as _tiktoken
except ModuleNotFoundError as exc:
    missing_name = getattr(exc, "name", None)
    if missing_name != "tiktoken" and "No module named 'tiktoken'" not in str(exc):
        raise
    _tiktoken = None

# o200k_base matches GPT-4o / approximates Claude tokenization.
_ENCODING = _tiktoken.get_encoding("o200k_base") if _tiktoken is not None else None


class MissingLocDependencyError(RuntimeError):
    """Raised when the LOC tool cannot perform an exact token count."""


def _missing_tiktoken_message() -> str:
    requirements_file = ROOT / "requirements-dev.txt"
    return (
        "Missing Python dependency: tiktoken\n"
        "Install the development requirements for this checkout:\n"
        f'  python -m pip install -r "{requirements_file}"'
    )


def _count_tokens(text: str) -> int:
    if _ENCODING is None:
        raise MissingLocDependencyError(_missing_tiktoken_message())
    return len(_ENCODING.encode(text, disallowed_special=()))


def _find_project_root() -> Path:
    """Find project root by looking for game/ and data/ directories."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "data").is_dir():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


ROOT = _find_project_root()
SKIP_DIRS = {
    "__pycache__",
    ".git",
    "venv",
    ".venv",
    "node_modules",
    ".VSCodeCounter",
    "test_history",
    "_ignore",  # docs/_ignore is user scratch space; never count it
}
SKIP_FILES = {"test_history.json", "test_history.json.migrated"}

# -- Production sections (subdirs of game/) ----------------------------------
PROD_SECTIONS = ["ai", "assets", "core", "data", "engine", "research", "simulation", "strategy", "ui"]

# -- Additional source dirs/files outside game/ ------------------------------
EXTRA_SOURCE_DIRS = []
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

# -- Documentation sections --------------------------------------------------
DOC_SECTIONS = {
    "docs/guides": "docs/guides",
    "docs/systems": "docs/systems",
}
EXTRA_DOC_FILES = ["AGENTS.md", "CLAUDE.md"]

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


def _measure_file(path: Path) -> tuple[int, int]:
    """Return (lines, tokens) for a single file, or (0, 0) on read failure."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0, 0
    lines = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
    return lines, _count_tokens(text)


def count_lines_by_type(path: Path) -> dict[str, tuple[int, int, int]]:
    """Count lines and tokens under path grouped by file type.

    Returns dict with keys 'py', 'json', 'other', each mapping to (lines, tokens, files).
    """
    counts: dict[str, list[int]] = {"py": [0, 0, 0], "json": [0, 0, 0], "other": [0, 0, 0]}

    if path.is_file():
        if _should_skip(path):
            return {k: tuple(v) for k, v in counts.items()}
        bucket = "py" if path.suffix in PY_EXTS else "json" if path.suffix in JSON_EXTS else "other"
        lines, tokens = _measure_file(path)
        counts[bucket] = [lines, tokens, 1]
        return {k: tuple(v) for k, v in counts.items()}

    for f in path.rglob("*"):
        if not f.is_file() or _should_skip(f):
            continue
        bucket = "py" if f.suffix in PY_EXTS else "json" if f.suffix in JSON_EXTS else "other"
        lines, tokens = _measure_file(f)
        counts[bucket][0] += lines
        counts[bucket][1] += tokens
        counts[bucket][2] += 1

    return {k: tuple(v) for k, v in counts.items()}


def count_py_lines(path: Path) -> tuple[int, int, int]:
    """Return (lines, tokens, file_count) for all .py files under path."""
    c = count_lines_by_type(path)
    return c["py"]


def count_all_lines(path: Path) -> tuple[int, int, int]:
    """Return (lines, tokens, file_count) summed across every file type under path."""
    c = count_lines_by_type(path)
    return _total_lines(c), _total_tokens(c), _total_files(c)


def count_single_file(path: Path) -> tuple[int, int, int]:
    """Return (lines, tokens, 1) for a single file, or (0, 0, 0) if missing."""
    if not path.exists():
        return 0, 0, 0
    lines, tokens = _measure_file(path)
    return lines, tokens, 1


def count_top_level_files(directory: Path) -> dict[str, tuple[int, int, int]]:
    """Count lines and tokens for files directly in directory (not subdirs)."""
    counts: dict[str, list[int]] = {"py": [0, 0, 0], "json": [0, 0, 0], "other": [0, 0, 0]}
    for f in directory.iterdir():
        if not f.is_file() or _should_skip(f):
            continue
        bucket = "py" if f.suffix in PY_EXTS else "json" if f.suffix in JSON_EXTS else "other"
        lines, tokens = _measure_file(f)
        counts[bucket][0] += lines
        counts[bucket][1] += tokens
        counts[bucket][2] += 1
    return {k: tuple(v) for k, v in counts.items()}


def fmt(n: int) -> str:
    return f"{n:,}"


def _add_counts(
    a: dict[str, tuple[int, int, int]], b: dict[str, tuple[int, int, int]]
) -> dict[str, tuple[int, int, int]]:
    """Sum two count dicts together."""
    return {k: (a[k][0] + b[k][0], a[k][1] + b[k][1], a[k][2] + b[k][2]) for k in ("py", "json", "other")}


def _zero_counts() -> dict[str, tuple[int, int, int]]:
    return {"py": (0, 0, 0), "json": (0, 0, 0), "other": (0, 0, 0)}


def _total_lines(c: dict[str, tuple[int, int, int]]) -> int:
    return c["py"][0] + c["json"][0] + c["other"][0]


def _total_tokens(c: dict[str, tuple[int, int, int]]) -> int:
    return c["py"][1] + c["json"][1] + c["other"][1]


def _total_files(c: dict[str, tuple[int, int, int]]) -> int:
    return c["py"][2] + c["json"][2] + c["other"][2]


def build_detailed() -> dict:
    """Build full detailed breakdown and return as a dict."""
    result: dict = {"production": {}, "tests": {}, "docs": {}}

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

    # Docs: docs/ subsections
    for label, relpath in DOC_SECTIONS.items():
        p = ROOT / relpath
        if p.is_dir():
            result["docs"][label] = count_lines_by_type(p)

    # docs/ top-level files
    if (ROOT / "docs").is_dir():
        result["docs"]["docs/ (top-level)"] = count_top_level_files(ROOT / "docs")

    # Extra doc files
    for f in EXTRA_DOC_FILES:
        p = ROOT / f
        if p.exists():
            result["docs"][f] = count_lines_by_type(p)

    return result


def print_detailed() -> None:
    """Print detailed JSON breakdown for the /loc skill."""
    data = build_detailed()
    print(json.dumps(data, indent=2))


def print_simple() -> None:
    """Print the original simple summary."""
    rows_source = []
    rows_test = []

    for d in ["game"] + EXTRA_SOURCE_DIRS:
        p = ROOT / d
        if p.is_dir():
            lines, tokens, files = count_py_lines(p)
            rows_source.append((f"Source ({d}/)", lines, tokens, files))

    for f in EXTRA_SOURCE_FILES:
        lines, tokens, files = count_single_file(ROOT / f)
        if files:
            rows_source.append((f"Source ({f})", lines, tokens, files))

    for d in list(TEST_SECTIONS.values()) + EXTRA_TEST_DIRS:
        p = ROOT / d
        if p.is_dir():
            label = d.replace("tests/", "") if d.startswith("tests/") else d
            lines, tokens, files = count_py_lines(p)
            if lines:
                rows_test.append((f"Tests ({label}/)", lines, tokens, files))

    # tests/ top-level
    tl_lines, tl_tokens, tl_files = 0, 0, 0
    for f in (ROOT / "tests").iterdir():
        if f.is_file() and f.suffix == ".py":
            lines, tokens = _measure_file(f)
            tl_lines += lines
            tl_tokens += tokens
            tl_files += 1
    if tl_lines:
        rows_test.append(("Tests (tests/ top-level)", tl_lines, tl_tokens, tl_files))

    for f in EXTRA_TEST_FILES:
        lines, tokens, files = count_single_file(ROOT / f)
        if files:
            rows_test.append((f"Tests ({f})", lines, tokens, files))

    rows_doc = []
    for d in DOC_SECTIONS.values():
        p = ROOT / d
        if p.is_dir():
            label = d.replace("docs/", "") if d.startswith("docs/") else d
            lines, tokens, files = count_all_lines(p)
            if lines:
                rows_doc.append((f"Docs ({label}/)", lines, tokens, files))

    # docs/ top-level
    dl_lines, dl_tokens, dl_files = 0, 0, 0
    docs_root = ROOT / "docs"
    if docs_root.is_dir():
        for f in docs_root.iterdir():
            if f.is_file() and not _should_skip(f):
                lines, tokens = _measure_file(f)
                dl_lines += lines
                dl_tokens += tokens
                dl_files += 1
    if dl_lines:
        rows_doc.append(("Docs (docs/ top-level)", dl_lines, dl_tokens, dl_files))

    for f in EXTRA_DOC_FILES:
        lines, tokens, files = count_single_file(ROOT / f)
        if files:
            rows_doc.append((f"Docs ({f})", lines, tokens, files))

    src_lines = sum(r[1] for r in rows_source)
    src_tokens = sum(r[2] for r in rows_source)
    src_files = sum(r[3] for r in rows_source)
    test_lines = sum(r[1] for r in rows_test)
    test_tokens = sum(r[2] for r in rows_test)
    test_files = sum(r[3] for r in rows_test)
    doc_lines = sum(r[1] for r in rows_doc)
    doc_tokens = sum(r[2] for r in rows_doc)
    doc_files = sum(r[3] for r in rows_doc)
    grand_lines = src_lines + test_lines + doc_lines
    grand_tokens = src_tokens + test_tokens + doc_tokens
    grand_files = src_files + test_files + doc_files

    col_w = 40
    num_w = 10
    tok_w = 14
    file_w = 12

    def header() -> None:
        print(
            f"  {'':<{col_w}} {'LOC':>{num_w}}  {'Tokens':>{tok_w}}  {'Files':>{file_w}}"
        )

    def row(label: str, lines: int, tokens: int, files: int) -> None:
        f_label = "file" if files == 1 else "files"
        print(
            f"  {label:<{col_w}} {fmt(lines):>{num_w}}  {fmt(tokens):>{tok_w}}  "
            f"{fmt(files):>{file_w}} {f_label}"
        )

    width = col_w + num_w + tok_w + file_w + 14
    bar = "=" * width
    thin = "-" * width

    print()
    print("  Starship Battles - Lines of Code")
    print(f"  {bar}")
    header()
    print(f"  {thin}")

    for r in rows_source:
        row(*r)
    print(f"  {thin}")
    row("Total source code", src_lines, src_tokens, src_files)

    print()
    for r in rows_test:
        row(*r)
    print(f"  {thin}")
    row("Total test code", test_lines, test_tokens, test_files)

    if rows_doc:
        print()
        for r in rows_doc:
            row(*r)
        print(f"  {thin}")
        row("Total documentation", doc_lines, doc_tokens, doc_files)

    print(f"\n  {bar}")
    row("GRAND TOTAL", grand_lines, grand_tokens, grand_files)

    if src_lines:
        ratio = test_lines / src_lines
        print(f"\n  Test:Source ratio  {ratio:.2f}:1")
    print()


def main() -> int:
    try:
        if "--detailed" in sys.argv:
            print_detailed()
        else:
            print_simple()
    except MissingLocDependencyError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
