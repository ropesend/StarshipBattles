"""
Unit tests for ConflictResolutionEngine battle resolver integration.

Tests battle resolver injection, result handling, and public API.
"""

import pytest
from unittest.mock import MagicMock

from game.strategy.data.hex_math import HexCoord


class TestBattleResolverIntegration:
    """Tests for battle resolver injection and usage."""

    def test_resolve_combat_simulated_uses_injected_resolver(self):
        """_resolve_combat_simulated should use injected resolver."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        call_count = 0
        last_fleets = []

        class TrackingResolver(IBattleResolver):
            def resolve_battle(self, fleet1, fleet2, seed=None, registries=None):
                nonlocal call_count, last_fleets
                call_count += 1
                last_fleets = [fleet1, fleet2]
                return BattleResult(
                    winner=0,
                    tick_count=100,
                    team0_survivors=[],
                    team1_survivors=[]
                )

        resolver = TrackingResolver()
        engine = ConflictResolutionEngine(battle_resolver=resolver)

        fleet1 = MagicMock()
        fleet1.id = 1
        fleet1.has_ship_instances.return_value = True

        fleet2 = MagicMock()
        fleet2.id = 2
        fleet2.has_ship_instances.return_value = True

        result = engine._resolve_combat_simulated(fleet1, fleet2)

        assert call_count == 1
        assert fleet1 in last_fleets
        assert fleet2 in last_fleets
        assert result == fleet1  # Winner was team 0 (fleet1)

    def test_mock_resolver_enables_unit_testing(self):
        """Mock resolver allows unit testing without simulation."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class AlwaysFleet1WinsResolver(IBattleResolver):
            def resolve_battle(self, fleet1, fleet2, seed=None, registries=None):
                return BattleResult(
                    winner=0,  # Team 0 (fleet1) wins
                    tick_count=50,
                    team0_survivors=[MagicMock()],
                    team1_survivors=[]
                )

        engine = ConflictResolutionEngine(battle_resolver=AlwaysFleet1WinsResolver())

        fleet1 = MagicMock()
        fleet1.id = 1
        fleet1.has_ship_instances.return_value = True
        fleet1.get_ship_instances.return_value = [MagicMock()]
        fleet1.ships = [MagicMock()]
        fleet1.update_from_battle_results = MagicMock()

        fleet2 = MagicMock()
        fleet2.id = 2
        fleet2.has_ship_instances.return_value = True
        fleet2.get_ship_instances.return_value = [MagicMock()]
        fleet2.ships = [MagicMock()]
        fleet2.update_from_battle_results = MagicMock()

        winner = engine._resolve_combat_simulated(fleet1, fleet2)

        assert winner == fleet1

    def test_battle_results_applied_to_fleets(self):
        """Battle results should be applied to fleet ship states."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        survivor0 = MagicMock()
        survivor1 = MagicMock()

        class ResultResolver(IBattleResolver):
            def resolve_battle(self, fleet1, fleet2, seed=None, registries=None):
                return BattleResult(
                    winner=0,
                    tick_count=100,
                    team0_survivors=[survivor0],
                    team1_survivors=[survivor1]
                )

        engine = ConflictResolutionEngine(battle_resolver=ResultResolver())

        fleet1 = MagicMock()
        fleet1.id = 1
        fleet1.has_ship_instances.return_value = True
        fleet1.update_from_battle_results = MagicMock()

        fleet2 = MagicMock()
        fleet2.id = 2
        fleet2.has_ship_instances.return_value = True
        fleet2.update_from_battle_results = MagicMock()

        engine._resolve_combat_simulated(fleet1, fleet2)

        # Verify fleet.update_from_battle_results was called with survivors
        fleet1.update_from_battle_results.assert_called_once_with([survivor0])
        fleet2.update_from_battle_results.assert_called_once_with([survivor1])

    def test_draw_returns_fleet_with_more_survivors(self):
        """Draw (winner=None) returns fleet with more survivors."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class DrawResolver(IBattleResolver):
            def resolve_battle(self, fleet1, fleet2, seed=None, registries=None):
                return BattleResult(
                    winner=None,  # Draw
                    tick_count=1000,
                    team0_survivors=[MagicMock(), MagicMock()],  # 2 survivors
                    team1_survivors=[MagicMock()]  # 1 survivor
                )

        engine = ConflictResolutionEngine(battle_resolver=DrawResolver())

        fleet1 = MagicMock()
        fleet1.id = 1
        fleet1.has_ship_instances.return_value = True
        fleet1.update_from_battle_results = MagicMock()

        fleet2 = MagicMock()
        fleet2.id = 2
        fleet2.has_ship_instances.return_value = True
        fleet2.update_from_battle_results = MagicMock()

        winner = engine._resolve_combat_simulated(fleet1, fleet2)

        # Fleet with more survivors wins on draw
        assert winner == fleet1

    def test_seed_passed_to_resolver(self):
        """Battle seed should be passed to resolver."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        received_seed = None

        class SeedCapturingResolver(IBattleResolver):
            def resolve_battle(self, fleet1, fleet2, seed=None, registries=None):
                nonlocal received_seed
                received_seed = seed
                return BattleResult(
                    winner=0,
                    tick_count=0,
                    team0_survivors=[],
                    team1_survivors=[]
                )

        engine = ConflictResolutionEngine(battle_resolver=SeedCapturingResolver())

        fleet1 = MagicMock()
        fleet1.id = 1
        fleet1.has_ship_instances.return_value = True

        fleet2 = MagicMock()
        fleet2.id = 2
        fleet2.has_ship_instances.return_value = True

        engine._resolve_combat_simulated(fleet1, fleet2)

        # The engine uses _generate_battle_seed() internally
        assert received_seed is not None
        assert isinstance(received_seed, int)


class TestResolveAllConflicts:
    """Tests for the public resolve_all_conflicts method."""

    def test_resolve_all_conflicts_returns_conflict_result(self):
        """resolve_all_conflicts returns a ConflictResult."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine, ConflictResult

        engine = ConflictResolutionEngine()

        empire = MagicMock()
        empire.id = 0
        empire.fleets = []

        result = engine.resolve_all_conflicts([empire])

        assert isinstance(result, ConflictResult)

    def test_resolve_all_conflicts_tracks_combats(self):
        """resolve_all_conflicts tracks number of combats."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class QuickResolver(IBattleResolver):
            def resolve_battle(self, fleet1, fleet2, seed=None, registries=None):
                return BattleResult(winner=0, tick_count=10, team0_survivors=[], team1_survivors=[])

        engine = ConflictResolutionEngine(battle_resolver=QuickResolver())

        empire1 = MagicMock()
        empire1.id = 0
        empire2 = MagicMock()
        empire2.id = 1

        fleet1 = MagicMock()
        fleet1.id = 1
        fleet1.location = HexCoord(5, 5)
        fleet1.owner_id = 0
        fleet1.ships = [MagicMock()]
        fleet1.update_from_battle_results = MagicMock()

        fleet2 = MagicMock()
        fleet2.id = 2
        fleet2.location = HexCoord(5, 5)
        fleet2.owner_id = 1
        fleet2.ships = [MagicMock()]
        fleet2.update_from_battle_results = MagicMock()

        empire1.fleets = [fleet1]
        empire2.fleets = [fleet2]

        result = engine.resolve_all_conflicts([empire1, empire2])

        assert result.combats_resolved >= 1

    def test_resolve_all_conflicts_tracks_destroyed_fleets(self):
        """resolve_all_conflicts tracks destroyed fleet IDs."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        # Resolver where the first fleet passed always wins (winner=0)
        class FirstFleetWinsResolver(IBattleResolver):
            def resolve_battle(self, fleet1, fleet2, seed=None, registries=None):
                return BattleResult(winner=0, tick_count=10, team0_survivors=[MagicMock()], team1_survivors=[])

        engine = ConflictResolutionEngine(battle_resolver=FirstFleetWinsResolver())

        empire1 = MagicMock()
        empire1.id = 0
        empire1.remove_fleet = MagicMock()

        empire2 = MagicMock()
        empire2.id = 1
        empire2.remove_fleet = MagicMock()

        fleet1 = MagicMock()
        fleet1.id = 1
        fleet1.location = HexCoord(5, 5)
        fleet1.owner_id = 0
        fleet1.ships = [MagicMock()]
        fleet1.update_from_battle_results = MagicMock()

        fleet2 = MagicMock()
        fleet2.id = 2
        fleet2.location = HexCoord(5, 5)
        fleet2.owner_id = 1
        fleet2.ships = [MagicMock()]
        fleet2.update_from_battle_results = MagicMock()

        empire1.fleets = [fleet1]
        empire2.fleets = [fleet2]

        result = engine.resolve_all_conflicts([empire1, empire2])

        # Exactly one fleet should be destroyed (the loser)
        # Due to random.sample(), either fleet could be picked first
        assert len(result.fleets_destroyed) == 1
        assert result.fleets_destroyed[0] in [1, 2]

    def test_no_conflicts_returns_zero_combats(self):
        """No conflicts returns zero combats resolved."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine

        engine = ConflictResolutionEngine()

        empire = MagicMock()
        empire.id = 0

        fleet = MagicMock()
        fleet.location = HexCoord(0, 0)
        fleet.owner_id = 0

        empire.fleets = [fleet]

        result = engine.resolve_all_conflicts([empire])

        assert result.combats_resolved == 0
        assert result.fleets_destroyed == []


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
