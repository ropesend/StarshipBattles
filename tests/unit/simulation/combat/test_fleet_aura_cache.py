"""
Tests for fleet aura caching and shared aggregator reuse (PROJ-253 Phase 3).

Verifies that:
- FleetAuraManager uses the shared _aggregate_ability_groups function
- Provider-state caching prevents redundant recalculation
"""
from unittest.mock import MagicMock
from game.simulation.combat.fleet_aura_manager import FleetAuraManager
from game.simulation.components.abilities.base import AbilityScope


def _mock_ship(team_id=0, alive=True, name="Ship1", abilities=None):
    """Create a mock ship with optional aura abilities.

    ``abilities`` is a list of ``(name, value, scope)`` tuples (all with
    ``stack_group=None``) OR ``(name, value, scope, stack_group)`` 4-tuples.
    """
    ship = MagicMock()
    ship.team_id = team_id
    ship.is_alive = alive
    ship.is_derelict = False
    ship.name = name
    ship.fleet_attack_bonus = 0.0
    ship.fleet_defense_bonus = 0.0

    comps = []
    if abilities:
        for entry in abilities:
            if len(entry) == 4:
                ab_name, value, scope, stack_group = entry
            else:
                ab_name, value, scope = entry
                stack_group = None
            comp = MagicMock()
            comp.is_operational = True
            comp.name = f"comp_{ab_name}"
            ab = MagicMock()
            type(ab).__name__ = ab_name
            ab.scope = scope
            ab.value = value
            ab.stack_group = stack_group
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

    def test_aggregates_same_stack_group_via_max_and_distinct_groups_via_sum(self):
        """Behavioral coverage of the shared aggregator's two-phase
        MAX-within-group / SUM-across-groups rule.

        PROJ-491 Task 1.7: replaces the prior ``patch('..._aggregate_ability_groups')``
        + ``assert_called`` smoke. Three same-team ships provide
        ``ToHitAttackModifier`` auras:

        - Ship A: value 3.0 under stack_group ``"alpha"``
        - Ship B: value 5.0 under stack_group ``"alpha"`` (same group as A)
        - Ship C: value 2.0 under stack_group ``"beta"``

        Within ``"alpha"`` the aggregator picks ``MAX(3.0, 5.0) = 5.0``.
        Across groups it ``SUM``s: ``5.0 + 2.0 = 7.0``. Every alive
        same-team ship observes the team total via ``fleet_attack_bonus``.
        """
        mgr = FleetAuraManager()
        ship_a = _mock_ship(
            name="A",
            abilities=[("ToHitAttackModifier", 3.0, AbilityScope.FLEET, "alpha")],
        )
        ship_b = _mock_ship(
            name="B",
            abilities=[("ToHitAttackModifier", 5.0, AbilityScope.FLEET, "alpha")],
        )
        ship_c = _mock_ship(
            name="C",
            abilities=[("ToHitAttackModifier", 2.0, AbilityScope.FLEET, "beta")],
        )

        mgr.initialize([ship_a, ship_b, ship_c])

        # MAX(3, 5) = 5; 5 + 2 = 7 — same team bonus on all participants.
        assert ship_a.fleet_attack_bonus == 7.0
        assert ship_b.fleet_attack_bonus == 7.0
        assert ship_c.fleet_attack_bonus == 7.0
