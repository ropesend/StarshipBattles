"""PROJ-431 Phase 1d — AST regression guard for colonize + transfer validators.

Pins that :mod:`game.strategy.validation.colonize_validator` and
:mod:`game.strategy.validation.transfer_validator` operate on the typed
:class:`~game.strategy.data.bay_inventory.BayInventory` substrate
exclusively. The legacy mixed-shape ``ShipInstance.carried_items`` list
and the ``CarriedVehicle.from_any()`` discriminator must not appear in
either source file.

Sub-phase 1d scope: validators (this guard) plus the colonize order
handler and the transfer-handler dispatch branches (covered by a
sibling guard under ``tests/unit/strategy/engine/order_handlers/``).
"""
from __future__ import annotations

import ast
from pathlib import Path

# Smoke-import: ensure both modules still load after the Phase 1d
# migration. The AST checks below operate on the source files directly.
from game.strategy.validation import colonize_validator as _colonize_module  # noqa: F401
from game.strategy.validation import transfer_validator as _transfer_module  # noqa: F401


_REPO_ROOT = Path(__file__).resolve().parents[4]
COLONIZE_VALIDATOR_PATH = (
    _REPO_ROOT / "game" / "strategy" / "validation" / "colonize_validator.py"
)
TRANSFER_VALIDATOR_PATH = (
    _REPO_ROOT / "game" / "strategy" / "validation" / "transfer_validator.py"
)


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _carried_items_offenders(tree: ast.Module) -> list[str]:
    offenders: list[str] = []
    for node in ast.walk(tree):
        # Direct attribute access: ship.carried_items
        if isinstance(node, ast.Attribute) and node.attr == "carried_items":
            try:
                expr = ast.unparse(node)
            except Exception:  # Intentional broad catch: ast.unparse may fail on synthesised nodes.
                expr = f"<expr>.{node.attr}"
            offenders.append(f"line {node.lineno}: {expr}")
            continue
        # Indirect access: getattr(ship, 'carried_items', ...)
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
        except Exception:  # Intentional broad catch: ast.unparse may fail on synthesised nodes.
            expr = "<expr>.from_any(...)"
        offenders.append(f"line {node.lineno}: {expr}")
    return offenders


class TestColonizeValidatorNoLegacySubstrate:
    """``ColonizeValidator`` must read drop-pod inventory via
    ``ship.bay_inventory.pods`` — never via ``ship.carried_items``.
    """

    def test_no_carried_items_attribute_access(self) -> None:
        offenders = _carried_items_offenders(_parse(COLONIZE_VALIDATOR_PATH))
        assert not offenders, (
            "ColonizeValidator must not access `.carried_items` directly. "
            "Use `ship.bay_inventory.pods` instead. "
            f"Offenders: {offenders}"
        )

    def test_no_from_any_calls(self) -> None:
        offenders = _from_any_offenders(_parse(COLONIZE_VALIDATOR_PATH))
        assert not offenders, (
            "ColonizeValidator must not call `.from_any(...)`. "
            f"Offenders: {offenders}"
        )


class TestTransferValidatorNoLegacySubstrate:
    """``TransferValidator`` must walk staging / bay inventory via the
    typed accessors, not ``CarriedVehicle.from_any(...)``.
    """

    def test_no_carried_items_attribute_access(self) -> None:
        offenders = _carried_items_offenders(_parse(TRANSFER_VALIDATOR_PATH))
        assert not offenders, (
            "TransferValidator must not access `.carried_items` directly. "
            f"Offenders: {offenders}"
        )

    def test_no_from_any_calls(self) -> None:
        offenders = _from_any_offenders(_parse(TRANSFER_VALIDATOR_PATH))
        assert not offenders, (
            "TransferValidator must not call `.from_any(...)`. "
            f"Offenders: {offenders}"
        )
