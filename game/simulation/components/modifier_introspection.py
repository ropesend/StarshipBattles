"""
Modifier Introspection Module.

This module provides UI-friendly introspection of the modifier system:
1. What abilities a modifier affects
2. Summary of all applied modifiers on a component
3. Base vs current values for each ability
4. Human-readable tooltip generation

Used by UI components to display:
- Modifier tooltips when hovering over modifier options
- Component detail panels showing applied modifiers
- Ability stat displays showing base → current values
"""
from typing import Dict, Any, List, Optional, Set, TYPE_CHECKING

from .modifier_effects import ModifierEffectEvaluator

if TYPE_CHECKING:
    from .component import Component
    from .abilities.base import Ability


class ModifierIntrospection:
    """
    Provides introspection capabilities for the modifier system.

    All methods are static - this is a utility class.
    """

    @staticmethod
    def get_modifier_affects(
        mod_def: Dict[str, Any],
        component: 'Component',
        param_value: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Determine what abilities a modifier affects on a given component.

        This is used for:
        - UI tooltips showing "This modifier affects: WeaponAbility, ShieldProjection"
        - Validation/warnings about modifiers that won't do anything

        Args:
            mod_def: Modifier definition dict (from JSON or registry)
            component: The component to check against
            param_value: Optional parameter value (uses default if not specified)

        Returns:
            {
                'abilities': ['ProjectileWeaponAbility', 'ShieldProjection'],
                'effects_preview': ['damage_mult x1.50', 'capacity_mult x1.20'],
                'affected_stats': ['damage_mult', 'capacity_mult'],
                'targeted_abilities': ['ProjectileWeaponAbility'],  # Only explicitly targeted
            }
        """
        # Get param value from definition if not provided
        if param_value is None:
            param_def = mod_def.get('param', {})
            param_value = param_def.get('default', 1.0) if isinstance(param_def, dict) else 1.0

        # Evaluate effects
        effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, param_value)

        # Gather affected stats and targeted abilities
        affected_stats: Set[str] = set()
        targeted_abilities: Set[str] = set()
        effects_preview: List[str] = []

        for effect in effects:
            affected_stats.add(effect.stat_key)
            effects_preview.append(effect.describe())
            if effect.target_ability:
                targeted_abilities.add(effect.target_ability)

        # Find which abilities on this component consume these stats
        affected_abilities: Set[str] = set()

        # Add explicitly targeted abilities
        affected_abilities.update(targeted_abilities)

        # Find abilities that consume the affected stats
        for ability in component.ability_instances:
            ability_class_name = ability.__class__.__name__
            consumed_stats = ability.get_consumed_stats()

            # Check if any of the affected stats are consumed by this ability
            for stat_key in affected_stats:
                # Convert string stat key to enum for comparison
                for consumed in consumed_stats:
                    if consumed.value == stat_key:
                        affected_abilities.add(ability_class_name)
                        break

        return {
            'abilities': list(affected_abilities),
            'effects_preview': effects_preview,
            'affected_stats': list(affected_stats),
            'targeted_abilities': list(targeted_abilities),
        }

    @staticmethod
    def get_component_modifier_summary(component: 'Component') -> Dict[str, Any]:
        """
        Get a summary of all modifiers applied to a component.

        Used for component detail panels showing what modifiers are active.

        Args:
            component: The component to summarize

        Returns:
            {
                'component_id': 'railgun',
                'component_name': 'Railgun',
                'applied_modifiers': [
                    {
                        'id': 'hardened_mount',
                        'name': 'Hardened',
                        'param_value': 2.0,
                        'effects': ['mass_mult x2.00', 'hp_mult x4.00']
                    },
                    ...
                ],
                'total_stats': {
                    'mass_mult': 2.0,
                    'hp_mult': 4.0,
                    ...
                }
            }
        """
        applied_modifiers: List[Dict[str, Any]] = []

        # Get applied modifiers from component
        # component.modifiers is a list of ApplicationModifier objects
        for app_mod in component.modifiers:
            mod_def = app_mod.definition
            mod_value = app_mod.value

            # Evaluate effects for this modifier
            effects = mod_def.evaluate_effects(mod_value) if hasattr(mod_def, 'evaluate_effects') else []
            effect_descriptions = [e.describe() for e in effects] if effects else []

            applied_modifiers.append({
                'id': mod_def.id,
                'name': mod_def.display_name if hasattr(mod_def, 'display_name') else mod_def.id,
                'param_value': mod_value,
                'effects': effect_descriptions,
            })

        return {
            'component_id': component.id,
            'component_name': component.display_name if hasattr(component, 'display_name') else component.id,
            'applied_modifiers': applied_modifiers,
            'total_stats': dict(component.stats) if hasattr(component, 'stats') else {},
        }

    @staticmethod
    def get_ability_modifier_summary(ability: 'Ability') -> Dict[str, Any]:
        """
        Get a summary of how modifiers affect a specific ability.

        Shows base vs current values for each stat the ability consumes.

        Args:
            ability: The ability to summarize

        Returns:
            {
                'ability_class': 'ProjectileWeaponAbility',
                'stats': [
                    {
                        'attribute': 'damage',
                        'base': 100.0,
                        'current': 150.0,
                        'stat_key': 'damage_mult',
                        'stat_value': 1.5,
                        'operation': 'multiply'
                    },
                    ...
                ]
            }
        """
        # Use the ability's built-in get_effect_summary() if available
        summary = ability.get_effect_summary() if hasattr(ability, 'get_effect_summary') else []

        return {
            'ability_class': ability.__class__.__name__,
            'stats': summary,
        }

    @staticmethod
    def generate_modifier_tooltip(
        mod_def: Dict[str, Any],
        param_value: float,
        component: Optional['Component'] = None
    ) -> str:
        """
        Generate a human-readable tooltip for a modifier.

        Used when hovering over modifier options in the UI.

        Args:
            mod_def: Modifier definition dict
            param_value: Current parameter value
            component: Optional component context for ability-specific info

        Returns:
            Multi-line string suitable for tooltip display
        """
        lines: List[str] = []

        # Header with modifier name
        name = mod_def.get('name', mod_def.get('id', 'Unknown Modifier'))
        lines.append(f"=== {name} ===")

        # Description if available
        description = mod_def.get('description', '')
        if description:
            lines.append(description)
            lines.append("")

        # Evaluate effects
        effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, param_value)

        if effects:
            lines.append("Effects:")
            for effect in effects:
                effect_line = f"  • {effect.describe()}"
                lines.append(effect_line)

        # Show affected abilities if component provided
        if component:
            affects = ModifierIntrospection.get_modifier_affects(mod_def, component, param_value)
            if affects['abilities']:
                lines.append("")
                lines.append("Affects:")
                for ability_name in affects['abilities']:
                    lines.append(f"  • {ability_name}")

        return "\n".join(lines)

    @staticmethod
    def generate_ability_stats_display(ability: 'Ability') -> List[Dict[str, Any]]:
        """
        Generate display-ready stat entries for an ability.

        Each entry contains enough info for UI to render base/modified values,
        with visual indicators for changes.

        Args:
            ability: The ability to display stats for

        Returns:
            [
                {
                    'label': 'Damage',
                    'attribute': 'damage',
                    'base': 100.0,
                    'current': 150.0,
                    'modified': True,
                    'change_percent': 50.0,
                    'display_text': '150 (base: 100, +50%)'
                },
                ...
            ]
        """
        display_entries: List[Dict[str, Any]] = []

        # Get effect summary from the ability
        summary = ability.get_effect_summary() if hasattr(ability, 'get_effect_summary') else []

        for stat_info in summary:
            attribute = stat_info.get('attribute', 'unknown')
            base = stat_info.get('base', 0)
            current = stat_info.get('current', base)
            operation = stat_info.get('operation', 'multiply')

            # Calculate change
            modified = abs(current - base) > 0.001
            if base != 0:
                if operation == 'multiply':
                    change_percent = ((current / base) - 1.0) * 100 if base != 0 else 0
                else:
                    change_percent = ((current - base) / abs(base)) * 100 if base != 0 else 0
            else:
                change_percent = 0 if current == 0 else float('inf')

            # Format display text
            if modified:
                sign = "+" if change_percent >= 0 else ""
                display_text = f"{current:.1f} (base: {base:.1f}, {sign}{change_percent:.0f}%)"
            else:
                display_text = f"{current:.1f}"

            display_entries.append({
                'label': attribute.replace('_', ' ').title(),
                'attribute': attribute,
                'base': base,
                'current': current,
                'modified': modified,
                'change_percent': change_percent,
                'display_text': display_text,
            })

        return display_entries
