"""StormAbilitySource adapter — wraps a Storm entity (PROJ-300).

Storms are sector-scope ability sources with no owner. Phase 3 supports both
the legacy `Storm.effects: StormEffect` shape (translates to abilities dict
on-the-fly) AND the new `Storm.abilities: Dict[str, Any]` shape introduced in
Phase 5. After Phase 5 lands, the legacy translation path is removed.
"""
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class StormAbilitySource:
    """IAbilitySource adapter for Storm entities."""
    storm: Any  # game.strategy.data.storm.Storm

    @property
    def source_kind(self) -> str:
        return 'storm'

    @property
    def source_label(self) -> str:
        return getattr(self.storm, 'name', 'Storm')

    @property
    def source_id(self) -> str:
        # Storm.name is a stable display id (Storms have no UUID); prefix to
        # disambiguate from other source kinds.
        return f"storm:{getattr(self.storm, 'name', id(self.storm))}"

    @property
    def owner_id(self) -> Optional[int]:
        return None  # Storms are ownerless — apply to all empires.

    def get_abilities(self) -> Dict[str, Any]:
        """Return storm abilities dict.

        Phase-5-aware: if the storm carries a non-empty `abilities` dict, use
        it. Otherwise, fall back to translating from the legacy
        `effects: StormEffect` shape (Phase 7 removes the fallback).
        """
        abilities_attr = getattr(self.storm, 'abilities', None)
        if isinstance(abilities_attr, dict) and abilities_attr:
            return abilities_attr

        # Legacy translation — Phase 7 removes this once StormEffect is gone.
        effects = getattr(self.storm, 'effects', None)
        if effects is None:
            return abilities_attr if isinstance(abilities_attr, dict) else {}
        return _legacy_effects_to_abilities(effects)

    def affects_hex(self, hex_coord) -> bool:
        # Storm.occupied_hexes is in local-system coordinates; the iterator
        # passes the GLOBAL hex it's queried for. Caller-specified hex match
        # logic; for symmetry with the legacy AreaEffectManager check, we
        # delegate to the storm's `occupied_hexes` property.
        try:
            occupied = self.storm.occupied_hexes
        except AttributeError:
            return False
        return hex_coord in occupied

    def affects_system(self, system) -> bool:
        # A storm belongs to exactly one system. The iterator is responsible
        # for only calling adapters from the right system; if asked, we
        # return True (the system that produced this adapter).
        return True

    def get_activation_state(self, ability_name: str) -> Optional[Any]:
        return None  # Storms are always active.


def _legacy_effects_to_abilities(effects: Any) -> Dict[str, Any]:
    """Translate a legacy `StormEffect` instance to the abilities-dict shape.

    Used during the Phase 3-5 migration window. Removed in Phase 5 when
    `Storm.abilities` becomes the single source of truth.
    """
    abilities: Dict[str, Any] = {}

    shield_mult = getattr(effects, 'shield_capacity_mult', 1.0)
    if shield_mult != 1.0:
        abilities['ShieldModifier'] = {
            'multiplier': shield_mult,
            'scope': 'sector',
        }

    thrust_mult = getattr(effects, 'thrust_mult', 1.0)
    if thrust_mult != 1.0:
        abilities['ThrustModifier'] = {
            'multiplier': thrust_mult,
            'scope': 'sector',
        }

    strategic_mult = getattr(effects, 'strategic_mult', 1.0)
    if strategic_mult != 1.0:
        abilities['StrategicSpeedModifier'] = {
            'multiplier': strategic_mult,
            'scope': 'sector',
        }

    damage_per_tick = getattr(effects, 'damage_per_tick', 0.0)
    if damage_per_tick > 0.0:
        # Legacy data is per-tick; framework speaks per-turn. /tick * 100 = /turn.
        abilities['EnvironmentalDamage'] = {
            'rate': damage_per_tick * 100.0,
            'damage_type': 'environmental',
            'scope': 'sector',
        }

    fuel_drain_per_tick = getattr(effects, 'fuel_drain_per_tick', 0.0)
    if fuel_drain_per_tick > 0.0:
        abilities['FuelDrain'] = {
            'rate': fuel_drain_per_tick * 100.0,
            'scope': 'sector',
        }

    return abilities
