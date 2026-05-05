"""EffectAbilityMetadata registry for strategic-layer effect aggregation (PROJ-362 Phase 2).

Replaces the hardcoded module-level constants previously living in
`system_effects_collector` (`SYSTEM_EFFECT_ABILITIES`, `_RATE_ABILITIES`,
`_OWNER_AWARE_SCOPES`) and the name-keyed branches in `make_group_key` /
`make_display_name`. Each `EffectAbilityMetadata` entry tells the collector:

  - the canonical display name (or that it should be derived from a data field),
  - whether the value is a rate or a multiplier,
  - whether the ability is activatable,
  - which `ability_data` field (if any) drives per-instance grouping,
  - which scopes require the source to declare an `owner_id`,
  - which fields to read for the value, with fallback.

Adding a new strategic effect is now a single-entry edit to
`EFFECT_ABILITY_METADATA` — no more code edits to the collector.

Pattern reference: `stabilizer_registry.py:54-70` — frozen dataclass + tuple
registry with name-keyed lookup helpers.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional


# PROJ-300 D17: ownership-aware scopes can only be declared by sources with
# an owner_id. "enemy_sector" on an ownerless storm is undefined ("enemy of
# whom?"). The collector skips + logs when an ownerless source declares one
# of these. Shared by every effect ability.
_OWNER_AWARE_SCOPES: frozenset[str] = frozenset({
    'allied_sector', 'enemy_sector', 'player_sector',
    'allied_system', 'enemy_system', 'player_system',
    'allied_empire',
})


@dataclass(frozen=True)
class EffectAbilityMetadata:
    """Declarative metadata for a strategic effect ability.

    Attributes:
        ability_name: Registry key (matches the ability_data dict key in
            component / source ability listings).
        display_name: Human-readable label. ``None`` means the label is
            derived from ``ability_data`` via ``grouping_key_field`` (e.g.
            "Metals Harvest Boost" from ``resource_type='metals'``).
        kind: ``'rate'`` for additively aggregated rate-style abilities
            (EnvironmentalDamage, FuelDrain). ``'multiplier'`` for
            multiplicatively aggregated multiplier-style abilities.
        is_activatable: ``True`` for abilities that have an ``activation_time``
            field (stabilizers, shield modifiers). Activatable abilities read
            their per-source activation state via
            ``source.get_activation_state``; non-activatable abilities are
            always-on.
        grouping_key_field: ``ability_data`` field used to compute the group
            key (e.g. ``'resource_type'`` for ResourceHarvestBooster). When
            ``None`` the group key is the ability_name alone.
        owner_aware_scopes: Scopes that require the source to declare an
            ``owner_id``. Currently the same set for every entry, but
            keeping this per-entry leaves room for future divergence.
        value_field_primary: Primary ``ability_data`` field read for the
            per-source value (``'rate'`` or ``'multiplier'``).
        value_field_fallback: Fallback field read when ``value_field_primary``
            is missing (legacy schemas used ``'improvement_rate'``).
    """
    ability_name: str
    display_name: Optional[str]
    kind: Literal['rate', 'multiplier']
    is_activatable: bool
    grouping_key_field: Optional[str]
    owner_aware_scopes: frozenset[str]
    value_field_primary: str
    value_field_fallback: str


def _multiplier(ability_name: str, display_name: Optional[str], *,
                is_activatable: bool, grouping_key_field: Optional[str] = None
                ) -> EffectAbilityMetadata:
    """Helper: construct a multiplier-style EffectAbilityMetadata."""
    return EffectAbilityMetadata(
        ability_name=ability_name,
        display_name=display_name,
        kind='multiplier',
        is_activatable=is_activatable,
        grouping_key_field=grouping_key_field,
        owner_aware_scopes=_OWNER_AWARE_SCOPES,
        value_field_primary='multiplier',
        value_field_fallback='improvement_rate',
    )


def _rate(ability_name: str, display_name: Optional[str], *,
          grouping_key_field: Optional[str] = None) -> EffectAbilityMetadata:
    """Helper: construct a rate-style EffectAbilityMetadata."""
    return EffectAbilityMetadata(
        ability_name=ability_name,
        display_name=display_name,
        kind='rate',
        is_activatable=False,
        grouping_key_field=grouping_key_field,
        owner_aware_scopes=_OWNER_AWARE_SCOPES,
        value_field_primary='rate',
        value_field_fallback='improvement_rate',
    )


# Authoritative metadata registry. Order is irrelevant; lookup is by
# ability_name. Adding a new strategic effect is a single tuple-entry edit.
EFFECT_ABILITY_METADATA: tuple[EffectAbilityMetadata, ...] = (
    # Activatable stabilizers (multiplier-style; no per-instance grouping).
    _multiplier('GeologicStabilizer', 'Geologic Stabilizer', is_activatable=True),
    _multiplier('StellarStabilizer', 'Stellar Stabilizer', is_activatable=True),
    _multiplier('WarpFieldStabilizer', 'Warp Field Stabilizer', is_activatable=True),

    # Resource boosters (passive multiplier; per-resource_type grouping).
    _multiplier('ResourceHarvestBooster', None,
                is_activatable=False, grouping_key_field='resource_type'),
    _multiplier('QualityImprovement', 'Quality Enrichment',
                is_activatable=False, grouping_key_field='resource_type'),

    # Construction acceleration.
    _multiplier('BuildRateBooster', 'Construction Acceleration',
                is_activatable=False),

    # Shield / damage / thrust / strategic-speed modifiers (multiplier-style;
    # is_activatable depends on whether the entry carries `activation_time`,
    # which the collector still detects via `_is_activatable(entry)`. The
    # registry default here is False because most modifier entries are
    # passive intrinsic abilities; activatable facility components are
    # detected per-entry, not via the registry).
    _multiplier('ShieldModifier', 'Shield Modifier', is_activatable=False),
    _multiplier('DamageModifier', 'Damage Modifier', is_activatable=False),
    _multiplier('ThrustModifier', 'Thrust Modifier', is_activatable=False),
    _multiplier('StrategicSpeedModifier', 'Strategic Speed Modifier',
                is_activatable=False),

    # Rate-style environmental hazards.
    _rate('EnvironmentalDamage', None, grouping_key_field='damage_type'),
    _rate('FuelDrain', 'Fuel Drain'),
)


# Index by ability_name for O(1) lookup. Built once at module load.
_BY_NAME: dict[str, EffectAbilityMetadata] = {
    m.ability_name: m for m in EFFECT_ABILITY_METADATA
}


def find_metadata(ability_name: str) -> Optional[EffectAbilityMetadata]:
    """Return the metadata entry for `ability_name`, or None if unknown."""
    return _BY_NAME.get(ability_name)


def is_known_effect_ability(ability_name: str) -> bool:
    """True iff `ability_name` is registered in the effect-metadata registry."""
    return ability_name in _BY_NAME


def all_owner_aware_scopes() -> frozenset[str]:
    """Union of `owner_aware_scopes` across every registered entry.

    Preserves the original `_OWNER_AWARE_SCOPES` semantics for the global
    "ownerless source declared an owner-aware scope" check inside the
    collector pipeline.
    """
    if not EFFECT_ABILITY_METADATA:
        return frozenset()
    result: frozenset[str] = frozenset()
    for m in EFFECT_ABILITY_METADATA:
        result = result | m.owner_aware_scopes
    return result
