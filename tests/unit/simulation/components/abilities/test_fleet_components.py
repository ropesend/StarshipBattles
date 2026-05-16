"""Tests for fleet-scoped Tactical Data Link and Electronic Warfare Suite components.

Verifies:
- Components load from production data with correct abilities and scope
- Fleet aura manager picks up fleet-scoped ToHit modifiers
- Stack groups are isolated from ship-level Sensor/ECM groups
- Energy consumption and crew requirements are present
"""
import pytest
from unittest.mock import MagicMock

from game.simulation.components.component import create_component
from game.simulation.components.abilities.base import AbilityScope
from game.simulation.combat.fleet_aura_manager import FleetAuraManager


# =============================================================================
# Component IDs
# =============================================================================

TACTICAL_DATA_LINK_ID = "tactical_data_link"
ELECTRONIC_WARFARE_SUITE_ID = "electronic_warfare_suite"


# =============================================================================
# Data Loading Tests
# =============================================================================


class TestTacticalDataLinkDefinition:
    """Verify Tactical Data Link loads from components.json with correct properties."""

    def test_component_loads(self, fresh_registries):
        """Tactical Data Link should load from production data."""
        comp = create_component(TACTICAL_DATA_LINK_ID, registries=fresh_registries)
        assert comp is not None
        assert comp.name == "Tactical Data Link"

    def test_has_to_hit_attack_modifier(self, fresh_registries):
        """Should have a ToHitAttackModifier ability."""
        comp = create_component(TACTICAL_DATA_LINK_ID, registries=fresh_registries)
        ability = _find_ability(comp, "ToHitAttackModifier")
        assert ability is not None

    def test_attack_modifier_value(self, fresh_registries):
        """ToHitAttackModifier should have value 0.5."""
        comp = create_component(TACTICAL_DATA_LINK_ID, registries=fresh_registries)
        ability = _find_ability(comp, "ToHitAttackModifier")
        assert ability.value == pytest.approx(0.5)

    def test_attack_modifier_fleet_scope(self, fresh_registries):
        """ToHitAttackModifier should have fleet scope."""
        comp = create_component(TACTICAL_DATA_LINK_ID, registries=fresh_registries)
        ability = _find_ability(comp, "ToHitAttackModifier")
        assert ability.scope == AbilityScope.FLEET

    def test_attack_modifier_stack_group(self, fresh_registries):
        """ToHitAttackModifier should use TacticalDataLink stack group."""
        comp = create_component(TACTICAL_DATA_LINK_ID, registries=fresh_registries)
        ability = _find_ability(comp, "ToHitAttackModifier")
        assert ability.stack_group == "TacticalDataLink"

    def test_stack_group_differs_from_sensor(self, fresh_registries):
        """Stack group should differ from regular Combat Sensor's 'Sensor' group."""
        comp = create_component(TACTICAL_DATA_LINK_ID, registries=fresh_registries)
        ability = _find_ability(comp, "ToHitAttackModifier")
        assert ability.stack_group != "Sensor"

    def test_has_energy_consumption(self, fresh_registries):
        """Should have ResourceConsumption for energy."""
        comp = create_component(TACTICAL_DATA_LINK_ID, registries=fresh_registries)
        ability = _find_ability(comp, "ResourceConsumption")
        assert ability is not None

    def test_has_crew_required(self, fresh_registries):
        """Should have CrewRequired ability."""
        comp = create_component(TACTICAL_DATA_LINK_ID, registries=fresh_registries)
        ability = _find_ability(comp, "RequiresMaintenance")
        assert ability is not None

    def test_has_requires_cnc(self, fresh_registries):
        """Should require command and control."""
        comp = create_component(TACTICAL_DATA_LINK_ID, registries=fresh_registries)
        ability = _find_ability(comp, "RequiresCommandAndControl")
        assert ability is not None

    def test_mass_is_large(self, fresh_registries):
        """Should be significantly heavier than a regular Combat Sensor (mass 30)."""
        comp = create_component(TACTICAL_DATA_LINK_ID, registries=fresh_registries)
        assert comp.mass >= 150


