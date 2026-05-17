"""PROJ-431 Phase 1e — AST regression guard for UI/DTO/AI readers.

Pins that the read-only UI, DTO, and AI-controller surfaces operate on
the typed :class:`~game.strategy.data.bay_inventory.BayInventory`
substrate exclusively. The legacy mixed-shape
``ShipInstance.carried_items`` list and the
``CarriedVehicle.from_any()`` discriminator must not appear in any of
these four files.

Covered files (1e scope per the Phase 1 sub-phase tracker):

* ``game/ai/carrier_controller.py`` (AI launch-budget walker)
* ``game/strategy/facade/dto/fleet_dto.py`` (FleetInfo aggregation)
* ``game/ui/screens/fleet_menu_items.py`` (FMS row gates)
* ``game/ui/screens/strategy_detail_fmt.py`` (cargo summary formatter)
"""
from __future__ import annotations

import ast
from pathlib import Path

# Smoke-import: ensure each module still loads after the Phase 1e
# migration. The AST checks below operate on the source files directly.
from game.ai import carrier_controller as _carrier_module  # noqa: F401
from game.strategy.facade.dto import fleet_dto as _fleet_dto_module  # noqa: F401
from game.ui.screens import fleet_menu_items as _fleet_menu_items_module  # noqa: F401
from game.ui.screens import strategy_detail_fmt as _strategy_detail_fmt_module  # noqa: F401


_REPO_ROOT = Path(__file__).resolve().parents[3]
CARRIER_CONTROLLER_PATH = _REPO_ROOT / "game" / "ai" / "carrier_controller.py"
FLEET_DTO_PATH = (
    _REPO_ROOT / "game" / "strategy" / "facade" / "dto" / "fleet_dto.py"
)
FLEET_MENU_ITEMS_PATH = (
    _REPO_ROOT / "game" / "ui" / "screens" / "fleet_menu_items.py"
)
STRATEGY_DETAIL_FMT_PATH = (
    _REPO_ROOT / "game" / "ui" / "screens" / "strategy_detail_fmt.py"
)


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _carried_items_offenders(tree: ast.Module) -> list[str]:
    offenders: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "carried_items":
            try:
                expr = ast.unparse(node)
            except Exception:  # Intentional broad catch: ast.unparse can fail on synthetic nodes.
                expr = f"<expr>.{node.attr}"
            offenders.append(f"line {node.lineno}: {expr}")
            continue
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "getattr"
            and len(node.args) >= 2
            and isinstance(node.args[1], ast.Constant)
            and node.args[1].value == "carried_items"
        ):
            try:
                expr = ast.unparse(node)
            except Exception:  # Intentional broad catch.
                expr = "getattr(<expr>, 'carried_items', ...)"
            offenders.append(f"line {node.lineno}: {expr}")
    return offenders


def _from_any_offenders(tree: ast.Module) -> list[str]:
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
        except Exception:  # Intentional broad catch.
            expr = "<expr>.from_any(...)"
        offenders.append(f"line {node.lineno}: {expr}")
    return offenders


class TestCarrierControllerNoLegacySubstrate:
    def test_no_carried_items_attribute_access(self) -> None:
        offenders = _carried_items_offenders(_parse(CARRIER_CONTROLLER_PATH))
        assert not offenders, (
            "CarrierAIController must not access `.carried_items` "
            "directly; walk `carrier.bay_inventory.bay` and write back "
            "via `carrier.set_bay_inventory(...)`. "
            f"Offenders: {offenders}"
        )

    def test_no_from_any_calls(self) -> None:
        offenders = _from_any_offenders(_parse(CARRIER_CONTROLLER_PATH))
        assert not offenders, (
            "CarrierAIController must not call `.from_any(...)`. The "
            "bay slot is homogeneous `list[CarriedVehicle]`. "
            f"Offenders: {offenders}"
        )


class TestFleetDtoNoLegacySubstrate:
    def test_no_carried_items_attribute_access(self) -> None:
        offenders = _carried_items_offenders(_parse(FLEET_DTO_PATH))
        assert not offenders, (
            "FleetInfo aggregation must read through "
            "`ship.bay_inventory.bay` / `.pods`, not `.carried_items`. "
            f"Offenders: {offenders}"
        )

    def test_no_from_any_calls(self) -> None:
        offenders = _from_any_offenders(_parse(FLEET_DTO_PATH))
        assert not offenders, (
            "FleetInfo aggregation must not call `.from_any(...)`. "
            f"Offenders: {offenders}"
        )


class TestFleetMenuItemsNoLegacySubstrate:
    def test_no_carried_items_attribute_access(self) -> None:
        offenders = _carried_items_offenders(_parse(FLEET_MENU_ITEMS_PATH))
        assert not offenders, (
            "FMS row gates must read through `ship.bay_inventory.bay`, "
            "not `.carried_items`. "
            f"Offenders: {offenders}"
        )

    def test_no_from_any_calls(self) -> None:
        offenders = _from_any_offenders(_parse(FLEET_MENU_ITEMS_PATH))
        assert not offenders, (
            "FMS row gates must not call `.from_any(...)`. "
            f"Offenders: {offenders}"
        )


class TestStrategyDetailFmtNoLegacySubstrate:
    def test_no_carried_items_attribute_access(self) -> None:
        offenders = _carried_items_offenders(_parse(STRATEGY_DETAIL_FMT_PATH))
        assert not offenders, (
            "Cargo-summary formatter must read through "
            "`ship.bay_inventory.pods`, not `.carried_items`. "
            f"Offenders: {offenders}"
        )

    def test_no_from_any_calls(self) -> None:
        offenders = _from_any_offenders(_parse(STRATEGY_DETAIL_FMT_PATH))
        assert not offenders, (
            "Cargo-summary formatter must not call `.from_any(...)`. "
            f"Offenders: {offenders}"
        )
