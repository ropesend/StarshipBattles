"""Tests for ship spawning, complex spawning, and multi-processing."""
import pytest
from unittest.mock import MagicMock, patch

from game.strategy.data.hex_math import HexCoord


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
