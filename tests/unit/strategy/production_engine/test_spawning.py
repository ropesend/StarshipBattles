"""Tests for ship spawning, complex spawning, and multi-processing.

PROJ-69 Phase 2: Updated multi-processing tests to use facility queues
for ship items (base queue now handles complexes only).
PROJ-427 Phase 3: spawn paths now resolve designs through an in-memory
``DesignCatalog`` map wired into the spawner. Tests stub the catalog
directly instead of patching ``DesignLibrary``.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.core.hex_math import HexCoord
from game.strategy.data.planetary_facility import PlanetaryFacility


def _wire_catalog(engine, empire_id, design_data):
    """Seed a catalog containing ``design_data`` under every test design_id
    spawn-tests look up, then install it on the engine's spawner."""
    from game.strategy.systems.design_catalog import DesignCatalog
    cat = DesignCatalog(empire_id=empire_id)
    # Pre-populate by short-circuiting through upsert with each ID we
    # expect the test to look up (Scout / Factory etc.).
    for design_id in ("Scout", "Factory", "Test"):
        cat._data_by_id[design_id] = design_data
    engine._spawner.set_design_catalogs_by_empire({empire_id: cat})
    return cat


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
    """Tests for _spawn_ship method.

    PROJ-427 Phase 3: designs come from an in-memory DesignCatalog wired
    onto the spawner — no DesignLibrary, no save_path.
    """

    def test_spawn_ship_without_catalog_logs_warning(self, mock_planet, mock_empire, mock_galaxy, fresh_registries):
        """Spawn with no catalog wired logs a warning and skips the spawn."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine(registries=fresh_registries)

        with patch('game.strategy.engine.production_spawner.logger') as mock_logger:
            engine._spawner._spawn_ship(mock_planet, "Scout", mock_empire, mock_galaxy)

            mock_logger.warning.assert_called()

    def test_spawn_ship_creates_fleet(self, mock_planet, mock_empire, mock_galaxy, fresh_registries):
        """Ship spawning creates a new fleet using catalog data."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine(registries=fresh_registries)
        _wire_catalog(engine, mock_empire.id, {"name": "Scout Ship"})

        with patch('game.strategy.engine.production_spawner.ShipInstance') as mock_ship_class:
            mock_ship = MagicMock()
            mock_ship.design_data = {'vehicle_type': 'Ship'}
            mock_ship.get_calculated_stats.return_value = {'mass': 100, 'strategic_movement': 500}
            mock_ship.is_combat_capable.return_value = True
            mock_ship_class.create.return_value = mock_ship

            engine._spawner._spawn_ship(mock_planet, "Scout", mock_empire, mock_galaxy)

            mock_empire.add_fleet.assert_called()

    def test_spawn_ship_records_built_count_on_catalog(self, mock_planet, mock_empire, mock_galaxy, fresh_registries):
        """Ship spawning bumps the catalog's pending built-count entry."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine(registries=fresh_registries)
        cat = _wire_catalog(engine, mock_empire.id, {"name": "Scout"})

        with patch('game.strategy.engine.production_spawner.ShipInstance') as mock_ship_class:
            mock_ship = MagicMock()
            mock_ship.design_data = {'vehicle_type': 'Ship'}
            mock_ship.get_calculated_stats.return_value = {'mass': 100, 'strategic_movement': 500}
            mock_ship.is_combat_capable.return_value = True
            mock_ship_class.create.return_value = mock_ship

            engine._spawner._spawn_ship(mock_planet, "Scout", mock_empire, mock_galaxy)

            assert cat.pending_built_counts.get("Scout") == 1


class TestComplexSpawning:
    """Tests for complex placement on a planet."""

    def test_spawn_complex_adds_facility(self, mock_planet, mock_empire, fresh_registries):
        """Complex spawning adds facility to planet (no catalog wired -> empty data)."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine(registries=fresh_registries)
        engine._spawner._create_and_place_facility(mock_planet, "Factory", mock_empire)

        assert len(mock_planet.facilities) == 1

    def test_spawn_complex_loads_design_data_from_catalog(self, mock_planet, mock_empire, fresh_registries):
        """Complex spawn looks up design data via the catalog."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine(registries=fresh_registries)
        _wire_catalog(engine, mock_empire.id, {"name": "Advanced Factory"})

        engine._spawner._create_and_place_facility(mock_planet, "Factory", mock_empire)

        # Facility should reflect data from the catalog.
        assert mock_planet.facilities[-1].design_data == {"name": "Advanced Factory"}


class TestSpawnLocation:
    """Tests for spawn location calculation."""

    def test_spawn_location_uses_planet_location(self, mock_planet, mock_empire, mock_galaxy, fresh_registries):
        """Ship spawns at planet's location by default."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine(registries=fresh_registries)
        mock_planet.location = HexCoord(10, 20)
        mock_galaxy.get_system_of_planet.return_value = None
        _wire_catalog(engine, mock_empire.id, {"name": "Scout"})

        with patch('game.strategy.engine.production_spawner.ShipInstance') as mock_ship_class:
            mock_ship = MagicMock()
            mock_ship_class.create.return_value = mock_ship

            with patch('game.strategy.engine.production_spawner.Fleet') as mock_fleet_class:
                mock_fleet = MagicMock()
                mock_fleet_class.return_value = mock_fleet

                engine._spawner._spawn_ship(mock_planet, "Scout", mock_empire, mock_galaxy)

                mock_fleet_class.assert_called()
                call_args = mock_fleet_class.call_args[0]
                assert call_args[2] == HexCoord(10, 20)

    def test_spawn_location_calculates_global_hex(self, mock_planet, mock_empire, mock_galaxy, fresh_registries):
        """Ship spawns at global hex when system context available."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine(registries=fresh_registries)
        mock_planet.location = HexCoord(2, 3)

        mock_system = MagicMock()
        mock_system.global_location = HexCoord(100, 200)
        mock_galaxy.get_system_of_planet.return_value = mock_system
        _wire_catalog(engine, mock_empire.id, {"name": "Scout"})

        with patch('game.strategy.engine.production_spawner.ShipInstance') as mock_ship_class:
            mock_ship = MagicMock()
            mock_ship_class.create.return_value = mock_ship

            with patch('game.strategy.engine.production_spawner.Fleet') as mock_fleet_class:
                mock_fleet = MagicMock()
                mock_fleet_class.return_value = mock_fleet

                engine._spawner._spawn_ship(mock_planet, "Scout", mock_empire, mock_galaxy)

                call_args = mock_fleet_class.call_args[0]
                expected_loc = HexCoord(100 + 2, 200 + 3)
                assert call_args[2] == expected_loc


# ---------------------------------------------------------------------------
# PROJ-427 Phase 3: assert the runtime production / construction call chain
# is FREE of save_path. Spawners receive an in-memory DesignCatalog map
# instead.
# ---------------------------------------------------------------------------


def test_proj427_production_engine_process_does_not_take_save_path():
    """PROJ-427 Phase 3: ``process_construction_tick`` no longer accepts
    ``save_path``."""
    import inspect as _inspect
    from game.strategy.engine.production_engine import ProductionEngine

    sig = _inspect.signature(ProductionEngine.process_construction_tick)
    assert "save_path" not in sig.parameters, (
        "PROJ-427 Phase 3: save_path must be removed from "
        "process_construction_tick."
    )


def test_proj427_production_engine_complete_item_does_not_take_save_path(fresh_registries):
    """PROJ-427 Phase 3: ``_complete_item`` no longer accepts ``save_path``."""
    import inspect as _inspect
    from game.strategy.engine.production_engine import ProductionEngine

    engine = ProductionEngine(registries=fresh_registries)
    sig = _inspect.signature(engine._complete_item)
    assert "save_path" not in sig.parameters, (
        "PROJ-427 Phase 3: save_path must be removed from _complete_item."
    )


def test_proj427_production_engine_forwards_catalog_map_to_spawner(fresh_registries):
    """PROJ-427 Phase 3: ``set_design_catalogs_by_empire`` forwards through
    to the embedded ``ProductionSpawner``."""
    from game.strategy.engine.production_engine import ProductionEngine
    from game.strategy.systems.design_catalog import DesignCatalog

    engine = ProductionEngine(registries=fresh_registries)
    catalogs = {0: DesignCatalog(empire_id=0)}
    engine.set_design_catalogs_by_empire(catalogs)
    assert engine._spawner._design_catalogs_by_empire is catalogs


