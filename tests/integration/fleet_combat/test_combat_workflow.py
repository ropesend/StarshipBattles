"""
Integration tests for fleet combat workflows.

Tests complete battle workflow, determinism, damage tracking, and fleet scale combat.
"""

import pytest

from game.simulation.battle_controller import (
    BattleController,
    BattleConfig,
    BattleMode,
    create_manual_battle,
    create_hypothetical_battle,
)
from game.simulation.battle_state import ShipState
from tests.fixtures.ships import create_test_ship


class TestFleetCombatWorkflow:
    """Integration tests for complete fleet combat workflows."""

    def test_battle_controller_full_workflow(self, two_ship_teams):
        """Test complete battle workflow: configure -> add ships -> start -> run."""
        team1, team2 = two_ship_teams

        # Create controller
        controller = BattleController()

        # Configure battle
        config = BattleConfig(
            mode=BattleMode.MANUAL,
            seed=12345,
            max_ticks=50000,
        )
        result = controller.configure(config)
        assert result.success, f"Configure failed: {result.errors}"

        # Add ships
        result = controller.add_ships(team1, team_id=0)
        assert result.success, f"Add team1 failed: {result.errors}"

        result = controller.add_ships(team2, team_id=1)
        assert result.success, f"Add team2 failed: {result.errors}"

        # Start battle
        result = controller.start()
        assert result.success, f"Start failed: {result.errors}"

        # Verify initial state
        assert len(controller.get_all_ships()) == 2
        assert controller.get_tick_count() == 0
        assert not controller.is_battle_over()

        # Run some ticks
        result = controller.run_ticks(100)
        assert result.success

        # Verify ticks ran
        assert controller.get_tick_count() == 100

    def test_battle_runs_headless_with_max_ticks(self, two_ship_teams):
        """Test that headless battle respects max_ticks and returns results."""
        team1, team2 = two_ship_teams

        # Create controller with short max_ticks
        controller = BattleController()
        config = BattleConfig(
            mode=BattleMode.MANUAL,
            seed=42,
            max_ticks=1000,  # Short limit for test
        )
        controller.configure(config)
        controller.add_ships(team1, 0)
        controller.add_ships(team2, 1)
        controller.start()

        # Run battle
        results = controller.run_headless()

        # Verify results structure
        assert results.tick_count <= 1000
        assert results.winner in (0, 1, -1)  # 0, 1, or draw
        assert results.seed == 42
        assert results.initial_state is not None
        assert results.final_state is not None

    def test_battle_with_deterministic_seed(self, two_ship_teams, fresh_registries):
        """Test that same seed produces same tick count (deterministic simulation)."""
        seed = 98765
        max_ticks = 500

        # Run battle twice with same seed
        tick_counts = []

        for _ in range(2):
            # Need fresh ships each time
            fresh_team1 = [
                create_test_ship(
                    name="Ship1",
                    x=500, y=400, team_id=0,
                    add_bridge=True, add_engine=True, add_weapons=2,
                    registries=fresh_registries,
                )
            ]
            fresh_team2 = [
                create_test_ship(
                    name="Ship2",
                    x=2000, y=400, team_id=1,
                    add_bridge=True, add_engine=True, add_weapons=2,
                    registries=fresh_registries,
                )
            ]

            controller = BattleController()
            config = BattleConfig(mode=BattleMode.MANUAL, seed=seed, max_ticks=max_ticks)
            controller.configure(config)
            controller.add_ships(fresh_team1, 0)
            controller.add_ships(fresh_team2, 1)
            controller.start()
            results = controller.run_headless()
            tick_counts.append(results.tick_count)

        # Same seed should produce same tick count (deterministic)
        assert tick_counts[0] == tick_counts[1]

    def test_create_hypothetical_battle_isolates_ships(self, two_ship_teams):
        """Test that hypothetical battles don't modify original ships."""
        team1, team2 = two_ship_teams

        # Record original HP
        original_hp1 = team1[0].hp
        original_hp2 = team2[0].hp

        # Run hypothetical battle with short limit
        controller = create_hypothetical_battle(team1, team2, seed=123)
        # Run just a few ticks to avoid long test
        controller.run_ticks(100)

        # Original ships should be unchanged
        assert team1[0].hp == original_hp1
        assert team2[0].hp == original_hp2


