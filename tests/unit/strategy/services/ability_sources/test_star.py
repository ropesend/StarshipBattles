"""Tests for StarAbilitySource (PROJ-302)."""
from dataclasses import dataclass, field
from typing import Any, Dict

from game.core.hex_math import HexCoord
from game.core.protocols import IAbilitySource, is_ability_source
from game.strategy.services.ability_sources import StarAbilitySource


@dataclass
class _MockStarType:
    name: str = "NEUTRON_STAR"


@dataclass
class _MockStar:
    name: str = "Sol"
    star_type: Any = field(default_factory=_MockStarType)
    location: Any = HexCoord(0, 0)
    intrinsic_abilities: Dict[str, Any] = field(default_factory=dict)


@dataclass
class _MockSystem:
    global_location: Any = HexCoord(20, 20)


def test_source_kind_is_star():
    src = StarAbilitySource(star=_MockStar(), system=_MockSystem())
    assert src.source_kind == 'star'


def test_source_label_uses_star_name_and_type():
    src = StarAbilitySource(
        star=_MockStar(name="Pulsar X-1", star_type=_MockStarType(name="NEUTRON_STAR")),
        system=_MockSystem(),
    )
    assert src.source_label == "Pulsar X-1 (Neutron Star)"


def test_source_id_uses_star_name():
    src = StarAbilitySource(star=_MockStar(name="Sol"), system=_MockSystem())
    assert src.source_id == "star:Sol"


def test_owner_id_is_none():
    src = StarAbilitySource(star=_MockStar(), system=_MockSystem())
    assert src.owner_id is None


def test_get_abilities_returns_intrinsic_dict():
    abilities = {
        "EnvironmentalDamage": {"rate": 0.3, "damage_type": "radiation", "scope": "system"},
        "ShieldModifier": {"multiplier": 0.8, "scope": "system"},
    }
    src = StarAbilitySource(
        star=_MockStar(intrinsic_abilities=abilities),
        system=_MockSystem(),
    )
    assert src.get_abilities() == abilities


def test_affects_hex_at_star_global_location():
    """Star at local (0,0) within system at (20,20) -> global (20,20)."""
    src = StarAbilitySource(
        star=_MockStar(location=HexCoord(0, 0)),
        system=_MockSystem(global_location=HexCoord(20, 20)),
    )
    assert src.affects_hex(HexCoord(20, 20)) is True
    assert src.affects_hex(HexCoord(99, 99)) is False


def test_source_label_defaults_to_star_when_type_missing():
    src = StarAbilitySource(
        star=_MockStar(name="Nameless", star_type=None),
        system=_MockSystem(),
    )
    assert src.source_label == "Nameless (Star)"


def test_get_abilities_returns_empty_dict_when_missing():
    src = StarAbilitySource(
        star=_MockStar(intrinsic_abilities=None),
        system=_MockSystem(),
    )
    assert src.get_abilities() == {}


def test_affects_hex_uses_system_location_when_global_location_missing():
    system = type("SystemWithLocation", (), {"location": HexCoord(7, 8)})()
    src = StarAbilitySource(
        star=_MockStar(location=HexCoord(2, -1)),
        system=system,
    )
    assert src.affects_hex(HexCoord(9, 7)) is True


def test_affects_hex_returns_false_without_location_data():
    missing_star_location = StarAbilitySource(
        star=_MockStar(location=None),
        system=_MockSystem(global_location=HexCoord(20, 20)),
    )
    missing_system_location = StarAbilitySource(
        star=_MockStar(location=HexCoord(0, 0)),
        system=type("SystemWithoutLocation", (), {})(),
    )

    assert missing_star_location.affects_hex(HexCoord(20, 20)) is False
    assert missing_system_location.affects_hex(HexCoord(20, 20)) is False


def test_affects_hex_returns_false_when_locations_cannot_be_added():
    src = StarAbilitySource(
        star=_MockStar(location=object()),
        system=_MockSystem(global_location=object()),
    )
    assert src.affects_hex(HexCoord(20, 20)) is False


def test_affects_hex_returns_true_for_system_scope_ability_at_any_hex():
    """PROJ-398 / FND-041: star declaring a system-scope ability is visible
    at every hex of the system, not just the star's own hex.

    This widening lets `_star_provider` use the shared
    `_iter_hex_filtered_sources` skeleton.
    """
    abilities_with_system_scope = {
        "RadiationField": {"rate": 0.3, "scope": "system"},
    }
    src = StarAbilitySource(
        star=_MockStar(
            location=HexCoord(0, 0),
            intrinsic_abilities=abilities_with_system_scope,
        ),
        system=_MockSystem(global_location=HexCoord(20, 20)),
    )
    # Star's global hex is (20, 20); a hex elsewhere in the system still
    # gets True because of the system-scope ability.
    assert src.affects_hex(HexCoord(99, 99)) is True
    assert src.affects_hex(HexCoord(20, 20)) is True


def test_affects_hex_returns_true_for_allied_system_scope():
    """system-shaped scopes (`allied_system` etc.) all qualify."""
    abilities = {"Buff": {"scope": "allied_system"}}
    src = StarAbilitySource(
        star=_MockStar(
            location=HexCoord(0, 0),
            intrinsic_abilities=abilities,
        ),
        system=_MockSystem(global_location=HexCoord(20, 20)),
    )
    assert src.affects_hex(HexCoord(50, 50)) is True


def test_affects_hex_supports_list_valued_ability_entries():
    """When intrinsic_abilities maps name -> list of dicts (multi-instance
    declaration), system-scope detection still works."""
    abilities = {
        "MultiInstance": [
            {"scope": "sector"},
            {"scope": "system"},
        ],
    }
    src = StarAbilitySource(
        star=_MockStar(
            location=HexCoord(0, 0),
            intrinsic_abilities=abilities,
        ),
        system=_MockSystem(global_location=HexCoord(20, 20)),
    )
    assert src.affects_hex(HexCoord(99, 99)) is True


def test_affects_hex_returns_false_when_only_sector_scope_and_hex_mismatches():
    """Star with sector-scope-only abilities at a non-matching hex returns False."""
    abilities = {"LocalEffect": {"scope": "sector"}}
    src = StarAbilitySource(
        star=_MockStar(
            location=HexCoord(0, 0),
            intrinsic_abilities=abilities,
        ),
        system=_MockSystem(global_location=HexCoord(20, 20)),
    )
    # Star's global hex is (20, 20) — a different hex returns False.
    assert src.affects_hex(HexCoord(99, 99)) is False
    assert src.affects_hex(HexCoord(20, 20)) is True


def test_affects_system_matches_only_parent_system():
    system = _MockSystem()
    src = StarAbilitySource(star=_MockStar(), system=system)

    assert src.affects_system(system) is True
    assert src.affects_system(_MockSystem()) is False


def test_get_activation_state_is_none():
    src = StarAbilitySource(star=_MockStar(), system=_MockSystem())
    assert src.get_activation_state("EnvironmentalDamage") is None


def test_satisfies_iability_source_protocol():
    src = StarAbilitySource(star=_MockStar(), system=_MockSystem())
    assert isinstance(src, IAbilitySource)
    assert is_ability_source(src)
