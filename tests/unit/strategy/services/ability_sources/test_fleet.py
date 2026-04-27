"""Tests for FleetAbilitySource (PROJ-305)."""
from dataclasses import dataclass, field
from typing import Any, Dict, List

from game.core.hex_math import HexCoord
from game.core.protocols import IAbilitySource, is_ability_source
from game.strategy.services.ability_sources import FleetAbilitySource


@dataclass
class _MockShip:
    design_data: Dict[str, Any] = field(default_factory=dict)
    _is_combat: bool = True

    def is_combat_capable(self) -> bool:
        return self._is_combat


@dataclass
class _MockFleet:
    id: int = 1
    owner_id: int = 0
    location: Any = HexCoord(5, 5)
    display_name: str = ""
    ships: List[Any] = field(default_factory=list)
    is_hidden: bool = False


def _ship_with_ability(ability_name, ability_data):
    """Build a ship whose design has one component with the given ability."""
    return _MockShip(design_data={
        "layers": {
            "CORE": [
                {"id": f"comp_{ability_name}", "abilities": {ability_name: ability_data}},
            ],
        },
    })


def test_source_kind_is_fleet():
    src = FleetAbilitySource(fleet=_MockFleet())
    assert src.source_kind == 'fleet'


def test_source_label_uses_display_name_or_fleet_id():
    src1 = FleetAbilitySource(fleet=_MockFleet(id=42, owner_id=1, display_name="Indomitable"))
    assert "Indomitable" in src1.source_label
    assert "Player 1" in src1.source_label

    src2 = FleetAbilitySource(fleet=_MockFleet(id=42, owner_id=1))
    assert "Fleet 42" in src2.source_label


def test_source_id_uses_fleet_id():
    src = FleetAbilitySource(fleet=_MockFleet(id=42))
    assert src.source_id == "fleet:42"


def test_owner_id_propagates():
    src = FleetAbilitySource(fleet=_MockFleet(owner_id=7))
    assert src.owner_id == 7


def test_get_abilities_extracts_strategic_scope():
    """Strategic-scope abilities flow through; combat-only scopes are filtered."""
    fleet = _MockFleet(ships=[
        _ship_with_ability("ShieldModifier", {"multiplier": 1.25, "scope": "allied_sector"}),
    ])
    src = FleetAbilitySource(fleet=fleet)
    abilities = src.get_abilities()
    assert "ShieldModifier" in abilities
    assert abilities["ShieldModifier"][0]["scope"] == "allied_sector"


def test_get_abilities_filters_combat_scopes():
    """scope: fleet (combat-only) does NOT flow through strategic projection."""
    fleet = _MockFleet(ships=[
        _ship_with_ability("ShieldProjection", {"value": 100, "scope": "fleet"}),  # Combat scope
    ])
    src = FleetAbilitySource(fleet=fleet)
    assert src.get_abilities() == {}


def test_get_abilities_skips_inactive_ships():
    fleet = _MockFleet(ships=[
        _MockShip(design_data={"layers": {"CORE": [
            {"id": "x", "abilities": {"ShieldModifier": {"multiplier": 1.25, "scope": "allied_sector"}}},
        ]}}, _is_combat=False),
    ])
    src = FleetAbilitySource(fleet=fleet)
    assert src.get_abilities() == {}


def test_get_abilities_memoized():
    """PROJ-305 D12: per-instance memoization avoids re-walking ships."""
    fleet = _MockFleet(ships=[
        _ship_with_ability("ShieldModifier", {"multiplier": 1.25, "scope": "allied_sector"}),
    ])
    src = FleetAbilitySource(fleet=fleet)
    first = src.get_abilities()
    second = src.get_abilities()
    assert first is second  # Same dict object, not just equal.


def test_cloaked_fleet_projects_nothing():
    """PROJ-305 D11: cloaked fleets project no abilities."""
    fleet = _MockFleet(
        is_hidden=True,
        ships=[_ship_with_ability("ShieldModifier", {"multiplier": 1.25, "scope": "allied_sector"})],
    )
    src = FleetAbilitySource(fleet=fleet)
    assert src.get_abilities() == {}
    assert src.affects_hex(HexCoord(5, 5)) is False


def test_affects_hex_matches_fleet_location():
    fleet = _MockFleet(location=HexCoord(5, 5))
    src = FleetAbilitySource(fleet=fleet)
    assert src.affects_hex(HexCoord(5, 5)) is True
    assert src.affects_hex(HexCoord(99, 99)) is False


def test_get_activation_state_is_none():
    src = FleetAbilitySource(fleet=_MockFleet())
    assert src.get_activation_state("ShieldModifier") is None


def test_satisfies_iability_source_protocol():
    src = FleetAbilitySource(fleet=_MockFleet())
    assert isinstance(src, IAbilitySource)
    assert is_ability_source(src)
