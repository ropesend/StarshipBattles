"""Registry coverage tests for PROJ-301..304 intrinsic-ability registries.

For every value in the canonical type enum (PlanetType, StarType), the
registry JSON must declare a corresponding entry. A future enum addition
that forgets to update the registry would silently produce empty
intrinsic abilities; this test catches that.
"""
import json
from pathlib import Path

import pytest

from game.core.paths import Paths
from game.strategy.data.planet import PlanetType
from game.strategy.data.stars import StarType


def _load_registry(path_str: str, top_key: str) -> dict:
    p = Path(path_str)
    if not p.exists():
        pytest.skip(f"{path_str} not present")
    with p.open('r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get(top_key, {})


@pytest.mark.parametrize("planet_type", list(PlanetType), ids=lambda t: t.name)
def test_every_planet_type_has_registry_entry(planet_type):
    """PROJ-301: every PlanetType enum value must appear in planet_types.json."""
    registry = _load_registry(Paths.PLANET_TYPES_FILE, 'planet_types')
    assert planet_type.name in registry, (
        f"PROJ-301 coverage: PlanetType.{planet_type.name} missing from "
        f"data/planet_types.json. Add an entry (empty `abilities: {{}}` "
        f"is fine for benign types)."
    )


@pytest.mark.parametrize("star_type", list(StarType), ids=lambda t: t.name)
def test_every_star_type_has_registry_entry(star_type):
    """PROJ-302: every StarType enum value must appear in star_types.json."""
    registry = _load_registry(Paths.STAR_TYPES_FILE, 'star_types')
    assert star_type.name in registry, (
        f"PROJ-302 coverage: StarType.{star_type.name} missing from "
        f"data/star_types.json. Add an entry (empty `abilities: {{}}` "
        f"is fine for benign types)."
    )


def test_warp_point_types_registry_has_known_set():
    """PROJ-303: warp_point_types should include at least the canonical 4 types."""
    registry = _load_registry(Paths.WARP_POINT_TYPES_FILE, 'warp_point_types')
    expected = {'stable', 'unstable', 'dimensional_rift', 'precursor_gateway'}
    missing = expected - set(registry.keys())
    assert not missing, f"PROJ-303 missing warp_point_types: {missing}"


def test_system_archetypes_registry_has_known_set():
    """PROJ-304: system_archetypes should include at least the canonical 5 archetypes."""
    p = Path(Paths.SYSTEM_ARCHETYPES_FILE)
    if not p.exists():
        pytest.skip("system_archetypes.json not present")
    with p.open('r', encoding='utf-8') as f:
        data = json.load(f)
    archetypes = data.get('archetypes', {})
    expected = {'nebula', 'ancient_battlefield', 'precursor_ruins', 'ion_field', 'void'}
    missing = expected - set(archetypes.keys())
    assert not missing, f"PROJ-304 missing archetypes: {missing}"
    # archetype_chance should be a sane float.
    chance = data.get('archetype_chance', 0.0)
    assert 0.0 <= chance <= 1.0, (
        f"PROJ-304 archetype_chance {chance} must be in [0.0, 1.0]"
    )


def _walk_ability_chances(registry: dict) -> list:
    """Yield (entry_key, ability_name, chance) for every ability that
    declares a `chance` field in a per-type intrinsic registry."""
    found = []
    for entry_key, entry_data in registry.items():
        if not isinstance(entry_data, dict):
            continue
        abilities = entry_data.get('abilities', {})
        if not isinstance(abilities, dict):
            continue
        for ability_name, ability_data in abilities.items():
            if isinstance(ability_data, dict) and 'chance' in ability_data:
                found.append((entry_key, ability_name, ability_data['chance']))
    return found


def test_planet_types_chance_fields_in_valid_range():
    """FEAT-15: every per-ability `chance` field in planet_types.json must
    be a numeric value in [0.0, 1.0]. Mirrors the archetype_chance check."""
    registry = _load_registry(Paths.PLANET_TYPES_FILE, 'planet_types')
    for entry_key, ability_name, chance in _walk_ability_chances(registry):
        assert isinstance(chance, (int, float)) and not isinstance(chance, bool), (
            f"FEAT-15: planet_types.{entry_key}.{ability_name}.chance "
            f"must be numeric, got {type(chance).__name__}={chance!r}"
        )
        assert 0.0 <= chance <= 1.0, (
            f"FEAT-15: planet_types.{entry_key}.{ability_name}.chance={chance} "
            f"must be in [0.0, 1.0]"
        )
