#!/usr/bin/env python3
"""
Lint test files: flag any test file under ``tests/`` that imports zero
``game.*`` modules.

A test file with no ``from game...`` / ``import game...`` import statements is
strongly suspect — historically these have been files that re-implement
production logic locally (the ``tests/unit/test_modifier_logic.py`` pattern
PROJ-321 deleted) or trivial-pass tests with no real coverage. Legitimate
exceptions (tests of repo tooling, the test infrastructure itself, or test
data fixtures) live in an allowlist file.

Usage:
    python Tools/lint_test_files.py
    python Tools/lint_test_files.py --root tests/
    python Tools/lint_test_files.py --allowlist Tools/lint_test_files_allowlist.txt
    python Tools/lint_test_files.py --strict   # bypass allowlist (audit mode)

Exit codes:
    0 — no violations
    1 — at least one non-allowlisted file with zero ``game`` imports, OR an
        AST parse failure on a scanned file.

The check is AST-based, NOT regex — string-matching for ``import game``
produces false positives on docstrings, comments, and strings.

Allowlist format (Tools/lint_test_files_allowlist.txt):
    - One path per line, relative to the repo root.
    - Glob patterns are matched by an internal POSIX-style glob translator
      (``_glob_to_regex``) — NOT ``pathlib.PurePosixPath.match`` (which
      doesn't recurse on ``**``). The translator supports ``**`` recursion
      and works under any supported Python version.
    - Blank lines and lines starting with ``#`` are ignored.

Known blind spots (tracked, not fixed because the false-positive cost
exceeds the marginal value):
    - ``importlib.import_module("game.foo")`` is a string literal, not
      an AST ``Import``/``ImportFrom`` node, so a test that ONLY uses
      string-based imports would be flagged as having "no game imports".
      Fix: use a real ``import game.foo`` (or ``from game.foo import ...``)
      somewhere in the file. If a deferred-import pattern is genuinely
      required, allowlist the specific test file.

Created by PROJ-326 Phase 1.
PROJ-353 Tier-7 (T2.10): docstring corrections + blind-spot
documentation; Python version comment updated to reflect 3.13+ baseline.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path, PurePosixPath


def _find_project_root() -> Path:
    """Find project root by looking for ``game/`` and ``tests/`` directories."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "tests").is_dir():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root (game/ + tests/)")


PROJECT_ROOT = _find_project_root()
DEFAULT_ALLOWLIST = PROJECT_ROOT / "Tools" / "lint_test_files_allowlist.txt"
DEFAULT_ROOT = PROJECT_ROOT / "tests"

# Files we never lint (not test files in the meaningful sense).
SKIP_FILENAMES: frozenset[str] = frozenset({"conftest.py", "__init__.py"})
SKIP_DIR_NAMES: frozenset[str] = frozenset({"__pycache__"})


def load_allowlist(path: Path) -> list[str]:
    """Load allowlist patterns from a file.

    Returns a list of glob pattern strings (POSIX-style, relative to the repo
    root). Blank lines and ``#`` comments are stripped.
    """
    if not path.exists():
        return []
    patterns: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns


