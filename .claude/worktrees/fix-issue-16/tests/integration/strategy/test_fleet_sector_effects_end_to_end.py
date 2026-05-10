"""PROJ-305 Phase 3 integration tests: full path from Fleet at hex through
FleetAbilitySource → iterator → collector → effect dict.

Per phase_3_checklist.md Task 3.4, six scenarios:
1. Fleet at hex with flagship renders ShieldModifier effect.
2. Combat at hex picks up flagship ShieldModifier (covered by spec_compiler tests).
3. Fleet moves to new hex; effect moves too (per-instance memoization correctness).
4. Enemy fleet does NOT see allied_sector effect.
5. Combat scopes (scope=fleet) don't leak into strategic projection.
6. Cloaked fleet projects no abilities (D11).
"""
from dataclasses import dataclass, field
from typing import Any, List

from game.core.hex_math import HexCoord
from game.strategy.services.ability_iterator import (
    set_fleet_lookups,
    iter_ability_sources_at_hex,
)
from game.strategy.services.ability_sources import FleetAbilitySource
from game.strategy.services.system_effects_collector import collect_sector_effects


@dataclass
class _Ship:
    design_data: dict = field(default_factory=dict)
    is_combat: bool = True

    def is_combat_capable(self) -> bool:
        return self.is_combat


@dataclass
class _Fleet:
    id: int = 1
    owner_id: int = 0
    location: Any = HexCoord(5, 5)
    display_name: str = ""
    ships: List[Any] = field(default_factory=list)
    is_hidden: bool = False


@dataclass
class _Empire:
    id: int = 0
    fleets: List[Any] = field(default_factory=list)


@dataclass
class _MockSystem:
    name: str = "Sol"
    global_location: Any = HexCoord(0, 0)
    planets: List[Any] = field(default_factory=list)
    storms: List[Any] = field(default_factory=list)
    stars: List[Any] = field(default_factory=list)
    warp_points: List[Any] = field(default_factory=list)
    archetype: Any = None
    intrinsic_abilities: dict = field(default_factory=dict)


def _flagship_design():
    """Build a design with the Flagship Shield Projector ability."""
    return {
        "layers": {
            "OUTER": [
                {"id": "flagship_shield_projector", "abilities": {
                    "ShieldModifier": {"multiplier": 1.25, "scope": "allied_sector"},
                }},
            ],
        },
    }


def _setup_fleet_lookups(empires):
    """Register fleet-at-hex callbacks against an explicit empires list
    (mirrors GameInitializer._wire_fleet_lookups but for tests)."""
    def _at_hex(system, hex_coord):
        for empire in empires:
            for fleet in empire.fleets:
                if fleet.location == hex_coord:
                    yield fleet

    def _in_system(system):
        for empire in empires:
            for fleet in empire.fleets:
                yield fleet

    set_fleet_lookups(at_hex=_at_hex, in_system=_in_system)


def _teardown_fleet_lookups():
    set_fleet_lookups(at_hex=None, in_system=None)


def test_fleet_at_hex_with_flagship_renders_shield_modifier_effect():
    """Scenario 1: a flagship at hex H projects ShieldModifier visible in
    Sector Effects from the owner's perspective."""
    flagship = _Fleet(id=42, owner_id=1, location=HexCoord(5, 5),
                      ships=[_Ship(design_data=_flagship_design())])
    empire = _Empire(id=1, fleets=[flagship])
    system = _MockSystem(global_location=HexCoord(0, 0))

    _setup_fleet_lookups([empire])
    try:
        effects = collect_sector_effects(system, HexCoord(5, 5), empire_id=1)
        shields = [e for e in effects if e['ability_name'] == 'ShieldModifier']
        assert shields, "Flagship should project ShieldModifier at its hex"
        assert shields[0]['aggregate_value'] == 1.25
        provider = shields[0]['providers'][0]
        assert provider['source_kind'] == 'fleet'
        assert provider['owner_id'] == 1
    finally:
        _teardown_fleet_lookups()


