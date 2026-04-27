"""Tests for PlanetIntrinsicAbilitySource (PROJ-301)."""
from dataclasses import dataclass, field
from typing import Any, Dict

from game.core.hex_math import HexCoord
from game.core.protocols import IAbilitySource, is_ability_source
from game.strategy.services.ability_sources import PlanetIntrinsicAbilitySource


@dataclass
class _MockPlanetType:
    name: str = "MAGMA"


@dataclass
class _MockPlanet:
    id: int = 42
    name: str = "Tarsis IV"
    planet_type: Any = field(default_factory=_MockPlanetType)
    location: Any = HexCoord(2, 3)
    intrinsic_abilities: Dict[str, Any] = field(default_factory=dict)


@dataclass
class _MockSystem:
    global_location: Any = HexCoord(10, 10)


def test_source_kind_is_planet():
    src = PlanetIntrinsicAbilitySource(planet=_MockPlanet(), system=_MockSystem())
    assert src.source_kind == 'planet'


def test_source_label_is_planet_name_with_type():
    src = PlanetIntrinsicAbilitySource(
        planet=_MockPlanet(name="Tarsis IV", planet_type=_MockPlanetType(name="MAGMA")),
        system=_MockSystem(),
    )
    assert src.source_label == "Tarsis IV (Magma)"


def test_source_id_uses_planet_id():
    src = PlanetIntrinsicAbilitySource(
        planet=_MockPlanet(id=42), system=_MockSystem(),
    )
    assert src.source_id == "planet:42"


def test_owner_id_is_always_none():
    """PROJ-301 D2: planet intrinsics are ownerless."""
    planet = _MockPlanet()
    planet.owner_id = 7  # type: ignore[attr-defined]
    src = PlanetIntrinsicAbilitySource(planet=planet, system=_MockSystem())
    assert src.owner_id is None


def test_get_abilities_returns_intrinsic_dict():
    abilities = {"EnvironmentalDamage": {"rate": 0.3, "damage_type": "thermal", "scope": "sector"}}
    src = PlanetIntrinsicAbilitySource(
        planet=_MockPlanet(intrinsic_abilities=abilities),
        system=_MockSystem(),
    )
    assert src.get_abilities() == abilities


def test_get_abilities_empty_when_planet_has_none():
    src = PlanetIntrinsicAbilitySource(planet=_MockPlanet(), system=_MockSystem())
    assert src.get_abilities() == {}


def test_affects_hex_at_global_location():
    """Planet at local (2,3) within system at (10,10) -> global (12,13)."""
    src = PlanetIntrinsicAbilitySource(
        planet=_MockPlanet(location=HexCoord(2, 3)),
        system=_MockSystem(global_location=HexCoord(10, 10)),
    )
    assert src.affects_hex(HexCoord(12, 13)) is True
    assert src.affects_hex(HexCoord(99, 99)) is False


def test_get_activation_state_is_none():
    src = PlanetIntrinsicAbilitySource(planet=_MockPlanet(), system=_MockSystem())
    assert src.get_activation_state("EnvironmentalDamage") is None


def test_satisfies_iability_source_protocol():
    src = PlanetIntrinsicAbilitySource(planet=_MockPlanet(), system=_MockSystem())
    assert isinstance(src, IAbilitySource)
    assert is_ability_source(src)
