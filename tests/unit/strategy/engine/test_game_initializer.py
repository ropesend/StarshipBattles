"""
Unit tests for GameInitializer.

Tests galaxy initialization and empire scenario setup.
"""

import pytest
from unittest.mock import patch

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

    # PROJ-283 Phase 4: replaced Mock-based race_configs with real
    # RaceConfig instances built via the test helper. The new
    # `_adjust_homeworld_to_race` reads `race_config.preferences[<id>].setpoint`
    # rather than the deleted scalar attributes.

    @staticmethod
    def _make_race(homeworld_type, gravity_ms2=9.81, temp_k=288.0,
                   water=0.7, atmosphere_pa=None):
        from game.strategy.data.race_config import RaceConfig
        from game.strategy.data.environmental_preference import EnvironmentalPreference
        from game.strategy.data.habitability_factors import get_factor

        rc = RaceConfig(
            name="Test",
            flag_id="flag_test",
            portrait_id="portrait_test",
            theme_id="Federation",
            homeworld_type=homeworld_type,
        )

        def _override(factor_id, setpoint):
            f = get_factor(factor_id)
            rc.preferences[factor_id] = EnvironmentalPreference(
                setpoint=setpoint, tolerance=f.default_tolerance,
                min_value=f.min_value, max_value=f.max_value, step=f.step,
            )

        _override("gravity", gravity_ms2)
        _override("temperature", temp_k)
        _override("water", water)
        for formula, pa in (atmosphere_pa or {}).items():
            _override(f"gas.{formula}", pa)
        return rc

    @staticmethod
    def _make_test_planet():
        from game.strategy.data.planet import Planet, PlanetType
        from game.core.hex_math import HexCoord
        return Planet(
            name="Test", location=HexCoord(0, 0), orbit_distance=1,
            mass=5.9e24, radius=6.3e6, surface_area=5.1e14, density=5500.0,
            surface_gravity=9.81, surface_pressure=101325.0,
            surface_temperature=288.0, surface_water=0.5, tectonic_activity=0.5,
            magnetic_field=1.0, planet_type=PlanetType.BARREN,
        )

    def test_adjust_homeworld_to_race_sets_planet_type(self):
        """_adjust_homeworld_to_race should set planet type from race config."""
        from game.strategy.engine.game_initializer import GameInitializer
        from game.strategy.data.planet import PlanetType

        planet = self._make_test_planet()
        race_config = self._make_race(
            homeworld_type="CONTINENTAL",
            atmosphere_pa={"O2": 21000.0, "N2": 79000.0},
        )

        GameInitializer._adjust_homeworld_to_race(planet, race_config)

        assert planet.planet_type == PlanetType.CONTINENTAL

    def test_adjust_homeworld_to_race_sets_gravity(self):
        """_adjust_homeworld_to_race should set surface gravity."""
        from game.strategy.engine.game_initializer import GameInitializer

        planet = self._make_test_planet()
        # 1.2 g = 11.772 m/s²
        race_config = self._make_race(homeworld_type="CONTINENTAL", gravity_ms2=1.2 * 9.81)

        GameInitializer._adjust_homeworld_to_race(planet, race_config)

        assert abs(planet.surface_gravity - 1.2 * 9.81) < 0.1

    def test_adjust_homeworld_translates_gas_names_to_formulas(self):
        """_adjust_homeworld_to_race should populate atmosphere by chemical
        formula (BUG-90 / PROJ-283: gas factors are keyed by formula in
        the registry, no display-name translation needed)."""
        from game.strategy.engine.game_initializer import GameInitializer

        planet = self._make_test_planet()
        race_config = self._make_race(
            homeworld_type="CONTINENTAL",
            atmosphere_pa={"O2": 21000.0, "N2": 79000.0},
        )

        GameInitializer._adjust_homeworld_to_race(planet, race_config)

        assert "O2" in planet.atmosphere
        assert "N2" in planet.atmosphere
        assert "Oxygen" not in planet.atmosphere
        assert "Nitrogen" not in planet.atmosphere

    def test_adjust_homeworld_handles_invalid_planet_type(self):
        """_adjust_homeworld_to_race should handle invalid planet type gracefully."""
        from game.strategy.engine.game_initializer import GameInitializer

        planet = self._make_test_planet()
        original_type = planet.planet_type
        race_config = self._make_race(homeworld_type="INVALID_TYPE_XYZ")

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


