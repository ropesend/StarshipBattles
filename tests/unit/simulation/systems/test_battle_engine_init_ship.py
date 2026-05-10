"""
Tests for the per-ship initialization sequence inside ``BattleEngine``.

PROJ-243 Phase 2 originally tested the extracted helper
``BattleEngine._initialize_ship`` directly. PROJ-322 Tasks 3.9 / 5.28
rewrote these tests to drive the engine through the public ``start()``
API instead — the helper is an implementation detail; what callers
observe is the post-start state of every ship that was passed in
(event bus wired, active components updated, stats recalculated,
derelict status refreshed).
"""
import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def battle_engine():
    """Build a `BattleEngine` with the bare minimum dependencies for ``start()``.

    The AI factory is replaced with a no-op fake so ``start_teams`` can
    take the ``elif self._ai_factory is not None`` branch without
    construction-time work; the alternative is to pass an explicit
    ``ai_controllers=[]`` list to every ``start()`` call below, which is
    noisier.
    """
    from game.simulation.systems.battle_engine import BattleEngine

    with patch("game.simulation.systems.battle_engine.BattleLogger"):
        engine = BattleEngine()
    return engine


def _make_mock_ship(team_id: int = 0):
    """Build a mock ship with the surface ``start()`` and ``_initialize_ship`` need."""
    ship = Mock()
    ship.name = "TestShip"
    ship.is_alive = True
    ship.is_derelict = False
    ship.team_id = team_id

    # Combat-engine plumbing for set_event_bus.
    ship.combat_engine = Mock()
    ship.combat_engine._event_bus = None

    def _set_event_bus(bus):
        ship.combat_engine._event_bus = bus

    ship.set_event_bus = Mock(side_effect=_set_event_bus)

    # Components — one active, one inactive. Both must expose iterable
    # attributes the post-start aura manager scans (`ability_instances`).
    active_comp = Mock()
    active_comp.is_active = True
    active_comp.is_operational = False  # skip aura scan
    active_comp.ability_instances = []
    inactive_comp = Mock()
    inactive_comp.is_active = False
    inactive_comp.is_operational = False
    inactive_comp.ability_instances = []
    ship.get_all_components = Mock(return_value=[active_comp, inactive_comp])

    # Real Ship surface that `start()` and the post-start sweep call.
    ship.recalculate_stats = Mock()
    ship.update_derelict_status = Mock()
    # `_log_initial_status` reads these — use cheap defaults so the log call
    # doesn't blow up when start() runs.
    ship.resources = Mock()
    ship.resources.get_value = Mock(return_value=100)
    ship.hp = 100
    ship.max_hp = 100
    ship.mass = 100
    ship.total_thrust = 50
    ship.turn_speed = 1.0
    ship.max_speed = 10.0
    return ship, active_comp, inactive_comp


class TestStartInitializesEachShip:
    """Driving ``BattleEngine.start()`` should run the per-ship init sequence."""

    def test_wires_event_bus_for_every_ship(self, battle_engine):
        """``start()`` wires ``ship.combat_engine._event_bus`` to ``engine.combat_events``."""
        ship_a, _, _ = _make_mock_ship(team_id=0)
        ship_b, _, _ = _make_mock_ship(team_id=1)

        battle_engine.start([ship_a], [ship_b], ai_controllers=[])

        assert ship_a.combat_engine._event_bus is battle_engine.combat_events
        assert ship_b.combat_engine._event_bus is battle_engine.combat_events

    def test_calls_update_on_active_components_only(self, battle_engine):
        """``start()`` calls ``comp.update()`` only on active components."""
        ship_a, active_comp, inactive_comp = _make_mock_ship(team_id=0)
        ship_b, _, _ = _make_mock_ship(team_id=1)

        battle_engine.start([ship_a], [ship_b], ai_controllers=[])

        active_comp.update.assert_called_once()
        inactive_comp.update.assert_not_called()

    def test_calls_recalculate_stats_for_every_ship(self, battle_engine):
        """``start()`` calls ``ship.recalculate_stats()`` for every ship passed in.

        Counted at-least-once: the post-start aura initialization may call it a
        second time for the modifier-stack pass; the public contract is only
        that every ship had its stats recalculated.
        """
        ship_a, _, _ = _make_mock_ship(team_id=0)
        ship_b, _, _ = _make_mock_ship(team_id=1)

        battle_engine.start([ship_a], [ship_b], ai_controllers=[])

        assert ship_a.recalculate_stats.call_count >= 1
        assert ship_b.recalculate_stats.call_count >= 1

    def test_calls_update_derelict_status_for_every_ship(self, battle_engine):
        """``start()`` calls ``ship.update_derelict_status()`` for every ship passed in."""
        ship_a, _, _ = _make_mock_ship(team_id=0)
        ship_b, _, _ = _make_mock_ship(team_id=1)

        battle_engine.start([ship_a], [ship_b], ai_controllers=[])

        ship_a.update_derelict_status.assert_called_once()
        ship_b.update_derelict_status.assert_called_once()
