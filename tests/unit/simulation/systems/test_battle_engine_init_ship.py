"""
Tests for BattleEngine._initialize_ship() helper method.

PROJ-243 Phase 2: Verify the extracted helper runs the 4-step per-ship
initialization sequence: event bus wiring, component update, stat
recalculation, and derelict status check.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch

from game.simulation.systems.battle_engine import BattleEngine
from game.simulation.systems.battle_end_conditions import TeamEliminatedCondition


@pytest.fixture
def battle_engine():
    """Create a BattleEngine instance for testing with mocked dependencies."""
    with patch('game.simulation.systems.battle_engine.BattleLogger'):
        engine = BattleEngine()
        engine.ships = []
        engine.ai_controllers = []
        engine.tick_counter = 0
        engine.end_condition = TeamEliminatedCondition()
        engine.recent_beams = []
        return engine


def _make_mock_ship(team_id=0):
    """Create a mock ship with the attributes _initialize_ship needs."""
    ship = Mock()
    ship.name = "TestShip"
    ship.is_alive = True
    ship.is_derelict = False
    ship.team_id = team_id

    # combat_engine is a lazy property on real Ship; mock it with a nested mock
    ship.combat_engine = Mock()
    ship.combat_engine._event_bus = None

    # Components: one active, one inactive
    active_comp = Mock()
    active_comp.is_active = True
    inactive_comp = Mock()
    inactive_comp.is_active = False
    ship.get_all_components = Mock(return_value=[active_comp, inactive_comp])

    ship.recalculate_stats = Mock()
    ship.update_derelict_status = Mock()

    return ship, active_comp, inactive_comp


class TestInitializeShip:
    """Tests for BattleEngine._initialize_ship() helper."""

    def test_wires_event_bus(self, battle_engine):
        """_initialize_ship wires ship.combat_engine._event_bus to engine.combat_events."""
        ship, _, _ = _make_mock_ship()

        battle_engine._initialize_ship(ship)

        assert ship.combat_engine._event_bus is battle_engine.combat_events

    def test_calls_update_on_active_components(self, battle_engine):
        """_initialize_ship calls comp.update() for all active components."""
        ship, active_comp, inactive_comp = _make_mock_ship()

        battle_engine._initialize_ship(ship)

        active_comp.update.assert_called_once()
        inactive_comp.update.assert_not_called()

    def test_calls_recalculate_stats(self, battle_engine):
        """_initialize_ship calls ship.recalculate_stats()."""
        ship, _, _ = _make_mock_ship()

        battle_engine._initialize_ship(ship)

        ship.recalculate_stats.assert_called_once()

    def test_calls_update_derelict_status(self, battle_engine):
        """_initialize_ship calls ship.update_derelict_status()."""
        ship, _, _ = _make_mock_ship()

        battle_engine._initialize_ship(ship)

        ship.update_derelict_status.assert_called_once()
