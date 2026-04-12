"""Tests for `ShipInstance <-> Ship` component-HP round-trip (PROJ-269 Phase 2 Task 2.2).

Covers:
- `ShipInstance.to_ship` applies `self.components[key].current_hp` to each
  constructed simulation Ship's component (by id + instance_index)
- `ShipInstance.update_from_ship` writes each simulation Ship's per-component
  HP back into `self.components` by (component_id, instance_index) key
- Full round-trip: damage persists through `to_ship` → direct HP read
  → `update_from_ship` with no drift for the fields we round-trip
"""
import pytest

from game.core.math import Vector2
from game.strategy.data.component_state import ComponentState, component_state_key
from game.strategy.data.ship_instance import ShipInstance


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _design_laser_cruiser() -> dict:
    return {
        "name": "LaserCruiser",
        "ship_class": "Escort",
        "vehicle_type": "Ship",
        "design_role": "fleet_escort",
        "theme_id": "Federation",
        "layers": {
            "CORE": [{"id": "bridge"}],
            "OUTER": [
                {"id": "laser_cannon"},
                {"id": "laser_cannon"},
            ],
            "ARMOR": [],
        },
        "_metadata": {},
    }


# ---------------------------------------------------------------------------
# to_ship: applies ComponentState HP onto the engine Ship's components
# ---------------------------------------------------------------------------


def test_to_ship_applies_component_hp_from_components(session_registries):
    instance = ShipInstance.create(
        design_data=_design_laser_cruiser(),
        owner_id=0,
        registries=session_registries,
    )
    assert instance.components, "populate-on-create must provide components"

    # Pick the first laser_cannon instance and damage it to 50% HP.
    key0 = component_state_key("laser_cannon", 0)
    cs0 = instance.components[key0]
    half_hp = cs0.current_hp / 2.0
    instance.components[key0] = ComponentState(
        component_id=cs0.component_id,
        instance_index=cs0.instance_index,
        current_hp=half_hp,
        is_active=cs0.is_active,
    )

    ship = instance.to_ship(position=(0.0, 0.0), team_id=0, registries=session_registries)

    # Find laser_cannon components on the Ship. There should be 2, one at
    # full HP and one at half HP.
    laser_cannons = []
    for layer_data in ship.layers.values():
        for comp in getattr(layer_data, "components", []):
            if comp.id == "laser_cannon":
                laser_cannons.append(comp)
    assert len(laser_cannons) == 2
    hps = sorted(c.current_hp for c in laser_cannons)
    # The damaged one should be ~half_hp, the other at full max_hp.
    full_hp = max(laser_cannons, key=lambda c: c.current_hp).max_hp
    assert hps[0] == pytest.approx(half_hp, abs=1.0)
    assert hps[1] == pytest.approx(full_hp, abs=1.0)


def test_to_ship_preserves_instance_id(session_registries):
    instance = ShipInstance.create(
        design_data=_design_laser_cruiser(),
        owner_id=0,
        registries=session_registries,
    )
    ship = instance.to_ship(position=(0.0, 0.0), team_id=0, registries=session_registries)
    assert ship.instance_id == instance.instance_id


# ---------------------------------------------------------------------------
# update_from_ship: writes per-component HP back into instance.components
# ---------------------------------------------------------------------------


def test_update_from_ship_writes_component_hp_back(session_registries):
    instance = ShipInstance.create(
        design_data=_design_laser_cruiser(),
        owner_id=0,
        registries=session_registries,
    )
    ship = instance.to_ship(position=(0.0, 0.0), team_id=0, registries=session_registries)

    # Simulate combat: damage one laser_cannon to ~30% HP.
    target_comp = None
    for layer_data in ship.layers.values():
        for comp in getattr(layer_data, "components", []):
            if comp.id == "laser_cannon":
                target_comp = comp
                break
        if target_comp is not None:
            break
    assert target_comp is not None

    damage_amount = int(target_comp.max_hp * 0.7)
    target_comp.take_damage(damage_amount)
    expected_hp_after = target_comp.current_hp  # post-damage

    instance.update_from_ship(ship)

    # At least one laser_cannon entry in instance.components should now
    # reflect the damage (current_hp roughly equal to expected_hp_after).
    laser_states = [
        cs for cs in instance.components.values()
        if cs.component_id == "laser_cannon"
    ]
    assert len(laser_states) == 2
    hps = sorted(cs.current_hp for cs in laser_states)
    assert hps[0] == pytest.approx(expected_hp_after, abs=1.0)


# ---------------------------------------------------------------------------
# Full round-trip: damage persists across to_ship -> update_from_ship
# ---------------------------------------------------------------------------


def test_round_trip_preserves_damage(session_registries):
    instance = ShipInstance.create(
        design_data=_design_laser_cruiser(),
        owner_id=0,
        registries=session_registries,
    )

    # Damage laser_cannon#0 to half HP on the ShipInstance.
    key0 = component_state_key("laser_cannon", 0)
    cs0 = instance.components[key0]
    original_hp = cs0.current_hp
    half_hp = original_hp / 2.0
    instance.components[key0] = ComponentState(
        component_id=cs0.component_id,
        instance_index=cs0.instance_index,
        current_hp=half_hp,
        is_active=cs0.is_active,
    )

    # Round-trip
    ship = instance.to_ship(position=(0.0, 0.0), team_id=0, registries=session_registries)
    instance.update_from_ship(ship)

    restored_cs = instance.components[key0]
    # Should still be at roughly half HP (no change during round-trip
    # because we didn't simulate any new damage).
    assert restored_cs.current_hp == pytest.approx(half_hp, abs=1.0)
