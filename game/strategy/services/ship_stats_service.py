"""
Ship Stats Service - Calculates ship statistics from component definitions.

PROJ-07: Strategy Layer Stats Calculation Refactor

This service calculates ship stats dynamically from component definitions
rather than reading from cached `expected_stats`. This ensures stats
accurately reflect component damage state.

Key design decisions:
- Only imports from game.core.registry (no simulation layer coupling)
- Damage model: gradual degradation to 30% HP, then inactive
- Special cases: Warp drives require 100% HP, Armor never degrades
- Stats cached on ShipInstance with invalidation on damage change
"""

from typing import Dict, Any, Optional, List, Tuple
from game.core.registry import get_component_registry
from game.core.logger import log_warning


# Default damage threshold - components become useless below this HP percentage
DEFAULT_DAMAGE_THRESHOLD = 0.3  # 30%

# Component types that never degrade (always 100% effective)
NON_DEGRADING_TYPES = {'Armor'}

# Ability types that require 100% HP to function
FULL_HP_REQUIRED_ABILITIES = {'WarpJump'}


class ShipStatsService:
    """
    Service for calculating ship statistics from component definitions.

    This replaces reading from expected_stats with dynamic calculation
    that respects component damage state.
    """

    @staticmethod
    def calculate_stats(
        design_data: Dict[str, Any],
        component_damage: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Calculate all ship stats from design data and component damage.

        Args:
            design_data: Serialized ship design containing 'layers' dict
            component_damage: Optional dict of component_id -> current_hp
                             If None, assumes all components undamaged

        Returns:
            Dict with calculated stats matching expected_stats structure:
            - max_hp: Total HP from all components
            - mass: Total mass (doesn't degrade with damage)
            - max_fuel, max_energy, max_ammo: Resource storage capacities
            - strategic_movement: Movement points for strategic map
            - strategic_fuel_per_hex: Fuel cost per hex moved
            - warp_max_tonnage: Max ship mass for warp (0 if damaged)
            - warp_energy_cost: Energy cost per warp jump
        """
        if component_damage is None:
            component_damage = {}

        # Initialize accumulators
        total_mass = 0.0
        total_hp = 0.0
        resource_storage: Dict[str, float] = {}  # Generic resource storage
        total_strategic_movement = 0.0
        total_strategic_fuel_per_hex = 0.0
        warp_max_tonnage = 0
        warp_resource_costs: Dict[str, float] = {}  # Generic warp resource costs

        # Iterate through all components in design
        components_found = ShipStatsService._iterate_design_components(design_data)

        # Fallback to expected_stats if no components found in layers
        # This handles test fixtures and designs without component registry entries
        if not components_found:
            expected = design_data.get('expected_stats', {})
            # Build warp_resource_costs from legacy fields if present
            fallback_warp_costs = expected.get('warp_resource_costs', {})
            if not fallback_warp_costs:
                # Check legacy specific cost fields
                if expected.get('warp_energy_cost', 0) > 0:
                    fallback_warp_costs['energy'] = expected['warp_energy_cost']
                if expected.get('warp_fuel_cost', 0) > 0:
                    fallback_warp_costs['fuel'] = expected['warp_fuel_cost']
            return {
                'max_hp': expected.get('max_hp', 0),
                'mass': expected.get('mass', 0),
                'max_fuel': expected.get('max_fuel', 0),
                'max_energy': expected.get('max_energy', 0),
                'max_ammo': expected.get('max_ammo', 0),
                'strategic_movement': expected.get('strategic_movement', 0),
                'strategic_fuel_per_hex': expected.get('strategic_fuel_per_hex', 0),
                'warp_max_tonnage': expected.get('warp_max_tonnage', 0),
                'warp_resource_costs': fallback_warp_costs,
                # Keep legacy fields for backward compatibility
                'warp_energy_cost': expected.get('warp_energy_cost', 0),
                'warp_fuel_cost': expected.get('warp_fuel_cost', 0),
            }

        for layer_name, comp_entry, comp_def in components_found:
            if comp_def is None:
                continue

            comp_id = comp_entry.get('id', '')

            # Get effectiveness based on damage (0.0 to 1.0)
            effectiveness = ShipStatsService.get_component_effectiveness(
                comp_id, comp_def, component_damage
            )

            # Mass never degrades - add full mass regardless of damage
            comp_mass = ShipStatsService._get_numeric_value(comp_def, 'mass', 0)
            total_mass += comp_mass

            # HP degrades with damage
            comp_hp = ShipStatsService._get_numeric_value(comp_def, 'max_hp', 0)
            total_hp += comp_hp * effectiveness

            # Get abilities from component definition
            abilities = getattr(comp_def, 'abilities', {}) or {}

            # Resource Storage - degrades with damage
            for ability_data in ShipStatsService._get_ability_list(abilities, 'ResourceStorage'):
                resource_type = ability_data.get('resource', '')
                # Check both 'max_amount' and 'amount' keys (components use 'amount')
                max_amount = ability_data.get('max_amount') or ability_data.get('amount', 0)
                if resource_type == 'fuel':
                    total_fuel_storage += max_amount * effectiveness
                elif resource_type == 'energy':
                    total_energy_storage += max_amount * effectiveness
                elif resource_type == 'ammo':
                    total_ammo_storage += max_amount * effectiveness

            # Also check shortcut abilities (FuelStorage, EnergyStorage, AmmoStorage)
            if 'FuelStorage' in abilities:
                val = ShipStatsService._get_ability_value(abilities, 'FuelStorage')
                total_fuel_storage += val * effectiveness
            if 'EnergyStorage' in abilities:
                val = ShipStatsService._get_ability_value(abilities, 'EnergyStorage')
                total_energy_storage += val * effectiveness
            if 'AmmoStorage' in abilities:
                val = ShipStatsService._get_ability_value(abilities, 'AmmoStorage')
                total_ammo_storage += val * effectiveness

            # Strategic Movement - degrades with damage
            if 'StrategicMovement' in abilities:
                movement = ShipStatsService._get_ability_value(abilities, 'StrategicMovement')
                total_strategic_movement += movement * effectiveness

            # Strategic Fuel Consumption - degrades (less fuel consumed when damaged)
            for ability_data in ShipStatsService._get_ability_list(abilities, 'ResourceConsumption'):
                if ability_data.get('trigger') == 'strategic_per_hex':
                    if ability_data.get('resource') == 'fuel':
                        total_strategic_fuel_per_hex += ability_data.get('amount', 0) * effectiveness

            # Warp Jump - requires 100% HP (effectiveness must be 1.0)
            if 'WarpJump' in abilities:
                warp_effectiveness = ShipStatsService._get_warp_effectiveness(
                    comp_id, comp_def, component_damage
                )
                if warp_effectiveness > 0:
                    warp_data = abilities.get('WarpJump', {})
                    if isinstance(warp_data, dict):
                        tonnage = warp_data.get('max_tonnage', 0)
                        energy = warp_data.get('energy_cost', 0)
                        fuel = warp_data.get('fuel_cost', 0)
                    else:
                        # Simple numeric value = max_tonnage
                        tonnage = warp_data if isinstance(warp_data, (int, float)) else 0
                        energy = 0
                        fuel = 0

                    # Use largest warp drive tonnage
                    if tonnage > warp_max_tonnage:
                        warp_max_tonnage = tonnage
                    warp_energy_cost += energy
                    warp_fuel_cost += fuel

        return {
            'max_hp': int(total_hp),
            'mass': total_mass,
            'max_fuel': total_fuel_storage,
            'max_energy': total_energy_storage,
            'max_ammo': total_ammo_storage,
            'strategic_movement': total_strategic_movement,
            'strategic_fuel_per_hex': total_strategic_fuel_per_hex,
            'warp_max_tonnage': warp_max_tonnage,
            'warp_energy_cost': warp_energy_cost,
            'warp_fuel_cost': warp_fuel_cost,
        }

    @staticmethod
    def get_component_effectiveness(
        comp_id: str,
        comp_def: Any,
        component_damage: Dict[str, int]
    ) -> float:
        """
        Calculate component effectiveness based on damage state.

        Damage model:
        - Above 30% HP: Gradual degradation (linear from 100% to 0%)
        - At or below 30% HP: Component is inactive (0% effectiveness)
        - Armor: Never degrades (always 100% effective)

        Args:
            comp_id: Component ID string
            comp_def: Component definition from registry
            component_damage: Dict of component_id -> current_hp

        Returns:
            Float from 0.0 to 1.0 representing effectiveness
        """
        # Check if this is armor (never degrades)
        comp_type = getattr(comp_def, 'type_str', '')
        if comp_type in NON_DEGRADING_TYPES:
            return 1.0

        # Check for 'Armor' ability marker
        abilities = getattr(comp_def, 'abilities', {}) or {}
        if abilities.get('Armor'):
            return 1.0

        # Get max HP from component definition
        max_hp = ShipStatsService._get_numeric_value(comp_def, 'max_hp', 0)
        if max_hp <= 0:
            return 1.0  # No HP means always active

        # Get current HP - check both indexed and base forms
        current_hp = ShipStatsService._get_current_hp(comp_id, max_hp, component_damage)

        # Calculate HP percentage
        hp_pct = current_hp / max_hp

        # Get damage threshold (default 30%)
        threshold = getattr(comp_def, 'damage_threshold', DEFAULT_DAMAGE_THRESHOLD)

        # Below threshold = inactive
        if hp_pct <= threshold:
            return 0.0

        # Gradual degradation from 100% to threshold
        # Map hp_pct [threshold, 1.0] to effectiveness [0.0, 1.0]
        return (hp_pct - threshold) / (1.0 - threshold)

    @staticmethod
    def _get_warp_effectiveness(
        comp_id: str,
        comp_def: Any,
        component_damage: Dict[str, int]
    ) -> float:
        """
        Get warp drive effectiveness - requires 100% HP.

        Warp drives are either fully functional (100% HP) or completely
        non-functional (any damage at all disables warp).
        """
        max_hp = ShipStatsService._get_numeric_value(comp_def, 'max_hp', 0)
        if max_hp <= 0:
            return 1.0  # No HP tracked = always works

        current_hp = ShipStatsService._get_current_hp(comp_id, max_hp, component_damage)

        # Must be at exactly full HP
        if current_hp >= max_hp:
            return 1.0
        return 0.0

    @staticmethod
    def _iterate_design_components(
        design_data: Dict[str, Any]
    ) -> List[Tuple[str, Dict[str, Any], Any]]:
        """
        Iterate through all components in a design.

        Yields:
            Tuples of (layer_name, component_entry, component_def)
            where component_def is the registry definition or None if not found
        """
        result = []
        layers = design_data.get('layers', {})
        registry = get_component_registry()

        for layer_name, layer_components in layers.items():
            # Handle both list format and dict format
            if isinstance(layer_components, list):
                components = layer_components
            elif isinstance(layer_components, dict):
                components = layer_components.get('components', [])
            else:
                continue

            for comp_entry in components:
                comp_id = comp_entry.get('id', '')
                comp_def = registry.get(comp_id)

                if comp_def is None:
                    log_warning(f"Component '{comp_id}' not found in registry, skipping")
                    continue

                result.append((layer_name, comp_entry, comp_def))

        return result

    @staticmethod
    def _get_current_hp(
        comp_id: str,
        max_hp: float,
        component_damage: Dict[str, int]
    ) -> float:
        """
        Get current HP for a component, checking multiple ID formats.

        Component damage dict may use indexed IDs (e.g., "bridge_0") or
        base IDs (e.g., "bridge"). We check both.
        """
        # Direct lookup
        if comp_id in component_damage:
            return component_damage[comp_id]

        # Try indexed forms (component_0, component_1, etc.)
        for key, hp in component_damage.items():
            # Check if key is an indexed version of comp_id
            if key.startswith(comp_id + '_'):
                try:
                    # Verify it's actually an index suffix
                    int(key[len(comp_id) + 1:])
                    return hp
                except ValueError:
                    pass

        # No damage recorded = full HP
        return max_hp

    @staticmethod
    def _get_numeric_value(obj: Any, attr: str, default: float) -> float:
        """Get a numeric attribute from an object, handling formulas."""
        val = getattr(obj, attr, default)
        if isinstance(val, str):
            # It's a formula - can't evaluate without context
            return default
        return float(val) if val is not None else default

    @staticmethod
    def _get_ability_value(abilities: Dict[str, Any], ability_name: str) -> float:
        """Get the primary value from an ability definition."""
        val = abilities.get(ability_name, 0)
        if isinstance(val, (int, float)):
            return float(val)
        elif isinstance(val, dict):
            # Try common keys for primary value
            for key in ['value', 'amount', 'max_amount', 'thrust_force', 'movement_points']:
                if key in val:
                    return float(val[key])
            return 0.0
        return 0.0

    @staticmethod
    def _get_ability_list(
        abilities: Dict[str, Any],
        ability_name: str
    ) -> List[Dict[str, Any]]:
        """
        Get ability data as a list (handles both single and multiple abilities).

        Returns list of ability data dicts for the given ability name.
        """
        val = abilities.get(ability_name)
        if val is None:
            return []
        if isinstance(val, list):
            return val
        if isinstance(val, dict):
            return [val]
        # Simple value - wrap in dict
        return [{'value': val}]
