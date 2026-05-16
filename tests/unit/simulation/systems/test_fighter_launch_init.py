"""
Tests for fighter launch initialization via BattleEngine.update().

PROJ-243 Phase 3: Verify that fighters launched via LAUNCH attack type
go through add_ship_mid_battle() and receive full initialization
(event bus, component update, stats, derelict check, aura registration).

PROJ-FMS-C audit Fix 1: migrated from the legacy ``fighter_class``
class-string payload to the design-instance ``carried_vehicle`` payload.
The legacy spawn path was removed; spawning is now driven by
:func:`game.simulation.systems.attack_processor._spawn_from_carried_vehicle`
which uses :meth:`ShipSerializer.from_dict`.
"""
import pytest
from unittest.mock import Mock, patch

from game.simulation.systems.battle_engine import BattleEngine
from game.simulation.systems.battle_end_conditions import NeverCondition
from game.core.constants import AttackType
from game.core.math import Vector2
from game.strategy.data.carried_vehicle import CarriedVehicle


def _minimal_fighter_design() -> dict:
    return {
        "name": "Test Fighter",
        "ship_class": "Fighter (Small)",
        "vehicle_class": "Fighter (Small)",
        "vehicle_type": "Fighter",
        "theme_id": "Federation",
        "layers": {"CORE": [{"id": "hull_fighter_small"}]},
    }


@pytest.fixture
def fighter_launch_engine(fresh_registries):
    """Create a BattleEngine set up for a fighter launch test.

    Returns (engine, source_ship, mock_fighter) where source_ship has a
    design-instance LAUNCH attack queued up. ``ShipSerializer.from_dict``
    is patched to return ``mock_fighter`` so the test doesn't depend on
    a real fighter design definition.
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
        source_ship.ram_target = None

        cv = CarriedVehicle(
            design_id="test_fighter",
            design_data=_minimal_fighter_design(),
            vehicle_type="fighter",
            mass=20.0,
            current_hp=80,
        )
        launch_attack = {
            'type': AttackType.LAUNCH,
            'source': source_ship,
            'hangar': Mock(),
            'carried_vehicle': cv,
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
        enemy_ship.ram_target = None

        # Initialize engine state manually (bypass start() complexity)
        engine.ships = [source_ship, enemy_ship]
        engine.ai_controllers = [mock_ai, Mock(update=Mock())]
        engine.tick_counter = 0
        engine.end_condition = NeverCondition()
        engine.recent_beams = []

        # Mark source ship as fleet-bonus aware
        source_ship.fleet_attack_bonus = 0.0
        source_ship.fleet_defense_bonus = 0.0

        # Build the mock fighter that ShipSerializer.from_dict will return.
        mock_fighter = Mock()
        mock_fighter.team_id = 0
        mock_fighter.velocity = Vector2(0, 0)
        mock_fighter.angle = 0
        mock_fighter.is_alive = True
        mock_fighter.is_derelict = False
        mock_fighter.position = Vector2(100, 100)
        mock_fighter.just_fired_projectiles = []
        mock_fighter.update = Mock()
        mock_fighter.combat_engine = Mock()
        mock_fighter.get_all_components = Mock(return_value=[])
        mock_fighter.recalculate_stats = Mock()
        mock_fighter.update_derelict_status = Mock()
        mock_fighter.fleet_attack_bonus = 0.0
        mock_fighter.fleet_defense_bonus = 0.0
        mock_fighter.name = ""
        mock_fighter.current_hp = 80
        mock_fighter.components = {}
        # Ramming resolver iterates all ships; default Mocks auto-create
        # truthy attributes so explicitly clear ram_target.
        mock_fighter.ram_target = None

        return engine, source_ship, mock_fighter


class TestFighterLaunchInitialization:
    """Tests for fighter launch via LAUNCH attack type."""

    def test_fighter_has_event_bus_set(self, fighter_launch_engine):
        """Fighter launched via LAUNCH has its event bus set via set_event_bus.

        ``BattleEngine.add_ship_mid_battle`` calls
        ``ship.set_event_bus(engine.combat_events)`` so any spawned
        fighter gets the session bus. We pin that the call happened
        with the right bus rather than reaching into the inner
        ``combat_engine._event_bus`` attribute — the latter requires
        a real ``Ship`` instance to hold.
        """
        engine, source_ship, mock_fighter = fighter_launch_engine
        initial_ship_count = len(engine.ships)

        with patch(
            'game.simulation.entities.ship_serialization.ShipSerializer.from_dict',
            return_value=mock_fighter,
        ):
            engine.update()

        assert len(engine.ships) > initial_ship_count
        fighter = engine.ships[-1]
        assert "Wing" in fighter.name
        fighter.set_event_bus.assert_called_with(engine.combat_events)

    def test_fighter_is_in_ships_list(self, fighter_launch_engine):
        """Fighter launched via LAUNCH is in engine.ships."""
        engine, source_ship, mock_fighter = fighter_launch_engine
        initial_ship_count = len(engine.ships)

        with patch(
            'game.simulation.entities.ship_serialization.ShipSerializer.from_dict',
            return_value=mock_fighter,
        ):
            engine.update()

        assert len(engine.ships) == initial_ship_count + 1
        fighter = engine.ships[-1]
        assert "Wing" in fighter.name

    def test_fighter_has_ai_controller(self, fighter_launch_engine):
        """Fighter launched via LAUNCH has an AI controller in engine.ai_controllers."""
        engine, source_ship, mock_fighter = fighter_launch_engine
        initial_ai_count = len(engine.ai_controllers)

        with patch(
            'game.simulation.entities.ship_serialization.ShipSerializer.from_dict',
            return_value=mock_fighter,
        ):
            engine.update()

        assert len(engine.ai_controllers) == initial_ai_count + 1
