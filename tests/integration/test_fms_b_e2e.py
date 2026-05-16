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
                        {"id": "warhead_small",
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
                        {"id": "laserhead_small",
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
    owner_empire = SimpleNamespace(id=1, name="Owner", fleets=[fleet])
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

    mine_groups = [
        f for f in owner_empire.fleets
        if getattr(f, "group_kind", "fleet") == "mine_group"
    ]
    assert len(mine_groups) == 1
    mg = mine_groups[0]
    assert len(mg.ships[0].carried_items) == 5

    # 4. Build an enemy fleet that enters the same hex.
    enemy_ship = _StubEnemyShip("dread_1", max_hp=2000.0)
    enemy_fleet = Fleet(
        fleet_id=20, owner_id=0, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    enemy_fleet.ships.append(enemy_ship)
    enemy_empire = SimpleNamespace(id=0, name="Invader", fleets=[enemy_fleet])

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
    assert len(mg.ships[0].carried_items) < 5


def test_self_destruct_after_laying():
    """End-to-end: lay 4, self-destruct 2 of one design."""
    hex_c = HexCoord(0, 0)
    carrier = _StubCarrier("carrier_2")
    carrier.owner_id = 1
    for _ in range(4):
        carrier.carried_items.append(_warhead_mine())
    fleet = Fleet(fleet_id=10, owner_id=1, location=hex_c, speed=5.0)
    fleet.ships.append(carrier)
    owner_empire = SimpleNamespace(id=1, name="O", fleets=[fleet])
    galaxy = SimpleNamespace(current_turn=1)

    fleet.add_order(Order(OrderType.LAY_MINES, target={
        "ship_instance_id": carrier.instance_id,
        "mine_design_id": "mine_warhead_small",
        "count": 4,
        "target_hex": hex_c,
    }))
    LayMinesOrderHandler().execute_action_order(fleet, owner_empire, galaxy)
    mg = [f for f in owner_empire.fleets if f.group_kind == "mine_group"][0]
    assert len(mg.ships[0].carried_items) == 4

    svc = MineGroupService()
    svc.self_destruct(mg, owner_empire, {"mine_warhead_small": 2})
    assert len(mg.ships[0].carried_items) == 2


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
    owner_empire = SimpleNamespace(id=1, name="O", fleets=[laying_fleet])
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
    owner_empire = SimpleNamespace(id=1, name="O", fleets=[laying_fleet])
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
    mine_groups = [f for f in owner_empire.fleets if f.group_kind == "mine_group"]
    assert len(mine_groups) == 2
    total_mines = sum(len(mg.ships[0].carried_items) for mg in mine_groups)
    assert total_mines == 6
    for mg in mine_groups:
        mg.expected_hit_chance_threshold = 0.0  # always-fire laserheads

    # Enemy enters.
    enemy_ship = _StubEnemyShip("dread", max_hp=2000.0, total_defense_score=0.0)
    enemy_fleet = Fleet(fleet_id=20, owner_id=0, location=hex_c, speed=5.0)
    enemy_fleet.ships.append(enemy_ship)
    enemy_empire = SimpleNamespace(id=0, name="E", fleets=[enemy_fleet])

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
    from game.strategy.combat.spec_compiler import (
        build_strategy_battle_spec,
        build_mine_resolver_setup,
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
    )
    enemy_empire = SimpleNamespace(id=0, name="Enemy", fleets=[enemy_fleet])
    galaxy = SimpleNamespace(current_turn=1)
    lay_fleet.add_order(Order(OrderType.LAY_MINES, target={
        "ship_instance_id": mine_carrier.instance_id,
        "mine_design_id": "mine_warhead_small",
        "count": 1,
        "target_hex": hex_c,
    }))
    LayMinesOrderHandler().execute_action_order(lay_fleet, owner_empire, galaxy)
    mine_groups_at_hex = [
        f for f in owner_empire.fleets if f.group_kind == "mine_group"
    ]
    assert len(mine_groups_at_hex) == 1
    mg = mine_groups_at_hex[0]

    # Build the spec. We use registries=MagicMock() since we are not
    # going to materialize ships — we only inspect the spec's structure
    # and the wiring callbacks.
    spec = build_strategy_battle_spec(
        [enemy_fleet, mg, owner_combat_fleet],
        empires={0: enemy_empire, 1: owner_empire},
        registries=MagicMock(),
        post_battle_hook=None,  # let the compiler build the real hook
    )

    # (1) Mine_group is NOT a team in the spec — only the two combat
    # fleets produce teams.
    team_count = len(spec.teams)
    assert team_count == 2, (
        f"Expected exactly 2 combat teams (mine_group filtered out), got "
        f"{team_count}."
    )

    # (2) Spec carries mine_groups + owner_to_team_id side-channel.
    assert getattr(spec, "_mine_groups", None) == (mg,)
    owner_map = getattr(spec, "_owner_to_team_id", {})
    assert 1 in owner_map  # owner empire is in the battle

    # (3) build_mine_resolver_setup returns a callable that populates
    # engine.mine_resolvers.
    setup = build_mine_resolver_setup(spec._mine_groups, owner_map)
    assert setup is not None
    fake_engine = SimpleNamespace(mine_resolvers=[])
    setup(fake_engine)
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
    from game.strategy.combat.spec_compiler import (
        build_strategy_battle_spec,
        build_mine_resolver_setup,
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
    )
    enemy_empire = SimpleNamespace(id=0, name="E", fleets=[enemy_combat])
    galaxy = SimpleNamespace(current_turn=1)
    lay_fleet.add_order(Order(OrderType.LAY_MINES, target={
        "ship_instance_id": carrier.instance_id,
        "mine_design_id": "mine_warhead_small",
        "count": 2,
        "target_hex": hex_c,
    }))
    LayMinesOrderHandler().execute_action_order(lay_fleet, owner_empire, galaxy)
    mg = [f for f in owner_empire.fleets if f.group_kind == "mine_group"][0]

    spec = build_strategy_battle_spec(
        [enemy_combat, mg, owner_combat],
        empires={0: enemy_empire, 1: owner_empire},
        registries=MagicMock(),
    )

    # Wire the resolver onto the mine_group then simulate "all mines
    # consumed during battle" by marking every tactical entity consumed.
    setup = build_mine_resolver_setup(
        spec._mine_groups, spec._owner_to_team_id,
    )
    fake_engine = SimpleNamespace(mine_resolvers=[])
    setup(fake_engine)
    resolver = fake_engine.mine_resolvers[0]
    for entity in resolver.mines:
        entity.consumed = True

    # Invoke the post-battle hook with a minimal outcome.
    outcome = SimpleNamespace(teams=[
        SimpleNamespace(team_id=0, ships=[]),
        SimpleNamespace(team_id=1, ships=[]),
    ])
    spec.post_battle_hook(outcome)

    # Writeback ran: carrier's carried_items is empty.
    assert mg.ships[0].carried_items == []
    # Empty mine_group pruned from owner's fleets list.
    assert mg not in owner_empire.fleets


def test_insufficient_mines_returns_clean_failure():
    """No partial consumption when fewer mines available than requested."""
    hex_c = HexCoord(0, 0)
    carrier = _StubCarrier("carrier_x")
    carrier.owner_id = 1
    carrier.carried_items.append(_warhead_mine())
    fleet = Fleet(fleet_id=10, owner_id=1, location=hex_c, speed=5.0)
    fleet.ships.append(carrier)
    owner_empire = SimpleNamespace(id=1, name="O", fleets=[fleet])
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
