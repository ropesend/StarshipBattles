"""
Tests for fleet aura caching and shared aggregator reuse (PROJ-253 Phase 3).

Verifies that:
- FleetAuraManager uses the shared _aggregate_ability_groups function
- Provider-state caching prevents redundant recalculation
"""
from unittest.mock import MagicMock, patch
from game.simulation.combat.fleet_aura_manager import FleetAuraManager
from game.simulation.components.abilities.base import AbilityScope


def _mock_ship(team_id=0, alive=True, name="Ship1", abilities=None):
    """Create a mock ship with optional aura abilities."""
    ship = MagicMock()
    ship.team_id = team_id
    ship.is_alive = alive
    ship.is_derelict = False
    ship.name = name
    ship.fleet_attack_bonus = 0.0
    ship.fleet_defense_bonus = 0.0

    comps = []
    if abilities:
        for ab_name, value, scope in abilities:
            comp = MagicMock()
            comp.is_operational = True
            comp.name = f"comp_{ab_name}"
            ab = MagicMock()
            type(ab).__name__ = ab_name
            ab.scope = scope
            ab.value = value
            ab.stack_group = None
            comp.ability_instances = [ab]
            comps.append(comp)

    ship.get_all_components.return_value = comps
    return ship


class TestFleetAuraCaching:
    """FleetAuraManager should cache and reuse aggregation results."""

    def test_update_with_no_changes_skips_recalculation(self):
        """Calling update() when providers haven't changed should use cache."""
        mgr = FleetAuraManager()
        ship = _mock_ship(abilities=[
            ("ToHitAttackModifier", 5.0, AbilityScope.FLEET),
        ])
        mgr.initialize([ship])

        # After initialize, bonuses are computed
        assert ship.fleet_attack_bonus == 5.0

        # Mark as clean (initialize already ran)
        assert mgr._providers_dirty is False

        # Update should skip recalculation since nothing changed
        mgr.update([ship])
        assert ship.fleet_attack_bonus == 5.0

    def test_invalidate_forces_recalculation(self):
        """invalidate_aura_cache() should force next update to recalculate."""
        mgr = FleetAuraManager()
        ship = _mock_ship()
        mgr.initialize([ship])

        mgr.invalidate_aura_cache()
        assert mgr._providers_dirty is True

    def test_uses_shared_aggregator(self):
        """_recalculate should delegate to the shared _aggregate_ability_groups."""
        mgr = FleetAuraManager()
        ship = _mock_ship(abilities=[
            ("ToHitAttackModifier", 5.0, AbilityScope.FLEET),
        ])

        with patch(
            'game.simulation.combat.fleet_aura_manager._aggregate_ability_groups'
        ) as mock_agg:
            mock_agg.return_value = {'ToHitAttackModifier': 5.0}
            mgr.initialize([ship])
            mock_agg.assert_called()
