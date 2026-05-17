"""PROJ-431 Phase 1b — AST regression guard for ``minefield_resolver``.

Pins that :mod:`game.strategy.engine.minefield_resolver` reads and
writes the mine inventory through the typed
:class:`~game.strategy.data.bay_inventory.BayInventory` substrate rather
than the legacy mixed-shape ``ShipInstance.carried_items`` list.

Sub-phase 1b scope: ``minefield_resolver.py``, ``mine_group_service.py``
(``game/strategy/services/``), and ``issuer_adapter.py``. This guard is
scoped to the resolver only — the per-file AST guard is worthwhile here
because mine-counting and per-pass consumption are the most substantial
logic in the sub-phase 1b set.

Pattern: walk the module's AST and reject any
``Attribute(attr="carried_items")`` and any ``Attribute(attr="from_any")``
call. Mirrors the sub-phase 1a guard style.
"""
from __future__ import annotations

import ast
from pathlib import Path

# Smoke-import to catch wiring breakage during migration.
from game.strategy.engine import minefield_resolver as _minefield_resolver_module  # noqa: F401


RESOLVER_PATH = (
    Path(__file__).resolve().parents[4]
    / "game"
    / "strategy"
    / "engine"
    / "minefield_resolver.py"
)


def _parse_module() -> ast.Module:
    src = RESOLVER_PATH.read_text(encoding="utf-8")
    return ast.parse(src)


class TestMinefieldResolverNoLegacySubstrate:
    """``minefield_resolver`` must not touch ``carried_items`` or call
    ``CarriedVehicle.from_any()`` directly. The mine inventory is read
    via ``carrier.bay_inventory.bay`` and written via
    ``carrier.set_bay_inventory(BayInventory(...))``.
    """

    def test_no_carried_items_attribute_access(self) -> None:
        tree = _parse_module()
        offenders: list[str] = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Attribute):
                continue
            if node.attr != "carried_items":
                continue
            try:
                expr = ast.unparse(node)
            except Exception:  # Intentional broad catch: ast.unparse may fail on synthesised nodes; fall back to attr name.
                expr = f"<expr>.{node.attr}"
            offenders.append(f"line {node.lineno}: {expr}")
        assert not offenders, (
            "minefield_resolver must not access `.carried_items` directly. "
            "Use ShipInstance.bay_inventory / set_bay_inventory(...) instead. "
            f"Offenders: {offenders}"
        )

    def test_no_from_any_calls(self) -> None:
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
            "minefield_resolver must not call `.from_any(...)`. "
            f"Offenders: {offenders}"
        )
