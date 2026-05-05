"""PROJ-333 Phase 1: ProductionEngine consumption + affordability characterization.

Pins resource math + affordability routing: planet stockpile vs fleet
cargo vs empire pool dispatch via `context_type`, shortage-event
emission, completion epsilon, design-cost cache, and the
`_calculate_tick_expenditure` math (zero-rate-required-resource halts,
already-complete short-circuit).

Companion file: ``test_production_engine_queue.py`` covers queue
iteration semantics on the same ProductionEngine class.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.planet import Planet
from game.strategy.engine.production_engine import (
    COMPLETION_EPSILON,
    ProductionEngine,
)


@pytest.fixture
def engine(fresh_registries):
    return ProductionEngine(registries=fresh_registries)


@pytest.fixture
def empire():
    emp = MagicMock(spec=Empire)
    emp.id = "emp1"
    emp.resource_pool = {"metals": 100.0}
    emp.has_resources.return_value = True
    emp.consume_resources = MagicMock()
    return emp


# ---------------------------------------------------------------------------
# _check_affordability dispatch by context_type
# ---------------------------------------------------------------------------


def test_check_affordability_routes_to_planet_stockpile_when_context_planet(engine, empire):
    """`context_type='planet'` calls `colony.has_stockpile`."""
    colony = MagicMock(spec=Planet)
    colony.context_type = "planet"
    colony.has_stockpile.return_value = True

    result = engine._check_affordability(empire, {"metals": 5.0}, colony)

    colony.has_stockpile.assert_called_once_with({"metals": 5.0})
    assert result is True


def test_check_affordability_routes_to_fleet_cargo_when_context_fleet(engine, empire):
    """`context_type='fleet'` calls `fleet.has_cargo_resources`."""
    fleet = MagicMock(spec=Fleet)
    fleet.context_type = "fleet"
    fleet.has_cargo_resources.return_value = False

    result = engine._check_affordability(empire, {"metals": 3.0}, fleet)

    fleet.has_cargo_resources.assert_called_once_with({"metals": 3.0})
    assert result is False


def test_check_affordability_falls_back_to_empire_pool_when_no_context_type(engine, empire):
    """Bare object without `context_type` falls back to empire.has_resources."""
    bare = object()
    empire.has_resources.return_value = True

    assert engine._check_affordability(empire, {"metals": 1.0}, bare) is True
    empire.has_resources.assert_called_once_with({"metals": 1.0})


# ---------------------------------------------------------------------------
# _apply_resource_consumption dispatch
# ---------------------------------------------------------------------------


def test_apply_resource_consumption_updates_resources_consumed_dict(engine, empire):
    """Consumption sums into the existing `resources_consumed[res]` entry."""
    colony = MagicMock(spec=Planet)
    colony.context_type = "planet"
    colony.consume_from_stockpile = MagicMock()
    item = {"resources_consumed": {"metals": 2.0}}

    engine._apply_resource_consumption(empire, item, {"metals": 3.0}, colony)

    assert item["resources_consumed"]["metals"] == 5.0
    colony.consume_from_stockpile.assert_called_once_with("metals", 3.0)


def test_apply_resource_consumption_routes_to_fleet_cargo_when_context_fleet(engine, empire):
    """PROJ-345 T3.5: `context_type='fleet'` calls `fleet.consume_cargo_resource`.

    Pins the fleet-context branch of `_apply_resource_consumption`. The
    empire pool is NOT touched, and the per-resource cargo consumer is
    called with (resource, amount); resources_consumed is summed.
    """
    fleet = MagicMock(spec=Fleet)
    fleet.context_type = "fleet"
    fleet.consume_cargo_resource = MagicMock()
    item = {"resources_consumed": {"metals": 1.5}}

    engine._apply_resource_consumption(empire, item, {"metals": 2.5}, fleet)

    fleet.consume_cargo_resource.assert_called_once_with("metals", 2.5)
    assert item["resources_consumed"]["metals"] == 4.0
    empire.consume_resources.assert_not_called()


def test_apply_resource_consumption_falls_back_to_empire_pool_when_no_context(engine, empire):
    """PROJ-345 T3.5: no `context_type` on owner → empire.consume_resources
    is the consumer. Pins the empire-pool fallback branch (third branch);
    neither stockpile nor cargo APIs are touched.
    """
    bare = object()  # No context_type attribute at all.
    item = {"resources_consumed": {"metals": 0.0}}

    engine._apply_resource_consumption(empire, item, {"metals": 7.0}, bare)

    empire.consume_resources.assert_called_once_with("metals", 7.0)
    assert item["resources_consumed"]["metals"] == 7.0


def test_apply_resource_consumption_skips_zero_amount_resources(engine, empire):
    """Resources with `amount <= 0` are not consumed (guard at line 601)."""
    fleet = MagicMock(spec=Fleet)
    fleet.context_type = "fleet"
    fleet.consume_cargo_resource = MagicMock()
    item = {"resources_consumed": {}}

    engine._apply_resource_consumption(
        empire, item, {"metals": 0.0, "organics": 5.0}, fleet,
    )

    # Only the non-zero resource was consumed.
    fleet.consume_cargo_resource.assert_called_once_with("organics", 5.0)
    assert item["resources_consumed"] == {"organics": 5.0}


# ---------------------------------------------------------------------------
# _log_resource_shortage limiting-resource picker
# ---------------------------------------------------------------------------


def test_log_resource_shortage_picks_largest_shortfall_ratio_as_limiting():
    """Limiting resource = max (needed/available) ratio across resources."""
    captured: list = []

    class _Bus:
        def log_event(self, event_type, **kwargs):
            captured.append((event_type, kwargs))

    from game.core.registry import GameRegistries
    bus = _Bus()
    engine = ProductionEngine(
        registries=GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={}),
        event_bus=bus,
    )

    empire = MagicMock(spec=Empire)
    empire.id = 1
    empire.resource_pool = {"metals": 100.0, "organics": 0.5}

    colony = MagicMock(spec=Planet)
    colony.context_type = "planet"
    colony.get_stockpile.side_effect = lambda res: {"metals": 100.0, "organics": 0.5}[res]

    item = {"design_id": "frig", "type": "ship"}
    engine._log_resource_shortage(empire, item, {"metals": 5.0, "organics": 5.0}, colony)

    assert len(captured) == 1
    payload = captured[0][1]
    assert payload["limiting_resource"] == "organics"
    assert payload["available"] == 0.5
    assert payload["needed"] == 5.0


def test_log_resource_shortage_uses_fleet_cargo_for_available_in_fleet_context():
    """PROJ-345 T3.5: `context_type='fleet'` reads `fleet.get_cargo_resource`.

    Pins the fleet-context branch of `_log_resource_shortage`
    (production_engine.py:545). The shortfall ratio is computed from
    cargo levels, NOT from empire.resource_pool or planet stockpile,
    and the emitted RESOURCE_SHORTAGE event records the fleet-cargo
    available value plus the fleet's hex location.
    """
    captured: list = []

    class _Bus:
        def log_event(self, event_type, **kwargs):
            captured.append((event_type, kwargs))

    from game.core.registry import GameRegistries
    eng = ProductionEngine(
        registries=GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={}),
        event_bus=_Bus(),
    )

    empire = MagicMock(spec=Empire)
    empire.id = 7
    # Empire has plenty — but fleet cargo is the source of truth for fleet ctx.
    empire.resource_pool = {"metals": 99999.0, "organics": 99999.0}

    fleet = MagicMock(spec=Fleet)
    fleet.context_type = "fleet"
    fleet.location = MagicMock()
    fleet.location.q = 3
    fleet.location.r = -2
    cargo = {"metals": 100.0, "organics": 0.5}
    fleet.get_cargo_resource.side_effect = lambda res: cargo[res]

    item = {"design_id": "frig", "type": "ship"}
    eng._log_resource_shortage(empire, item, {"metals": 5.0, "organics": 5.0}, fleet)

    assert len(captured) == 1
    payload = captured[0][1]
    # Limiting resource picked using FLEET cargo (organics: 5.0/0.5 worst).
    assert payload["limiting_resource"] == "organics"
    assert payload["available"] == 0.5
    assert payload["needed"] == 5.0
    assert payload["empire_id"] == 7
    assert payload["location_hex"] == [3, -2]
    # `get_cargo_resource` was the source — not stockpile, not pool.
    assert fleet.get_cargo_resource.call_count >= 1


def test_log_resource_shortage_uses_empire_pool_when_no_context_type():
    """PROJ-345 T3.5: no `context_type` on owner → `empire.resource_pool`
    is the source. Pins the third (fallback) branch at
    production_engine.py:548. Neither `get_stockpile` nor
    `get_cargo_resource` is consulted.
    """
    captured: list = []

    class _Bus:
        def log_event(self, event_type, **kwargs):
            captured.append((event_type, kwargs))

    from game.core.registry import GameRegistries
    eng = ProductionEngine(
        registries=GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={}),
        event_bus=_Bus(),
    )

    empire = MagicMock(spec=Empire)
    empire.id = 9
    empire.resource_pool = {"metals": 1.0}

    bare = object()  # No context_type attribute → fallback branch.
    item = {"design_id": "frig", "type": "ship"}

    eng._log_resource_shortage(empire, item, {"metals": 10.0}, bare)

    assert len(captured) == 1
    payload = captured[0][1]
    assert payload["limiting_resource"] == "metals"
    assert payload["available"] == 1.0
    assert payload["needed"] == 10.0
    assert payload["location_hex"] is None  # bare object has no `location`.


def test_log_resource_shortage_emitted_once_per_item_per_turn(engine, empire):
    """Subsequent ticks within a turn do not re-log once `_shortage_logged`."""
    captured: list = []

    class _Bus:
        def log_event(self, event_type, **kwargs):
            captured.append(event_type)

    from game.core.registry import GameRegistries
    eng = ProductionEngine(
        registries=GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={}),
        event_bus=_Bus(),
    )

    colony = MagicMock(spec=Planet)
    colony.context_type = "planet"
    colony.has_stockpile.return_value = False
    colony.get_stockpile.side_effect = lambda res: 0.0
    colony.stockpile = {}

    item = {
        "design_id": "f",
        "type": "ship",
        "total_cost": {"A": 100.0},
        "resources_consumed": {"A": 0.0},
    }
    queue = [item]

    # Tick 1 logs; tick 2 does not.
    for tick in (1, 2):
        eng._process_queue_tick_dynamic(
            queue, empire, tick, MagicMock(), None,
            {"A": 500.0}, colony, is_complex_only=False,
        )

    assert len(captured) == 1


# ---------------------------------------------------------------------------
# _check_item_completion epsilon
# ---------------------------------------------------------------------------


def test_check_item_completion_uses_completion_epsilon(engine):
    """Item is complete when remaining < COMPLETION_EPSILON."""
    item_done = {
        "total_cost": {"A": 100.0},
        "resources_consumed": {"A": 100.0 - (COMPLETION_EPSILON / 2)},
    }
    item_undone = {
        "total_cost": {"A": 100.0},
        "resources_consumed": {"A": 100.0 - (COMPLETION_EPSILON * 5)},
    }
    assert engine._check_item_completion(item_done) is True
    assert engine._check_item_completion(item_undone) is False


# ---------------------------------------------------------------------------
# _complete_item: pop + spawner dispatch
# ---------------------------------------------------------------------------


def test_complete_item_pops_queue_and_calls_spawner(engine, empire):
    """`_complete_item` removes the head and forwards to ProductionSpawner."""
    item = {"design_id": "frigate", "type": "ship"}
    queue = [item, {"design_id": "later"}]
    engine._spawner.spawn_completed_item = MagicMock()
    colony = MagicMock(spec=Planet)

    engine._complete_item(queue, item, empire, colony, MagicMock(), None, 1)

    assert queue[0]["design_id"] == "later"
    engine._spawner.spawn_completed_item.assert_called_once()


# ---------------------------------------------------------------------------
# _calculate_tick_expenditure math
# ---------------------------------------------------------------------------


def test_calculate_tick_expenditure_returns_none_for_zero_rate_required_resource(engine):
    """Zero rate on a still-required resource halts the item (None return)."""
    item = {
        "total_cost": {"A": 50.0, "B": 50.0},
        "resources_consumed": {"A": 0.0, "B": 0.0},
    }
    result = engine._calculate_tick_expenditure(item, 1.0, {"A": 100.0, "B": 0.0})
    assert result is None


def test_calculate_tick_expenditure_returns_empty_for_already_complete_item(engine):
    """Item with no remaining cost returns an empty TickExpenditure (not None)."""
    item = {
        "total_cost": {"A": 10.0},
        "resources_consumed": {"A": 10.0},
    }
    result = engine._calculate_tick_expenditure(item, 1.0, {"A": 100.0})
    assert result is not None
    assert result.remaining_cost == {}
    assert result.cost_this_step == {}


# ---------------------------------------------------------------------------
# _update_turns_remaining
# ---------------------------------------------------------------------------


def test_update_turns_remaining_zero_when_no_ticks_needed(engine):
    """`max_ticks_needed == 0` writes `turns_remaining = 0`."""
    from game.strategy.engine.production_engine import TickExpenditure

    item = {"turns_remaining": 0.5}
    engine._update_turns_remaining(
        item,
        TickExpenditure(remaining_cost={}, ticks_to_spend=0.0,
                        cost_this_step={}, max_ticks_needed=0.0),
    )
    assert item["turns_remaining"] == 0


# ---------------------------------------------------------------------------
# _calculate_design_cost caches result on the design dict
# ---------------------------------------------------------------------------


def test_calculate_design_cost_caches_result_in_design_data(engine):
    """First call computes cost; subsequent calls reuse `total_resource_cost`."""
    design = {"layers": {}}
    first = engine._calculate_design_cost(design)
    assert "total_resource_cost" in design
    assert design["total_resource_cost"] is first

    # Mutate the cache to a sentinel; if it wasn't reused, recomputation
    # would replace it with the real (likely empty) cost dict.
    design["total_resource_cost"] = {"sentinel": 999.0}
    second = engine._calculate_design_cost(design)
    assert second == {"sentinel": 999.0}
