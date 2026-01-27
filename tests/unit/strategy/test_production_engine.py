"""
Unit tests for ProductionEngine.

PROJ-12 Phase 3: TDD tests written before implementation.
Tests construction queue processing, ship spawning, complex spawning.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from game.strategy.data.hex_math import HexCoord


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_empire():
    """Create a mock empire."""
    empire = MagicMock()
    empire.id = 0
    empire.name = "Test Empire"
    empire.colonies = []
    empire.fleets = []
    empire.add_fleet = MagicMock()
    empire.get_next_fleet_id = MagicMock(return_value=1)
    return empire


@pytest.fixture
def mock_planet():
    """Create a mock planet/colony."""
    planet = MagicMock()
    planet.id = 1
    planet.name = "Test Colony"
    planet.owner_id = 0
    planet.location = HexCoord(5, 5)
    planet.construction_queue = []
    planet.facilities = []
    planet.has_space_shipyard = True
    return planet


@pytest.fixture
def mock_galaxy():
    """Create a mock galaxy."""
    galaxy = MagicMock()
    galaxy.get_system_of_planet = MagicMock(return_value=None)
    return galaxy


# =============================================================================
# Test: ProductionEngine Creation
# =============================================================================

class TestProductionEngineCreation:
    """Tests for ProductionEngine initialization."""

    def test_production_engine_can_be_created(self):
        """ProductionEngine can be instantiated."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()

        assert engine is not None

    def test_production_engine_has_process_production(self):
        """ProductionEngine has process_production method."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()

        assert hasattr(engine, 'process_production')
        assert callable(engine.process_production)


# =============================================================================
# Test: Empty Queue Handling
# =============================================================================

class TestEmptyQueueHandling:
    """Tests for colonies with empty construction queues."""

    def test_empty_queue_skipped(self, mock_empire, mock_planet):
        """Colonies with empty queues are skipped."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = []
        mock_empire.colonies = [mock_planet]

        # Should not raise any errors
        engine.process_production([mock_empire])

    def test_no_colonies_handled(self, mock_empire):
        """Empire with no colonies processes without error."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_empire.colonies = []

        engine.process_production([mock_empire])


# =============================================================================
# Test: Production Turn Decrement
# =============================================================================

class TestProductionTurnDecrement:
    """Tests for turn decrement in construction queue."""

    def test_production_decrements_turns_dict_format(self, mock_empire, mock_planet):
        """Production decrements turns remaining (dict format)."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = [{"type": "ship", "design_id": "Scout", "turns_remaining": 3}]
        mock_planet.has_space_shipyard = True
        mock_empire.colonies = [mock_planet]

        engine.process_production([mock_empire])

        assert mock_planet.construction_queue[0]["turns_remaining"] == 2



# =============================================================================
# Test: Production Completion
# =============================================================================

class TestProductionCompletion:
    """Tests for production completion (turns reach zero)."""

    def test_production_completes_at_zero(self, mock_empire, mock_planet, mock_galaxy):
        """Production completes when turns reach zero."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = [{"type": "ship", "design_id": "Scout", "turns_remaining": 1}]
        mock_planet.has_space_shipyard = True
        mock_empire.colonies = [mock_planet]

        with patch.object(engine, '_spawn_ship') as mock_spawn:
            engine.process_production([mock_empire], mock_galaxy)

            mock_spawn.assert_called()
            assert len(mock_planet.construction_queue) == 0

    def test_complex_production_completes(self, mock_empire, mock_planet, mock_galaxy):
        """Complex production completes when turns reach zero."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = [{"type": "complex", "design_id": "Factory", "turns_remaining": 1}]
        mock_empire.colonies = [mock_planet]

        with patch.object(engine, '_spawn_complex') as mock_spawn:
            engine.process_production([mock_empire], mock_galaxy)

            mock_spawn.assert_called()


# =============================================================================
# Test: Shipyard Requirements
# =============================================================================

