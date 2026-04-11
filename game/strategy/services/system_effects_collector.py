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

# Abilities we consider "system effects" — must have scope == "system"
# Maps ability_name -> display_name
# Scopes considered relevant for the system effects display panel.
# Includes all system-level and sector-level scopes (anything that affects
# more than just the owning entity).
_SYSTEM_RELEVANT_SCOPES = frozenset({
    'system', 'allied_system', 'player_system', 'enemy_system',
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
    """Collect all system-scope effects from empire colonies in the system.

    Returns a list of effect dicts, each representing a grouped ability type.
    Effects are grouped by ability_name (+ resource_type for parameterized abilities).

    Args:
        system: StarSystem to scan.
        empire_id: Empire ID to filter colonies by ownership.
        registries: Optional GameRegistries for component lookup.

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
    # Collect raw provider entries
    raw_providers: Dict[str, list] = {}  # group_key -> list of provider dicts

    for planet in system.planets:
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

                    # Handle list format (QualityImprovement has array of entries)
                    entries = ability_data if isinstance(ability_data, list) else [ability_data]

                    for entry in entries:
                        if not isinstance(entry, dict):
                            continue

                        # Filter to system/sector-level scopes (any scope that affects
                        # a meaningful area around the planet, not just self/fleet)
                        entry_scope = entry.get('scope', 'self')
                        if entry_scope not in _SYSTEM_RELEVANT_SCOPES:
                            continue

                        group_key = _make_group_key(ability_name, entry)
                        display_name = _make_display_name(ability_name, entry)

                        # Determine status
                        if _is_activatable(entry):
                            status = _get_component_status(facility, comp_key)
                            is_active = _is_active_component(facility, comp_key, entry)
                        else:
                            status = "Active"
                            is_active = True

                        # Extract value (multiplier or rate)
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

        # Aggregate status: Active if any provider is active
        any_active = any(p['is_active'] for p in providers)
        any_activating = any('Activating' in p['status'] for p in providers)
        any_deactivating = any('Deactivating' in p['status'] for p in providers)

        if any_active:
            aggregate_status = "Active"
        elif any_activating:
            # Show first activating status with counter
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

        # Aggregate value using two-phase stacking
        active_entries = [p['ability_data'] for p in providers if p['is_active']]
        if active_entries:
            aggregate_value = aggregate_multipliers(active_entries)
        else:
            # Show what the value would be if activated
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
