"""PROJ-FMS-C audit Fix 1 — carrier-AI auto-launch production wire-up.

Integration test that exercises the new design-instance tactical launch
path THROUGH the production AI dispatch:

  - The :class:`AIControllerFactory` is the real one (not a mock).
  - The factory's ``set_engine`` wiring is the production
    :meth:`BattleEngine.__init__` call site.
  - A ship with a ``TacticalFighterLaunchAbility`` component is built
    through :class:`AIControllerFactory.create_for_ship`; the controller
    that comes back must be a :class:`CarrierAIController`.
  - One tick of the controller, with a loaded fighter
    :class:`CarriedVehicle` in ``carried_items`` and an enemy in the
    spatial grid, must invoke :meth:`BattleEngine.launch_fighters_in_battle`
    and spawn a real design-backed fighter on the engine's ship list.

This is the missing production-reachability proof that the audit called
out: the resolver / action surface had no caller before the audit fix,
and the integration tests that existed drove
``launch_fighters_in_battle`` directly without going through the AI.
"""
from __future__ import annotations

import random
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from game.core.constants import LayerType
from game.core.math import Vector2
from game.simulation.systems.battle_engine import BattleEngine
from game.simulation.systems.battle_end_conditions import NeverCondition
from game.simulation.systems.fighter_reboard import ReboardTracker
from game.strategy.data.carried_vehicle import CarriedVehicle
from game.ai.ai_factory import AIControllerFactory
from game.ai.carrier_controller import CarrierAIController


def _minimal_fighter_design() -> dict:
    return {
        "name": "Test Fighter",
        "ship_class": "Fighter (Small)",
        "vehicle_class": "Fighter (Small)",
        "vehicle_type": "Fighter",
        "theme_id": "Federation",
        "layers": {
            "CORE": [
                {"id": "hull_fighter_small", "is_active": True},
                {"id": "fighter_cockpit", "is_active": True},
            ],
        },
    }


class _StubTacticalLaunchAbility:
    """Mirror of TacticalFighterLaunchAbility surface used by the controller."""

    def __init__(
        self,
        capacity_per_action: int = 2,
        cycle_time: float = 6.0,
        launch_rate_tons_per_sec: float = 100000.0,
    ):
        self.capacity_per_action = capacity_per_action
        self.cycle_time = cycle_time
        # QA-C: tactical throughput dial. Default to a high rate so the
        # 20t fighter stubs fit in a single-tick budget (10t per tick
        # would otherwise need to accumulate across several ticks).
        self.launch_rate_tons_per_sec = launch_rate_tons_per_sec


class _StubComponent:
    def __init__(self, ability_name: str, ability):
        self._n = ability_name
        self._a = ability
        self.is_active = True
        self.is_operational = True

    def has_ability(self, name: str) -> bool:
        return name == self._n

    def get_ability(self, name: str):
        return self._a if name == self._n else None

    def get_abilities(self, name: str):
        return [self._a] if name == self._n else []


def _make_carrier_ship(fresh_registries):
    """Carrier stub exposing the surface CarrierAIController + factory read.

    PROJ-431 Phase 1e: ``CarrierAIController`` reads through
    ``carrier.bay_inventory.bay``. The stub wraps a MagicMock with a
    typed view that refreshes from the mutable ``carried_items`` list
    on every read (and writes back through it on
    ``set_bay_inventory``). Tests can still ``append`` to
    ``carried_items`` after construction.
    """
    from game.strategy.data.bay_inventory import BayInventory
    from game.strategy.data.carried_vehicle import CarriedVehicle

    inner = MagicMock()
    inner.is_alive = True
    inner.is_derelict = False
    inner.team_id = 0
    inner.position = Vector2(0.0, 0.0)
    inner.velocity = Vector2(0, 0)
    inner.angle = 0
    inner.radius = 20
    inner.color = (255, 255, 255)
    inner.theme_id = "Federation"
    inner.vehicle_type = "Ship"
    inner.registries = fresh_registries
    inner.get_all_components = MagicMock(return_value=[])
    inner.update = MagicMock()
    inner.just_fired_projectiles = []
    inner.fleet_attack_bonus = 0.0
    inner.fleet_defense_bonus = 0.0
    # Tactical fighter launch ability mounted on a fake INNER hangar.
    hangar = _StubComponent("TacticalFighterLaunch", _StubTacticalLaunchAbility())
    inner.iter_components = MagicMock(return_value=[(LayerType.INNER, hangar)])

    class _CarrierWrapper:
        def __init__(self, m: MagicMock) -> None:
            object.__setattr__(self, "_inner", m)
            object.__setattr__(self, "carried_items", [])

        @property
        def bay_inventory(self) -> BayInventory:
            # PROJ-431 Phase 1f: from_any deleted; explicit shape probe
            # against the dict-list legacy ``carried_items`` shape.
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

        def __getattr__(self, name: str):
            return getattr(self._inner, name)

        def __setattr__(self, name: str, value) -> None:
            if name == "carried_items":
                object.__setattr__(self, name, value)
            else:
                setattr(self._inner, name, value)

    return _CarrierWrapper(inner)


