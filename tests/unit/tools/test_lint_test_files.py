"""Smoke tests for ``Tools/lint_test_files.py`` (PROJ-326 Phase 1).

These tests don't import ``game.*`` (this file is a tools test). The tools-test
allowlist entry covers it, but if it ever escapes the allowlist it would be
self-flagged correctly — which is the right behavior.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


def _load_linter():
    """Load Tools/lint_test_files.py as a module without polluting sys.path."""
    repo_root = Path(__file__).resolve().parents[3]
    script = repo_root / "Tools" / "lint_test_files.py"
    spec = importlib.util.spec_from_file_location("lint_test_files_under_test", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["lint_test_files_under_test"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def linter():
    return _load_linter()


@pytest.fixture
def tmp_tree(tmp_path: Path) -> Path:
    """A fake repo-root-like tmp tree with a ``tests/`` subdir."""
    (tmp_path / "tests").mkdir()
    return tmp_path


def _write(tree: Path, rel: str, content: str) -> Path:
    p = tree / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

def test_zero_game_import_file_is_flagged(linter, tmp_tree, monkeypatch):
    """A test file with no `from game...` import is flagged."""
    monkeypatch.setattr(linter, "PROJECT_ROOT", tmp_tree)
    _write(tmp_tree, "tests/test_bad.py", "import os\n\ndef test_one():\n    assert True\n")

    violations, parse_errors = linter.lint(tmp_tree / "tests", [])

    assert parse_errors == []
    assert len(violations) == 1
    assert violations[0].as_posix() == "tests/test_bad.py"


def test_from_game_import_is_not_flagged(linter, tmp_tree, monkeypatch):
    monkeypatch.setattr(linter, "PROJECT_ROOT", tmp_tree)
    _write(
        tmp_tree,
        "tests/test_good.py",
        "from game.core.hex_math import HexCoord\n\ndef test_one():\n    assert HexCoord\n",
    )

    violations, parse_errors = linter.lint(tmp_tree / "tests", [])

    assert violations == []
    assert parse_errors == []


def test_from_game_bare_import_is_not_flagged(linter, tmp_tree, monkeypatch):
    """`from game import x` (without dotted submodule) is still a game import."""
    monkeypatch.setattr(linter, "PROJECT_ROOT", tmp_tree)
    _write(
        tmp_tree,
        "tests/test_bare_from.py",
        "from game import context\n\ndef test_one():\n    assert context\n",
    )

    violations, _ = linter.lint(tmp_tree / "tests", [])
    assert violations == []


def test_import_game_dotted_is_not_flagged(linter, tmp_tree, monkeypatch):
    monkeypatch.setattr(linter, "PROJECT_ROOT", tmp_tree)
    _write(
        tmp_tree,
        "tests/test_import_dotted.py",
        "import game.core.hex_math\n\ndef test_one():\n    assert game.core.hex_math\n",
    )

    violations, _ = linter.lint(tmp_tree / "tests", [])
    assert violations == []


def test_lookalike_module_name_is_flagged(linter, tmp_tree, monkeypatch):
    """`from somethinglikegame import X` MUST NOT count — top-level pkg must be exactly `game`."""
    monkeypatch.setattr(linter, "PROJECT_ROOT", tmp_tree)
    _write(
        tmp_tree,
        "tests/test_lookalike.py",
        "from somethinglikegame import X\n\ndef test_one():\n    assert X\n",
    )

    violations, _ = linter.lint(tmp_tree / "tests", [])
    assert len(violations) == 1
    assert violations[0].as_posix() == "tests/test_lookalike.py"


def test_importlib_import_module_with_game_string_is_not_flagged(
    linter, tmp_tree, monkeypatch,
):
    """PROJ-353A Tier-7 (T2.10): `importlib.import_module("game.foo")`
    is detected as a `game.*` dependency. The previous AST-based check
    only inspected `Import` / `ImportFrom` nodes, so a file using only
    dynamic imports would be flagged as zero-game-import."""
    monkeypatch.setattr(linter, "PROJECT_ROOT", tmp_tree)
    _write(
        tmp_tree,
        "tests/test_dynamic_import.py",
        "import importlib\n\n"
        "def test_one():\n"
        "    mod = importlib.import_module('game.core.hex_math')\n"
        "    assert mod\n",
    )

    violations, _ = linter.lint(tmp_tree / "tests", [])
    assert violations == []


def test_bare_import_module_with_game_string_is_not_flagged(
    linter, tmp_tree, monkeypatch,
):
    """PROJ-353A Tier-7 (T2.10): the `from importlib import import_module`
    form is also recognized."""
    monkeypatch.setattr(linter, "PROJECT_ROOT", tmp_tree)
    _write(
        tmp_tree,
        "tests/test_bare_dynamic_import.py",
        "from importlib import import_module\n\n"
        "def test_one():\n"
        "    mod = import_module('game.core.hex_math')\n"
        "    assert mod\n",
    )

    violations, _ = linter.lint(tmp_tree / "tests", [])
    assert violations == []


def test_runtime_built_module_name_is_still_flagged(
    linter, tmp_tree, monkeypatch,
):
    """PROJ-353A Tier-7 (T2.10): non-constant arguments to `import_module`
    (f-strings, variables) MUST NOT satisfy the check — that pattern
    hides the dependency from static analysis."""
    monkeypatch.setattr(linter, "PROJECT_ROOT", tmp_tree)
    _write(
        tmp_tree,
        "tests/test_dynamic_runtime.py",
        "import importlib\n\n"
        "def test_one():\n"
        "    name = 'core.hex_math'\n"
        "    mod = importlib.import_module(f'game.{name}')\n"
        "    assert mod\n",
    )

    violations, _ = linter.lint(tmp_tree / "tests", [])
    assert len(violations) == 1


def test_docstring_mentioning_game_is_still_flagged(linter, tmp_tree, monkeypatch):
    """AST-based, not regex: a docstring mentioning `import game` does NOT satisfy the check."""
    monkeypatch.setattr(linter, "PROJECT_ROOT", tmp_tree)
    _write(
        tmp_tree,
        "tests/test_docstring_only.py",
        '"""This file talks about `from game.core import X` but never imports it."""\n\nimport os\n\n'
        "def test_one():\n    assert True\n",
    )

    violations, _ = linter.lint(tmp_tree / "tests", [])
    assert len(violations) == 1


# ---------------------------------------------------------------------------
# Allowlist
# ---------------------------------------------------------------------------

def test_allowlist_exact_path_skips_file(linter, tmp_tree, monkeypatch):
    monkeypatch.setattr(linter, "PROJECT_ROOT", tmp_tree)
    _write(tmp_tree, "tests/test_allowed.py", "import os\n\ndef test_one():\n    assert True\n")

    violations, _ = linter.lint(tmp_tree / "tests", ["tests/test_allowed.py"])
    assert violations == []


def test_allowlist_glob_pattern_works(linter, tmp_tree, monkeypatch):
    monkeypatch.setattr(linter, "PROJECT_ROOT", tmp_tree)
    _write(tmp_tree, "tests/unit/tools/test_a.py", "import os\n")
    _write(tmp_tree, "tests/unit/tools/test_b.py", "import sys\n")
    _write(tmp_tree, "tests/test_other.py", "import os\n")

    violations, _ = linter.lint(tmp_tree / "tests", ["tests/unit/tools/**/*.py"])

    rels = {v.as_posix() for v in violations}
    assert rels == {"tests/test_other.py"}


def test_strict_mode_bypasses_allowlist(linter, tmp_tree, monkeypatch):
    """In strict mode every zero-game-import file is flagged regardless of allowlist."""
    monkeypatch.setattr(linter, "PROJECT_ROOT", tmp_tree)
    _write(tmp_tree, "tests/unit/tools/test_a.py", "import os\n")

    violations, _ = linter.lint(
        tmp_tree / "tests", ["tests/unit/tools/**/*.py"], strict=True
    )

    assert len(violations) == 1


# ---------------------------------------------------------------------------
# Skipped files
# ---------------------------------------------------------------------------

def test_conftest_and_init_are_not_scanned(linter, tmp_tree, monkeypatch):
    """`conftest.py` and `__init__.py` are infrastructure — never linted."""
    monkeypatch.setattr(linter, "PROJECT_ROOT", tmp_tree)
    _write(tmp_tree, "tests/conftest.py", "import os\n")
    _write(tmp_tree, "tests/__init__.py", "import os\n")
    _write(tmp_tree, "tests/test_real.py", "from game.core import X\n")

    violations, parse_errors = linter.lint(tmp_tree / "tests", [])
    assert violations == []
    assert parse_errors == []


# ---------------------------------------------------------------------------
# Parse failure handling
# ---------------------------------------------------------------------------

def test_ast_parse_failure_is_a_hard_error(linter, tmp_tree, monkeypatch):
    """Malformed Python in a test file must NOT silently allow — surface it."""
    monkeypatch.setattr(linter, "PROJECT_ROOT", tmp_tree)
    _write(tmp_tree, "tests/test_broken.py", "def oops(:\n    pass\n")

    violations, parse_errors = linter.lint(tmp_tree / "tests", [])
    assert violations == []
    assert len(parse_errors) == 1
    rel, msg = parse_errors[0]
    assert rel.as_posix() == "tests/test_broken.py"
    assert "SyntaxError" in msg


# ---------------------------------------------------------------------------
# CLI / exit codes
# ---------------------------------------------------------------------------

def test_main_returns_zero_on_clean_tree(linter, tmp_tree, monkeypatch):
    monkeypatch.setattr(linter, "PROJECT_ROOT", tmp_tree)
    _write(tmp_tree, "tests/test_ok.py", "from game.core import X\n")

    rc = linter.main([
        "--root", str(tmp_tree / "tests"),
        "--allowlist", str(tmp_tree / "nonexistent.txt"),
    ])
    assert rc == 0


def test_main_returns_one_on_violation(linter, tmp_tree, monkeypatch, capsys):
    monkeypatch.setattr(linter, "PROJECT_ROOT", tmp_tree)
    _write(tmp_tree, "tests/test_bad.py", "import os\n")

    rc = linter.main([
        "--root", str(tmp_tree / "tests"),
        "--allowlist", str(tmp_tree / "nonexistent.txt"),
    ])
    captured = capsys.readouterr()
    assert rc == 1
    assert "tests/test_bad.py" in captured.out


def test_main_strict_mode_bypasses_allowlist(linter, tmp_tree, monkeypatch, capsys):
    monkeypatch.setattr(linter, "PROJECT_ROOT", tmp_tree)
    _write(tmp_tree, "tests/test_bad.py", "import os\n")
    allowlist = tmp_tree / "allow.txt"
    allowlist.write_text("tests/test_bad.py\n", encoding="utf-8")

    rc_normal = linter.main([
        "--root", str(tmp_tree / "tests"),
        "--allowlist", str(allowlist),
    ])
    assert rc_normal == 0

    rc_strict = linter.main([
        "--root", str(tmp_tree / "tests"),
        "--allowlist", str(allowlist),
        "--strict",
    ])
    captured = capsys.readouterr()
    assert rc_strict == 1
    assert "tests/test_bad.py" in captured.out
