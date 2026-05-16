"""PROJ-FMS-D Phase 1 — satellite_group combat join via spec compiler.

Mirrors :mod:`test_fighter_group_combat_join`. ``satellite_group`` Fleets
must flow through ``build_strategy_battle_spec`` just like
``fighter_group``: real-ship-bearing combat fleets that merge onto the
owner's team. Only ``mine_group`` Fleets are filtered out of the
combat-fleets stream into the side-channel handled by
``TacticalMineResolver``.
"""
from __future__ import annotations

from game.core.hex_math import HexCoord
from game.strategy.combat.spec_compiler import (
    _split_mine_groups_from_fleets,
    build_strategy_battle_spec,
)
from game.strategy.data.fleet import Fleet
from game.strategy.data.ship_instance import ShipInstance


def _make_satellite_ship(instance_id: str, owner_id: int) -> ShipInstance:
    return ShipInstance(
        instance_id=instance_id,
        design_id="test_satellite",
        name=instance_id,
        owner_id=owner_id,
        design_data={
            "name": "Test Satellite",
            "ship_class": "Satellite",
            "vehicle_class": "Satellite",
            "vehicle_type": "Satellite",
        },
        current_hp=60,
    )


def _make_enemy_ship(instance_id: str, owner_id: int) -> ShipInstance:
    return ShipInstance(
        instance_id=instance_id,
        design_id="test_escort",
        name=instance_id,
        owner_id=owner_id,
        design_data={"name": "Test Escort", "ship_class": "Escort"},
        current_hp=200,
    )


def test_satellite_group_not_filtered_as_mine_group():
    """``_split_mine_groups_from_fleets`` keeps satellite_group in combat."""
    hex_c = HexCoord(0, 0)
    satellite_group = Fleet(
        fleet_id=300001, owner_id=10, location=hex_c, speed=0.0,
        group_kind="satellite_group",
    )
    satellite_group.ships.append(_make_satellite_ship("s1", owner_id=10))

    mine_group = Fleet(
        fleet_id=100001, owner_id=10, location=hex_c, speed=0.0,
        group_kind="mine_group",
    )

    regular = Fleet(
        fleet_id=1, owner_id=10, location=hex_c, speed=5.0,
        group_kind="fleet",
    )

    combat, mine_groups = _split_mine_groups_from_fleets(
        [regular, satellite_group, mine_group]
    )
    assert mine_group in mine_groups
    assert satellite_group in combat
    assert regular in combat


def test_satellite_group_joins_owner_team_in_spec(fresh_registries):
    """A satellite_group merges onto its owner's team (allies by owner_id)."""
    hex_c = HexCoord(0, 0)
    main_fleet = Fleet(
        fleet_id=1, owner_id=10, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    main_fleet.ships.append(_make_enemy_ship("alpha", owner_id=10))

    sg = Fleet(
        fleet_id=300001, owner_id=10, location=hex_c, speed=0.0,
        group_kind="satellite_group",
    )
    sg.ships.append(_make_satellite_ship("s1", owner_id=10))
    sg.ships.append(_make_satellite_ship("s2", owner_id=10))

    enemy_fleet = Fleet(
        fleet_id=2, owner_id=20, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    enemy_fleet.ships.append(_make_enemy_ship("beta", owner_id=20))

    spec = build_strategy_battle_spec(
        [main_fleet, sg, enemy_fleet],
        registries=fresh_registries,
    )

    assert len(spec.teams) == 2
    team_ship_counts = sorted(
        sum(len(sq.ships) for tf in t.fleet_hierarchy for sq in tf.squadrons)
        for t in spec.teams
    )
    assert team_ship_counts == [1, 3]


def test_satellite_group_alone_vs_enemy_fleet_makes_2_team_spec(fresh_registries):
    """A satellite_group is a full combat entity even without a parent fleet."""
    hex_c = HexCoord(0, 0)
    sg = Fleet(
        fleet_id=300001, owner_id=10, location=hex_c, speed=0.0,
        group_kind="satellite_group",
    )
    sg.ships.append(_make_satellite_ship("s1", owner_id=10))

    enemy_fleet = Fleet(
        fleet_id=2, owner_id=20, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    enemy_fleet.ships.append(_make_enemy_ship("beta", owner_id=20))

    spec = build_strategy_battle_spec(
        [sg, enemy_fleet],
        registries=fresh_registries,
    )
    assert len(spec.teams) == 2
