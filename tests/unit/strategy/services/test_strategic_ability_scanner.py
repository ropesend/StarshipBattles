"""Tests for strategic_ability_scanner — scoped ability queries and aggregation."""
import pytest
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from unittest.mock import MagicMock

from game.strategy.services.strategic_ability_scanner import (
    find_abilities_at_planet,
    find_abilities_in_scope,
    aggregate_multipliers,
    aggregate_rates,
)


# --- Minimal test doubles ---

@dataclass
class MockFacility:
    design_data: Dict[str, Any]
    is_operational: bool = True
    instance_id: str = "fac-1"
    component_states: Dict[str, Any] = field(default_factory=dict)

    def is_component_active(self, comp_id):
        return self.component_states.get(comp_id, True)

    def get_activation_state(self, component_key: str):
        """Return ComponentActivationState for a component (mirrors PlanetaryFacility)."""
        from game.strategy.data.component_activation_state import ComponentActivationState
        data = self.component_states.get(component_key)
        if data is None:
            return ComponentActivationState()
        if isinstance(data, dict):
            return ComponentActivationState.from_dict(data)
        return ComponentActivationState()


@dataclass
class MockPlanet:
    name: str = "Alpha"
    id: int = 1
    owner_id: int = 0
    location: Any = None
    facilities: List = field(default_factory=list)


@dataclass
class MockSystem:
    planets: List = field(default_factory=list)
    global_location: Any = None


@dataclass
class MockEmpire:
    id: int = 0
    colonies: List = field(default_factory=list)


def _make_facility_with_ability(ability_key, ability_data, comp_id="comp1"):
    """Helper to create a facility with one component having a specific ability."""
    return MockFacility(
        design_data={
            "layers": {
                "CORE": [
                    {"id": comp_id, "abilities": {ability_key: ability_data}}
                ]
            }
        }
    )


def _make_facility_with_activation(
    ability_key, ability_data, phase, comp_id="comp1", layer="CORE", index=0
):
    """Helper to create a facility with a component at a specific activation phase.

    Sets up both the design_data (so the ability is discoverable) and the
    component_states (so the activation state can be checked).
    """
    comp_key = f"{layer}:{index}:{comp_id}"
    state_data = {"phase": phase, "ability_name": ability_key}
    return MockFacility(
        design_data={
            "layers": {
                layer: [
                    {"id": comp_id, "abilities": {ability_key: ability_data}}
                ]
            }
        },
        component_states={comp_key: state_data},
    )


class TestFindAbilitiesAtPlanet:
    """Test finding abilities on a single planet's facilities."""

    def test_finds_ability_on_planet(self):
        """Should find an ability on the planet's operational facility."""
        planet = MockPlanet()
        planet.facilities = [
            _make_facility_with_ability(
                "ResourceHarvestBooster",
                {"resource_type": "metals", "multiplier": 1.5, "scope": "planet"}
            )
        ]

        results = find_abilities_at_planet("ResourceHarvestBooster", planet)
        assert len(results) == 1
        assert results[0]["multiplier"] == 1.5
        assert results[0]["resource_type"] == "metals"

    def test_skips_non_operational_facility(self):
        """Should skip non-operational facilities."""
        fac = _make_facility_with_ability(
            "ResourceHarvestBooster",
            {"resource_type": "metals", "multiplier": 1.5}
        )
        fac.is_operational = False

        planet = MockPlanet(facilities=[fac])
        results = find_abilities_at_planet("ResourceHarvestBooster", planet)
        assert len(results) == 0

    def test_returns_empty_for_no_matching_ability(self):
        """Should return empty list when no matching ability exists."""
        planet = MockPlanet()
        planet.facilities = [
            _make_facility_with_ability("SomeOtherAbility", {"value": 1.0})
        ]

        results = find_abilities_at_planet("ResourceHarvestBooster", planet)
        assert len(results) == 0

    def test_finds_multiple_abilities_across_facilities(self):
        """Should aggregate abilities from multiple facilities."""
        planet = MockPlanet()
        planet.facilities = [
            _make_facility_with_ability(
                "ResourceHarvestBooster",
                {"resource_type": "metals", "multiplier": 1.5, "stack_group": "a"}
            ),
            _make_facility_with_ability(
                "ResourceHarvestBooster",
                {"resource_type": "metals", "multiplier": 1.3, "stack_group": "b"},
                comp_id="comp2"
            ),
        ]

        results = find_abilities_at_planet("ResourceHarvestBooster", planet)
        assert len(results) == 2