def _make_enemy_ship() -> MagicMock:
    enemy = MagicMock()
    enemy.is_alive = True
    enemy.is_derelict = False
    enemy.team_id = 1
    enemy.position = Vector2(500.0, 0.0)
    # Make the spatial grid happy.
    enemy.radius = 10.0
    return enemy


def _make_engine(fresh_registries) -> BattleEngine:
    with patch("game.simulation.systems.battle_engine.BattleLogger"):
        factory = AIControllerFactory()
        engine = BattleEngine(ai_factory=factory)
        engine.end_condition = NeverCondition()
        engine.tick_counter = 0
        engine.recent_beams = []
        # Spec-compiler would normally install this; install manually so the
        # mid-battle launch path can register on the tracker.
        engine.reboard_tracker = ReboardTracker(battle_id=id(engine))
        # PROJ-312: the factory needs a seeded RNG before creating controllers.
        factory.set_rng(random.Random(0))
        return engine


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_factory_dispatches_carrier_to_carrier_ai_controller(fresh_registries):
    """A ship with TacticalFighterLaunchAbility → CarrierAIController."""
    engine = _make_engine(fresh_registries)
    carrier = _make_carrier_ship(fresh_registries)

    controller = engine._ai_factory.create_for_ship(carrier, enemy_team_id=1)
    assert isinstance(controller, CarrierAIController)


def test_carrier_ai_controller_drives_launch_via_engine_action_surface(
    fresh_registries,
):
    """Production AI path: factory build → tick → engine.launch_fighters_in_battle.

    The new design-instance tactical launch path is reachable end-to-end
    via the AI: no test calls ``launch_fighters_in_battle`` directly here.
    """
    engine = _make_engine(fresh_registries)
    carrier = _make_carrier_ship(fresh_registries)
    enemy = _make_enemy_ship()

    # Load a fighter into the carrier's bay.
    cv = CarriedVehicle(
        design_id="test_fighter",
        design_data=_minimal_fighter_design(),
        vehicle_type="fighter",
        mass=20.0,
        current_hp=80,
    )
    carrier.carried_items.append(cv.to_dict())

    # Insert carrier + enemy into the engine's grid so the controller's
    # spatial query sees the enemy.
    engine.ships = [carrier, enemy]
    engine.grid.insert(carrier)
    engine.grid.insert(enemy)

    # Build the controller via the production factory.
    controller = engine._ai_factory.create_for_ship(carrier, enemy_team_id=1)
    assert isinstance(controller, CarrierAIController)

    # Stub launch_fighters_in_battle so we can pin the call without
    # depending on the real ShipSerializer for design assembly.
    engine.launch_fighters_in_battle = MagicMock(return_value=[])

    # One AI tick.
    controller.update()

    assert engine.launch_fighters_in_battle.called, (
        "CarrierAIController must call engine.launch_fighters_in_battle "
        "on the production AI tick — this is the only production caller "
        "for the design-instance launch surface."
    )
    args, _kwargs = engine.launch_fighters_in_battle.call_args
    assert args[0] is carrier
    assert len(args[1]) == 1
    assert isinstance(args[1][0], CarriedVehicle)
    # The carried_items entry was popped from the carrier.
    assert carrier.carried_items == []


def test_carrier_ai_controller_no_enemy_does_not_launch(fresh_registries):
    """No enemy in spatial-grid radius → no engine launch call."""
    engine = _make_engine(fresh_registries)
    carrier = _make_carrier_ship(fresh_registries)

    cv = CarriedVehicle(
        design_id="test_fighter",
        design_data=_minimal_fighter_design(),
        vehicle_type="fighter",
        mass=20.0,
        current_hp=80,
    )
    carrier.carried_items.append(cv.to_dict())

    # Carrier alone in grid, no enemy.
    engine.ships = [carrier]
    engine.grid.insert(carrier)

    controller = engine._ai_factory.create_for_ship(carrier, enemy_team_id=1)
    engine.launch_fighters_in_battle = MagicMock(return_value=[])

    controller.update()
    assert not engine.launch_fighters_in_battle.called
    assert len(carrier.carried_items) == 1