# ---------------------------------------------------------------------------
# FEAT-27: galaxy size 1, default 2, distinct empire placement at N≥2
# ---------------------------------------------------------------------------

class TestFeat27EmpirePlacement:
    """Empire-to-system / empire-to-planet assignment under FEAT-27 rules."""

    @staticmethod
    def _config(system_count: int, num_empires: int, seed: int = 42):
        from game.strategy.engine.game_config import GameConfig, PlayerConfig
        players = [PlayerConfig(name=f"E{i}") for i in range(num_empires)]
        return GameConfig(
            system_count=system_count,
            players=players,
            galaxy_radius=2000,
            galaxy_seed=seed,
        )

    def test_n1_e1_works(self):
        from game.strategy.engine.game_initializer import GameInitializer
        config = self._config(system_count=1, num_empires=1)
        galaxy, empires = GameInitializer.initialize(config)
        assert len(galaxy.systems) == 1
        assert len(empires) == 1
        assert len(empires[0].colonies) == 1

    def test_n1_e2_shares_system_distinct_planets(self):
        """N=1 + E=2: both empires colonise the lone system on different planets."""
        from game.strategy.engine.game_initializer import GameInitializer

        config = self._config(system_count=1, num_empires=2)
        galaxy, empires = GameInitializer.initialize(config)

        assert len(galaxy.systems) == 1
        the_system = list(galaxy.systems.values())[0]

        # Both empires have a colony.
        assert len(empires[0].colonies) == 1
        assert len(empires[1].colonies) == 1

        # Both colonies are inside the lone system.
        assert empires[0].colonies[0] in the_system.planets
        assert empires[1].colonies[0] in the_system.planets

        # Different planets — not the same Python object.
        assert empires[0].colonies[0] is not empires[1].colonies[0]

        # owner_id consistency: each planet reports the correct empire.
        assert empires[0].colonies[0].owner_id == empires[0].id
        assert empires[1].colonies[0].owner_id == empires[1].id

    def test_n1_e2_no_warp_points(self):
        from game.strategy.engine.game_initializer import GameInitializer
        config = self._config(system_count=1, num_empires=2)
        galaxy, _empires = GameInitializer.initialize(config)
        total_warps = sum(len(sys.warp_points) for sys in galaxy.systems.values())
        assert total_warps == 0

    def test_n2_e2_distinct_systems(self):
        """N=2 + E=2: each empire owns a different system (the original invariant)."""
        from game.strategy.engine.game_initializer import GameInitializer

        config = self._config(system_count=2, num_empires=2)
        galaxy, empires = GameInitializer.initialize(config)

        assert len(galaxy.systems) == 2
        # Find each empire's home system by looking up which system contains its colony.
        sys_for_empire = []
        for empire in empires:
            home_planet = empire.colonies[0]
            for sys in galaxy.systems.values():
                if home_planet in sys.planets:
                    sys_for_empire.append(sys)
                    break

        assert len(sys_for_empire) == 2
        assert sys_for_empire[0] is not sys_for_empire[1], (
            "Empires must occupy distinct systems at N≥2"
        )

    def test_n2_e2_one_warp_link(self):
        from game.strategy.engine.game_initializer import GameInitializer
        config = self._config(system_count=2, num_empires=2)
        galaxy, _empires = GameInitializer.initialize(config)
        total_warps = sum(len(sys.warp_points) for sys in galaxy.systems.values())
        assert total_warps == 2  # one bidirectional link = one warp point per system

    def test_n2_far_apart_seed_2_still_links(self):
        """Regression: galaxy_radius=4000 + galaxy_seed=2 historically placed
        the only two systems many cell-widths apart and the MST left them
        isolated. Every system must own at least one warp point at N=2.
        """
        from game.strategy.engine.game_config import GameConfig
        from game.strategy.engine.game_initializer import GameInitializer

        config = GameConfig(
            system_count=2,
            galaxy_radius=4000,
            galaxy_seed=2,
        )
        galaxy, _empires = GameInitializer.initialize(config)

        assert len(galaxy.systems) == 2
        for sys in galaxy.systems.values():
            assert len(sys.warp_points) >= 1, (
                f"System {sys.name} at {sys.global_location} is isolated"
            )
        total_warps = sum(len(sys.warp_points) for sys in galaxy.systems.values())
        assert total_warps == 2

    def test_n5_e4_distinct_systems_evenly_spread(self):
        """N=5 + E=4: linspace places empires at indices [0, 1, 3, 4] (no clustering)."""
        from game.strategy.engine.game_initializer import GameInitializer

        config = self._config(system_count=5, num_empires=4)
        galaxy, empires = GameInitializer.initialize(config)

        # All four empires must be in distinct systems.
        empire_systems = []
        for empire in empires:
            home_planet = empire.colonies[0]
            for idx, sys in enumerate(galaxy.systems.values()):
                if home_planet in sys.planets:
                    empire_systems.append(idx)
                    break

        assert len(empire_systems) == 4
        assert len(set(empire_systems)) == 4, (
            f"All empires must occupy distinct systems, got indices {empire_systems}"
        )


