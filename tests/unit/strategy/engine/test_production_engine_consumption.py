"""PROJ-333 Phase 1: ProductionEngine consumption + affordability characterization.

Pins resource math + affordability routing through the unified
``IProductionResourceSource`` protocol (PROJ-436 Phase 8), shortage-event
emission, completion epsilon, design-cost cache, and the
`_calculate_tick_expenditure` math (zero-rate-required-resource halts,
already-complete short-circuit).

PROJ-436 Phase 8: the engine no longer dispatches on
``colony_or_fleet.context_type``. Both Planet and Fleet satisfy
``IProductionResourceSource`` via
``production_has_resources`` / ``production_get_resource`` /
``production_consume_resource`` polymorphic delegators; this test
file mirrors that contract.

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
from game.strategy.events.event_types import EventType


@pytest.fixture
def engine(fresh_registries):
    return ProductionEngine(registries=fresh_registries)


@pytest.fixture
def empire():
    # PROJ-443 Phase 5c: dropped `emp.consume_resources = MagicMock()` —
    # `Empire.consume_resources` was deleted in PROJ-436 Phase 5; the inert
    # attachment masked the rename rather than catching a real call.
    emp = MagicMock(spec=Empire)
    emp.id = "emp1"
    emp.resource_pool = {"metals": 100.0}
    emp.has_resources.return_value = True
    return emp


# ---------------------------------------------------------------------------
# _check_affordability dispatch through IProductionResourceSource
# ---------------------------------------------------------------------------


def test_check_affordability_routes_to_planet_production_method(engine, empire):
    """Planet's ``production_has_resources`` is the engine's read path.

    PROJ-436 Phase 8: the engine no longer dispatches on
    ``context_type``; Planet satisfies ``IProductionResourceSource``
    via ``production_has_resources`` which delegates to the existing
    ``has_stockpile`` stockpile API.
    """
    colony = MagicMock(spec=Planet)
    colony.production_has_resources.return_value = True

    result = engine._check_affordability(empire, {"metals": 5.0}, colony)

    colony.production_has_resources.assert_called_once_with({"metals": 5.0})
    assert result is True


def test_check_affordability_routes_to_fleet_production_method(engine, empire):
    """Fleet's ``production_has_resources`` is the engine's read path.

    PROJ-436 Phase 8: Fleet satisfies ``IProductionResourceSource``
    via ``production_has_resources`` which delegates to the existing
    ``has_cargo_resources`` cargo API.
    """
    fleet = MagicMock(spec=Fleet)
    fleet.production_has_resources.return_value = False

    result = engine._check_affordability(empire, {"metals": 3.0}, fleet)

    fleet.production_has_resources.assert_called_once_with({"metals": 3.0})
    assert result is False


def test_check_affordability_raises_when_not_production_resource_source(engine, empire):
    """PROJ-436 Phase 8: a bare object lacking ``production_has_resources``
    raises ``AttributeError``.

    The Phase 5 ``ValueError`` contract on ``context_type`` is gone —
    Phase 8 collapsed the dispatch into a uniform protocol call. An
    owner that does not satisfy ``IProductionResourceSource`` is a
    programmer error, surfaced as the natural ``AttributeError`` raised
    by Python when the method is missing.
    """
    bare = object()
    with pytest.raises(AttributeError, match="production_has_resources"):
        engine._check_affordability(empire, {"metals": 1.0}, bare)


# ---------------------------------------------------------------------------
# _apply_resource_consumption dispatch
# ---------------------------------------------------------------------------


def test_apply_resource_consumption_updates_resources_consumed_dict(engine, empire):
    """Consumption sums into the existing `resources_consumed[res]` entry.

    PROJ-436 Phase 8: the engine calls
    ``planet.production_consume_resource`` (which delegates to
    ``consume_from_stockpile`` on a real Planet). PROJ-436 Phase 12:
    the recorded amount is the ``production_get_resource`` before/after
    diff, not the requested ``amount`` — mock the diff to simulate
    Planet's float-exact consumption (3.0 consumed against 100.0
    starting balance).
    """
    colony = MagicMock(spec=Planet)
    colony.production_get_resource.side_effect = [100.0, 97.0]  # before, after
    item = {"resources_consumed": {"metals": 2.0}}

    engine._apply_resource_consumption(empire, item, {"metals": 3.0}, colony)

    # 2.0 (prior) + 3.0 (diff) = 5.0.
    assert item["resources_consumed"]["metals"] == 5.0
    colony.production_consume_resource.assert_called_once_with("metals", 3.0)


def test_apply_resource_consumption_routes_to_fleet_production_method(engine, empire):
    """PROJ-436 Phase 8: Fleet's ``production_consume_resource`` is the
    engine's write path; on a real Fleet this delegates to the existing
    ``consume_cargo_resource`` cargo API. The empire pool is NOT touched,
    and ``resources_consumed`` is summed. PROJ-436 Phase 12: recorded
    amount is the before/after diff — mock 2.5 actually-consumed.
    """
    fleet = MagicMock(spec=Fleet)
    fleet.production_get_resource.side_effect = [50.0, 47.5]  # before, after
    item = {"resources_consumed": {"metals": 1.5}}

    engine._apply_resource_consumption(empire, item, {"metals": 2.5}, fleet)

    fleet.production_consume_resource.assert_called_once_with("metals", 2.5)
    # 1.5 (prior) + 2.5 (diff) = 4.0.
    assert item["resources_consumed"]["metals"] == 4.0


def test_apply_resource_consumption_raises_when_not_production_resource_source(engine, empire):
    """PROJ-436 Phase 8: a bare object lacking the
    ``IProductionResourceSource`` Protocol raises ``AttributeError``.

    The Phase 5 ``ValueError`` contract on ``context_type`` is gone —
    Phase 8 collapsed the dispatch into a uniform protocol call. An
    owner that does not satisfy ``IProductionResourceSource`` is a
    programmer error. PROJ-436 Phase 12: the failing attribute is now
    ``production_get_resource`` (the first Protocol method called in
    the diff path) rather than ``production_consume_resource``.
    """
    bare = object()
    item = {"resources_consumed": {"metals": 0.0}}

    with pytest.raises(AttributeError, match="production_get_resource"):
        engine._apply_resource_consumption(empire, item, {"metals": 7.0}, bare)


@pytest.mark.xfail(
    reason="PROJ-451 Phase 1 RED — fixed by Phase 2 (emit RESOURCE_SHORTAGE on zero-consume).",
    strict=True,
)
def test_apply_resource_consumption_emits_shortage_on_zero_consume(fresh_registries, empire):
    """PROJ-451 Phase 1 RED: DI-2026-05-18-006 unit-test analog.

    When ``production_get_resource`` reports a constant before/after
    value (so ``actually_consumed == 0``) despite a positive
    requested amount, the engine must emit a ``RESOURCE_SHORTAGE``
    event so the player sees a clear shortage indicator. Pre-fix,
    ``_apply_resource_consumption`` silently records 0 progress and
    returns, leaving the queue stalled without UX feedback.

    Scope (per Phase 1 docstring + decisions.md): exercises the
    zero-consume / no-diff path only (``production_consume_resource``
    returns True). The contract-breach path where
    ``production_consume_resource`` returns False after affordability
    passed is deferred to Phase 3 (DI-007 bool-return-handling decision).
    """
    event_bus = MagicMock()
    engine_with_bus = ProductionEngine(
        registries=fresh_registries, event_bus=event_bus,
    )
    mock_source = MagicMock(spec=Fleet)
    # Constant before/after — actually_consumed == 0.
    mock_source.production_get_resource.return_value = 1.0
    mock_source.production_consume_resource.return_value = True
    mock_source.location = None

    item = {
        "design_id": "fractional-x",
        "type": "ship",
        "resources_consumed": {"metals": 0.0},
    }

    engine_with_bus._apply_resource_consumption(
        empire, item, {"metals": 0.1}, mock_source,
    )

    shortage_calls = [
        call for call in event_bus.log_event.call_args_list
        if call.args and call.args[0] == EventType.RESOURCE_SHORTAGE
    ]
    assert shortage_calls, (
        "Engine recorded actually_consumed == 0 against a non-zero "
        "requested amount but did not emit RESOURCE_SHORTAGE."
    )


def test_apply_resource_consumption_skips_zero_amount_resources(engine, empire):
    """Resources with `amount <= 0` are not consumed (guard preserved).

    PROJ-436 Phase 12: the before/after diff math also runs only for
    non-zero amounts; ``production_get_resource`` is mocked so the
    one non-zero call has numeric inputs.
    """
    fleet = MagicMock(spec=Fleet)
    fleet.production_get_resource.side_effect = [50.0, 45.0]  # before, after
    item = {"resources_consumed": {}}

    engine._apply_resource_consumption(
        empire, item, {"metals": 0.0, "organics": 5.0}, fleet,
    )

    # Only the non-zero resource was consumed.
    fleet.production_consume_resource.assert_called_once_with("organics", 5.0)
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
    colony.production_get_resource.side_effect = lambda res: {"metals": 100.0, "organics": 0.5}[res]

    item = {"design_id": "frig", "type": "ship"}
    engine._log_resource_shortage(empire, item, {"metals": 5.0, "organics": 5.0}, colony)

    assert len(captured) == 1
    payload = captured[0][1]
    assert payload["limiting_resource"] == "organics"
    assert payload["available"] == 0.5
    assert payload["needed"] == 5.0


def test_log_resource_shortage_uses_fleet_cargo_for_available_for_fleet_owner():
    """PROJ-436 Phase 8: ``Fleet.production_get_resource`` is the source
    of truth for shortage event ``available`` when the owner is a Fleet.

    On a real Fleet, ``production_get_resource`` delegates to
    ``get_cargo_resource``. The shortfall ratio is computed from cargo
    levels, NOT from empire.resource_pool, and the emitted
    RESOURCE_SHORTAGE event records the fleet-cargo available value
    plus the fleet's hex location.
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
    # Empire has plenty — but fleet cargo is the source of truth.
    empire.resource_pool = {"metals": 99999.0, "organics": 99999.0}

    fleet = MagicMock(spec=Fleet)
    fleet.location = MagicMock()
    fleet.location.q = 3
    fleet.location.r = -2
    cargo = {"metals": 100.0, "organics": 0.5}
    fleet.production_get_resource.side_effect = lambda res: cargo[res]

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
    # `production_get_resource` was the source — not stockpile, not pool.
    assert fleet.production_get_resource.call_count >= 1


def test_log_resource_shortage_raises_when_not_production_resource_source():
    """PROJ-436 Phase 8: a bare object lacking
    ``production_get_resource`` raises ``AttributeError``.

    The Phase 5 ``ValueError`` contract on ``context_type`` is gone —
    Phase 8 collapsed the dispatch into a uniform protocol call.
    """
    class _Bus:
        def log_event(self, event_type, **kwargs):
            pass

    from game.core.registry import GameRegistries
    eng = ProductionEngine(
        registries=GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={}),
        event_bus=_Bus(),
    )

    empire = MagicMock(spec=Empire)
    empire.id = 9

    bare = object()
    item = {"design_id": "frig", "type": "ship"}

    with pytest.raises(AttributeError, match="production_get_resource"):
        eng._log_resource_shortage(empire, item, {"metals": 10.0}, bare)


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
    colony.production_has_resources.return_value = False
    colony.production_get_resource.side_effect = lambda res: 0.0
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
            queue, empire, tick, MagicMock(),
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

    # PROJ-427 Phase 3: save_path arg removed; signature is
    # (queue, item, empire, colony_or_fleet, galaxy, tick).
    engine._complete_item(queue, item, empire, colony, None, 1)

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
