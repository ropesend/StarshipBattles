"""Tests for BattleOrchestrator.

PROJ-17 Phase 4: Tests for UI-layer battle orchestration that creates AI controllers.
This follows proper layer boundaries by keeping AI controller creation in the UI layer.
"""
import pytest
from unittest.mock import MagicMock, patch

# Note: These imports will fail until we implement the module (TDD - tests first)
# from game.ui.orchestration import BattleOrchestrator
# from game.engine.spatial import SpatialGrid


class TestBattleOrchestratorCreation:
    """Test BattleOrchestrator instantiation."""

    def test_orchestrator_requires_grid(self):
        """Verify orchestrator is initialized with a spatial grid."""
        from game.ui.orchestration import BattleOrchestrator
        from game.engine.spatial import SpatialGrid

        grid = MagicMock(spec=SpatialGrid)
        orchestrator = BattleOrchestrator(grid)

        assert orchestrator.grid is grid


class TestCreateAIControllers:
    """Test create_ai_controllers method."""

    def test_create_ai_controllers_creates_correct_count(self):
        """Verify correct number of controllers created for both teams."""
        from game.ui.orchestration import BattleOrchestrator
        from game.engine.spatial import SpatialGrid

        grid = MagicMock(spec=SpatialGrid)
        orchestrator = BattleOrchestrator(grid)

        # Create mock ships
        team0 = [MagicMock() for _ in range(3)]
        team1 = [MagicMock() for _ in range(2)]

        controllers = orchestrator.create_ai_controllers(team0, team1)

        assert len(controllers) == 5

    def test_create_ai_controllers_empty_teams(self):
        """Verify handling of empty ship lists."""
        from game.ui.orchestration import BattleOrchestrator
        from game.engine.spatial import SpatialGrid

        grid = MagicMock(spec=SpatialGrid)
        orchestrator = BattleOrchestrator(grid)

        controllers = orchestrator.create_ai_controllers([], [])

        assert len(controllers) == 0

    def test_create_ai_controllers_single_ship_per_team(self):
        """Verify single ship per team works correctly."""
        from game.ui.orchestration import BattleOrchestrator
        from game.engine.spatial import SpatialGrid

        grid = MagicMock(spec=SpatialGrid)
        orchestrator = BattleOrchestrator(grid)

        team0 = [MagicMock()]
        team1 = [MagicMock()]

        controllers = orchestrator.create_ai_controllers(team0, team1)

        assert len(controllers) == 2

    @patch('game.ui.orchestration.battle_orchestrator.AIController')
    @patch('game.ui.orchestration.battle_orchestrator.ShipControllableAdapter')
    def test_create_ai_controllers_uses_correct_enemy_teams(self, mock_adapter, mock_controller):
        """Verify team 0 ships target team 1 and vice versa."""
        from game.ui.orchestration import BattleOrchestrator
        from game.engine.spatial import SpatialGrid

        grid = MagicMock(spec=SpatialGrid)
        orchestrator = BattleOrchestrator(grid)

        ship0 = MagicMock()
        ship1 = MagicMock()

        orchestrator.create_ai_controllers([ship0], [ship1])

        # Verify AIController was called with correct enemy_team_id
        calls = mock_controller.call_args_list
        assert len(calls) == 2

        # First call: team0 ship targets team 1
        # enemy_team_id is passed as keyword argument
        assert calls[0].kwargs.get('enemy_team_id') == 1

        # Second call: team1 ship targets team 0
        assert calls[1].kwargs.get('enemy_team_id') == 0


class TestCreateAIForShip:
    """Test create_ai_for_ship method (for reinforcements)."""

    def test_create_ai_for_ship(self):
        """Verify single ship AI creation returns a controller."""
        from game.ui.orchestration import BattleOrchestrator
        from game.engine.spatial import SpatialGrid
        from game.ai.controller import AIController

        grid = MagicMock(spec=SpatialGrid)
        orchestrator = BattleOrchestrator(grid)

        ship = MagicMock()
        controller = orchestrator.create_ai_for_ship(ship, enemy_team_id=1)

        assert controller is not None
        assert isinstance(controller, AIController)

    @patch('game.ui.orchestration.battle_orchestrator.AIController')
    @patch('game.ui.orchestration.battle_orchestrator.ShipControllableAdapter')
    def test_create_ai_for_ship_with_enemy_team_0(self, mock_adapter, mock_controller):
        """Verify enemy team ID is passed correctly for team 1 ships."""
        from game.ui.orchestration import BattleOrchestrator
        from game.engine.spatial import SpatialGrid

        grid = MagicMock(spec=SpatialGrid)
        orchestrator = BattleOrchestrator(grid)

        ship = MagicMock()
        orchestrator.create_ai_for_ship(ship, enemy_team_id=0)

        # Verify AIController was called with correct enemy_team_id
        mock_controller.assert_called_once()
        call_args = mock_controller.call_args[0]
        assert call_args[2] == 0  # enemy_team_id = 0

    @patch('game.ui.orchestration.battle_orchestrator.AIController')
    @patch('game.ui.orchestration.battle_orchestrator.ShipControllableAdapter')
    def test_create_ai_for_ship_wraps_with_adapter(self, mock_adapter, mock_controller):
        """Verify ship is wrapped with ShipControllableAdapter."""
        from game.ui.orchestration import BattleOrchestrator
        from game.engine.spatial import SpatialGrid

        grid = MagicMock(spec=SpatialGrid)
        orchestrator = BattleOrchestrator(grid)

        ship = MagicMock()
        orchestrator.create_ai_for_ship(ship, enemy_team_id=1)

        # Verify ShipControllableAdapter was called with the ship
        mock_adapter.assert_called_once_with(ship)


