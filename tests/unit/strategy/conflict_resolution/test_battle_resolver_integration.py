"""
Unit tests for ConflictResolutionEngine ↔ IBattleResolver integration.

PROJ-275 Phase 7: the legacy sequential 2-fleet decomposition was
replaced with a single N-team `_resolve_combat_at_hex` call. Tests
that exercised `_resolve_combat`/`_resolve_combat_simulated` (now
removed) have been migrated to drive `_resolve_combat_at_hex` with
synthetic occupants directly.
"""

import pytest
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord


def _empire(empire_id):
    emp = MagicMock()
    emp.id = empire_id
    emp.fleets = []
    emp.remove_fleet = MagicMock()
    return emp


def _fleet(fleet_id, owner_id, location=None):
    f = MagicMock()
    f.id = fleet_id
    f.owner_id = owner_id
    f.location = location or HexCoord(0, 0)
    f.ships = [MagicMock()]
    return f


class TestBattleResolverIntegration:
    """Tests for battle resolver injection and usage in single N-team mode."""

    def test_resolve_combat_at_hex_uses_injected_resolver(self):
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        calls = []

        class TrackingResolver(IBattleResolver):
            def resolve_battle(self, fleets, modifiers=None, seed=None,
                               registries=None, environmental_effects=None,
                               empires=None):
                calls.append(list(fleets))
                return BattleResult(
                    winner=0, tick_count=100,
                    team_survivors={i: [] for i in range(len(list(fleets)))},
                )

        resolver = TrackingResolver()
        engine = ConflictResolutionEngine(battle_resolver=resolver)

        emp1 = _empire(0)
        emp2 = _empire(1)
        f1 = _fleet(1, owner_id=0)
        f2 = _fleet(2, owner_id=1)
        emp1.fleets.append(f1)
        emp2.fleets.append(f2)

        engine._empires = [emp1, emp2]
        engine._resolve_combat_at_hex([(emp1, f1), (emp2, f2)])

        assert len(calls) == 1
        assert f1 in calls[0] and f2 in calls[0]

    def test_mock_resolver_enables_unit_testing(self):
        """BUG-126: when the (mock) resolver wipes the loser's fleet to
        zero ships, the engine reports the destroyed fleet id. The
        strategy engine no longer calls `empire.remove_fleet` itself —
        that is the `PostBattleHook`'s job."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class AlwaysTeam0WinsResolver(IBattleResolver):
            def resolve_battle(self, fleets, modifiers=None, seed=None,
                               registries=None, environmental_effects=None,
                               empires=None):
                fleet_list = list(fleets)
                # Simulate the PostBattleHook wiping the loser fleet.
                for f in fleet_list[1:]:
                    f.ships = []
                return BattleResult(
                    winner=0, tick_count=50,
                    team_survivors={
                        0: [MagicMock()],
                        **{i: [] for i in range(1, len(fleet_list))},
                    },
                )

        engine = ConflictResolutionEngine(battle_resolver=AlwaysTeam0WinsResolver())

        emp1 = _empire(0); emp2 = _empire(1)
        f1 = _fleet(1, owner_id=0); f2 = _fleet(2, owner_id=1)
        emp1.fleets.append(f1); emp2.fleets.append(f2)
        engine._empires = [emp1, emp2]
        engine._combats_resolved = 0
        engine._fleets_destroyed = []

        engine._resolve_combat_at_hex([(emp1, f1), (emp2, f2)])

        # Strategy engine no longer prunes — that is the hook's job.
        emp2.remove_fleet.assert_not_called()
        # But the engine reports the wiped fleet for audit/event payload.
        assert engine._fleets_destroyed == [2]

    def test_battle_results_not_applied_via_adapter(self):
        """PROJ-269 Phase 6: ConflictResolutionEngine no longer calls
        `fleet.battle.update_from_battle_results` — fleet updates flow
        via the compiler-attached `PostBattleHook` inside `run_battle`.
        """
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class ResultResolver(IBattleResolver):
            def resolve_battle(self, fleets, modifiers=None, seed=None,
                               registries=None, environmental_effects=None,
                               empires=None):
                return BattleResult(
                    winner=0, tick_count=100,
                    team_survivors={0: [MagicMock()], 1: [MagicMock()]},
                )

        engine = ConflictResolutionEngine(battle_resolver=ResultResolver())
        emp1 = _empire(0); emp2 = _empire(1)
        f1 = _fleet(1, owner_id=0); f2 = _fleet(2, owner_id=1)
        f1.battle = MagicMock(spec=[])  # Adapter exposes NO update method
        f2.battle = MagicMock(spec=[])
        emp1.fleets.append(f1); emp2.fleets.append(f2)
        engine._empires = [emp1, emp2]
        engine._combats_resolved = 0
        engine._fleets_destroyed = []

        # Would raise AttributeError if engine called fleet.battle.*.
        engine._resolve_combat_at_hex([(emp1, f1), (emp2, f2)])

    def test_draw_keeps_both_fleets(self):
        """BUG-126: draws no longer destroy a fleet. The legacy
        survivor-count tiebreaker is gone — both fleets remain in
        their empires when `BattleResult.winner is None` and both
        sides retain ships."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class DrawResolver(IBattleResolver):
            def resolve_battle(self, fleets, modifiers=None, seed=None,
                               registries=None, environmental_effects=None,
                               empires=None):
                return BattleResult(
                    winner=None, tick_count=1000,
                    team_survivors={0: [MagicMock(), MagicMock()], 1: [MagicMock()]},
                )

        engine = ConflictResolutionEngine(battle_resolver=DrawResolver())
        emp1 = _empire(0); emp2 = _empire(1)
        f1 = _fleet(1, owner_id=0); f2 = _fleet(2, owner_id=1)
        emp1.fleets.append(f1); emp2.fleets.append(f2)
        engine._empires = [emp1, emp2]
        engine._combats_resolved = 0
        engine._fleets_destroyed = []

        engine._resolve_combat_at_hex([(emp1, f1), (emp2, f2)])

        # Both fleets retained their ships — neither is destroyed.
        emp1.remove_fleet.assert_not_called()
        emp2.remove_fleet.assert_not_called()
        assert engine._fleets_destroyed == []

    def test_seed_passed_to_resolver(self):
        """The engine's deterministic seed counter feeds the resolver."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        received_seed = None

        class SeedCapturingResolver(IBattleResolver):
            def resolve_battle(self, fleets, modifiers=None, seed=None,
                               registries=None, environmental_effects=None,
                               empires=None):
                nonlocal received_seed
                received_seed = seed
                return BattleResult(
                    winner=0, tick_count=0,
                    team_survivors={i: [] for i in range(len(list(fleets)))},
                )

        engine = ConflictResolutionEngine(battle_resolver=SeedCapturingResolver())
        emp1 = _empire(0); emp2 = _empire(1)
        f1 = _fleet(1, owner_id=0); f2 = _fleet(2, owner_id=1)
        emp1.fleets.append(f1); emp2.fleets.append(f2)
        engine._empires = [emp1, emp2]
        engine._combats_resolved = 0
        engine._fleets_destroyed = []

        engine._resolve_combat_at_hex([(emp1, f1), (emp2, f2)])

        assert received_seed is not None
        assert isinstance(received_seed, int)


class TestResolveAllConflicts:
    """Tests for the public resolve_all_conflicts method."""

    def test_resolve_all_conflicts_returns_conflict_result(self):
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine, ConflictResult

        engine = ConflictResolutionEngine(battle_resolver=MagicMock())

        empire = MagicMock()
        empire.id = 0
        empire.fleets = []

        result = engine.resolve_all_conflicts([empire])

        assert isinstance(result, ConflictResult)

    def test_resolve_all_conflicts_tracks_combats(self):
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class QuickResolver(IBattleResolver):
            def resolve_battle(self, fleets, modifiers=None, seed=None,
                               registries=None, environmental_effects=None,
                               empires=None):
                return BattleResult(
                    winner=0, tick_count=10,
                    team_survivors={i: ([MagicMock()] if i == 0 else []) for i in range(len(list(fleets)))},
                )

        engine = ConflictResolutionEngine(battle_resolver=QuickResolver())

        emp1 = _empire(0); emp2 = _empire(1)
        f1 = _fleet(1, owner_id=0, location=HexCoord(5, 5))
        f2 = _fleet(2, owner_id=1, location=HexCoord(5, 5))
        emp1.fleets = [f1]; emp2.fleets = [f2]

        result = engine.resolve_all_conflicts([emp1, emp2])

        assert result.combats_resolved >= 1

    def test_resolve_all_conflicts_tracks_destroyed_fleets(self):
        """BUG-126: a fleet id appears in `fleets_destroyed` only when
        the resolver wiped its `ships` list to empty — not just because
        the resolver named it the loser."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class FirstFleetWinsResolver(IBattleResolver):
            def resolve_battle(self, fleets, modifiers=None, seed=None,
                               registries=None, environmental_effects=None,
                               empires=None):
                # Simulate the PostBattleHook wiping the loser fleet.
                fleet_list = list(fleets)
                for f in fleet_list[1:]:
                    f.ships = []
                return BattleResult(
                    winner=0, tick_count=10,
                    team_survivors={i: ([MagicMock()] if i == 0 else []) for i in range(len(fleet_list))},
                )

        engine = ConflictResolutionEngine(battle_resolver=FirstFleetWinsResolver())

        emp1 = _empire(0); emp2 = _empire(1)
        f1 = _fleet(1, owner_id=0, location=HexCoord(5, 5))
        f2 = _fleet(2, owner_id=1, location=HexCoord(5, 5))
        emp1.fleets = [f1]; emp2.fleets = [f2]

        result = engine.resolve_all_conflicts([emp1, emp2])

        # Team 1's fleet (id=2) was wiped → reported as destroyed.
        assert result.fleets_destroyed == [2]

    def test_no_conflicts_returns_zero_combats(self):
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine

        engine = ConflictResolutionEngine(battle_resolver=MagicMock())

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
