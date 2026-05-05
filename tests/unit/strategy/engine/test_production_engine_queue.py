"""PROJ-333 Phase 1: ProductionEngine queue-iteration characterization.

Pins queue-tick state machine behaviors: validation routing, pause flags,
fleet yard rate scaling, complex-only STOP semantics, MAX_QUEUE_ITERATIONS
cap, and the first-tick shortage-flag reset.

Companion file: ``test_production_engine_consumption.py`` covers resource
math + affordability routing on the same ProductionEngine class.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.core.exceptions import ValidationException
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.planet import Planet
from game.strategy.engine.production_engine import (
    MAX_QUEUE_ITERATIONS,
    ProductionEngine,
    QueueItemAction,
)


# ---------------------------------------------------------------------------
# Local fixtures (engine + minimal state mocks)
# ---------------------------------------------------------------------------


@pytest.fixture
def engine(fresh_registries):
    return ProductionEngine(registries=fresh_registries)


@pytest.fixture
def empire():
    emp = MagicMock(spec=Empire)
    emp.id = "emp1"
    emp.resource_pool = {"metals": 1000.0}
    emp.has_resources.return_value = True
    emp.consume_resources = MagicMock()
    return emp


@pytest.fixture
def colony():
    col = MagicMock(spec=Planet)
    col.construction_queue = []
    col.facilities = []
    col.context_type = None  # falls back to empire pool
    return col


def _ship_item(design_id: str = "frigate", cost_a: float = 10.0) -> dict:
    return {
        "design_id": design_id,
        "type": "ship",
        "total_cost": {"A": cost_a},
        "resources_consumed": {"A": 0.0},
    }


# ---------------------------------------------------------------------------
# init / set_current_turn / validate_tick_inputs
# ---------------------------------------------------------------------------


def test_init_raises_validation_when_registries_none():
    """ProductionEngine demands non-None registries (strict DI)."""
    with pytest.raises(ValidationException) as exc_info:
        ProductionEngine(registries=None)
    assert "registries is required" in str(exc_info.value)


def test_set_current_turn_updates_field_for_habitability_cache(engine):
    """`set_current_turn` mutates the cache-key field used by PROJ-285."""
    assert engine._current_turn == 0
    engine.set_current_turn(7)
    assert engine._current_turn == 7


def test_process_construction_tick_validates_resource_pool_not_none(engine):
    """Empire with `resource_pool=None` triggers a ValidationException."""
    bad_empire = MagicMock(spec=Empire)
    bad_empire.id = "emp1"
    bad_empire.resource_pool = None
    with pytest.raises(ValidationException):
        engine.process_construction_tick(1, [bad_empire], None, None)


# ---------------------------------------------------------------------------
# Pause flags + planetary-yard requirement (process_construction_tick)
# ---------------------------------------------------------------------------


def test_construction_queue_paused_skips_colony_base_queue(engine, empire, monkeypatch):
    """A colony with `construction_queue_paused=True` produces nothing."""
    item = _ship_item(design_id="complex_x", cost_a=10.0)
    item["type"] = "complex"
    colony = MagicMock(spec=Planet)
    colony.construction_queue = [item]
    colony.facilities = []
    colony.construction_queue_paused = True
    colony.context_type = "planet"
    empire.colonies = [colony]
    empire.fleets = []

    # Force planetary-yard True so we know the pause flag is the gate.
    monkeypatch.setattr(
        "game.strategy.engine.production_engine._colony_has_planetary_yard",
        lambda *_args, **_kw: True,
    )

    engine.process_construction_tick(1, [empire], None, None)

    assert item["resources_consumed"]["A"] == 0.0


def test_per_facility_pause_skips_only_that_shipyard(engine, empire, monkeypatch):
    """A paused facility yard is skipped; sibling unpaused yards still run."""
    paused_item = _ship_item(design_id="paused_ship", cost_a=10.0)
    active_item = _ship_item(design_id="active_ship", cost_a=10.0)

    paused_fac = MagicMock()
    paused_fac.construction_queue = [paused_item]
    paused_fac.construction_queue_paused = True
    paused_fac.is_shipyard = True
    paused_fac.design_data = {}

    active_fac = MagicMock()
    active_fac.construction_queue = [active_item]
    active_fac.construction_queue_paused = False
    active_fac.is_shipyard = True
    active_fac.design_data = {}

    colony = MagicMock(spec=Planet)
    colony.construction_queue = []
    colony.facilities = [paused_fac, active_fac]
    colony.context_type = "planet"
    colony.has_stockpile.return_value = True
    colony.consume_from_stockpile = MagicMock()
    empire.colonies = [colony]
    empire.fleets = []

    monkeypatch.setattr(
        "game.strategy.engine.production_engine._get_facility_production_rates",
        lambda fac: {"A": 1000.0},
    )
    engine._spawner.spawn_completed_item = MagicMock()

    engine.process_construction_tick(1, [empire], None, None)

    assert paused_item["resources_consumed"]["A"] == 0.0
    assert active_item["resources_consumed"]["A"] > 0.0


def test_fleet_without_space_shipyard_is_skipped(engine, empire):
    """Fleet without `capabilities.has_space_shipyard` is silently skipped."""
    item = _ship_item()
    fleet = MagicMock()
    fleet.is_building = True
    fleet.capabilities.has_space_shipyard = False
    fleet.construction_queue = [item]
    empire.colonies = []
    empire.fleets = [fleet]

    engine.process_construction_tick(1, [empire], None, None)

    assert item["resources_consumed"]["A"] == 0.0


def test_fleet_pause_flag_blocks_fleet_queue_processing(engine, empire):
    """Even with a space yard, a paused fleet produces nothing."""
    item = _ship_item()
    fleet = MagicMock()
    fleet.is_building = True
    fleet.capabilities.has_space_shipyard = True
    fleet.capabilities.space_shipyard_count = 1
    fleet.construction_queue = [item]
    fleet.construction_queue_paused = True
    empire.colonies = []
    empire.fleets = [fleet]

    engine.process_construction_tick(1, [empire], None, None)

    assert item["resources_consumed"]["A"] == 0.0


def test_fleet_yard_count_multiplies_production_rate(engine):
    """`_resolve_fleet_production_rate` multiplies base rate by yard count."""
    fleet = MagicMock()
    fleet.capabilities.space_shipyard_count = 4
    rate = engine._resolve_fleet_production_rate(fleet)

    # Compare against the default (count=1) baseline so the test remains
    # robust to actual production_rates.json contents.
    fleet_one = MagicMock()
    fleet_one.capabilities.space_shipyard_count = 1
    base = engine._resolve_fleet_production_rate(fleet_one)
    for res, value in base.items():
        assert rate[res] == pytest.approx(value * 4)


# ---------------------------------------------------------------------------
# _validate_queue_item / queue iteration
# ---------------------------------------------------------------------------


def test_complex_only_queue_stops_on_non_complex_item(engine, empire, colony):
    """`is_complex_only=True` halts the queue (STOP, not SKIP) on a ship."""
    ship_item = _ship_item(design_id="stop_ship")
    later_complex = {
        "design_id": "later_complex",
        "type": "complex",
        "total_cost": {"A": 1.0},
        "resources_consumed": {"A": 0.0},
    }
    queue = [ship_item, later_complex]
    engine._spawner.spawn_completed_item = MagicMock()

    engine._process_queue_tick_dynamic(
        queue, empire, 1, MagicMock(), None,
        {"A": 1000.0}, colony, is_complex_only=True,
    )

    # Both items remain — STOP halts processing without removing the offender.
    assert queue == [ship_item, later_complex]
    assert engine._spawner.spawn_completed_item.call_count == 0


def test_fleet_complex_without_planet_at_hex_returns_stop(engine, empire):
    """Fleet building a complex with no planet at its hex returns STOP."""
    fleet = MagicMock(spec=Fleet)
    fleet.location = MagicMock()

    galaxy = MagicMock()
    galaxy.get_planets_at_global_hex.return_value = []

    item = {
        "design_id": "fleet_complex",
        "type": "complex",
        "total_cost": {"A": 1.0},
        "resources_consumed": {"A": 0.0},
    }
    action = engine._validate_queue_item(item, fleet, galaxy, is_complex_only=False)
    assert action == QueueItemAction.STOP


def test_queue_item_missing_total_cost_is_skipped_with_warning(engine, empire, colony, caplog):
    """Items without `total_cost` are SKIPPED (popped) with a warning log."""
    bad = {"design_id": "no_cost", "type": "ship", "resources_consumed": {}}
    good = _ship_item(design_id="good", cost_a=1.0)
    queue = [bad, good]
    engine._spawner.spawn_completed_item = MagicMock()

    import logging
    with caplog.at_level(logging.WARNING):
        engine._process_queue_tick_dynamic(
            queue, empire, 1, MagicMock(), None,
            {"A": 10000.0}, colony, is_complex_only=False,
        )

    assert queue == []  # bad popped, good completed
    assert "missing 'total_cost'" in caplog.text


def test_queue_item_not_a_dict_is_skipped(engine, empire, colony):
    """Non-dict queue entries are SKIPPED (popped), processing continues."""
    queue = ["literal string", _ship_item(design_id="real", cost_a=1.0)]
    engine._spawner.spawn_completed_item = MagicMock()

    engine._process_queue_tick_dynamic(
        queue, empire, 1, MagicMock(), None,
        {"A": 10000.0}, colony, is_complex_only=False,
    )

    assert queue == []
    assert engine._spawner.spawn_completed_item.call_count == 1


def test_max_queue_iterations_limits_inner_loop_to_10(engine, empire, colony):
    """Inner loop processes EXACTLY MAX_QUEUE_ITERATIONS items per tick.

    With 20 free items in the queue and effectively unlimited tick capacity
    relative to per-item cost, the safety ceiling kicks in at exactly 10
    iterations and the remaining 10 items carry over silently to the next
    tick (PROJ-333 Observation: silent drop).
    """
    items = [_ship_item(design_id=f"ship_{i}", cost_a=0.001) for i in range(20)]
    spawn_count = {"n": 0}

    def _count_spawn(*_args, **_kwargs):
        spawn_count["n"] += 1

    engine._spawner.spawn_completed_item = MagicMock(side_effect=_count_spawn)

    queue = list(items)
    engine._process_queue_tick_dynamic(
        queue, empire, 1, MagicMock(), None,
        {"A": 1_000_000.0}, colony, is_complex_only=False,
    )

    # Exact ceiling: not <=, exactly == MAX_QUEUE_ITERATIONS.
    assert spawn_count["n"] == MAX_QUEUE_ITERATIONS
    assert engine._spawner.spawn_completed_item.call_count == MAX_QUEUE_ITERATIONS
    # 20 - 10 = 10 items remain in the queue (silent carry-over).
    assert len(queue) == 20 - MAX_QUEUE_ITERATIONS


# ---------------------------------------------------------------------------
# First-tick reset of shortage flags
# ---------------------------------------------------------------------------


def test_first_tick_clears_shortage_logged_flags(engine, empire, colony):
    """Tick == 1 pops any leftover `_shortage_logged` flags from prior turns."""
    item = _ship_item(design_id="frigate", cost_a=100.0)
    item["_shortage_logged"] = True
    queue = [item]
    # Make affordability fail so we know the flag would be re-set if cleared.
    colony.context_type = "planet"
    colony.has_stockpile.return_value = False
    colony.get_stockpile.side_effect = lambda res: 0.0
    colony.stockpile = {}

    engine._process_queue_tick_dynamic(
        queue, empire, 1, MagicMock(), None,
        {"A": 500.0}, colony, is_complex_only=False,
    )

    # Flag was reset on entry, then re-set by the shortage handler this tick.
    assert item.get("_shortage_logged") is True


# ---------------------------------------------------------------------------
# Habitability multiplier
# ---------------------------------------------------------------------------


def test_habitability_multiplier_scales_production_rate_for_colony_only(fresh_registries):
    """`_get_habitability_mult` returns 1.0 for fleets, race-config value for colonies."""
    race_registry = MagicMock()
    engine_with_race = ProductionEngine(
        registries=fresh_registries, race_registry=race_registry,
    )

    # Fleet: no get_cached_habitability_multiplier attribute → 1.0
    fleet = MagicMock(spec=Fleet)
    if hasattr(fleet, "get_cached_habitability_multiplier"):
        del fleet.get_cached_habitability_multiplier
    assert engine_with_race._get_habitability_mult(fleet) == 1.0

    # Colony with cache method gets queried.
    colony = MagicMock()
    colony.get_cached_habitability_multiplier = MagicMock(return_value=0.5)
    engine_with_race.set_current_turn(3)
    assert engine_with_race._get_habitability_mult(colony) == 0.5
    colony.get_cached_habitability_multiplier.assert_called_once_with(race_registry, 3)

    # Engine with no race_registry always returns 1.0.
    engine_no_race = ProductionEngine(registries=fresh_registries)
    colony2 = MagicMock()
    colony2.get_cached_habitability_multiplier = MagicMock(return_value=0.5)
    assert engine_no_race._get_habitability_mult(colony2) == 1.0
