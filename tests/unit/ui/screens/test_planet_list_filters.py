
import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from game.core.hex_math import HexCoord
from game.strategy.data.planet import Planet, PlanetType
from game.ui.screens.planet_list_filters import gather_planets, filter_planets

class TestPlanetListFilters:
    """Tests for planet list filtering and categorization."""
    
    def test_gather_planets_categorization(self):
        """Verify gather_planets correctly categorizes new planet types."""
        galaxy = MagicMock()
        empire = MagicMock()
        
        # Create mock planets with new types
        p1 = MagicMock(spec=Planet)
        p1.planet_type = PlanetType.CONTINENTAL
        p1.name = "Terra"
        p1.mass = 5.97e24
        p1.surface_gravity = 9.81
        p1.surface_temperature = 288
        
        p2 = MagicMock(spec=Planet)
        p2.planet_type = PlanetType.ICE_GIANT
        p2.name = "Neptune"
        p2.mass = 1.02e26
        p2.surface_gravity = 11.15
        p2.surface_temperature = 72
        
        # Mock system structure
        system = MagicMock()
        system.planets = [p1, p2]
        galaxy.iter_systems.side_effect = lambda d={'Sys1': system}: iter(d.values())  # PROJ-477: world seam
        
        planets = gather_planets(galaxy, empire)
        
        assert len(planets) == 2
        # Verify cached categories match "Title Case" of Enum
        assert p1._cached_type_category == "Continental"
        assert p2._cached_type_category == "Ice Giant"

    def test_filter_planets_by_type(self):
        """Verify filter_planets respects new type filters."""
        # Create planets with cached values (simulating gather_planets result)
        p1 = MagicMock()
        p1._cached_type_category = "Continental"
        p1._cached_name_lower = "terra"
        p1._cached_gravity_g = 1.0
        p1.surface_temperature = 288
        p1._cached_mass_earth = 1.0
        p1.owner_id = 1
        
        p2 = MagicMock()
        p2._cached_type_category = "Ice Giant"
        p2._cached_name_lower = "neptune"
        p2._cached_gravity_g = 1.1
        p2.surface_temperature = 72
        p2._cached_mass_earth = 17.0
        p2.owner_id = 1
        
        all_planets = [p1, p2]
        
        # Test 1: Both enabled
        filter_types = {'Continental': True, 'Ice Giant': True}
        res = filter_planets(all_planets, "", filter_types, 0, 100, 0, 1000, 0, 1000, {'Player': True}, MagicMock(id=1))
        assert len(res) == 2
        
        # Test 2: Disable Ice Giant
        filter_types['Ice Giant'] = False
        res = filter_planets(all_planets, "", filter_types, 0, 100, 0, 1000, 0, 1000, {'Player': True}, MagicMock(id=1))
        assert len(res) == 1
        assert res[0] == p1
        
        # Test 3: Disable All
        filter_types['Continental'] = False
        res = filter_planets(all_planets, "", filter_types, 0, 100, 0, 1000, 0, 1000, {'Player': True}, MagicMock(id=1))
        assert len(res) == 0


class TestGatherPlanetsCachesSystemLocation:
    """gather_planets should cache system global_location for navigation."""

    def test_caches_system_global_location(self):
        """Each planet should get _cached_system_global_location from its system."""
        galaxy = MagicMock()
        empire = MagicMock()

        p1 = MagicMock(spec=Planet)
        p1.planet_type = PlanetType.CONTINENTAL
        p1.name = "Terra"
        p1.mass = 5.97e24
        p1.surface_gravity = 9.81

        system = MagicMock()
        system.name = "Solar"
        system.global_location = HexCoord(10, 20)
        system.planets = [p1]
        galaxy.iter_systems.side_effect = lambda d={'Solar': system}: iter(d.values())  # PROJ-477: world seam

        planets = gather_planets(galaxy, empire)
        assert len(planets) == 1
        assert p1._cached_system_global_location == HexCoord(10, 20)

    def test_different_systems_cache_different_locations(self):
        """Planets from different systems should get their own system location."""
        galaxy = MagicMock()
        empire = MagicMock()

        p1 = MagicMock(spec=Planet)
        p1.planet_type = PlanetType.ARID
        p1.name = "Dry"
        p1.mass = 3e24
        p1.surface_gravity = 5.0

        p2 = MagicMock(spec=Planet)
        p2.planet_type = PlanetType.PELAGIC
        p2.name = "Wet"
        p2.mass = 6e24
        p2.surface_gravity = 10.0

        sys1 = MagicMock()
        sys1.name = "Alpha"
        sys1.global_location = HexCoord(5, 5)
        sys1.planets = [p1]

        sys2 = MagicMock()
        sys2.name = "Beta"
        sys2.global_location = HexCoord(50, 50)
        sys2.planets = [p2]

        galaxy.iter_systems.side_effect = lambda d={'Alpha': sys1, 'Beta': sys2}: iter(d.values())  # PROJ-477: world seam

        planets = gather_planets(galaxy, empire)
        assert p1._cached_system_global_location == HexCoord(5, 5)
        assert p2._cached_system_global_location == HexCoord(50, 50)


