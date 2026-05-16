"""Tests for system-scoped planetary complex components: System Defense Uplink and
System Countermeasures Network.

Verifies:
- Components load from production data with correct abilities, scope, and stack group
- Restricted to Planetary Complex vehicle type only
- Fleet aura manager picks up allied_system-scoped ToHit modifiers
- Stack groups are isolated from ship-level TDL/EWS and from Sensor/ECM
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

SYSTEM_DEFENSE_UPLINK_ID = "system_defense_uplink"
SYSTEM_COUNTERMEASURES_NETWORK_ID = "system_countermeasures_network"


# =============================================================================
# System Defense Uplink Tests
# =============================================================================


class TestSystemDefenseUplinkDefinition:
    """Verify System Defense Uplink loads from components.json with correct properties."""

    def test_component_loads(self, fresh_registries):
        """System Defense Uplink should load from production data."""
        comp = create_component(SYSTEM_DEFENSE_UPLINK_ID, registries=fresh_registries)
        assert comp is not None
        assert comp.name == "System Defense Uplink"

    def test_has_to_hit_attack_modifier(self, fresh_registries):
        """Should have a ToHitAttackModifier ability."""
        comp = create_component(SYSTEM_DEFENSE_UPLINK_ID, registries=fresh_registries)
        ability = _find_ability(comp, "ToHitAttackModifier")
        assert ability is not None

    def test_attack_modifier_value(self, fresh_registries):
        """ToHitAttackModifier should have value 0.3."""
        comp = create_component(SYSTEM_DEFENSE_UPLINK_ID, registries=fresh_registries)
        ability = _find_ability(comp, "ToHitAttackModifier")
        assert ability.value == pytest.approx(0.3)

    def test_attack_modifier_allied_system_scope(self, fresh_registries):
        """ToHitAttackModifier should have allied_system scope."""
        comp = create_component(SYSTEM_DEFENSE_UPLINK_ID, registries=fresh_registries)
        ability = _find_ability(comp, "ToHitAttackModifier")
        assert ability.scope == AbilityScope.ALLIED_SYSTEM

    def test_attack_modifier_stack_group(self, fresh_registries):
        """ToHitAttackModifier should use SystemDefenseUplink stack group."""
        comp = create_component(SYSTEM_DEFENSE_UPLINK_ID, registries=fresh_registries)
        ability = _find_ability(comp, "ToHitAttackModifier")
        assert ability.stack_group == "SystemDefenseUplink"

    def test_stack_group_differs_from_ship_variants(self, fresh_registries):
        """Stack group should differ from TDL, Sensor, and MasterComputer groups."""
        comp = create_component(SYSTEM_DEFENSE_UPLINK_ID, registries=fresh_registries)
        ability = _find_ability(comp, "ToHitAttackModifier")
        assert ability.stack_group not in ("TacticalDataLink", "Sensor", "MasterComputer")

    def test_planetary_complex_only(self, fresh_registries):
        """Should only be allowed on Planetary Complex."""
        comp = create_component(SYSTEM_DEFENSE_UPLINK_ID, registries=fresh_registries)
        allowed = comp.data.get("allowed_vehicle_types", [])
        assert allowed == ["Planetary Complex"]

    def test_has_energy_consumption(self, fresh_registries):
        """Should have ResourceConsumption for energy."""
        comp = create_component(SYSTEM_DEFENSE_UPLINK_ID, registries=fresh_registries)
        ability = _find_ability(comp, "ResourceConsumption")
        assert ability is not None

    def test_has_crew_required(self, fresh_registries):
        """Should have CrewRequired ability."""
        comp = create_component(SYSTEM_DEFENSE_UPLINK_ID, registries=fresh_registries)
        ability = _find_ability(comp, "RequiresMaintenance")
        assert ability is not None

    def test_has_requires_cnc(self, fresh_registries):
        """Should require command and control."""
        comp = create_component(SYSTEM_DEFENSE_UPLINK_ID, registries=fresh_registries)
        ability = _find_ability(comp, "RequiresCommandAndControl")
        assert ability is not None

    def test_mass_is_heavy(self, fresh_registries):
        """Should be much heavier than ship-level TDL (mass 200)."""
        comp = create_component(SYSTEM_DEFENSE_UPLINK_ID, registries=fresh_registries)
        assert comp.mass >= 400


# =============================================================================
# System Countermeasures Network Tests
# =============================================================================


class TestSystemCountermeasuresNetworkDefinition:
    """Verify System Countermeasures Network loads from components.json with correct properties."""

    def test_component_loads(self, fresh_registries):
        """System Countermeasures Network should load from production data."""
        comp = create_component(SYSTEM_COUNTERMEASURES_NETWORK_ID, registries=fresh_registries)
        assert comp is not None
        assert comp.name == "System Countermeasures Network"

    def test_has_to_hit_defense_modifier(self, fresh_registries):
        """Should have a ToHitDefenseModifier ability."""
        comp = create_component(SYSTEM_COUNTERMEASURES_NETWORK_ID, registries=fresh_registries)
        ability = _find_ability(comp, "ToHitDefenseModifier")
        assert ability is not None

    def test_defense_modifier_value(self, fresh_registries):
        """ToHitDefenseModifier should have value 0.3."""
        comp = create_component(SYSTEM_COUNTERMEASURES_NETWORK_ID, registries=fresh_registries)
        ability = _find_ability(comp, "ToHitDefenseModifier")
        assert ability.value == pytest.approx(0.3)

    def test_defense_modifier_allied_system_scope(self, fresh_registries):
        """ToHitDefenseModifier should have allied_system scope."""
        comp = create_component(SYSTEM_COUNTERMEASURES_NETWORK_ID, registries=fresh_registries)
        ability = _find_ability(comp, "ToHitDefenseModifier")
        assert ability.scope == AbilityScope.ALLIED_SYSTEM

    def test_defense_modifier_stack_group(self, fresh_registries):
        """ToHitDefenseModifier should use SystemCountermeasures stack group."""
        comp = create_component(SYSTEM_COUNTERMEASURES_NETWORK_ID, registries=fresh_registries)
        ability = _find_ability(comp, "ToHitDefenseModifier")
        assert ability.stack_group == "SystemCountermeasures"

    def test_stack_group_differs_from_ship_variants(self, fresh_registries):
        """Stack group should differ from EWS, ECM, and MasterComputer groups."""
        comp = create_component(SYSTEM_COUNTERMEASURES_NETWORK_ID, registries=fresh_registries)
        ability = _find_ability(comp, "ToHitDefenseModifier")
        assert ability.stack_group not in ("ElectronicWarfare", "ECM", "MasterComputer")

    def test_planetary_complex_only(self, fresh_registries):
        """Should only be allowed on Planetary Complex."""
        comp = create_component(SYSTEM_COUNTERMEASURES_NETWORK_ID, registries=fresh_registries)
        allowed = comp.data.get("allowed_vehicle_types", [])
        assert allowed == ["Planetary Complex"]

    def test_has_energy_consumption(self, fresh_registries):
        """Should have ResourceConsumption for energy."""
        comp = create_component(SYSTEM_COUNTERMEASURES_NETWORK_ID, registries=fresh_registries)
        ability = _find_ability(comp, "ResourceConsumption")
        assert ability is not None

    def test_has_crew_required(self, fresh_registries):
        """Should have CrewRequired ability."""
        comp = create_component(SYSTEM_COUNTERMEASURES_NETWORK_ID, registries=fresh_registries)
        ability = _find_ability(comp, "RequiresMaintenance")
        assert ability is not None

    def test_has_requires_cnc(self, fresh_registries):
        """Should require command and control."""
        comp = create_component(SYSTEM_COUNTERMEASURES_NETWORK_ID, registries=fresh_registries)
        ability = _find_ability(comp, "RequiresCommandAndControl")
        assert ability is not None

    def test_mass_is_heavy(self, fresh_registries):
        """Should be much heavier than ship-level EWS (mass 250)."""
        comp = create_component(SYSTEM_COUNTERMEASURES_NETWORK_ID, registries=fresh_registries)
        assert comp.mass >= 400


# =============================================================================
# Fleet Aura Integration Tests
# =============================================================================


def _make_ability_class(name):
    """Create a real class with the given name for type(ab).__name__ checks."""
    return type(name, (), {})


def _make_ship(team_id=0, alive=True, abilities=None):
    """Create a mock ship with optional scoped abilities."""
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


class TestSystemScopeAuraIntegration:
    """Verify FleetAuraManager picks up allied_system-scoped abilities."""

    def test_system_uplink_provides_attack_bonus(self):
        """System Defense Uplink should provide attack bonus to all team ships."""
        manager = FleetAuraManager()
        provider = _make_ship(team_id=0, abilities=[
            ("ToHitAttackModifier", 0.3, AbilityScope.ALLIED_SYSTEM, "SystemDefenseUplink"),
        ])
        teammate = _make_ship(team_id=0)

        manager.initialize([provider, teammate])

        assert provider.fleet_attack_bonus == pytest.approx(0.3)
        assert teammate.fleet_attack_bonus == pytest.approx(0.3)

    def test_system_countermeasures_provides_defense_bonus(self):
        """System Countermeasures Network should provide defense bonus to all team ships."""
        manager = FleetAuraManager()
        provider = _make_ship(team_id=0, abilities=[
            ("ToHitDefenseModifier", 0.3, AbilityScope.ALLIED_SYSTEM, "SystemCountermeasures"),
        ])
        teammate = _make_ship(team_id=0)

        manager.initialize([provider, teammate])

        assert provider.fleet_defense_bonus == pytest.approx(0.3)
        assert teammate.fleet_defense_bonus == pytest.approx(0.3)

    def test_system_uplink_stacks_separately_from_tdl(self):
        """System Defense Uplink (SystemDefenseUplink) should SUM with TDL (TacticalDataLink)."""
        manager = FleetAuraManager()
        ship = _make_ship(team_id=0, abilities=[
            ("ToHitAttackModifier", 0.3, AbilityScope.ALLIED_SYSTEM, "SystemDefenseUplink"),
            ("ToHitAttackModifier", 0.5, AbilityScope.FLEET, "TacticalDataLink"),
        ])
        teammate = _make_ship(team_id=0)

        manager.initialize([ship, teammate])

        # Different stack groups SUM: 0.3 + 0.5 = 0.8
        assert teammate.fleet_attack_bonus == pytest.approx(0.8)

    def test_system_uplink_does_not_buff_enemies(self):
        """System Defense Uplink should not buff enemy ships."""
        manager = FleetAuraManager()
        provider = _make_ship(team_id=0, abilities=[
            ("ToHitAttackModifier", 0.3, AbilityScope.ALLIED_SYSTEM, "SystemDefenseUplink"),
        ])
        enemy = _make_ship(team_id=1)

        manager.initialize([provider, enemy])

        assert enemy.fleet_attack_bonus == pytest.approx(0.0)


# =============================================================================
# Helpers
# =============================================================================


def _find_ability(component, ability_class_name: str):
    """Find an ability instance on a component by class name."""
    for ab in getattr(component, 'ability_instances', []):
        if type(ab).__name__ == ability_class_name:
            return ab
    return None
