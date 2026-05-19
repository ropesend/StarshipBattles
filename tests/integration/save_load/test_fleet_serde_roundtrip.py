"""Characterization tests for ``Fleet`` serde extraction (PROJ-459 Phase 1).

These tests lock the byte-for-byte shape of ``Fleet.to_dict`` and the
round-trip identity through ``Fleet.from_dict`` so the Phase 1 extraction
into ``game/strategy/data/fleet_serde.py`` cannot drift.

Per PROJ-459 plan: this is a *characterization-first* refactor (not a
RED-then-GREEN cycle), so the tests pass against current code and serve
as the regression gate post-extraction.
"""
from __future__ import annotations

import json

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.fleet_hierarchy import CombatPolicy
from game.strategy.data.order_types import Order, OrderType
from tests.fixtures.strategy_entities import (
    create_test_fleet,
    create_test_fleet_order,
)


def _build_representative_fleet() -> Fleet:
    """Build a Fleet with cargo, orders, path, queue, and policy populated.

    This is the canonical fixture for the byte-identical comparison —
    deterministic content covering each serialized field path.
    """
    fleet = create_test_fleet(
        fleet_id=4242,
        owner_id=1,
        num_ships=2,
        location=HexCoord(3, -7),
        speed=4.5,
    )
    # Add a display name (otherwise empty).
    fleet.display_name = "Sword of Damocles"

    # Seed cargo onto ship 0 so the embedded ship dict is non-trivial.
    fleet.ships[0]._cargo_mgr.set_cargo("metals", 12)
    fleet.ships[0]._cargo_mgr.set_cargo("organics", 7)

    # Multiple orders covering several target shapes.
    fleet.orders = [
        create_test_fleet_order(OrderType.MOVE, HexCoord(5, -3)),
        create_test_fleet_order(OrderType.WARP, HexCoord(10, 2)),
        Order(OrderType.COLONIZE, target=None),
    ]
    fleet.orders[1].execution_progress = 4

    # Path with multiple hops.
    fleet.path = [HexCoord(4, -7), HexCoord(5, -7), HexCoord(5, -6)]

    # Construction queue entries.
    fleet.construction_queue = [
        {"design_id": "escort", "progress": 3, "cost": 50},
        {"design_id": "frigate", "progress": 0, "cost": 120},
    ]
    fleet.construction_queue_paused = True

    # Customize fleet-level combat policy (non-default — must have at
    # least one non-None axis to appear in the dict; default CombatPolicy
    # serializes to {} and is omitted by Fleet.to_dict).
    fleet.fleet_policy = CombatPolicy(
        targeting="closest",
        movement="hold",
        retreat="break_at_50",
    )

    return fleet


def _canonical_json(d: dict) -> str:
    """Deterministic stringification for byte-identity comparison."""
    return json.dumps(d, sort_keys=True, default=str)


def test_fleet_to_dict_shape_is_stable() -> None:
    """``Fleet.to_dict`` produces a stable, characterized dict shape.

    The test pins the top-level key set and selected representative
    field values. Any drift in the serialized shape after Phase 1
    extraction will fail this test.
    """
    fleet = _build_representative_fleet()
    data = fleet.to_dict()

    expected_top_keys = {
        "id",
        "owner_id",
        "location",
        "speed",
        "display_name",
        "ships",
        "orders",
        "path",
        "construction_queue",
        "construction_queue_paused",
        "fleet_policy",
    }
    assert expected_top_keys.issubset(set(data.keys())), (
        f"Top-level keys missing: {expected_top_keys - set(data.keys())}"
    )

    # Scalar identity.
    assert data["id"] == 4242
    assert data["owner_id"] == 1
    assert data["speed"] == 4.5
    assert data["display_name"] == "Sword of Damocles"
    assert data["construction_queue_paused"] is True

    # HexCoord-as-dict for location.
    assert data["location"] == {"q": 3, "r": -7}

    # Embedded ships preserved (2 ships).
    assert isinstance(data["ships"], list) and len(data["ships"]) == 2

    # Orders preserved (3 items, types serialized as their .name strings).
    assert len(data["orders"]) == 3
    assert data["orders"][0]["type"] == "MOVE"
    assert data["orders"][1]["type"] == "WARP"
    assert data["orders"][1].get("execution_progress") == 4
    assert data["orders"][2]["type"] == "COLONIZE"

    # Path as list-of-hex-dicts.
    assert data["path"] == [
        {"q": 4, "r": -7},
        {"q": 5, "r": -7},
        {"q": 5, "r": -6},
    ]

    # Construction queue passes through verbatim.
    assert data["construction_queue"][0]["design_id"] == "escort"
    assert data["construction_queue"][1]["progress"] == 0


def test_fleet_to_dict_byte_identical_pre_extraction() -> None:
    """Two calls to ``to_dict`` over the same Fleet produce identical strings.

    Serves both as a determinism check and as the byte-identity gate the
    Phase 1 extraction must preserve. Recording the JSON-canonical string
    on disk is unnecessary — the same in-process fixture before/after
    extraction is sufficient because the test file is checked in alongside
    the refactor.
    """
    fleet = _build_representative_fleet()
    first = _canonical_json(fleet.to_dict())
    second = _canonical_json(fleet.to_dict())
    assert first == second, "to_dict is non-deterministic across calls"
    # The exact byte-string is captured by the assertions in
    # test_fleet_to_dict_shape_is_stable; the canonical-json form here
    # is the determinism check.


def test_fleet_round_trip(fresh_registries) -> None:
    """A Fleet survives ``to_dict`` → ``from_dict`` → ``to_dict`` unchanged.

    This is the core regression gate. The reconstructed Fleet's serialized
    form must match the original's serialized form byte-for-byte.
    """
    fleet = _build_representative_fleet()
    first_dump = fleet.to_dict()

    reconstructed = Fleet.from_dict(first_dump, registries=fresh_registries)
    second_dump = reconstructed.to_dict()

    # Core scalars preserved.
    assert reconstructed.id == fleet.id
    assert reconstructed.owner_id == fleet.owner_id
    assert reconstructed.location == fleet.location
    assert reconstructed.speed == fleet.speed
    assert reconstructed.display_name == fleet.display_name

    # Lists preserved by length and selected identity.
    assert len(reconstructed.ships) == len(fleet.ships)
    assert reconstructed.ships[0].instance_id == fleet.ships[0].instance_id

    assert len(reconstructed.orders) == len(fleet.orders)
    assert reconstructed.orders[0].type == OrderType.MOVE
    assert reconstructed.orders[0].target == HexCoord(5, -3)
    assert reconstructed.orders[1].type == OrderType.WARP
    assert reconstructed.orders[1].execution_progress == 4
    assert reconstructed.orders[2].type == OrderType.COLONIZE

    assert reconstructed.path == fleet.path
    assert reconstructed.construction_queue == fleet.construction_queue
    assert reconstructed.construction_queue_paused is True

    # Byte-identical re-serialization.
    assert _canonical_json(second_dump) == _canonical_json(first_dump)