class TestOrchestratorIntegration:
    """Integration tests for BattleOrchestrator with real AIController."""

    def test_created_controllers_have_correct_grid(self):
        """Verify controllers receive the correct spatial grid reference."""
        from game.ui.orchestration import BattleOrchestrator
        from game.engine.spatial import SpatialGrid

        grid = MagicMock(spec=SpatialGrid)
        orchestrator = BattleOrchestrator(grid)

        ship = MagicMock()
        controller = orchestrator.create_ai_for_ship(ship, enemy_team_id=1)

        assert controller.grid is grid


class TestBattleOrchestratorEdgeCases:
    """PROJ-142: TCG-UI2-006 - Edge case tests for BattleOrchestrator."""

    def test_create_ai_controllers_with_one_empty_team(self):
        """Verify handling when only one team has ships."""
        from game.ui.orchestration import BattleOrchestrator
        from game.engine.spatial import SpatialGrid

        grid = MagicMock(spec=SpatialGrid)
        orchestrator = BattleOrchestrator(grid)

        team0 = [MagicMock() for _ in range(3)]
        team1 = []  # Empty team

        controllers = orchestrator.create_ai_controllers(team0, team1)

        # Should create controllers only for team0
        assert len(controllers) == 3

    def test_create_ai_controllers_with_large_teams(self):
        """Verify handling of large team sizes."""
        from game.ui.orchestration import BattleOrchestrator
        from game.engine.spatial import SpatialGrid

        grid = MagicMock(spec=SpatialGrid)
        orchestrator = BattleOrchestrator(grid)

        # Large battle scenario
        team0 = [MagicMock() for _ in range(50)]
        team1 = [MagicMock() for _ in range(50)]

        controllers = orchestrator.create_ai_controllers(team0, team1)

        assert len(controllers) == 100

    def test_create_ai_for_ship_with_enemy_team_id_zero(self):
        """Verify correct enemy team ID when ship is on team 1."""
        from game.ui.orchestration import BattleOrchestrator
        from game.engine.spatial import SpatialGrid
        from game.ai.controller import AIController

        grid = MagicMock(spec=SpatialGrid)
        orchestrator = BattleOrchestrator(grid)

        ship = MagicMock()
        controller = orchestrator.create_ai_for_ship(ship, enemy_team_id=0)

        # Controller should target team 0
        assert isinstance(controller, AIController)

    def test_create_ai_controllers_preserves_ship_order(self):
        """Verify controllers are created in the same order as ships."""
        from game.ui.orchestration import BattleOrchestrator
        from game.engine.spatial import SpatialGrid

        grid = MagicMock(spec=SpatialGrid)
        orchestrator = BattleOrchestrator(grid)

        # Create ships with identifiable attributes
        team0 = [MagicMock(name=f"ship0_{i}") for i in range(3)]
        team1 = [MagicMock(name=f"ship1_{i}") for i in range(2)]

        controllers = orchestrator.create_ai_controllers(team0, team1)

        # Should have 5 controllers in team order
        assert len(controllers) == 5

    def test_orchestrator_grid_reference_persists(self):
        """Verify grid reference is maintained after multiple operations."""
        from game.ui.orchestration import BattleOrchestrator
        from game.engine.spatial import SpatialGrid

        grid = MagicMock(spec=SpatialGrid)
        orchestrator = BattleOrchestrator(grid)

        # Perform multiple operations
        orchestrator.create_ai_controllers([MagicMock()], [MagicMock()])
        orchestrator.create_ai_for_ship(MagicMock(), enemy_team_id=1)
        orchestrator.create_ai_controllers([MagicMock()], [])

        # Grid reference should still be the same
        assert orchestrator.grid is grid
