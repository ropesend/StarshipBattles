"""Ability aggregation utilities for ship components.

This module provides functions for calculating total ability values
across ship components, supporting stacking groups and redundancy.

PROJ-190: Updated to use IAbility and IComponent protocols.
"""

from typing import Dict, Any, List, Optional, Iterator, Tuple

from game.simulation.components.abilities.base import AbilityLayer, AbilityScope
from game.simulation.interfaces import IAbility, is_ability


# Abilities that should multiply instead of sum
MULTIPLICATIVE_ABILITIES = {'ToHitAttackModifier', 'ToHitDefenseModifier'}

# Marker abilities that use boolean True semantics
MARKER_ABILITIES = {'CommandAndControl', 'Armor', 'RequiresCommandAndControl', 'RequiresCombatMovement'}


def _aggregate_ability_groups(ability_groups: Dict[str, Dict[Any, List[Any]]]) -> Dict[str, Any]:
    """Aggregate ability values from grouped data structure.

    Two-phase aggregation:
    1. Intra-group: Take MAX within each named group (redundancy)
    2. Inter-group: Sum across different groups (or multiply for special abilities)

    Args:
        ability_groups: Dict mapping ability_name -> {group_key -> [values]}

    Returns:
        Dict mapping ability names to their aggregated totals
    """
    totals = {}

    for ability_name, groups in ability_groups.items():
        # 1. Intra-Group Aggregation (MAX / Redundancy)
        group_contributions = []

        for key, values in groups.items():
            # Filter for numeric
            nums = [v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
            if nums:
                group_contributions.append(max(nums))
            elif any(v is True for v in values):
                # Boolean support (if any is True, the group is True)
                group_contributions.append(True)

        if not group_contributions:
            continue

        # 2. Inter-Group Aggregation (Sum or Multiply)
        first = group_contributions[0]

        if isinstance(first, bool):
            # If any group contributes True, result is True
            totals[ability_name] = True
        else:
            if ability_name in MULTIPLICATIVE_ABILITIES:
                val = 1.0
                for v in group_contributions:
                    if isinstance(v, (int, float)):
                        val *= v
                totals[ability_name] = val
            else:
                val = sum(v for v in group_contributions if isinstance(v, (int, float)))
                totals[ability_name] = val

    return totals


def calculate_ability_totals(
    components,
    layer: Optional[AbilityLayer] = None,
    scope_filter: Optional[AbilityScope] = None
):
    """Calculate total values for all abilities from components.

    Supports 'stack_group' in ability definition for redundancy (MAX) vs stacking (SUM/MULT).
    Optionally filters abilities by layer and/or scope.

    Args:
        components: List of components to aggregate abilities from
        layer: Optional layer to filter by (COMBAT, STRATEGIC, or BOTH).
               When specified, only processes ability instances (not raw dicts)
               and only includes abilities that apply to the requested layer.
        scope_filter: Optional scope to filter by (e.g., only ALLIED_SYSTEM abilities).
                      Only effective when layer is also specified.

    Returns:
        Dict mapping ability names to their total values
    """
    totals = {}

    # Intermediate structure: ability -> { group_key -> [values] }
    ability_groups = {}

    for comp in components:
        # 1. Process Ability Instances (New System - Scaled Values)
        # Track which abilities are handled to avoid double counting from dict
        handled_abilities = set()

        # IComponent protocol guarantees ability_instances exists
        for ab in comp.ability_instances:
            # Layer filtering (when layer is specified)
            if layer is not None:
                if not ab.applies_to_layer(layer):
                    continue
                # Scope filtering (only when layer is specified)
                if scope_filter is not None and ab.scope != scope_filter:
                    continue

            ability_name = ab.__class__.__name__
            handled_abilities.add(ability_name)

            # Extract value using polymorphic interface
            value = ab.get_primary_value()

            # Marker abilities (no numeric value) return 0.0 from get_primary_value()
            # For class requirements, these need boolean True semantics
            if ability_name in MARKER_ABILITIES:
                value = True

            # IAbility protocol guarantees stack_group exists
            stack_group = ab.stack_group
            group_key = stack_group if stack_group else comp

            if ability_name not in ability_groups:
                ability_groups[ability_name] = {}
            if group_key not in ability_groups[ability_name]:
                ability_groups[ability_name][group_key] = []

            ability_groups[ability_name][group_key].append(value)

        # 2. Process Raw Dictionary (skipped when layer filtering is active)
        # Layer filtering requires ability instances with applies_to_layer() method
        if layer is not None:
            continue

        # IComponent protocol guarantees abilities exists
        abilities = comp.abilities
        if isinstance(abilities, dict):
            for ability_name, raw_value in abilities.items():
                # Check handled
                if ability_name in handled_abilities:
                    continue

                # Parse Value & Group
                value = raw_value
                stack_group = None

                if isinstance(raw_value, dict) and 'value' in raw_value:
                    value = raw_value['value']
                    stack_group = raw_value.get('stack_group')

                # Determine Group Key
                group_key = stack_group if stack_group else comp

                if ability_name not in ability_groups:
                    ability_groups[ability_name] = {}
                if group_key not in ability_groups[ability_name]:
                    ability_groups[ability_name][group_key] = []

                ability_groups[ability_name][group_key].append(value)

    # Use shared aggregation helper
    return _aggregate_ability_groups(ability_groups)


def get_ability_total(components, ability_name):
    """Calculate total value of a specific ability across provided components.

    Args:
        components: List of components to check
        ability_name: Name of the ability to total

    Returns:
        Total value for the ability, or 0 if not found
    """
    totals = calculate_ability_totals(components)
    return totals.get(ability_name, 0)


def get_ability_instances_by_class(
    components,
    class_name: str
) -> Iterator[Tuple[Any, Any]]:
    """Yield (component, ability) pairs for abilities matching class_name.

    This utility extracts ability instances that match a specific class name
    from a list of components. It enables filtering abilities by type without
    duplicating the iteration pattern across multiple files.

    Args:
        components: List of components to search
        class_name: The ability class name to filter for (e.g., 'ResourceConsumption')

    Yields:
        Tuples of (component, ability_instance) for each matching ability

    Example:
        for comp, ability in get_ability_instances_by_class(components, 'ResourceConsumption'):
            resource_type = ability.resource_type
            rate = ability.get_primary_value()
            # Process the ability...
    """
    for comp in components:
        # IComponent protocol guarantees ability_instances exists
        for ab in comp.ability_instances:
            if ab.__class__.__name__ == class_name:
                yield comp, ab


