"""File-level regression guard for PROJ-443.

Asserts every on-disk ``test_*.py`` under ``tests/`` that defines at
least one test item is reachable by pytest's collection. Prevents
future ``norecursedirs`` / ``--ignore`` / ``python_files`` regressions
that would silently drop test files from the canonical sharded run.

PROJ-443 root cause this guard catches: ``pytest.ini`` had ``data``,
``Assets``, and ``combat_lab`` in ``norecursedirs``, which match
directory **basenames at any depth** (per ``_pytest/main.py:455-458``).
Three real test directories collided with those tokens — ``tests/unit/
strategy/data/`` (95 files), ``tests/unit/combat_lab/`` (24), and the
remaining `data` / `assets` clusters — hiding 126 test files (1952
tests) from the sharded suite for an extended period.

SCOPE NOTES:
1. **File-level only.** A ``python_functions`` / ``python_classes`` /
   collection-hook drop that silently filters individual test items
   out of a still-collected file will NOT be caught. That's a
   different class of drift than this guard targets.
2. **Test-bearing files only.** A ``test_*.py`` under ``tests/`` that
   defines zero test items (no ``def test_`` and no ``class Test``)
   is structurally a fixture / scaffold module — pytest collects it
   silently and emits no node-ids, so it cannot be intersected here.
   Such files are excluded via an AST scan; they are not the target
   of this guard.

Implementation: shells out to ``pytest tests/ --collect-only -q -n 0
--no-header`` from the repo root and intersects the resulting file
set against the AST-filtered on-disk set. The 120-second timeout
matches a typical "warm" collection at this suite's current size;
if collection grows past that, raise the timeout rather than
tightening the guard.
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_TESTS_DIR = _REPO_ROOT / "tests"


def _file_defines_test_items(path: Path) -> bool:
    """True if the file has at least one ``test_*`` function OR ``Test*`` class.

    Uses ``ast.parse`` so a syntactically-broken file fails noisily
    (which itself would surface as a collection error elsewhere).
    """
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        # Surface as a real collection issue rather than silently masking.
        return True
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            return True
        if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            return True
    return False


def test_every_test_bearing_file_is_collected() -> None:
    """Every on-disk ``test_*.py`` with test items is in pytest's collection."""
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest", "tests/",
            "--collect-only", "-q", "--no-header", "-n", "0",
        ],
        capture_output=True,
        text=True,
        cwd=str(_REPO_ROOT),
        timeout=120,
    )

    # The collection output has lines like ``tests/foo/test_bar.py::test_baz``.
    collected_ids = {
        line.strip()
        for line in result.stdout.splitlines()
        if "::" in line
    }
    collected_files = {nid.split("::", 1)[0] for nid in collected_ids}

    on_disk_with_items = {
        str(p.relative_to(_REPO_ROOT)).replace("\\", "/")
        for p in _TESTS_DIR.rglob("test_*.py")
        if _file_defines_test_items(p)
    }
    missing = on_disk_with_items - collected_files
    assert not missing, (
        f"{len(missing)} on-disk test_*.py files with at least one test item "
        "are not collected by pytest. This usually means a `norecursedirs` "
        "entry in pytest.ini matches a directory basename under `tests/` "
        "(the PROJ-443 root cause), or a new `--ignore` pattern caught a real "
        "test file, or `python_files` was narrowed. First few missing: "
        f"{sorted(missing)[:10]}"
    )
