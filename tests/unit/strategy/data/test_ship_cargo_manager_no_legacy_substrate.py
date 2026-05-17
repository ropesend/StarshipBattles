"""PROJ-431 Phase 1a — AST regression guard for ShipCargoManager.

Pins that :mod:`game.strategy.data.ship_cargo_manager` operates on the
typed :class:`~game.strategy.data.bay_inventory.BayInventory` substrate
exclusively. The legacy mixed-shape ``ShipInstance.carried_items`` list
and the ``CarriedVehicle.from_any()`` discriminator must not appear in
the source.

Sub-phase 1a migrates ONLY ``ShipCargoManager``. Other callers (FMS
order handlers, the serializer, validators, UI readers) still reach
into ``carried_items`` and migrate in sub-phases 1b–1f; this guard is
scoped to one file.

Pattern: walk the module's AST and reject any
``Attribute(attr="carried_items")`` whose value resolves to a
``ShipInstance`` (in practice: ``self._ship.carried_items`` or
``ship.carried_items``) and any ``Attribute(attr="from_any")`` call on a
``CarriedVehicle`` reference. This mirrors the AST-guard style PROJ-369
established for ``turn_engine.py``.
"""
from __future__ import annotations

import ast
from pathlib import Path

# Smoke-import: ensures the module under audit still loads after the
# Phase 1a migration. The AST checks below operate on the source file
# directly so they catch comments/strings differently than runtime
# introspection — but if the module fails to import, the typed-view
# wiring is broken and that's the more urgent failure to surface.
from game.strategy.data import ship_cargo_manager as _ship_cargo_manager_module  # noqa: F401


CARGO_MGR_PATH = (
    Path(__file__).resolve().parents[4]
    / "game"
    / "strategy"
    / "data"
    / "ship_cargo_manager.py"
)


def _parse_module() -> ast.Module:
    src = CARGO_MGR_PATH.read_text(encoding="utf-8")
    return ast.parse(src)


class TestShipCargoManagerNoLegacySubstrate:
    """ShipCargoManager must not reach into ``carried_items`` or call
    ``CarriedVehicle.from_any()`` — both are the legacy substrate that
    PROJ-431 Phase 1 is replacing with :class:`BayInventory`.
    """

    def test_no_carried_items_attribute_access(self) -> None:
        """No ``<expr>.carried_items`` attribute access anywhere in the
        module. The typed accessor is ``ship.bay_inventory`` plus
        ``ship.set_bay_inventory(...)`` for write-through.
        """
        tree = _parse_module()
        offenders: list[str] = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Attribute):
                continue
            if node.attr != "carried_items":
                continue
            # Reconstruct the expression for the error message.
            try:
                expr = ast.unparse(node)
            except Exception:  # Intentional broad catch: ast.unparse may fail on synthesised nodes; fall back to attr name.
                expr = f"<expr>.{node.attr}"
            offenders.append(f"line {node.lineno}: {expr}")
        assert not offenders, (
            "ShipCargoManager must not access `.carried_items` directly. "
            "Use ShipInstance.bay_inventory / set_bay_inventory(...) instead. "
            f"Offenders: {offenders}"
        )

    def test_no_from_any_calls(self) -> None:
        """No ``<expr>.from_any(...)`` call anywhere in the module.

        ``CarriedVehicle.from_any()`` is the legacy runtime discriminator
        for the mixed-shape ``carried_items`` list. The typed
        ``BayInventory.bay`` is a homogeneous ``list[CarriedVehicle]`` so
        no discrimination is needed.
        """
        tree = _parse_module()
        offenders: list[str] = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            f = node.func
            if not isinstance(f, ast.Attribute):
                continue
            if f.attr != "from_any":
                continue
            try:
                expr = ast.unparse(node)
            except Exception:  # Intentional broad catch: ast.unparse may fail on synthesised nodes.
                expr = "<expr>.from_any(...)"
            offenders.append(f"line {node.lineno}: {expr}")
        assert not offenders, (
            "ShipCargoManager must not call `.from_any(...)`. The typed "
            "BayInventory.bay is homogeneous; no discriminator needed. "
            f"Offenders: {offenders}"
        )

    def test_no_carried_vehicle_from_any_import_alias(self) -> None:
        """``CarriedVehicle.from_any`` must not be imported as a name
        alias either (e.g. ``from ... import from_any as _from_any``).
        Belt-and-braces over the call-site check above.
        """
        tree = _parse_module()
        offenders: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == "from_any":
                        offenders.append(
                            f"line {node.lineno}: from {node.module} import from_any"
                        )
        assert not offenders, (
            f"Found `from_any` name imports: {offenders}"
        )
