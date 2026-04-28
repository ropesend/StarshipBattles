"""Tests for ComponentState (PROJ-297 Phase 1 Task 1.1).

`ComponentState` is the per-component-instance state that persists across
battles. One entry per *ship-component instance* — disambiguated by
`instance_index` — with HP, active flag, and the originating `component_id`.

Originally introduced by PROJ-269 Phase 2 in `game/strategy/data/component_state.py`,
moved to `game/core/` by PROJ-297 because the module is layer-neutral and was
being imported by Simulation (a forbidden Simulation→Strategy dependency).
"""
import dataclasses

import pytest

from game.core.component_state import (
    ComponentInstanceView,
    ComponentState,
    component_state_key,
)


def test_component_state_is_dataclass_with_expected_fields():
    assert dataclasses.is_dataclass(ComponentState)
    fields = {f.name for f in dataclasses.fields(ComponentState)}
    assert {"component_id", "instance_index", "current_hp", "max_hp", "is_active"}.issubset(
        fields
    )


def test_component_state_roundtrip_to_dict_from_dict():
    cs = ComponentState(
        component_id="bridge",
        instance_index=0,
        current_hp=123.4,
        max_hp=200.0,
        is_active=True,
    )
    restored = ComponentState.from_dict(cs.to_dict())
    assert restored == cs


def test_component_state_defaults_is_active_true():
    cs = ComponentState(component_id="engine", instance_index=2, current_hp=50.0)
    assert cs.is_active is True


def test_component_state_default_max_hp_zero():
    cs = ComponentState(component_id="engine", instance_index=2, current_hp=50.0)
    assert cs.max_hp == 0.0


def test_component_state_key_helper():
    assert component_state_key("bridge", 0) == "bridge#0"
    assert component_state_key("seeker_missile", 3) == "seeker_missile#3"


def test_component_state_accepts_integer_hp_coerced_to_float():
    cs = ComponentState(
        component_id="bridge",
        instance_index=0,
        current_hp=100,
        max_hp=200,
        is_active=True,
    )
    assert cs.current_hp == pytest.approx(100.0)
    assert cs.max_hp == pytest.approx(200.0)
    assert isinstance(cs.current_hp, float)
    assert isinstance(cs.max_hp, float)


def test_component_state_is_damaged_false_at_full_hp():
    cs = ComponentState(component_id="hull", instance_index=0, current_hp=100, max_hp=100)
    assert cs.is_damaged is False


def test_component_state_is_damaged_true_below_max():
    cs = ComponentState(component_id="hull", instance_index=0, current_hp=50, max_hp=100)
    assert cs.is_damaged is True


def test_component_state_is_damaged_false_when_max_hp_zero():
    # max_hp default is 0.0; with no max_hp set, is_damaged should be False
    # (test ergonomic-construction path).
    cs = ComponentState(component_id="hull", instance_index=0, current_hp=50)
    assert cs.is_damaged is False


def test_component_state_from_dict_handles_missing_optional_fields():
    # Older save data may omit `max_hp` and `is_active`.
    minimal = {
        "component_id": "engine",
        "instance_index": 1,
        "current_hp": 75.0,
    }
    cs = ComponentState.from_dict(minimal)
    assert cs.max_hp == 0.0
    assert cs.is_active is True


# --- ComponentInstanceView (PROJ-315 Phase 1 Task 1.1) ----------------------


def test_component_instance_view_is_frozen_dataclass():
    assert dataclasses.is_dataclass(ComponentInstanceView)
    fields = {f.name for f in dataclasses.fields(ComponentInstanceView)}
    assert fields == {
        "component_id",
        "instance_index",
        "current_hp",
        "max_hp",
        "is_active",
    }


def test_component_instance_view_constructs_with_all_fields():
    view = ComponentInstanceView(
        component_id="reactor_mark_2",
        instance_index=3,
        current_hp=80,
        max_hp=100,
        is_active=True,
    )
    assert view.component_id == "reactor_mark_2"
    assert view.instance_index == 3
    assert view.current_hp == 80
    assert view.max_hp == 100
    assert view.is_active is True


def test_component_instance_view_is_frozen_assignment_raises():
    view = ComponentInstanceView(
        component_id="bridge",
        instance_index=0,
        current_hp=100,
        max_hp=100,
        is_active=True,
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        view.current_hp = 50  # type: ignore[misc]


def test_component_instance_view_equality_on_identical_fields():
    view_a = ComponentInstanceView(
        component_id="engine",
        instance_index=1,
        current_hp=50,
        max_hp=100,
        is_active=False,
    )
    view_b = ComponentInstanceView(
        component_id="engine",
        instance_index=1,
        current_hp=50,
        max_hp=100,
        is_active=False,
    )
    assert view_a == view_b


def test_component_instance_view_unequal_when_field_differs():
    view_a = ComponentInstanceView(
        component_id="engine",
        instance_index=1,
        current_hp=50,
        max_hp=100,
        is_active=True,
    )
    view_b = dataclasses.replace(view_a, current_hp=51)
    assert view_a != view_b
