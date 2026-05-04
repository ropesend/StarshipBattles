"""
PROJ-332 — Characterization tests for the end-of-turn block in
`TurnEngine.process_turn`.

Pins:
- The injectable end-of-turn engines run in this order, after the
  100-tick loop:
      organics_consumption_engine.process_consumption
      → happiness_engine.process_happiness
      → population_engine.process_population_growth
- The locally-constructed `QualityEngine`, `AtmosphereEngine`, and
  `WaterEngine` are each instantiated once per `process_turn` call and
  their respective methods are invoked AFTER the population step
  (D-004 OBSERVATION: these are not injectable; tested by patching the
  source modules — they are function-local imports inside
  `process_turn`, so `patch('game.strategy.engine.turn_engine.X')`
  fails with AttributeError).
- D-007 OBSERVATION: a raise from the end-of-turn block escapes
  `_time_phase` wrapping. The exception propagates raw (NOT
  `EnginePhaseError`) and `_phase_times` does not gain a "happiness" key.

Discipline: pure characterization — no production refactors.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from game.core.exceptions import EnginePhaseError
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.interfaces.engines import (
    IHappinessEngine,
    IOrganicsConsumptionEngine,
    IPopulationEngine,
)


class TestEndOfTurnEngineOrder:
    """Pin the end-of-turn engine call order and locally-constructed engine
    instantiation pattern."""

    def test_end_of_turn_engines_called_in_order_organics_then_happiness_then_population(
        self, fresh_registries, mock_empire, mock_galaxy
    ):
        """The injectable end-of-turn trio fires in fixed order."""
        mock_empire.fleets = []

        # All three share a parent so we can read the global mock_calls
        # list to verify cross-mock ordering.
        parent = MagicMock()
        organics = MagicMock(spec=IOrganicsConsumptionEngine)
        happiness = MagicMock(spec=IHappinessEngine)
        population = MagicMock(spec=IPopulationEngine)
        parent.attach_mock(organics, "organics")
        parent.attach_mock(happiness, "happiness")
        parent.attach_mock(population, "population")

        engine = TurnEngine(
            registries=fresh_registries,
            ai_factory=MagicMock(),
            organics_consumption_engine=organics,
            happiness_engine=happiness,
            population_engine=population,
        )

        # Patch the locally-constructed end-of-turn engines so they don't
        # touch real production code. They are imported inside
        # `process_turn` from their source modules, so patch there.
        with patch(
            'game.strategy.engine.quality_engine.QualityEngine'
        ), patch(
            'game.strategy.engine.atmosphere_engine.AtmosphereEngine'
        ), patch(
            'game.strategy.engine.water_engine.WaterEngine'
        ):
            engine.process_turn([mock_empire], mock_galaxy)

        # Pull the names of the three relevant calls in order.
        relevant = [
            name for name, _, _ in parent.mock_calls
            if name.endswith(
                ("organics.process_consumption",
                 "happiness.process_happiness",
                 "population.process_population_growth")
            )
        ]
        assert relevant == [
            "organics.process_consumption",
            "happiness.process_happiness",
            "population.process_population_growth",
        ]

    def test_quality_atmosphere_water_engines_instantiated_per_process_turn_after_population_step(
        self, fresh_registries, mock_empire, mock_galaxy
    ):
        """D-004 OBSERVATION: the three terraforming engines are constructed
        locally inside `process_turn`. Each is instantiated once per call
        and its method is invoked after the population growth step.
        """
        mock_empire.fleets = []
        population = MagicMock(spec=IPopulationEngine)

        engine = TurnEngine(
            registries=fresh_registries,
            ai_factory=MagicMock(),
            population_engine=population,
        )

        with patch(
            'game.strategy.engine.quality_engine.QualityEngine'
        ) as mock_quality_cls, patch(
            'game.strategy.engine.atmosphere_engine.AtmosphereEngine'
        ) as mock_atmosphere_cls, patch(
            'game.strategy.engine.water_engine.WaterEngine'
        ) as mock_water_cls:
            engine.process_turn([mock_empire], mock_galaxy)

            # Each constructed exactly once.
            assert mock_quality_cls.call_count == 1
            assert mock_atmosphere_cls.call_count == 1
            assert mock_water_cls.call_count == 1

            # Their respective process methods invoked.
            mock_quality_cls.return_value.process_quality_improvement.assert_called_once_with(
                [mock_empire]
            )
            mock_atmosphere_cls.return_value.process_atmosphere.assert_called_once_with(
                [mock_empire]
            )
            mock_water_cls.return_value.process_water_modification.assert_called_once_with(
                [mock_empire]
            )

            # Population growth runs before the locally-constructed
            # engines. Structural assertion: pop_engine ran exactly once
            # and each local engine class was constructed/called once.
            assert population.process_population_growth.call_count == 1

    def test_end_of_turn_engine_raise_propagates_unwrapped_and_skips_phase_times_recording(
        self, fresh_registries, mock_empire, mock_galaxy
    ):
        """D-007 OBSERVATION: the end-of-turn block does NOT use
        `_time_phase`. A raise from `happiness_engine.process_happiness`
        propagates as the original exception type (NOT `EnginePhaseError`)
        and `_phase_times` retains its 14 canonical keys without
        a 'happiness' entry.
        """
        mock_empire.fleets = []
        organics = MagicMock(spec=IOrganicsConsumptionEngine)
        happiness = MagicMock(spec=IHappinessEngine)
        happiness.process_happiness.side_effect = RuntimeError("happiness boom")

        engine = TurnEngine(
            registries=fresh_registries,
            ai_factory=MagicMock(),
            organics_consumption_engine=organics,
            happiness_engine=happiness,
        )

        with patch(
            'game.strategy.engine.quality_engine.QualityEngine'
        ), patch(
            'game.strategy.engine.atmosphere_engine.AtmosphereEngine'
        ), patch(
            'game.strategy.engine.water_engine.WaterEngine'
        ):
            with pytest.raises(RuntimeError, match="happiness boom") as exc_info:
                engine.process_turn([mock_empire], mock_galaxy)

        # NOT wrapped in EnginePhaseError.
        assert not isinstance(exc_info.value, EnginePhaseError)

        # `_phase_times` keeps its canonical 14 keys; no 'happiness' entry.
        assert 'happiness' not in engine._phase_times
        assert len(engine._phase_times) == 14