class TestDamageAccumulation:
    """Tests for damage accumulation mechanics."""

    def test_ships_track_damage_state(self, two_ship_teams):
        """Test that ships have damage tracking attributes."""
        team1, team2 = two_ship_teams

        controller = create_manual_battle(team1, team2, seed=111)

        # Verify ships have damage-related attributes
        for ship in controller.get_all_ships():
            assert hasattr(ship, 'hp')
            assert hasattr(ship, 'max_hp')
            assert hasattr(ship, 'is_alive')
            assert ship.hp > 0
            assert ship.is_alive is True

    def test_shield_components_provide_shield_stats(self, fresh_registries):
        """Test that shield components provide shield stats."""
        # Create ships with shields
        ship = create_test_ship(
            name="Shielded",
            x=500, y=400, team_id=0,
            add_bridge=True, add_engine=True, add_shields=2,
            registries=fresh_registries,
        )

        # Ship should have shield attributes
        assert hasattr(ship, 'max_shields')
        assert hasattr(ship, 'current_shields')

    def test_destroyed_ship_state_is_not_alive(self):
        """Test that ShipState for destroyed ships has is_alive=False."""
        # Create a ShipState representing destroyed ship
        state = ShipState(
            ship_id="test-id",
            name="Destroyed Ship",
            ship_class="Escort",
            theme_id="Federation",
            team_id=0,
            color=(255, 0, 0),
            ai_strategy="standard_ranged",
            position=(0, 0),
            velocity=(0, 0),
            angle=0,
            current_hp=0,
            max_hp=100,
            current_shields=0,
            max_shields=0,
            is_alive=False,
        )

        assert not state.is_alive


class TestFleetScaleCombat:
    """Tests for multi-ship fleet combat."""

    def test_fleet_vs_fleet_setup(self, fleet_battle_teams):
        """Test that multi-ship fleets can be configured."""
        team1, team2 = fleet_battle_teams

        controller = BattleController()
        config = BattleConfig(mode=BattleMode.MANUAL, seed=444, max_ticks=1000)
        controller.configure(config)
        controller.add_ships(team1, 0)
        controller.add_ships(team2, 1)
        controller.start()

        # Verify all ships added
        assert len(controller.get_all_ships()) == 6

        # Run some ticks
        controller.run_ticks(100)

        # Should be able to get results
        results = controller.get_results()
        assert results.tick_count == 100

    def test_fleet_combat_ships_support_each_other(self, fleet_battle_teams):
        """Test that fleet ships can engage different targets."""
        team1, team2 = fleet_battle_teams

        controller = create_manual_battle(team1, team2, seed=555)

        # Run some ticks to let AI engage
        controller.run_ticks(2000)

        # Check that ships have targets
        ships_with_targets = sum(
            1 for ship in controller.get_alive_ships()
            if ship.current_target is not None
        )

        # At least some ships should have targets
        assert ships_with_targets > 0

    def test_fleet_combat_preserves_team_integrity(self, fleet_battle_teams):
        """Test that team assignments are preserved during combat."""
        team1, team2 = fleet_battle_teams

        controller = create_manual_battle(team1, team2, seed=666)

        # Get initial team counts
        team0_count = len([s for s in controller.get_all_ships() if s.team_id == 0])
        team1_count = len([s for s in controller.get_all_ships() if s.team_id == 1])

        assert team0_count == 3
        assert team1_count == 3

        # Run some ticks
        controller.run_ticks(1000)

        # Team assignments should not change
        for ship in controller.get_all_ships():
            assert ship.team_id in (0, 1)


class TestBattleOutcome:
    """Tests for battle outcome determination."""

    def test_battle_results_have_winner_field(self, two_ship_teams):
        """Test that battle results include winner field."""
        team1, team2 = two_ship_teams

        controller = BattleController()
        config = BattleConfig(mode=BattleMode.MANUAL, seed=777, max_ticks=1000)
        controller.configure(config)
        controller.add_ships(team1, 0)
        controller.add_ships(team2, 1)
        controller.start()
        results = controller.run_headless()

        # Results should have winner field
        assert hasattr(results, 'winner')
        assert results.winner in (0, 1, -1, None)  # Valid winner values

    def test_battle_results_contain_ship_states(self, two_ship_teams):
        """Test that battle results contain ship state information."""
        team1, team2 = two_ship_teams

        controller = BattleController()
        config = BattleConfig(mode=BattleMode.MANUAL, seed=888, max_ticks=500)
        controller.configure(config)
        controller.add_ships(team1, 0)
        controller.add_ships(team2, 1)
        controller.start()
        results = controller.run_headless()

        # Results should have ship categorizations
        total_ships = (
            len(results.surviving_ships) +
            len(results.destroyed_ships) +
            len(results.escaped_ships)
        )

        # Should account for all ships
        assert total_ships == 2

    def test_battle_has_initial_and_final_state(self, two_ship_teams):
        """Test that battle captures initial and final states."""
        team1, team2 = two_ship_teams

        controller = BattleController()
        config = BattleConfig(mode=BattleMode.MANUAL, seed=999, max_ticks=500)
        controller.configure(config)
        controller.add_ships(team1, 0)
        controller.add_ships(team2, 1)
        controller.start()
        results = controller.run_headless()

        # Should have both states
        assert results.initial_state is not None
        assert results.final_state is not None

        # Initial state should have 0 ticks
        assert results.initial_state.tick_count == 0

        # Final state should have battle tick count
        assert results.final_state.tick_count == results.tick_count


