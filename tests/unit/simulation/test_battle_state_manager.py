"""
Tests for BattleStateManager (PROJ-29 SIM-03 Phase 2)

Tests the extracted BattleStateManager class that handles:
- Capturing battle state (save)
- Restoring battle state (load)
- State data structure management
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from dataclasses import dataclass

from game.simulation.managers.battle_state_manager import BattleStateManager


# === Fixtures ===

@pytest.fixture
def mock_engine():
    """Create a mock BattleEngine."""
    engine = Mock()
    engine.ships = []
    engine.projectiles = []
    engine.tick_counter = 100
    return engine


@pytest.fixture
def mock_config():
    """Create a mock BattleConfig-like object."""
    config = Mock()
    config.mode = Mock()
    config.mode.value = "manual"
    config.seed = 12345
    config.allow_retreat = False
    config.allow_reinforcements = False
    return config


@pytest.fixture
def state_manager():
    """Create a BattleStateManager instance."""
    return BattleStateManager()


# === Capture State Tests ===

class TestBattleStateManagerCapture:
    """Tests for BattleStateManager.capture_state()."""

    def test_capture_state_raises_without_engine(self, state_manager, mock_config):
        """capture_state raises when no engine provided."""
        with pytest.raises(RuntimeError, match="No engine"):
            state_manager.capture_state(None, mock_config)

    def test_capture_state_returns_battle_state(self, state_manager, mock_engine, mock_config):
        """capture_state returns a BattleState object."""
        with patch('game.simulation.managers.battle_state_manager.BattleState') as MockState:
            mock_state = Mock()
            MockState.capture_from_engine.return_value = mock_state

            result = state_manager.capture_state(mock_engine, mock_config)

            assert result is mock_state

    def test_capture_state_passes_config_values(self, state_manager, mock_engine, mock_config):
        """capture_state passes config values to BattleState."""
        mock_config.mode.value = "strategy"
        mock_config.seed = 99999
        mock_config.allow_retreat = True
        mock_config.allow_reinforcements = True

        with patch('game.simulation.managers.battle_state_manager.BattleState') as MockState:
            MockState.capture_from_engine.return_value = Mock()

            state_manager.capture_state(mock_engine, mock_config)

            MockState.capture_from_engine.assert_called_once_with(
                mock_engine,
                mode="strategy",
                seed=99999,
                allow_retreat=True,
                allow_reinforcements=True,
            )


# === Restore State Tests ===

class TestBattleStateManagerRestore:
    """Tests for BattleStateManager.restore_state()."""

    def test_restore_state_returns_config(self, state_manager):
        """restore_state returns a BattleConfig."""
        mock_state = Mock()
        mock_state.mode = "manual"
        mock_state.seed = 12345
        mock_state.max_ticks = 10000
        mock_state.end_mode = "HP_BASED"
        mock_state.allow_retreat = False
        mock_state.allow_reinforcements = False

        config = state_manager.restore_config_from_state(mock_state)

        assert config is not None
        assert config.seed == 12345
        assert config.max_ticks == 10000
        assert config.allow_retreat is False

    def test_restore_state_handles_strategy_mode(self, state_manager):
        """restore_state handles strategy mode correctly."""
        mock_state = Mock()
        mock_state.mode = "strategy"
        mock_state.seed = 42
        mock_state.max_ticks = 50000
        mock_state.end_mode = "HP_BASED"
        mock_state.allow_retreat = True
        mock_state.allow_reinforcements = True

        config = state_manager.restore_config_from_state(mock_state)

        assert config.allow_retreat is True
        assert config.allow_reinforcements is True

    def test_restore_state_handles_missing_max_ticks(self, state_manager):
        """restore_state handles missing max_ticks."""
        mock_state = Mock()
        mock_state.mode = "manual"
        mock_state.seed = None
        mock_state.max_ticks = None
        mock_state.end_mode = "HP_BASED"
        mock_state.allow_retreat = False
        mock_state.allow_reinforcements = False

        config = state_manager.restore_config_from_state(mock_state)

        assert config.max_ticks == 100000  # Default

    def test_restore_state_raises_on_invalid_mode(self, state_manager):
        """restore_state raises on invalid mode."""
        mock_state = Mock()
        mock_state.mode = "invalid_mode"

        with pytest.raises(ValueError, match="Invalid"):
            state_manager.restore_config_from_state(mock_state)


# === Extract Ships From State Tests ===

class TestBattleStateManagerExtractShips:
    """Tests for BattleStateManager.extract_ships_from_state()."""

    def test_extract_ships_converts_states(self, state_manager):
        """extract_ships_from_state converts ShipStates to ships."""
        mock_ship_state = Mock()
        mock_ship = Mock()
        mock_ship_state.to_ship.return_value = mock_ship
        mock_ship_state.ship_id = "ship-1"
        mock_ship_state.team_id = 0

        mock_battle_state = Mock()
        mock_battle_state.ships = {"ship-1": mock_ship_state}

        ships, id_map = state_manager.extract_ships_from_state(mock_battle_state)

        assert len(ships) == 1
        assert mock_ship in ships
        assert id_map[id(mock_ship)] == "ship-1"

    def test_extract_ships_empty_state(self, state_manager):
        """extract_ships_from_state handles empty ship list."""
        mock_battle_state = Mock()
        mock_battle_state.ships = {}

        ships, id_map = state_manager.extract_ships_from_state(mock_battle_state)

        assert ships == []
        assert id_map == {}

    def test_extract_ships_groups_by_team(self, state_manager):
        """extract_ships_from_state returns ships grouped by team."""
        ship_state_0 = Mock()
        ship_state_0.to_ship.return_value = Mock()
        ship_state_0.ship_id = "ship-0"
        ship_state_0.team_id = 0

        ship_state_1 = Mock()
        ship_state_1.to_ship.return_value = Mock()
        ship_state_1.ship_id = "ship-1"
        ship_state_1.team_id = 1

        mock_battle_state = Mock()
        mock_battle_state.ships = {
            "ship-0": ship_state_0,
            "ship-1": ship_state_1
        }

        ships, id_map = state_manager.extract_ships_from_state(mock_battle_state)

        assert len(ships) == 2
        assert len(id_map) == 2


# === State Validation Tests ===

class TestBattleStateManagerValidation:
    """Tests for state validation."""

    def test_validate_state_valid(self, state_manager):
        """validate_state returns True for valid state."""
        mock_state = Mock()
        mock_state.mode = "manual"
        mock_state.ships = {}
        mock_state.tick_count = 0

        assert state_manager.validate_state(mock_state) is True

    def test_validate_state_missing_mode(self, state_manager):
        """validate_state returns False for missing mode."""
        mock_state = Mock(spec=[])  # No attributes

        assert state_manager.validate_state(mock_state) is False

    def test_validate_state_none(self, state_manager):
        """validate_state returns False for None."""
        assert state_manager.validate_state(None) is False
