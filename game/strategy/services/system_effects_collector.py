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

Each provider carries both the universal PROJ-300 fields (source_kind,
source_label, source_id, owner_id) AND legacy back-compat fields
(planet_name, planet_id, facility_name, facility_id, component_key) so
existing consumers keep working until Phase 8 retires them.
"""
import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from game.strategy.data.component_activation_state import (
    ActivationPhase,
    ComponentActivationState,
)
from game.strategy.services.strategic_ability_scanner import (
    aggregate_multipliers,
    aggregate_rates,
)
from game.strategy.services.ability_iterator import (
    iter_ability_sources_at_hex,
    iter_ability_sources_in_system,
)

if TYPE_CHECKING:
    from game.strategy.data.galaxy import StarSystem

logger = logging.getLogger(__name__)


# Scope sets for filtering effects into the correct UI panel.
# System = all hexes in a star system (radius 50, diameter 101).
# Sector = a single hex on the galaxy map.
_SYSTEM_SCOPES = frozenset({
    'system', 'allied_system', 'player_system', 'enemy_system',
})

_SECTOR_SCOPES = frozenset({
    'sector', 'allied_sector', 'player_sector', 'enemy_sector',
})


SYSTEM_EFFECT_ABILITIES = {
    'GeologicStabilizer': 'Geologic Stabilizer',
    'StellarStabilizer': 'Stellar Stabilizer',
    'WarpFieldStabilizer': 'Warp Field Stabilizer',
    'ResourceHarvestBooster': None,  # Display name derived from resource_type
    'BuildRateBooster': 'Construction Acceleration',
    'QualityImprovement': 'Quality Enrichment',
    'ShieldModifier': 'Shield Modifier',
    'DamageModifier': 'Damage Modifier',
    # PROJ-300 — storm/environmental abilities (formerly StormEffect fields).
    'ThrustModifier': 'Thrust Modifier',
    'StrategicSpeedModifier': 'Strategic Speed Modifier',
    'EnvironmentalDamage': None,  # Display name derived from damage_type
    'FuelDrain': 'Fuel Drain',
}


# Rate-style abilities (read aggregate_value as additive). Multiplier-style
# is the default and reads aggregate_value as multiplicative-with-1.0-default.
_RATE_ABILITIES = frozenset({'EnvironmentalDamage', 'FuelDrain'})


# PROJ-300 D17: ownership-aware scopes can only be declared by sources with
# an owner_id ("enemy of whom?" is undefined for ownerless sources).
_OWNER_AWARE_SCOPES = frozenset({
    'allied_sector', 'enemy_sector', 'player_sector',
    'allied_system', 'enemy_system', 'player_system',
    'allied_empire',
})


def _ability_kind(ability_name: str) -> str:
    return 'rate' if ability_name in _RATE_ABILITIES else 'multiplier'


# ---------------------------------------------------------------------------
# Status helpers (unchanged from the pre-PROJ-300 collector). These work on
# any object exposing `get_activation_state(comp_key) -> ComponentActivationState`.
# ---------------------------------------------------------------------------


def _format_status(state: Optional[ComponentActivationState]) -> str:
    """Render an activation state as a human-readable status string."""
    if state is None:
        return "Active"  # Sources without activation tracking are always-on.
    if state.phase == ActivationPhase.ACTIVE:
        return "Active"
    if state.phase == ActivationPhase.ACTIVATING:
        remaining = state.required_ticks - state.progress_ticks
        return f"Activating ({remaining})"
    if state.phase == ActivationPhase.DEACTIVATING:
        remaining = state.required_ticks - state.progress_ticks
        return f"Deactivating ({remaining})"
    return "Inactive"


def _is_activatable(ability_data: dict) -> bool:
    """Activatable abilities have an `activation_time` field."""
    return isinstance(ability_data, dict) and 'activation_time' in ability_data


# ---------------------------------------------------------------------------
# Grouping + display name (unchanged).
# ---------------------------------------------------------------------------


def make_group_key(ability_name: str, ability_data) -> str:
    """Group key for an ability instance.

    ResourceHarvestBooster + QualityImprovement: per resource_type.
    EnvironmentalDamage: per damage_type (PROJ-300).
    Other abilities: by ability_name alone.

    Public since FEAT-16 — also consumed by the Planet List effects filter
    and per-effect column generators.
    """
    if ability_name == 'ResourceHarvestBooster' and isinstance(ability_data, dict):
        resource = ability_data.get('resource_type', '')
        return f"{ability_name}:{resource}"
    if ability_name == 'QualityImprovement' and isinstance(ability_data, dict):
        resource = ability_data.get('resource_type', '')
        if resource:
            return f"{ability_name}:{resource}"
    if ability_name == 'EnvironmentalDamage' and isinstance(ability_data, dict):
        damage_type = ability_data.get('damage_type', 'environmental')
        return f"{ability_name}:{damage_type}"
    return ability_name


def make_display_name(ability_name: str, ability_data) -> str:
    """Human-readable label for an ability instance.

    Public since FEAT-16 — used as Planet List per-effect column titles and
    Effects filter chip labels.
    """
    if ability_name == 'ResourceHarvestBooster' and isinstance(ability_data, dict):
        resource = ability_data.get('resource_type', 'unknown')
        return f"{resource.capitalize()} Harvest Boost"
    if ability_name == 'EnvironmentalDamage' and isinstance(ability_data, dict):
        damage_type = ability_data.get('damage_type', 'environmental')
        return f"{damage_type.capitalize()} Damage"
    display = SYSTEM_EFFECT_ABILITIES.get(ability_name)
    if display:
        return display
    return ability_name


def format_intrinsic_ability_magnitude(ability_name: str, ability_data) -> str:
    """Render the magnitude of a single ability instance for UI display.

    Used by the Planet List per-effect columns (FEAT-16) and by the System
    Tree panel's per-effect rendering. The aggregate-effect formatter in
    `system_tree_panel._format_effect_value` delegates to this for the
    shared multiplier/rate paths.

    Returns "" when the value is the additive/multiplicative identity (so
    cells stay blank rather than rendering noise like "x1.00").
    """
    if not isinstance(ability_data, dict):
        return ""

    if ability_name in _RATE_ABILITIES:
        rate = ability_data.get('rate')
        if not rate:
            return ""
        try:
            r = float(rate)
        except (TypeError, ValueError):
            return ""
        if ability_name == 'EnvironmentalDamage':
            return f"-{r:.2f} hull/turn"
        if ability_name == 'FuelDrain':
            return f"-{r:.2f} fuel/turn"
        return f"{r:+.2f}/turn"

    # Multiplier-style. Gate on SYSTEM_EFFECT_ABILITIES so unknown names
    # (no registry entry, no rate kind) fall through to the empty string
    # rather than fabricating "x..." for arbitrary input.
    if ability_name not in SYSTEM_EFFECT_ABILITIES:
        return ""
    mult = ability_data.get('multiplier')
    if mult is None:
        return ""
    try:
        m = float(mult)
    except (TypeError, ValueError):
        return ""
    if m == 1.0:
        return ""
    return f"x{m:.2f}"


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
) -> Optional[Dict[str, Any]]:
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


def _aggregate(
    sources,
    allowed_scopes: frozenset,
    empire_id,
    registries,
    *,
    hex_coord,
    system,
) -> List[Dict[str, Any]]:
    """Walk every source, build per-group provider dicts, aggregate per kind."""
    raw_providers: Dict[str, dict] = {}

    for source in sources:
        # Owner filter: ownerless sources (storms, planets-themselves, stars,
        # warp points, system archetypes) apply to ALL empires; owned sources
        # only contribute to a query for their own owner_id.
        owner_id = getattr(source, 'owner_id', None)
        if owner_id is not None and empire_id is not None and owner_id != empire_id:
            continue

        # Hex affinity check (if querying a specific hex). Storms enforce this
        # via `affects_hex`; the iterator pre-filters facilities by-planet-at-hex,
        # so this is mostly a safety net for adapter implementations.
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
            if ability_name not in SYSTEM_EFFECT_ABILITIES:
                continue
            entries = ability_data if isinstance(ability_data, list) else [ability_data]
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                entry_scope = entry.get('scope', 'self')
                if entry_scope not in allowed_scopes:
                    continue

                # PROJ-300 D17: ownerless sources may only declare ownership-
                # neutral scopes. "enemy_sector" on a storm is undefined
                # ("enemy of whom?"). Skip + log; do not crash the collector.
                if owner_id is None and entry_scope in _OWNER_AWARE_SCOPES:
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
                display_name = make_display_name(ability_name, entry)

                # Activation state — None means always-on (storms, planets,
                # stars, etc.). Activatable abilities on facilities have a
                # state from their owning facility.
                state = None
                if _is_activatable(entry):
                    state = source.get_activation_state(ability_name)
                status = _format_status(state)
                if _is_activatable(entry):
                    is_active = state is not None and state.phase == ActivationPhase.ACTIVE
                else:
                    is_active = True

                # Value pulled from the entry per its kind.
                if ability_name in _RATE_ABILITIES:
                    value = float(entry.get('rate', entry.get('improvement_rate', 0.0)))
                else:
                    value = float(entry.get('multiplier', entry.get('improvement_rate', 1.0)))

                provider = {
                    # Universal PROJ-300 fields.
                    'source_kind': source.source_kind,
                    'source_label': source.source_label,
                    'source_id': source.source_id,
                    'owner_id': owner_id,
                    'status': status,
                    'is_active': is_active,
                    'value': value,
                    'ability_data': entry,
                    # Legacy back-compat fields — populated for facility sources
                    # so existing UI consumers keep working until Phase 8.
                    **_legacy_provider_fields(source),
                }

                if group_key not in raw_providers:
                    raw_providers[group_key] = {
                        'ability_name': ability_name,
                        'display_name': display_name,
                        'resource_type': entry.get('resource_type'),
                        'damage_type': entry.get('damage_type'),
                        'kind': _ability_kind(ability_name),
                        'providers': [],
                    }
                raw_providers[group_key]['providers'].append(provider)

    # Build aggregated effect rows.
    results: List[Dict[str, Any]] = []
    for group_key, group_data in raw_providers.items():
        providers = group_data['providers']

        any_active = any(p['is_active'] for p in providers)
        any_activating = any('Activating' in p['status'] for p in providers)
        any_deactivating = any('Deactivating' in p['status'] for p in providers)

        if any_active:
            aggregate_status = "Active"
        elif any_activating:
            for p in providers:
                if 'Activating' in p['status']:
                    aggregate_status = p['status']
                    break
            else:
                aggregate_status = "Activating"
        elif any_deactivating:
            aggregate_status = "Deactivating"
        else:
            aggregate_status = "Inactive"

        # Aggregate from active providers if any are active; otherwise show
        # the would-be value across all providers (matches pre-PROJ-300
        # behavior where inactive providers still rendered a stack value).
        active_entries = [p['ability_data'] for p in providers if p['is_active']]
        entries_for_agg = active_entries if active_entries else [p['ability_data'] for p in providers]

        kind = group_data['kind']
        # PROJ-300 D16: mixed-kind validation. A group declared as multiplier
        # but containing rate-style entries (or vice versa) is a registry
        # smell — skip the offender and log so the issue is debuggable
        # without crashing the panel.
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
        entries_for_agg = clean_entries

        if kind == 'rate':
            # Adapt entry shape for aggregator: rate field maps to 'rate'.
            agg_entries = [
                {'rate': e.get('rate', e.get('improvement_rate', 0.0)),
                 'stack_group': e.get('stack_group')}
                for e in entries_for_agg
            ]
            aggregate_value = aggregate_rates(agg_entries)
        else:
            aggregate_value = aggregate_multipliers(entries_for_agg)

        results.append({
            'ability_name': group_data['ability_name'],
            'display_name': group_data['display_name'],
            'group_key': group_key,
            'status': aggregate_status,
            'resource_type': group_data['resource_type'],
            'damage_type': group_data['damage_type'],
            'kind': kind,
            'aggregate_value': aggregate_value,
            'providers': providers,
        })

    return results


def _legacy_provider_fields(source) -> Dict[str, Any]:
    """Build legacy provider fields (`planet_name`, `facility_name`, etc.).

    Populated for facility sources so existing UI/tests keep working. For
    other source kinds (storms, future PROJ-301..305), these fields default
    to None / the source label. Phase 8 will retire the legacy fields.
    """
    if getattr(source, 'source_kind', None) != 'facility':
        # Best-effort fill for non-facility sources so renderers that always
        # read legacy fields don't crash.
        label = getattr(source, 'source_label', '')
        return {
            'planet_name': None,
            'planet_id': None,
            'facility_name': label,
            'facility_id': getattr(source, 'source_id', None),
            'component_key': None,
        }

    facility = getattr(source, 'facility', None)
    planet = getattr(source, 'planet', None)
    return {
        'planet_name': getattr(planet, 'name', None),
        'planet_id': getattr(planet, 'id', None),
        'facility_name': getattr(facility, 'name', None),
        'facility_id': getattr(facility, 'instance_id', None),
        'component_key': None,  # Adapter no longer tracks per-component key.
    }
