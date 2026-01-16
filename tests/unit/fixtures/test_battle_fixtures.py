"""
Tests for shared battle engine fixtures.

These fixtures provide consistent battle engine setup patterns for tests,
eliminating boilerplate and ensuring test isolation.
"""
import pytest
from unittest.mock import Mock

from game.simulation.systems.battle_engine import BattleEngine


class TestBattleEngineFixture:
    """Tests for battle_engine fixture."""

    def test_returns_battle_engine(self, battle_engine):
        """Returns a BattleEngine instance."""
        assert isinstance(battle_engine, BattleEngine)

    def test_has_empty_ships_list(self, battle_engine):
        """Engine starts with no ships."""
        assert battle_engine.ships == []

    def test_has_spatial_grid(self, battle_engine):
        """Engine has spatial grid initialized."""
        assert battle_engine.grid is not None

    def test_has_collision_system(self, battle_engine):
        """Engine has collision system."""
        assert battle_engine.collision_system is not None

    def test_has_projectile_manager(self, battle_engine):
        """Engine has projectile manager."""
        assert battle_engine.projectile_manager is not None

    def test_logging_disabled_by_default(self, battle_engine):
        """Logging is disabled by default to avoid side effects."""
        assert battle_engine.logger.enabled is False


class TestBattleEngineWithShipsFixture:
    """Tests for battle_engine_with_ships fixture."""

    def test_returns_battle_engine(self, battle_engine_with_ships):
        """Returns a BattleEngine instance."""
        assert isinstance(battle_engine_with_ships, BattleEngine)

    def test_has_ships(self, battle_engine_with_ships):
        """Engine has ships loaded."""
        assert len(battle_engine_with_ships.ships) >= 2

    def test_ships_on_different_teams(self, battle_engine_with_ships):
        """Ships are on different teams."""
        teams = set(ship.team_id for ship in battle_engine_with_ships.ships)
        assert len(teams) >= 2


class TestMockBattleEngineFixture:
    """Tests for mock_battle_engine fixture."""

    def test_is_mock(self, mock_battle_engine):
        """Returns a Mock object."""
        assert isinstance(mock_battle_engine, Mock)

    def test_has_tick_counter(self, mock_battle_engine):
        """Mock has tick_counter attribute."""
        assert hasattr(mock_battle_engine, 'tick_counter')
        assert mock_battle_engine.tick_counter == 0

    def test_has_ships_list(self, mock_battle_engine):
        """Mock has ships list."""
        assert hasattr(mock_battle_engine, 'ships')
        assert mock_battle_engine.ships == []

    def test_has_update_method(self, mock_battle_engine):
        """Mock has update method."""
        mock_battle_engine.update()  # Should not raise

    def test_has_is_battle_over_method(self, mock_battle_engine):
        """Mock has is_battle_over method."""
        result = mock_battle_engine.is_battle_over()
        assert result is False

    def test_has_start_method(self, mock_battle_engine):
        """Mock has start method."""
        mock_battle_engine.start()  # Should not raise


class TestMockBattleSceneFixture:
    """Tests for mock_battle_scene fixture."""

    def test_is_mock(self, mock_battle_scene):
        """Returns a Mock object."""
        assert isinstance(mock_battle_scene, Mock)

    def test_has_engine(self, mock_battle_scene):
        """Mock has engine attribute."""
        assert hasattr(mock_battle_scene, 'engine')
        assert mock_battle_scene.engine is not None

    def test_has_headless_mode(self, mock_battle_scene):
        """Mock has headless_mode attribute."""
        assert hasattr(mock_battle_scene, 'headless_mode')
        assert mock_battle_scene.headless_mode is False

    def test_has_sim_paused(self, mock_battle_scene):
        """Mock has sim_paused attribute."""
        assert hasattr(mock_battle_scene, 'sim_paused')
        assert mock_battle_scene.sim_paused is True


class TestBattleFactory:
    """Tests for battle factory functions."""

    def test_create_battle_engine(self):
        """Factory creates battle engine."""
        from tests.fixtures.battle import create_battle_engine
        engine = create_battle_engine()
        assert isinstance(engine, BattleEngine)
        assert engine.logger.enabled is False

    def test_create_battle_engine_with_logging(self):
        """Factory creates battle engine with logging enabled."""
        from tests.fixtures.battle import create_battle_engine
        engine = create_battle_engine(enable_logging=True)
        assert engine.logger.enabled is True
        # Clean up
        engine.logger.close()

    def test_create_battle_engine_with_ships(self):
        """Factory creates battle engine with ships."""
        from tests.fixtures.battle import create_battle_engine_with_ships
        engine = create_battle_engine_with_ships()
        assert isinstance(engine, BattleEngine)
        assert len(engine.ships) >= 2

    def test_create_mock_battle_engine(self):
        """Factory creates mock battle engine."""
        from tests.fixtures.battle import create_mock_battle_engine
        engine = create_mock_battle_engine()
        assert isinstance(engine, Mock)
        assert engine.tick_counter == 0