# ---------------------------------------------------------------------------
# FEAT-16: Planet effects filter & column support.
#
# `compute_planet_effect_keys(all_planets)` returns the sorted, de-duplicated
# list of group-keys (e.g. "EnvironmentalDamage:thermal", "ThrustModifier")
# present across the galaxy. Used to populate Effects filter chips and
# per-effect columns dynamically.
#
# `effects_predicate(filter_effects)` is the predicate used by `filter_planets`.
# Per FEAT-16: OR within Effects, and the **special case** that an empty /
# all-False `filter_effects` selection is a no-op (every planet passes — the
# opposite of how Type/Owner behave). Documented in `planet_list_filters.py`.
# ---------------------------------------------------------------------------


class TestComputePlanetEffectKeys:
    """`compute_planet_effect_keys(all_planets)` returns sorted unique
    group-keys across all planets' `intrinsic_abilities`."""

    def test_empty_galaxy_returns_empty_list(self):
        from game.ui.screens.planet_list_filters import compute_planet_effect_keys
        assert compute_planet_effect_keys([]) == []

    def test_planets_with_no_effects_return_empty_list(self):
        from game.ui.screens.planet_list_filters import compute_planet_effect_keys
        p1 = MagicMock()
        p1.intrinsic_abilities = {}
        p2 = MagicMock()
        p2.intrinsic_abilities = {}
        assert compute_planet_effect_keys([p1, p2]) == []

    def test_includes_damage_type_in_environmental_damage_key(self):
        from game.ui.screens.planet_list_filters import compute_planet_effect_keys
        p_thermal = MagicMock()
        p_thermal.intrinsic_abilities = {
            'EnvironmentalDamage': {'rate': 0.3, 'damage_type': 'thermal', 'scope': 'sector'},
        }
        p_radiation = MagicMock()
        p_radiation.intrinsic_abilities = {
            'EnvironmentalDamage': {'rate': 0.1, 'damage_type': 'radiation', 'scope': 'sector'},
        }
        keys = compute_planet_effect_keys([p_thermal, p_radiation])
        assert 'EnvironmentalDamage:thermal' in keys
        assert 'EnvironmentalDamage:radiation' in keys

    def test_dedupes_across_planets(self):
        from game.ui.screens.planet_list_filters import compute_planet_effect_keys
        p1 = MagicMock()
        p1.intrinsic_abilities = {'ThrustModifier': {'multiplier': 0.9, 'scope': 'sector'}}
        p2 = MagicMock()
        p2.intrinsic_abilities = {'ThrustModifier': {'multiplier': 0.85, 'scope': 'sector'}}
        keys = compute_planet_effect_keys([p1, p2])
        assert keys == ['ThrustModifier']

    def test_sorted_stable(self):
        from game.ui.screens.planet_list_filters import compute_planet_effect_keys
        p_a = MagicMock()
        p_a.intrinsic_abilities = {
            'ThrustModifier': {'multiplier': 0.9, 'scope': 'sector'},
            'ShieldModifier': {'multiplier': 0.85, 'scope': 'sector'},
        }
        p_b = MagicMock()
        p_b.intrinsic_abilities = {
            'EnvironmentalDamage': {'rate': 0.3, 'damage_type': 'thermal', 'scope': 'sector'},
            'FuelDrain': {'rate': 0.5, 'scope': 'sector'},
        }
        keys = compute_planet_effect_keys([p_a, p_b])
        assert keys == sorted(keys)
        assert keys == [
            'EnvironmentalDamage:thermal',
            'FuelDrain',
            'ShieldModifier',
            'ThrustModifier',
        ]


