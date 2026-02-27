"""
Tests for SimulationBattleResolver storm shield interference (PROJ-189 Phase 7).

Tests that environmental effects reduce shield capacity during combat.
"""

import pytest
from unittest.mock import MagicMock, patch


class TestSimulationBattleResolverEnvironmentalEffects:
    """Tests for environmental_effects parameter in resolve_battle."""

    def test_resolve_battle_accepts_environmental_effects(self):
        """resolve_battle accepts optional environmental_effects parameter."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver
        from game.strategy.services.area_effect_manager import EnvironmentalEffects

        resolver = SimulationBattleResolver()

        # Create fleets with no ships (triggers early return)
        fleet1 = MagicMock()
        fleet1.id = 1
        fleet1.to_battle_ships.return_value = []

        fleet2 = MagicMock()
        fleet2.id = 2
        fleet2.to_battle_ships.return_value = []

        effects = EnvironmentalEffects(shield_capacity_mult=0.5, in_storm=True)

        # Should not raise
        result = resolver.resolve_battle(fleet1, fleet2, environmental_effects=effects)

        assert result is not None

    def test_resolve_battle_with_shield_interference_in_storm(self):
        """resolve_battle applies shield_capacity_mult to ships in storm."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver
        from game.strategy.services.area_effect_manager import EnvironmentalEffects

        resolver = SimulationBattleResolver()

        # Create mock battle ships with real shield values
        mock_ship1 = MagicMock()
        mock_ship1.max_shields = 1000
        mock_ship1.current_shields = 1000

        mock_ship2 = MagicMock()
        mock_ship2.max_shields = 500
        mock_ship2.current_shields = 400

        fleet1 = MagicMock()
        fleet1.id = 1
        fleet1.to_battle_ships.return_value = [mock_ship1]

        fleet2 = MagicMock()
        fleet2.id = 2
        fleet2.to_battle_ships.return_value = [mock_ship2]

        # Storm with 50% shield reduction
        effects = EnvironmentalEffects(shield_capacity_mult=0.5, in_storm=True)

        with patch('game.strategy.adapters.simulation_adapter.BattleController') as mock_controller_cls:
            mock_controller = MagicMock()
            mock_controller_cls.return_value = mock_controller

            mock_results = MagicMock()
            mock_results.winner = 0
            mock_results.tick_count = 100
            mock_results.surviving_ships = []
            mock_controller.run_headless.return_value = mock_results

            resolver.resolve_battle(fleet1, fleet2, environmental_effects=effects)

            # Verify shield interference was applied - max_shields reduced by 50%
            assert mock_ship1.max_shields == 500  # 1000 * 0.5
            assert mock_ship2.max_shields == 250  # 500 * 0.5
            # Current shields capped to new max
            assert mock_ship1.current_shields == 500  # min(1000, 500)
            assert mock_ship2.current_shields == 250  # min(400, 250)

    def test_resolve_battle_no_shield_interference_without_storm(self):
        """resolve_battle does not modify shields when not in storm."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver
        from game.strategy.services.area_effect_manager import EnvironmentalEffects

        resolver = SimulationBattleResolver()

        mock_ship1 = MagicMock()
        mock_ship1.max_shields = 1000
        mock_ship1.current_shields = 1000

        mock_ship2 = MagicMock()
        mock_ship2.max_shields = 500
        mock_ship2.current_shields = 500

        fleet1 = MagicMock()
        fleet1.id = 1
        fleet1.to_battle_ships.return_value = [mock_ship1]

        fleet2 = MagicMock()
        fleet2.id = 2
        fleet2.to_battle_ships.return_value = [mock_ship2]

        # No storm - neutral effects
        effects = EnvironmentalEffects()

        with patch('game.strategy.adapters.simulation_adapter.BattleController') as mock_controller_cls:
            mock_controller = MagicMock()
            mock_controller_cls.return_value = mock_controller

            mock_results = MagicMock()
            mock_results.winner = 0
            mock_results.tick_count = 100
            mock_results.surviving_ships = []
            mock_controller.run_headless.return_value = mock_results

            resolver.resolve_battle(fleet1, fleet2, environmental_effects=effects)

            # Shield values unchanged (mult is 1.0)
            assert mock_ship1.max_shields == 1000
            assert mock_ship2.max_shields == 500

    def test_resolve_battle_none_effects_no_interference(self):
        """resolve_battle with None effects does not modify shields."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        resolver = SimulationBattleResolver()

        mock_ship1 = MagicMock()
        mock_ship1.max_shields = 1000
        mock_ship1.current_shields = 1000

        mock_ship2 = MagicMock()
        mock_ship2.max_shields = 500
        mock_ship2.current_shields = 500

        fleet1 = MagicMock()
        fleet1.id = 1
        fleet1.to_battle_ships.return_value = [mock_ship1]

        fleet2 = MagicMock()
        fleet2.id = 2
        fleet2.to_battle_ships.return_value = [mock_ship2]

        with patch('game.strategy.adapters.simulation_adapter.BattleController') as mock_controller_cls:
            mock_controller = MagicMock()
            mock_controller_cls.return_value = mock_controller

            mock_results = MagicMock()
            mock_results.winner = 0
            mock_results.tick_count = 100
            mock_results.surviving_ships = []
            mock_controller.run_headless.return_value = mock_results

            resolver.resolve_battle(fleet1, fleet2, environmental_effects=None)

            # Shield values unchanged
            assert mock_ship1.max_shields == 1000
            assert mock_ship2.max_shields == 500


class TestBattleResolverInterfaceUpdate:
    """Tests that IBattleResolver interface supports environmental_effects."""

    def test_ibattle_resolver_accepts_environmental_effects(self):
        """IBattleResolver.resolve_battle accepts environmental_effects parameter."""
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult
        from game.strategy.services.area_effect_manager import EnvironmentalEffects

        class TestResolver(IBattleResolver):
            def resolve_battle(self, fleet1, fleet2, seed=None, registries=None, environmental_effects=None):
                return BattleResult(winner=0, tick_count=0, team0_survivors=[], team1_survivors=[])

        resolver = TestResolver()
        effects = EnvironmentalEffects(shield_capacity_mult=0.5)

        # Should work without error
        result = resolver.resolve_battle(MagicMock(), MagicMock(), environmental_effects=effects)
        assert result is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
