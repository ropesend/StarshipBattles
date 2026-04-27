"""Tests for WarpPointAbilitySource (PROJ-303)."""
from dataclasses import dataclass
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


def test_source_id_uses_destination():
    src = WarpPointAbilitySource(warp_point=_wp(), system=_MockSystem())
    assert src.source_id == "warp_point:OtherSystem"


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


def test_affects_hex_at_global_location():
    """Warp point at local (5,5) within system at (50,50) -> global (55,55)."""
    src = WarpPointAbilitySource(
        warp_point=_wp(location=HexCoord(5, 5)),
        system=_MockSystem(global_location=HexCoord(50, 50)),
    )
    assert src.affects_hex(HexCoord(55, 55)) is True
    assert src.affects_hex(HexCoord(99, 99)) is False


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
