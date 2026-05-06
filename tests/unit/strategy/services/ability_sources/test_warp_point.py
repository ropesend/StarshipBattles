"""Tests for WarpPointAbilitySource (PROJ-303)."""
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Dict

from game.core.hex_math import HexCoord
from game.core.protocols import IAbilitySource, is_ability_source
from game.strategy.data.galaxy import WarpPoint
from game.strategy.services.ability_sources import WarpPointAbilitySource


@dataclass
class _MockSystem:
    global_location: Any = HexCoord(50, 50)


def _wp(warp_type='stable', abilities=None, location=HexCoord(5, 5)):
    return WarpPoint(
        destination_id='OtherSystem',
        location=location,
        warp_type=warp_type,
        intrinsic_abilities=abilities or {},
    )


def test_source_kind_is_warp_point():
    src = WarpPointAbilitySource(warp_point=_wp(), system=_MockSystem())
    assert src.source_kind == 'warp_point'


def test_source_label_includes_warp_type():
    src = WarpPointAbilitySource(warp_point=_wp(warp_type='unstable'), system=_MockSystem())
    assert 'unstable' in src.source_label
    assert 'OtherSystem' in src.source_label


def test_source_label_uses_stable_and_unknown_destination_defaults():
    warp_point = SimpleNamespace(location=HexCoord(1, 1), intrinsic_abilities={})
    src = WarpPointAbilitySource(warp_point=warp_point, system=_MockSystem())

    assert 'stable' in src.source_label
    assert '?' in src.source_label


def test_source_id_uses_destination():
    src = WarpPointAbilitySource(warp_point=_wp(), system=_MockSystem())
    assert src.source_id == "warp_point:OtherSystem"


def test_source_id_falls_back_to_object_id_without_destination():
    warp_point = SimpleNamespace(location=HexCoord(1, 1), intrinsic_abilities={})
    src = WarpPointAbilitySource(warp_point=warp_point, system=_MockSystem())

    assert src.source_id == f"warp_point:{id(warp_point)}"


def test_owner_id_is_none():
    src = WarpPointAbilitySource(warp_point=_wp(), system=_MockSystem())
    assert src.owner_id is None


def test_get_abilities_returns_intrinsic_dict():
    abilities = {"EnvironmentalDamage": {"rate": 0.5, "damage_type": "warp", "scope": "sector"}}
    src = WarpPointAbilitySource(
        warp_point=_wp(warp_type='unstable', abilities=abilities),
        system=_MockSystem(),
    )
    assert src.get_abilities() == abilities


def test_get_abilities_returns_empty_for_missing_intrinsic_abilities():
    warp_point = SimpleNamespace(destination_id='OtherSystem', location=HexCoord(5, 5))
    src = WarpPointAbilitySource(warp_point=warp_point, system=_MockSystem())

    assert src.get_abilities() == {}


def test_affects_hex_at_global_location():
    """Warp point at local (5,5) within system at (50,50) -> global (55,55)."""
    src = WarpPointAbilitySource(
        warp_point=_wp(location=HexCoord(5, 5)),
        system=_MockSystem(global_location=HexCoord(50, 50)),
    )
    assert src.affects_hex(HexCoord(55, 55)) is True
    assert src.affects_hex(HexCoord(99, 99)) is False


def test_affects_hex_returns_false_when_location_data_missing():
    no_warp_location = WarpPointAbilitySource(
        warp_point=SimpleNamespace(destination_id='OtherSystem'),
        system=_MockSystem(global_location=HexCoord(50, 50)),
    )
    no_system_location = WarpPointAbilitySource(
        warp_point=_wp(location=HexCoord(5, 5)),
        system=SimpleNamespace(),
    )

    assert no_warp_location.affects_hex(HexCoord(55, 55)) is False
    assert no_system_location.affects_hex(HexCoord(55, 55)) is False


def test_affects_hex_returns_false_for_incompatible_coordinate_types():
    src = WarpPointAbilitySource(
        warp_point=_wp(location=HexCoord(5, 5)),
        system=_MockSystem(global_location="not-a-hex"),
    )

    assert src.affects_hex(HexCoord(55, 55)) is False


def test_affects_system_requires_same_system_object():
    system = _MockSystem(global_location=HexCoord(50, 50))
    src = WarpPointAbilitySource(warp_point=_wp(), system=system)

    assert src.affects_system(system) is True
    assert src.affects_system(_MockSystem(global_location=HexCoord(50, 50))) is False


def test_activation_state_is_always_none():
    src = WarpPointAbilitySource(warp_point=_wp(), system=_MockSystem())

    assert src.get_activation_state("EnvironmentalDamage") is None


def test_warp_point_serialization_roundtrip():
    """WarpPoint with warp_type + intrinsic_abilities round-trips."""
    wp = _wp(
        warp_type='dimensional_rift',
        abilities={"ShieldModifier": {"multiplier": 0.8, "scope": "sector"}},
        location=HexCoord(3, 4),
    )
    data = wp.to_dict()
    restored = WarpPoint.from_dict(data)
    assert restored.warp_type == 'dimensional_rift'
    assert restored.intrinsic_abilities == wp.intrinsic_abilities
    assert restored.location == wp.location


def test_satisfies_iability_source_protocol():
    src = WarpPointAbilitySource(warp_point=_wp(), system=_MockSystem())
    assert isinstance(src, IAbilitySource)
    assert is_ability_source(src)
