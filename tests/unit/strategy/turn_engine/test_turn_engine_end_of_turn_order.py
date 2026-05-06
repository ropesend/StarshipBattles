"""
PROJ-332 — Characterization tests for the end-of-turn block in
`TurnEngine.process_turn`.

PROJ-369 Phase 2: Updated to use constructor injection for the three
terraforming engines (Quality / Atmosphere / Water) — they are now
first-class injectable engines (mirrored on `TurnEngineConfig`),
replacing the prior function-local-import + module-patch pattern.

Pins:
- The 6 end-of-turn engines fire in this order, after the 100-tick loop:
      organics_consumption_engine.process_consumption
      → happiness_engine.process_happiness
      → population_engine.process_population_growth
      → quality_engine.process_quality_improvement
      → atmosphere_engine.process_atmosphere
      → water_engine.process_water_modification
- Each terraforming engine's process method is invoked exactly once per
  `process_turn` call.
- A raise from the end-of-turn block is wrapped in `EnginePhaseError`
  (PROJ-343 T1.2-engines) so the rollback site at process_turn catches it.

Discipline: pure characterization — no production refactors.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.core.exceptions import EnginePhaseError
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.interfaces.engines import (
    IAtmosphereEngine,
    IHappinessEngine,
    IOrganicsConsumptionEngine,
    IPopulationEngine,
    IQualityEngine,
    IWaterEngine,
)


def _build_terraforming_mocks():
    """Return a (quality, atmosphere, water) triple of spec'd mocks."""
    return (
        MagicMock(spec=IQualityEngine),
        MagicMock(spec=IAtmosphereEngine),
        MagicMock(spec=IWaterEngine),
    )


class TestEndOfTurnEngineOrder:
    """Pin the end-of-turn engine call order across all 6 phases."""

    def test_end_of_turn_engines_called_in_order(
        self, fresh_registries, mock_empire, mock_galaxy
    ):
        """All 6 end-of-turn engines fire in the PROJ-284-pinned order."""
        mock_empire.fleets = []

        # Attach all six to a parent so cross-mock ordering is observable.
        parent = MagicMock()
        organics = MagicMock(spec=IOrganicsConsumptionEngine)
        happiness = MagicMock(spec=IHappinessEngine)
        population = MagicMock(spec=IPopulationEngine)
        quality, atmosphere, water = _build_terraforming_mocks()
        parent.attach_mock(organics, "organics")
        parent.attach_mock(happiness, "happiness")
        parent.attach_mock(population, "population")
        parent.attach_mock(quality, "quality")
        parent.attach_mock(atmosphere, "atmosphere")
        parent.attach_mock(water, "water")

        engine = TurnEngine(
            registries=fresh_registries,
            ai_factory=MagicMock(),
            organics_consumption_engine=organics,
            happiness_engine=happiness,
            population_engine=population,
            quality_engine=quality,
            atmosphere_engine=atmosphere,
            water_engine=water,
        )
        engine.process_turn([mock_empire], mock_galaxy)

        # Pull only end-of-turn calls in observed order.
        relevant_method_suffixes = (
            "organics.process_consumption",
            "happiness.process_happiness",
            "population.process_population_growth",
            "quality.process_quality_improvement",
            "atmosphere.process_atmosphere",
            "water.process_water_modification",
        )
        relevant = [
            name for name, _, _ in parent.mock_calls
            if name.endswith(relevant_method_suffixes)
        ]
        assert relevant == [
            "organics.process_consumption",
            "happiness.process_happiness",
            "population.process_population_growth",
            "quality.process_quality_improvement",
            "atmosphere.process_atmosphere",
            "water.process_water_modification",
        ]

    def test_terraforming_engines_each_called_once_after_population(
        self, fresh_registries, mock_empire, mock_galaxy
    ):
        """Each of Quality / Atmosphere / Water is invoked exactly once
        per `process_turn` call, after the population growth phase.
        """
        mock_empire.fleets = []
        population = MagicMock(spec=IPopulationEngine)
        quality, atmosphere, water = _build_terraforming_mocks()

        engine = TurnEngine(
            registries=fresh_registries,
            ai_factory=MagicMock(),
            population_engine=population,
            quality_engine=quality,
            atmosphere_engine=atmosphere,
            water_engine=water,
        )
        engine.process_turn([mock_empire], mock_galaxy)

        quality.process_quality_improvement.assert_called_once_with(
            [mock_empire]
        )
        atmosphere.process_atmosphere.assert_called_once_with(
            [mock_empire]
        )
        water.process_water_modification.assert_called_once_with(
            [mock_empire]
        )
        # Population growth runs before the terraforming engines.
        assert population.process_population_growth.call_count == 1

    def test_end_of_turn_engine_raise_wraps_in_engine_phase_error_and_records_timing(
        self, fresh_registries, mock_empire, mock_galaxy
    ):
        """PROJ-343 T1.2-engines: end-of-turn engines route through
        `_time_phase`, so a raise from `happiness_engine.process_happiness`
        is wrapped in `EnginePhaseError` (with `phase_name='happiness'`)
        and the rollback site catches it.
        """
        mock_empire.fleets = []
        organics = MagicMock(spec=IOrganicsConsumptionEngine)
        happiness = MagicMock(spec=IHappinessEngine)
        happiness.process_happiness.side_effect = RuntimeError("happiness boom")
        quality, atmosphere, water = _build_terraforming_mocks()

        engine = TurnEngine(
            registries=fresh_registries,
            ai_factory=MagicMock(),
            organics_consumption_engine=organics,
            happiness_engine=happiness,
            quality_engine=quality,
            atmosphere_engine=atmosphere,
            water_engine=water,
        )

        with pytest.raises(EnginePhaseError) as exc_info:
            engine.process_turn([mock_empire], mock_galaxy)

        # `_time_phase` records the phase name in EnginePhaseError.context.
        assert exc_info.value.context.get('phase_name') == 'happiness'

        # `_phase_times` includes the 'happiness' entry.
        assert 'happiness' in engine._phase_times
        # PROJ-365 added `planet_modifier_effects` to the tick-loop bucket.
        # Total = 15 tick + 6 end-of-turn = 21 buckets.
        assert len(engine._phase_times) == 21
