"""
Tests for BattleEngine.add_ship_mid_battle() initialization.

PROJ-243 Phase 3: Verify that add_ship_mid_battle() runs the full
initialization sequence (_initialize_ship + aura registration) so
that reinforcement ships have event bus wiring, stats, and fleet bonuses.
"""
import pytest
from unittest.mock import Mock, patch

from game.simulation.systems.battle_engine import BattleEngine
from game.simulation.systems.battle_end_conditions import TeamEliminatedCondition


@pytest.fixture
def battle_engine():
    """Create a BattleEngine with a mock AI factory, ready for add_ship_mid_battle."""
    with patch('game.simulation.systems.battle_engine.BattleLogger'):
        engine = BattleEngine()
        engine.ships = []
        engine.ai_controllers = []
        engine.tick_counter = 0
        engine.end_condition = TeamEliminatedCondition()
        engine.recent_beams = []

        # Provide an AI factory so add_ship_mid_battle can create controllers
        mock_factory = Mock()
        mock_ai = Mock()
        mock_ai.ship = Mock()
        mock_ai.ship.ship = None  # Will be set per-call
        mock_factory.create_for_ship = Mock(return_value=mock_ai)
        engine._ai_factory = mock_factory

        return engine


def _make_mock_ship(team_id=0, name="ReinforcementShip"):
    """Create a mock ship suitable for add_ship_mid_battle."""
    ship = Mock()
    ship.name = name
    ship.is_alive = True
    ship.is_derelict = False
    ship.team_id = team_id
    ship.fleet_attack_bonus = 0.0
    ship.fleet_defense_bonus = 0.0

    # combat_engine with a writable _event_bus
    ship.combat_engine = Mock()
    ship.combat_engine._event_bus = None

    # Components - need is_active for _initialize_ship and is_operational + ability_instances for _scan_ship
    active_comp = Mock()
    active_comp.is_active = True
    active_comp.is_operational = True
    active_comp.ability_instances = []
    ship.get_all_components = Mock(return_value=[active_comp])

    ship.recalculate_stats = Mock()
    ship.update_derelict_status = Mock()

    return ship


class TestAddShipMidBattleInitialization:
    """Tests for add_ship_mid_battle() initialization steps."""

    def test_event_bus_wired(self, battle_engine):
        """Ship added via add_ship_mid_battle() has combat_engine._event_bus set."""
        ship = _make_mock_ship()

        battle_engine.add_ship_mid_battle(ship, team_id=0)

        assert ship.combat_engine._event_bus is battle_engine.combat_events

    def test_recalculate_stats_called(self, battle_engine):
        """Ship added via add_ship_mid_battle() has had recalculate_stats() called."""
        ship = _make_mock_ship()

        battle_engine.add_ship_mid_battle(ship, team_id=0)

        ship.recalculate_stats.assert_called_once()

    def test_update_derelict_status_called(self, battle_engine):
        """Ship added via add_ship_mid_battle() has had update_derelict_status() called."""
        ship = _make_mock_ship()

        battle_engine.add_ship_mid_battle(ship, team_id=0)

        ship.update_derelict_status.assert_called_once()

    def test_aura_manager_register_ship_called(self, battle_engine):
        """Ship added via add_ship_mid_battle() is registered with aura manager."""
        ship = _make_mock_ship()

        with patch.object(battle_engine.aura_manager, 'register_ship') as mock_register:
            battle_engine.add_ship_mid_battle(ship, team_id=0)
            mock_register.assert_called_once_with(ship, battle_engine.ships)

    def test_receives_existing_fleet_bonuses(self, battle_engine):
        """Ship added via add_ship_mid_battle() receives existing fleet bonuses.

        This test uses the real FleetAuraManager to verify end-to-end bonus
        propagation. The aura manager is already initialized by the engine.
        """
        from game.simulation.components.abilities.base import AbilityScope

        # Set up an existing ship that provides fleet-scope attack bonus
        provider = _make_mock_ship(team_id=0, name="Provider")
        ab = Mock()
        ab.value = 4.0
        ab.scope = AbilityScope.FLEET
        ab.stack_group = "sensors"
        type(ab).__name__ = "ToHitAttackModifier"

        comp = Mock()
        comp.name = "sensor_array"
        comp.is_operational = True
        comp.ability_instances = [ab]
        provider.get_all_components = Mock(return_value=[comp])

        # Put the provider in the battle and initialize aura manager
        battle_engine.ships = [provider]
        battle_engine.aura_manager.initialize([provider])
        assert provider.fleet_attack_bonus == 4.0

        # Add reinforcement
        reinforcement = _make_mock_ship(team_id=0, name="Reinforcement")
        battle_engine.add_ship_mid_battle(reinforcement, team_id=0)

        # Reinforcement should receive the fleet attack bonus
        assert reinforcement.fleet_attack_bonus == 4.0
