"""
Tests for SimulationBattleResolver adapter.

PROJ-11 Phase 4: Interface Contracts - Tests written BEFORE implementation (TDD).

SimulationBattleResolver adapts the simulation layer's BattleController
to the strategy layer's IBattleResolver interface.
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock


# =============================================================================
# SimulationBattleResolver Import Tests
# =============================================================================


class TestSimulationBattleResolverImport:
    """Test SimulationBattleResolver is properly importable."""

    def test_adapter_importable_from_adapters(self):
        """SimulationBattleResolver should be importable from adapters module."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver
        assert SimulationBattleResolver is not None

    def test_adapter_importable_from_adapters_package(self):
        """SimulationBattleResolver should be accessible from adapters package."""
        from game.strategy.adapters import SimulationBattleResolver
        assert SimulationBattleResolver is not None


# =============================================================================
# SimulationBattleResolver Implementation Tests
# =============================================================================


class TestSimulationBattleResolverImplementation:
    """Test SimulationBattleResolver properly implements IBattleResolver."""

    def test_implements_ibattle_resolver(self):
        """SimulationBattleResolver should implement IBattleResolver interface."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver
        from game.strategy.interfaces.battle_resolver import IBattleResolver

        assert issubclass(SimulationBattleResolver, IBattleResolver)

    def test_can_instantiate(self):
        """SimulationBattleResolver should be instantiable."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        resolver = SimulationBattleResolver()
        assert resolver is not None

    def test_has_resolve_battle_method(self):
        """SimulationBattleResolver should have resolve_battle method."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        resolver = SimulationBattleResolver()
        assert hasattr(resolver, 'resolve_battle')
        assert callable(resolver.resolve_battle)


# =============================================================================
# SimulationBattleResolver Behavior Tests
# =============================================================================


class TestSimulationBattleResolverBehavior:
    """Test SimulationBattleResolver behavior with mocked simulation layer."""

    @pytest.fixture
    def mock_fleet_with_ships(self):
        """Create a mock fleet with ship instances."""
        fleet = MagicMock()
        fleet.id = 1
        fleet.has_ship_instances.return_value = True
        # PROJ-210: battle adapter is now accessed via fleet.battle property
        fleet.battle = MagicMock()
        fleet.battle.to_battle_ships.return_value = [MagicMock(), MagicMock()]
        return fleet

    @pytest.fixture
    def mock_fleet_empty(self):
        """Create a mock fleet without ship instances."""
        fleet = MagicMock()
        fleet.id = 2
        fleet.has_ship_instances.return_value = True
        # PROJ-210: battle adapter is now accessed via fleet.battle property
        fleet.battle = MagicMock()
        fleet.battle.to_battle_ships.return_value = []
        return fleet

    def test_resolve_battle_returns_battle_result(self, mock_fleet_with_ships):
        """resolve_battle should return a BattleResult object."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver
        from game.strategy.interfaces.battle_resolver import BattleResult

        resolver = SimulationBattleResolver()

        # Create another fleet
        fleet2 = MagicMock()
        fleet2.id = 2
        fleet2.has_ship_instances.return_value = True
        fleet2.to_battle_ships.return_value = [MagicMock()]

        with patch('game.strategy.adapters.simulation_adapter.BattleController') as mock_controller_cls, \
             patch('game.strategy.adapters.simulation_adapter.BattleService'):

            # Setup mock controller
            mock_controller = MagicMock()
            mock_controller_cls.return_value = mock_controller

            # Setup mock battle results
            mock_results = MagicMock()
            mock_results.winner = 0
            mock_results.tick_count = 100
            mock_results.surviving_ships = []
            mock_controller.run_headless.return_value = mock_results

            result = resolver.resolve_battle(mock_fleet_with_ships, fleet2)

            assert isinstance(result, BattleResult)
            assert result.winner == 0
            assert result.tick_count == 100

    def test_resolve_battle_uses_seed(self, mock_fleet_with_ships):
        """resolve_battle should pass seed to BattleConfig."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        resolver = SimulationBattleResolver()

        fleet2 = MagicMock()
        fleet2.id = 2
        fleet2.has_ship_instances.return_value = True
        fleet2.to_battle_ships.return_value = [MagicMock()]

        with patch('game.strategy.adapters.simulation_adapter.BattleController') as mock_controller_cls, \
             patch('game.strategy.adapters.simulation_adapter.BattleService'), \
             patch('game.strategy.adapters.simulation_adapter.BattleConfig') as mock_config_cls:

            mock_controller = MagicMock()
            mock_controller_cls.return_value = mock_controller

            mock_results = MagicMock()
            mock_results.winner = 1
            mock_results.tick_count = 50
            mock_results.surviving_ships = []
            mock_controller.run_headless.return_value = mock_results

            resolver.resolve_battle(mock_fleet_with_ships, fleet2, seed=42)

            # Verify BattleConfig was called with seed=42
            mock_config_cls.assert_called()
            call_kwargs = mock_config_cls.call_args.kwargs
            assert call_kwargs.get('seed') == 42

    def test_resolve_battle_team0_is_fleet1(self, mock_fleet_with_ships):
        """Fleet1 should be assigned to team 0."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        resolver = SimulationBattleResolver()

        fleet2 = MagicMock()
        fleet2.id = 2
        fleet2.has_ship_instances.return_value = True
        # PROJ-210: to_battle_ships accessed via fleet.battle property
        fleet2.battle = MagicMock()
        fleet2.battle.to_battle_ships.return_value = [MagicMock()]

        with patch('game.strategy.adapters.simulation_adapter.BattleController') as mock_controller_cls, \
             patch('game.strategy.adapters.simulation_adapter.BattleService'):

            mock_controller = MagicMock()
            mock_controller_cls.return_value = mock_controller

            mock_results = MagicMock()
            mock_results.winner = 0
            mock_results.tick_count = 100
            mock_results.surviving_ships = []
            mock_controller.run_headless.return_value = mock_results

            resolver.resolve_battle(mock_fleet_with_ships, fleet2)

            # PROJ-210: Verify fleet1 converted with team_id=0 via battle adapter
            mock_fleet_with_ships.battle.to_battle_ships.assert_called_with(team_id=0, registries=None)

            # PROJ-210: Verify fleet2 converted with team_id=1 via battle adapter
            fleet2.battle.to_battle_ships.assert_called_with(team_id=1, registries=None)

    def test_resolve_battle_converts_survivors_to_ships(self, mock_fleet_with_ships):
        """Survivors should be converted using to_ship() method."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        resolver = SimulationBattleResolver()

        fleet2 = MagicMock()
        fleet2.id = 2
        fleet2.has_ship_instances.return_value = True
        fleet2.to_battle_ships.return_value = [MagicMock()]

        with patch('game.strategy.adapters.simulation_adapter.BattleController') as mock_controller_cls, \
             patch('game.strategy.adapters.simulation_adapter.BattleService'):

            mock_controller = MagicMock()
            mock_controller_cls.return_value = mock_controller

            # Create mock survivors
            survivor0 = MagicMock()
            survivor0.team_id = 0
            survivor0.to_ship.return_value = MagicMock(name="Ship0")

            survivor1 = MagicMock()
            survivor1.team_id = 1
            survivor1.to_ship.return_value = MagicMock(name="Ship1")

            mock_results = MagicMock()
            mock_results.winner = 0
            mock_results.tick_count = 100
            mock_results.surviving_ships = [survivor0, survivor1]
            mock_controller.run_headless.return_value = mock_results

            result = resolver.resolve_battle(mock_fleet_with_ships, fleet2)

            # Verify survivors were converted
            survivor0.to_ship.assert_called_once()
            survivor1.to_ship.assert_called_once()

            # Verify result has correct survivors
            assert len(result.team0_survivors) == 1
            assert len(result.team1_survivors) == 1

    def test_resolve_battle_handles_empty_fleet(self, mock_fleet_with_ships, mock_fleet_empty):
        """resolve_battle should handle one fleet with no combat ships."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver
        from game.strategy.interfaces.battle_resolver import BattleResult

        resolver = SimulationBattleResolver()

        # Fleet with no ships should return early with winner being the non-empty fleet
        result = resolver.resolve_battle(mock_fleet_with_ships, mock_fleet_empty)

        assert isinstance(result, BattleResult)
        # Fleet1 has ships, fleet2 doesn't, so fleet1 (team 0) wins
        assert result.winner == 0

    def test_resolve_battle_handles_both_empty_fleets(self, mock_fleet_empty):
        """resolve_battle should handle both fleets with no combat ships."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver
        from game.strategy.interfaces.battle_resolver import BattleResult

        resolver = SimulationBattleResolver()

        fleet2 = MagicMock()
        fleet2.id = 3
        fleet2.has_ship_instances.return_value = True
        fleet2.to_battle_ships.return_value = []

        result = resolver.resolve_battle(mock_fleet_empty, fleet2)

        assert isinstance(result, BattleResult)
        # Both empty - could be draw or random, but should return a result
        assert result.winner is None or result.winner in [0, 1]

    def test_resolve_battle_uses_headless_mode(self, mock_fleet_with_ships):
        """BattleConfig should be created with headless=True."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        resolver = SimulationBattleResolver()

        fleet2 = MagicMock()
        fleet2.id = 2
        fleet2.has_ship_instances.return_value = True
        fleet2.to_battle_ships.return_value = [MagicMock()]

        with patch('game.strategy.adapters.simulation_adapter.BattleController') as mock_controller_cls, \
             patch('game.strategy.adapters.simulation_adapter.BattleService'), \
             patch('game.strategy.adapters.simulation_adapter.BattleConfig') as mock_config_cls:

            mock_controller = MagicMock()
            mock_controller_cls.return_value = mock_controller

            mock_results = MagicMock()
            mock_results.winner = 0
            mock_results.tick_count = 100
            mock_results.surviving_ships = []
            mock_controller.run_headless.return_value = mock_results

            resolver.resolve_battle(mock_fleet_with_ships, fleet2)

            # Verify headless=True in config
            call_kwargs = mock_config_cls.call_args.kwargs
            assert call_kwargs.get('headless') is True

    def test_resolve_battle_uses_strategy_mode(self, mock_fleet_with_ships):
        """BattleConfig should be created with mode=STRATEGY."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        resolver = SimulationBattleResolver()

        fleet2 = MagicMock()
        fleet2.id = 2
        fleet2.has_ship_instances.return_value = True
        fleet2.to_battle_ships.return_value = [MagicMock()]

        with patch('game.strategy.adapters.simulation_adapter.BattleController') as mock_controller_cls, \
             patch('game.strategy.adapters.simulation_adapter.BattleService'), \
             patch('game.strategy.adapters.simulation_adapter.BattleConfig') as mock_config_cls, \
             patch('game.strategy.adapters.simulation_adapter.BattleMode') as mock_mode:

            mock_mode.STRATEGY = 'STRATEGY'

            mock_controller = MagicMock()
            mock_controller_cls.return_value = mock_controller

            mock_results = MagicMock()
            mock_results.winner = 0
            mock_results.tick_count = 100
            mock_results.surviving_ships = []
            mock_controller.run_headless.return_value = mock_results

            resolver.resolve_battle(mock_fleet_with_ships, fleet2)

            # Verify mode=STRATEGY in config
            call_kwargs = mock_config_cls.call_args.kwargs
            assert call_kwargs.get('mode') == 'STRATEGY'


# =============================================================================
# SimulationBattleResolver Dependency Injection Tests
# =============================================================================


class TestSimulationBattleResolverDependencyInjection:
    """Test SimulationBattleResolver supports dependency injection of AI factory.

    PROJ-147: ADR-STR-001 - Strategy layer should not directly import from AI layer.
    The AI factory should be injectable to maintain proper layer separation.
    """

    def test_accepts_ai_factory_parameter(self):
        """SimulationBattleResolver should accept optional ai_factory parameter."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver
        from unittest.mock import MagicMock

        mock_factory = MagicMock()
        resolver = SimulationBattleResolver(ai_factory=mock_factory)
        assert resolver is not None
        assert resolver._ai_factory is mock_factory

    def test_uses_injected_ai_factory(self):
        """SimulationBattleResolver should use injected ai_factory when provided."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver
        from unittest.mock import MagicMock, patch

        mock_factory = MagicMock()
        resolver = SimulationBattleResolver(ai_factory=mock_factory)

        fleet1 = MagicMock()
        fleet1.id = 1
        fleet1.to_battle_ships.return_value = [MagicMock()]

        fleet2 = MagicMock()
        fleet2.id = 2
        fleet2.to_battle_ships.return_value = [MagicMock()]

        with patch('game.strategy.adapters.simulation_adapter.BattleController') as mock_controller_cls:
            mock_controller = MagicMock()
            mock_controller_cls.return_value = mock_controller

            mock_results = MagicMock()
            mock_results.winner = 0
            mock_results.tick_count = 100
            mock_results.surviving_ships = []
            mock_controller.run_headless.return_value = mock_results

            resolver.resolve_battle(fleet1, fleet2)

            # Verify BattleController was created with the injected factory
            mock_controller_cls.assert_called_once_with(ai_factory=mock_factory)

    def test_no_direct_ai_layer_import_at_module_level(self):
        """SimulationBattleResolver module should not import AIControllerFactory at module level."""
        import game.strategy.adapters.simulation_adapter as module
        import inspect

        source = inspect.getsource(module)
        # Check that the module-level imports don't include direct AI factory import
        # The import should be inside resolve_battle method, not at module level
        module_imports_section = source.split('class SimulationBattleResolver')[0]
        assert 'from game.ai.ai_factory import AIControllerFactory' not in module_imports_section
