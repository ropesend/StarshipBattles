"""Tests for CombatModifierCollector — strategic-to-combat modifier resolution."""
import pytest
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from game.strategy.services.combat_modifier_collector import (
    FleetCombatModifiers,
    collect_combat_modifiers,
)


@dataclass
class MockFacility:
    design_data: Dict[str, Any] = field(default_factory=dict)
    is_operational: bool = True
    component_states: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MockPlanet:
    name: str = "Test"
    id: int = 1
    owner_id: int = 0
    facilities: List = field(default_factory=list)


@dataclass
class MockFleet:
    id: int = 1
    owner_id: int = 0
    location: Any = None
    ships: List = field(default_factory=list)


@dataclass
class MockEmpire:
    id: int = 0
    colonies: List = field(default_factory=list)


@dataclass
class MockSystem:
    planets: List = field(default_factory=list)


@dataclass
class MockGalaxy:
    _systems: Dict = field(default_factory=dict)
    _planets_by_hex: Dict = field(default_factory=dict)

    def get_system_at_hex(self, hex_coord):
        return self._systems.get(str(hex_coord))

    def get_planets_at_global_hex(self, hex_coord):
        return self._planets_by_hex.get(str(hex_coord), [])

    def get_planet_global_hex(self, planet):
        return "hex_0"

    def get_system_of_planet(self, planet):
        return self._systems.get("default")


def _facility_with_ability(ability_name, data):
    """Create a facility with a specific ability on a component."""
    return MockFacility(design_data={
        "layers": {"CORE": [
            {"id": "test_comp", "abilities": {ability_name: data}}
        ]}
    })


class TestFleetCombatModifiers:
    """Tests for the FleetCombatModifiers dataclass."""

    def test_defaults(self):
        mods = FleetCombatModifiers()
        assert mods.shield_mult == 1.0
        assert mods.damage_mult == 1.0
        assert mods.flat_shield_bonus == 0.0

    def test_no_effect_when_defaults(self):
        """Default modifiers should have no combat effect."""
        mods = FleetCombatModifiers()
        assert mods.shield_mult == 1.0
        assert mods.damage_mult == 1.0


class TestCollectCombatModifiers:
    """Tests for collect_combat_modifiers()."""

    def test_no_facilities_returns_defaults(self):
        """No facilities at battle location = default modifiers."""
        fleet = MockFleet(location="hex_0", owner_id=0)
        opponent = MockFleet(location="hex_0", owner_id=1)
        galaxy = MockGalaxy()
        empires = [MockEmpire(id=0), MockEmpire(id=1)]

        result = collect_combat_modifiers(fleet, opponent, galaxy, empires, None)

        assert result.shield_mult == pytest.approx(1.0)
        assert result.damage_mult == pytest.approx(1.0)
        assert result.flat_shield_bonus == pytest.approx(0.0)

    def test_allied_shield_booster_applies_to_fleet(self):
        """Allied shield booster on a planet should boost the fleet's shields."""
        booster_facility = _facility_with_ability("ShieldModifier", {
            "multiplier": 1.25,
            "scope": "allied_system",
            "stack_group": "shield_boost_sys"
        })
        planet = MockPlanet(owner_id=0, facilities=[booster_facility])
        system = MockSystem(planets=[planet])
        galaxy = MockGalaxy(
            _systems={"default": system},
            _planets_by_hex={"hex_0": [planet]}
        )
        fleet = MockFleet(location="hex_0", owner_id=0)
        opponent = MockFleet(location="hex_0", owner_id=1)
        emp0 = MockEmpire(id=0, colonies=[planet])
        empires = [emp0, MockEmpire(id=1)]

        result = collect_combat_modifiers(fleet, opponent, galaxy, empires, None)

        assert result.shield_mult == pytest.approx(1.25)

    def test_enemy_shield_suppressor_applies_to_fleet(self):
        """Enemy shield suppressor should reduce the fleet's shields."""
        suppressor_facility = _facility_with_ability("ShieldModifier", {
            "multiplier": 0.75,
            "scope": "enemy_system",
            "stack_group": "shield_suppress_sys"
        })
        # Suppressor is owned by empire 1, enemies of fleet owner (empire 0)
        enemy_planet = MockPlanet(owner_id=1, facilities=[suppressor_facility])
        # Need a planet at the hex for reference, and the enemy planet in the system
        ref_planet = MockPlanet(owner_id=0)
        system = MockSystem(planets=[ref_planet, enemy_planet])
        galaxy = MockGalaxy(
            _systems={"default": system},
            _planets_by_hex={"hex_0": [ref_planet]}
        )
        fleet = MockFleet(location="hex_0", owner_id=0)
        opponent = MockFleet(location="hex_0", owner_id=1)
        emp1 = MockEmpire(id=1, colonies=[enemy_planet])
        empires = [MockEmpire(id=0, colonies=[ref_planet]), emp1]

        result = collect_combat_modifiers(fleet, opponent, galaxy, empires, None)

        assert result.shield_mult == pytest.approx(0.75)

    def test_flat_shield_projection_sums(self):
        """Scoped ShieldProjection should add flat shield points."""
        projector_facility = _facility_with_ability("ShieldProjection", {
            "value": 50,
            "scope": "allied_system"
        })
        planet = MockPlanet(owner_id=0, facilities=[projector_facility])
        system = MockSystem(planets=[planet])
        galaxy = MockGalaxy(
            _systems={"default": system},
            _planets_by_hex={"hex_0": [planet]}
        )
        fleet = MockFleet(location="hex_0", owner_id=0)
        opponent = MockFleet(location="hex_0", owner_id=1)
        emp0 = MockEmpire(id=0, colonies=[planet])
        empires = [emp0, MockEmpire(id=1)]

        result = collect_combat_modifiers(fleet, opponent, galaxy, empires, None)

        assert result.flat_shield_bonus == pytest.approx(50.0)

    def test_damage_modifier_applies(self):
        """Damage booster should modify the fleet's damage output."""
        booster = _facility_with_ability("DamageModifier", {
            "multiplier": 1.25,
            "scope": "allied_system",
            "stack_group": "damage_boost_sys"
        })
        planet = MockPlanet(owner_id=0, facilities=[booster])
        system = MockSystem(planets=[planet])
        galaxy = MockGalaxy(
            _systems={"default": system},
            _planets_by_hex={"hex_0": [planet]}
        )
        fleet = MockFleet(location="hex_0", owner_id=0)
        opponent = MockFleet(location="hex_0", owner_id=1)
        emp0 = MockEmpire(id=0, colonies=[planet])
        empires = [emp0, MockEmpire(id=1)]

        result = collect_combat_modifiers(fleet, opponent, galaxy, empires, None)

        assert result.damage_mult == pytest.approx(1.25)
