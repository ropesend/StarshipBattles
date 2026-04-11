"""System Effects Collector — aggregates system-scope abilities for UI display.

Scans all empire-owned colonies in a star system for system-scope abilities
(stabilizers, harvest boosters, build rate boosters, quality improvers) and
returns structured effect data grouped by ability type.

Each effect has:
- ability_name, display_name, status (Active/Inactive/Activating/Deactivating)
- providers: list of {planet_name, facility_name, component_key, status, value}
- aggregate_value: stacked value using two-phase aggregation (where applicable)
"""
import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from game.core.patterns.layer_iterator import iter_keyed_components
from game.strategy.services.component_inspector import extract_abilities_from_component
from game.strategy.data.component_activation_state import (
    ActivationPhase,
    ComponentActivationState,
)
from game.strategy.services.strategic_ability_scanner import aggregate_multipliers

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
}


def _get_component_status(facility, comp_key: str) -> str:
    """Get the activation status string for a component."""
    state = facility.get_activation_state(comp_key)
    if state.phase == ActivationPhase.ACTIVE:
        return "Active"
    elif state.phase == ActivationPhase.ACTIVATING:
        remaining = state.required_ticks - state.progress_ticks
        return f"Activating ({remaining})"
    elif state.phase == ActivationPhase.DEACTIVATING:
        remaining = state.required_ticks - state.progress_ticks
        return f"Deactivating ({remaining})"
    return "Inactive"


def _is_activatable(ability_data: dict) -> bool:
    """Check if an ability is activatable (has activation_time)."""
    return isinstance(ability_data, dict) and 'activation_time' in ability_data


def _is_active_component(facility, comp_key: str, ability_data: dict) -> bool:
    """Determine if a component is functionally providing its effect.

    Activatable abilities must be in ACTIVE phase.
    Passive abilities are always active when facility is operational.
    """
    if _is_activatable(ability_data):
        state = facility.get_activation_state(comp_key)
        return state.phase == ActivationPhase.ACTIVE
    return True  # Passive: always active when facility is operational


def _make_group_key(ability_name: str, ability_data) -> str:
    """Create a grouping key for an ability instance.

    ResourceHarvestBooster and QualityImprovement are grouped per resource_type.
    Other abilities are grouped by ability_name alone.
    """
    if ability_name == 'ResourceHarvestBooster' and isinstance(ability_data, dict):
        resource = ability_data.get('resource_type', '')
        return f"{ability_name}:{resource}"
    if ability_name == 'QualityImprovement' and isinstance(ability_data, dict):
        resource = ability_data.get('resource_type', '')
        if resource:
            return f"{ability_name}:{resource}"
    return ability_name


def _make_display_name(ability_name: str, ability_data) -> str:
    """Create a display name for an ability."""
    if ability_name == 'ResourceHarvestBooster' and isinstance(ability_data, dict):
        resource = ability_data.get('resource_type', 'unknown')
        return f"{resource.capitalize()} Harvest Boost"
    display = SYSTEM_EFFECT_ABILITIES.get(ability_name)
    if display:
        return display
    return ability_name


def collect_system_effects(
    system: 'StarSystem',
    empire_id: int,
    registries=None,
) -> List[Dict[str, Any]]:
    """Collect system-scope effects from empire colonies in the system.

    Only includes abilities with system-level scopes (system, allied_system,
    player_system, enemy_system). Sector-scoped abilities are excluded —
    use collect_sector_effects() for those.

    Args:
        system: StarSystem to scan.
        empire_id: Empire ID to filter colonies by ownership.
        registries: Optional GameRegistries for component lookup.

    Returns:
        List of effect dicts (see _collect_effects for structure).
    """
    return _collect_effects(list(system.planets), empire_id, registries, _SYSTEM_SCOPES)


