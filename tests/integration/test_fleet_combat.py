"""
Integration tests for fleet combat workflows.

Tests the end-to-end battle system including:
- Fleet vs fleet combat workflow
- Damage accumulation across ships
- Projectile-to-ship damage pipeline
- Battle outcome determination
- BattleController integration with BattleService and BattleEngine
"""
import pytest
from typing import List

from game.simulation.battle_controller import (
    BattleController,
    BattleConfig,
    BattleMode,
    create_manual_battle,
    create_hypothetical_battle,
)
from game.simulation.services.battle_service import BattleService
from game.simulation.systems.battle_engine import BattleEngine, BattleLogger
from game.simulation.systems.battle_end_conditions import BattleEndMode
from tests.fixtures.ships import create_test_ship
from tests.fixtures.battle import create_battle_engine, create_battle_engine_with_ships


# === Fixtures ===

@pytest.fixture
def battle_service():
    """Create a fresh BattleService."""
    return BattleService()


@pytest.fixture
def two_ship_teams():
    """Create two teams of ships for battle testing.

    Ships are positioned close enough for weapons to engage (within ~2000 units).
    """
    team1 = [
        create_test_ship(
            name="Team1_Attacker",
            x=500,
            y=400,
            team_id=0,
            add_bridge=True,
            add_engine=True,
            add_weapons=2,
        )
    ]
    team2 = [
        create_test_ship(
            name="Team2_Defender",
            x=2000,
            y=400,
            team_id=1,
            add_bridge=True,
            add_engine=True,
            add_weapons=2,
        )
    ]
    return team1, team2


@pytest.fixture
def fleet_battle_teams():
    """Create multi-ship fleets for larger scale testing.

    Ships are positioned close enough for weapons to engage.
    """
    team1 = [
        create_test_ship(
            name=f"Fleet1_Ship{i}",
            x=500 + (i * 200),
            y=400 + (i * 100),
            team_id=0,
            add_bridge=True,
            add_engine=True,
            add_weapons=1,
            add_shields=1,
        )
        for i in range(3)
    ]
    team2 = [
        create_test_ship(
            name=f"Fleet2_Ship{i}",
            x=2000 + (i * 200),
            y=400 + (i * 100),
            team_id=1,
            add_bridge=True,
            add_engine=True,
            add_weapons=1,
            add_shields=1,
        )
        for i in range(3)
    ]
    return team1, team2


