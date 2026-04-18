"""
Unit tests for ConflictResolutionEngine storm integration (PROJ-189 Phase 7).

PROJ-275 Phase 7: routed through `_resolve_combat_at_hex` (single
N-team battle path) since `_resolve_combat_simulated` was removed.
"""

import pytest
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord


def _empire(empire_id):
    e = MagicMock()
    e.id = empire_id
    e.fleets = []
    e.remove_fleet = MagicMock()
    return e


def _fleet(fleet_id, owner_id, location):
    f = MagicMock()
    f.id = fleet_id
    f.owner_id = owner_id
    f.location = location
    f.ships = [MagicMock()]
    return f


class TestConflictResolutionStormEffects:
    """Tests for passing storm effects to battle resolver."""

    def test_engine_accepts_area_effect_manager(self):
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.services.area_effect_manager import AreaEffectManager

        manager = AreaEffectManager()
        engine = ConflictResolutionEngine(battle_resolver=MagicMock(), area_effect_manager=manager)
        assert engine._area_effect_manager is manager

    def test_engine_area_effect_manager_defaults_to_none(self):
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine

        engine = ConflictResolutionEngine(battle_resolver=MagicMock())
        assert engine._area_effect_manager is None

    def test_resolve_combat_queries_area_effects_when_manager_present(self):
        """`_resolve_combat_at_hex` queries AreaEffectManager when provided."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.services.area_effect_manager import AreaEffectManager, EnvironmentalEffects
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class MockResolver(IBattleResolver):
            def __init__(self):
                self.received_effects = None

            def resolve_battle(self, fleets, modifiers=None, seed=None,
                               registries=None, environmental_effects=None):
                self.received_effects = environmental_effects
                return BattleResult(
                    winner=0, tick_count=100,
                    team_survivors={i: [] for i in range(len(list(fleets)))},
                )

        mock_effects = EnvironmentalEffects(
            shield_capacity_mult=0.5,
            in_storm=True,
            storm_names=["Ion Storm Alpha"],
        )
        mock_manager = MagicMock(spec=AreaEffectManager)
        mock_manager.get_effects_at_global_hex.return_value = mock_effects

        resolver = MockResolver()
        engine = ConflictResolutionEngine(
            battle_resolver=resolver, area_effect_manager=mock_manager
        )
        engine._galaxy = MagicMock()
        engine._empires = []
        engine._combats_resolved = 0
        engine._fleets_destroyed = []

        emp1 = _empire(0); emp2 = _empire(1)
        f1 = _fleet(1, owner_id=0, location=HexCoord(5, 5))
        f2 = _fleet(2, owner_id=1, location=HexCoord(5, 5))

        engine._resolve_combat_at_hex([(emp1, f1), (emp2, f2)])

        assert resolver.received_effects is not None
        assert resolver.received_effects.shield_capacity_mult == 0.5
        assert resolver.received_effects.in_storm is True

    def test_resolve_combat_passes_neutral_effects_when_not_in_storm(self):
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.services.area_effect_manager import AreaEffectManager, EnvironmentalEffects
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class MockResolver(IBattleResolver):
            def __init__(self):
                self.received_effects = None

            def resolve_battle(self, fleets, modifiers=None, seed=None,
                               registries=None, environmental_effects=None):
                self.received_effects = environmental_effects
                return BattleResult(
                    winner=0, tick_count=100,
                    team_survivors={i: [] for i in range(len(list(fleets)))},
                )

        mock_manager = MagicMock(spec=AreaEffectManager)
        mock_manager.get_effects_at_global_hex.return_value = EnvironmentalEffects()

        resolver = MockResolver()
        engine = ConflictResolutionEngine(
            battle_resolver=resolver, area_effect_manager=mock_manager
        )
        engine._galaxy = MagicMock()
        engine._empires = []
        engine._combats_resolved = 0
        engine._fleets_destroyed = []

        emp1 = _empire(0); emp2 = _empire(1)
        f1 = _fleet(1, owner_id=0, location=HexCoord(10, 10))
        f2 = _fleet(2, owner_id=1, location=HexCoord(10, 10))

        engine._resolve_combat_at_hex([(emp1, f1), (emp2, f2)])

        assert resolver.received_effects is not None
        assert resolver.received_effects.shield_capacity_mult == 1.0
        assert resolver.received_effects.in_storm is False

    def test_resolve_combat_no_effects_when_manager_is_none(self):
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class MockResolver(IBattleResolver):
            def __init__(self):
                self.received_effects = "not_set"

            def resolve_battle(self, fleets, modifiers=None, seed=None,
                               registries=None, environmental_effects=None):
                self.received_effects = environmental_effects
                return BattleResult(
                    winner=0, tick_count=100,
                    team_survivors={i: [] for i in range(len(list(fleets)))},
                )

        resolver = MockResolver()
        engine = ConflictResolutionEngine(battle_resolver=resolver)
        engine._empires = []
        engine._combats_resolved = 0
        engine._fleets_destroyed = []

        emp1 = _empire(0); emp2 = _empire(1)
        f1 = _fleet(1, owner_id=0, location=HexCoord(0, 0))
        f2 = _fleet(2, owner_id=1, location=HexCoord(0, 0))

        engine._resolve_combat_at_hex([(emp1, f1), (emp2, f2)])

        assert resolver.received_effects is None

    def test_resolve_all_conflicts_sets_galaxy_for_effect_lookup(self):
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine

        engine = ConflictResolutionEngine(battle_resolver=MagicMock())
        mock_galaxy = MagicMock()
        empire = MagicMock()
        empire.id = 0
        empire.fleets = []
        engine.resolve_all_conflicts([empire], galaxy=mock_galaxy)
        assert engine._galaxy is mock_galaxy


class TestConflictResolutionEngineGalaxyParameter:
    """Tests for galaxy parameter in resolve_all_conflicts."""

    def test_resolve_all_conflicts_accepts_galaxy(self):
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine

        engine = ConflictResolutionEngine(battle_resolver=MagicMock())
        mock_galaxy = MagicMock()
        empire = MagicMock()
        empire.id = 0
        empire.fleets = []
        result = engine.resolve_all_conflicts([empire], galaxy=mock_galaxy)
        assert result is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
