"""
Unit tests for ConflictResolutionEngine storm integration (PROJ-189 Phase 7).

Tests that environmental effects from storms are passed to battle resolver
when combat occurs in storm hexes.
"""

import pytest
from unittest.mock import MagicMock, patch

from game.core.hex_math import HexCoord


class TestConflictResolutionStormEffects:
    """Tests for passing storm effects to battle resolver."""

    def test_engine_accepts_area_effect_manager(self):
        """ConflictResolutionEngine accepts area_effect_manager parameter."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.services.area_effect_manager import AreaEffectManager

        manager = AreaEffectManager()
        engine = ConflictResolutionEngine(area_effect_manager=manager)

        assert engine._area_effect_manager is manager

    def test_engine_area_effect_manager_defaults_to_none(self):
        """ConflictResolutionEngine defaults to None area_effect_manager."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine

        engine = ConflictResolutionEngine()

        assert engine._area_effect_manager is None

    def test_resolve_combat_queries_area_effects_when_manager_present(self):
        """_resolve_combat_simulated queries AreaEffectManager when provided."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.services.area_effect_manager import AreaEffectManager, EnvironmentalEffects
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        # Mock battle resolver that tracks what it receives
        class MockResolver(IBattleResolver):
            def __init__(self):
                self.received_effects = None

            def resolve_battle(self, fleet1, fleet2, seed=None, registries=None, environmental_effects=None):
                self.received_effects = environmental_effects
                return BattleResult(winner=0, tick_count=100, team0_survivors=[], team1_survivors=[])

        # Mock area effect manager
        mock_effects = EnvironmentalEffects(
            shield_capacity_mult=0.5,
            in_storm=True,
            storm_names=["Ion Storm Alpha"]
        )
        mock_manager = MagicMock(spec=AreaEffectManager)
        mock_manager.get_effects_at_global_hex.return_value = mock_effects

        resolver = MockResolver()
        engine = ConflictResolutionEngine(
            battle_resolver=resolver,
            area_effect_manager=mock_manager
        )

        # Create fleets with ships at a specific location
        fleet1 = MagicMock()
        fleet1.ships = [MagicMock()]
        fleet1.location = HexCoord(5, 5)

        fleet2 = MagicMock()
        fleet2.ships = [MagicMock()]
        fleet2.location = HexCoord(5, 5)

        # Mock galaxy for area effect lookup
        mock_galaxy = MagicMock()
        engine._galaxy = mock_galaxy

        # Resolve combat
        engine._resolve_combat_simulated(fleet1, fleet2)

        # Verify effects were passed to resolver
        assert resolver.received_effects is not None
        assert resolver.received_effects.shield_capacity_mult == 0.5
        assert resolver.received_effects.in_storm is True

    def test_resolve_combat_passes_neutral_effects_when_not_in_storm(self):
        """_resolve_combat_simulated passes neutral effects when not in storm."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.services.area_effect_manager import AreaEffectManager, EnvironmentalEffects
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class MockResolver(IBattleResolver):
            def __init__(self):
                self.received_effects = None

            def resolve_battle(self, fleet1, fleet2, seed=None, registries=None, environmental_effects=None):
                self.received_effects = environmental_effects
                return BattleResult(winner=0, tick_count=100, team0_survivors=[], team1_survivors=[])

        # Neutral effects (not in storm)
        neutral_effects = EnvironmentalEffects()
        mock_manager = MagicMock(spec=AreaEffectManager)
        mock_manager.get_effects_at_global_hex.return_value = neutral_effects

        resolver = MockResolver()
        engine = ConflictResolutionEngine(
            battle_resolver=resolver,
            area_effect_manager=mock_manager
        )

        fleet1 = MagicMock()
        fleet1.ships = [MagicMock()]
        fleet1.location = HexCoord(10, 10)

        fleet2 = MagicMock()
        fleet2.ships = [MagicMock()]
        fleet2.location = HexCoord(10, 10)

        mock_galaxy = MagicMock()
        engine._galaxy = mock_galaxy

        engine._resolve_combat_simulated(fleet1, fleet2)

        # Verify neutral effects were passed
        assert resolver.received_effects is not None
        assert resolver.received_effects.shield_capacity_mult == 1.0
        assert resolver.received_effects.in_storm is False

    def test_resolve_combat_no_effects_when_manager_is_none(self):
        """_resolve_combat_simulated passes None when no AreaEffectManager."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class MockResolver(IBattleResolver):
            def __init__(self):
                self.received_effects = "not_set"

            def resolve_battle(self, fleet1, fleet2, seed=None, registries=None, environmental_effects=None):
                self.received_effects = environmental_effects
                return BattleResult(winner=0, tick_count=100, team0_survivors=[], team1_survivors=[])

        resolver = MockResolver()
        engine = ConflictResolutionEngine(battle_resolver=resolver)

        fleet1 = MagicMock()
        fleet1.ships = [MagicMock()]

        fleet2 = MagicMock()
        fleet2.ships = [MagicMock()]

        engine._resolve_combat_simulated(fleet1, fleet2)

        # Verify None was passed (no manager)
        assert resolver.received_effects is None

    def test_resolve_all_conflicts_sets_galaxy_for_effect_lookup(self):
        """resolve_all_conflicts stores galaxy reference for effect lookup."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine

        engine = ConflictResolutionEngine()

        mock_galaxy = MagicMock()
        empire = MagicMock()
        empire.id = 0
        empire.fleets = []

        # Call with galaxy parameter
        engine.resolve_all_conflicts([empire], galaxy=mock_galaxy)

        # Verify galaxy was stored
        assert engine._galaxy is mock_galaxy


class TestConflictResolutionEngineGalaxyParameter:
    """Tests for galaxy parameter in resolve_all_conflicts."""

    def test_resolve_all_conflicts_accepts_galaxy(self):
        """resolve_all_conflicts accepts optional galaxy parameter."""
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine

        engine = ConflictResolutionEngine()

        mock_galaxy = MagicMock()
        empire = MagicMock()
        empire.id = 0
        empire.fleets = []

        # Should not raise
        result = engine.resolve_all_conflicts([empire], galaxy=mock_galaxy)

        assert result is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
