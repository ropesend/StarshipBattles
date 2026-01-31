"""
Integration tests for BattleService and BattleEngine.

Tests service creation, ship management, adapter integration, and engine operations.
"""

import pytest

from game.simulation.services.battle_service import BattleService
from game.simulation.systems.battle_engine import BattleEngine
from tests.fixtures.battle import create_battle_engine, create_battle_engine_with_ships
from tests.fixtures.ships import create_test_ship


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

    def test_engine_fixture_provides_ready_battle(self, fresh_registries):
        """Test that battle_engine_with_ships fixture works."""
        engine = create_battle_engine_with_ships(team1_count=2, team2_count=2, registries=fresh_registries)

        assert len(engine.ships) == 4
        team0_ships = [s for s in engine.ships if s.team_id == 0]
        team1_ships = [s for s in engine.ships if s.team_id == 1]
        assert len(team0_ships) == 2
        assert len(team1_ships) == 2


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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