class TestEffectsPredicate:
    """`effects_predicate(filter_effects)` returns a predicate. Per FEAT-25:

    - Per-effect tri-state (FilterState.YES / NO / IGNORE).
    - Multiple non-IGNORE effects compose as **AND**.
    - All-IGNORE (or empty) → no-op (every planet passes). The only no-op state.
    - YES requires presence; NO requires absence.
    """

    def _planet_with(self, abilities):
        p = MagicMock()
        p.intrinsic_abilities = abilities
        return p

    def test_no_selections_is_noop_show_all(self):
        """Empty filter dict = no-op."""
        from game.ui.screens.planet_list_filters import effects_predicate
        pred = effects_predicate({})
        assert pred(self._planet_with({})) is True
        assert pred(self._planet_with({'ThrustModifier': {'multiplier': 0.9}})) is True

    def test_all_ignore_is_noop_show_all(self):
        """All-IGNORE dict is functionally equivalent to empty."""
        from game.ui.screens.planet_list_filters import effects_predicate
        from game.ui.filters.filter_state import FilterState
        pred = effects_predicate({
            'ThrustModifier': FilterState.IGNORE,
            'FuelDrain': FilterState.IGNORE,
        })
        assert pred(self._planet_with({})) is True
        assert pred(self._planet_with({'ThrustModifier': {'multiplier': 0.9}})) is True

    def test_yes_requires_presence(self):
        """YES: planet must have the effect; planets without it are rejected."""
        from game.ui.screens.planet_list_filters import effects_predicate
        from game.ui.filters.filter_state import FilterState
        pred = effects_predicate({'ThrustModifier': FilterState.YES})
        with_thrust = self._planet_with({'ThrustModifier': {'multiplier': 0.9, 'scope': 'sector'}})
        without_thrust = self._planet_with({})
        with_other = self._planet_with({'ShieldModifier': {'multiplier': 0.85}})
        assert pred(with_thrust) is True
        assert pred(without_thrust) is False
        assert pred(with_other) is False

    def test_no_requires_absence(self):
        """NO: planet must NOT have the effect; planets with it are rejected."""
        from game.ui.screens.planet_list_filters import effects_predicate
        from game.ui.filters.filter_state import FilterState
        pred = effects_predicate({'ThrustModifier': FilterState.NO})
        with_thrust = self._planet_with({'ThrustModifier': {'multiplier': 0.9, 'scope': 'sector'}})
        without_thrust = self._planet_with({})
        assert pred(with_thrust) is False
        assert pred(without_thrust) is True

    def test_yes_and_no_compose_as_and(self):
        """{Thermal: NO, Shield: YES} → both conditions must hold simultaneously."""
        from game.ui.screens.planet_list_filters import effects_predicate
        from game.ui.filters.filter_state import FilterState
        pred = effects_predicate({
            'EnvironmentalDamage:thermal': FilterState.NO,
            'ShieldModifier': FilterState.YES,
        })
        only_shield = self._planet_with({'ShieldModifier': {'multiplier': 0.85}})
        only_thermal = self._planet_with({
            'EnvironmentalDamage': {'rate': 0.3, 'damage_type': 'thermal', 'scope': 'sector'},
        })
        both = self._planet_with({
            'ShieldModifier': {'multiplier': 0.85},
            'EnvironmentalDamage': {'rate': 0.3, 'damage_type': 'thermal', 'scope': 'sector'},
        })
        neither = self._planet_with({})
        assert pred(only_shield) is True   # NO satisfied (no thermal), YES satisfied (has shield)
        assert pred(only_thermal) is False  # NO violated (has thermal)
        assert pred(both) is False          # NO violated
        assert pred(neither) is False       # YES violated (no shield)

    def test_ignore_mixed_with_others_skipped(self):
        """{A: YES, B: IGNORE} behaves identically to {A: YES} alone."""
        from game.ui.screens.planet_list_filters import effects_predicate
        from game.ui.filters.filter_state import FilterState
        pred_mixed = effects_predicate({
            'ThrustModifier': FilterState.YES,
            'FuelDrain': FilterState.IGNORE,
        })
        pred_alone = effects_predicate({'ThrustModifier': FilterState.YES})
        with_thrust_only = self._planet_with({'ThrustModifier': {'multiplier': 0.9}})
        with_fuel_only = self._planet_with({'FuelDrain': {'rate': 0.5}})
        assert pred_mixed(with_thrust_only) is pred_alone(with_thrust_only) is True
        assert pred_mixed(with_fuel_only) is pred_alone(with_fuel_only) is False

    def test_environmental_damage_yes_distinguishes_subtype(self):
        """YES on EnvironmentalDamage:thermal must not match a radiation planet."""
        from game.ui.screens.planet_list_filters import effects_predicate
        from game.ui.filters.filter_state import FilterState
        pred = effects_predicate({'EnvironmentalDamage:thermal': FilterState.YES})
        thermal_planet = self._planet_with({
            'EnvironmentalDamage': {'rate': 0.3, 'damage_type': 'thermal', 'scope': 'sector'},
        })
        radiation_planet = self._planet_with({
            'EnvironmentalDamage': {'rate': 0.1, 'damage_type': 'radiation', 'scope': 'sector'},
        })
        assert pred(thermal_planet) is True
        assert pred(radiation_planet) is False

    def test_environmental_damage_no_excludes_thermal_planet(self):
        """NO on EnvironmentalDamage:thermal must reject thermal planets."""
        from game.ui.screens.planet_list_filters import effects_predicate
        from game.ui.filters.filter_state import FilterState
        pred = effects_predicate({'EnvironmentalDamage:thermal': FilterState.NO})
        thermal_planet = self._planet_with({
            'EnvironmentalDamage': {'rate': 0.3, 'damage_type': 'thermal', 'scope': 'sector'},
        })
        radiation_planet = self._planet_with({
            'EnvironmentalDamage': {'rate': 0.1, 'damage_type': 'radiation', 'scope': 'sector'},
        })
        assert pred(thermal_planet) is False
        assert pred(radiation_planet) is True