class TestFindAbilitiesInScope:
    """Test scoped ability discovery."""

    def _make_galaxy_mock(self, planets_at_hex=None, system_planets=None):
        from game.core.hex_math import HexCoord
        galaxy = MagicMock()

        # Sector scope: get_planet_global_hex -> get_planets_at_global_hex
        galaxy.get_planet_global_hex.return_value = HexCoord(5, 5)
        if planets_at_hex is not None:
            galaxy.get_planets_at_global_hex.return_value = planets_at_hex
        else:
            galaxy.get_planets_at_global_hex.return_value = []

        # System scope: get_system_of_planet -> system.planets
        if system_planets is not None:
            mock_system = MagicMock()
            mock_system.planets = system_planets
            galaxy.get_system_of_planet.return_value = mock_system
        else:
            galaxy.get_system_of_planet.return_value = None

        return galaxy

    def test_planet_scope_finds_on_target_only(self):
        """PLANET scope should only scan the target planet."""
        target = MockPlanet(name="Target", owner_id=0)
        target.facilities = [
            _make_facility_with_ability("TestAbility", {"multiplier": 2.0})
        ]

        other = MockPlanet(name="Other", owner_id=0)
        other.facilities = [
            _make_facility_with_ability("TestAbility", {"multiplier": 3.0})
        ]

        galaxy = self._make_galaxy_mock(planets_at_hex=[target, other])
        empire = MockEmpire(id=0, colonies=[target, other])

        results = find_abilities_in_scope("TestAbility", target, galaxy, empire, "planet")
        assert len(results) == 1
        assert results[0]["multiplier"] == 2.0

    def test_sector_scope_finds_on_colocated_planets(self):
        """SECTOR scope should find abilities on all owned planets in the hex."""
        from game.core.hex_math import HexCoord
        target = MockPlanet(name="Target", owner_id=0, location=HexCoord(5, 5))
        other = MockPlanet(name="Other", owner_id=0, location=HexCoord(5, 5))
        other.facilities = [
            _make_facility_with_ability("TestAbility", {"multiplier": 1.5})
        ]

        galaxy = self._make_galaxy_mock(planets_at_hex=[target, other])
        empire = MockEmpire(id=0, colonies=[target, other])

        results = find_abilities_in_scope("TestAbility", target, galaxy, empire, "sector")
        assert len(results) == 1
        assert results[0]["multiplier"] == 1.5

    def test_system_scope_finds_across_system(self):
        """SYSTEM scope should find abilities on all owned planets in the system."""
        from game.core.hex_math import HexCoord
        target = MockPlanet(name="Target", owner_id=0, location=HexCoord(5, 5))
        other = MockPlanet(name="Other", owner_id=0, location=HexCoord(5, 6))
        other.facilities = [
            _make_facility_with_ability("TestAbility", {"multiplier": 1.3})
        ]

        galaxy = self._make_galaxy_mock(system_planets=[target, other])
        empire = MockEmpire(id=0, colonies=[target, other])

        results = find_abilities_in_scope("TestAbility", target, galaxy, empire, "system")
        assert len(results) == 1
        assert results[0]["multiplier"] == 1.3

    def test_empire_scope_finds_across_all_colonies(self):
        """EMPIRE scope should scan all of the empire's colonies."""
        target = MockPlanet(name="Target", owner_id=0)
        far_colony = MockPlanet(name="Far", owner_id=0)
        far_colony.facilities = [
            _make_facility_with_ability("TestAbility", {"multiplier": 1.1})
        ]

        galaxy = self._make_galaxy_mock()
        empire = MockEmpire(id=0, colonies=[target, far_colony])

        results = find_abilities_in_scope("TestAbility", target, galaxy, empire, "empire")
        assert len(results) == 1
        assert results[0]["multiplier"] == 1.1

    def test_ignores_unowned_planets_in_sector(self):
        """SECTOR scope should only include planets owned by the empire."""
        from game.core.hex_math import HexCoord
        target = MockPlanet(name="Target", owner_id=0, location=HexCoord(5, 5))
        enemy = MockPlanet(name="Enemy", owner_id=1, location=HexCoord(5, 5))
        enemy.facilities = [
            _make_facility_with_ability("TestAbility", {"multiplier": 9.9})
        ]

        galaxy = self._make_galaxy_mock(planets_at_hex=[target, enemy])
        empire = MockEmpire(id=0, colonies=[target])

        results = find_abilities_in_scope("TestAbility", target, galaxy, empire, "sector")
        assert len(results) == 0


