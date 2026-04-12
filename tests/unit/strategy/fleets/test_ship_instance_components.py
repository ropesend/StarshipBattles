"""Tests for `ShipInstance.components` field (PROJ-269 Phase 2 Task 2.1).

Covers:
- `ShipInstance.components` is a Dict[str, ComponentState]
- A newly-created ShipInstance from a full design is populated with
  full-HP ComponentState entries keyed by `"{component_id}#{instance_index}"`
- Serialization (`to_dict` / `from_dict`) preserves `components`
- Loading a legacy save dict without `components` defaults to empty
  (graceful degradation per CLAUDE.md "saves are disposable" rule)
"""
import pytest

from game.strategy.data.component_state import ComponentState, component_state_key
from game.strategy.data.ship_instance import ShipInstance


# ---------------------------------------------------------------------------
# Fixtures — Minimal design + design with multiple identical components
# ---------------------------------------------------------------------------


def _design_with_single_component() -> dict:
    """Design with one Bridge component."""
    return {
        "name": "TestShip",
        "ship_class": "Escort",
        "vehicle_type": "Ship",
        "design_role": "fleet_escort",
        "theme_id": "Federation",
        "layers": {
            "CORE": [{"id": "bridge"}],
            "ARMOR": [],
        },
        "_metadata": {},
    }


def _design_with_multiple_identical_components() -> dict:
    """Design with 3 identical laser_cannon components."""
    return {
        "name": "ThreeLasers",
        "ship_class": "Escort",
        "vehicle_type": "Ship",
        "design_role": "fleet_escort",
        "theme_id": "Federation",
        "layers": {
            "CORE": [{"id": "bridge"}],
            "OUTER": [
                {"id": "laser_cannon"},
                {"id": "laser_cannon"},
                {"id": "laser_cannon"},
            ],
            "ARMOR": [],
        },
        "_metadata": {},
    }


# ---------------------------------------------------------------------------
# ShipInstance.components field presence
# ---------------------------------------------------------------------------


def test_ship_instance_has_components_field(session_registries):
    ship = ShipInstance.create(
        design_data=_design_with_single_component(),
        owner_id=0,
        registries=session_registries,
    )
    assert hasattr(ship, "components")
    assert isinstance(ship.components, dict)


def test_ship_instance_components_populated_on_create(session_registries):
    ship = ShipInstance.create(
        design_data=_design_with_single_component(),
        owner_id=0,
        registries=session_registries,
    )
    # At least the bridge should be present.
    assert len(ship.components) >= 1
    # Key format: "component_id#instance_index"
    assert all("#" in k for k in ship.components.keys())
    for value in ship.components.values():
        assert isinstance(value, ComponentState)


def test_ship_instance_components_full_hp_on_create(session_registries):
    ship = ShipInstance.create(
        design_data=_design_with_single_component(),
        owner_id=0,
        registries=session_registries,
    )
    # Every component entry should have current_hp > 0 (full HP from design).
    for cs in ship.components.values():
        assert cs.current_hp > 0, f"{cs.component_id}#{cs.instance_index} has no HP"
        assert cs.is_active is True


def test_ship_instance_components_disambiguates_identical_components(
    session_registries,
):
    """Three identical beam components should produce three separate
    ComponentState entries, each with a unique instance_index."""
    design = _design_with_multiple_identical_components()
    ship = ShipInstance.create(
        design_data=design,
        owner_id=0,
        registries=session_registries,
    )
    beam_entries = [
        cs for cs in ship.components.values()
        if cs.component_id == "laser_cannon"
    ]
    assert len(beam_entries) == 3
    # instance_indexes should be {0, 1, 2}
    assert {cs.instance_index for cs in beam_entries} == {0, 1, 2}

    # Keys reflect instance disambiguation.
    for i in range(3):
        assert component_state_key("laser_cannon", i) in ship.components


# ---------------------------------------------------------------------------
# Serialization round-trip
# ---------------------------------------------------------------------------


def test_ship_instance_components_serialization_roundtrip(session_registries):
    ship = ShipInstance.create(
        design_data=_design_with_single_component(),
        owner_id=0,
        registries=session_registries,
    )
    # Damage one component so we can verify the damage round-trips.
    for key, cs in ship.components.items():
        ship.components[key] = ComponentState(
            component_id=cs.component_id,
            instance_index=cs.instance_index,
            current_hp=cs.current_hp / 2.0,
            is_active=cs.is_active,
        )
        break

    data = ship.to_dict()
    assert "components" in data
    assert isinstance(data["components"], dict)

    restored = ShipInstance.from_dict(data, registries=session_registries)
    assert len(restored.components) == len(ship.components)
    for key, cs in ship.components.items():
        assert key in restored.components
        restored_cs = restored.components[key]
        assert restored_cs.component_id == cs.component_id
        assert restored_cs.instance_index == cs.instance_index
        assert restored_cs.current_hp == pytest.approx(cs.current_hp)
        assert restored_cs.is_active == cs.is_active


def test_ship_instance_legacy_save_without_components_defaults_empty(
    session_registries,
):
    """Loading an existing save dict that predates PROJ-269 should NOT
    crash; `components` defaults to an empty dict (graceful degradation
    per CLAUDE.md 'saves are disposable' rule)."""
    # Start from a normal serialized ship, then remove the `components` key
    # to simulate a legacy save.
    ship = ShipInstance.create(
        design_data=_design_with_single_component(),
        owner_id=0,
        registries=session_registries,
    )
    data = ship.to_dict()
    data.pop("components", None)

    restored = ShipInstance.from_dict(data, registries=session_registries)
    assert hasattr(restored, "components")
    assert restored.components == {}
