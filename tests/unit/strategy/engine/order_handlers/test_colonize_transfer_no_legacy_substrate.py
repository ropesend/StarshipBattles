"""PROJ-431 Phase 1d — AST regression guard for colonize + transfer handlers.

Pins that the colonize order handler and the transfer-handler dispatch
branches operate on the typed
:class:`~game.strategy.data.bay_inventory.BayInventory` substrate
exclusively. The legacy mixed-shape ``ShipInstance.carried_items`` list
and the ``CarriedVehicle.from_any()`` discriminator must not appear in
either source file.

The transfer dispatch branches drive both the planet staging yard path
(``planet.staging_yard`` is a list of dicts — still on the legacy
substrate, deferred to a later phase) AND the fleet bay path (which
this guard pins to the typed substrate). The guard rejects
``carried_items``/``from_any`` attribute / call usage that targets a
``ShipInstance`` or ``CarriedVehicle``. Bare ``from_any`` references
that target other types (none today) would still be visible to a code
reviewer.
"""
from __future__ import annotations

import ast
from pathlib import Path

# Smoke-import: ensure both modules still load after the Phase 1d
# migration. The AST checks below operate on the source files directly.
from game.strategy.engine.order_handlers import colonize as _colonize_module  # noqa: F401
from game.strategy.engine.order_handlers import transfer_branches as _branches_module  # noqa: F401


_REPO_ROOT = Path(__file__).resolve().parents[5]
COLONIZE_HANDLER_PATH = (
    _REPO_ROOT
    / "game"
    / "strategy"
    / "engine"
    / "order_handlers"
    / "colonize.py"
)
TRANSFER_BRANCHES_PATH = (
    _REPO_ROOT
    / "game"
    / "strategy"
    / "engine"
    / "order_handlers"
    / "transfer_branches.py"
)


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _carried_items_offenders(tree: ast.Module) -> list[str]:
    offenders: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "carried_items":
            try:
                expr = ast.unparse(node)
            except Exception:  # Intentional broad catch.
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


class TestColonizeHandlerNoLegacySubstrate:
    def test_no_carried_items_attribute_access(self) -> None:
        offenders = _carried_items_offenders(_parse(COLONIZE_HANDLER_PATH))
        assert not offenders, (
            "ColonizeHandler must not access `.carried_items` directly. "
            "Drop-pod deploy walks `ship.bay_inventory.pods`. "
            f"Offenders: {offenders}"
        )

    def test_no_from_any_calls(self) -> None:
        offenders = _from_any_offenders(_parse(COLONIZE_HANDLER_PATH))
        assert not offenders, (
            "ColonizeHandler must not call `.from_any(...)`. "
            f"Offenders: {offenders}"
        )


class TestTransferBranchesNoLegacySubstrate:
    def test_no_carried_items_attribute_access(self) -> None:
        offenders = _carried_items_offenders(_parse(TRANSFER_BRANCHES_PATH))
        assert not offenders, (
            "TransferHandler dispatch branches must not access "
            "`.carried_items` directly. The fleet-side drop-pod / "
            "carried-vehicle paths walk `ship.bay_inventory` and write "
            "via `ship.set_bay_inventory(...)`. "
            f"Offenders: {offenders}"
        )

    def test_no_from_any_calls(self) -> None:
        offenders = _from_any_offenders(_parse(TRANSFER_BRANCHES_PATH))
        assert not offenders, (
            "TransferHandler dispatch branches must not call "
            "`.from_any(...)`. The fleet-side bay is typed; legacy "
            "staging-yard reads route via `_yard_pod_entries(...)`. "
            f"Offenders: {offenders}"
        )
