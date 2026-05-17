"""PROJ-FMS-C Phase 2 — fighter_group combat join via spec compiler.

The conflict_resolution_engine iterates over ``empire.fleets`` and feeds
all fleets at the contested hex into ``build_strategy_battle_spec``.
``fighter_group`` Fleets are real-ship-bearing combat fleets — unlike
``mine_group`` synthetic carriers — and must be translated into
``ShipSpec`` entries on the owner's team.

These tests pin that contract:

1. A fighter_group at the same hex as a real fleet is grouped onto its
   owner's team (allies merge by ``owner_id``).
2. A fighter_group does NOT count as a ``mine_group`` and is not
   filtered out by the mine-group splitter.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from game.core.hex_math import HexCoord
from game.strategy.combat.spec_compiler import build_strategy_battle_spec
from game.strategy.combat.team_spec_builder import TeamSpecBuilder
from game.strategy.data.fleet import Fleet
from game.strategy.data.ship_instance import ShipInstance


def _make_fighter_ship(instance_id: str, owner_id: int) -> ShipInstance:
    return ShipInstance(
        instance_id=instance_id,
        design_id="test_fighter",
        name=instance_id,
        owner_id=owner_id,
        design_data={
            "name": "Test Fighter",
            "ship_class": "Fighter (Small)",
            "vehicle_class": "Fighter (Small)",
            "vehicle_type": "Fighter",
        },
        current_hp=80,
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


def test_fighter_group_not_filtered_as_mine_group():
    """`TeamSpecBuilder.split_mine_groups` must only filter mine_group."""
    hex_c = HexCoord(0, 0)
    fighter_group = Fleet(
        fleet_id=200001, owner_id=10, location=hex_c, speed=0.0,
        group_kind="fighter_group",
    )
    fighter_group.ships.append(_make_fighter_ship("f1", owner_id=10))

    mine_group = Fleet(
        fleet_id=100001, owner_id=10, location=hex_c, speed=0.0,
        group_kind="mine_group",
    )

    regular = Fleet(
        fleet_id=1, owner_id=10, location=hex_c, speed=5.0,
        group_kind="fleet",
    )

    combat, mine_groups = TeamSpecBuilder().split_mine_groups(
        [regular, fighter_group, mine_group]
    )
    assert mine_group in mine_groups
    assert fighter_group in combat
    assert regular in combat


def test_fighter_group_joins_owner_team_in_spec(fresh_registries):
    """A fighter_group and a regular fleet of the same owner share a team."""
    hex_c = HexCoord(0, 0)
    # Empire 10's main fleet + their fighter_group at the same hex.
    main_fleet = Fleet(
        fleet_id=1, owner_id=10, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    main_fleet.ships.append(_make_enemy_ship("alpha", owner_id=10))

    fg = Fleet(
        fleet_id=200001, owner_id=10, location=hex_c, speed=0.0,
        group_kind="fighter_group",
    )
    fg.ships.append(_make_fighter_ship("f1", owner_id=10))
    fg.ships.append(_make_fighter_ship("f2", owner_id=10))

    # Enemy empire's fleet so we have 2 unique owners.
    enemy_fleet = Fleet(
        fleet_id=2, owner_id=20, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    enemy_fleet.ships.append(_make_enemy_ship("beta", owner_id=20))

    spec = build_strategy_battle_spec(
        [main_fleet, fg, enemy_fleet],
        registries=fresh_registries,
    )

    # Two teams: one per owner.
    assert len(spec.teams) == 2
    # Owner-10 team has main_fleet's 1 ship + fg's 2 ships = 3 ships.
    team_ship_counts = sorted(
        sum(len(sq.ships) for tf in t.fleet_hierarchy for sq in tf.squadrons)
        for t in spec.teams
    )
    assert team_ship_counts == [1, 3]


def test_fighter_group_alone_vs_enemy_fleet_makes_2_team_spec(fresh_registries):
    """An empire whose only presence at the hex is a fighter_group still
    fields a team — fighter_groups are full combat entities."""
    hex_c = HexCoord(0, 0)
    fg = Fleet(
        fleet_id=200001, owner_id=10, location=hex_c, speed=0.0,
        group_kind="fighter_group",
    )
    fg.ships.append(_make_fighter_ship("f1", owner_id=10))

    enemy_fleet = Fleet(
        fleet_id=2, owner_id=20, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    enemy_fleet.ships.append(_make_enemy_ship("beta", owner_id=20))

    spec = build_strategy_battle_spec(
        [fg, enemy_fleet],
        registries=fresh_registries,
    )
    assert len(spec.teams) == 2
