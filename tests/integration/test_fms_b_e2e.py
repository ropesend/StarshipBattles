"""PROJ-FMS-B Phase 5 — end-to-end integration tests.

Exercises the full mine lifecycle:

1. Mines authored as CarriedVehicle entries in a ship's bay.
2. Strategic LAY_MINES order popped through the command/order handler chain.
3. Enemy fleet enters the mined hex -> MinefieldResolver applies damage.
4. MineGroupService self-destruct prunes the group cleanly.

These tests stub-out the heavier objects (Empire, Galaxy) to keep the
integration focused on the mine plumbing while still exercising the
real Fleet / Order / Handler / Resolver code paths.
"""
from __future__ import annotations

import random
from types import SimpleNamespace

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.minefield_resolver import (
    MinefieldResolver,
    resolve_minefield_entry,
)
from game.strategy.engine.order_handlers.lay_mines import LayMinesOrderHandler
from game.strategy.services.mine_group_service import MineGroupService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _warhead_mine(design_id="mine_warhead_small", damage=80, hull_hp=30):
    return {
        "design_id": design_id,
        "design_data": {
            "name": design_id,
            "vehicle_class": "Mine (Small)",
            "layers": {
                "CORE": {
                    "components": [
                        {"id": "hull_mine_small",
                         "abilities": {"StructuralIntegrity": {"hp": hull_hp}}},
                        {"id": "warhead",
                         "abilities": {"Warhead": {"damage": damage}}},
                    ],
                },
            },
        },
        "vehicle_type": "mine",
        "mass": 5.0,
        "current_hp": hull_hp,
    }


def _laserhead_mine(design_id="mine_laserhead_small", damage=40, beam_range=600):
    return {
        "design_id": design_id,
        "design_data": {
            "name": design_id,
            "vehicle_class": "Mine (Small)",
            "layers": {
                "CORE": {
                    "components": [
                        {"id": "hull_mine_small",
                         "abilities": {"StructuralIntegrity": {"hp": 30}}},
                        {"id": "laserhead",
                         "abilities": {"Laserhead": {
                             "damage": damage,
                             "range": beam_range,
                             "base_accuracy": 5.0,
                             "accuracy_falloff": 0.001,
                             "consume_on_fire": True,
                         }}},
                    ],
                },
            },
        },
        "vehicle_type": "mine",
        "mass": 5.0,
        "current_hp": 30,
    }


class _StubEnemyShip:
    """Strategy-layer ShipInstance stand-in for the resolver."""

    def __init__(self, instance_id="enemy_ship", max_hp=400.0, total_defense_score=0.0):
        self.instance_id = instance_id
        self.design_id = "enemy_design"
        self.owner_id = 0
        self.name = instance_id
        self.design_data = {}
        self._max_hp = max_hp
        self.current_hp = int(max_hp)
        self.is_alive = True
        self.is_derelict = False
        self.carried_items = []
        self._defense = total_defense_score

    def get_calculated_stats(self):
        return {
            "max_hp": self._max_hp,
            "diameter": 320.0,  # dread-class
            "acceleration_rate": 10.0,
            "turn_speed": 30.0,
            "total_defense_score": self._defense,
        }


