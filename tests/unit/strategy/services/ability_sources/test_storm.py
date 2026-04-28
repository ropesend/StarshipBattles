"""Tests for StormAbilitySource (PROJ-300 Phase 3 + Phase 7)."""
import pytest

from game.core.hex_math import HexCoord
from game.core.protocols import IAbilitySource, is_ability_source
from game.strategy.data.storm import Storm
from game.strategy.services.ability_sources import StormAbilitySource


def _make_storm(name="Ion Storm Alpha", storm_type="ion_storm", abilities=None):
    return Storm(
        name=name,
        storm_type=storm_type,
        location=HexCoord(0, 0),
        hex_offsets=frozenset({HexCoord(0, 0), HexCoord(1, 0)}),
        abilities=abilities or {},
    )


def test_source_kind_is_storm():
    src = StormAbilitySource(storm=_make_storm())
    assert src.source_kind == 'storm'


def test_source_label_is_storm_name():
    src = StormAbilitySource(storm=_make_storm(name="Ion Storm Alpha"))
    assert src.source_label == "Ion Storm Alpha"


def test_source_id_stable_and_prefixed():
    storm = _make_storm(name="Ion Storm Alpha")
    a = StormAbilitySource(storm=storm)
    b = StormAbilitySource(storm=storm)
    assert a.source_id == b.source_id
    assert a.source_id.startswith("storm:")


def test_owner_id_is_none():
    src = StormAbilitySource(storm=_make_storm())
    assert src.owner_id is None


def test_get_abilities_returns_storm_abilities_dict():
    abilities = {"ShieldModifier": {"multiplier": 0.5, "scope": "sector"}}
    src = StormAbilitySource(storm=_make_storm(abilities=abilities))
    assert src.get_abilities() == abilities


def test_get_abilities_empty_when_storm_has_no_abilities():
    src = StormAbilitySource(storm=_make_storm())
    assert src.get_abilities() == {}


def test_affects_hex_true_for_occupied_unparented_storm():
    """Unparented adapter (no system) falls back to local-frame matching.

    Used by mock-style fixtures that build storms with `occupied_hexes` only
    and no parent system. Production code paths always pass a system —
    see `test_affects_hex_translates_local_to_global_when_system_provided`.
    """
    storm = _make_storm()
    src = StormAbilitySource(storm=storm)
    assert src.affects_hex(HexCoord(0, 0)) is True
    assert src.affects_hex(HexCoord(1, 0)) is True


def test_affects_hex_false_outside_unparented_storm():
    src = StormAbilitySource(storm=_make_storm())
    assert src.affects_hex(HexCoord(99, 99)) is False


def test_affects_hex_translates_local_to_global_when_system_provided():
    """BUG-119 regression: with a system reference the adapter must match
    the GLOBAL hex (system.global_location + storm.location + offset), not
    the raw local-frame `occupied_hexes`.
    """
    class _MockSystem:
        global_location = HexCoord(1969, 817)

    storm = Storm(
        name="Plasma Storm Beta",
        storm_type="plasma_storm",
        location=HexCoord(3, 3),
        hex_offsets=frozenset({HexCoord(0, 0), HexCoord(1, 0)}),
        abilities={"ShieldModifier": {"multiplier": 0.7, "scope": "sector"}},
    )
    src = StormAbilitySource(storm=storm, system=_MockSystem())

    # Global hexes that the storm occupies must match.
    assert src.affects_hex(HexCoord(1969 + 3, 817 + 3)) is True
    assert src.affects_hex(HexCoord(1969 + 4, 817 + 3)) is True
    # The LOCAL coord must NOT match — the storm is far from the galaxy origin.
    assert src.affects_hex(HexCoord(3, 3)) is False
    # Far-away hex still rejected.
    assert src.affects_hex(HexCoord(99, 99)) is False


def test_get_activation_state_is_none():
    src = StormAbilitySource(storm=_make_storm())
    assert src.get_activation_state("ShieldModifier") is None


def test_satisfies_iability_source_protocol():
    src = StormAbilitySource(storm=_make_storm())
    assert isinstance(src, IAbilitySource)
    assert is_ability_source(src)
