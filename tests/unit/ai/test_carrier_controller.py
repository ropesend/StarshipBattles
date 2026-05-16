"""PROJ-FMS-C audit Fix 1 — CarrierAIController.

Adds a real production caller for the design-instance tactical launch
path: a carrier-side AI controller that calls
``BattleEngine.launch_fighters_in_battle`` when:

  - the ship has a ``TacticalFighterLaunchAbility`` on an active component
  - the ship has ``CarriedVehicle`` fighters in its ``carried_items``
  - an enemy is within the launch radius
  - the per-controller cooldown has elapsed

This replaces the legacy ``VehicleLaunchAbility`` auto-launch path in
``WeaponFiringSystem._process_hangar_launch`` (removed in the same pass).
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any, List
from unittest.mock import MagicMock

import pytest

from game.core.math import Vector2


class _StubComponent:
    """Minimal component stub: tracks one ability instance."""

    def __init__(self, ability_name: str, ability_obj: Any):
        self._name = ability_name
        self._ab = ability_obj
        self.is_active = True
        self.is_operational = True

    def has_ability(self, name: str) -> bool:
        return name == self._name

    def get_ability(self, name: str) -> Any:
        return self._ab if name == self._name else None

    def get_abilities(self, name: str) -> List[Any]:
        return [self._ab] if name == self._name else []


def _make_tactical_launch_ability(*, capacity: int = 2, cycle_time: float = 6.0):
    return SimpleNamespace(capacity_per_action=capacity, cycle_time=cycle_time)


def _make_carrier_ship(
    *,
    pos: Vector2 = Vector2(0.0, 0.0),
    carried_items: List[Any] | None = None,
    tactical: bool = True,
) -> MagicMock:
    ship = MagicMock()
    ship.is_alive = True
    ship.is_derelict = False
    ship.team_id = 0
    ship.position = pos
    ship.velocity = Vector2(0, 0)
    ship.angle = 0
    ship.radius = 20.0
    ship.color = (255, 255, 255)
    ship.theme_id = "Federation"
    ship.vehicle_type = "Ship"
    ship.carried_items = carried_items or []
    if tactical:
        comp = _StubComponent("TacticalFighterLaunch", _make_tactical_launch_ability())
    else:
        comp = _StubComponent("VehicleLaunch", _make_tactical_launch_ability())
    ship.iter_components = MagicMock(return_value=[("INNER", comp)])
    ship.get_all_components = MagicMock(return_value=[comp])
    return ship


def _make_enemy_ship(pos: Vector2) -> MagicMock:
    enemy = MagicMock()
    enemy.is_alive = True
    enemy.is_derelict = False
    enemy.team_id = 1
    enemy.position = pos
    return enemy


def _make_fighter_cv():
    from game.strategy.data.carried_vehicle import CarriedVehicle
    return CarriedVehicle(
        design_id="test_fighter",
        design_data={
            "name": "Test Fighter",
            "vehicle_type": "Fighter",
            "layers": {"CORE": [{"id": "hull_fighter_small"}]},
        },
        vehicle_type="fighter",
        mass=20.0,
        current_hp=80,
    )


def _make_engine_stub() -> MagicMock:
    engine = MagicMock()
    engine.launch_fighters_in_battle = MagicMock(return_value=[])
    return engine


def _make_grid_stub(enemies: List[Any]) -> MagicMock:
    grid = MagicMock()
    grid.query_radius_exact = MagicMock(return_value=enemies)
    return grid


# ---------------------------------------------------------------------------
# Tests for CarrierAIController (currently failing - class does not exist)
# ---------------------------------------------------------------------------


def test_carrier_controller_launches_when_enemy_in_range_and_cargo_ready():
    """Carrier with loaded fighters + enemy in range → engine launch call."""
    from game.ai.carrier_controller import CarrierAIController

    cv = _make_fighter_cv()
    carrier = _make_carrier_ship(carried_items=[cv.to_dict()])
    enemy = _make_enemy_ship(pos=Vector2(500.0, 0.0))
    engine = _make_engine_stub()
    grid = _make_grid_stub([enemy])

    from game.ai.interfaces.controllable import ShipControllableAdapter
    import random
    adapter = ShipControllableAdapter(carrier)
    ctrl = CarrierAIController(
        adapter, grid, enemy_team_id=1, rng=random.Random(0), engine=engine,
    )
    ctrl.update()

    assert engine.launch_fighters_in_battle.called
    args, kwargs = engine.launch_fighters_in_battle.call_args
    assert args[0] is carrier
    assert len(args[1]) >= 1
    # The popped CV must be removed from the carrier's carried_items.
    assert len(carrier.carried_items) == 0


def test_carrier_controller_does_not_launch_without_enemy():
    """No enemy in range → no launch."""
    from game.ai.carrier_controller import CarrierAIController

    cv = _make_fighter_cv()
    carrier = _make_carrier_ship(carried_items=[cv.to_dict()])
    engine = _make_engine_stub()
    grid = _make_grid_stub([])

    from game.ai.interfaces.controllable import ShipControllableAdapter
    import random
    adapter = ShipControllableAdapter(carrier)
    ctrl = CarrierAIController(
        adapter, grid, enemy_team_id=1, rng=random.Random(0), engine=engine,
    )
    ctrl.update()

    assert not engine.launch_fighters_in_battle.called


def test_carrier_controller_does_not_launch_without_loaded_fighters():
    """No loaded fighters → no launch."""
    from game.ai.carrier_controller import CarrierAIController

    carrier = _make_carrier_ship(carried_items=[])  # empty bay
    enemy = _make_enemy_ship(pos=Vector2(500.0, 0.0))
    engine = _make_engine_stub()
    grid = _make_grid_stub([enemy])

    from game.ai.interfaces.controllable import ShipControllableAdapter
    import random
    adapter = ShipControllableAdapter(carrier)
    ctrl = CarrierAIController(
        adapter, grid, enemy_team_id=1, rng=random.Random(0), engine=engine,
    )
    ctrl.update()

    assert not engine.launch_fighters_in_battle.called


def test_carrier_controller_respects_cooldown_between_waves():
    """After a launch, cooldown must elapse before the next wave fires."""
    from game.ai.carrier_controller import CarrierAIController

    cvs = [_make_fighter_cv().to_dict() for _ in range(4)]
    carrier = _make_carrier_ship(carried_items=list(cvs))
    enemy = _make_enemy_ship(pos=Vector2(500.0, 0.0))
    engine = _make_engine_stub()
    grid = _make_grid_stub([enemy])

    from game.ai.interfaces.controllable import ShipControllableAdapter
    import random
    adapter = ShipControllableAdapter(carrier)
    ctrl = CarrierAIController(
        adapter, grid, enemy_team_id=1, rng=random.Random(0), engine=engine,
    )

    # First tick: launches a wave.
    ctrl.update()
    assert engine.launch_fighters_in_battle.call_count == 1
    # Second tick immediately after: cooldown still active → no launch.
    ctrl.update()
    assert engine.launch_fighters_in_battle.call_count == 1


def test_carrier_controller_skips_when_only_legacy_vehicle_launch():
    """A ship with only the legacy VehicleLaunch ability does NOT auto-launch.

    Production guarantee post-audit-fix: only ``TacticalFighterLaunchAbility``
    drives auto-launch. The legacy ``VehicleLaunchAbility`` weapon-firing
    auto-launch path has been removed.
    """
    from game.ai.carrier_controller import CarrierAIController

    cv = _make_fighter_cv()
    carrier = _make_carrier_ship(carried_items=[cv.to_dict()], tactical=False)
    enemy = _make_enemy_ship(pos=Vector2(500.0, 0.0))
    engine = _make_engine_stub()
    grid = _make_grid_stub([enemy])

    from game.ai.interfaces.controllable import ShipControllableAdapter
    import random
    adapter = ShipControllableAdapter(carrier)
    ctrl = CarrierAIController(
        adapter, grid, enemy_team_id=1, rng=random.Random(0), engine=engine,
    )
    ctrl.update()

    assert not engine.launch_fighters_in_battle.called
