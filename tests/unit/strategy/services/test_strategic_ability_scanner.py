"""Tests for strategic_ability_scanner — scoped ability queries and aggregation."""
import pytest
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from unittest.mock import MagicMock

from game.strategy.services.strategic_ability_scanner import (
    find_abilities_at_planet,
    find_abilities_in_scope,
    aggregate_multipliers,
)


# --- Minimal test doubles ---

@dataclass
class MockFacility:
    design_data: Dict[str, Any]
    is_operational: bool = True
    instance_id: str = "fac-1"
    component_states: Dict[str, bool] = field(default_factory=dict)

    def is_component_active(self, comp_id):
        return self.component_states.get(comp_id, True)


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
        galaxy = MagicMock()

        if planets_at_hex is not None:
            galaxy.get_planets_at_global_hex.return_value = planets_at_hex
        else:
            galaxy.get_planets_at_global_hex.return_value = []

        if system_planets is not None:
            mock_system = MagicMock()
            mock_system.planets = system_planets
            galaxy.get_system_at_location.return_value = mock_system
        else:
            galaxy.get_system_at_location.return_value = None

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
