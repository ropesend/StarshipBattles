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


def _make_tactical_launch_ability(
    *,
    capacity: int = 2,
    cycle_time: float = 6.0,
    launch_rate_tons_per_sec: float = 100000.0,
):
    """QA-C: tactical launch abilities expose a mass-tons/sec budget.

    Default rate (100000 t/s) is intentionally huge so a single
    tick (0.01s) yields 1000t of budget — more than enough for the
    20t fighter stubs the legacy tests build. Keeps the "one tick =
    at least one launch" expectation in the original tests.
    """
    return SimpleNamespace(
        capacity_per_action=capacity,
        cycle_time=cycle_time,
        launch_rate_tons_per_sec=launch_rate_tons_per_sec,
    )


def _make_carrier_ship(
    *,
    pos: Vector2 = Vector2(0.0, 0.0),
    carried_items: List[Any] | None = None,
    tactical: bool = True,
) -> MagicMock:
    """Build a carrier mock with a typed ``bay_inventory`` view.

    PROJ-431 Phase 1e: ``CarrierAIController`` reads through
    ``carrier.bay_inventory.bay`` (homogeneous ``list[CarriedVehicle]``)
    and writes back via ``carrier.set_bay_inventory(...)``. The mock
    still mirrors the legacy ``carried_items`` list so existing
    assertions on ``len(carrier.carried_items)`` keep working — both
    views stay in lockstep through the test-local ``_set_bay_inventory``
    closure.
    """
    from game.strategy.data.bay_inventory import BayInventory
    from game.strategy.data.carried_vehicle import CarriedVehicle

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

    items = list(carried_items or [])

    # PROJ-431 Phase 1e: a lightweight wrapper that owns a mutable
    # ``carried_items`` list and exposes a ``bay_inventory`` view that
    # refreshes on every read. Attribute access falls through to the
    # underlying MagicMock for everything else (component iteration,
    # position, etc.). Using a wrapper rather than patching
    # ``type(MagicMock).bay_inventory`` keeps the override per-test —
    # touching the class would leak the property to every other
    # MagicMock in the suite.
    class _CarrierWrapper:
        def __init__(self, inner: MagicMock, carried: list[Any]) -> None:
            object.__setattr__(self, "_inner", inner)
            object.__setattr__(self, "carried_items", carried)

        @property
        def bay_inventory(self) -> BayInventory:
            # PROJ-431 Phase 1f: from_any deleted; explicit shape probe.
            from game.strategy.data.carried_vehicle import (
                VALID_VEHICLE_TYPES,
            )
            bay: list[CarriedVehicle] = []
            for entry in self.carried_items:
                if isinstance(entry, CarriedVehicle):
                    bay.append(entry)
                elif isinstance(entry, dict) and str(
                    entry.get("vehicle_type", "")
                ).lower() in VALID_VEHICLE_TYPES:
                    bay.append(CarriedVehicle.from_dict(entry))
            return BayInventory(bay=bay, pods=[])

        def set_bay_inventory(self, bi: BayInventory) -> None:
            object.__setattr__(
                self, "carried_items", [cv.to_dict() for cv in bi.bay]
            )

        def __getattr__(self, name: str) -> Any:
            return getattr(self._inner, name)

        def __setattr__(self, name: str, value: Any) -> None:
            if name == "carried_items":
                object.__setattr__(self, name, value)
            else:
                setattr(self._inner, name, value)

    if tactical:
        comp = _StubComponent("TacticalFighterLaunch", _make_tactical_launch_ability())
    else:
        comp = _StubComponent("VehicleLaunch", _make_tactical_launch_ability())
    ship.iter_components = MagicMock(return_value=[("INNER", comp)])
    ship.get_all_components = MagicMock(return_value=[comp])
    return _CarrierWrapper(ship, items)


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