class TestBattleEdgeCases:
    """Tests for edge cases in battle system."""

    def test_battle_with_one_ship_per_team(self, fresh_registries):
        """Test minimal battle: 1v1 setup works."""
        team1 = [create_test_ship(
            name="Solo1", x=500, y=400, team_id=0,
            add_bridge=True, add_engine=True, add_weapons=1,
            registries=fresh_registries,
        )]
        team2 = [create_test_ship(
            name="Solo2", x=2000, y=400, team_id=1,
            add_bridge=True, add_engine=True, add_weapons=1,
            registries=fresh_registries,
        )]

        controller = BattleController()
        config = BattleConfig(mode=BattleMode.MANUAL, seed=111, max_ticks=500)
        controller.configure(config)
        controller.add_ships(team1, 0)
        controller.add_ships(team2, 1)
        controller.start()

        # Battle should be able to run
        controller.run_ticks(100)
        assert controller.get_tick_count() == 100

    def test_battle_with_unarmed_ship(self, fresh_registries):
        """Test battle setup where one ship has no weapons."""
        team1 = [create_test_ship(
            name="Armed", x=500, y=400, team_id=0,
            add_bridge=True, add_engine=True, add_weapons=2,
            registries=fresh_registries,
        )]
        team2 = [create_test_ship(
            name="Unarmed", x=2000, y=400, team_id=1,
            add_bridge=True, add_engine=True, add_weapons=0,  # No weapons
            registries=fresh_registries,
        )]

        controller = BattleController()
        config = BattleConfig(mode=BattleMode.MANUAL, seed=222, max_ticks=500)
        controller.configure(config)
        controller.add_ships(team1, 0)
        controller.add_ships(team2, 1)
        controller.start()

        # Both ships should be in battle
        assert len(controller.get_all_ships()) == 2

        # Run some ticks
        controller.run_ticks(100)
        assert controller.get_tick_count() == 100

    def test_battle_max_ticks_limit(self, fresh_registries):
        """Test that battle respects max_ticks limit."""
        team1 = [create_test_ship(
            name="Ship1", x=500, y=400, team_id=0,
            add_bridge=True, add_engine=True, add_weapons=1, add_shields=3,
            registries=fresh_registries,
        )]
        team2 = [create_test_ship(
            name="Ship2", x=2000, y=400, team_id=1,
            add_bridge=True, add_engine=True, add_weapons=1, add_shields=3,
            registries=fresh_registries,
        )]

        # Create controller with very short max_ticks
        controller = BattleController()
        config = BattleConfig(
            mode=BattleMode.MANUAL,
            seed=333,
            max_ticks=100,  # Very short
        )
        controller.configure(config)
        controller.add_ships(team1, 0)
        controller.add_ships(team2, 1)
        controller.start()

        results = controller.run_headless()

        # Should stop at or before max_ticks
        assert results.tick_count <= 100

    def test_battle_controller_reset(self, two_ship_teams):
        """Test that controller can be reset and reused."""
        team1, team2 = two_ship_teams

        controller = BattleController()

        # First battle
        config = BattleConfig(mode=BattleMode.MANUAL, seed=444)
        controller.configure(config)
        controller.add_ships(team1, 0)
        controller.add_ships(team2, 1)
        controller.start()
        controller.run_ticks(100)

        # Reset
        controller.reset()

        # Verify reset state
        assert controller._is_configured is False
        assert controller._is_started is False
        assert len(controller._ship_id_map) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
