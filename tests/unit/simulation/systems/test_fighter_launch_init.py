"""
Tests for fighter launch initialization via BattleEngine.update().

PROJ-243 Phase 3: Verify that fighters launched via LAUNCH attack type
go through add_ship_mid_battle() and receive full initialization
(event bus, component update, stats, derelict check, aura registration).
"""
import pytest
from unittest.mock import Mock, patch

from game.simulation.systems.battle_engine import BattleEngine
from game.simulation.systems.battle_end_conditions import NeverCondition
from game.core.constants import AttackType
from game.core.math import Vector2


@pytest.fixture
def fighter_launch_engine(fresh_registries):
    """Create a BattleEngine set up for a fighter launch test.

    Returns (engine, source_ship) where source_ship has a LAUNCH attack
    ready to fire on the next update().
    """
    with patch('game.simulation.systems.battle_engine.BattleLogger'):
        # Create engine with AI factory
        mock_factory = Mock()
        mock_ai = Mock()
        mock_ai.update = Mock()
        mock_ai.ship = Mock()
        mock_factory.create_for_ship = Mock(return_value=mock_ai)
        mock_factory.create_for_ships = Mock(return_value=[mock_ai])
        mock_factory.set_grid = Mock()

        engine = BattleEngine(ai_factory=mock_factory)

        # Create a minimal source ship (mock, not real, for simplicity)
        source_ship = Mock()
        source_ship.name = "Carrier"
        source_ship.is_alive = True
        source_ship.is_derelict = False
        source_ship.team_id = 0
        source_ship.position = Vector2(100, 100)
        source_ship.velocity = Vector2(0, 0)
        source_ship.angle = 0
        source_ship.radius = 20
        source_ship.color = (255, 0, 0)
        source_ship.theme_id = "Federation"
        source_ship.registries = fresh_registries
        source_ship.get_all_components = Mock(return_value=[])
        source_ship.update = Mock()

        # The LAUNCH attack dict
        launch_attack = {
            'type': AttackType.LAUNCH,
            'source': source_ship,
            'hangar': Mock(),
            'fighter_class': 'Fighter (Small)',
            'origin': Vector2(100, 100),
        }

        # Source ship fires the launch on next update
        source_ship.just_fired_projectiles = [launch_attack]

        # Enemy ship (required so battle doesn't end immediately)
        enemy_ship = Mock()
        enemy_ship.name = "Enemy"
        enemy_ship.is_alive = True
        enemy_ship.is_derelict = False
        enemy_ship.team_id = 1
        enemy_ship.position = Vector2(500, 500)
        enemy_ship.velocity = Vector2(0, 0)
        enemy_ship.angle = 0
        enemy_ship.radius = 20
        enemy_ship.get_all_components = Mock(return_value=[])
        enemy_ship.just_fired_projectiles = []
        enemy_ship.update = Mock()
        enemy_ship.fleet_attack_bonus = 0.0
        enemy_ship.fleet_defense_bonus = 0.0

        # Initialize engine state manually (bypass start() complexity)
        engine.ships = [source_ship, enemy_ship]
        engine.ai_controllers = [mock_ai, Mock(update=Mock())]
        engine.tick_counter = 0
        engine.end_condition = NeverCondition()
        engine.recent_beams = []

        # Mark source ship as fleet-bonus aware
        source_ship.fleet_attack_bonus = 0.0
        source_ship.fleet_defense_bonus = 0.0

        return engine, source_ship


class TestFighterLaunchInitialization:
    """Tests for fighter launch via LAUNCH attack type."""

    def test_fighter_has_event_bus_set(self, fighter_launch_engine):
        """Fighter launched via LAUNCH has combat_engine._event_bus set."""
        engine, source_ship = fighter_launch_engine
        initial_ship_count = len(engine.ships)

        engine.update()

        # Find the newly added fighter
        assert len(engine.ships) > initial_ship_count
        fighter = engine.ships[-1]  # Last added
        assert "Wing" in fighter.name
        assert fighter.combat_engine._event_bus is engine.combat_events

    def test_fighter_is_in_ships_list(self, fighter_launch_engine):
        """Fighter launched via LAUNCH is in engine.ships."""
        engine, source_ship = fighter_launch_engine
        initial_ship_count = len(engine.ships)

        engine.update()

        assert len(engine.ships) == initial_ship_count + 1
        fighter = engine.ships[-1]
        assert "Wing" in fighter.name

    def test_fighter_has_ai_controller(self, fighter_launch_engine):
        """Fighter launched via LAUNCH has an AI controller in engine.ai_controllers."""
        engine, source_ship = fighter_launch_engine
        initial_ai_count = len(engine.ai_controllers)

        engine.update()

        assert len(engine.ai_controllers) == initial_ai_count + 1