class TestPlayerAndEnemyScopeResolution:
    """Test PLAYER_* and ENEMY_* scope resolution in find_abilities_in_scope."""

    def _make_galaxy_mock(self, planets_at_hex=None, system_planets=None):
        from game.core.hex_math import HexCoord
        galaxy = MagicMock()

        # Sector scope: get_planet_global_hex -> get_planets_at_global_hex
        galaxy.get_planet_global_hex.return_value = HexCoord(5, 5)
        if planets_at_hex is not None:
            galaxy.get_planets_at_global_hex.return_value = planets_at_hex
        else:
            galaxy.get_planets_at_global_hex.return_value = []

        # System scope: get_system_of_planet -> system.planets
        if system_planets is not None:
            mock_system = MagicMock()
            mock_system.planets = system_planets
            galaxy.get_system_of_planet.return_value = mock_system
        else:
            galaxy.get_system_of_planet.return_value = None

        return galaxy

    def test_player_sector_returns_only_owned_planets(self):
        """PLAYER_SECTOR scope should return only owned planets at the hex."""
        from game.core.hex_math import HexCoord
        target = MockPlanet(name="Mine", owner_id=0, location=HexCoord(5, 5))
        target.facilities = [
            _make_facility_with_ability("TestAbility", {"multiplier": 1.5})
        ]
        enemy = MockPlanet(name="Enemy", owner_id=1, location=HexCoord(5, 5))
        enemy.facilities = [
            _make_facility_with_ability("TestAbility", {"multiplier": 9.9})
        ]

        galaxy = self._make_galaxy_mock(planets_at_hex=[target, enemy])
        empire = MockEmpire(id=0, colonies=[target])

        results = find_abilities_in_scope("TestAbility", target, galaxy, empire, "player_sector")
        assert len(results) == 1
        assert results[0]["multiplier"] == 1.5

    def test_player_system_returns_only_owned_planets(self):
        """PLAYER_SYSTEM scope should return only owned planets in the system."""
        from game.core.hex_math import HexCoord
        target = MockPlanet(name="Mine", owner_id=0, location=HexCoord(5, 5))
        target.facilities = [
            _make_facility_with_ability("TestAbility", {"multiplier": 1.5})
        ]
        allied = MockPlanet(name="Ally", owner_id=2, location=HexCoord(5, 6))
        allied.facilities = [
            _make_facility_with_ability("TestAbility", {"multiplier": 2.0})
        ]
        enemy = MockPlanet(name="Enemy", owner_id=1, location=HexCoord(5, 7))
        enemy.facilities = [
            _make_facility_with_ability("TestAbility", {"multiplier": 9.9})
        ]

        galaxy = self._make_galaxy_mock(system_planets=[target, allied, enemy])
        empire = MockEmpire(id=0, colonies=[target])

        results = find_abilities_in_scope("TestAbility", target, galaxy, empire, "player_system")
        assert len(results) == 1
        assert results[0]["multiplier"] == 1.5

    def test_enemy_sector_returns_only_non_owned_planets(self):
        """ENEMY_SECTOR scope should return only non-owned planets at the hex."""
        from game.core.hex_math import HexCoord
        target = MockPlanet(name="Mine", owner_id=0, location=HexCoord(5, 5))
        target.facilities = [
            _make_facility_with_ability("TestAbility", {"multiplier": 1.0})
        ]
        enemy = MockPlanet(name="Enemy", owner_id=1, location=HexCoord(5, 5))
        enemy.facilities = [
            _make_facility_with_ability("TestAbility", {"multiplier": 3.0})
        ]

        galaxy = self._make_galaxy_mock(planets_at_hex=[target, enemy])
        empire = MockEmpire(id=0, colonies=[target])

        results = find_abilities_in_scope("TestAbility", target, galaxy, empire, "enemy_sector")
        assert len(results) == 1
        assert results[0]["multiplier"] == 3.0

    def test_enemy_system_returns_only_non_owned_planets(self):
        """ENEMY_SYSTEM scope should return only non-owned planets in the system."""
        from game.core.hex_math import HexCoord
        target = MockPlanet(name="Mine", owner_id=0, location=HexCoord(5, 5))
        target.facilities = [
            _make_facility_with_ability("TestAbility", {"multiplier": 1.0})
        ]
        enemy1 = MockPlanet(name="Enemy1", owner_id=1, location=HexCoord(5, 6))
        enemy1.facilities = [
            _make_facility_with_ability("TestAbility", {"multiplier": 2.0})
        ]
        enemy2 = MockPlanet(name="Enemy2", owner_id=2, location=HexCoord(5, 7))
        enemy2.facilities = [
            _make_facility_with_ability("TestAbility", {"multiplier": 4.0})
        ]

        galaxy = self._make_galaxy_mock(system_planets=[target, enemy1, enemy2])
        empire = MockEmpire(id=0, colonies=[target])

        results = find_abilities_in_scope("TestAbility", target, galaxy, empire, "enemy_system")
        assert len(results) == 2
        multipliers = sorted([r["multiplier"] for r in results])
        assert multipliers == [2.0, 4.0]

    def test_enemy_sector_excludes_owned_planets(self):
        """ENEMY_SECTOR scope should not include the owner's own planets."""
        from game.core.hex_math import HexCoord
        owned = MockPlanet(name="Mine", owner_id=0, location=HexCoord(5, 5))
        owned.facilities = [
            _make_facility_with_ability("TestAbility", {"multiplier": 1.0})
        ]

        galaxy = self._make_galaxy_mock(planets_at_hex=[owned])
        empire = MockEmpire(id=0, colonies=[owned])

        results = find_abilities_in_scope("TestAbility", owned, galaxy, empire, "enemy_sector")
        assert len(results) == 0


