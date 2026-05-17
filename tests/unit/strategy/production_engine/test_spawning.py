"""Tests for ship spawning, complex spawning, and multi-processing.

PROJ-69 Phase 2: Updated multi-processing tests to use facility queues
for ship items (base queue now handles complexes only).
"""
import pytest
from unittest.mock import MagicMock, patch

from game.core.hex_math import HexCoord
from game.strategy.data.planetary_facility import PlanetaryFacility
from game.strategy.systems.design_library import DesignLoadResult


def _make_shipyard(instance_id: str = "yard_1") -> PlanetaryFacility:
    """Create a shipyard facility for tests."""
    return PlanetaryFacility(
        instance_id=instance_id,
        design_id="shipyard_complex",
        name="Space Shipyard",
        design_data={
            "layers": {
                "CORE": [{
                    "id": "space_shipyard",
                    "abilities": {"SpaceShipyard": {"value": 1}}
                }]
            }
        },
        is_operational=True,
    )


class TestShipSpawning:
    """Tests for _spawn_ship method."""

    def test_spawn_ship_requires_save_path(self, mock_planet, mock_empire, mock_galaxy, fresh_registries):
        """Ship spawning requires save_path for design loading."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine(registries=fresh_registries)

        # Should not crash, but should log warning
        with patch('game.strategy.engine.production_spawner.logger') as mock_logger:
            engine._spawner._spawn_ship(mock_planet, "Scout", mock_empire, mock_galaxy, save_path=None)

            mock_logger.warning.assert_called()

    def test_spawn_ship_creates_fleet(self, mock_planet, mock_empire, mock_galaxy, fresh_registries):
        """Ship spawning creates a new fleet."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine(registries=fresh_registries)

        with patch('game.strategy.engine.production_spawner.DesignLibrary') as mock_lib_class:
            mock_library = MagicMock()
            mock_library.load_design_data.return_value = DesignLoadResult.ok({"name": "Scout Ship"})
            mock_lib_class.return_value = mock_library

            with patch('game.strategy.engine.production_spawner.ShipInstance') as mock_ship_class:
                mock_ship = MagicMock()
                mock_ship.design_data = {'vehicle_type': 'Ship'}
                mock_ship.get_calculated_stats.return_value = {'mass': 100, 'strategic_movement': 500}
                mock_ship.is_combat_capable.return_value = True
                mock_ship_class.create.return_value = mock_ship

                engine._spawner._spawn_ship(mock_planet, "Scout", mock_empire, mock_galaxy, save_path="/test")

                mock_empire.add_fleet.assert_called()

    def test_spawn_ship_increments_built_count(self, mock_planet, mock_empire, mock_galaxy, fresh_registries):
        """Ship spawning increments design's times_built counter."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine(registries=fresh_registries)

        with patch('game.strategy.engine.production_spawner.DesignLibrary') as mock_lib_class:
            mock_library = MagicMock()
            mock_library.load_design_data.return_value = DesignLoadResult.ok({"name": "Scout"})
            mock_lib_class.return_value = mock_library

            with patch('game.strategy.engine.production_spawner.ShipInstance') as mock_ship_class:
                mock_ship = MagicMock()
                mock_ship.design_data = {'vehicle_type': 'Ship'}
                mock_ship.get_calculated_stats.return_value = {'mass': 100, 'strategic_movement': 500}
                mock_ship.is_combat_capable.return_value = True
                mock_ship_class.create.return_value = mock_ship

                engine._spawner._spawn_ship(mock_planet, "Scout", mock_empire, mock_galaxy, save_path="/test")

                mock_library.increment_built_count.assert_called_with("Scout")


class TestComplexSpawning:
    """Tests for _spawn_complex method."""

    def test_spawn_complex_adds_facility(self, mock_planet, mock_empire, fresh_registries):
        """Complex spawning adds facility to planet."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine(registries=fresh_registries)

        engine._spawner._create_and_place_facility(mock_planet, "Factory", mock_empire, save_path=None)

        assert len(mock_planet.facilities) == 1

    def test_spawn_complex_loads_design_data(self, mock_planet, mock_empire, fresh_registries):
        """Complex spawning loads design data if save_path provided."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine(registries=fresh_registries)

        with patch('game.strategy.engine.production_spawner.DesignLibrary') as mock_lib_class:
            mock_library = MagicMock()
            mock_library.load_design_data.return_value = DesignLoadResult.ok({"name": "Advanced Factory"})
            mock_lib_class.return_value = mock_library

            engine._spawner._create_and_place_facility(mock_planet, "Factory", mock_empire, save_path="/test")

            mock_library.load_design_data.assert_called_with("Factory")


class TestSpawnLocation:
    """Tests for spawn location calculation."""

    def test_spawn_location_uses_planet_location(self, mock_planet, mock_empire, mock_galaxy, fresh_registries):
        """Ship spawns at planet's location by default."""
        from game.strategy.engine.production_engine import ProductionEngine
        from game.strategy.data.fleet import Fleet

        engine = ProductionEngine(registries=fresh_registries)
        mock_planet.location = HexCoord(10, 20)
        mock_galaxy.get_system_of_planet.return_value = None

        with patch('game.strategy.engine.production_spawner.DesignLibrary') as mock_lib_class:
            mock_library = MagicMock()
            mock_library.load_design_data.return_value = DesignLoadResult.ok({"name": "Scout"})
            mock_lib_class.return_value = mock_library

            with patch('game.strategy.engine.production_spawner.ShipInstance') as mock_ship_class:
                mock_ship = MagicMock()
                mock_ship_class.create.return_value = mock_ship

                with patch('game.strategy.engine.production_spawner.Fleet') as mock_fleet_class:
                    mock_fleet = MagicMock()
                    mock_fleet_class.return_value = mock_fleet

                    engine._spawner._spawn_ship(mock_planet, "Scout", mock_empire, mock_galaxy, save_path="/test")

                    # Fleet created at planet location
                    mock_fleet_class.assert_called()
                    call_args = mock_fleet_class.call_args[0]
                    assert call_args[2] == HexCoord(10, 20)

    def test_spawn_location_calculates_global_hex(self, mock_planet, mock_empire, mock_galaxy, fresh_registries):
        """Ship spawns at global hex when system context available."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine(registries=fresh_registries)
        mock_planet.location = HexCoord(2, 3)  # Local coordinates

        mock_system = MagicMock()
        mock_system.global_location = HexCoord(100, 200)
        mock_galaxy.get_system_of_planet.return_value = mock_system

        with patch('game.strategy.engine.production_spawner.DesignLibrary') as mock_lib_class:
            mock_library = MagicMock()
            mock_library.load_design_data.return_value = DesignLoadResult.ok({"name": "Scout"})
            mock_lib_class.return_value = mock_library

            with patch('game.strategy.engine.production_spawner.ShipInstance') as mock_ship_class:
                mock_ship = MagicMock()
                mock_ship_class.create.return_value = mock_ship

                with patch('game.strategy.engine.production_spawner.Fleet') as mock_fleet_class:
                    mock_fleet = MagicMock()
                    mock_fleet_class.return_value = mock_fleet

                    engine._spawner._spawn_ship(mock_planet, "Scout", mock_empire, mock_galaxy, save_path="/test")

                    # Fleet created at global location (system + planet)
                    call_args = mock_fleet_class.call_args[0]
                    expected_loc = HexCoord(100 + 2, 200 + 3)
                    assert call_args[2] == expected_loc


# ---------------------------------------------------------------------------
# PROJ-427 Phase 0: characterization — pin current save_path threading in
# ProductionEngine. Phase 3 will drop save_path from the runtime production
# call chain entirely; these tests fail at that point and get rewritten.
# ---------------------------------------------------------------------------


def test_proj427_phase0_production_engine_process_takes_save_path_kwarg():
    """PROJ-427 Phase 0: ProductionEngine.process_construction_tick
    currently accepts a `save_path` keyword argument. This pins the
    threading Phase 3 will remove."""
    import inspect as _inspect
    from game.strategy.engine.production_engine import ProductionEngine

    sig = _inspect.signature(ProductionEngine.process_construction_tick)
    assert "save_path" in sig.parameters, (
        "Current ProductionEngine signature must accept save_path; "
        "this characterization pins that today."
    )


def test_proj427_phase0_production_engine_threads_save_path_into_spawner(fresh_registries):
    """PROJ-427 Phase 0: when an item completes during tick processing,
    ProductionEngine threads save_path through to ProductionSpawner.
    Phase 3 replaces this with a DesignCatalog lookup that needs no
    save_path."""
    import inspect as _inspect
    from game.strategy.engine.production_engine import ProductionEngine

    engine = ProductionEngine(registries=fresh_registries)

    sig = _inspect.signature(engine._complete_item)
    assert "save_path" in sig.parameters, (
        "_complete_item must take save_path on the current code path; "
        "Phase 3 drops this."
    )


