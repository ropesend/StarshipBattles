"""
PROJ-367 Phase 3: ``StatAccumulator`` dataclass tests (closes EXT-13).

Pins the 14-field shape (10 scalar + 4 named map fields), the slots-based
runtime safety (misspelled scalar/map field names raise ``AttributeError``),
and the default values.
"""
from __future__ import annotations

import dataclasses

import pytest


# Authoritative field set per PROJ-367 design.md / phase_3_checklist.md.
SCALAR_FIELDS: list[str] = [
    "thrust",
    "strategic_movement",
    "turn_speed",
    "maneuver_points",
    "max_shields",
    "shield_regen",
    "shield_cost",
    "warp_max_tonnage",
    "warp_energy_cost",
    "pod_storage_mass",
]

MAP_FIELDS: list[str] = [
    "warp_resource_costs",
    "cargo_storage",
    "resource_storage",
    "resource_generation",
]


def test_dataclass_has_exactly_14_fields():
    """``dataclasses.fields(StatAccumulator)`` yields exactly 14 fields."""
    from game.simulation.entities.stat_contributors.accumulator import (
        StatAccumulator,
    )

    fields = dataclasses.fields(StatAccumulator)
    assert len(fields) == 14, (
        f"StatAccumulator should have exactly 14 fields (10 scalar + 4 map); "
        f"got {len(fields)}: {[f.name for f in fields]}"
    )


def test_dataclass_field_names_match_authoritative_list():
    """Exact set match — no extra fields, no missing fields."""
    from game.simulation.entities.stat_contributors.accumulator import (
        StatAccumulator,
    )

    field_names = {f.name for f in dataclasses.fields(StatAccumulator)}
    expected = set(SCALAR_FIELDS) | set(MAP_FIELDS)
    assert field_names == expected, (
        f"StatAccumulator field name mismatch: extra="
        f"{field_names - expected}, missing={expected - field_names}"
    )


def test_misspelled_field_assignment_raises_attribute_error():
    """``slots=True`` makes the dataclass __slots__-backed; typos raise."""
    from game.simulation.entities.stat_contributors.accumulator import (
        StatAccumulator,
    )

    acc = StatAccumulator()
    with pytest.raises(AttributeError):
        acc.shield_regen_typo = 1.0  # type: ignore[attr-defined]


def test_misspelled_field_read_raises_attribute_error():
    """Reads of misspelled fields raise (slots=True semantics)."""
    from game.simulation.entities.stat_contributors.accumulator import (
        StatAccumulator,
    )

    acc = StatAccumulator()
    with pytest.raises(AttributeError):
        _ = acc.thrust_typo  # type: ignore[attr-defined]


@pytest.mark.parametrize("name", SCALAR_FIELDS)
def test_scalar_field_default_is_zero(name: str):
    """Scalar fields default to 0 / 0.0."""
    from game.simulation.entities.stat_contributors.accumulator import (
        StatAccumulator,
    )

    acc = StatAccumulator()
    val = getattr(acc, name)
    assert val == 0 or val == 0.0, (
        f"Field {name!r} expected default 0/0.0; got {val!r}"
    )


@pytest.mark.parametrize("name", MAP_FIELDS)
def test_map_field_defaults_to_empty_dict(name: str):
    """Map fields default to a fresh empty dict (not a shared default)."""
    from game.simulation.entities.stat_contributors.accumulator import (
        StatAccumulator,
    )

    acc = StatAccumulator()
    val = getattr(acc, name)
    assert val == {}
    # Each instance owns a fresh dict (no shared default — would be a
    # mutable-default footgun).
    acc2 = StatAccumulator()
    assert getattr(acc, name) is not getattr(acc2, name)


def test_dynamic_resource_keys_live_in_resource_maps_not_scalars():
    """``max_<resource>`` / ``gen_<resource>`` are NOT top-level scalar fields.

    They live INSIDE ``resource_storage`` / ``resource_generation`` because
    resource types come from data files at runtime — adding a new resource
    type must NOT require a code edit (data-driven invariant at
    ``ship_stats.py:285-295``).
    """
    from game.simulation.entities.stat_contributors.accumulator import (
        StatAccumulator,
    )

    field_names = {f.name for f in dataclasses.fields(StatAccumulator)}
    # Sanity: no synthetic "max_X" / "gen_X" scalar fields.
    for prefix in ("max_", "gen_"):
        synthetic = {n for n in field_names if n.startswith(prefix)}
        # The only legitimate "max_*" scalar field is `max_shields`.
        synthetic.discard("max_shields")
        assert not synthetic, (
            f"StatAccumulator must not have flat {prefix}<resource> fields; "
            f"found: {synthetic}. Resource keys live in resource_storage / "
            f"resource_generation map fields."
        )