class TestActivationStateFiltering:
    """Test that require_active filters by ComponentActivationState."""

    def test_require_active_finds_active_component(self):
        """require_active=True should include abilities on ACTIVE components."""
        planet = MockPlanet()
        planet.facilities = [
            _make_facility_with_activation(
                "GeologicStabilizer",
                {"energy_drain_rate": 50.0},
                phase="active",
            )
        ]

        results = find_abilities_at_planet(
            "GeologicStabilizer", planet, require_active=True
        )
        assert len(results) == 1
        assert results[0]["energy_drain_rate"] == 50.0

    def test_require_active_skips_inactive_component(self):
        """require_active=True should exclude abilities on INACTIVE components."""
        planet = MockPlanet()
        planet.facilities = [
            _make_facility_with_activation(
                "GeologicStabilizer",
                {"energy_drain_rate": 50.0},
                phase="inactive",
            )
        ]

        results = find_abilities_at_planet(
            "GeologicStabilizer", planet, require_active=True
        )
        assert len(results) == 0

    def test_require_active_skips_activating_component(self):
        """require_active=True should exclude ACTIVATING (not yet ready)."""
        planet = MockPlanet()
        planet.facilities = [
            _make_facility_with_activation(
                "GeologicStabilizer",
                {"energy_drain_rate": 50.0},
                phase="activating",
            )
        ]

        results = find_abilities_at_planet(
            "GeologicStabilizer", planet, require_active=True
        )
        assert len(results) == 0

    def test_require_active_skips_deactivating_component(self):
        """require_active=True should exclude DEACTIVATING (shutting down)."""
        planet = MockPlanet()
        planet.facilities = [
            _make_facility_with_activation(
                "GeologicStabilizer",
                {"energy_drain_rate": 50.0},
                phase="deactivating",
            )
        ]

        results = find_abilities_at_planet(
            "GeologicStabilizer", planet, require_active=True
        )
        assert len(results) == 0

    def test_default_require_active_false_includes_all(self):
        """Default require_active=False should return abilities regardless of phase."""
        planet = MockPlanet()
        planet.facilities = [
            _make_facility_with_activation(
                "GeologicStabilizer",
                {"energy_drain_rate": 50.0},
                phase="inactive",
            )
        ]

        # Default (no require_active) — should still find it
        results = find_abilities_at_planet("GeologicStabilizer", planet)
        assert len(results) == 1

    def test_require_active_with_mixed_components(self):
        """Only ACTIVE components returned when require_active=True with mixed states."""
        active_fac = _make_facility_with_activation(
            "GeologicStabilizer",
            {"energy_drain_rate": 50.0, "scope": "system"},
            phase="active",
            comp_id="geo_stab_1",
        )
        inactive_fac = _make_facility_with_activation(
            "GeologicStabilizer",
            {"energy_drain_rate": 25.0, "scope": "sector"},
            phase="inactive",
            comp_id="geo_stab_2",
        )

        planet = MockPlanet()
        planet.facilities = [active_fac, inactive_fac]

        results = find_abilities_at_planet(
            "GeologicStabilizer", planet, require_active=True
        )
        assert len(results) == 1
        assert results[0]["energy_drain_rate"] == 50.0