def test_carrier_controller_respects_mass_budget_between_waves():
    """QA-C: with a low launch_rate_tons_per_sec, the mass budget
    rebuilds slowly. After spending the budget on a launch, the next
    immediate tick has too little budget to launch the next fighter.
    """
    from game.ai.carrier_controller import CarrierAIController

    # Slow rate: 1.0 t/s. Each tick adds 0.01t (TICK_RATE=0.01). A
    # 20t fighter needs 2000 ticks of accumulation.
    carrier = _make_carrier_ship(
        carried_items=[_make_fighter_cv().to_dict() for _ in range(4)]
    )
    slow_ability = _make_tactical_launch_ability(launch_rate_tons_per_sec=1.0)
    comp = _StubComponent("TacticalFighterLaunch", slow_ability)
    # Override the default launch ability the helper installed.
    carrier.iter_components = MagicMock(return_value=[("INNER", comp)])
    carrier.get_all_components = MagicMock(return_value=[comp])
    enemy = _make_enemy_ship(pos=Vector2(500.0, 0.0))
    engine = _make_engine_stub()
    grid = _make_grid_stub([enemy])

    from game.ai.interfaces.controllable import ShipControllableAdapter
    import random
    adapter = ShipControllableAdapter(carrier)
    ctrl = CarrierAIController(
        adapter, grid, enemy_team_id=1, rng=random.Random(0), engine=engine,
    )
    # Pre-warm the budget enough for exactly one 20t fighter.
    ctrl._mass_budget_by_ability["TacticalFighterLaunch"] = 20.0

    # First tick: budget grows by 0.01t and 20.01t covers exactly one launch.
    ctrl.update()
    assert engine.launch_fighters_in_battle.call_count == 1
    # Second tick: only 0.01t accumulated since the spend; can't launch.
    ctrl.update()
    assert engine.launch_fighters_in_battle.call_count == 1


def test_carrier_controller_mass_budget_launches_variable_mass_fighters():
    """QA-C: a 100 t/s bay launches a small fighter every tick it can
    afford the mass, and stops when the next-in-line fighter exceeds
    the residual budget.
    """
    from game.ai.carrier_controller import CarrierAIController
    from game.strategy.data.carried_vehicle import CarriedVehicle

    # Variable-mass payload: 30t + 30t + 50t = 110t total. With a
    # 100 t/s rate the first tick accumulates 1.0t; pre-warm to 60.5t
    # so the controller fits two 30t fighters in one launch, leaving
    # 0.5t residual that can't fit the 50t bomber.
    light_a = CarriedVehicle(
        design_id="lite", design_data={"name": "lite"},
        vehicle_type="fighter", mass=30.0, current_hp=10,
    )
    light_b = CarriedVehicle(
        design_id="lite", design_data={"name": "lite"},
        vehicle_type="fighter", mass=30.0, current_hp=10,
    )
    heavy = CarriedVehicle(
        design_id="bomber", design_data={"name": "bomber"},
        vehicle_type="fighter", mass=50.0, current_hp=10,
    )
    carrier = _make_carrier_ship(
        carried_items=[light_a.to_dict(), light_b.to_dict(), heavy.to_dict()]
    )
    ability = _make_tactical_launch_ability(launch_rate_tons_per_sec=100.0)
    comp = _StubComponent("TacticalFighterLaunch", ability)
    # Override the default launch ability the helper installed.
    carrier.iter_components = MagicMock(return_value=[("INNER", comp)])
    carrier.get_all_components = MagicMock(return_value=[comp])
    enemy = _make_enemy_ship(pos=Vector2(500.0, 0.0))
    engine = _make_engine_stub()
    grid = _make_grid_stub([enemy])

    from game.ai.interfaces.controllable import ShipControllableAdapter
    import random
    adapter = ShipControllableAdapter(carrier)
    ctrl = CarrierAIController(
        adapter, grid, enemy_team_id=1, rng=random.Random(0), engine=engine,
    )
    # Pre-warm budget: 60.5t. Per-tick tick adds 1.0t -> 61.5t entering
    # the pop loop. Two 30t fighters fit (61.5 - 60 = 1.5t remaining),
    # but the 50t heavy does not.
    ctrl._mass_budget_by_ability["TacticalFighterLaunch"] = 60.5

    ctrl.update()
    assert engine.launch_fighters_in_battle.call_count == 1
    _args, _kwargs = engine.launch_fighters_in_battle.call_args
    assert len(_args[1]) == 2  # the two lights, heavy stays in the bay
    assert len(carrier.carried_items) == 1
    # Residual budget = 61.5 - 60.0 = 1.5t.
    assert abs(ctrl._mass_budget_by_ability["TacticalFighterLaunch"] - 1.5) < 1e-9


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