class TestShipyardRequirements:
    """Tests for shipyard requirements on production."""

    def test_no_shipyard_pauses_ship_production(self, mock_empire, mock_planet):
        """Ships require shipyard to build."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = [{"type": "ship", "design_id": "Scout", "turns_remaining": 2}]
        mock_planet.has_space_shipyard = False
        mock_empire.colonies = [mock_planet]

        engine.process_production([mock_empire])

        # Turns should NOT decrement
        assert mock_planet.construction_queue[0]["turns_remaining"] == 2

    def test_no_shipyard_pauses_fighter_production(self, mock_empire, mock_planet):
        """Fighters require shipyard to build."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = [{"type": "fighter", "design_id": "Fighter", "turns_remaining": 2}]
        mock_planet.has_space_shipyard = False
        mock_empire.colonies = [mock_planet]

        engine.process_production([mock_empire])

        assert mock_planet.construction_queue[0]["turns_remaining"] == 2

    def test_no_shipyard_pauses_satellite_production(self, mock_empire, mock_planet):
        """Satellites require shipyard to build."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = [{"type": "satellite", "design_id": "Satellite", "turns_remaining": 2}]
        mock_planet.has_space_shipyard = False
        mock_empire.colonies = [mock_planet]

        engine.process_production([mock_empire])

        assert mock_planet.construction_queue[0]["turns_remaining"] == 2

    def test_complex_production_no_shipyard_needed(self, mock_empire, mock_planet, mock_galaxy):
        """Complexes don't need shipyard."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = [{"type": "complex", "design_id": "Factory", "turns_remaining": 1}]
        mock_planet.has_space_shipyard = False
        mock_empire.colonies = [mock_planet]

        with patch.object(engine, '_spawn_complex') as mock_spawn:
            engine.process_production([mock_empire], mock_galaxy)

            mock_spawn.assert_called()


# =============================================================================
# Test: Dict Format Support
# =============================================================================

class TestDictFormatSupport:
    """Tests for dict format production queue items."""

    def test_dict_format_supported(self, mock_empire, mock_planet):
        """Dict format is fully supported."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = [
            {"type": "ship", "design_id": "Cruiser", "turns_remaining": 5}
        ]
        mock_planet.has_space_shipyard = True
        mock_empire.colonies = [mock_planet]

        engine.process_production([mock_empire])

        assert mock_planet.construction_queue[0]["turns_remaining"] == 4

    def test_dict_format_default_type_is_ship(self, mock_empire, mock_planet, mock_galaxy):
        """Dict format without 'type' key defaults to ship type."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = [{"design_id": "Scout", "turns_remaining": 1}]  # No "type" key
        mock_planet.has_space_shipyard = True
        mock_empire.colonies = [mock_planet]

        with patch.object(engine, '_spawn_ship') as mock_spawn:
            engine.process_production([mock_empire], mock_galaxy)

            # Should call _spawn_ship (default type)
            mock_spawn.assert_called()


# =============================================================================
# Test: Ship Spawning
# =============================================================================