class TestScopeResolutionCoordinateCorrectness:
    """Test that scope resolution uses correct coordinate types.

    _resolve_planets_for_scope must use global hex coordinates (not local
    planet.location) when calling Galaxy spatial methods.
    """

    def test_system_scope_uses_get_system_of_planet(self):
        """System scope must use get_system_of_planet, not get_system_at_location.

        Planet.location is local (relative to system center). Passing it to
        get_system_at_location (which expects global coords) returns None for
        most planets, silently breaking system-scope lookups.
        """
        from game.core.hex_math import HexCoord

        # Planet at local coord (2,3) — NOT a system center
        target = MockPlanet(name="Target", owner_id=0, location=HexCoord(2, 3))
        sibling = MockPlanet(name="Sibling", owner_id=0, location=HexCoord(1, 0))
        sibling.facilities = [
            _make_facility_with_ability("GeologicStabilizer", {"energy_drain_rate": 50.0})
        ]

        mock_system = MagicMock()
        mock_system.planets = [target, sibling]

        galaxy = MagicMock()
        # get_system_at_location with local coord returns None (realistic)
        galaxy.get_system_at_location.return_value = None
        # get_system_of_planet returns the correct system
        galaxy.get_system_of_planet.return_value = mock_system

        empire = MockEmpire(id=0)

        results = find_abilities_in_scope(
            "GeologicStabilizer", target, galaxy, empire, "system"
        )
        assert len(results) == 1
        assert results[0]["energy_drain_rate"] == 50.0

    def test_sector_scope_uses_global_hex_not_local(self):
        """Sector scope must convert planet.location to global hex before lookup.

        Planet.location is local. get_planets_at_global_hex expects global
        coordinates. The scanner must call get_planet_global_hex first.
        """
        from game.core.hex_math import HexCoord

        local_coord = HexCoord(2, 3)
        global_coord = HexCoord(52, 33)  # system at (50,30) + local (2,3)

        target = MockPlanet(name="Target", owner_id=0, location=local_coord)
        colocated = MockPlanet(name="Colocated", owner_id=0, location=local_coord)
        colocated.facilities = [
            _make_facility_with_ability("TestAbility", {"multiplier": 1.5})
        ]

        galaxy = MagicMock()
        galaxy.get_planet_global_hex.return_value = global_coord
        # Local coord lookup returns empty (realistic — no planets at global (2,3))
        galaxy.get_planets_at_global_hex.side_effect = (
            lambda hex_c: [target, colocated] if hex_c == global_coord else []
        )

        empire = MockEmpire(id=0)

        results = find_abilities_in_scope(
            "TestAbility", target, galaxy, empire, "sector"
        )
        assert len(results) == 1
        assert results[0]["multiplier"] == 1.5

    def test_system_scope_finds_stabilizer_on_sibling_planet(self):
        """A system-scope stabilizer on Planet A must protect Planet B in same system."""
        from game.core.hex_math import HexCoord

        planet_a = MockPlanet(name="A", owner_id=0, location=HexCoord(1, 0))
        planet_a.facilities = [
            _make_facility_with_ability(
                "GeologicStabilizer",
                {"energy_drain_rate": 50.0, "scope": "system"}
            )
        ]
        planet_b = MockPlanet(name="B", owner_id=0, location=HexCoord(0, 2))

        mock_system = MagicMock()
        mock_system.planets = [planet_a, planet_b]

        galaxy = MagicMock()
        galaxy.get_system_of_planet.return_value = mock_system
        # Simulate the real failure: local coord lookup misses
        galaxy.get_system_at_location.return_value = None

        empire = MockEmpire(id=0)

        # Scan from planet B — should find stabilizer on planet A
        results = find_abilities_in_scope(
            "GeologicStabilizer", planet_b, galaxy, empire, "system"
        )
        assert len(results) == 1, (
            "System-scope stabilizer on sibling planet must be found"
        )

    def test_sector_scope_finds_ability_at_correct_global_hex(self):
        """Sector scope must find abilities on co-located planet via global hex."""
        from game.core.hex_math import HexCoord

        global_hex = HexCoord(50, 30)

        planet_a = MockPlanet(name="A", owner_id=0, location=HexCoord(0, 0))
        planet_a.facilities = [
            _make_facility_with_ability("TestAbility", {"multiplier": 2.0})
        ]
        planet_b = MockPlanet(name="B", owner_id=0, location=HexCoord(0, 0))

        galaxy = MagicMock()
        galaxy.get_planet_global_hex.return_value = global_hex
        galaxy.get_planets_at_global_hex.side_effect = (
            lambda hex_c: [planet_a, planet_b] if hex_c == global_hex else []
        )

        empire = MockEmpire(id=0)

        results = find_abilities_in_scope(
            "TestAbility", planet_b, galaxy, empire, "sector"
        )
        assert len(results) == 1
        assert results[0]["multiplier"] == 2.0