class _StubCarrier:
    def __init__(self, instance_id="carrier"):
        self.instance_id = instance_id
        self.design_id = "carrier_design"
        self.owner_id = 1
        self.name = instance_id
        self.design_data = {}
        self.current_hp = 100
        self.is_alive = True
        self.is_derelict = False
        self.carried_items = []

    # PROJ-431 Phase 1f: production callers read carried inventory via
    # the typed BayInventory. Derive it from the raw ``carried_items``
    # list so existing tests keep working.
    @property
    def bay_inventory(self):
        from game.strategy.data.bay_inventory import BayInventory, DropPod
        from game.strategy.data.carried_vehicle import (
            VALID_VEHICLE_TYPES, CarriedVehicle,
        )
        bay = []
        pods = []
        for item in self.carried_items:
            if isinstance(item, CarriedVehicle):
                bay.append(item)
            elif isinstance(item, dict) and str(
                item.get("vehicle_type", "")
            ).lower() in VALID_VEHICLE_TYPES:
                bay.append(CarriedVehicle.from_dict(item))
            elif isinstance(item, dict):
                pods.append(DropPod(
                    design_id=str(item.get("design_id", "")),
                    design_data=dict(item.get("design_data", {})),
                    mass=float(item.get("mass", 0.0)),
                    payload={
                        k: v for k, v in item.items()
                        if k not in {"design_id", "design_data", "mass"}
                    },
                ))
        return BayInventory(bay=bay, pods=pods)

    def set_bay_inventory(self, bi) -> None:
        new_items = [cv.to_dict() for cv in bi.bay]
        for pod in bi.pods:
            entry = {
                "design_id": pod.design_id,
                "design_data": pod.design_data,
                "mass": pod.mass,
            }
            entry.update(pod.payload)
            new_items.append(entry)
        self.carried_items = new_items


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_lay_mines_then_enemy_enters_takes_damage():
    """End-to-end: load mines, lay them, enemy enters, damage applied."""
    hex_c = HexCoord(0, 0)

    # 1. Build a carrier ship loaded with 6 warhead mines.
    carrier = _StubCarrier("carrier_1")
    carrier.owner_id = 1
    for _ in range(6):
        carrier.carried_items.append(_warhead_mine(damage=120))

    # 2. Build a fleet containing the carrier (owner empire).
    fleet = Fleet(
        fleet_id=10, owner_id=1, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    fleet.ships.append(carrier)
    owner_empire = SimpleNamespace(id=1, name="Owner", fleets=[fleet], deployed_groups=[])
    galaxy = SimpleNamespace(current_turn=1)

    # 3. Queue LAY_MINES order for 5 mines, run handler.
    order = Order(OrderType.LAY_MINES, target={
        "ship_instance_id": carrier.instance_id,
        "mine_design_id": "mine_warhead_small",
        "count": 5,
        "target_hex": hex_c,
    })
    fleet.add_order(order)
    handler = LayMinesOrderHandler()
    result = handler.execute_action_order(fleet, owner_empire, galaxy)
    assert result.success

    mine_groups = owner_empire.deployed_groups
    assert len(mine_groups) == 1
    mg = mine_groups[0]
    assert len(mg.mines) == 5

    # 4. Build an enemy fleet that enters the same hex.
    enemy_ship = _StubEnemyShip("dread_1", max_hp=2000.0)
    enemy_fleet = Fleet(
        fleet_id=20, owner_id=0, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    enemy_fleet.ships.append(enemy_ship)
    enemy_empire = SimpleNamespace(id=0, name="Invader", fleets=[enemy_fleet], deployed_groups=[])

    # 5. Force a trigger for deterministic test outcome.
    rng = random.Random()
    rng.random = lambda: 0.0
    rng.randrange = lambda n: 0

    res = resolve_minefield_entry(
        galaxy=galaxy,
        empires=[owner_empire, enemy_empire],
        fleet=enemy_fleet,
        rng=rng,
    )
    # At least one warhead detonation occurred.
    warhead_evs = [d for d in res.detonations if d.pass_kind == "warhead"]
    assert warhead_evs, "Expected at least one warhead detonation"
    assert enemy_ship.current_hp < 2000  # damage applied
    # Mine count decremented.
    assert len(mg.mines) < 5


def test_self_destruct_after_laying():
    """End-to-end: lay 4, self-destruct 2 of one design."""
    hex_c = HexCoord(0, 0)
    carrier = _StubCarrier("carrier_2")
    carrier.owner_id = 1
    for _ in range(4):
        carrier.carried_items.append(_warhead_mine())
    fleet = Fleet(fleet_id=10, owner_id=1, location=hex_c, speed=5.0)
    fleet.ships.append(carrier)
    owner_empire = SimpleNamespace(id=1, name="O", fleets=[fleet], deployed_groups=[])
    galaxy = SimpleNamespace(current_turn=1)

    fleet.add_order(Order(OrderType.LAY_MINES, target={
        "ship_instance_id": carrier.instance_id,
        "mine_design_id": "mine_warhead_small",
        "count": 4,
        "target_hex": hex_c,
    }))
    LayMinesOrderHandler().execute_action_order(fleet, owner_empire, galaxy)
    mg = owner_empire.deployed_groups[0]
    assert len(mg.mines) == 4

    svc = MineGroupService()
    svc.self_destruct(mg, owner_empire, {"mine_warhead_small": 2})
    assert len(mg.mines) == 2


def test_friendly_fleet_does_not_trigger_on_entry():
    """Friendly fleet at a mined hex never rolls mine triggers."""
    hex_c = HexCoord(0, 0)

    # Owner lays 5 mines.
    carrier = _StubCarrier("carrier_1")
    carrier.owner_id = 1
    for _ in range(5):
        carrier.carried_items.append(_warhead_mine())
    laying_fleet = Fleet(fleet_id=10, owner_id=1, location=hex_c, speed=5.0)
    laying_fleet.ships.append(carrier)
    owner_empire = SimpleNamespace(id=1, name="O", fleets=[laying_fleet], deployed_groups=[])
    galaxy = SimpleNamespace(current_turn=1)
    laying_fleet.add_order(Order(OrderType.LAY_MINES, target={
        "ship_instance_id": carrier.instance_id,
        "mine_design_id": "mine_warhead_small",
        "count": 5,
        "target_hex": hex_c,
    }))
    LayMinesOrderHandler().execute_action_order(laying_fleet, owner_empire, galaxy)

    # Owner brings a friendly fleet into the same hex.
    friendly_ship = _StubEnemyShip("friendly_1", max_hp=400.0)
    friendly_ship.owner_id = 1
    friendly_fleet = Fleet(fleet_id=99, owner_id=1, location=hex_c, speed=5.0)
    friendly_fleet.ships.append(friendly_ship)

    res = resolve_minefield_entry(
        galaxy=galaxy,
        empires=[owner_empire],
        fleet=friendly_fleet,
    )
    assert res.detonations == []
    assert friendly_ship.current_hp == 400


def test_mixed_warhead_and_laserhead_minefield():
    """Mixed-design mine_group: both passes run per entering ship."""
    hex_c = HexCoord(0, 0)
    carrier = _StubCarrier("carrier_mix")
    carrier.owner_id = 1
    for _ in range(3):
        carrier.carried_items.append(_warhead_mine())
    for _ in range(3):
        carrier.carried_items.append(_laserhead_mine())
    laying_fleet = Fleet(fleet_id=10, owner_id=1, location=hex_c, speed=5.0)
    laying_fleet.ships.append(carrier)
    owner_empire = SimpleNamespace(id=1, name="O", fleets=[laying_fleet], deployed_groups=[])
    galaxy = SimpleNamespace(current_turn=1)

    # Lay all 3 warheads first.
    laying_fleet.add_order(Order(OrderType.LAY_MINES, target={
        "ship_instance_id": carrier.instance_id,
        "mine_design_id": "mine_warhead_small",
        "count": 3,
        "target_hex": hex_c,
    }))
    LayMinesOrderHandler().execute_action_order(laying_fleet, owner_empire, galaxy)
    laying_fleet.add_order(Order(OrderType.LAY_MINES, target={
        "ship_instance_id": carrier.instance_id,
        "mine_design_id": "mine_laserhead_small",
        "count": 3,
        "target_hex": hex_c,
    }))
    LayMinesOrderHandler().execute_action_order(laying_fleet, owner_empire, galaxy)

    # PROJ-FMS-B audit Fix 4: two separate lay actions => two mine_groups
    # (no auto-merge). One holds the 3 warhead mines, the other holds the
    # 3 laserhead mines.
    mine_groups = owner_empire.deployed_groups
    assert len(mine_groups) == 2
    total_mines = sum(len(mg.mines) for mg in mine_groups)
    assert total_mines == 6
    for mg in mine_groups:
        mg.expected_hit_chance_threshold = 0.0  # always-fire laserheads

    # Enemy enters.
    enemy_ship = _StubEnemyShip("dread", max_hp=2000.0, total_defense_score=0.0)
    enemy_fleet = Fleet(fleet_id=20, owner_id=0, location=hex_c, speed=5.0)
    enemy_fleet.ships.append(enemy_ship)
    enemy_empire = SimpleNamespace(id=0, name="E", fleets=[enemy_fleet], deployed_groups=[])

    rng = random.Random()
    rng.random = lambda: 0.0
    rng.randrange = lambda n: 0
    res = resolve_minefield_entry(
        galaxy=galaxy,
        empires=[owner_empire, enemy_empire],
        fleet=enemy_fleet,
        rng=rng,
    )
    pass_kinds = {d.pass_kind for d in res.detonations}
    assert "warhead" in pass_kinds
    assert "laserhead" in pass_kinds


def test_spec_compiler_filters_mine_groups_and_wires_resolver():
    """PROJ-FMS-B audit Fix 2: when ``build_strategy_battle_spec`` sees
    a ``mine_group`` Fleet among the fleets entering combat:

    1. The mine_group is FILTERED OUT of team construction — the
       synthetic mine_carrier ShipInstance does NOT become a ShipSpec
       on its own team.
    2. The spec carries ``_mine_groups`` / ``_owner_to_team_id`` for the
       caller to wire :class:`TacticalMineResolver` with.
    3. The ``build_mine_resolver_setup`` helper attaches one resolver
       per mine_group to ``engine.mine_resolvers`` with the correct
       ``_owner_team_id`` so friendly fire is filtered.
    4. The post-battle hook calls ``writeback_to_mine_group`` for each
       mine_group, and empty groups are pruned from their empire.
    """
    from unittest.mock import MagicMock
    from game.strategy.combat.battle_assembly import (
        build_strategy_battle_assembly,
    )
    from game.strategy.data.fleet import Fleet

    hex_c = HexCoord(0, 0)

    # Set up: owner empire has a mine_group (1 mine), enemy empire has a
    # combat fleet with one ship. The strategic resolver hands all three
    # fleets (owner's combat fleet + mine_group + enemy combat fleet) to
    # the spec compiler.
    owner_combat_carrier = _StubCarrier("owner_carrier")
    owner_combat_carrier.owner_id = 1
    owner_combat_fleet = Fleet(
        fleet_id=11, owner_id=1, location=hex_c, speed=5.0, group_kind="fleet",
    )
    owner_combat_fleet.ships.append(owner_combat_carrier)
    owner_combat_carrier.design_id = "ship_with_layers"
    owner_combat_carrier.design_data = {"theme_id": "Federation"}
    owner_combat_carrier.components = {}
    owner_combat_carrier.name = "OwnerShip"

    enemy_ship = _StubEnemyShip("enemy_1", max_hp=200.0)
    enemy_ship.components = {}
    enemy_ship.name = "Enemy"
    enemy_ship.design_data = {"theme_id": "Federation"}
    enemy_fleet = Fleet(
        fleet_id=20, owner_id=0, location=hex_c, speed=5.0, group_kind="fleet",
    )
    enemy_fleet.ships.append(enemy_ship)

    # Build the mine_group via the order handler so it's real-shaped.
    mine_carrier = _StubCarrier("mine_carrier")
    mine_carrier.owner_id = 1
    mine_carrier.carried_items.append(_warhead_mine(damage=80))
    lay_fleet = Fleet(fleet_id=10, owner_id=1, location=hex_c, speed=5.0)
    lay_fleet.ships.append(mine_carrier)
    owner_empire = SimpleNamespace(
        id=1, name="Owner", fleets=[lay_fleet, owner_combat_fleet],
        deployed_groups=[],
    )
    enemy_empire = SimpleNamespace(id=0, name="Enemy", fleets=[enemy_fleet], deployed_groups=[])
    galaxy = SimpleNamespace(current_turn=1)
    lay_fleet.add_order(Order(OrderType.LAY_MINES, target={
        "ship_instance_id": mine_carrier.instance_id,
        "mine_design_id": "mine_warhead_small",
        "count": 1,
        "target_hex": hex_c,
    }))
    LayMinesOrderHandler().execute_action_order(lay_fleet, owner_empire, galaxy)
    mine_groups_at_hex = owner_empire.deployed_groups
    assert len(mine_groups_at_hex) == 1
    mg = mine_groups_at_hex[0]

    # Build the assembly. We use registries=MagicMock() since we are not
    # going to materialize ships — we only inspect the spec's structure
    # and the wiring callbacks.
    # PROJ-431 Phase 2: mine groups arrive via ``empire.deployed_groups``,
    # NOT via the fleets list.
    assembly = build_strategy_battle_assembly(
        [enemy_fleet, owner_combat_fleet],
        empires={0: enemy_empire, 1: owner_empire},
        registries=MagicMock(),
        post_battle_hook=None,  # let the compiler build the real hook
    )
    spec = assembly.spec

    # (1) Mine_group is NOT a team in the spec — only the two combat
    # fleets produce teams.
    team_count = len(spec.teams)
    assert team_count == 2, (
        f"Expected exactly 2 combat teams (mine_group filtered out), got "
        f"{team_count}."
    )

    # (2) PROJ-426: mine_groups + owner_to_team_id now live on
    # `assembly.extensions`, no longer on the spec.
    assert assembly.extensions.mine_groups == (mg,)
    owner_map = assembly.extensions.owner_to_team_id
    assert 1 in owner_map  # owner empire is in the battle

    # (3) The PreTickBattleSetupRegistry's composed callback — the same
    # callable the simulation adapter feeds into `run_battle` via
    # `pre_tick_loop_callback` — wires `engine.mine_resolvers`. We invoke
    # the public seam here rather than reaching into the underlying
    # `build_mine_resolver_setup` helper so the integration exercises
    # the exact code path the runtime uses (Codex Phase 6 follow-up).
    composed = assembly.pre_tick_setup.composed_callback()
    assert composed is not None, (
        "composed_callback() must be non-None when a mine_group is in the "
        "battle — the registry should have a 'mine' setup registered."
    )
    fake_engine = SimpleNamespace(mine_resolvers=[])
    composed(fake_engine)
    assert len(fake_engine.mine_resolvers) == 1
    resolver = fake_engine.mine_resolvers[0]
    assert getattr(resolver, "_owner_team_id", None) == owner_map[1]
    # The resolver should have one mine entity for the one laid mine.
    assert len(resolver.mines) == 1
    # The mine_group also carries a back-reference for writeback.
    assert getattr(mg, "_tactical_resolver", None) is resolver


def test_post_battle_hook_calls_writeback_and_prunes_empty_mine_group():
    """PROJ-FMS-B audit Fix 2: the spec compiler's post-battle hook drives
    ``writeback_to_mine_group`` for every mine_group attached to the
    spec, and prunes any mine_group whose carrier ends up with empty
    inventory.
    """
    from unittest.mock import MagicMock
    from game.strategy.combat.battle_assembly import (
        build_strategy_battle_assembly,
    )
    from game.strategy.data.fleet import Fleet

    hex_c = HexCoord(0, 0)
    # Two real combat fleets to clear the 2-team minimum.
    s1 = _StubCarrier("ship_owner")
    s1.owner_id = 1
    s1.design_id = "d"
    s1.design_data = {"theme_id": "Federation"}
    s1.name = "owner"
    s1.components = {}
    owner_combat = Fleet(fleet_id=11, owner_id=1, location=hex_c, speed=5.0)
    owner_combat.ships.append(s1)
    s2 = _StubEnemyShip("ship_enemy")
    s2.design_data = {"theme_id": "Federation"}
    s2.name = "enemy"
    s2.components = {}
    enemy_combat = Fleet(fleet_id=20, owner_id=0, location=hex_c, speed=5.0)
    enemy_combat.ships.append(s2)

    # Lay 2 mines for the owner.
    carrier = _StubCarrier("mine_carrier")
    carrier.owner_id = 1
    for _ in range(2):
        carrier.carried_items.append(_warhead_mine(damage=50))
    lay_fleet = Fleet(fleet_id=10, owner_id=1, location=hex_c, speed=5.0)
    lay_fleet.ships.append(carrier)
    owner_empire = SimpleNamespace(
        id=1, name="O", fleets=[lay_fleet, owner_combat],
        deployed_groups=[],
    )
    enemy_empire = SimpleNamespace(id=0, name="E", fleets=[enemy_combat], deployed_groups=[])
    galaxy = SimpleNamespace(current_turn=1)
    lay_fleet.add_order(Order(OrderType.LAY_MINES, target={
        "ship_instance_id": carrier.instance_id,
        "mine_design_id": "mine_warhead_small",
        "count": 2,
        "target_hex": hex_c,
    }))
    LayMinesOrderHandler().execute_action_order(lay_fleet, owner_empire, galaxy)
    mg = owner_empire.deployed_groups[0]

    # PROJ-431 Phase 2: mine groups arrive via ``empire.deployed_groups``,
    # NOT via the fleets list.
    assembly = build_strategy_battle_assembly(
        [enemy_combat, owner_combat],
        empires={0: enemy_empire, 1: owner_empire},
        registries=MagicMock(),
    )
    spec = assembly.spec

    # Wire the resolver onto the mine_group then simulate "all mines
    # consumed during battle" by marking every tactical entity consumed.
    # Use the assembly's composed pre-tick callback — the same surface
    # the simulation adapter feeds into `run_battle` — rather than the
    # underlying `build_mine_resolver_setup` helper (Codex Phase 6
    # follow-up: exercise the integration seam, not a private helper).
    composed = assembly.pre_tick_setup.composed_callback()
    assert composed is not None
    fake_engine = SimpleNamespace(mine_resolvers=[])
    composed(fake_engine)
    resolver = fake_engine.mine_resolvers[0]
    for entity in resolver.mines:
        entity.consumed = True

    # Invoke the post-battle hook with a minimal outcome.
    outcome = SimpleNamespace(teams=[
        SimpleNamespace(team_id=0, ships=[]),
        SimpleNamespace(team_id=1, ships=[]),
    ])
    spec.post_battle_hook(outcome)

    # Writeback ran: mine inventory is empty.
    assert mg.mines == []
    # Empty MineGroup pruned from owner's deployed_groups list.
    assert mg not in owner_empire.deployed_groups


def test_insufficient_mines_returns_clean_failure():
    """No partial consumption when fewer mines available than requested."""
    hex_c = HexCoord(0, 0)
    carrier = _StubCarrier("carrier_x")
    carrier.owner_id = 1
    carrier.carried_items.append(_warhead_mine())
    fleet = Fleet(fleet_id=10, owner_id=1, location=hex_c, speed=5.0)
    fleet.ships.append(carrier)
    owner_empire = SimpleNamespace(id=1, name="O", fleets=[fleet], deployed_groups=[])
    galaxy = SimpleNamespace(current_turn=1)
    fleet.add_order(Order(OrderType.LAY_MINES, target={
        "ship_instance_id": carrier.instance_id,
        "mine_design_id": "mine_warhead_small",
        "count": 5,  # only 1 available
        "target_hex": hex_c,
    }))
    result = LayMinesOrderHandler().execute_action_order(
        fleet, owner_empire, galaxy,
    )
    assert not result.success
    # No partial consumption — carrier still holds 1.
    assert len(carrier.carried_items) == 1
