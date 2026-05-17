"""AST guard: forbid leaf-path imports of ``game.strategy.interfaces.engines.*``.

PROJ-422 split the ``game/strategy/interfaces/engines.py`` monolith into a
package with one leaf module per domain. The package's ``__init__.py``
re-exports every ABC under the package-root namespace. The hard
architectural invariant (see ``engines/__init__.py``):

    Leaf modules under this package are private. Consumers MUST import
    via ``game.strategy.interfaces.engines`` (the package path), never via
    ``game.strategy.interfaces.engines.movement`` etc.

This keeps the public API surface narrow and lets future domain regrouping
happen inside the package without churning consumers. The rule was
documented in PROJ-422 phase 1 but not enforced. This phase 6 guard test
walks ``game/`` and ``tests/`` and flags any leaf-path import.

Allowed exceptions:
- ``game/strategy/interfaces/engines/__init__.py`` — the package itself
  re-exports from its own leaves; that is its purpose.
- ``tests/unit/strategy/interfaces/test_engines_package_layout.py`` — the
  structural layout test legitimately probes leaf paths to validate the
  package layout.
"""
from __future__ import annotations

import ast
from pathlib import Path

# Static import to satisfy `Tools/lint_test_files.py` (rejects test files with
# zero `game.*` AST imports). The guard below operates on text files via
# `ast.parse`, so it does not otherwise need to import production code.
import game.strategy.interfaces.engines  # noqa: F401

REPO_ROOT = Path(__file__).resolve().parents[4]
GAME_ROOT = REPO_ROOT / "game"
TESTS_ROOT = REPO_ROOT / "tests"

ENGINES_PKG = "game.strategy.interfaces.engines"
LEAF_NAMES: frozenset[str] = frozenset(
    {
        "movement",
        "orders",
        "combat",
        "production",
        "logistics",
        "population",
        "planet_ops",
        "terraforming",
        "components",
    }
)

# Files allowed to import leaves directly.
ALLOWED_RELATIVE_PATHS: frozenset[str] = frozenset(
    {
        "game/strategy/interfaces/engines/__init__.py",
        "tests/unit/strategy/interfaces/test_engines_package_layout.py",
    }
)


def _find_leaf_path_imports(tree: ast.Module) -> list[tuple[int, str]]:
    """Return ``(lineno, offending_module)`` for any leaf-path import.

    Catches both forms:
      * ``from game.strategy.interfaces.engines.<leaf> import ...``
      * ``import game.strategy.interfaces.engines.<leaf>``
    """
    hits: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod.startswith(ENGINES_PKG + "."):
                leaf = mod[len(ENGINES_PKG) + 1 :].split(".", 1)[0]
                if leaf in LEAF_NAMES:
                    hits.append((node.lineno, mod))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name or ""
                if name.startswith(ENGINES_PKG + "."):
                    leaf = name[len(ENGINES_PKG) + 1 :].split(".", 1)[0]
                    if leaf in LEAF_NAMES:
                        hits.append((node.lineno, name))
    return hits


def _scan_roots(roots: list[Path]) -> list[str]:
    """Walk each root and return ``"<rel_path>:<lineno>: <module>"`` strings."""
    offending: list[str] = []
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            if rel in ALLOWED_RELATIVE_PATHS:
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except SyntaxError:
                # Malformed source — someone else's problem.
                continue
            for lineno, mod in _find_leaf_path_imports(tree):
                offending.append(f"{rel}:{lineno}: imports {mod}")
    return offending


def test_no_leaf_path_imports_under_game_or_tests() -> None:
    """No file outside the allowlist may import an engines leaf module directly."""
    assert GAME_ROOT.is_dir(), f"GAME_ROOT does not exist: {GAME_ROOT}"
    assert TESTS_ROOT.is_dir(), f"TESTS_ROOT does not exist: {TESTS_ROOT}"
    offending = _scan_roots([GAME_ROOT, TESTS_ROOT])
    assert offending == [], (
        "PROJ-422 architectural invariant violated: the following file(s) "
        "import a private leaf of `game.strategy.interfaces.engines` instead "
        "of importing the ABC via the package root. Rewrite each import as "
        "`from game.strategy.interfaces.engines import I<Name>`.\n  - "
        + "\n  - ".join(offending)
    )


# ---------------------------------------------------------------------------
# Walker self-tests — prove the walker actually flags violations.
# ---------------------------------------------------------------------------


def test_walker_flags_from_leaf_import() -> None:
    """Synthetic positive: ``from <pkg>.<leaf> import X`` IS flagged."""
    src = "from game.strategy.interfaces.engines.movement import IMovementEngine\n"
    tree = ast.parse(src)
    hits = _find_leaf_path_imports(tree)
    assert len(hits) == 1
    assert hits[0][1] == "game.strategy.interfaces.engines.movement"


def test_walker_flags_import_leaf() -> None:
    """Synthetic positive: ``import <pkg>.<leaf>`` IS flagged."""
    src = "import game.strategy.interfaces.engines.combat\n"
    tree = ast.parse(src)
    hits = _find_leaf_path_imports(tree)
    assert len(hits) == 1
    assert hits[0][1] == "game.strategy.interfaces.engines.combat"


def test_walker_does_not_flag_package_root_import() -> None:
    """Synthetic negative: the allowed package-root import is NOT flagged."""
    src = "from game.strategy.interfaces.engines import IMovementEngine\n"
    tree = ast.parse(src)
    assert _find_leaf_path_imports(tree) == []


def test_walker_does_not_flag_unrelated_import() -> None:
    """Synthetic negative: an unrelated import is NOT flagged."""
    src = "from game.strategy.engine.fleet_movement_engine import FleetMovementEngine\n"
    tree = ast.parse(src)
    assert _find_leaf_path_imports(tree) == []


def test_walker_does_not_flag_unknown_leaf_name() -> None:
    """Synthetic negative: a not-real ``<pkg>.<unknown>`` import is NOT flagged.

    The guard intentionally lists the nine known leaves so that a future
    same-namespace utility module (e.g. ``engines/_helpers.py``) isn't
    accidentally swept up. If a new leaf is added, both this test and the
    LEAF_NAMES set should be updated together.
    """
    src = "from game.strategy.interfaces.engines._not_a_leaf import X\n"
    tree = ast.parse(src)
    assert _find_leaf_path_imports(tree) == []