class TestAggregateMultipliers:
    """Test two-phase stacking: intra-group MAX, inter-group MULTIPLY."""

    def test_single_entry(self):
        """Single entry returns its multiplier."""
        entries = [{"multiplier": 1.5, "stack_group": "a"}]
        assert aggregate_multipliers(entries) == pytest.approx(1.5)

    def test_same_group_takes_max(self):
        """Same stack_group: MAX, not multiply."""
        entries = [
            {"multiplier": 1.5, "stack_group": "a"},
            {"multiplier": 1.3, "stack_group": "a"},
        ]
        assert aggregate_multipliers(entries) == pytest.approx(1.5)

    def test_different_groups_multiply(self):
        """Different stack_groups: MULTIPLY."""
        entries = [
            {"multiplier": 1.5, "stack_group": "a"},
            {"multiplier": 1.3, "stack_group": "b"},
        ]
        assert aggregate_multipliers(entries) == pytest.approx(1.5 * 1.3)

    def test_no_entries_returns_1(self):
        """Empty list returns 1.0 (no boost)."""
        assert aggregate_multipliers([]) == pytest.approx(1.0)

    def test_no_stack_group_each_stacks(self):
        """Entries without stack_group each form their own group (multiply)."""
        entries = [
            {"multiplier": 1.5},
            {"multiplier": 1.3},
        ]
        assert aggregate_multipliers(entries) == pytest.approx(1.5 * 1.3)

    def test_mixed_groups_and_ungrouped(self):
        """Mix of grouped and ungrouped entries."""
        entries = [
            {"multiplier": 1.5, "stack_group": "a"},
            {"multiplier": 1.2, "stack_group": "a"},  # MAX with above = 1.5
            {"multiplier": 1.1},                       # own group
        ]
        # 1.5 * 1.1 = 1.65
        assert aggregate_multipliers(entries) == pytest.approx(1.65)


class TestAggregateRates:
    """Two-phase rate stacking: intra-group MAX, inter-group SUM (PROJ-300)."""

    def test_no_entries_returns_zero(self):
        assert aggregate_rates([]) == pytest.approx(0.0)

    def test_single_entry(self):
        entries = [{"rate": 0.5, "stack_group": "radiation"}]
        assert aggregate_rates(entries) == pytest.approx(0.5)

    def test_same_group_takes_max(self):
        """Two radiation belts at same hex: take the worst, don't sum."""
        entries = [
            {"rate": 0.5, "stack_group": "radiation"},
            {"rate": 0.3, "stack_group": "radiation"},
        ]
        assert aggregate_rates(entries) == pytest.approx(0.5)

    def test_different_groups_sum(self):
        """Plasma damage + radiation damage: physically additive."""
        entries = [
            {"rate": 0.5, "stack_group": "plasma"},
            {"rate": 0.3, "stack_group": "radiation"},
        ]
        assert aggregate_rates(entries) == pytest.approx(0.8)

    def test_no_stack_group_each_sums(self):
        """Ungrouped entries each form own group (sum)."""
        entries = [{"rate": 0.4}, {"rate": 0.2}]
        assert aggregate_rates(entries) == pytest.approx(0.6)

    def test_mixed_groups_and_ungrouped(self):
        entries = [
            {"rate": 0.5, "stack_group": "a"},
            {"rate": 0.2, "stack_group": "a"},  # MAX with above = 0.5
            {"rate": 0.1},                       # own group
        ]
        assert aggregate_rates(entries) == pytest.approx(0.6)

    def test_zero_rate_entries(self):
        entries = [{"rate": 0.0, "stack_group": "a"}, {"rate": 0.0}]
        assert aggregate_rates(entries) == pytest.approx(0.0)

    def test_missing_rate_treated_as_zero(self):
        entries = [{"stack_group": "a"}, {"rate": 0.5}]
        assert aggregate_rates(entries) == pytest.approx(0.5)
