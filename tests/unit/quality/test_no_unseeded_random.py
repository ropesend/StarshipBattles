"""PROJ-312 Phase 1 — AST guard against unseeded ``random.*`` calls.

Replay determinism (PROJ-312) requires that every RNG consumer in the battle
hot path receive its RNG via dependency injection, sourced from
``BattleEngine.rng`` (a ``random.Random(seed)`` instance set at battle start
— Pattern #18 in ``docs/02_PATTERNS.md``).

A direct call like ``random.choice(...)`` or ``random.uniform(...)`` reaches
the **module-level** RNG, which is global state shared across the process and
NOT seeded by simulation code. Any such call breaks replay determinism: a
captured ``BattleSpec + seed`` cannot be re-run to produce an identical
``BattleOutcome`` if other entropy sources leak in.

This test walks the AST of every ``.py`` file under ``game/simulation/``,
``game/engine/``, and ``game/ai/`` and fails if it finds any ``random.<X>``
call other than ``random.Random(...)`` (the constructor — that produces a
seedable instance, which is fine).

Add ``# noqa: replay-determinism`` on a line to allowlist a genuinely-justified
module-level use. None are expected today; the marker is preserved for future
flexibility (e.g., a tool-only path that must use module-level state).
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import List, Tuple

import pytest


# Layers covered by the determinism contract. Strategy is intentionally
# excluded: PROJ-301-304 plumbs a separate seeded RNG through the strategy
# layer's intrinsic rolls, and `ConflictResolutionEngine` owns its own
# `Random` instance for empire-pairing decisions. That contract is
# audited separately.
GUARDED_DIRECTORIES = ("game/simulation", "game/engine", "game/ai")

# `random.Random(...)` is the constructor — produces a seedable instance.
# Every other ``random.<NAME>(...)`` call reaches the module-level RNG.
ALLOWED_ATTRIBUTES = frozenset({"Random"})

ALLOWLIST_MARKER = "noqa: replay-determinism"


def _project_root() -> Path:
    """Return the repository root regardless of test cwd."""
    here = Path(__file__).resolve()
    # tests/unit/quality/test_no_unseeded_random.py -> repo root
    return here.parent.parent.parent.parent


def _iter_guarded_files() -> List[Path]:
    """All .py files under the guarded directories."""
    root = _project_root()
    files: List[Path] = []
    for rel_dir in GUARDED_DIRECTORIES:
        directory = root / rel_dir
        if not directory.is_dir():
            continue
        files.extend(p for p in directory.rglob("*.py") if p.is_file())
    return files


def _is_random_module_call(node: ast.AST) -> bool:
    """True if `node` is a call like `random.<NAME>(...)`."""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if not isinstance(func, ast.Attribute):
        return False
    if not isinstance(func.value, ast.Name):
        return False
    return func.value.id == "random"


def _line_has_allowlist_marker(source_lines: List[str], lineno: int) -> bool:
    """True if the matching source line carries the allowlist marker."""
    if 0 < lineno <= len(source_lines):
        return ALLOWLIST_MARKER in source_lines[lineno - 1]
    return False


def _scan_file(path: Path) -> List[Tuple[int, str]]:
    """Return list of (lineno, attribute) for unseeded random.* calls in file."""
    source = path.read_text(encoding="utf-8")
    source_lines = source.splitlines()
    tree = ast.parse(source, filename=str(path))
    findings: List[Tuple[int, str]] = []
    for node in ast.walk(tree):
        if not _is_random_module_call(node):
            continue
        attr = node.func.attr  # type: ignore[union-attr]
        if attr in ALLOWED_ATTRIBUTES:
            continue
        if _line_has_allowlist_marker(source_lines, node.lineno):
            continue
        findings.append((node.lineno, attr))
    return findings


def test_no_unseeded_random_in_battle_layer() -> None:
    """No file under game/simulation, game/engine, or game/ai may call
    ``random.<X>(...)`` (other than the ``Random()`` constructor) without an
    explicit ``# noqa: replay-determinism`` allowlist marker.

    Failure means the listed call site uses the global module-level RNG,
    breaking PROJ-312's seeded-replay contract. Fix by injecting a
    ``random.Random`` instance via the existing DI chain (engine → factory →
    controller → behavior).
    """
    violations: List[str] = []
    root = _project_root()
    for path in _iter_guarded_files():
        for lineno, attr in _scan_file(path):
            rel = path.relative_to(root)
            violations.append(f"{rel.as_posix()}:{lineno}: random.{attr}(...)")
    assert not violations, (
        "Unseeded random.* calls found in battle/AI layer. Inject a "
        "random.Random instance via DI (see Pattern #18 in docs/02_PATTERNS.md). "
        "If module-level random is genuinely required, add `# noqa: "
        "replay-determinism` on the offending line.\n"
        + "\n".join(violations)
    )
