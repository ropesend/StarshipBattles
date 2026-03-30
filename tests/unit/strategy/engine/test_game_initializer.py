"""
Unit tests for GameInitializer.

Tests galaxy initialization and empire scenario setup.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch

from game.core.hex_math import HexCoord


class TestGameInitializer:
    """Tests for GameInitializer class."""

    def test_initialize_returns_galaxy_and_empires(self):
        """initialize() should return a tuple of (Galaxy, list[Empire])."""
        from game.strategy.engine.game_initializer import GameInitializer
        from game.strategy.engine.game_config import GameConfig

        config = GameConfig(system_count=5, galaxy_radius=1000)
        galaxy, empires = GameInitializer.initialize(config)

        assert galaxy is not None
        assert len(empires) == 2  # Default config has 2 players
        assert len(galaxy.systems) == 5

    def test_initialize_creates_correct_empire_count(self):
        """initialize() should create one empire per player in config."""
        from game.strategy.engine.game_initializer import GameInitializer
        from game.strategy.engine.game_config import GameConfig, PlayerConfig

        players = [
            PlayerConfig(name="Player 1"),
            PlayerConfig(name="Player 2"),
            PlayerConfig(name="Player 3"),
        ]
        config = GameConfig(system_count=5, players=players)
        galaxy, empires = GameInitializer.initialize(config)

        assert len(empires) == 3
        assert empires[0].name == "Player 1"
        assert empires[1].name == "Player 2"
        assert empires[2].name == "Player 3"

    def test_initialize_assigns_homeworlds(self):
        """initialize() should assign homeworld colonies to each empire."""
        from game.strategy.engine.game_initializer import GameInitializer
        from game.strategy.engine.game_config import GameConfig

        config = GameConfig(system_count=10, galaxy_radius=2000)
        galaxy, empires = GameInitializer.initialize(config)

        # Each empire should have at least one colony (homeworld)
        for empire in empires:
            assert len(empire.colonies) >= 1

    def test_initialize_uses_galaxy_seed_for_determinism(self):
        """initialize() with same seed should produce same galaxy."""
        from game.strategy.engine.game_initializer import GameInitializer
        from game.strategy.engine.game_config import GameConfig

        config1 = GameConfig(system_count=10, galaxy_seed=12345)
        config2 = GameConfig(system_count=10, galaxy_seed=12345)

        galaxy1, _ = GameInitializer.initialize(config1)
        galaxy2, _ = GameInitializer.initialize(config2)

        # Same seed should produce same system locations
        coords1 = sorted([str(c) for c in galaxy1.systems.keys()])
        coords2 = sorted([str(c) for c in galaxy2.systems.keys()])
        assert coords1 == coords2

    def test_initialize_different_seeds_different_galaxies(self):
        """initialize() with different seeds should produce different galaxies."""
        from game.strategy.engine.game_initializer import GameInitializer
        from game.strategy.engine.game_config import GameConfig

        config1 = GameConfig(system_count=10, galaxy_seed=12345)
        config2 = GameConfig(system_count=10, galaxy_seed=54321)

        galaxy1, _ = GameInitializer.initialize(config1)
        galaxy2, _ = GameInitializer.initialize(config2)

        coords1 = sorted([str(c) for c in galaxy1.systems.keys()])
        coords2 = sorted([str(c) for c in galaxy2.systems.keys()])
        # Very unlikely to be the same with different seeds
        assert coords1 != coords2

    def test_initialize_generates_warp_lanes(self):
        """initialize() should generate warp lanes between systems."""
        from game.strategy.engine.game_initializer import GameInitializer
        from game.strategy.engine.game_config import GameConfig

        config = GameConfig(system_count=10)
        galaxy, _ = GameInitializer.initialize(config)

        # At least some systems should have warp points
        systems_with_warp = sum(
            1 for s in galaxy.systems.values() if s.warp_points
        )
        assert systems_with_warp > 0

    def test_empire_always_has_race_config(self):
        """Empires should always have a RaceConfig, even without explicit race setup (BUG-88)."""
        from game.strategy.engine.game_initializer import GameInitializer
        from game.strategy.engine.game_config import GameConfig, PlayerConfig
        from game.strategy.data.race_config import RaceConfig

        # Create players WITHOUT explicit race_config (simulates new game without race setup)
        players = [
            PlayerConfig(name="Test Empire", theme="Federation", color=(100, 100, 255)),
        ]
        config = GameConfig(system_count=5, players=players)
        galaxy, empires = GameInitializer.initialize(config)

        # Empire should have a default race_config with player name
        assert empires[0].race_config is not None
        assert isinstance(empires[0].race_config, RaceConfig)
        assert empires[0].race_config.name == "Test Empire"

    def test_empire_preserves_explicit_race_config(self):
        """Empires with explicit race_config should keep it as-is (BUG-88)."""
        from game.strategy.engine.game_initializer import GameInitializer
        from game.strategy.engine.game_config import GameConfig, PlayerConfig
        from game.strategy.data.race_config import RaceConfig

        explicit_race = RaceConfig(
            race_id="custom_species",
            name="Custom Species",
            faction_name="Custom Empire",
            aptitude_strength=80
        )
        players = [
            PlayerConfig(
                name="Custom Species",
                theme="Federation",
                color=(100, 100, 255),
                race_config=explicit_race
            ),
        ]
        config = GameConfig(system_count=5, players=players)
        galaxy, empires = GameInitializer.initialize(config)

        # Should keep the explicit race config
        assert empires[0].race_config is explicit_race
        assert empires[0].race_config.race_id == "custom_species"
        assert empires[0].race_config.aptitude_strength == 80

    def test_adjust_homeworld_to_race_sets_planet_type(self):
        """_adjust_homeworld_to_race should set planet type from race config."""
        from game.strategy.engine.game_initializer import GameInitializer
        from game.strategy.data.planet import Planet, PlanetType
        from game.core.hex_math import HexCoord

        planet = Planet(
            name="Test", location=HexCoord(0, 0), orbit_distance=1,
            mass=5.9e24, radius=6.3e6, surface_area=5.1e14, density=5500.0,
            surface_gravity=9.81, surface_pressure=101325.0, surface_temperature=288.0,
            surface_water=0.7, tectonic_activity=0.5, magnetic_field=1.0,
            planet_type=PlanetType.BARREN
        )
        race_config = Mock()
        race_config.homeworld_type = "CONTINENTAL"  # Earth-like
        race_config.gravity_ideal = 1.0
        race_config.temperature_ideal = 288.0
        race_config.water_ideal = 0.7
        race_config.atmosphere_preferences = {"O2": 1.0, "N2": 0.5}

        GameInitializer._adjust_homeworld_to_race(planet, race_config)

        assert planet.planet_type == PlanetType.CONTINENTAL

    def test_adjust_homeworld_to_race_sets_gravity(self):
        """_adjust_homeworld_to_race should set surface gravity."""
        from game.strategy.engine.game_initializer import GameInitializer
        from game.strategy.data.planet import Planet, PlanetType
        from game.core.hex_math import HexCoord

        planet = Planet(
            name="Test", location=HexCoord(0, 0), orbit_distance=1,
            mass=5.9e24, radius=6.3e6, surface_area=5.1e14, density=5500.0,
            surface_gravity=9.81, surface_pressure=101325.0, surface_temperature=288.0,
            surface_water=0.5, tectonic_activity=0.5, magnetic_field=1.0,
            planet_type=PlanetType.BARREN
        )
        race_config = Mock()
        race_config.homeworld_type = "TERRAN"
        race_config.gravity_ideal = 1.2  # 1.2g
        race_config.temperature_ideal = 288.0
        race_config.water_ideal = 0.5
        race_config.atmosphere_preferences = {}

        GameInitializer._adjust_homeworld_to_race(planet, race_config)

        assert abs(planet.surface_gravity - 1.2 * 9.81) < 0.1

    def test_adjust_homeworld_translates_gas_names_to_formulas(self):
        """_adjust_homeworld_to_race should convert full gas names to chemical formulas (BUG-90)."""
        from game.strategy.engine.game_initializer import GameInitializer
        from game.strategy.data.planet import Planet, PlanetType
        from game.core.hex_math import HexCoord

        planet = Planet(
            name="Test", location=HexCoord(0, 0), orbit_distance=1,
            mass=5.9e24, radius=6.3e6, surface_area=5.1e14, density=5500.0,
            surface_gravity=9.81, surface_pressure=101325.0, surface_temperature=288.0,
            surface_water=0.7, tectonic_activity=0.5, magnetic_field=1.0,
            planet_type=PlanetType.BARREN
        )
        race_config = Mock()
        race_config.homeworld_type = "CONTINENTAL"
        race_config.gravity_ideal = 1.0
        race_config.temperature_ideal = 288.0
        race_config.water_ideal = 0.7
        # Use full gas names as in DEFAULT_ATMOSPHERE_PREFERENCES / homeworld_presets.json
        race_config.atmosphere_preferences = {"Oxygen": 50.0, "Nitrogen": 30.0}

        GameInitializer._adjust_homeworld_to_race(planet, race_config)

        # Atmosphere dict should use chemical formulas, not full names
        assert "O2" in planet.atmosphere, "Expected 'O2' key, got full name 'Oxygen'"
        assert "N2" in planet.atmosphere, "Expected 'N2' key, got full name 'Nitrogen'"
        assert "Oxygen" not in planet.atmosphere, "Full name 'Oxygen' should be translated to 'O2'"
        assert "Nitrogen" not in planet.atmosphere, "Full name 'Nitrogen' should be translated to 'N2'"

    def test_adjust_homeworld_handles_invalid_planet_type(self):
        """_adjust_homeworld_to_race should handle invalid planet type gracefully."""
        from game.strategy.engine.game_initializer import GameInitializer
        from game.strategy.data.planet import Planet, PlanetType
        from game.core.hex_math import HexCoord

        planet = Planet(
            name="Test", location=HexCoord(0, 0), orbit_distance=1,
            mass=5.9e24, radius=6.3e6, surface_area=5.1e14, density=5500.0,
            surface_gravity=9.81, surface_pressure=101325.0, surface_temperature=288.0,
            surface_water=0.5, tectonic_activity=0.5, magnetic_field=1.0,
            planet_type=PlanetType.BARREN
        )
        original_type = planet.planet_type

        race_config = Mock()
        race_config.homeworld_type = "INVALID_TYPE_XYZ"
        race_config.gravity_ideal = 1.0
        race_config.temperature_ideal = 288.0
        race_config.water_ideal = 0.5
        race_config.atmosphere_preferences = {}

        # Should not raise, should keep existing type
        GameInitializer._adjust_homeworld_to_race(planet, race_config)
        assert planet.planet_type == original_type


class TestEnsureHomeworldResourceQuality:
    """Tests for _ensure_homeworld_resource_quality method."""

    def _make_planet(self, resources):
        """Create a Planet with given resources dict."""
        from game.strategy.data.planet import Planet, PlanetType
        planet = Planet(
            name="Test", location=HexCoord(0, 0), orbit_distance=1,
            mass=5.9e24, radius=6.3e6, surface_area=5.1e14, density=5500.0,
            surface_gravity=9.81, surface_pressure=101325.0, surface_temperature=288.0,
            surface_water=0.7, tectonic_activity=0.5, magnetic_field=1.0,
            planet_type=PlanetType.CONTINENTAL
        )
        planet.deposits = resources
        return planet

    def test_raises_low_quality_to_floor(self):
        """Resources below the homeworld floor should be raised to it."""
        from game.strategy.engine.game_initializer import GameInitializer

        planet = self._make_planet({
            "metals": {"quantity": 100000, "quality": 10.0},
            "organics": {"quantity": 200000, "quality": 3.0},
            "vapors": {"quantity": 150000, "quality": 25.0},
        })

        GameInitializer._ensure_homeworld_resource_quality(planet)

        assert planet.deposits["metals"]["quality"] == 50.0
        assert planet.deposits["organics"]["quality"] == 50.0
        assert planet.deposits["vapors"]["quality"] == 50.0

    def test_preserves_high_quality(self):
        """Resources already above the floor should not be changed."""
        from game.strategy.engine.game_initializer import GameInitializer

        planet = self._make_planet({
            "metals": {"quantity": 100000, "quality": 75.0},
            "exotics": {"quantity": 50000, "quality": 90.0},
        })

        GameInitializer._ensure_homeworld_resource_quality(planet)

        assert planet.deposits["metals"]["quality"] == 75.0
        assert planet.deposits["exotics"]["quality"] == 90.0

    def test_mixed_resources(self):
        """Only resources below the floor should be raised; others stay."""
        from game.strategy.engine.game_initializer import GameInitializer

        planet = self._make_planet({
            "metals": {"quantity": 100000, "quality": 10.0},
            "organics": {"quantity": 200000, "quality": 80.0},
            "radioactives": {"quantity": 150000, "quality": 50.0},
        })

        GameInitializer._ensure_homeworld_resource_quality(planet)

        assert planet.deposits["metals"]["quality"] == 50.0
        assert planet.deposits["organics"]["quality"] == 80.0
        assert planet.deposits["radioactives"]["quality"] == 50.0  # Exactly at floor, unchanged

    def test_uses_config_value(self):
        """Should use homeworld_quality_floor from ResourceGenerationConfig."""
        from game.strategy.engine.game_initializer import GameInitializer
        from game.strategy.data.resource_generation_config import ResourceGenerationConfig

        planet = self._make_planet({
            "metals": {"quantity": 100000, "quality": 10.0},
        })

        mock_cfg = ResourceGenerationConfig(None)
        mock_cfg.homeworld_quality_floor = 70.0

        with patch(
            'game.strategy.data.resource_generation_config.get_resource_generation_config',
            return_value=mock_cfg
        ):
            GameInitializer._ensure_homeworld_resource_quality(planet)

        assert planet.deposits["metals"]["quality"] == 70.0

    def test_quantity_not_modified(self):
        """Resource quantity should never be changed by quality enforcement."""
        from game.strategy.engine.game_initializer import GameInitializer

        planet = self._make_planet({
            "metals": {"quantity": 5000, "quality": 10.0},
        })

        GameInitializer._ensure_homeworld_resource_quality(planet)

        assert planet.deposits["metals"]["quantity"] == 5000


class TestGalaxyFleetRegistry:
    """Tests for Galaxy fleet registry (O(1) lookup)."""

    def test_get_fleet_by_id_returns_fleet(self):
        """get_fleet_by_id() should return the fleet with matching ID."""
        from game.strategy.data.galaxy import Galaxy
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        galaxy = Galaxy(radius=1000)
        fleet = Fleet(fleet_id=42, owner_id=0, location=HexCoord(0, 0))
        galaxy.register_fleet(fleet)

        result = galaxy.get_fleet_by_id(42)
        assert result is fleet

    def test_get_fleet_by_id_returns_none_for_unknown(self):
        """get_fleet_by_id() should return None for unknown fleet ID."""
        from game.strategy.data.galaxy import Galaxy

        galaxy = Galaxy(radius=1000)

        result = galaxy.get_fleet_by_id(999)
        assert result is None

    def test_unregister_fleet_removes_from_registry(self):
        """unregister_fleet() should remove fleet from registry."""
        from game.strategy.data.galaxy import Galaxy
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        galaxy = Galaxy(radius=1000)
        fleet = Fleet(fleet_id=42, owner_id=0, location=HexCoord(0, 0))
        galaxy.register_fleet(fleet)
        assert galaxy.get_fleet_by_id(42) is fleet

        galaxy.unregister_fleet(fleet)
        assert galaxy.get_fleet_by_id(42) is None

    def test_fleet_registry_handles_multiple_fleets(self):
        """Fleet registry should handle multiple fleets correctly."""
        from game.strategy.data.galaxy import Galaxy
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        galaxy = Galaxy(radius=1000)
        fleet1 = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        fleet2 = Fleet(fleet_id=2, owner_id=1, location=HexCoord(10, 10))
        fleet3 = Fleet(fleet_id=3, owner_id=0, location=HexCoord(20, 20))

        galaxy.register_fleet(fleet1)
        galaxy.register_fleet(fleet2)
        galaxy.register_fleet(fleet3)

        assert galaxy.get_fleet_by_id(1) is fleet1
        assert galaxy.get_fleet_by_id(2) is fleet2
        assert galaxy.get_fleet_by_id(3) is fleet3

    def test_fleet_registry_preserved_after_serialization(self):
        """Fleet registry should work after galaxy deserialization."""
        from game.strategy.data.galaxy import Galaxy
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        galaxy = Galaxy(radius=1000)
        # Note: Fleet registry is NOT serialized - fleets are owned by empires
        # After deserialization, empires need to re-register their fleets

        # Serialize and deserialize
        data = galaxy.to_dict()
        restored = Galaxy.from_dict(data)

        # Empty registry after restore (fleets come from empires)
        assert restored.get_fleet_by_id(42) is None


class TestGameSessionFleetLookup:
    """Tests for GameSession fleet lookup using Galaxy registry."""

    def test_get_fleet_by_id_uses_galaxy_registry(self):
        """_get_fleet_by_id should use Galaxy registry for O(1) lookup."""
        from game.strategy.engine.game_session import GameSession
        from game.strategy.engine.game_config import GameConfig
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        config = GameConfig(system_count=3)
        session = GameSession(config=config)

        # Create and add a fleet to empire
        fleet = Fleet(fleet_id=42, owner_id=0, location=HexCoord(0, 0))
        session.empires[0].add_fleet(fleet)
        session.galaxy.register_fleet(fleet)

        # Should find via registry
        result = session._get_fleet_by_id(42)
        assert result is fleet

    def test_get_fleet_by_id_returns_none_for_unknown(self):
        """_get_fleet_by_id should return None for unknown fleet."""
        from game.strategy.engine.game_session import GameSession
        from game.strategy.engine.game_config import GameConfig

        config = GameConfig(system_count=3)
        session = GameSession(config=config)

        result = session._get_fleet_by_id(999)
        assert result is None
