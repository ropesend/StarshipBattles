"""
PROJ-343 T1.1 — Failing API test for fleet-to-fleet TransferDialog dispatch.

Bug shape (verified by planning instance 2026-05-04):
- TransferController emits `IssueTransferCommand(planet_id=None, target_fleet_id=<id>)`
  for the both-fleets branch.
- `TransferCommandHandler.execute` unconditionally calls `_resolve_planet(cmd.planet_id)`
  (game/strategy/engine/handlers/transfer.py:47-48). With `planet_id=None` the
  handler returns "Planet not found." and the fleet-to-fleet path never runs.
- Even if the planet guard were bypassed, the persisted `transfer_params` dict
  at lines 79-85 omits `target_fleet_id`, so the order would lose its target.

This test exercises the real handler with a fleet-to-fleet command and asserts
the dispatch succeeds and a TRANSFER order is queued carrying `target_fleet_id`.
Currently FAILS with "Planet not found.". Will PASS once T1.1 is fixed.

PROJ-491 Task 1.18 entry-check result:
  Constructing a minimal real ``GameSession`` requires ``GameConfig`` + a full
  ``SessionBootstrap.new_game_state(...)`` run, which is far heavier than the
  scope of a brittle-mock cleanup. The duck-typed ``MagicMock``-backed session
  below is the right shape for this unit-level handler test — the handler only
  reads ``_get_fleet_by_id`` / ``_get_planet_by_id`` and the active empire's
  fleet list, which are all naturally expressible as small lambdas. The real
  ``Fleet`` upgrade is similarly entangled with the duck-typed session
  (``fleet.resources.get_fleet_cargo_*`` is read once before validation).
  Recommendation: defer the upgrade to PROJ-493 once a ``minimal_game_session``
  fixture exists. Status: BLOCKED — see plan.md Current State entry for the
  Phase 1 Task 1.18 routing.
"""
from __future__ import annotations

from unittest.mock import MagicMock

from game.core.validation import ValidationResult
from game.strategy.data.order_types import OrderType
from game.strategy.engine.commands import IssueTransferCommand
from game.strategy.engine.handlers.transfer import TransferCommandHandler


def _make_transfer_handler_fleet(fleet_id: int, owner_id: int, location):
    """Minimal fleet stub sufficient for the handler's resolver + validator."""
    fleet = MagicMock()
    fleet.id = fleet_id
    fleet.owner_id = owner_id
    fleet.location = location
    fleet.orders = []
    fleet.path = []
    # cargo facade — passengers slot.
    fleet.resources = MagicMock()
    fleet.resources.get_fleet_cargo_capacity.return_value = 100
    fleet.resources.get_fleet_cargo_current.return_value = 50
    # Real method behavior so tests can inspect appended orders.
    fleet.add_order = lambda order: fleet.orders.append(order)
    return fleet


def _make_session_with_two_fleets():
    """Session with one empire, two fleets at the same hex, ready to transfer."""
    location = (3, 3)
    fleet_a = _make_transfer_handler_fleet(fleet_id=10, owner_id=0, location=location)
    fleet_b = _make_transfer_handler_fleet(fleet_id=11, owner_id=0, location=location)

    empire = MagicMock()
    empire.id = 0
    empire.fleets = [fleet_a, fleet_b]

    session = MagicMock()
    session.active_empire = empire
    session.empires = [empire]

    def _get_fleet_by_id(fleet_id):
        for f in empire.fleets:
            if f.id == fleet_id:
                return f
        return None

    session._get_fleet_by_id = _get_fleet_by_id
    # No planet lookup needed — fleet-to-fleet transfer.
    session._get_planet_by_id = lambda _id: None

    return session, fleet_a, fleet_b


def test_fleet_to_fleet_transfer_succeeds_and_order_carries_target_fleet_id():
    """`IssueTransferCommand(planet_id=None, target_fleet_id=B)` against fleet
    A must succeed and append a TRANSFER order to A whose `target` dict
    includes `target_fleet_id=B`."""
    session, fleet_a, fleet_b = _make_session_with_two_fleets()

    cmd = IssueTransferCommand(
        fleet_id=fleet_a.id,
        planet_id=None,
        cargo_type='passengers',
        direction='unload',
        amount=10,
        species_id=None,
        target_fleet_id=fleet_b.id,
    )

    handler = TransferCommandHandler()
    result = handler.execute(session, cmd)

    # Currently FAILS here: result is invalid with message "Planet not found."
    assert result.is_valid, (
        f"Expected fleet-to-fleet transfer to succeed; got: "
        f"is_valid={result.is_valid} message={result.message!r}"
    )

    # A TRANSFER order must be queued on the source fleet.
    assert len(fleet_a.orders) >= 1, "Source fleet got no order"
    transfer_orders = [o for o in fleet_a.orders if o.type == OrderType.TRANSFER]
    assert transfer_orders, "Source fleet has no TRANSFER order"

    # The order's target dict must carry `target_fleet_id`. Currently FAILS:
    # the prior arc's transfer.py:79-85 omits `target_fleet_id` from
    # `transfer_params`, so `target_fleet_id` is missing/None in the queued order.
    persisted_target = transfer_orders[-1].target
    assert isinstance(persisted_target, dict), "Order target should be a params dict"
    assert persisted_target.get('target_fleet_id') == fleet_b.id, (
        f"Queued TRANSFER order must persist target_fleet_id={fleet_b.id}; "
        f"got: {persisted_target!r}"
    )
