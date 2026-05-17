"""EffectAbilityMetadata — strategy-layer effect-aggregation shim.

**Shim status (PROJ-429 / TD-07).** As of PROJ-429 this module is a thin
shim over the unified ``AbilityMetadataRegistry`` (``ability_metadata.py``).
The shim preserves three public helpers and the ``EffectAbilityMetadata``
dataclass signature so existing callers — ``effect_ability_display.py``,
``system_effects_collector.py`` and their consumer chains — continue to
work unchanged:

* ``EFFECT_ABILITY_METADATA`` — tuple of records derived from every
  ``AbilityMetadata`` entry whose ``effect`` facet is not ``None``.
* ``find_metadata(name)`` — returns ``EffectAbilityMetadata | None``.
* ``is_known_effect_ability(name)`` — fast membership.
* ``all_owner_aware_scopes()`` — union across registered entries.
* ``EffectAbilityMetadata`` — re-exported dataclass shape (now derived
  from ``EffectFacet`` + the ability name).

Collapsing this shim is intentionally OUT of scope for PROJ-429
(decisions.md row 2). The shim isolates the migration; a follow-up
project will collapse it once all downstream callers are ready to
migrate to the unified registry directly.

Original PROJ-362 Phase 2 docstring preserved below for historical
context. The registered ability list moved to ``ability_metadata.py``;
this module no longer carries the authoritative table.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

from game.strategy.services.ability_metadata import (
    EffectFacet,
    _ENTRIES,
)


# PROJ-300 D17: ownership-aware scopes can only be declared by sources with
# an owner_id. Same constant the legacy module exposed; the unified registry
# also stores this set per EffectFacet via _OWNER_AWARE_SCOPES.
_OWNER_AWARE_SCOPES: frozenset[str] = frozenset({
    'allied_sector', 'enemy_sector', 'player_sector',
    'allied_system', 'enemy_system', 'player_system',
    'allied_empire',
})


@dataclass(frozen=True)
class EffectAbilityMetadata:
    """Declarative metadata for a strategic effect ability.

    Public shape preserved from the pre-PROJ-429 module. New code should
    read from ``ability_metadata.AbilityMetadata`` / ``EffectFacet``
    directly; this dataclass is retained as a shim for backward
    compatibility.
    """
    ability_name: str
    display_name: Optional[str]
    kind: Literal['rate', 'multiplier']
    is_activatable: bool
    grouping_key_field: Optional[str]
    owner_aware_scopes: frozenset[str]
    value_field_primary: str
    value_field_fallback: str


def _from_facet(name: str, facet: EffectFacet) -> EffectAbilityMetadata:
    """Build an ``EffectAbilityMetadata`` view from a unified-registry
    ``EffectFacet``. Preserves the legacy public shape."""
    return EffectAbilityMetadata(
        ability_name=name,
        display_name=facet.display_name,
        kind=facet.kind,
        is_activatable=facet.is_activatable_hint,
        grouping_key_field=facet.grouping_key_field,
        owner_aware_scopes=facet.owner_aware_scopes,
        value_field_primary=facet.value_field_primary,
        value_field_fallback=facet.value_field_fallback,
    )


# Derived from the unified registry at import time. Iteration order
# follows ``ability_metadata._ENTRIES``, which mirrors the legacy
# author-time grouping (stabilizers, resource boosters, construction,
# combat modifiers, strategic-speed, environmental).
EFFECT_ABILITY_METADATA: tuple[EffectAbilityMetadata, ...] = tuple(
    _from_facet(m.name, m.effect)
    for m in _ENTRIES
    if m.effect is not None
)


# O(1) lookup index.
_BY_NAME: dict[str, EffectAbilityMetadata] = {
    m.ability_name: m for m in EFFECT_ABILITY_METADATA
}


def find_metadata(ability_name: str) -> Optional[EffectAbilityMetadata]:
    """Return the metadata entry for ``ability_name``, or ``None`` if unknown."""
    return _BY_NAME.get(ability_name)


def is_known_effect_ability(ability_name: str) -> bool:
    """True iff ``ability_name`` is registered in the effect-metadata registry."""
    return ability_name in _BY_NAME


def all_owner_aware_scopes() -> frozenset[str]:
    """Union of ``owner_aware_scopes`` across every registered entry.

    Preserves the original ``_OWNER_AWARE_SCOPES`` semantics for the
    global "ownerless source declared an owner-aware scope" check inside
    the collector pipeline.
    """
    if not EFFECT_ABILITY_METADATA:
        return frozenset()
    result: frozenset[str] = frozenset()
    for m in EFFECT_ABILITY_METADATA:
        result = result | m.owner_aware_scopes
    return result


__all__ = [
    "EFFECT_ABILITY_METADATA",
    "EffectAbilityMetadata",
    "all_owner_aware_scopes",
    "find_metadata",
    "is_known_effect_ability",
]