def collect_sector_effects(
    system: 'StarSystem',
    hex_coord,
    empire_id: int,
    registries=None,
) -> List[Dict[str, Any]]:
    """Collect sector-scope effects from empire colonies at a specific hex.

    Only includes abilities with sector-level scopes (sector, allied_sector,
    player_sector, enemy_sector). System-scoped abilities are excluded —
    use collect_system_effects() for those.

    Args:
        system: StarSystem containing the hex.
        hex_coord: Global hex coordinate to filter planets by location.
        empire_id: Empire ID to filter colonies by ownership.
        registries: Optional GameRegistries for component lookup.

    Returns:
        List of effect dicts (see _collect_effects for structure).
    """
    # Find planets at this specific hex
    planets_at_hex = []
    global_loc = getattr(system, 'global_location', None)
    for planet in system.planets:
        if global_loc is not None:
            planet_global = global_loc + planet.location
            if planet_global == hex_coord:
                planets_at_hex.append(planet)
        else:
            planets_at_hex.append(planet)

    return _collect_effects(planets_at_hex, empire_id, registries, _SECTOR_SCOPES)


def _collect_effects(
    planets: List,
    empire_id: int,
    registries,
    allowed_scopes: frozenset,
) -> List[Dict[str, Any]]:
    """Shared logic: scan planets for abilities matching allowed_scopes.

    Returns a list of effect dicts, each representing a grouped ability type.
    Effects are grouped by ability_name (+ resource_type for parameterized abilities).

    Returns:
        List of effect dicts with keys:
        - ability_name: str
        - display_name: str
        - group_key: str (for dedup/grouping)
        - status: str ("Active"/"Inactive"/"Activating (N)"/"Deactivating (N)")
        - resource_type: Optional[str] (for parameterized abilities)
        - aggregate_value: float (stacked multiplier or rate, 0.0 if N/A)
        - providers: list of provider dicts
    """
    raw_providers: Dict[str, dict] = {}

    for planet in planets:
        if getattr(planet, 'owner_id', None) != empire_id:
            continue

        for facility in planet.facilities:
            if not getattr(facility, 'is_operational', True):
                continue

            for comp_key, layer_name, comp in iter_keyed_components(facility.design_data):
                abilities = extract_abilities_from_component(comp, registries)

                for ability_name in SYSTEM_EFFECT_ABILITIES:
                    ability_data = abilities.get(ability_name)
                    if ability_data is None:
                        continue

                    entries = ability_data if isinstance(ability_data, list) else [ability_data]

                    for entry in entries:
                        if not isinstance(entry, dict):
                            continue

                        entry_scope = entry.get('scope', 'self')
                        if entry_scope not in allowed_scopes:
                            continue

                        group_key = _make_group_key(ability_name, entry)
                        display_name = _make_display_name(ability_name, entry)

                        if _is_activatable(entry):
                            status = _get_component_status(facility, comp_key)
                            is_active = _is_active_component(facility, comp_key, entry)
                        else:
                            status = "Active"
                            is_active = True

                        value = entry.get('multiplier', entry.get('improvement_rate', 0.0))

                        provider = {
                            'planet_name': planet.name,
                            'planet_id': planet.id,
                            'facility_name': facility.name,
                            'facility_id': facility.instance_id,
                            'component_key': comp_key,
                            'status': status,
                            'is_active': is_active,
                            'value': value,
                            'ability_data': entry,
                        }

                        if group_key not in raw_providers:
                            raw_providers[group_key] = {
                                'ability_name': ability_name,
                                'display_name': display_name,
                                'resource_type': entry.get('resource_type'),
                                'providers': [],
                            }
                        raw_providers[group_key]['providers'].append(provider)

    # Build result with aggregate values and status
    results = []
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

        active_entries = [p['ability_data'] for p in providers if p['is_active']]
        if active_entries:
            aggregate_value = aggregate_multipliers(active_entries)
        else:
            aggregate_value = aggregate_multipliers([p['ability_data'] for p in providers])

        results.append({
            'ability_name': group_data['ability_name'],
            'display_name': group_data['display_name'],
            'group_key': group_key,
            'status': aggregate_status,
            'resource_type': group_data['resource_type'],
            'aggregate_value': aggregate_value,
            'providers': providers,
        })

    return results