class TestShipSpawning:
    """Tests for _spawn_ship method."""

    def test_spawn_ship_requires_save_path(self, mock_planet, mock_empire, mock_galaxy):
        """Ship spawning requires save_path for design loading."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()

        # Should not crash, but should log warning
        with patch('game.strategy.engine.production_engine.log_warning') as mock_log:
            engine._spawn_ship(mock_planet, "Scout", mock_empire, mock_galaxy, save_path=None)

            mock_log.assert_called()

    def test_spawn_ship_creates_fleet(self, mock_planet, mock_empire, mock_galaxy):
        """Ship spawning creates a new fleet."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()

        with patch('game.strategy.engine.production_engine.DesignLibrary') as mock_lib_class:
            mock_library = MagicMock()
            mock_library.load_design_data.return_value = {"name": "Scout Ship"}
            mock_lib_class.return_value = mock_library

            with patch('game.strategy.engine.production_engine.ShipInstance') as mock_ship_class:
                mock_ship = MagicMock()
                mock_ship.design_data = {'vehicle_type': 'Ship'}
                mock_ship.get_calculated_stats.return_value = {'mass': 100, 'strategic_movement': 500}
                mock_ship.is_combat_capable.return_value = True
                mock_ship_class.create.return_value = mock_ship

                engine._spawn_ship(mock_planet, "Scout", mock_empire, mock_galaxy, save_path="/test")

                mock_empire.add_fleet.assert_called()

    def test_spawn_ship_increments_built_count(self, mock_planet, mock_empire, mock_galaxy):
        """Ship spawning increments design's times_built counter."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()

        with patch('game.strategy.engine.production_engine.DesignLibrary') as mock_lib_class:
            mock_library = MagicMock()
            mock_library.load_design_data.return_value = {"name": "Scout"}
            mock_lib_class.return_value = mock_library

            with patch('game.strategy.engine.production_engine.ShipInstance') as mock_ship_class:
                mock_ship = MagicMock()
                mock_ship.design_data = {'vehicle_type': 'Ship'}
                mock_ship.get_calculated_stats.return_value = {'mass': 100, 'strategic_movement': 500}
                mock_ship.is_combat_capable.return_value = True
                mock_ship_class.create.return_value = mock_ship

                engine._spawn_ship(mock_planet, "Scout", mock_empire, mock_galaxy, save_path="/test")

                mock_library.increment_built_count.assert_called_with("Scout")


# =============================================================================
# Test: Complex Spawning
# =============================================================================

class TestComplexSpawning:
    """Tests for _spawn_complex method."""

    def test_spawn_complex_adds_facility(self, mock_planet, mock_empire):
        """Complex spawning adds facility to planet."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()

        engine._spawn_complex(mock_planet, "Factory", mock_empire, save_path=None)

        assert len(mock_planet.facilities) == 1

    def test_spawn_complex_loads_design_data(self, mock_planet, mock_empire):
        """Complex spawning loads design data if save_path provided."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()

        with patch('game.strategy.engine.production_engine.DesignLibrary') as mock_lib_class:
            mock_library = MagicMock()
            mock_library.load_design_data.return_value = {"name": "Advanced Factory"}
            mock_lib_class.return_value = mock_library

            engine._spawn_complex(mock_planet, "Factory", mock_empire, save_path="/test")

            mock_library.load_design_data.assert_called_with("Factory")


# =============================================================================
# Test: Spawn Location Calculation
# =============================================================================

class TestSpawnLocation:
    """Tests for spawn location calculation."""

    def test_spawn_location_uses_planet_location(self, mock_planet, mock_empire, mock_galaxy):
        """Ship spawns at planet's location by default."""
        from game.strategy.engine.production_engine import ProductionEngine
        from game.strategy.data.fleet import Fleet

        engine = ProductionEngine()
        mock_planet.location = HexCoord(10, 20)
        mock_galaxy.get_system_of_planet.return_value = None

        with patch('game.strategy.engine.production_engine.DesignLibrary') as mock_lib_class:
            mock_library = MagicMock()
            mock_library.load_design_data.return_value = {"name": "Scout"}
            mock_lib_class.return_value = mock_library

            with patch('game.strategy.engine.production_engine.ShipInstance') as mock_ship_class:
                mock_ship = MagicMock()
                mock_ship_class.create.return_value = mock_ship

                with patch('game.strategy.engine.production_engine.Fleet') as mock_fleet_class:
                    mock_fleet = MagicMock()
                    mock_fleet_class.return_value = mock_fleet

                    engine._spawn_ship(mock_planet, "Scout", mock_empire, mock_galaxy, save_path="/test")

                    # Fleet created at planet location
                    mock_fleet_class.assert_called()
                    call_args = mock_fleet_class.call_args[0]
                    assert call_args[2] == HexCoord(10, 20)

    def test_spawn_location_calculates_global_hex(self, mock_planet, mock_empire, mock_galaxy):
        """Ship spawns at global hex when system context available."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.location = HexCoord(2, 3)  # Local coordinates

        mock_system = MagicMock()
        mock_system.global_location = HexCoord(100, 200)
        mock_galaxy.get_system_of_planet.return_value = mock_system

        with patch('game.strategy.engine.production_engine.DesignLibrary') as mock_lib_class:
            mock_library = MagicMock()
            mock_library.load_design_data.return_value = {"name": "Scout"}
            mock_lib_class.return_value = mock_library

            with patch('game.strategy.engine.production_engine.ShipInstance') as mock_ship_class:
                mock_ship = MagicMock()
                mock_ship_class.create.return_value = mock_ship

                with patch('game.strategy.engine.production_engine.Fleet') as mock_fleet_class:
                    mock_fleet = MagicMock()
                    mock_fleet_class.return_value = mock_fleet

                    engine._spawn_ship(mock_planet, "Scout", mock_empire, mock_galaxy, save_path="/test")

                    # Fleet created at global location (system + planet)
                    call_args = mock_fleet_class.call_args[0]
                    expected_loc = HexCoord(100 + 2, 200 + 3)
                    assert call_args[2] == expected_loc


# =============================================================================
# Test: Multiple Items Processing
# =============================================================================

class TestMultipleItemsProcessing:
    """Tests for processing multiple queue items."""

    def test_only_first_item_processed_per_turn(self, mock_empire, mock_planet):
        """Only first item in queue is processed each turn."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = [
            {"type": "ship", "design_id": "Scout", "turns_remaining": 3},
            {"type": "ship", "design_id": "Cruiser", "turns_remaining": 5}
        ]
        mock_planet.has_space_shipyard = True
        mock_empire.colonies = [mock_planet]

        engine.process_production([mock_empire])

        # First item decremented
        assert mock_planet.construction_queue[0]["turns_remaining"] == 2
        # Second item unchanged
        assert mock_planet.construction_queue[1]["turns_remaining"] == 5


