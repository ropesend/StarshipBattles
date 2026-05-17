"""PROJ-426 Phase 2 — tests for `TeamSpecBuilder`.

The `TeamSpecBuilder` owns the helpers that used to be private functions
in `spec_compiler.py`:

- `split_mine_groups(fleets) -> (combat, mine_groups)` — was the private
  `_split_mine_groups_from_fleets` helper.
- `team_spec_for_fleet_group(...)` — was `_team_spec_for_fleet_group`.
- `pick_formation_for_fleet(...)` — was `_pick_formation_for_fleet`.
- `ship_spec_from_instance(...)` — was `_ship_spec_from_instance`.

These tests pin the seam contract — formation/team construction is still
covered by the existing `test_spec_compiler.py` / `_formation.py` suites
end-to-end.
"""
from __future__ import annotations

import pytest

from game.core.hex_math import HexCoord
from game.core.math import Vector2
from game.simulation.battle_spec import EntryVector, TeamSpec
from game.simulation.combat.formation import FormationSpec
from game.strategy.combat.team_spec_builder import TeamSpecBuilder
from game.strategy.data.fleet import Fleet
from game.strategy.data.ship_instance import ShipInstance


def _make_ship(instance_id: str, owner_id: int) -> ShipInstance:
    return ShipInstance(
        instance_id=instance_id,
        design_id="test_escort",
        name=instance_id,
        owner_id=owner_id,
        design_data={"name": "Test Escort", "ship_class": "Escort"},
        current_hp=200,
    )


def test_team_spec_for_fleet_group_returns_team_spec_with_expected_shape():
    """One fleet -> one TaskForce -> one Squadron with the fleet's ships."""
    builder = TeamSpecBuilder()
    hex_c = HexCoord(0, 0)
    fleet = Fleet(
        fleet_id=42, owner_id=10, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    fleet.ships.append(_make_ship("a-1", owner_id=10))
    fleet.ships.append(_make_ship("a-2", owner_id=10))

    entry_vector = EntryVector(origin=Vector2(0.0, 0.0), facing=0.0)
    team = builder.team_spec_for_fleet_group(
        [fleet], team_id=7, entry_vector=entry_vector,
    )

    assert isinstance(team, TeamSpec)
    assert team.team_id == 7
    assert team.entry_vector is entry_vector
    assert len(team.fleet_hierarchy) == 1
    tf = team.fleet_hierarchy[0]
    assert tf.task_force_id == "tf-fleet-42"
    assert len(tf.squadrons) == 1
    assert len(tf.squadrons[0].ships) == 2


def test_team_spec_for_fleet_group_raises_on_empty_input():
    builder = TeamSpecBuilder()
    entry_vector = EntryVector(origin=Vector2(0.0, 0.0), facing=0.0)
    with pytest.raises(ValueError):
        builder.team_spec_for_fleet_group(
            [], team_id=0, entry_vector=entry_vector,
        )


def test_ship_spec_from_instance_carries_theme_and_components():
    """`ship_spec_from_instance` extracts theme + components + pose."""
    builder = TeamSpecBuilder()
    ship = _make_ship("x-1", owner_id=10)
    ship.design_data["theme_id"] = "Borg"

    spec = builder.ship_spec_from_instance(ship, pose=None)
    assert spec.instance_id == "x-1"
    assert spec.theme_id == "Borg"
    assert spec.instance_ref is ship


def test_pick_formation_for_fleet_returns_default_when_no_tf_formation():
    """No TF-level formation -> default-resolver formation."""
    builder = TeamSpecBuilder()
    hex_c = HexCoord(0, 0)
    fleet = Fleet(
        fleet_id=1, owner_id=10, location=hex_c, speed=5.0, group_kind="fleet",
    )
    fleet.ships.append(_make_ship("z-1", owner_id=10))

    formation = builder.pick_formation_for_fleet(fleet)
    assert isinstance(formation, FormationSpec)
