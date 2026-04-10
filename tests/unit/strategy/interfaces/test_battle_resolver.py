"""
Tests for IBattleResolver interface and BattleResult DTO.

PROJ-11 Phase 4: Interface Contracts - Tests written BEFORE implementation (TDD).
"""
import pytest
from dataclasses import dataclass
from unittest.mock import MagicMock


# =============================================================================
# BattleResult DTO Tests
# =============================================================================


class TestBattleResult:
    """Test BattleResult data transfer object."""

    def test_battle_result_has_winner_field(self):
        """BattleResult should have winner field (0, 1, or None for draw)."""
        from game.strategy.interfaces.battle_resolver import BattleResult
        result = BattleResult(winner=0, tick_count=100, team0_survivors=[], team1_survivors=[])
        assert result.winner == 0

    def test_battle_result_has_tick_count(self):
        """BattleResult should have tick_count field."""
        from game.strategy.interfaces.battle_resolver import BattleResult
        result = BattleResult(winner=1, tick_count=250, team0_survivors=[], team1_survivors=[])
        assert result.tick_count == 250

    def test_battle_result_has_team_survivors(self):
        """BattleResult should have team0_survivors and team1_survivors lists."""
        from game.strategy.interfaces.battle_resolver import BattleResult

        survivor1 = MagicMock()
        survivor2 = MagicMock()

        result = BattleResult(
            winner=0,
            tick_count=100,
            team0_survivors=[survivor1],
            team1_survivors=[survivor2]
        )

        assert len(result.team0_survivors) == 1
        assert len(result.team1_survivors) == 1
        assert result.team0_survivors[0] is survivor1
        assert result.team1_survivors[0] is survivor2

    def test_battle_result_none_winner_for_draw(self):
        """BattleResult winner can be None for a draw."""
        from game.strategy.interfaces.battle_resolver import BattleResult
        result = BattleResult(winner=None, tick_count=1000, team0_survivors=[], team1_survivors=[])
        assert result.winner is None


# =============================================================================
# IBattleResolver Interface Tests
# =============================================================================


class TestIBattleResolverInterface:
    """Test IBattleResolver abstract base class interface contract."""

    def test_concrete_implementation_must_implement_resolve_battle(self):
        """Concrete implementation must implement resolve_battle."""
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class IncompleteResolver(IBattleResolver):
            pass

        with pytest.raises(TypeError):
            IncompleteResolver()

    def test_concrete_implementation_works(self):
        """Concrete implementation with resolve_battle should work."""
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class MockResolver(IBattleResolver):
            def resolve_battle(self, fleet1, fleet2, seed=None):
                return BattleResult(
                    winner=0,
                    tick_count=100,
                    team0_survivors=[],
                    team1_survivors=[]
                )

        resolver = MockResolver()
        assert resolver is not None

    def test_resolve_battle_accepts_two_fleets_and_optional_seed(self):
        """resolve_battle should accept two fleets and optional seed parameter."""
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class TestResolver(IBattleResolver):
            def resolve_battle(self, fleet1, fleet2, seed=None):
                self.last_fleet1 = fleet1
                self.last_fleet2 = fleet2
                self.last_seed = seed
                return BattleResult(winner=0, tick_count=0, team0_survivors=[], team1_survivors=[])

        resolver = TestResolver()
        mock_fleet1 = MagicMock()
        mock_fleet2 = MagicMock()

        # Test without seed
        resolver.resolve_battle(mock_fleet1, mock_fleet2)
        assert resolver.last_fleet1 is mock_fleet1
        assert resolver.last_fleet2 is mock_fleet2
        assert resolver.last_seed is None

        # Test with seed
        resolver.resolve_battle(mock_fleet1, mock_fleet2, seed=42)
        assert resolver.last_seed == 42

    def test_resolve_battle_returns_battle_result(self):
        """resolve_battle should return a BattleResult."""
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class TestResolver(IBattleResolver):
            def resolve_battle(self, fleet1, fleet2, seed=None):
                return BattleResult(winner=1, tick_count=150, team0_survivors=[], team1_survivors=[])

        resolver = TestResolver()
        result = resolver.resolve_battle(MagicMock(), MagicMock())

        assert isinstance(result, BattleResult)
        assert result.winner == 1
        assert result.tick_count == 150


