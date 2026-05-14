"""System Effects Collector — aggregates strategic-layer abilities for UI display.

After PROJ-300 Phase 4, this module is a thin wrapper over the unified
`ability_iterator`. Walks every `IAbilitySource` adapter the iterator yields,
filters by scope, groups by `(ability_name, resource_type | damage_type)`,
and dispatches to either `aggregate_multipliers` (for multiplier-style
abilities like ShieldModifier) or `aggregate_rates` (for rate-style abilities
like EnvironmentalDamage). Storms, facilities, and (post-PROJ-301..305)
planets / stars / warp points / system archetypes / fleets all flow through
the same pipeline.

Effect dict shape:
- ability_name: str
- display_name: str
- group_key: str (for dedup/grouping)
- status: str ("Active"/"Inactive"/"Activating (N)"/"Deactivating (N)")
- resource_type: Optional[str]
- damage_type: Optional[str]      # NEW (PROJ-300) — for EnvironmentalDamage
- kind: 'multiplier' | 'rate'     # NEW (PROJ-300) — disambiguates aggregate
- aggregate_value: float           # 1.0 if multiplier+empty, 0.0 if rate+empty
- providers: list of provider dicts

Each provider carries the universal PROJ-300 fields (source_kind,
source_label, source_id, owner_id). The pre-PROJ-300 legacy back-compat
fields (planet_name, planet_id, facility_name, facility_id,
component_key) were retired in PROJ-362 Phase 4 along with the
``_legacy_provider_fields`` shim — UI consumers read ``source_label`` /
``source_kind`` / ``source_id`` directly.
"""
import logging
from typing import Any, Dict, List, TYPE_CHECKING

from game.strategy.data.component_activation_state import ActivationPhase
from game.strategy.services.strategic_ability_scanner import (
    aggregate_multipliers,
    aggregate_rates,
)
from game.strategy.services.ability_iterator import (
    iter_ability_sources_at_hex,
    iter_ability_sources_in_system,
)
from game.strategy.services.effect_ability_metadata import (
    find_metadata,
    is_known_effect_ability,
)
from game.strategy.services.effect_ability_display import (
    _format_status,
    _is_activatable,
    format_intrinsic_ability_magnitude,
    make_display_name,
    make_group_key,
)

if TYPE_CHECKING:
    from game.strategy.data.star_system import StarSystem
logger = logging.getLogger(__name__)


# Re-exports — the display/grouping/format helpers were moved to
# `effect_ability_display` (PROJ-362 audit remediation). Import from here is
# preserved so existing UI callers (planet_list_filters, planet_list_window,
# system_tree_panel) keep working without churn.
__all__ = [
    'collect_system_effects',
    'collect_sector_effects',
    'find_sector_effect',
    'aggregate_value_or',
    'make_group_key',
    'make_display_name',
    'format_intrinsic_ability_magnitude',
    'is_known_effect_ability',
]


# Scope sets for filtering effects into the correct UI panel.
# System = all hexes in a star system (radius 50, diameter 101).
# Sector = a single hex on the galaxy map.
_SYSTEM_SCOPES = frozenset({
    'system', 'allied_system', 'player_system', 'enemy_system',
})

_SECTOR_SCOPES = frozenset({
    'sector', 'allied_sector', 'player_sector', 'enemy_sector',
})


# PROJ-362: ability metadata (display name, kind, grouping, owner-aware
# scopes, value field selection) lives in `effect_ability_metadata.
# EFFECT_ABILITY_METADATA`. Adding a new strategic effect is a single-entry
# edit there — no changes needed here.


# ---------------------------------------------------------------------------
# Public API.
# ---------------------------------------------------------------------------


def collect_system_effects(
    system: 'StarSystem',
    empire_id: int,
    registries=None,
) -> List[Dict[str, Any]]:
    """Collect system-scope effects from sources in the system."""
    sources = iter_ability_sources_in_system(system, registries=registries)
    return _aggregate(
        sources, _SYSTEM_SCOPES, empire_id, registries,
        hex_coord=None, system=system,
    )


def collect_sector_effects(
    system: 'StarSystem',
    hex_coord,
    empire_id: int,
    registries=None,
) -> List[Dict[str, Any]]:
    """Collect sector-scope effects from sources at the given hex."""
    sources = iter_ability_sources_at_hex(
        system, hex_coord, registries=registries, include_system_sources=False,
    )
    return _aggregate(
        sources, _SECTOR_SCOPES, empire_id, registries,
        hex_coord=hex_coord, system=system,
    )


