"""Lines of code counter for Starship Battles."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKIP_DIRS = {"__pycache__", ".git", "venv", ".venv", "node_modules", ".VSCodeCounter"}

SOURCE_DIRS = ["game", "scripts"]
SOURCE_FILES = ["launcher.py"]

TEST_DIRS = ["tests", "simulation_tests", "test_framework"]
TEST_FILES = ["conftest.py"]


def count_py_lines(path: Path) -> tuple[int, int]:
    """Return (lines, file_count) for all .py files under path, skipping SKIP_DIRS."""
    total_lines = 0
    total_files = 0
    for f in path.rglob("*.py"):
        if any(part in SKIP_DIRS for part in f.parts):
            continue
        try:
            total_lines += sum(1 for _ in f.open(encoding="utf-8", errors="replace"))
            total_files += 1
        except OSError:
            pass
    return total_lines, total_files


def count_single_file(path: Path) -> tuple[int, int]:
    """Return (lines, 1) for a single file, or (0, 0) if missing."""
    if not path.exists():
        return 0, 0
    try:
        lines = sum(1 for _ in path.open(encoding="utf-8", errors="replace"))
        return lines, 1
    except OSError:
        return 0, 0


def fmt(n: int) -> str:
    return f"{n:,}"


def main():
    rows_source = []
    rows_test = []

    for d in SOURCE_DIRS:
        p = ROOT / d
        if p.is_dir():
            lines, files = count_py_lines(p)
            rows_source.append((f"Source ({d}/)", lines, files))

    for f in SOURCE_FILES:
        lines, files = count_single_file(ROOT / f)
        if files:
            rows_source.append((f"Source ({f})", lines, files))

    for d in TEST_DIRS:
        p = ROOT / d
        if p.is_dir():
            lines, files = count_py_lines(p)
            rows_test.append((f"Tests ({d}/)", lines, files))

    for f in TEST_FILES:
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


if __name__ == "__main__":
    main()