class TestElectronicWarfareSuiteDefinition:
    """Verify Electronic Warfare Suite loads from components.json with correct properties."""

    def test_component_loads(self, fresh_registries):
        """Electronic Warfare Suite should load from production data."""
        comp = create_component(ELECTRONIC_WARFARE_SUITE_ID, registries=fresh_registries)
        assert comp is not None
        assert comp.name == "Electronic Warfare Suite"

    def test_has_to_hit_defense_modifier(self, fresh_registries):
        """Should have a ToHitDefenseModifier ability."""
        comp = create_component(ELECTRONIC_WARFARE_SUITE_ID, registries=fresh_registries)
        ability = _find_ability(comp, "ToHitDefenseModifier")
        assert ability is not None

    def test_defense_modifier_value(self, fresh_registries):
        """ToHitDefenseModifier should have value 0.5."""
        comp = create_component(ELECTRONIC_WARFARE_SUITE_ID, registries=fresh_registries)
        ability = _find_ability(comp, "ToHitDefenseModifier")
        assert ability.value == pytest.approx(0.5)

    def test_defense_modifier_fleet_scope(self, fresh_registries):
        """ToHitDefenseModifier should have fleet scope."""
        comp = create_component(ELECTRONIC_WARFARE_SUITE_ID, registries=fresh_registries)
        ability = _find_ability(comp, "ToHitDefenseModifier")
        assert ability.scope == AbilityScope.FLEET

    def test_defense_modifier_stack_group(self, fresh_registries):
        """ToHitDefenseModifier should use ElectronicWarfare stack group."""
        comp = create_component(ELECTRONIC_WARFARE_SUITE_ID, registries=fresh_registries)
        ability = _find_ability(comp, "ToHitDefenseModifier")
        assert ability.stack_group == "ElectronicWarfare"

    def test_stack_group_differs_from_ecm(self, fresh_registries):
        """Stack group should differ from regular ECM Suite's 'ECM' group."""
        comp = create_component(ELECTRONIC_WARFARE_SUITE_ID, registries=fresh_registries)
        ability = _find_ability(comp, "ToHitDefenseModifier")
        assert ability.stack_group != "ECM"

    def test_has_energy_consumption(self, fresh_registries):
        """Should have ResourceConsumption for energy."""
        comp = create_component(ELECTRONIC_WARFARE_SUITE_ID, registries=fresh_registries)
        ability = _find_ability(comp, "ResourceConsumption")
        assert ability is not None

    def test_has_crew_required(self, fresh_registries):
        """Should have CrewRequired ability."""
        comp = create_component(ELECTRONIC_WARFARE_SUITE_ID, registries=fresh_registries)
        ability = _find_ability(comp, "RequiresMaintenance")
        assert ability is not None

    def test_has_requires_cnc(self, fresh_registries):
        """Should require command and control."""
        comp = create_component(ELECTRONIC_WARFARE_SUITE_ID, registries=fresh_registries)
        ability = _find_ability(comp, "RequiresCommandAndControl")
        assert ability is not None

    def test_mass_is_large(self, fresh_registries):
        """Should be significantly heavier than a regular ECM Suite (mass 40)."""
        comp = create_component(ELECTRONIC_WARFARE_SUITE_ID, registries=fresh_registries)
        assert comp.mass >= 150


# =============================================================================
# Fleet Aura Integration Tests
# =============================================================================


def _make_ability_class(name):
    """Create a real class with the given name for type(ab).__name__ checks."""
    return type(name, (), {})


