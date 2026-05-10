"""
PROJ-365 Phase 1 — Golden phase-list characterization tests for
``TurnEngine._process_tick``.

These tests pin the current per-tick phase ordering and the tick-1-only
behaviors before Phase 2/3 of PROJ-365 introduces a declarative
``DEFAULT_TICK_PHASE_LIST`` and replaces ``_process_tick``'s body with
descriptor iteration. The golden list MUST keep matching after the
refactor — any divergence is a regression.

The ordering captured here matches the imperative implementation at
``turn_engine.py:703-782`` exactly.

Discipline: pure characterization — no production refactor in Phase 1.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

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


# Golden ordering — every per-tick phase, in the exact order
# ``_process_tick`` invokes them.
GOLDEN_PHASE_ORDER = [
    'harvesting',
    'resources',
    'fuel_gen',
    'planet_energy',
    'resupply',
    'production',
    'environmental',
    'instant_orders',
    'actions',
    'planet_actions',
    'activation_timers',
    'planet_modifier_effects',
    'movement_calc',
    'movement_apply',
    'combat',
]


def _build_engine_with_all_mocks(
    fresh_registries,
    *,
    movement_engine=None,
    conflict_engine=None,
):
    """Stand up a TurnEngine where every per-tick engine is a mock so
    ``_process_tick`` cannot reach real production logic."""
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

    if movement_engine is None:
        movement_engine = MagicMock(spec=IMovementEngine)
        movement_engine.collect_movements.return_value = []
        movement_engine.apply_movements.return_value = []
    if conflict_engine is None:
        conflict_engine = MagicMock(spec=IConflictEngine)

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


def _capture_phase_calls(engine):
    """Wrap ``_time_phase`` and patch the ``PlanetModifierEffectEngine``
    construction site so we capture the full 15-phase call order.

    Returns ``(captured_phases, restore_callable)``. ``captured_phases``
    is a list mutated as the tick runs; ``restore_callable`` is unused
    (the patch is applied via context manager in the test).
    """
    captured: list[str] = []
    original_time_phase = engine._time_phase

    def wrapped_time_phase(key, fn, *args, **kwargs):
        captured.append(key)
        return original_time_phase(key, fn, *args, **kwargs)

    engine._time_phase = wrapped_time_phase  # type: ignore[method-assign]
    return captured


class TestDefaultPhaseOrder:
    """Pin the 15-phase per-tick ordering of ``_process_tick``."""

    def test_phase_order_matches_golden_on_tick_5(
        self, fresh_registries, mock_galaxy
    ):
        """tick=5 covers the non-tick-1 path. Captured phase order must
        equal ``GOLDEN_PHASE_ORDER``."""
        engine = _build_engine_with_all_mocks(fresh_registries)
        captured = _capture_phase_calls(engine)

        # Patch the locally-constructed PlanetModifierEffectEngine so it
        # doesn't reach real production code. The descriptor routes the
        # call through ``_time_phase``, so the wrapper above already
        # captures it under the 'planet_modifier_effects' key.
        with patch(
            'game.strategy.engine.planet_modifier_effect_engine.PlanetModifierEffectEngine'
        ):
            empire = MagicMock()
            empire.id = 0
            empire.fleets = []
            engine._process_tick(5, [empire], mock_galaxy)

        assert captured == GOLDEN_PHASE_ORDER

    def test_phase_order_matches_golden_on_tick_1(
        self, fresh_registries, mock_galaxy
    ):
        """tick=1 takes the same phase path; tick-1-only side effects
        (mid-phase logging) do not change the phase ordering."""
        engine = _build_engine_with_all_mocks(fresh_registries)
        captured = _capture_phase_calls(engine)

        with patch(
            'game.strategy.engine.planet_modifier_effect_engine.PlanetModifierEffectEngine'
        ):
            empire = MagicMock()
            empire.id = 0
            empire.fleets = []
            engine._process_tick(1, [empire], mock_galaxy)

        assert captured == GOLDEN_PHASE_ORDER


class TestTickOneOnlyLogging:
    """Pin the two ``_log_empire_state`` calls inside the tick loop."""

    def test_log_empire_state_called_twice_on_tick_1(
        self, fresh_registries, mock_galaxy
    ):
        """On tick==1, ``_log_empire_state`` is called twice mid-tick:
        once before harvesting ('TURN START tick=1'), once after the
        production phase ('Tick 1 AFTER CONSTRUCTION')."""
        engine = _build_engine_with_all_mocks(fresh_registries)

        with patch.object(engine, '_log_empire_state') as mock_log:
            with patch(
                'game.strategy.engine.planet_modifier_effect_engine.PlanetModifierEffectEngine'
            ):
                empire = MagicMock()
                empire.fleets = []
                engine._process_tick(1, [empire], mock_galaxy)

        # Exactly two mid-tick calls on tick==1.
        assert mock_log.call_count == 2
        labels = [call.args[1] for call in mock_log.call_args_list]
        assert labels == [
            'TURN START tick=1',
            'Tick 1 AFTER CONSTRUCTION',
        ]

    def test_log_empire_state_not_called_on_tick_5(
        self, fresh_registries, mock_galaxy
    ):
        """On tick != 1, no mid-tick ``_log_empire_state`` calls fire."""
        engine = _build_engine_with_all_mocks(fresh_registries)

        with patch.object(engine, '_log_empire_state') as mock_log:
            with patch(
                'game.strategy.engine.planet_modifier_effect_engine.PlanetModifierEffectEngine'
            ):
                empire = MagicMock()
                empire.fleets = []
                engine._process_tick(5, [empire], mock_galaxy)

        assert mock_log.call_count == 0


class TestMovedFleetIdsInvariant:
    """PROJ-320 invariant pinned inside the PROJ-365 module: combat
    receives ``moved_fleet_ids`` derived from the pre/post-Phase-3
    location diff. Mirrors ``test_turn_engine_phase_320_movement_diff``
    so the descriptor refactor cannot regress this invariant silently.
    """

    def test_combat_phase_receives_moved_fleet_ids(
        self, fresh_registries, mock_galaxy
    ):
        fleet_a = MagicMock()
        fleet_a.id = 100
        fleet_a.location = HexCoord(0, 0)

        fleet_b = MagicMock()
        fleet_b.id = 200
        fleet_b.location = HexCoord(5, 5)

        empire = MagicMock()
        empire.id = 0
        empire.fleets = [fleet_a, fleet_b]

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

        with patch(
            'game.strategy.engine.planet_modifier_effect_engine.PlanetModifierEffectEngine'
        ):
            engine._process_tick(1, [empire], mock_galaxy)

        assert mock_conflict.resolve_all_conflicts.call_count == 1
        kwargs = mock_conflict.resolve_all_conflicts.call_args.kwargs
        assert kwargs['moved_fleet_ids'] == {100}
