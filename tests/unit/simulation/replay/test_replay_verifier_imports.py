"""PROJ-366 Phase 4 — verifier dependency-direction lint.

Locks in the layer-violation fix from PROJ-354B audit-remediation
`27e297815` (finding AR-001): `game/simulation/replay/replay_verifier.py`
must NOT import from `game.strategy.*`, `game.ui.*`, or `game.ai.*`.
The materializer factory `build_replay_ship_builder` was moved out of
`replay_verifier.py` (and `replay_player.py`) into
`game/strategy/services/replay_ship_builder.py` so the simulation layer
no longer reaches into the strategy layer.

This test parses the verifier module's AST and asserts the import
contract. AST is preferred over a static analyzer to keep the test free
of new tooling dependencies.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest


_FORBIDDEN_PREFIXES = ("game.strategy.", "game.ui.", "game.ai.")


def _repo_root() -> Path:
    """Walk up from this test file to find the repo root.

    The test must not hardcode a checkout path (per CLAUDE.md). We climb
    until we find a directory containing `pyproject.toml` or `pytest.ini`.
    """
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pytest.ini").exists() or (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("could not locate repo root")


def test_verifier_has_no_upward_imports() -> None:
    """`replay_verifier.py` must not import from upper layers."""
    src_path = _repo_root() / "game" / "simulation" / "replay" / "replay_verifier.py"
    assert src_path.exists(), f"missing: {src_path}"

    tree = ast.parse(src_path.read_text(encoding="utf-8"))

    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if any(mod.startswith(p) for p in _FORBIDDEN_PREFIXES):
                violations.append(f"from {mod} import ...")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if any(alias.name.startswith(p) for p in _FORBIDDEN_PREFIXES):
                    violations.append(f"import {alias.name}")

    assert not violations, (
        f"replay_verifier.py imports forbidden upper-layer modules: {violations}"
    )