# =============================================================================
# Test: Multiple Colonies Processing
# =============================================================================

class TestMultipleColoniesProcessing:
    """Tests for processing multiple colonies."""

    def test_all_colonies_processed(self, mock_empire):
        """All empire colonies are processed."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()

        colony1 = MagicMock()
        colony1.construction_queue = [{"type": "ship", "design_id": "Scout", "turns_remaining": 3}]
        colony1.has_space_shipyard = True

        colony2 = MagicMock()
        colony2.construction_queue = [{"type": "ship", "design_id": "Cruiser", "turns_remaining": 5}]
        colony2.has_space_shipyard = True

        mock_empire.colonies = [colony1, colony2]

        engine.process_production([mock_empire])

        assert colony1.construction_queue[0]["turns_remaining"] == 2
        assert colony2.construction_queue[0]["turns_remaining"] == 4


# =============================================================================
# Test: Multiple Empires Processing
# =============================================================================

class TestMultipleEmpiresProcessing:
    """Tests for processing multiple empires."""

    def test_all_empires_processed(self, mock_planet):
        """All empires are processed."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()

        empire1 = MagicMock()
        empire1.id = 0
        colony1 = MagicMock()
        colony1.construction_queue = [{"type": "ship", "design_id": "Scout", "turns_remaining": 3}]
        colony1.has_space_shipyard = True
        empire1.colonies = [colony1]

        empire2 = MagicMock()
        empire2.id = 1
        colony2 = MagicMock()
        colony2.construction_queue = [{"type": "ship", "design_id": "Cruiser", "turns_remaining": 5}]
        colony2.has_space_shipyard = True
        empire2.colonies = [colony2]

        engine.process_production([empire1, empire2])

        assert colony1.construction_queue[0]["turns_remaining"] == 2
        assert colony2.construction_queue[0]["turns_remaining"] == 4