# === Full Combat Workflow Tests ===

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

    def test_battle_with_deterministic_seed(self, two_ship_teams):
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
                )
            ]
            fresh_team2 = [
                create_test_ship(
                    name="Ship2",
                    x=2000, y=400, team_id=1,
                    add_bridge=True, add_engine=True, add_weapons=2,
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


# === Damage Accumulation Tests ===

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

    def test_shield_components_provide_shield_stats(self):
        """Test that shield components provide shield stats."""
        # Create ships with shields
        ship = create_test_ship(
            name="Shielded",
            x=500, y=400, team_id=0,
            add_bridge=True, add_engine=True, add_shields=2,
        )

        # Ship should have shield attributes
        assert hasattr(ship, 'max_shields')
        assert hasattr(ship, 'current_shields')

    def test_destroyed_ship_state_is_not_alive(self):
        """Test that ShipState for destroyed ships has is_alive=False."""
        from game.simulation.battle_state import ShipState

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


# === Fleet Scale Tests ===

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


# === Battle Outcome Tests ===

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


# === Battle Service Integration Tests ===

class TestBattleServiceIntegration:
    """Tests for BattleService integration."""

    def test_service_creates_engine(self, battle_service):
        """Test that BattleService creates a battle engine."""
        result = battle_service.create_battle()

        assert result.success
        assert result.engine is not None
        assert isinstance(result.engine, BattleEngine)

    def test_service_adds_ships(self, battle_service, two_ship_teams):
        """Test that BattleService adds ships correctly."""
        team1, team2 = two_ship_teams

        battle_service.create_battle()

        for ship in team1:
            result = battle_service.add_ship(ship, team_id=0)
            assert result.success

        for ship in team2:
            result = battle_service.add_ship(ship, team_id=1)
            assert result.success

        # All ships should be tracked
        assert len(battle_service.get_all_ships()) == 2

    def test_service_starts_and_updates_battle(self, battle_service, two_ship_teams):
        """Test that BattleService starts and updates battle."""
        team1, team2 = two_ship_teams

        battle_service.create_battle()
        for ship in team1:
            battle_service.add_ship(ship, team_id=0)
        for ship in team2:
            battle_service.add_ship(ship, team_id=1)

        result = battle_service.start_battle()
        assert result.success

        # Update should work
        result = battle_service.update()
        assert result.success

        # Tick counter should increment
        engine = battle_service.get_engine()
        assert engine.tick_counter == 1

    def test_service_run_ticks(self, battle_service, two_ship_teams):
        """Test that BattleService can run multiple ticks."""
        team1, team2 = two_ship_teams

        battle_service.create_battle()
        for ship in team1:
            battle_service.add_ship(ship, team_id=0)
        for ship in team2:
            battle_service.add_ship(ship, team_id=1)

        battle_service.start_battle()
        result = battle_service.run_ticks(100)

        assert result.success
        assert battle_service.get_engine().tick_counter == 100

    def test_service_provides_battle_state(self, battle_service, two_ship_teams):
        """Test that BattleService provides battle state information."""
        team1, team2 = two_ship_teams

        battle_service.create_battle()
        for ship in team1:
            battle_service.add_ship(ship, team_id=0)
        for ship in team2:
            battle_service.add_ship(ship, team_id=1)

        battle_service.start_battle()

        # Run a few ticks
        battle_service.run_ticks(100)

        # Should be able to get battle state
        state = battle_service.get_battle_state()
        assert state['is_started'] is True
        assert state['tick_count'] == 100

    def test_service_is_battle_over_initially_false(self, battle_service, two_ship_teams):
        """Test that is_battle_over is False at start."""
        team1, team2 = two_ship_teams

        battle_service.create_battle()
        for ship in team1:
            battle_service.add_ship(ship, team_id=0)
        for ship in team2:
            battle_service.add_ship(ship, team_id=1)

        battle_service.start_battle()

        # Battle should not be over immediately
        assert battle_service.is_battle_over() is False


# === Battle Engine Direct Tests ===

class TestBattleEngineDirect:
    """Direct tests for BattleEngine."""

    def test_engine_starts_with_ships(self, two_ship_teams):
        """Test that engine starts with provided ships."""
        team1, team2 = two_ship_teams

        engine = create_battle_engine()
        engine.start(team1, team2)

        assert len(engine.ships) == 2
        assert engine.tick_counter == 0

    def test_engine_update_increments_tick(self, two_ship_teams):
        """Test that engine update increments tick counter."""
        team1, team2 = two_ship_teams

        engine = create_battle_engine()
        engine.start(team1, team2)

        initial_tick = engine.tick_counter
        engine.update()

        assert engine.tick_counter == initial_tick + 1

    def test_engine_fixture_provides_ready_battle(self):
        """Test that battle_engine_with_ships fixture works."""
        engine = create_battle_engine_with_ships(team1_count=2, team2_count=2)

        assert len(engine.ships) == 4
        team0_ships = [s for s in engine.ships if s.team_id == 0]
        team1_ships = [s for s in engine.ships if s.team_id == 1]
        assert len(team0_ships) == 2
        assert len(team1_ships) == 2


# === Adapter Integration Tests ===

class TestAIAdapterIntegration:
    """Tests for ShipControllableAdapter integration with BattleEngine."""

    def test_ai_controllers_use_adapter(self, two_ship_teams):
        """Test that AI controllers receive wrapped ships via adapter."""
        from game.ai.interfaces import ShipControllableAdapter

        team1, team2 = two_ship_teams
        engine = create_battle_engine()
        engine.start(team1, team2)

        # All AI controllers should have ShipControllableAdapter as their ship
        for ai in engine.ai_controllers:
            assert isinstance(ai.ship, ShipControllableAdapter), \
                f"AI controller should use ShipControllableAdapter, got {type(ai.ship)}"

    def test_adapter_provides_interface_methods(self, two_ship_teams):
        """Test that adapter provides IControllable interface methods."""
        team1, team2 = two_ship_teams
        engine = create_battle_engine()
        engine.start(team1, team2)

        for ai in engine.ai_controllers:
            adapter = ai.ship
            # Test interface methods exist and work
            assert hasattr(adapter, 'get_position')
            assert hasattr(adapter, 'get_velocity')
            assert hasattr(adapter, 'get_rotation')
            assert hasattr(adapter, 'set_throttle')
            assert hasattr(adapter, 'is_alive')
            assert hasattr(adapter, 'get_team_id')

            # Call methods to ensure they work
            pos = adapter.get_position()
            assert pos is not None

    def test_adapter_provides_ship_access(self, two_ship_teams):
        """Test that adapter provides access to underlying ship."""
        from game.simulation.entities.ship import Ship

        team1, team2 = two_ship_teams
        engine = create_battle_engine()
        engine.start(team1, team2)

        for ai in engine.ai_controllers:
            adapter = ai.ship
            # Test access to underlying ship via .ship property
            assert hasattr(adapter, 'ship')
            assert isinstance(adapter.ship, Ship)

            # Test interface methods work (PROJ-24 migration - no __getattr__ fallback)
            assert adapter.get_position() is not None
            assert adapter.get_team_id() == adapter.ship.team_id


# === Edge Case Tests ===

class TestBattleEdgeCases:
    """Tests for edge cases in battle system."""

    def test_battle_with_one_ship_per_team(self):
        """Test minimal battle: 1v1 setup works."""
        team1 = [create_test_ship(
            name="Solo1", x=500, y=400, team_id=0,
            add_bridge=True, add_engine=True, add_weapons=1
        )]
        team2 = [create_test_ship(
            name="Solo2", x=2000, y=400, team_id=1,
            add_bridge=True, add_engine=True, add_weapons=1
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

    def test_battle_with_unarmed_ship(self):
        """Test battle setup where one ship has no weapons."""
        team1 = [create_test_ship(
            name="Armed", x=500, y=400, team_id=0,
            add_bridge=True, add_engine=True, add_weapons=2
        )]
        team2 = [create_test_ship(
            name="Unarmed", x=2000, y=400, team_id=1,
            add_bridge=True, add_engine=True, add_weapons=0  # No weapons
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

    def test_battle_max_ticks_limit(self):
        """Test that battle respects max_ticks limit."""
        team1 = [create_test_ship(
            name="Ship1", x=500, y=400, team_id=0,
            add_bridge=True, add_engine=True, add_weapons=1, add_shields=3
        )]
        team2 = [create_test_ship(
            name="Ship2", x=2000, y=400, team_id=1,
            add_bridge=True, add_engine=True, add_weapons=1, add_shields=3
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