def test_fleet_move_relocates_effect():
    """Scenario 3: when the fleet moves, the effect appears at the new hex."""
    flagship = _Fleet(id=42, owner_id=1, location=HexCoord(5, 5),
                      ships=[_Ship(design_data=_flagship_design())])
    empire = _Empire(id=1, fleets=[flagship])
    system = _MockSystem(global_location=HexCoord(0, 0))

    _setup_fleet_lookups([empire])
    try:
        # Initially at (5,5)
        e1 = collect_sector_effects(system, HexCoord(5, 5), empire_id=1)
        assert any(e['ability_name'] == 'ShieldModifier' for e in e1)
        # Move
        flagship.location = HexCoord(7, 7)
        # Old hex no longer has the effect
        e2 = collect_sector_effects(system, HexCoord(5, 5), empire_id=1)
        assert not any(e['ability_name'] == 'ShieldModifier' for e in e2)
        # New hex picks it up
        e3 = collect_sector_effects(system, HexCoord(7, 7), empire_id=1)
        assert any(e['ability_name'] == 'ShieldModifier' for e in e3)
    finally:
        _teardown_fleet_lookups()


def test_enemy_fleet_does_not_see_allied_sector_effect():
    """Scenario 4: scope=allied_sector with an OWNER means only the owner
    empire sees the effect; an enemy querying the same hex doesn't."""
    flagship = _Fleet(id=42, owner_id=1, location=HexCoord(5, 5),
                      ships=[_Ship(design_data=_flagship_design())])
    empire1 = _Empire(id=1, fleets=[flagship])
    enemy_empire = _Empire(id=2, fleets=[])
    system = _MockSystem(global_location=HexCoord(0, 0))

    _setup_fleet_lookups([empire1, enemy_empire])
    try:
        # Owner sees it
        owner_effects = collect_sector_effects(system, HexCoord(5, 5), empire_id=1)
        assert any(e['ability_name'] == 'ShieldModifier' for e in owner_effects)
        # Enemy querying does NOT see it (owner_id=1, query empire=2)
        enemy_effects = collect_sector_effects(system, HexCoord(5, 5), empire_id=2)
        assert not any(e['ability_name'] == 'ShieldModifier' for e in enemy_effects)
    finally:
        _teardown_fleet_lookups()


def test_combat_scope_does_not_leak_into_strategic():
    """Scenario 5: scope=fleet (combat-only) on a fleet's component does NOT
    flow through FleetAbilitySource (filtered out by _STRATEGIC_SCOPES)."""
    fleet = _Fleet(id=42, owner_id=1, location=HexCoord(5, 5),
                   ships=[_Ship(design_data={"layers": {"OUTER": [
                       {"id": "x", "abilities": {
                           "ShieldProjection": {"value": 100, "scope": "fleet"},
                       }},
                   ]}})])
    src = FleetAbilitySource(fleet=fleet)
    abilities = src.get_abilities()
    # ShieldProjection scope=fleet is combat-only — must NOT appear here.
    assert 'ShieldProjection' not in abilities


def test_cloaked_fleet_projects_nothing():
    """Scenario 6 (D11): a cloaked fleet projects no abilities."""
    flagship = _Fleet(id=42, owner_id=1, location=HexCoord(5, 5),
                      is_hidden=True,
                      ships=[_Ship(design_data=_flagship_design())])
    src = FleetAbilitySource(fleet=flagship)
    assert src.get_abilities() == {}
    assert src.affects_hex(HexCoord(5, 5)) is False


def test_fleet_provider_yields_only_when_lookups_configured():
    """Without set_fleet_lookups, the iterator's _fleet_provider yields nothing.
    Once configured, it yields the FleetAbilitySource adapter."""
    fleet = _Fleet(id=42, owner_id=1, location=HexCoord(5, 5),
                   ships=[_Ship(design_data=_flagship_design())])
    empire = _Empire(id=1, fleets=[fleet])
    system = _MockSystem(global_location=HexCoord(0, 0))

    # Without lookups: no fleet sources.
    _teardown_fleet_lookups()
    sources_no_lookup = list(iter_ability_sources_at_hex(system, HexCoord(5, 5)))
    assert not any(getattr(s, 'source_kind', None) == 'fleet' for s in sources_no_lookup)

    # With lookups: fleet source surfaces.
    _setup_fleet_lookups([empire])
    try:
        sources_with_lookup = list(iter_ability_sources_at_hex(system, HexCoord(5, 5)))
        assert any(getattr(s, 'source_kind', None) == 'fleet' for s in sources_with_lookup)
    finally:
        _teardown_fleet_lookups()
