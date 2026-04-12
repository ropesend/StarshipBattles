"""Tests for FormationSpec / FormationShape (PROJ-269 Phase 1 Task 1.4).

Phase 1 only ships the type shape. The `FormationResolver` that converts
(formation, entry_vector, boundary, ships) → per-ship (position, angle)
lands in Phase 4.

Covers:
- `FormationShape` enum with all 8 documented members
- `FormationSpec` frozen dataclass with shape / spacing / custom_positions
- `custom_positions` defaults to empty tuple
"""
import dataclasses
from enum import Enum

import pytest

from game.core.math import Vector2
from game.simulation.combat.formation import FormationShape, FormationSpec


# ---------------------------------------------------------------------------
# FormationShape enum
# ---------------------------------------------------------------------------


def test_formation_shape_is_enum():
    assert issubclass(FormationShape, Enum)


def test_formation_shape_has_all_documented_members():
    names = {m.name for m in FormationShape}
    required = {
        "LINE_ABREAST",
        "LINE_ASTERN",
        "WEDGE",
        "ECHELON_LEFT",
        "ECHELON_RIGHT",
        "SCREEN",
        "CARRIER_PROTECTED",
        "CUSTOM",
    }
    missing = required - names
    assert not missing, f"FormationShape missing members: {missing}"


# ---------------------------------------------------------------------------
# FormationSpec dataclass
# ---------------------------------------------------------------------------


def test_formation_spec_is_frozen_dataclass():
    assert dataclasses.is_dataclass(FormationSpec)
    params = getattr(FormationSpec, "__dataclass_params__", None)
    assert params is not None and params.frozen


def test_formation_spec_required_fields():
    fs = FormationSpec(shape=FormationShape.WEDGE, spacing=150.0)
    assert fs.shape == FormationShape.WEDGE
    assert fs.spacing == pytest.approx(150.0)
    # custom_positions defaults to empty tuple
    assert fs.custom_positions == ()


def test_formation_spec_custom_positions_field():
    custom = (Vector2(0, 0), Vector2(100, 0), Vector2(-100, 0))
    fs = FormationSpec(
        shape=FormationShape.CUSTOM,
        spacing=100.0,
        custom_positions=custom,
    )
    assert fs.custom_positions == custom
    assert isinstance(fs.custom_positions, tuple)


def test_formation_spec_is_immutable():
    fs = FormationSpec(shape=FormationShape.LINE_ABREAST, spacing=200.0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        fs.spacing = 300.0  # type: ignore[misc]


def test_formation_spec_equality_semantics():
    a = FormationSpec(shape=FormationShape.LINE_ABREAST, spacing=100.0)
    b = FormationSpec(shape=FormationShape.LINE_ABREAST, spacing=100.0)
    c = FormationSpec(shape=FormationShape.LINE_ABREAST, spacing=200.0)
    assert a == b
    assert a != c
