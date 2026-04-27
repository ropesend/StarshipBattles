"""Regression: enforce game/services/ layer dependency rule (PROJ-296).

Per `docs/01_ARCHITECTURE.md`, the new `services/` layer depends only
on Core. It must NEVER import from any domain layer (Engine, Simulation,
Research, Strategy, AI, UI). This test scans every module under
`game/services/` and asserts the rule.

If a future agent adds an import from a domain layer to a services
module, this test fails immediately — preventing accidental layer
inversion.
"""
from __future__ import annotations

import ast
import os
from pathlib import Path
from typing import Iterator, Set

import pytest

FORBIDDEN_PREFIXES = (
    "game.engine",
    "game.simulation",
    "game.research",
    "game.strategy",
    "game.ai",
    "game.ui",
    # 'game.app' lives at the top level but pulls in UI; forbidden too.
    "game.app",
    # ApplicationContext is the inverse direction — context.py imports
    # services. Services importing context.py would create a circular
    # dependency.
    "game.context",
)

ALLOWED_GAME_PREFIXES = (
    "game.core",
    "game.services",
)


def _services_modules() -> Iterator[Path]:
    root = Path(__file__).resolve().parents[2] / "game" / "services"
    for path in root.rglob("*.py"):
        # Skip __pycache__ and similar
        if "__pycache__" in path.parts:
            continue
        yield path


def _collect_imports(source: str) -> Set[str]:
    tree = ast.parse(source)
    imports: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    return imports


@pytest.mark.parametrize(
    "module_path",
    list(_services_modules()),
    ids=lambda p: str(p.relative_to(Path(__file__).resolve().parents[2])),
)
def test_services_module_does_not_import_domain_layers(module_path: Path) -> None:
    """Every game/services/**.py may only import from game.core or stdlib/third-party."""
    source = module_path.read_text(encoding="utf-8")
    imports = _collect_imports(source)

    for imp in imports:
        # Only check game.* imports.
        if not imp.startswith("game."):
            continue
        # Allowed: game.core, game.services itself.
        if imp.startswith(ALLOWED_GAME_PREFIXES):
            continue
        # Forbidden — domain layer leak.
        for forbidden in FORBIDDEN_PREFIXES:
            if imp.startswith(forbidden):
                pytest.fail(
                    f"{module_path.relative_to(Path(__file__).resolve().parents[2])} "
                    f"imports {imp!r} from forbidden domain layer {forbidden!r}. "
                    f"game/services/ depends only on game.core (per docs/01_ARCHITECTURE.md)."
                )
        # Anything else under game.* that isn't core/services is also forbidden.
        pytest.fail(
            f"{module_path.relative_to(Path(__file__).resolve().parents[2])} "
            f"imports {imp!r}, which is neither game.core nor game.services. "
            f"Services may only depend on Core."
        )
