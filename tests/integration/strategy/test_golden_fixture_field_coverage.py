"""PROJ-379 Phase 1: golden-fixture field-coverage guard.

Asserts that the populated golden-save fixture
(``tests/fixtures/saves/galaxy_proj372_populated.json``) exercises every key
emitted by ``planet_to_dict`` (modulo the cosmetic-placeholder skiplist) with
a non-default value somewhere in the fixture's planets.

This catches the "developer added a Planet field but forgot to populate the
fixture" drift class — the only realistic regression path the hand-built
fixture approach reintroduces vs. generated fixtures.

**Implementation pattern (PROJ-379 decisions.md, 2026-05-08):** the guard uses
the **serialized-baseline pattern** rather than ``dataclasses.fields()``
introspection. ``planet_to_dict(_minimal_planet())`` is the single source of
truth for both the emitted-keys set and the per-key default value. This:
  - handles ``default_factory`` mutables (``[]``, ``{}``) correctly,
  - handles enum-name serialization (``PlanetType.BARREN`` → ``"BARREN"``),
  - is resilient if ``planet_to_dict`` is later refactored from a single dict
    literal into programmatic construction.

**Skiplist:** ``image_id`` and ``image_rotation`` are intentionally normalized
to deterministic placeholders by the fixture builder (see PROJ-379
``decisions.md`` row "Field-coverage skiplist" for rationale).
"""
from __future__ import annotations

import json
from pathlib import Path

from game.core.hex_math import HexCoord
from game.strategy.data.planet import Planet
from game.strategy.data.planet_serde import planet_to_dict


_FIXTURE_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures" / "saves"

# Skiplist documented in PROJ-379 decisions.md row "Field-coverage skiplist".
_SKIP_KEYS = frozenset({"image_id", "image_rotation"})


def _minimal_planet() -> Planet:
    """Construct a Planet with required fields only; default-valued fields fall through.

    `planet_type` defaults to `PlanetType.BARREN` per the Planet dataclass; we
    rely on that default rather than passing it explicitly so the serialized
    baseline matches the actual default behaviour.
    """
    return Planet(
        name="_baseline",
        location=HexCoord(0, 0),
        orbit_distance=1,
        mass=1.0,
        radius=1.0,
        surface_area=1.0,
        density=1.0,
        surface_gravity=1.0,
        surface_pressure=0.0,
        surface_temperature=0.0,
        surface_water=0.0,
        tectonic_activity=0.0,
        magnetic_field=0.0,
    )


def _serialized_defaults() -> dict[str, object]:
    """Return ``{key: default_serialized_value}`` per ``planet_to_dict`` applied to a minimal Planet."""
    return planet_to_dict(_minimal_planet())


def _emitted_keys() -> set[str]:
    """Return the set of keys ``planet_to_dict`` emits."""
    return set(_serialized_defaults().keys())


def test_populated_fixture_exercises_every_planet_field() -> None:
    """Every key emitted by planet_to_dict (modulo skiplist) appears with a non-default value."""
    emitted = _emitted_keys() - _SKIP_KEYS
    defaults = _serialized_defaults()
    fixture = json.loads((_FIXTURE_DIR / "galaxy_proj372_populated.json").read_text())

    planets: list[dict] = []
    for sys_entry in fixture["systems"]:
        planets.extend(sys_entry["system"].get("planets", []))

    assert planets, "PROJ-379: populated fixture has zero planets — builder bug."

    missing: list[str] = []
    for key in sorted(emitted):
        default = defaults[key]
        if not any(p.get(key, default) != default for p in planets):
            missing.append(key)

    assert not missing, (
        f"PROJ-379 field-coverage guard: planet_to_dict emits these keys but no "
        f"planet in galaxy_proj372_populated.json has a non-default value for "
        f"them: {missing}. Update tests/fixtures/saves/_build_galaxy_fixture.py::"
        f"build_populated() to populate them. See PROJ-379 decisions.md."
    )
