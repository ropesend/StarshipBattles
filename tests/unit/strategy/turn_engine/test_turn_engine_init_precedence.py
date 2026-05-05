"""
PROJ-332 — Characterization tests for TurnEngine.__init__ precedence and slot wiring.

Pins observed behavior of:
- Individual engine kwargs taking precedence over `TurnEngineConfig` fields.
- `_reset_phase_times` populating an exact 14-key dict.
- `race_registry` slot wiring (provided / None / default).
- `last_environmental_events` initializing to an empty list.

Discipline: pure characterization — no production refactors.
"""
from __future__ import annotations

from unittest.mock import MagicMock

from game.core.protocols import IRaceRegistry
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.engine.turn_engine_config import TurnEngineConfig
from game.strategy.interfaces.engines import IMovementEngine


class TestTurnEngineInitPrecedence:
    """Pin __init__ behavior: kwarg > config; slot defaults; phase-times keys."""

    def test_init_kwarg_takes_precedence_over_config_field_when_both_supplied(
        self, fresh_registries
    ):
        """Per-engine kwarg overrides the same field on `TurnEngineConfig`.

        Pins the `kwarg or cfg.field` precedence pattern in __init__.
        """
        config_movement = MagicMock(spec=IMovementEngine, name="config_movement")
        kwarg_movement = MagicMock(spec=IMovementEngine, name="kwarg_movement")
        config = TurnEngineConfig(movement_engine=config_movement)

        engine = TurnEngine(
            registries=fresh_registries,
            config=config,
            movement_engine=kwarg_movement,
        )

        assert engine.movement_engine is kwarg_movement
        assert engine.movement_engine is not config_movement

    def test_init_initializes_phase_times_with_canonical_keys(
        self, fresh_registries
    ):
        """Pins the exact phase_times key set populated by `_reset_phase_times`.

        15 tick-loop keys + 6 end-of-turn keys (added by PROJ-343 T1.2-engines
        and PROJ-365). PROJ-365 added `planet_modifier_effects` to the
        tick-loop bucket because the descriptor registry routes every
        per-tick phase through `_time_phase` uniformly.
        """
        engine = TurnEngine(registries=fresh_registries)

        assert set(engine._phase_times.keys()) == {
            'harvesting', 'resources',
            'fuel_gen', 'resupply', 'production',
            'environmental', 'instant_orders', 'actions',
            'planet_energy', 'planet_actions', 'activation_timers',
            # PROJ-365: descriptor registry now times this phase too.
            'planet_modifier_effects',
            'movement_calc', 'movement_apply', 'combat',
            # PROJ-343 T1.2-engines:
            'organics_consumption', 'happiness', 'population_growth',
            'quality_improvement', 'atmosphere', 'water_modification',
        }
        assert len(engine._phase_times) == 21
        # All values start at 0.0 float.
        assert all(v == 0.0 for v in engine._phase_times.values())
        assert all(isinstance(v, float) for v in engine._phase_times.values())

    def test_init_threads_race_registry_through_when_supplied_and_accepts_none(
        self, fresh_registries
    ):
        """Pins `race_registry` slot wiring: stored as `_race_registry`,
        defaults to None when omitted, accepts None explicitly, and threads
        a supplied registry through unchanged.
        """
        # Default: None when not supplied.
        engine_default = TurnEngine(registries=fresh_registries)
        assert engine_default._race_registry is None

        # Explicit None.
        engine_none = TurnEngine(registries=fresh_registries, race_registry=None)
        assert engine_none._race_registry is None

        # Supplied registry threaded through.
        mock_registry = MagicMock(spec=IRaceRegistry)
        engine_with = TurnEngine(
            registries=fresh_registries, race_registry=mock_registry
        )
        assert engine_with._race_registry is mock_registry

    def test_init_initializes_last_environmental_events_to_empty_list(
        self, fresh_registries
    ):
        """`last_environmental_events` is a fresh empty list per instance."""
        engine_a = TurnEngine(registries=fresh_registries)
        engine_b = TurnEngine(registries=fresh_registries)

        assert engine_a.last_environmental_events == []
        assert isinstance(engine_a.last_environmental_events, list)
        # Independent list per instance — not a shared mutable default.
        assert engine_a.last_environmental_events is not engine_b.last_environmental_events
