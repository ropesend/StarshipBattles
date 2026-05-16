"""PROJ-FMS-C Phase 2 — FighterAIController tests."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.ai.fighter_controller import FighterAIController
from game.core.math import Vector2


class _StubGrid:
    """Spatial grid stub used by ``_find_enemies_in_radius`` indirectly."""

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
    adapter.get_movement_policy.return_value = "kite_max"
    adapter.get_max_targets.return_value = 1
    adapter.get_vehicle_type.return_value = "Fighter"
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
    adapter.ship.ship = adapter  # circumvent the unwrap in check_avoidance
    adapter.get_all_components.return_value = []
    return adapter


def _patch_combatant(enemy):
    """Patch the is_combatant TypeGuard so MagicMock enemies pass."""
    from game.core import protocols as _protocols

    enemy.team_id = enemy.team_id  # noqa
    return enemy


def test_no_enemies_results_in_no_target_and_no_thrust():
    enemies = []
    grid = _StubGrid(enemies)
    adapter = _make_controllable()
    ctrl = FighterAIController(adapter, grid, enemy_team_id=1)

    ctrl.update()

    adapter.set_current_target.assert_called_with(None)
    adapter.set_trigger_pulled.assert_called_with(False)
    adapter.thrust_forward.assert_not_called()


def test_targets_nearest_enemy_and_fires(monkeypatch):
    # Two enemies; controller must pick the nearer.
    near = _stub_ship(Vector2(50, 0), team_id=1)
    far = _stub_ship(Vector2(500, 0), team_id=1)
    grid = _StubGrid([near, far])

    # Patch is_combatant so MagicMock enemies pass the typeguard.
    monkeypatch.setattr(
        "game.ai.controller.is_combatant", lambda obj: True,
    )

    adapter = _make_controllable(Vector2(0, 0))
    ctrl = FighterAIController(adapter, grid, enemy_team_id=1)

    ctrl.update()

    # Trigger pulled (the weapon system handles range/cooldown).
    adapter.set_trigger_pulled.assert_called_with(True)
    # Nearer target selected.
    target_calls = [
        c.args[0] for c in adapter.set_current_target.call_args_list
    ]
    assert near in target_calls
    # Thrust forward toward the target.
    adapter.thrust_forward.assert_called()


def test_kamikaze_with_ram_target_defers_movement(monkeypatch):
    """When RamTargetAbility has a target_id set, FighterAIController
    delegates movement to the engine's RamTargetResolver and only sets
    the current target + trigger so non-ram weapons keep firing."""
    enemy = _stub_ship(Vector2(80, 0), team_id=1)
    grid = _StubGrid([enemy])
    enemy.id = 12345  # match the ram target_id below

    monkeypatch.setattr(
        "game.ai.controller.is_combatant", lambda obj: True,
    )

    adapter = _make_controllable(Vector2(0, 0))

    # Build a fake RamTargetAbility-like ability with a set target_id.
    ram_ability = MagicMock()
    type(ram_ability).__name__ = "RamTargetAbility"
    ram_ability.target_id = 12345

    fake_comp = MagicMock()
    fake_comp.is_active = True
    fake_comp.ability_instances = [ram_ability]
    adapter.get_all_components.return_value = [fake_comp]

    ctrl = FighterAIController(adapter, grid, enemy_team_id=1)
    ctrl.update()

    # The controller sets the target + trigger.
    adapter.set_current_target.assert_called_with(enemy)
    adapter.set_trigger_pulled.assert_called_with(True)
    # Movement is NOT driven by FighterAIController on this tick — the
    # resolver handles intercept-and-pursue.
    adapter.thrust_forward.assert_not_called()


def test_dead_fighter_does_nothing():
    grid = _StubGrid([])
    adapter = _make_controllable()
    adapter.is_alive.return_value = False
    ctrl = FighterAIController(adapter, grid, enemy_team_id=1)
    ctrl.update()
    adapter.set_throttle.assert_not_called()
    adapter.set_current_target.assert_not_called()


def test_ai_factory_dispatches_fighter_controller(fresh_registries):
    """The AIControllerFactory must hand fighters a FighterAIController."""
    from game.ai.ai_factory import AIControllerFactory
    from game.engine.spatial import SpatialGrid
    from game.core.config import PhysicsConfig
    import random

    grid = SpatialGrid(cell_size=PhysicsConfig.SPATIAL_GRID_CELL_SIZE)
    factory = AIControllerFactory()
    factory.set_grid(grid)
    factory.set_rng(random.Random(0))

    fighter = MagicMock()
    fighter.vehicle_type = "Fighter"
    fighter.movement_policy = "kite_max"
    fighter.targeting_policy = "standard"

    ship = MagicMock()
    ship.vehicle_type = "Ship"
    ship.movement_policy = "kite_max"
    ship.targeting_policy = "standard"

    fighter_ai = factory.create_for_ship(fighter, enemy_team_id=1)
    ship_ai = factory.create_for_ship(ship, enemy_team_id=1)

    from game.ai.controller import AIController
    from game.ai.fighter_controller import FighterAIController

    assert isinstance(fighter_ai, FighterAIController)
    assert isinstance(ship_ai, AIController)
    assert not isinstance(ship_ai, FighterAIController)
