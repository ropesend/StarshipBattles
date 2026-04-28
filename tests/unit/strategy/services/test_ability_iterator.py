"""Tests for the unified ability-source iterator (PROJ-300)."""
from dataclasses import dataclass, field
from typing import Any, Dict, List

import pytest

from game.core.hex_math import HexCoord
from game.core.protocols import IAbilitySource
from game.strategy.data.storm import Storm
from game.strategy.services.ability_iterator import (
    iter_ability_sources_at_hex,
    iter_ability_sources_in_system,
    register_source_provider_at_hex,
    register_source_provider_in_system,
    unregister_source_provider,
)


@dataclass
class _MockFacility:
    instance_id: str = "fac-1"
    name: str = "Lab"
    is_operational: bool = True
    design_data: Dict[str, Any] = field(default_factory=lambda: {
        "CORE": [{"layer": "CORE", "components": [
            {"id": "x", "abilities": {"GeologicStabilizer": {"scope": "sector"}}},
        ]}],
    })

    def get_activation_state(self, comp_key: str) -> Any:
        return None


@dataclass
class _MockPlanet:
    name: str = "P"
    owner_id: int = 0
    location: Any = HexCoord(2, 2)
    facilities: List[Any] = field(default_factory=list)


@dataclass
class _MockSystem:
    global_location: Any = HexCoord(0, 0)
    planets: List[Any] = field(default_factory=list)
    storms: List[Any] = field(default_factory=list)


def _ion_storm_at(*hexes):
    """Construct a small storm covering the given hexes (relative to (0,0))."""
    offsets = frozenset({HexCoord(h.q, h.r) for h in hexes})
    return Storm(
        name="Storm-X",
        storm_type="ion_storm",
        location=HexCoord(0, 0),
        hex_offsets=offsets,
        abilities={"ShieldModifier": {"multiplier": 0.5, "scope": "sector"}},
    )


def test_iter_at_hex_yields_storm_for_storm_at_hex():
    # Non-zero system origin so local-vs-global frame distinction is meaningful.
    storm = _ion_storm_at(HexCoord(3, 3))
    system = _MockSystem(global_location=HexCoord(1969, 817), storms=[storm])
    global_hex = HexCoord(1969 + 3, 817 + 3)
    # include_system_sources=False so the hex-filter path is what's tested,
    # not the system-wide passthrough.
    sources = list(iter_ability_sources_at_hex(
        system, global_hex, include_system_sources=False,
    ))
    storm_sources = [s for s in sources if s.source_kind == 'storm']
    assert len(storm_sources) == 1


def test_iter_at_hex_excludes_storm_outside_hex():
    storm = _ion_storm_at(HexCoord(3, 3))
    system = _MockSystem(global_location=HexCoord(1969, 817), storms=[storm])
    sources = list(iter_ability_sources_at_hex(
        system, HexCoord(9999, 9999), include_system_sources=False,
    ))
    storm_sources = [s for s in sources if s.source_kind == 'storm']
    assert storm_sources == []


def test_iter_at_hex_yields_storm_when_system_has_nonzero_global_origin():
    """BUG-119 regression: storm.location is local, query hex is global.

    Pre-fix: StormAbilitySource.affects_hex compared the global query hex
    against local-frame occupied_hexes, so any storm in a system whose
    `global_location != HexCoord(0, 0)` was invisible to sector queries.
    """
    storm = Storm(
        name="Plasma Storm Beta",
        storm_type="plasma_storm",
        location=HexCoord(3, 3),
        hex_offsets=frozenset({HexCoord(0, 0)}),
        abilities={"ShieldModifier": {"multiplier": 0.7, "scope": "sector"}},
    )
    system = _MockSystem(global_location=HexCoord(1969, 817), storms=[storm])
    global_hex = HexCoord(1969 + 3, 817 + 3)

    sources = list(iter_ability_sources_at_hex(
        system, global_hex, include_system_sources=False,
    ))
    storm_sources = [s for s in sources if s.source_kind == 'storm']
    assert len(storm_sources) == 1


