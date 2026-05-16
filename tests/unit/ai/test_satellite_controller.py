"""PROJ-FMS-D Phase 1 — SatelliteAIController tests.

Verifies the stationary-AI contract:
- Zero throttle / zero turn throttle every tick.
- Acquires nearest enemy and pulls the trigger when in range.
- Idles when no enemies are visible.
- Never engages avoidance / movement behaviors.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.ai.satellite_controller import SatelliteAIController
from game.core.math import Vector2


class _StubGrid:
    def __init__(self, entities):
        self._entities = entities

    def query_radius_exact(self, pos, radius):
        return list(self._entities)

    def query_radius(self, pos, radius):
        return list(self._entities)


def _stub_ship(pos: Vector2, team_id: int = 0, is_alive: bool = True):
    s = MagicMock()
    s.is_alive = is_alive
    s.team_id = team_id
    s.position = pos
    return s


def _make_controllable(adapter_pos: Vector2 = Vector2(0, 0)):
    adapter = MagicMock()
    adapter.is_alive.return_value = True
    adapter.get_team_id.return_value = 0
    adapter.get_position.return_value = adapter_pos
    adapter.get_targeting_policy.return_value = "standard"
    adapter.get_movement_policy.return_value = "stationary"
    adapter.get_max_targets.return_value = 1
    adapter.get_vehicle_type.return_value = "Satellite"
    adapter.get_current_target.return_value = None
    adapter.set_current_target = MagicMock()
    adapter.set_trigger_pulled = MagicMock()
    adapter.set_throttle = MagicMock()
    adapter.set_turn_throttle = MagicMock()
    adapter.set_secondary_targets = MagicMock()
    adapter.get_radius.return_value = 5.0
    adapter.get_rotation.return_value = 0.0
    adapter.rotate = MagicMock()
    adapter.thrust_forward = MagicMock()
    adapter.ship = MagicMock()
    adapter.ship.ship = adapter
    adapter.get_all_components.return_value = []
    return adapter


def test_satellite_never_thrusts_or_turns():
    """Zero throttles every tick — satellites are stationary emplacements."""
    grid = _StubGrid([])
    adapter = _make_controllable()
    ctrl = SatelliteAIController(adapter, grid, enemy_team_id=1)

    ctrl.update()
    adapter.set_throttle.assert_called_with(0.0)
    adapter.set_turn_throttle.assert_called_with(0.0)
    # Critically: never call thrust_forward.
    adapter.thrust_forward.assert_not_called()


def test_satellite_no_enemy_releases_trigger():
    grid = _StubGrid([])
    adapter = _make_controllable()
    ctrl = SatelliteAIController(adapter, grid, enemy_team_id=1)

    ctrl.update()
    adapter.set_current_target.assert_called_with(None)
    adapter.set_trigger_pulled.assert_called_with(False)


def test_satellite_targets_nearest_enemy_and_fires(monkeypatch):
    near = _stub_ship(Vector2(50, 0), team_id=1)
    far = _stub_ship(Vector2(500, 0), team_id=1)
    grid = _StubGrid([near, far])

    monkeypatch.setattr(
        "game.ai.controller.is_combatant", lambda obj: True,
    )

    adapter = _make_controllable(Vector2(0, 0))
    ctrl = SatelliteAIController(adapter, grid, enemy_team_id=1)
    ctrl.update()

    adapter.set_trigger_pulled.assert_called_with(True)
    target_calls = [
        c.args[0] for c in adapter.set_current_target.call_args_list
    ]
    assert near in target_calls
    # Even when firing, the satellite must remain stationary.
    adapter.thrust_forward.assert_not_called()
    # Throttle commands were zero before targeting.
    throttle_calls = [c.args[0] for c in adapter.set_throttle.call_args_list]
    turn_calls = [c.args[0] for c in adapter.set_turn_throttle.call_args_list]
    assert all(t == 0.0 for t in throttle_calls)
    assert all(t == 0.0 for t in turn_calls)


def test_satellite_dead_ship_skips_silently():
    adapter = _make_controllable()
    adapter.is_alive.return_value = False
    grid = _StubGrid([])
    ctrl = SatelliteAIController(adapter, grid, enemy_team_id=1)

    ctrl.update()
    # No state changes on a dead satellite.
    adapter.set_throttle.assert_not_called()
    adapter.set_turn_throttle.assert_not_called()
    adapter.set_current_target.assert_not_called()
    adapter.set_trigger_pulled.assert_not_called()


def test_satellite_does_not_chase_when_target_far(monkeypatch):
    """Even far-distant targets do not cause the satellite to move.

    The weapon system still gates on range; the AI just sets the
    target and pulls the trigger.
    """
    far = _stub_ship(Vector2(10000.0, 0.0), team_id=1)
    grid = _StubGrid([far])

    monkeypatch.setattr(
        "game.ai.controller.is_combatant", lambda obj: True,
    )

    adapter = _make_controllable(Vector2(0, 0))
    ctrl = SatelliteAIController(adapter, grid, enemy_team_id=1)
    ctrl.update()

    # Trigger pulled, but no movement.
    adapter.set_trigger_pulled.assert_called_with(True)
    adapter.thrust_forward.assert_not_called()
