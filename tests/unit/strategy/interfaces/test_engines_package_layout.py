"""Structural regression tests for the `game.strategy.interfaces.engines` package.

PROJ-422 (TD-09) splits the 778-LOC `engines.py` monolith into a domain-organised
package while preserving every existing `from game.strategy.interfaces.engines
import I<Name>` import path. These tests pin the package layout, enumerate the
expected per-leaf `__all__`, assert symmetric re-export with the outer
`game.strategy.interfaces.__all__`, and forbid a leftover `engines.py` module
file.

The tests are deliberately strict: any drift between the design's layout table
and the package contents (new ABC without a leaf update, missing leaf, missing
top-level re-export, etc.) fails one of these assertions.
"""

from __future__ import annotations

import abc
import importlib
import sys
from pathlib import Path

# Static import to satisfy `Tools/lint_test_files.py` (rejects test files with
# zero `game.*` AST imports). The structural checks below re-import via
# `importlib` so they exercise a clean module state per-test.
import game.strategy.interfaces  # noqa: F401


# --- Expected layout, sourced from the PROJ-422 design ----------------------

# Per-leaf `__all__` — must match the layout table in `manifest.md` verbatim.
EXPECTED_LEAF_EXPORTS: dict[str, tuple[str, ...]] = {
    "movement": ("IMovementEngine",),
    "orders": ("IOrderProcessor", "IActionExecutionEngine"),
    "combat": ("IConflictEngine", "IEnvironmentalHazardEngine"),
    "production": ("IProductionEngine",),
    "logistics": ("IConsumableEngine", "IResupplyEngine", "IHarvestingEngine"),
    "population": (
        "IPopulationEngine",
        "IOrganicsConsumptionEngine",
        "IHappinessEngine",
    ),
    "planet_ops": ("IPlanetEnergyEngine", "IPlanetActionEngine"),
    "terraforming": ("IQualityEngine", "IAtmosphereEngine", "IWaterEngine"),
    "components": ("IComponentActivationEngine",),
}

# Flattened canonical 18-name set.
EXPECTED_ABC_NAMES: frozenset[str] = frozenset(
    name for names in EXPECTED_LEAF_EXPORTS.values() for name in names
)


# --- Helpers ---------------------------------------------------------------


def _fresh_import(dotted: str):
    """Import (or re-import) a module by dotted path."""
    if dotted in sys.modules:
        return importlib.reload(sys.modules[dotted])
    return importlib.import_module(dotted)


# --- Tests ----------------------------------------------------------------


def test_engines_is_a_package() -> None:
    """`game.strategy.interfaces.engines` must be a package (has `__path__`)."""
    engines = _fresh_import("game.strategy.interfaces.engines")
    assert hasattr(engines, "__path__"), (
        "engines must be a package (with __path__), not a single-file module. "
        "Got module file: "
        f"{getattr(engines, '__file__', '<missing>')!r}"
    )


def test_each_leaf_module_loads() -> None:
    """Every expected leaf module must import cleanly from the package."""
    for leaf in EXPECTED_LEAF_EXPORTS:
        mod = _fresh_import(f"game.strategy.interfaces.engines.{leaf}")
        assert mod is not None, f"leaf module {leaf!r} failed to import"


def test_each_abc_importable_from_package_root() -> None:
    """All 18 ABCs must be reachable via the package root and be `abc.ABC` subclasses."""
    engines = _fresh_import("game.strategy.interfaces.engines")
    for name in sorted(EXPECTED_ABC_NAMES):
        assert hasattr(engines, name), (
            f"{name} is not exposed by game.strategy.interfaces.engines"
        )
        cls = getattr(engines, name)
        assert isinstance(cls, type) and issubclass(cls, abc.ABC), (
            f"{name} is not an abc.ABC subclass"
        )


def test_each_leaf_exports_expected_abcs() -> None:
    """Each leaf `__all__` must equal the design's layout-table tuple verbatim."""
    for leaf, expected in EXPECTED_LEAF_EXPORTS.items():
        mod = _fresh_import(f"game.strategy.interfaces.engines.{leaf}")
        actual = tuple(getattr(mod, "__all__", ()))
        assert actual == expected, (
            f"leaf {leaf!r} __all__ mismatch: expected {expected}, got {actual}"
        )


def test_top_level_interfaces_reexports_all_engines() -> None:
    """Every name in `engines.__all__` must also be in `game.strategy.interfaces.__all__`."""
    engines = _fresh_import("game.strategy.interfaces.engines")
    interfaces = _fresh_import("game.strategy.interfaces")
    engines_all = set(getattr(engines, "__all__", ()))
    interfaces_all = set(getattr(interfaces, "__all__", ()))
    missing = engines_all - interfaces_all
    assert not missing, (
        f"game.strategy.interfaces.__all__ is missing engine re-exports: "
        f"{sorted(missing)}"
    )
    # And the engines package's __all__ must itself be the full 18-name set.
    assert engines_all == EXPECTED_ABC_NAMES, (
        f"engines.__all__ drift: missing={sorted(EXPECTED_ABC_NAMES - engines_all)}, "
        f"extra={sorted(engines_all - EXPECTED_ABC_NAMES)}"
    )


def test_no_dangling_engines_py_module() -> None:
    """The pre-split monolith must be deleted — no `engines.py` next to the package."""
    repo_root = Path(__file__).resolve().parents[4]
    stale = repo_root / "game" / "strategy" / "interfaces" / "engines.py"
    assert not stale.exists(), (
        f"Stale single-file monolith still present: {stale}. "
        "Phase 1 must delete it after the package split."
    )