def test_iter_at_hex_storm_does_not_match_local_hex_when_system_origin_nonzero():
    """BUG-119 regression: querying with the LOCAL hex against a system whose
    origin is non-zero should NOT match — only the GLOBAL hex should.
    """
    storm = Storm(
        name="Plasma Storm Beta",
        storm_type="plasma_storm",
        location=HexCoord(3, 3),
        hex_offsets=frozenset({HexCoord(0, 0)}),
        abilities={"ShieldModifier": {"multiplier": 0.7, "scope": "sector"}},
    )
    system = _MockSystem(global_location=HexCoord(1969, 817), storms=[storm])

    # The LOCAL coord (3, 3) must not match any sector when the system origin
    # is far from (0, 0) — that hex is out in the void.
    sources = list(iter_ability_sources_at_hex(
        system, HexCoord(3, 3), include_system_sources=False,
    ))
    assert [s for s in sources if s.source_kind == 'storm'] == []


def test_iter_at_hex_yields_facility_for_planet_at_hex():
    facility = _MockFacility(instance_id="fac-A")
    # Place planet at the queried hex (system_loc + planet_loc = global hex).
    planet = _MockPlanet(location=HexCoord(5, 5), facilities=[facility])
    system = _MockSystem(global_location=HexCoord(0, 0), planets=[planet])
    sources = list(iter_ability_sources_at_hex(
        system, HexCoord(5, 5), include_system_sources=False,
    ))
    facility_sources = [s for s in sources if s.source_kind == 'facility']
    assert len(facility_sources) == 1


def test_iter_at_hex_excludes_facility_for_distant_planet():
    facility = _MockFacility()
    planet = _MockPlanet(location=HexCoord(5, 5), facilities=[facility])
    system = _MockSystem(planets=[planet])
    sources = list(iter_ability_sources_at_hex(
        system, HexCoord(99, 99), include_system_sources=False,
    ))
    assert [s for s in sources if s.source_kind == 'facility'] == []


def test_iter_in_system_yields_all_facilities():
    fa = _MockFacility(instance_id="A")
    fb = _MockFacility(instance_id="B")
    p1 = _MockPlanet(location=HexCoord(1, 1), facilities=[fa])
    p2 = _MockPlanet(location=HexCoord(9, 9), facilities=[fb])
    system = _MockSystem(planets=[p1, p2])
    sources = list(iter_ability_sources_in_system(system))
    facility_ids = {s.source_id for s in sources if s.source_kind == 'facility'}
    assert facility_ids == {"facility:A", "facility:B"}


def test_iter_at_hex_dedupes_sources():
    """If the same storm is yielded by multiple providers, only emit once.

    The iterator dedupes across hex + system providers via `source_id`. With
    `include_system_sources=True` (default), the storm is yielded by both
    the hex-providers list (hex match) and the system-providers list
    (system-wide passthrough); the iterator must collapse the duplicate.
    """
    storm = _ion_storm_at(HexCoord(0, 0))
    system = _MockSystem(global_location=HexCoord(1969, 817), storms=[storm])
    sources = list(iter_ability_sources_at_hex(system, HexCoord(1969, 817)))
    storm_sources = [s for s in sources if s.source_kind == 'storm']
    assert len(storm_sources) == 1


def test_register_unregister_provider_roundtrip():
    """Custom providers can be registered + unregistered cleanly."""
    sentinel = object()
    yielded = []

    class _MockSource:
        source_kind = 'test'
        source_label = 'test-source'
        source_id = f'test:{id(sentinel)}'
        owner_id = None
        def get_abilities(self): return {}
        def affects_hex(self, h): return True
        def affects_system(self, s): return True
        def get_activation_state(self, n): return None

    def _custom_provider(system, hex_coord, registries):
        yielded.append((system, hex_coord))
        yield _MockSource()

    register_source_provider_at_hex(_custom_provider)
    try:
        sources = list(iter_ability_sources_at_hex(_MockSystem(), HexCoord(0, 0)))
        assert any(s.source_kind == 'test' for s in sources)
    finally:
        unregister_source_provider(_custom_provider)

    sources_after = list(iter_ability_sources_at_hex(_MockSystem(), HexCoord(0, 0)))
    assert not any(s.source_kind == 'test' for s in sources_after)
