"""PROJ-446 Phase 2 / F-C-018 static guard.

Locks in the final-state contract for the PROJ-427 / PROJ-434
`DesignLibrary` retirement: the legacy `DesignLibrary` class was
replaced by `DesignCatalog` (per-empire owned-design registry) and
`DesignRepository` (storage adapter). Production callers route through
those two surfaces.

PROJ-436 / PROJ-437 retirements got their own static guards
(`test_no_carried_items_proxy`, `test_no_legacy_storage_fields`,
`test_no_resource_types_constant` style). The DesignLibrary retirement
was the gap; this file closes it. A future "I'll just re-create
DesignLibrary as a thin shim..." regression now fails at static-guard
time rather than slipping in silently.
"""
from __future__ import annotations

import ast
from pathlib import Path

import game.strategy.systems.design_catalog as design_catalog_module


def test_design_catalog_module_has_no_design_library_attribute() -> None:
    """``game.strategy.systems.design_catalog`` MUST NOT expose ``DesignLibrary``.

    F-C-018 static guard. Production callers route through
    ``DesignCatalog`` (the new per-empire owned-design registry) and
    ``DesignRepository`` (storage adapter). The runtime attribute check
    catches both class redefinitions and import-time re-binding.
    """
    assert not hasattr(design_catalog_module, "DesignLibrary"), (
        "game.strategy.systems.design_catalog still exposes a "
        "`DesignLibrary` attribute (PROJ-446 F-C-018 static guard). The "
        "class was retired by PROJ-427 / PROJ-434 in favor of "
        "`DesignCatalog` + `DesignRepository`. Do not re-introduce."
    )


def _scan_for_design_library_classdef(package_dir: Path) -> list[tuple[Path, int]]:
    """AST-scan a package for ``class DesignLibrary`` definitions.

    Returns a list of (file_path, line_number) pairs for each
    `class DesignLibrary` ClassDef node found. Test-style files
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
            if isinstance(node, ast.ClassDef) and node.name == "DesignLibrary":
                hits.append((py_file, node.lineno))
    return hits


def _repo_root() -> Path:
    """Walk upward to the repo root (the dir containing ``game/`` and ``data/``)."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "game").is_dir() and (parent / "data").is_dir():
            return parent
    raise RuntimeError("Could not locate repo root from " + str(here))


def test_no_design_library_class_definition_in_strategy_systems() -> None:
    """AST scan: no ``class DesignLibrary`` definition under ``game/strategy/systems/``.

    F-C-018 static guard, AST-half. Catches a class redefinition the
    runtime ``hasattr`` check would also catch, but pins the location
    so re-introductions are diagnosed at file:line in the failure
    message.
    """
    package_dir = _repo_root() / "game" / "strategy" / "systems"
    hits = _scan_for_design_library_classdef(package_dir)
    assert not hits, (
        f"Found {len(hits)} `class DesignLibrary` definition(s) under "
        f"`game/strategy/systems/` (PROJ-446 F-C-018 static guard): "
        f"{[(str(p), n) for p, n in hits]}. The class was retired by "
        f"PROJ-427 / PROJ-434 in favor of `DesignCatalog` + "
        f"`DesignRepository`."
    )


def test_no_design_library_class_definition_in_simulation_services() -> None:
    """AST scan: no ``class DesignLibrary`` definition under ``game/simulation/services/``.

    F-C-018 static guard, secondary scan. `DesignLibrary` historically
    lived adjacent to `DesignLoader` in simulation services; pin the
    absence there too.
    """
    package_dir = _repo_root() / "game" / "simulation" / "services"
    hits = _scan_for_design_library_classdef(package_dir)
    assert not hits, (
        f"Found {len(hits)} `class DesignLibrary` definition(s) under "
        f"`game/simulation/services/` (PROJ-446 F-C-018 static guard): "
        f"{[(str(p), n) for p, n in hits]}. The class was retired by "
        f"PROJ-427 / PROJ-434."
    )