def find_sector_effect(
    effects: List[Dict[str, Any]],
    ability_name: str,
    **filters,
) -> Dict[str, Any] | None:
    """Find the first effect matching `ability_name` and any extra filters.

    Filters are matched against effect-dict keys (e.g. damage_type='radiation').
    """
    for e in effects:
        if e.get('ability_name') != ability_name:
            continue
        if all(e.get(k) == v for k, v in filters.items()):
            return e
    return None


def aggregate_value_or(
    effects: List[Dict[str, Any]],
    ability_name: str,
    default: float,
    **filters,
) -> float:
    """Read aggregate_value for an effect if present, else `default`."""
    e = find_sector_effect(effects, ability_name, **filters)
    return e['aggregate_value'] if e else default


# ---------------------------------------------------------------------------
# Internal aggregation pipeline.
# ---------------------------------------------------------------------------


def _build_provider(source, entry, ability_name, metadata, owner_id) -> Dict[str, Any]:
    """Build a single provider dict for one (source, ability_entry) pair.

    Reads activation state, computes is_active, extracts the value, and
    emits the PROJ-300 universal fields (``source_kind``, ``source_label``,
    ``source_id``, ``owner_id``).
    """
    state = None
    if _is_activatable(entry):
        state = source.get_activation_state(ability_name)
    status = _format_status(state)
    if _is_activatable(entry):
        is_active = state is not None and state.phase == ActivationPhase.ACTIVE
    else:
        is_active = True

    # Value driven by the registry's primary/fallback field selection.
    # Default depends on kind: 0.0 additive rate, 1.0 multiplicative multiplier.
    default = 0.0 if metadata.kind == 'rate' else 1.0
    value = float(entry.get(
        metadata.value_field_primary,
        entry.get(metadata.value_field_fallback, default),
    ))

    return {
        # Universal PROJ-300 fields.
        'source_kind': source.source_kind,
        'source_label': source.source_label,
        'source_id': source.source_id,
        'owner_id': owner_id,
        'status': status,
        'is_active': is_active,
        'value': value,
        'ability_data': entry,
    }


def _collect_providers(
    sources,
    allowed_scopes: frozenset,
    empire_id,
    *,
    hex_coord,
) -> Dict[str, dict]:
    """Walk every source, return `{group_key: group_dict}` keyed dict.

    Each group_dict carries `ability_name`, `display_name`, `resource_type`,
    `damage_type`, `kind`, and `providers` (list of provider dicts). The
    return shape is consumed downstream by `_aggregate_status`,
    `_aggregate_value`, and `_format_rows`.

    Per-source error tolerance: `affects_hex` and `get_abilities`
    exceptions are caught + logged so a malformed adapter cannot poison
    the pipeline.
    """
    raw_providers: Dict[str, dict] = {}

    for source in sources:
        # Owner filter: ownerless sources (storms, planets-themselves,
        # stars, warp points, system archetypes) apply to ALL empires;
        # owned sources only contribute to a query for their own owner_id.
        owner_id = getattr(source, 'owner_id', None)
        if owner_id is not None and empire_id is not None and owner_id != empire_id:
            continue

        # Hex affinity check (if querying a specific hex). Storms enforce
        # this via `affects_hex`; facilities are pre-filtered by the
        # iterator. This is mostly a safety net for adapter implementations.
        if hex_coord is not None:
            try:
                if not source.affects_hex(hex_coord):
                    continue
            except Exception:  # Intentional broad catch: source-impl errors must not poison the pipeline
                logger.warning(
                    "ability_source affects_hex raised — skipping source", exc_info=True,
                )
                continue

        try:
            abilities = source.get_abilities()
        except Exception:  # Intentional broad catch: same as above
            logger.warning(
                "ability_source get_abilities raised — skipping source", exc_info=True,
            )
            continue

        for ability_name, ability_data in abilities.items():
            metadata = find_metadata(ability_name)
            if metadata is None:
                continue
            entries = ability_data if isinstance(ability_data, list) else [ability_data]
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                entry_scope = entry.get('scope', 'self')
                if entry_scope not in allowed_scopes:
                    continue

                # PROJ-300 D17: ownerless sources may only declare
                # ownership-neutral scopes. "enemy_sector" on a storm is
                # undefined ("enemy of whom?"). Skip + log; don't crash.
                if owner_id is None and entry_scope in metadata.owner_aware_scopes:
                    logger.warning(
                        "PROJ-300 D17 violation: ownerless %s '%s' declares "
                        "scope=%s on ability '%s'. Skipping. Use 'sector' or "
                        "'system' for ownerless sources.",
                        getattr(source, 'source_kind', '?'),
                        getattr(source, 'source_id', '?'),
                        entry_scope,
                        ability_name,
                    )
                    continue

                group_key = make_group_key(ability_name, entry)
                provider = _build_provider(
                    source, entry, ability_name, metadata, owner_id,
                )

                if group_key not in raw_providers:
                    raw_providers[group_key] = {
                        'ability_name': ability_name,
                        'display_name': make_display_name(ability_name, entry),
                        'resource_type': entry.get('resource_type'),
                        'damage_type': entry.get('damage_type'),
                        'kind': metadata.kind,
                        'providers': [],
                    }
                raw_providers[group_key]['providers'].append(provider)

    return raw_providers


