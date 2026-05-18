"""
Tests for PlanetaryYard ability requirement for base construction queue.

A colony must have an operational facility with PlanetaryYard ability
for its base construction queue (complexes) to be processed.

PROJ-322 Task 6.6 (HLP-003): the per-file `_make_yard_facility` helper
is now a thin alias over the shared `make_planetary_yard_facility`
factory at `tests.fixtures.yard_facility`.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.planetary_facility import PlanetaryFacility
from game.strategy.engine.production_engine import ProductionEngine
from game.strategy.data.build_queue_source import colony_has_planetary_yard as _colony_has_planetary_yard
from tests.fixtures.yard_facility import make_planetary_yard_facility


def _make_yard_facility(is_operational=True):
    """Thin alias over the shared `make_planetary_yard_facility` factory."""
    return make_planetary_yard_facility(is_operational=is_operational)


class TestColonyHasPlanetaryYard:
    """Tests for _colony_has_planetary_yard() helper."""

    def test_colony_with_yard_returns_true(self):
        """Colony with operational PlanetaryYard facility returns True."""
        colony = MagicMock()
        colony.facilities = [_make_yard_facility()]
        assert _colony_has_planetary_yard(colony) is True

    def test_colony_without_yard_returns_false(self):
        """Colony with no PlanetaryYard facility returns False."""
        colony = MagicMock()
        colony.facilities = []
        assert _colony_has_planetary_yard(colony) is False

    def test_non_operational_yard_returns_false(self):
        """Non-operational PlanetaryYard facility doesn't count."""
        colony = MagicMock()
        colony.facilities = [_make_yard_facility(is_operational=False)]
        assert _colony_has_planetary_yard(colony) is False

    def test_colony_with_other_facilities_returns_false(self):
        """Facilities without PlanetaryYard don't enable base queue."""
        harvester = PlanetaryFacility(
            instance_id="harv_1",
            design_id="harvester",
            name="Harvester",
            design_data={
                "layers": {"CORE": [{"id": "h", "abilities": {"ResourceHarvester": {"resource_type": "metals", "base_harvest_rate": 50}}}]}
            },
        )
        colony = MagicMock()
        colony.facilities = [harvester]
        assert _colony_has_planetary_yard(colony) is False


class TestBaseQueueRequiresPlanetaryYard:
    """Tests that base construction queue only processes with PlanetaryYard."""

    def test_base_queue_blocked_without_yard(self, fresh_registries):
        """Colony without PlanetaryYard can't process base construction queue."""
        engine = ProductionEngine(registries=fresh_registries)
        empire = MagicMock()
        empire.id = 0
        empire.fleets = []

        colony = MagicMock()
        colony.name = "No Yard Colony"
        colony.facilities = []  # No PlanetaryYard
        colony.construction_queue = [
            {"design_id": "test", "type": "complex", "turns_remaining": 5,
             "total_cost": {"metals": 100}, "resources_consumed": {"metals": 0}}
        ]
        colony.stockpile = {"metals": 1000.0}

        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)

        # Nothing consumed — queue blocked
        assert colony.construction_queue[0]["resources_consumed"]["metals"] == 0.0
