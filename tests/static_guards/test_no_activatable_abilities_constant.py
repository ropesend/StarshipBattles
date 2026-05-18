"""PROJ-446 Phase 2 / F-C-019 static guard.

Locks in the final-state contract for the PROJ-435 retirement of the
hardcoded ``_ACTIVATABLE_ABILITIES`` literal in
``game/ui/screens/builder/stat_rows_dynamic.py``. The replacement
routes through
``abilities_with_kind_tag(StrategicKind.ENERGY_DRAINING)`` so any new
ability tagged with the energy-draining kind is automatically picked
up — adding the constant back is a regression.

PROJ-435 was an entire spin-off project to retire one hardcoded set;
the existing project trail captures the rationale. This guard catches
a re-introduction at static-scan time.
"""
from __future__ import annotations

import ast
from pathlib import Path


def _repo_root() -> Path:
    """Walk upward to the repo root (the dir containing ``game/`` and ``data/``)."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "game").is_dir() and (parent / "data").is_dir():
            return parent
    raise RuntimeError("Could not locate repo root from " + str(here))


def _scan_for_activatable_abilities_assignment(package_dir: Path) -> list[tuple[Path, int]]:
    """AST-scan a package for any ``_ACTIVATABLE_ABILITIES = ...`` assignment.

    Catches both module-level and function-local assignments. Returns a
    list of (file_path, line_number) pairs for each Assign node whose
    target name is ``_ACTIVATABLE_ABILITIES``. Test-style files
    (`test_*.py` and `*_test.py`) are excluded so this guard's own
    self-reference does not trip the scan if it ever moves under
    `game/`.
    """
    hits: list[tuple[Path, int]] = []
    for py_file in package_dir.rglob("*.py"):
        name = py_file.name
        if name.startswith("test_") or name.endswith("_test.py"):
            continue
        try:
            source = py_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        try:
            tree = ast.parse(source, filename=str(py_file))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "_ACTIVATABLE_ABILITIES":
                        hits.append((py_file, node.lineno))
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and node.target.id == "_ACTIVATABLE_ABILITIES":
                    hits.append((py_file, node.lineno))
    return hits


def test_no_activatable_abilities_assignment_in_stat_rows_dynamic() -> None:
    """``stat_rows_dynamic.py`` MUST NOT carry an ``_ACTIVATABLE_ABILITIES`` literal.

    F-C-019 static guard, primary site. The PROJ-435 retirement replaced
    the hardcoded ability-name set with a kind-tag query
    (``abilities_with_kind_tag(StrategicKind.ENERGY_DRAINING)``). A
    future "just add it back, it's easier" regression now fails here.
    """
    target = (
        _repo_root()
        / "game" / "ui" / "screens" / "builder" / "stat_rows_dynamic.py"
    )
    source = target.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(target))
    hits: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "_ACTIVATABLE_ABILITIES":
                    hits.append(node.lineno)
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == "_ACTIVATABLE_ABILITIES":
                hits.append(node.lineno)
    assert not hits, (
        f"stat_rows_dynamic.py contains {len(hits)} `_ACTIVATABLE_ABILITIES` "
        f"assignment(s) at line(s) {hits} (PROJ-446 F-C-019 static guard). "
        f"PROJ-435 retired the hardcoded set; use "
        f"`abilities_with_kind_tag(StrategicKind.ENERGY_DRAINING)` instead."
    )


def test_no_activatable_abilities_assignment_in_builder_package() -> None:
    """Broader AST scan: no ``_ACTIVATABLE_ABILITIES`` assignment anywhere under ``game/ui/screens/builder/``.

    F-C-019 static guard, package-wide. Catches the same regression
    landing in a sibling file (e.g., ``stat_definitions.py`` or
    ``stat_getters.py``) rather than the original site.
    """
    package_dir = _repo_root() / "game" / "ui" / "screens" / "builder"
    hits = _scan_for_activatable_abilities_assignment(package_dir)
    assert not hits, (
        f"Found {len(hits)} `_ACTIVATABLE_ABILITIES = ...` assignment(s) "
        f"under `game/ui/screens/builder/` (PROJ-446 F-C-019 static guard): "
        f"{[(str(p), n) for p, n in hits]}. PROJ-435 retired the hardcoded "
        f"set; use `abilities_with_kind_tag(StrategicKind.ENERGY_DRAINING)`."
    )