def _aggregate_status(providers: List[Dict[str, Any]]) -> str:
    """Roll a list of provider statuses into a single group status.

    Precedence: any ACTIVE → "Active"; else any ACTIVATING → first
    activating provider's status string; else any DEACTIVATING →
    "Deactivating"; else "Inactive".
    """
    if any(p['is_active'] for p in providers):
        return "Active"
    if any('Activating' in p['status'] for p in providers):
        for p in providers:
            if 'Activating' in p['status']:
                return p['status']
        return "Activating"
    if any('Deactivating' in p['status'] for p in providers):
        return "Deactivating"
    return "Inactive"


def _aggregate_value(
    providers: List[Dict[str, Any]],
    kind: str,
    group_key: str,
) -> float:
    """Aggregate the per-source values for a group.

    Active providers contribute when any exist; otherwise all providers'
    would-be values contribute (matches pre-PROJ-300 behavior). PROJ-300
    D16 mixed-kind entries (rate-shaped entry in a multiplier group, or
    vice versa) are skipped + logged so a malformed registry entry can't
    crash the panel.
    """
    active_entries = [p['ability_data'] for p in providers if p['is_active']]
    entries_for_agg = active_entries if active_entries else [
        p['ability_data'] for p in providers
    ]

    # PROJ-300 D16: mixed-kind validation.
    clean_entries = []
    for entry in entries_for_agg:
        entry_has_rate = isinstance(entry, dict) and 'rate' in entry
        entry_has_mult = isinstance(entry, dict) and 'multiplier' in entry
        if kind == 'rate' and entry_has_mult and not entry_has_rate:
            logger.warning(
                "PROJ-300 D16: mixed-kind in group '%s' — multiplier-style "
                "entry in rate-grouped ability. Skipping entry.",
                group_key,
            )
            continue
        if kind == 'multiplier' and entry_has_rate and not entry_has_mult:
            logger.warning(
                "PROJ-300 D16: mixed-kind in group '%s' — rate-style "
                "entry in multiplier-grouped ability. Skipping entry.",
                group_key,
            )
            continue
        clean_entries.append(entry)

    if kind == 'rate':
        # Adapt entry shape for aggregator: rate field maps to 'rate'.
        agg_entries = [
            {'rate': e.get('rate', e.get('improvement_rate', 0.0)),
             'stack_group': e.get('stack_group')}
            for e in clean_entries
        ]
        return aggregate_rates(agg_entries)
    return aggregate_multipliers(clean_entries)


def _format_rows(
    raw_providers: Dict[str, dict],
    status_per_group: Dict[str, str],
    value_per_group: Dict[str, float],
) -> List[Dict[str, Any]]:
    """Build the public effect-row return shape from intermediate state."""
    return [
        {
            'ability_name': group_data['ability_name'],
            'display_name': group_data['display_name'],
            'group_key': group_key,
            'status': status_per_group[group_key],
            'resource_type': group_data['resource_type'],
            'damage_type': group_data['damage_type'],
            'kind': group_data['kind'],
            'aggregate_value': value_per_group[group_key],
            'providers': group_data['providers'],
        }
        for group_key, group_data in raw_providers.items()
    ]


def _aggregate(
    sources,
    allowed_scopes: frozenset,
    empire_id,
    registries,
    *,
    hex_coord,
    system,
) -> List[Dict[str, Any]]:
    """Walk every source, build per-group provider dicts, aggregate per kind.

    Thin orchestrator over the four extracted helpers
    (`_collect_providers`, `_aggregate_status`, `_aggregate_value`,
    `_format_rows`). The `registries` and `system` parameters are unused
    here but retained for signature compatibility — collectors at the
    public boundary still pass them.
    """
    raw_providers = _collect_providers(
        sources, allowed_scopes, empire_id, hex_coord=hex_coord,
    )
    status_per_group = {
        k: _aggregate_status(v['providers']) for k, v in raw_providers.items()
    }
    value_per_group = {
        k: _aggregate_value(v['providers'], v['kind'], k)
        for k, v in raw_providers.items()
    }
    return _format_rows(raw_providers, status_per_group, value_per_group)


