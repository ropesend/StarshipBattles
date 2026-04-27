"""PROJ-300 Phase 4 Task 4.5 — AST static-analysis guard.

After PROJ-306 banned `get_default_registry_provider()` calls inside
`game/simulation/`, PROJ-300 extended the prohibition to the
`game/strategy/services/ability_sources/` adapter package: registries
must be constructor-injected, never globally looked up.

The AST scan fails if any adapter file contains a Name / Attribute /
Import reference to the forbidden symbol. Docstrings and comments
mentioning the rule itself are deliberately allowed.
"""
import ast
from pathlib import Path

import pytest

ADAPTER_DIR = (
    Path(__file__).resolve().parents[4]
    / "game" / "strategy" / "services" / "ability_sources"
)
FORBIDDEN = "get_default_registry_provider"


def _adapter_python_files():
    return [p for p in ADAPTER_DIR.glob("*.py") if p.name != "__pycache__"]


@pytest.mark.parametrize("path", _adapter_python_files(), ids=lambda p: p.name)
def test_no_get_default_registry_provider_in_ast(path):
    """AST scan: forbidden symbol must not appear as a Name/Attribute/Import
    reference. Docstrings + comments mentioning the rule are explicitly OK."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == FORBIDDEN:
            pytest.fail(
                f"PROJ-300 Task 4.5 violation: {path.name}:{node.lineno} "
                f"references `{FORBIDDEN}`. Adapters must take registries "
                f"via constructor injection, not module-level lookup."
            )
        if isinstance(node, ast.Attribute) and node.attr == FORBIDDEN:
            pytest.fail(
                f"PROJ-300 Task 4.5 violation: {path.name}:{node.lineno} "
                f"attribute access `.{FORBIDDEN}`."
            )
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == FORBIDDEN:
                    pytest.fail(
                        f"PROJ-300 Task 4.5 violation: {path.name}:"
                        f"{node.lineno} imports `{FORBIDDEN}`."
                    )


def test_adapter_package_actually_has_python_files():
    """Sanity: the package exists and has files (the parametrize would
    silently produce zero tests if not)."""
    files = _adapter_python_files()
    assert files, f"No .py files found in {ADAPTER_DIR}"
    names = {f.name for f in files}
    # Each PROJ-300..305 adapter file should be present.
    assert "facility.py" in names
    assert "storm.py" in names
    assert "planet_intrinsic.py" in names
    assert "star.py" in names
    assert "warp_point.py" in names
    assert "system_archetype.py" in names
    assert "fleet.py" in names
