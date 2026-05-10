"""
PROJ-332 — Characterization tests for the PROJ-320 `moved_fleet_ids`
derivation inside `TurnEngine._process_tick`.

Pins:
- After Phase 3 (`apply_movements`), `_process_tick` derives
  `moved_fleet_ids` as the set of fleet ids whose `location` differs
  from their pre-Phase-3 location, then passes that set to
  `conflict_engine.resolve_all_conflicts(..., moved_fleet_ids=...)`.
- With zero empires, `moved_fleet_ids` is the empty set and combat is
  still invoked once with `set()` — no exception.

Discipline: pure characterization — no production refactors.
"""
from __future__ import annotations

from unittest.mock import MagicMock

from game.core.hex_math import HexCoord
from game.strategy.engine.turn_engine import TurnEngine
from tests.fixtures.turn_engine import build_test_turn_engine
from game.strategy.interfaces.engines import (
    IActionExecutionEngine,
    IComponentActivationEngine,
    IConflictEngine,
    IConsumableEngine,
    IEnvironmentalHazardEngine,
    IHarvestingEngine,
    IMovementEngine,
    IOrderProcessor,
    IPlanetActionEngine,
    IPlanetEnergyEngine,
    IProductionEngine,
    IResupplyEngine,
)


def _build_engine_with_all_mocks(fresh_registries, *, movement_engine, conflict_engine):
    """Build a TurnEngine where every per-tick phase engine is a mock so
    `_process_tick` cannot reach real production logic."""
    mock_resource = MagicMock(spec=IConsumableEngine)
    mock_resource.process_per_turn_consumption.return_value = []
    mock_order = MagicMock(spec=IOrderProcessor)
    mock_order.process_instant_orders.return_value = []
    mock_resupply = MagicMock(spec=IResupplyEngine)
    mock_resupply.process_fuel_generation.return_value = []
    mock_resupply.process_fleet_resupply.return_value = []
    mock_harvest = MagicMock(spec=IHarvestingEngine)
    mock_production = MagicMock(spec=IProductionEngine)
    mock_environmental = MagicMock(spec=IEnvironmentalHazardEngine)
    mock_environmental.process_environmental_tick.return_value = []
    mock_planet_energy = MagicMock(spec=IPlanetEnergyEngine)
    mock_action = MagicMock(spec=IActionExecutionEngine)
    mock_planet_action = MagicMock(spec=IPlanetActionEngine)
    mock_activation = MagicMock(spec=IComponentActivationEngine)

    engine = build_test_turn_engine(fresh_registries, ai_factory=MagicMock(),
        movement_engine=movement_engine,
        conflict_engine=conflict_engine,
        resource_engine=mock_resource,
        order_processor=mock_order,
        resupply_engine=mock_resupply,
        harvesting_engine=mock_harvest,
        production_engine=mock_production,
        environmental_engine=mock_environmental,
        planet_energy_engine=mock_planet_energy,
        action_engine=mock_action,
        planet_action_engine=mock_planet_action,
        component_activation_engine=mock_activation,
    )
    return engine


class TestMovedFleetIdsDerivation:
    """Pin the PROJ-320 location-diff that produces `moved_fleet_ids`."""

    def test_moved_fleet_ids_contains_only_fleets_that_moved_in_tick(
        self, fresh_registries, mock_galaxy
    ):
        """Fleet A moves from hex (0,0) → (1,0). Fleet B stays at (5,5).
        Only fleet A's id should appear in `moved_fleet_ids`."""
        # Two fleets — A will be relocated by the fake apply_movements,
        # B stays put.
        fleet_a = MagicMock()
        fleet_a.id = 100
        fleet_a.location = HexCoord(0, 0)

        fleet_b = MagicMock()
        fleet_b.id = 200
        fleet_b.location = HexCoord(5, 5)

        empire = MagicMock()
        empire.id = 0
        empire.fleets = [fleet_a, fleet_b]

        # Fake movement engine: collect_movements returns a queue;
        # apply_movements mutates fleet_a's location to simulate the
        # actual move.
        mock_movement = MagicMock(spec=IMovementEngine)
        mock_movement.collect_movements.return_value = [
            (fleet_a, HexCoord(1, 0))
        ]

        def _apply(move_queue, galaxy):
            for fleet, hex_coord in move_queue:
                fleet.location = hex_coord
            return []

        mock_movement.apply_movements.side_effect = _apply

        mock_conflict = MagicMock(spec=IConflictEngine)

        engine = _build_engine_with_all_mocks(
            fresh_registries,
            movement_engine=mock_movement,
            conflict_engine=mock_conflict,
        )

        # Patch the locally-constructed Phase 1.8 engine.
        from unittest.mock import patch

        with patch(
            'game.strategy.engine.planet_modifier_effect_engine.PlanetModifierEffectEngine'
        ):
            engine._process_tick(1, [empire], mock_galaxy)

        # resolve_all_conflicts called once with moved_fleet_ids={100}.
        assert mock_conflict.resolve_all_conflicts.call_count == 1
        kwargs = mock_conflict.resolve_all_conflicts.call_args.kwargs
        assert kwargs['moved_fleet_ids'] == {100}

    def test_moved_fleet_ids_is_empty_set_with_zero_empires(
        self, fresh_registries, mock_galaxy
    ):
        """Zero empires → zero fleets → empty `moved_fleet_ids` set, but
        combat still fires exactly once with `set()`."""
        mock_movement = MagicMock(spec=IMovementEngine)
        mock_movement.collect_movements.return_value = []
        mock_movement.apply_movements.return_value = []
        mock_conflict = MagicMock(spec=IConflictEngine)

        engine = _build_engine_with_all_mocks(
            fresh_registries,
            movement_engine=mock_movement,
            conflict_engine=mock_conflict,
        )

        # Patch the locally-constructed Phase 1.8 engine.
        from unittest.mock import patch

        with patch(
            'game.strategy.engine.planet_modifier_effect_engine.PlanetModifierEffectEngine'
        ):
            # No exception with empty empire list.
            engine._process_tick(1, [], mock_galaxy)

        assert mock_conflict.resolve_all_conflicts.call_count == 1
        kwargs = mock_conflict.resolve_all_conflicts.call_args.kwargs
        assert kwargs['moved_fleet_ids'] == set()
