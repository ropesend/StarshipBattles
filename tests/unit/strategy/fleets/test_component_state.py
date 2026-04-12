"""Tests for ComponentState (PROJ-269 Phase 2 Task 2.1).

`ComponentState` is the strategy-layer per-component-instance state that
persists across battles. One entry per *ship-component instance* —
disambiguated by `instance_index` — with HP, active flag, and the
originating `component_id`.
"""
import dataclasses

import pytest

from game.strategy.data.component_state import (
    ComponentState,
    component_state_key,
)


def test_component_state_is_dataclass_with_expected_fields():
    assert dataclasses.is_dataclass(ComponentState)
    fields = {f.name for f in dataclasses.fields(ComponentState)}
    assert {"component_id", "instance_index", "current_hp", "is_active"}.issubset(
        fields
    )


def test_component_state_roundtrip_to_dict_from_dict():
    cs = ComponentState(
        component_id="bridge",
        instance_index=0,
        current_hp=123.4,
        is_active=True,
    )
    restored = ComponentState.from_dict(cs.to_dict())
    assert restored == cs


def test_component_state_defaults_is_active_true():
    cs = ComponentState(component_id="engine", instance_index=2, current_hp=50.0)
    assert cs.is_active is True


def test_component_state_key_helper():
    # Shared helper that produces the dict-key format used on ShipInstance.
    assert component_state_key("bridge", 0) == "bridge#0"
    assert component_state_key("seeker_missile", 3) == "seeker_missile#3"


def test_component_state_accepts_integer_hp_coerced_to_float():
    # The engine uses floats for hp; the strategy dataclass should accept
    # ints and keep them as floats (or equal numerically).
    cs = ComponentState(
        component_id="bridge",
        instance_index=0,
        current_hp=100,
        is_active=True,
    )
    assert cs.current_hp == pytest.approx(100.0)
