"""PROJ-303 Phase 3 integration test: a fleet at an unstable warp point's
hex receives EnvironmentalDamage (damage_type='warp') from the unified
sector-effects pipeline. Verifies the full path:

    WarpPoint(unstable, intrinsic_abilities) -> WarpPointAbilitySource ->
    iter_ability_sources_at_hex -> collect_sector_effects ->
    aggregate_rates -> caller (e.g. environmental_hazard_engine).

This is the end-to-end smoke test for warp-point intrinsic damage that the
skeptical review flagged as missing.
"""
from dataclasses import dataclass, field
from typing import Any, List

from game.core.hex_math import HexCoord
from game.strategy.data.galaxy import WarpPoint
from game.strategy.services.system_effects_collector import collect_sector_effects


@dataclass
class _MockSystem:
    name: str = "Test System"
    global_location: Any = HexCoord(0, 0)
    planets: List[Any] = field(default_factory=list)
    storms: List[Any] = field(default_factory=list)
    stars: List[Any] = field(default_factory=list)
    warp_points: List[Any] = field(default_factory=list)
    archetype: Any = None
    intrinsic_abilities: dict = field(default_factory=dict)


def test_unstable_warp_point_emits_environmental_damage_at_its_hex():
    """A fleet sitting at an unstable warp point's global hex should see
    EnvironmentalDamage in the sector-effects pipeline."""
    wp = WarpPoint(
        destination_id='OtherSystem',
        location=HexCoord(5, 5),  # Local to system at global (0,0) -> global (5,5)
        warp_type='unstable',
        intrinsic_abilities={
            'EnvironmentalDamage': {
                'rate': 0.5,
                'damage_type': 'warp',
                'scope': 'sector',
            },
        },
    )
    system = _MockSystem(global_location=HexCoord(0, 0), warp_points=[wp])

    effects = collect_sector_effects(system, HexCoord(5, 5), empire_id=1)
    env_damage = [e for e in effects if e['ability_name'] == 'EnvironmentalDamage']
    assert env_damage, "Unstable warp point at hex must emit EnvironmentalDamage"
    assert env_damage[0]['damage_type'] == 'warp'
    assert env_damage[0]['kind'] == 'rate'
    assert env_damage[0]['aggregate_value'] == 0.5
    # Provider should be the warp point itself.
    provider = env_damage[0]['providers'][0]
    assert provider['source_kind'] == 'warp_point'
    assert provider['owner_id'] is None  # Warp points are ownerless.


def test_stable_warp_point_emits_no_damage():
    """Stable warp points have no intrinsic abilities — no damage should fire."""
    wp = WarpPoint(
        destination_id='OtherSystem',
        location=HexCoord(5, 5),
        warp_type='stable',
        intrinsic_abilities={},
    )
    system = _MockSystem(global_location=HexCoord(0, 0), warp_points=[wp])
    effects = collect_sector_effects(system, HexCoord(5, 5), empire_id=1)
    env_damage = [e for e in effects if e['ability_name'] == 'EnvironmentalDamage']
    assert env_damage == []


def test_unstable_warp_point_does_not_emit_damage_at_distant_hex():
    """Damage only fires at the warp point's hex, not adjacent hexes."""
    wp = WarpPoint(
        destination_id='OtherSystem',
        location=HexCoord(5, 5),
        warp_type='unstable',
        intrinsic_abilities={
            'EnvironmentalDamage': {'rate': 0.5, 'damage_type': 'warp', 'scope': 'sector'},
        },
    )
    system = _MockSystem(global_location=HexCoord(0, 0), warp_points=[wp])
    # Query a far-away hex.
    effects = collect_sector_effects(system, HexCoord(99, 99), empire_id=1)
    env_damage = [e for e in effects if e['ability_name'] == 'EnvironmentalDamage']
    assert env_damage == []


def test_dimensional_rift_emits_shield_modifier():
    """Dimensional rifts impair shields rather than deal damage."""
    wp = WarpPoint(
        destination_id='OtherSystem',
        location=HexCoord(0, 0),
        warp_type='dimensional_rift',
        intrinsic_abilities={
            'ShieldModifier': {'multiplier': 0.7, 'scope': 'sector'},
        },
    )
    system = _MockSystem(global_location=HexCoord(0, 0), warp_points=[wp])
    effects = collect_sector_effects(system, HexCoord(0, 0), empire_id=1)
    shields = [e for e in effects if e['ability_name'] == 'ShieldModifier']
    assert shields
    assert shields[0]['aggregate_value'] == 0.7
