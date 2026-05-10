"""Tests for SystemAbilitySource (PROJ-304)."""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from game.core.protocols import IAbilitySource, is_ability_source
from game.strategy.services.ability_sources import SystemAbilitySource


@dataclass
class _MockSystem:
    name: str = "Sol"
    archetype: Optional[str] = None
    intrinsic_abilities: Dict[str, Any] = field(default_factory=dict)


def test_source_kind_is_system():
    src = SystemAbilitySource(system=_MockSystem(archetype='nebula'))
    assert src.source_kind == 'system'


def test_source_label_uses_archetype_title_case():
    src = SystemAbilitySource(system=_MockSystem(name="Bellatrix", archetype='ancient_battlefield'))
    assert src.source_label == "Bellatrix (Ancient Battlefield)"


def test_source_id_uses_system_name():
    src = SystemAbilitySource(system=_MockSystem(name="Sol"))
    assert src.source_id == "system:Sol"


def test_owner_id_is_none():
    src = SystemAbilitySource(system=_MockSystem())
    assert src.owner_id is None


def test_get_abilities_returns_intrinsic_dict():
    abilities = {
        "ShieldModifier": {"multiplier": 0.85, "scope": "system"},
        "StrategicSpeedModifier": {"multiplier": 0.8, "scope": "system"},
    }
    src = SystemAbilitySource(system=_MockSystem(archetype='nebula', intrinsic_abilities=abilities))
    assert src.get_abilities() == abilities


def test_satisfies_iability_source_protocol():
    src = SystemAbilitySource(system=_MockSystem(archetype='nebula'))
    assert isinstance(src, IAbilitySource)
    assert is_ability_source(src)


def test_starsystem_archetype_serialization_roundtrip():
    """StarSystem with archetype + intrinsic_abilities round-trips."""
    from game.core.hex_math import HexCoord
    from game.strategy.data.galaxy import StarSystem

    sys = StarSystem(
        name="Bellatrix",
        global_location=HexCoord(50, 50),
        archetype='ancient_battlefield',
        intrinsic_abilities={
            "EnvironmentalDamage": {"rate": 0.1, "damage_type": "debris", "scope": "system"},
        },
    )
    data = sys.to_dict()
    assert data['archetype'] == 'ancient_battlefield'
    restored = StarSystem.from_dict(data)
    assert restored.archetype == 'ancient_battlefield'
    assert restored.intrinsic_abilities == sys.intrinsic_abilities
