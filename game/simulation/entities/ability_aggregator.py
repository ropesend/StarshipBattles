"""Ability aggregation utilities for ship components.

This module provides functions for calculating total ability values
across ship components, supporting stacking groups and redundancy.
"""


# Abilities that should multiply instead of sum
MULTIPLICATIVE_ABILITIES = {'ToHitAttackModifier', 'ToHitDefenseModifier'}

# Marker abilities that use boolean True semantics
MARKER_ABILITIES = {'CommandAndControl', 'Armor', 'RequiresCommandAndControl', 'RequiresCombatMovement'}


def calculate_ability_totals(components):
    """Calculate total values for all abilities from components.

    Supports 'stack_group' in ability definition for redundancy (MAX) vs stacking (SUM/MULT).

    Args:
        components: List of components to aggregate abilities from

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

        if hasattr(comp, 'ability_instances'):
            # Handle List (Current Implementation)
            if isinstance(comp.ability_instances, list):
                for ab in comp.ability_instances:
                    ability_name = ab.__class__.__name__
                    handled_abilities.add(ability_name)

                    # Extract value using polymorphic interface
                    value = ab.get_primary_value()

                    # Marker abilities (no numeric value) return 0.0 from get_primary_value()
                    # For class requirements, these need boolean True semantics
                    if ability_name in MARKER_ABILITIES:
                        value = True

                    stack_group = getattr(ab, 'stack_group', None)
                    group_key = stack_group if stack_group else comp

                    if ability_name not in ability_groups:
                        ability_groups[ability_name] = {}
                    if group_key not in ability_groups[ability_name]:
                        ability_groups[ability_name][group_key] = []

                    ability_groups[ability_name][group_key].append(value)

                    # Fix for BUG-08: Alias ResourceStorage(fuel) to FuelStorage for ClassRequirementsRule
                    if ability_name == 'ResourceStorage' and getattr(ab, 'resource_type', '') == 'fuel':
                        alias = 'FuelStorage'
                        if alias not in ability_groups:
                            ability_groups[alias] = {}
                        if group_key not in ability_groups[alias]:
                            ability_groups[alias][group_key] = []
                        ability_groups[alias][group_key].append(value)

            # Handle Dict
            elif isinstance(comp.ability_instances, dict):
                # ... (omitted for brevity, assume debug print sufficient in list block)
                pass

        # 2. Process Raw Dictionary
        abilities = getattr(comp, 'abilities', {})
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

    # Aggregate
    for ability_name, groups in ability_groups.items():
        # 1. Intra-Group Aggregation (MAX / Redundancy)
        # All items in a Named Group provide redundancy -> Take MAX
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
