"""
Tests for FleetAuraManager.unregister_ship() method.

PROJ-268: Verify that unregister_ship() removes a ship's AuraProvider entries
from the manager and recalculates bonuses so teammates no longer receive
bonuses from the removed ship.
"""
import pytest
from unittest.mock import Mock, patch

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


class TestUnregisterShip:
    """Tests for FleetAuraManager.unregister_ship()."""

    def test_unregister_removes_providers_for_ship(self):
        """unregister_ship() removes all AuraProvider entries for the given ship."""
        manager = FleetAuraManager()
        provider_ship = _make_mock_ship(
            team_id=0,
            name="Provider",
            abilities=[("ToHitAttackModifier", 5.0, AbilityScope.FLEET, "sensors")]
        )
        other_ship = _make_mock_ship(team_id=0, name="Other")
        all_ships = [provider_ship, other_ship]
        manager.initialize(all_ships)

        # Verify provider was registered
        assert len(manager._providers) == 1

        # Unregister the provider ship
        remaining = [other_ship]
        manager.unregister_ship(provider_ship, remaining)

        # Provider entries should be removed
        assert len(manager._providers) == 0

    def test_unregister_calls_recalculate(self):
        """unregister_ship() calls _recalculate() with remaining ships."""
        manager = FleetAuraManager()
        provider_ship = _make_mock_ship(
            team_id=0,
            name="Provider",
            abilities=[("ToHitAttackModifier", 5.0, AbilityScope.FLEET, "sensors")]
        )
        other_ship = _make_mock_ship(team_id=0, name="Other")
        manager.initialize([provider_ship, other_ship])

        remaining = [other_ship]
        with patch.object(manager, '_recalculate', wraps=manager._recalculate) as mock_recalc:
            manager.unregister_ship(provider_ship, remaining)
            mock_recalc.assert_called_once_with(remaining)

    def test_teammates_lose_bonus_after_unregister(self):
        """After unregister_ship(), teammates no longer receive the removed ship's bonuses."""
        manager = FleetAuraManager()
        provider_ship = _make_mock_ship(
            team_id=0,
            name="Provider",
            abilities=[("ToHitAttackModifier", 5.0, AbilityScope.FLEET, "sensors")]
        )
        teammate = _make_mock_ship(team_id=0, name="Teammate")
        all_ships = [provider_ship, teammate]
        manager.initialize(all_ships)

        # Teammate should have the bonus
        assert teammate.fleet_attack_bonus == 5.0

        # Remove the provider
        remaining = [teammate]
        manager.unregister_ship(provider_ship, remaining)

        # Teammate should lose the bonus
        assert teammate.fleet_attack_bonus == 0.0

    def test_unregister_ship_without_abilities_is_noop(self):
        """Unregistering a ship that has no fleet-scope abilities does not crash."""
        manager = FleetAuraManager()
        ship_a = _make_mock_ship(team_id=0, name="A")
        ship_b = _make_mock_ship(team_id=0, name="B")
        manager.initialize([ship_a, ship_b])

        assert len(manager._providers) == 0

        # Should not raise
        remaining = [ship_b]
        manager.unregister_ship(ship_a, remaining)

        assert len(manager._providers) == 0

    def test_unregister_does_not_affect_other_teams_providers(self):
        """Unregistering a ship only removes that ship's providers, not other teams'."""
        manager = FleetAuraManager()
        team0_provider = _make_mock_ship(
            team_id=0,
            name="T0Provider",
            abilities=[("ToHitAttackModifier", 5.0, AbilityScope.FLEET, "sensors")]
        )
        team1_provider = _make_mock_ship(
            team_id=1,
            name="T1Provider",
            abilities=[("ToHitDefenseModifier", 3.0, AbilityScope.FLEET, "ecm")]
        )
        team0_other = _make_mock_ship(team_id=0, name="T0Other")
        team1_other = _make_mock_ship(team_id=1, name="T1Other")
        all_ships = [team0_provider, team1_provider, team0_other, team1_other]
        manager.initialize(all_ships)

        assert len(manager._providers) == 2
        assert team1_other.fleet_defense_bonus == 3.0

        # Remove team 0 provider
        remaining = [team1_provider, team0_other, team1_other]
        manager.unregister_ship(team0_provider, remaining)

        # Team 1's provider should still exist
        assert any(p.ship is team1_provider for p in manager._providers)
        assert team1_other.fleet_defense_bonus == 3.0

    def test_register_then_unregister_returns_to_original_state(self):
        """Round-trip: register then unregister restores original bonus state."""
        manager = FleetAuraManager()
        existing = _make_mock_ship(team_id=0, name="Existing")
        manager.initialize([existing])

        assert existing.fleet_attack_bonus == 0.0

        # Register a provider mid-battle
        new_provider = _make_mock_ship(
            team_id=0,
            name="NewProvider",
            abilities=[("ToHitAttackModifier", 7.0, AbilityScope.FLEET, "sensors")]
        )
        all_ships = [existing, new_provider]
        manager.register_ship(new_provider, all_ships)
        assert existing.fleet_attack_bonus == 7.0

        # Unregister the provider (it retreats)
        remaining = [existing]
        manager.unregister_ship(new_provider, remaining)
        assert existing.fleet_attack_bonus == 0.0
