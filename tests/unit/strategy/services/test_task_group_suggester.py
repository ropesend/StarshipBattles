"""
Unit tests for TaskGroupSuggester.

Phase 7: Auto-suggests fleet organization into TaskForces and Squadrons
based on ship design roles and capabilities.

TDD: Written before implementation.
"""

from unittest.mock import MagicMock


def _make_ship(name, role="line_combatant", mass=8000):
    """Create a mock ShipInstance with a design role."""
    ship = MagicMock()
    ship.name = name
    ship.instance_id = f"id_{name}"
    ship.effective_role = role
    ship.design_role = role
    ship.role_override = None
    ship.hull_class = "Cruiser"
    ship.is_combat_capable.return_value = True
    ship.get_calculated_stats.return_value = {"mass": mass}
    ship.design_data = {"ship_class": "Cruiser", "vehicle_type": "Ship"}
    return ship


# =============================================================================
# Basic Suggestion
# =============================================================================

class TestTaskGroupSuggesterBasic:
    """Tests for basic auto-suggestion logic."""

    def test_single_ship_gets_default_group(self):
        """A single ship gets placed in one task force."""
        from game.strategy.services.task_group_suggester import suggest_task_groups

        ships = [_make_ship("Solo")]
        result = suggest_task_groups(ships)

        assert len(result) >= 1
        # All ships should be accounted for
        total_ships = sum(
            len(tf.all_ships) for tf in result
        )
        assert total_ships == 1

    def test_empty_fleet_returns_empty(self):
        """No ships returns no task forces."""
        from game.strategy.services.task_group_suggester import suggest_task_groups

        result = suggest_task_groups([])
        assert result == []

    def test_all_ships_accounted_for(self):
        """Every input ship appears in exactly one group."""
        from game.strategy.services.task_group_suggester import suggest_task_groups

        ships = [
            _make_ship("LC1", "line_combatant", 32000),
            _make_ship("LC2", "line_combatant", 32000),
            _make_ship("FE1", "fleet_escort", 1000),
            _make_ship("FE2", "fleet_escort", 1000),
            _make_ship("CA1", "carrier", 64000),
        ]

        result = suggest_task_groups(ships)

        all_assigned = []
        for tf in result:
            all_assigned.extend(tf.all_ships)

        assigned_ids = {s.instance_id for s in all_assigned}
        input_ids = {s.instance_id for s in ships}
        assert assigned_ids == input_ids


# =============================================================================
# Role-Based Grouping
# =============================================================================

class TestRoleBasedGrouping:
    """Tests for grouping ships by their design roles."""

    def test_escorts_grouped_as_screen(self):
        """Fleet escorts are grouped into a screen squadron/task force."""
        from game.strategy.services.task_group_suggester import suggest_task_groups
        from game.strategy.data.fleet_hierarchy import BattleRole

        ships = [
            _make_ship("FE1", "fleet_escort", 1000),
            _make_ship("FE2", "fleet_escort", 1000),
            _make_ship("FE3", "fleet_escort", 1000),
        ]

        result = suggest_task_groups(ships)

        # Should have at least one group with SCREEN role
        screen_groups = [
            tf for tf in result if tf.battle_role == BattleRole.SCREEN
        ]
        assert len(screen_groups) >= 1

    def test_carriers_grouped_as_reserve(self):
        """Carriers are grouped into a reserve task force."""
        from game.strategy.services.task_group_suggester import suggest_task_groups
        from game.strategy.data.fleet_hierarchy import BattleRole

        ships = [
            _make_ship("Carrier1", "carrier", 64000),
            _make_ship("LC1", "line_combatant", 32000),
        ]

        result = suggest_task_groups(ships)

        # Should have a group with RESERVE role containing the carrier
        reserve_groups = [
            tf for tf in result if tf.battle_role == BattleRole.RESERVE
        ]
        assert len(reserve_groups) >= 1

        reserve_ships = []
        for tf in reserve_groups:
            reserve_ships.extend(tf.all_ships)
        carrier_ids = {s.instance_id for s in reserve_ships}
        assert "id_Carrier1" in carrier_ids

    def test_line_combatants_grouped_as_main_body(self):
        """Line combatants are grouped into main body."""
        from game.strategy.services.task_group_suggester import suggest_task_groups
        from game.strategy.data.fleet_hierarchy import BattleRole

        ships = [
            _make_ship("LC1", "line_combatant", 32000),
            _make_ship("LC2", "line_combatant", 32000),
        ]

        result = suggest_task_groups(ships)

        main_groups = [
            tf for tf in result if tf.battle_role == BattleRole.MAIN_BODY
        ]
        assert len(main_groups) >= 1

    def test_mixed_fleet_creates_multiple_groups(self):
        """A mixed fleet creates multiple task forces with appropriate roles."""
        from game.strategy.services.task_group_suggester import suggest_task_groups

        ships = [
            _make_ship("LC1", "line_combatant", 32000),
            _make_ship("LC2", "line_combatant", 32000),
            _make_ship("LC3", "line_combatant", 32000),
            _make_ship("FE1", "fleet_escort", 1000),
            _make_ship("FE2", "fleet_escort", 1000),
            _make_ship("CA1", "carrier", 64000),
            _make_ship("SS1", "support_ship", 16000),
        ]

        result = suggest_task_groups(ships)

        # Should have at least 2 task forces (combat + support/screen)
        assert len(result) >= 2

    def test_support_ships_grouped_separately(self):
        """Support ships get their own group."""
        from game.strategy.services.task_group_suggester import suggest_task_groups
        from game.strategy.data.fleet_hierarchy import BattleRole

        ships = [
            _make_ship("LC1", "line_combatant", 32000),
            _make_ship("SS1", "support_ship", 16000),
        ]

        result = suggest_task_groups(ships)

        # Support ship should be in RESERVE
        reserve_groups = [
            tf for tf in result if tf.battle_role == BattleRole.RESERVE
        ]
        reserve_ships = []
        for tf in reserve_groups:
            reserve_ships.extend(tf.all_ships)
        support_ids = {s.instance_id for s in reserve_ships}
        assert "id_SS1" in support_ids
