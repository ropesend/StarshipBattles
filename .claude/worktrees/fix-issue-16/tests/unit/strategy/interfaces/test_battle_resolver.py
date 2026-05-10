"""
Tests for IBattleResolver interface and BattleResult DTO.

PROJ-11 Phase 4: Interface Contracts.
PROJ-275 Phase 7: signature widened to N fleets; `BattleResult` carries
`team_survivors: Dict[int, List[IPostBattleShip]]` instead of the
legacy `team0_survivors`/`team1_survivors` pair.
"""
import pytest
from unittest.mock import MagicMock


# =============================================================================
# BattleResult DTO Tests
# =============================================================================


class TestBattleResult:
    """Test BattleResult data transfer object."""

    def test_battle_result_has_winner_field(self):
        from game.strategy.interfaces.battle_resolver import BattleResult
        result = BattleResult(winner=0, tick_count=100, team_survivors={0: [], 1: []})
        assert result.winner == 0

    def test_battle_result_has_tick_count(self):
        from game.strategy.interfaces.battle_resolver import BattleResult
        result = BattleResult(winner=1, tick_count=250, team_survivors={0: [], 1: []})
        assert result.tick_count == 250

    def test_battle_result_has_team_survivors(self):
        """BattleResult carries a `team_survivors` mapping keyed by team_id."""
        from game.strategy.interfaces.battle_resolver import BattleResult

        survivor1 = MagicMock()
        survivor2 = MagicMock()

        result = BattleResult(
            winner=0,
            tick_count=100,
            team_survivors={0: [survivor1], 1: [survivor2]},
        )

        assert len(result.team_survivors[0]) == 1
        assert len(result.team_survivors[1]) == 1
        assert result.team_survivors[0][0] is survivor1
        assert result.team_survivors[1][0] is survivor2

    def test_battle_result_supports_three_team_survivors(self):
        """PROJ-275 Phase 7 — `team_survivors` accepts any number of teams."""
        from game.strategy.interfaces.battle_resolver import BattleResult

        result = BattleResult(
            winner=2,
            tick_count=200,
            team_survivors={0: [], 1: [], 2: [MagicMock(), MagicMock()]},
        )
        assert set(result.team_survivors.keys()) == {0, 1, 2}
        assert len(result.team_survivors[2]) == 2

    def test_battle_result_none_winner_for_draw(self):
        from game.strategy.interfaces.battle_resolver import BattleResult
        result = BattleResult(
            winner=None, tick_count=1000, team_survivors={0: [], 1: []}
        )
        assert result.winner is None


# =============================================================================
# IBattleResolver Interface Tests
# =============================================================================


class TestIBattleResolverInterface:
    """Test IBattleResolver abstract base class interface contract."""

    def test_concrete_implementation_must_implement_resolve_battle(self):
        from game.strategy.interfaces.battle_resolver import IBattleResolver

        class IncompleteResolver(IBattleResolver):
            pass

        with pytest.raises(TypeError):
            IncompleteResolver()

    def test_concrete_implementation_works(self):
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class MockResolver(IBattleResolver):
            def resolve_battle(self, fleets, modifiers=None, seed=None,
                               registries=None, environmental_effects=None):
                return BattleResult(
                    winner=0, tick_count=100,
                    team_survivors={0: [], 1: []},
                )

        resolver = MockResolver()
        assert resolver is not None

    def test_resolve_battle_accepts_fleets_sequence_and_optional_seed(self):
        """resolve_battle takes a fleets sequence, optional modifiers + seed."""
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class TestResolver(IBattleResolver):
            def resolve_battle(self, fleets, modifiers=None, seed=None,
                               registries=None, environmental_effects=None):
                self.last_fleets = list(fleets)
                self.last_seed = seed
                return BattleResult(
                    winner=0, tick_count=0,
                    team_survivors={i: [] for i in range(len(self.last_fleets))},
                )

        resolver = TestResolver()
        f1, f2 = MagicMock(), MagicMock()

        resolver.resolve_battle([f1, f2])
        assert resolver.last_fleets == [f1, f2]
        assert resolver.last_seed is None

        resolver.resolve_battle([f1, f2], seed=42)
        assert resolver.last_seed == 42

    def test_resolve_battle_returns_battle_result(self):
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class TestResolver(IBattleResolver):
            def resolve_battle(self, fleets, modifiers=None, seed=None,
                               registries=None, environmental_effects=None):
                return BattleResult(
                    winner=1, tick_count=150,
                    team_survivors={0: [], 1: []},
                )

        resolver = TestResolver()
        result = resolver.resolve_battle([MagicMock(), MagicMock()])

        assert isinstance(result, BattleResult)
        assert result.winner == 1
        assert result.tick_count == 150
