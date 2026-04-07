"""
Tests for sub-engine per-tick input validation.

PROJ-251 Phase 6: Validates that engines raise ValidationException
with clear messages when preconditions are violated.
"""
import pytest
from unittest.mock import MagicMock

from game.core.exceptions import ValidationException


class TestHarvestingEngineValidation:
    """Tests for HarvestingEngine._validate_tick_inputs."""

    def test_valid_empires_pass(self, fresh_registries):
        from game.strategy.engine.harvesting_engine import HarvestingEngine
        engine = HarvestingEngine(registries=fresh_registries)

        empire = MagicMock()
        empire.id = 0
        empire.colonies = []

        # Should not raise
        engine._validate_tick_inputs([empire])

    def test_colony_with_none_planet_raises(self, fresh_registries):
        from game.strategy.engine.harvesting_engine import HarvestingEngine
        engine = HarvestingEngine(registries=fresh_registries)

        colony = MagicMock()
        colony.planet = None if hasattr(colony, 'planet') else None
        # MagicMock auto-creates attrs; explicitly set to None
        colony.configure_mock(planet=None)

        empire = MagicMock()
        empire.id = 0
        empire.colonies = [colony]

        # For harvesting, colonies are planets (empire.colonies IS a list of planets)
        # Check if the engine accesses colony.deposits or similar
        # Actually, empire.colonies is a list of Planet objects
        # The validation should catch None entries
        empire.colonies = [None]

        with pytest.raises(ValidationException):
            engine._validate_tick_inputs([empire])


class TestFleetMovementEngineValidation:
    """Tests for FleetMovementEngine._validate_tick_inputs."""

    def test_valid_empires_pass(self):
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine
        engine = FleetMovementEngine()

        empire = MagicMock()
        empire.fleets = []

        engine._validate_tick_inputs([empire])

    def test_fleet_with_none_location_raises(self):
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine
        engine = FleetMovementEngine()

        fleet = MagicMock()
        fleet.location = None
        fleet.id = "fleet-1"

        empire = MagicMock()
        empire.id = 0
        empire.fleets = [fleet]

        with pytest.raises(ValidationException):
            engine._validate_tick_inputs([empire])


class TestConflictResolutionEngineValidation:
    """Tests for ConflictResolutionEngine._validate_tick_inputs."""

    def test_valid_empires_pass(self, fresh_registries):
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        engine = ConflictResolutionEngine(battle_resolver=MagicMock(), registries=fresh_registries)

        empire = MagicMock()
        empire.fleets = []

        engine._validate_tick_inputs([empire])

    def test_fleet_with_none_location_raises(self, fresh_registries):
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        engine = ConflictResolutionEngine(battle_resolver=MagicMock(), registries=fresh_registries)

        fleet = MagicMock()
        fleet.location = None
        fleet.id = "fleet-1"

        empire = MagicMock()
        empire.id = 0
        empire.fleets = [fleet]

        with pytest.raises(ValidationException):
            engine._validate_tick_inputs([empire])