class TestFeat27PlanetShortageRetry:
    """N=1 with insufficient planets must retry generation, then refuse."""

    def test_planet_shortage_eventually_raises(self, monkeypatch):
        """If every regeneration attempt produces too few planets, raise ValidationException."""
        from game.core.exceptions import ValidationException
        from game.strategy.engine.game_initializer import GameInitializer
        from game.strategy.engine.game_config import GameConfig, PlayerConfig

        # Force every generated system to have zero planets.
        from game.strategy.data import galaxy_system_generator

        original = galaxy_system_generator.GalaxySystemGenerator.generate_systems

        def _generate_no_planets(self, galaxy, count, *args, **kwargs):
            systems = original(self, galaxy, count, *args, **kwargs)
            for sys in systems:
                sys.planets = []
            return systems

        monkeypatch.setattr(
            galaxy_system_generator.GalaxySystemGenerator,
            "generate_systems",
            _generate_no_planets,
        )

        players = [PlayerConfig(name=f"E{i}") for i in range(2)]
        config = GameConfig(
            system_count=1,
            players=players,
            galaxy_radius=2000,
            galaxy_seed=99,
        )

        with pytest.raises(ValidationException) as exc_info:
            GameInitializer.initialize(config)

        msg = str(exc_info.value).lower()
        assert "planet" in msg or "insufficient" in msg or "regener" in msg or "attempts" in msg

    def test_planet_shortage_retry_succeeds_when_a_later_attempt_has_enough(self, monkeypatch):
        """If the first attempt is short but a later attempt succeeds, initialize() should win."""
        from game.strategy.engine.game_initializer import GameInitializer
        from game.strategy.engine.game_config import GameConfig, PlayerConfig

        from game.strategy.data import galaxy_system_generator

        original = galaxy_system_generator.GalaxySystemGenerator.generate_systems
        call_count = {"n": 0}

        def _flaky_generate(self, galaxy, count, *args, **kwargs):
            call_count["n"] += 1
            systems = original(self, galaxy, count, *args, **kwargs)
            if call_count["n"] == 1:
                # First attempt: zero planets to force a retry.
                for sys in systems:
                    sys.planets = []
            return systems

        monkeypatch.setattr(
            galaxy_system_generator.GalaxySystemGenerator,
            "generate_systems",
            _flaky_generate,
        )

        players = [PlayerConfig(name=f"E{i}") for i in range(2)]
        config = GameConfig(
            system_count=1,
            players=players,
            galaxy_radius=2000,
            galaxy_seed=7,
        )

        galaxy, empires = GameInitializer.initialize(config)
        assert call_count["n"] >= 2, "initialize() should have retried generation at least once"
        assert len(empires[0].colonies) == 1
        assert len(empires[1].colonies) == 1
        assert empires[0].colonies[0] is not empires[1].colonies[0]