def _glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Translate a forward-slash glob (with ``**`` support) to a regex.

    Supports:
      - ``*`` — matches any non-separator characters within a single path segment
      - ``**`` — matches across path separators (zero or more segments)
      - ``?`` — matches a single non-separator character
      - literal segments otherwise

    Anchored at both ends. Always operates on POSIX-style paths.
    """
    i = 0
    out: list[str] = []
    while i < len(pattern):
        c = pattern[i]
        if c == "*":
            if i + 1 < len(pattern) and pattern[i + 1] == "*":
                # ``**`` — matches across separators (and zero segments).
                out.append(".*")
                i += 2
                # Eat an optional following slash so ``a/**/b`` also matches ``a/b``.
                if i < len(pattern) and pattern[i] == "/":
                    i += 1
            else:
                # ``*`` — non-separator characters only.
                out.append("[^/]*")
                i += 1
        elif c == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(c))
            i += 1
    return re.compile("^" + "".join(out) + "$")


def matches_allowlist(rel_path: Path, patterns: list[str]) -> bool:
    """Return True if ``rel_path`` (relative to repo root) matches any pattern.

    Uses a custom POSIX-style glob matcher that supports ``**`` recursion.
    ``pathlib.Path.match`` does NOT recurse on ``**`` (Python 3.13 added
    ``full_match`` for full-path matching, but its ``**`` semantics still
    differ from typical CI-glob expectations). The custom translator
    keeps behavior portable across Python versions.
    """
    posix = PurePosixPath(rel_path.as_posix()).as_posix()
    for pattern in patterns:
        if _glob_to_regex(pattern).match(posix):
            return True
    return False


def imports_game(tree: ast.AST) -> bool:
    """Return True if the AST contains any ``import game`` or
    ``from game...`` statement (the top-level package must be exactly
    ``game`` — ``somethinglikegame`` does NOT count).

    PROJ-353 Tier-7 (T2.10): also detects the dynamic-import pattern
    ``importlib.import_module("game.foo")`` so files using deferred
    imports as their primary surface are not flagged. The detection is
    deliberately limited to constant string arguments — a runtime-built
    module name (``import_module(f"game.{x}")``) is NOT detected, which
    is correct: that pattern hides the dependency from static analysis
    and the lint should treat it as missing.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root == "game":
                    return True
        elif isinstance(node, ast.ImportFrom):
            if node.module is None:
                # ``from . import x`` — relative; cannot reference top-level game.
                continue
            root = node.module.split(".", 1)[0]
            if root == "game":
                return True
        elif isinstance(node, ast.Call):
            # Detect importlib.import_module("game.foo") / import_module("game.foo").
            func = node.func
            is_import_module = (
                isinstance(func, ast.Attribute) and func.attr == "import_module"
            ) or (
                isinstance(func, ast.Name) and func.id == "import_module"
            )
            if is_import_module and node.args:
                first = node.args[0]
                if isinstance(first, ast.Constant) and isinstance(first.value, str):
                    root = first.value.split(".", 1)[0]
                    if root == "game":
                        return True
    return False


def iter_test_files(root: Path) -> list[Path]:
    """Walk ``root`` recursively for ``*.py`` test files, skipping infra."""
    results: list[Path] = []
    for path in sorted(root.rglob("*.py")):
        if path.name in SKIP_FILENAMES:
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        results.append(path)
    return results


def lint(
    root: Path,
    allowlist_patterns: list[str],
    *,
    strict: bool = False,
) -> tuple[list[Path], list[tuple[Path, str]]]:
    """Run the linter.

    Returns ``(violations, parse_errors)``:
      - ``violations``: files that lack ``game.*`` imports and are not allowlisted
        (in ``--strict`` mode, allowlist is ignored entirely).
      - ``parse_errors``: list of (file, message) for files that failed to parse.

    Caller decides exit-code semantics from these lists.
    """
    violations: list[Path] = []
    parse_errors: list[tuple[Path, str]] = []

    for path in iter_test_files(root):
        try:
            rel = path.relative_to(PROJECT_ROOT)
        except ValueError:
            # Scan root is outside PROJECT_ROOT (e.g. a temp tree in tests).
            # Allowlist patterns are repo-relative, so fall back to the
            # path-relative-to-scan-root form for matching.
            rel = path.relative_to(root)
        if not strict and matches_allowlist(rel, allowlist_patterns):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            parse_errors.append((rel, f"SyntaxError: {exc}"))
            continue
        except OSError as exc:
            parse_errors.append((rel, f"OSError: {exc}"))
            continue
        if not imports_game(tree):
            violations.append(rel)

    return violations, parse_errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Flag test files under tests/ that have zero `from game.*` / "
            "`import game.*` import statements. Allowlist supports glob "
            "patterns relative to the repo root."
        ),
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="Directory to scan recursively (default: tests/).",
    )
    parser.add_argument(
        "--allowlist",
        type=Path,
        default=DEFAULT_ALLOWLIST,
        help="Allowlist file (default: Tools/lint_test_files_allowlist.txt).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Bypass the allowlist entirely — flag every zero-game-import "
            "test file. Use for full audit enumeration."
        ),
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if not root.exists():
        print(f"Root does not exist: {root}", file=sys.stderr)
        return 1

    patterns = load_allowlist(args.allowlist) if not args.strict else []
    violations, parse_errors = lint(root, patterns, strict=args.strict)

    for rel in violations:
        print(rel.as_posix())

    if parse_errors:
        print("", file=sys.stderr)
        print("PARSE ERRORS (treated as failures):", file=sys.stderr)
        for rel, msg in parse_errors:
            print(f"  {rel.as_posix()}: {msg}", file=sys.stderr)

    if violations:
        print(
            f"\nlint_test_files: {len(violations)} file(s) flagged "
            f"(zero `game.*` imports, not in allowlist).",
            file=sys.stderr,
        )

    if violations or parse_errors:
        return 1
    print(
        "lint_test_files: OK (0 violations).",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
