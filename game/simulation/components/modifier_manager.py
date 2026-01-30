"""
ModifierManager - Centralized modifier handling for components.

PROJ-44 Phase 4: Extracted from Component god class to reduce complexity.

This module provides utility functions for:
- Adding/removing modifiers from components
- Querying applied modifiers
- Aggregating modifier effects
- Generating stat summaries

Usage:
    The Component class delegates modifier operations to this manager.
    Methods are implemented as static methods for flexibility.
"""
from typing import List, Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.simulation.components.component_constants import ApplicationModifier


class ModifierManager:
    """
    Utility class for modifier operations.

    All methods are static - this is a namespace for modifier-related functions.
    Component instances own their modifiers list.
    """

    @staticmethod
    def add_modifier(
        modifiers_list: List['ApplicationModifier'],
        mod_id: str,
        value: Optional[float],
        registries: 'GameRegistries',
        component_type: str = None
    ) -> bool:
        """
        Add a modifier to the modifiers list.

        Checks restrictions and replaces existing modifier with same ID.

        Args:
            modifiers_list: List of ApplicationModifier to modify (in-place)
            mod_id: The modifier ID to add
            value: Optional value for the modifier
            registries: GameRegistries for modifier lookup
            component_type: Optional component type string for restriction checks

        Returns:
            True if modifier was added, False if not found or restricted
        """
        from game.simulation.components.component_constants import ApplicationModifier

        mods = registries.modifiers
        if mod_id not in mods:
            return False

        # Check restrictions
        mod_def = mods[mod_id]
        if component_type:
            if 'deny_types' in mod_def.restrictions:
                if component_type in mod_def.restrictions['deny_types']:
                    return False
            if 'allow_types' in mod_def.restrictions:
                if component_type not in mod_def.restrictions['allow_types']:
                    return False

        # Remove existing if any (replace)
        ModifierManager.remove_modifier_inplace(modifiers_list, mod_id)

        app_mod = ApplicationModifier(mod_def, value)
        modifiers_list.append(app_mod)
        return True

    @staticmethod
    def remove_modifier(
        modifiers_list: List['ApplicationModifier'],
        mod_id: str
    ) -> List['ApplicationModifier']:
        """
        Remove a modifier from the list.

        Args:
            modifiers_list: List of ApplicationModifier
            mod_id: The modifier ID to remove

        Returns:
            New list without the specified modifier
        """
        return [m for m in modifiers_list if m.definition.id != mod_id]

    @staticmethod
    def remove_modifier_inplace(
        modifiers_list: List['ApplicationModifier'],
        mod_id: str
    ) -> None:
        """
        Remove a modifier from the list in-place.

        Args:
            modifiers_list: List of ApplicationModifier to modify
            mod_id: The modifier ID to remove
        """
        modifiers_list[:] = [m for m in modifiers_list if m.definition.id != mod_id]

    @staticmethod
    def get_modifier(
        modifiers_list: List['ApplicationModifier'],
        mod_id: str
    ) -> Optional['ApplicationModifier']:
        """
        Get a modifier by ID from the list.

        Args:
            modifiers_list: List of ApplicationModifier
            mod_id: The modifier ID to find

        Returns:
            The matching ApplicationModifier, or None if not found
        """
        for m in modifiers_list:
            if m.definition.id == mod_id:
                return m
        return None

    @staticmethod
    def get_all_effects(modifiers_list: List['ApplicationModifier']) -> List[Any]:
        """
        Get all evaluated effects from all applied modifiers.

        Args:
            modifiers_list: List of ApplicationModifier

        Returns:
            List of ModifierEffect from all modifiers
        """
        all_effects = []
        for app_mod in modifiers_list:
            effects = app_mod.definition.evaluate_effects(app_mod.value)
            all_effects.extend(effects)
        return all_effects

    @staticmethod
    def get_stat_summary(modifiers_list: List['ApplicationModifier']) -> Dict[str, Dict]:
        """
        Get summary grouped by stat with net values and contributors.

        Args:
            modifiers_list: List of ApplicationModifier

        Returns:
            Dict mapping stat_key to:
                {
                    'net_value': float,  # Combined value for this stat
                    'operation': str,    # 'multiply', 'add', or 'set'
                    'contributors': [    # List of contributing modifiers
                        {
                            'modifier_id': str,
                            'modifier_name': str,
                            'value': float,
                            'formula': str
                        },
                        ...
                    ]
                }
        """
        summary: Dict[str, Dict] = {}

        all_effects = ModifierManager.get_all_effects(modifiers_list)

        for effect in all_effects:
            stat_key = effect.stat_key

            if stat_key not in summary:
                # Initialize based on operation type
                default_value = 1.0 if effect.operation == 'multiply' else 0.0
                summary[stat_key] = {
                    'net_value': default_value,
                    'operation': effect.operation,
                    'contributors': []
                }

            entry = summary[stat_key]

            # Add contributor info
            entry['contributors'].append({
                'modifier_id': effect.source_modifier_id,
                'modifier_name': effect.source_modifier_name,
                'value': effect.value,
                'formula': effect.formula_str
            })

            # Calculate net value based on operation
            if effect.operation == 'multiply':
                entry['net_value'] *= effect.value
            elif effect.operation == 'add':
                entry['net_value'] += effect.value
            elif effect.operation == 'set':
                entry['net_value'] = effect.value  # Last set wins

        return summary
