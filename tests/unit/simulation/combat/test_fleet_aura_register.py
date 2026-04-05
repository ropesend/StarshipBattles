"""
Tests for FleetAuraManager.register_ship() method.

PROJ-243 Phase 2: Verify that register_ship() scans the new ship for
fleet-scope abilities and recalculates bonuses so the new ship both
contributes to and receives fleet bonuses.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch

from game.simulation.combat.fleet_aura_manager import FleetAuraManager
from game.simulation.components.abilities.base import AbilityScope


def _make_mock_ship(team_id=0, name="Ship", is_alive=True, abilities=None):
    """Create a mock ship with optional fleet-scope abilities.

    Args:
        team_id: Ship's team
        name: Ship name
        is_alive: Whether ship is alive
        abilities: List of (ability_name, value, scope, stack_group) tuples
    """
    ship = Mock()
    ship.name = name
    ship.team_id = team_id
    ship.is_alive = is_alive
    ship.is_derelict = False
    ship.fleet_attack_bonus = 0.0
    ship.fleet_defense_bonus = 0.0

    if abilities:
        components = []
        for ability_name, value, scope, stack_group in abilities:
            ab = Mock()
            ab.value = value
            ab.scope = scope
            ab.stack_group = stack_group
            type(ab).__name__ = ability_name

            comp = Mock()
            comp.name = f"comp_{ability_name}"
            comp.is_operational = True
            comp.ability_instances = [ab]
            components.append(comp)
        ship.get_all_components = Mock(return_value=components)
    else:
        ship.get_all_components = Mock(return_value=[])

    return ship


class TestRegisterShip:
    """Tests for FleetAuraManager.register_ship()."""

    def test_register_ship_scans_new_ship(self):
        """register_ship() calls _scan_ship for the new ship."""
        manager = FleetAuraManager()
        # Initialize with one existing ship (no abilities)
        existing = _make_mock_ship(team_id=0, name="Existing")
        manager.initialize([existing])

        new_ship = _make_mock_ship(team_id=0, name="Newcomer")
        all_ships = [existing, new_ship]

        with patch.object(manager, '_scan_ship', wraps=manager._scan_ship) as mock_scan:
            manager.register_ship(new_ship, all_ships)
            mock_scan.assert_called_once_with(new_ship)

    def test_register_ship_recalculates_bonuses(self):
        """register_ship() calls _recalculate with all_ships."""
        manager = FleetAuraManager()
        existing = _make_mock_ship(team_id=0, name="Existing")
        manager.initialize([existing])

        new_ship = _make_mock_ship(team_id=0, name="Newcomer")
        all_ships = [existing, new_ship]

        with patch.object(manager, '_recalculate', wraps=manager._recalculate) as mock_recalc:
            manager.register_ship(new_ship, all_ships)
            mock_recalc.assert_called_once_with(all_ships)

    def test_new_ship_receives_existing_fleet_bonuses(self):
        """After register_ship(), the new ship receives existing fleet attack bonuses."""
        manager = FleetAuraManager()

        # Existing ship provides a fleet-scope ToHitAttackModifier
        provider = _make_mock_ship(
            team_id=0,
            name="Provider",
            abilities=[("ToHitAttackModifier", 5.0, AbilityScope.FLEET, "sensors")]
        )
        manager.initialize([provider])
        assert provider.fleet_attack_bonus == 5.0

        # New ship joins mid-battle
        new_ship = _make_mock_ship(team_id=0, name="Newcomer")
        all_ships = [provider, new_ship]

        manager.register_ship(new_ship, all_ships)

        # New ship should now receive the fleet attack bonus
        assert new_ship.fleet_attack_bonus == 5.0

    def test_existing_ships_receive_new_ships_bonuses(self):
        """After register_ship(), existing ships receive bonuses from new ship's fleet-scope abilities."""
        manager = FleetAuraManager()

        # Existing ship has no fleet abilities
        existing = _make_mock_ship(team_id=0, name="Existing")
        manager.initialize([existing])
        assert existing.fleet_defense_bonus == 0.0

        # New ship provides a fleet-scope ToHitDefenseModifier
        new_ship = _make_mock_ship(
            team_id=0,
            name="ECMShip",
            abilities=[("ToHitDefenseModifier", 3.0, AbilityScope.FLEET, "ecm")]
        )
        all_ships = [existing, new_ship]

        manager.register_ship(new_ship, all_ships)

        # Both ships should receive the fleet defense bonus
        assert existing.fleet_defense_bonus == 3.0
        assert new_ship.fleet_defense_bonus == 3.0

    def test_register_dead_ship_does_not_scan(self):
        """register_ship() does not scan a dead ship."""
        manager = FleetAuraManager()
        existing = _make_mock_ship(team_id=0, name="Existing")
        manager.initialize([existing])

        dead_ship = _make_mock_ship(team_id=0, name="Dead", is_alive=False)
        all_ships = [existing, dead_ship]

        with patch.object(manager, '_scan_ship') as mock_scan:
            manager.register_ship(dead_ship, all_ships)
            mock_scan.assert_not_called()