class TestFilterPlanetsWithEffects:
    """Effects compose with other categories as AND when integrated through
    `filter_planets`."""

    def _planet(self, *, name="Terra", type_cat="Continental",
                grav_g=1.0, temp=288, mass_e=1.0, owner_id=1,
                abilities=None):
        p = MagicMock()
        p._cached_name_lower = name.lower()
        p._cached_type_category = type_cat
        p._cached_gravity_g = grav_g
        p.surface_temperature = temp
        p._cached_mass_earth = mass_e
        p.owner_id = owner_id
        p.intrinsic_abilities = abilities or {}
        return p

    def test_effects_and_type_compose_as_and(self):
        from game.ui.screens.planet_list_filters import filter_planets
        from game.ui.filters.filter_state import FilterState
        magma_thermal = self._planet(
            name="Inferno", type_cat="Magma",
            abilities={'EnvironmentalDamage': {'rate': 0.3, 'damage_type': 'thermal'}},
        )
        cryo_thrust = self._planet(
            name="Frigis", type_cat="Cryoplanet",
            abilities={'ThrustModifier': {'multiplier': 0.9}},
        )
        continental = self._planet(name="Terra", type_cat="Continental")
        all_planets = [magma_thermal, cryo_thrust, continental]

        # type=Magma only AND effects=ThrustModifier=YES → empty (Magma has thermal damage, not thrust)
        out = filter_planets(
            all_planets, "",
            {'Magma': True, 'Cryoplanet': False, 'Continental': False},
            0, 100, 0, 1000, 0, 1000,
            filter_owner={'Player': True, 'Enemy': True, 'Unowned': True},
            empire=MagicMock(id=1),
            filter_effects={'ThrustModifier': FilterState.YES},
        )
        assert out == []

        # type=Cryoplanet AND effects=ThrustModifier=YES → cryo_thrust passes
        out = filter_planets(
            all_planets, "",
            {'Magma': False, 'Cryoplanet': True, 'Continental': False},
            0, 100, 0, 1000, 0, 1000,
            filter_owner={'Player': True, 'Enemy': True, 'Unowned': True},
            empire=MagicMock(id=1),
            filter_effects={'ThrustModifier': FilterState.YES},
        )
        assert out == [cryo_thrust]


class TestPlanetColumnValues:
    def test_worker_i_planet_dot_walk_column(self):
        from game.ui.screens.planet_list_filters import get_column_value

        planet = SimpleNamespace(
            star_system=SimpleNamespace(
                primary=SimpleNamespace(name="Aster"),
                orbit=SimpleNamespace(distance=12.345),
            )
        )

        assert get_column_value(planet, {"attr": "star_system.primary.name"}) == "Aster"
        assert get_column_value(
            planet,
            {"attr": "star_system.orbit.distance", "fmt": "{:.1f} AU"},
        ) == "12.3 AU"
        assert get_column_value(planet, {"attr": "star_system.missing.name"}) == "?"


class TestPlanetRangeDefaults:
    def test_worker_i_planet_empty_range_defaults(self):
        from game.ui.screens.planet_list_filters import compute_planet_ranges

        assert compute_planet_ranges([]) == {
            "gravity": (0.0, 10.0),
            "temp": (0, 2000),
            "mass": (0.0, 500.0),
        }