def _make_ship(team_id=0, alive=True, abilities=None):
    """Create a mock ship with optional fleet-scope abilities."""
    ship = MagicMock()
    ship.team_id = team_id
    ship.is_alive = alive
    ship.is_derelict = False
    ship.name = f"Ship_team{team_id}"
    ship.fleet_attack_bonus = 0.0
    ship.fleet_defense_bonus = 0.0

    comps = []
    if abilities:
        for ab_name, value, scope, stack_group in abilities:
            AbClass = _make_ability_class(ab_name)
            ab = AbClass()
            ab.scope = scope
            ab.value = value
            ab.stack_group = stack_group

            comp = MagicMock()
            comp.is_operational = True
            comp.ability_instances = [ab]
            comp.name = f"{ab_name}_comp"
            comps.append(comp)

    ship.get_all_components = MagicMock(return_value=comps)
    return ship


class TestFleetAuraIntegration:
    """Verify FleetAuraManager picks up fleet-scoped TDL and EWS abilities."""

    def test_tdl_provides_fleet_attack_bonus(self):
        """Tactical Data Link should provide attack bonus to all fleet ships."""
        manager = FleetAuraManager()
        provider = _make_ship(team_id=0, abilities=[
            ("ToHitAttackModifier", 0.5, AbilityScope.FLEET, "TacticalDataLink"),
        ])
        teammate = _make_ship(team_id=0)

        manager.initialize([provider, teammate])

        assert provider.fleet_attack_bonus == pytest.approx(0.5)
        assert teammate.fleet_attack_bonus == pytest.approx(0.5)

    def test_ews_provides_fleet_defense_bonus(self):
        """Electronic Warfare Suite should provide defense bonus to all fleet ships."""
        manager = FleetAuraManager()
        provider = _make_ship(team_id=0, abilities=[
            ("ToHitDefenseModifier", 0.5, AbilityScope.FLEET, "ElectronicWarfare"),
        ])
        teammate = _make_ship(team_id=0)

        manager.initialize([provider, teammate])

        assert provider.fleet_defense_bonus == pytest.approx(0.5)
        assert teammate.fleet_defense_bonus == pytest.approx(0.5)

    def test_tdl_does_not_buff_enemies(self):
        """Tactical Data Link should not buff enemy ships."""
        manager = FleetAuraManager()
        provider = _make_ship(team_id=0, abilities=[
            ("ToHitAttackModifier", 0.5, AbilityScope.FLEET, "TacticalDataLink"),
        ])
        enemy = _make_ship(team_id=1)

        manager.initialize([provider, enemy])

        assert enemy.fleet_attack_bonus == pytest.approx(0.0)

    def test_tdl_stacks_separately_from_sensor(self):
        """TDL (TacticalDataLink group) should SUM with regular Sensor group."""
        manager = FleetAuraManager()
        ship = _make_ship(team_id=0, abilities=[
            ("ToHitAttackModifier", 0.5, AbilityScope.FLEET, "TacticalDataLink"),
            ("ToHitAttackModifier", 1.0, AbilityScope.FLEET, "Sensor"),
        ])
        teammate = _make_ship(team_id=0)

        manager.initialize([ship, teammate])

        # Different stack groups SUM: 0.5 + 1.0 = 1.5
        assert teammate.fleet_attack_bonus == pytest.approx(1.5)

    def test_duplicate_tdl_same_group_takes_max(self):
        """Two TDLs in same stack group should MAX, not SUM."""
        manager = FleetAuraManager()
        ship = _make_ship(team_id=0, abilities=[
            ("ToHitAttackModifier", 0.5, AbilityScope.FLEET, "TacticalDataLink"),
            ("ToHitAttackModifier", 0.3, AbilityScope.FLEET, "TacticalDataLink"),
        ])
        teammate = _make_ship(team_id=0)

        manager.initialize([ship, teammate])

        # Same stack group takes MAX: max(0.5, 0.3) = 0.5
        assert teammate.fleet_attack_bonus == pytest.approx(0.5)


# =============================================================================
# Helpers
# =============================================================================


def _find_ability(component, ability_class_name: str):
    """Find an ability instance on a component by class name."""
    for ab in getattr(component, 'ability_instances', []):
        if type(ab).__name__ == ability_class_name:
            return ab
    return None
