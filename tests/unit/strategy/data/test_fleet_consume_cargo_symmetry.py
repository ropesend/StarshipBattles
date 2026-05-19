"""PROJ-451 Phase 2 Task 2.0 — Fleet cargo gate symmetry ratchet.

Pins the post-Phase-2 contract that ``Fleet.has_cargo_resources`` and
``Fleet.consume_cargo_resource`` agree on rounded-to-integer comparisons
against integer-typed fleet cargo storage.

Pre-fix asymmetry (DI-2026-05-18-006 data half, codex r5 review): the
*has* predicate at `game/strategy/data/fleet.py:267` rounds the float
``amount`` to ``int(round(amount))`` before comparison; the sibling
*consume* gate at `:285` compares the raw float. Result: against
``cargo=0`` and ``amount=0.5`` the has-side returns True while the
consume-side returns False.

Phase 2 Task 2.0 rounds the consume-side gate to match. This file pins
the post-fix symmetry.
"""
from __future__ import annotations

from tests.fixtures.strategy_entities import create_test_fleet


def _make_fleet_with_cargo(cargo: dict[str, int]):
    fleet = create_test_fleet(num_ships=1)
    for resource_type, amount in cargo.items():
        fleet.ships[0]._cargo_mgr.set_cargo(resource_type, amount)
    return fleet


def test_consume_and_has_agree_on_zero_cargo_against_half_amount():
    """cargo=0, amount=0.5 → both must return True (rounded gate).

    Pre-fix: ``has_cargo_resources`` returns True (``0 >= int(round(0.5))
    == 0``) while ``consume_cargo_resource`` returns False
    (``0 < 0.5``) — the asymmetry. Post-fix: both gates round, both
    return True; the engine-side ``_apply_resource_consumption``
    detects ``actually_consumed == 0`` and emits RESOURCE_SHORTAGE
    so the queue stall is visible (PROJ-451 Phase 2 Task 2.1).
    """
    fleet = _make_fleet_with_cargo({"metals": 0})
    assert fleet.has_cargo_resources({"metals": 0.5}) is True
    assert fleet.consume_cargo_resource("metals", 0.5) is True
    # Rounded-to-zero unload — cargo stays at 0.
    assert fleet.get_cargo_resource("metals") == 0.0


def test_consume_and_has_agree_on_one_cargo_against_half_amount():
    """cargo=1, amount=0.5 → both must return True, consume unloads 0.

    The rounded-amount gate accepts ``int(round(0.5)) == 0`` units as
    affordable when any non-negative cargo exists, and ``consume`` then
    unloads 0 units (cargo stays at 1). The Phase-12 truth-up contract
    handles the engine-side accounting (resources_consumed records the
    diff, which is 0).
    """
    fleet = _make_fleet_with_cargo({"metals": 1})
    assert fleet.has_cargo_resources({"metals": 0.5}) is True
    assert fleet.consume_cargo_resource("metals", 0.5) is True
    assert fleet.get_cargo_resource("metals") == 1.0


def test_consume_and_has_agree_on_one_cargo_against_point_six_amount():
    """cargo=1, amount=0.6 → both return True, consume unloads 1.

    ``int(round(0.6)) == 1``. Both gates accept; consume actually
    unloads one unit. ``resources_consumed`` records the diff = 1.0
    via the engine's truth-up.
    """
    fleet = _make_fleet_with_cargo({"metals": 1})
    assert fleet.has_cargo_resources({"metals": 0.6}) is True
    assert fleet.consume_cargo_resource("metals", 0.6) is True
    assert fleet.get_cargo_resource("metals") == 0.0


def test_consume_and_has_agree_on_two_cargo_against_three_amount():
    """cargo=2, amount=3.0 → both return False.

    Whole-number under-budget request. Both gates reject.
    """
    fleet = _make_fleet_with_cargo({"metals": 2})
    assert fleet.has_cargo_resources({"metals": 3.0}) is False
    assert fleet.consume_cargo_resource("metals", 3.0) is False
    assert fleet.get_cargo_resource("metals") == 2.0
