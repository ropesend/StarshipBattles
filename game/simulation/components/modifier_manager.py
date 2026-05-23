"""
ModifierManager - Stateful delegate for component modifier management.

PROJ-44 Phase 4: Extracted from Component god class to reduce complexity.
PROJ-241: Converted from static namespace to proper stateful delegate
         matching ComponentHealthManager/ComponentResourceManager pattern.

This module manages:
- Modifier state (owns the modifiers list)
- Adding/removing modifiers with restriction checks
- Querying applied modifiers
- Aggregating modifier effects
- Generating stat summaries

Usage:
    The Component class creates a ModifierManager delegate that owns the
    component's modifier list. Component facade properties provide backward
    compatibility for external callers.
"""
import logging
from typing import List, Optional, Dict, Any, TYPE_CHECKING

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.simulation.components.component import Component
    from game.simulation.components.component_constants import ApplicationModifier


class ModifierManager:
    """Manages modifiers for a Component as a stateful delegate.

    PROJ-241: Converted from static namespace to proper delegate.
    Follows the ComponentHealthManager/ComponentResourceManager pattern:
    - __slots__ for memory efficiency
    - __init__(component) takes component reference
    - Instance methods own and operate on internal state
    - Component provides facade properties for backward compatibility

    The manager owns the _modifiers list and loads initial modifiers
    from component data during construction.
    """

    __slots__ = ('_component', '_modifiers', '_modifier_service')

    def __init__(self, component: 'Component'):
        """Initialize with a component reference and load initial modifiers.

        Args:
            component: The Component instance to manage modifiers for.
        """
        self._component = component
        self._modifiers: List['ApplicationModifier'] = []
        # PROJ-489: lazy ModifierService instance for restriction delegation.
        self._modifier_service = None  # type: ignore[assignment]
        self._load_initial_modifiers()

    def _get_modifier_service(self):
        """Return a cached ModifierService bound to this component's registries.

        PROJ-489: replaces the inline restriction check in ``add_modifier``
        with the canonical simulation-layer service so that ``allow_types``,
        ``deny_types`` AND ``allow_abilities`` are honored consistently.
        """
        if self._modifier_service is None:
            from game.simulation.services.modifier_service import ModifierService
            self._modifier_service = ModifierService(
                modifier_registry=self._component._registries.modifiers
            )
        return self._modifier_service

    def _load_initial_modifiers(self) -> None:
        """Load default modifiers from component data definition.

        Moved from Component.__init__ (formerly lines 171-180).
        Reads 'modifiers' from component.data and creates ApplicationModifier
        instances using the registry.
        """
        from game.simulation.components.component_constants import ApplicationModifier

        component = self._component
        if 'modifiers' not in component.data:
            return

        mods = component._registries.modifiers
        for mod_data in component.data['modifiers']:
            mod_id = mod_data['id']
            val = mod_data.get('value', None)
            if mod_id in mods:
                mod_def = mods[mod_id]
                self._modifiers.append(mod_def.create_modifier(val))
            else:
                logger.warning(
                    f"Component '{component.id}': Modifier '{mod_id}' "
                    f"not found in registry, skipping"
                )

    @property
    def modifiers(self) -> List['ApplicationModifier']:
        """The current list of applied modifiers."""
        return self._modifiers

    def add_modifier(self, mod_id: str, value: Optional[float] = None) -> bool:
        """Add a modifier to this component.

        Checks type restrictions and replaces existing modifier with same ID.
        Uses the component's registries for modifier lookup and type_str
        for restriction checks.

        Args:
            mod_id: The modifier ID to add.
            value: Optional value for the modifier.

        Returns:
            True if modifier was added, False if not found or restricted.
        """
        from game.simulation.components.component_constants import ApplicationModifier

        registries = self._component._registries
        mods = registries.modifiers
        if mod_id not in mods:
            return False

        # PROJ-489: delegate restriction checks (allow_types/deny_types/
        # allow_abilities) to the canonical ModifierService. Previously this
        # was an inline check that omitted the allow_abilities branch.
        if not self._get_modifier_service().is_modifier_allowed(mod_id, self._component):
            return False

        mod_def = mods[mod_id]

        # Remove existing if any (replace) -- in-place mutation
        self.remove_modifier(mod_id)

        app_mod = ApplicationModifier(mod_def, value)
        self._modifiers.append(app_mod)
        return True

    def remove_modifier(self, mod_id: str) -> None:
        """Remove a modifier by ID from the internal list.

        Mutates _modifiers in-place (fixes the old inconsistency where
        the static remove_modifier returned a new list).

        Args:
            mod_id: The modifier ID to remove.
        """
        self._modifiers[:] = [
            m for m in self._modifiers if m.definition.id != mod_id
        ]

    def get_modifier(self, mod_id: str) -> Optional['ApplicationModifier']:
        """Get a modifier by ID.

        Args:
            mod_id: The modifier ID to find.

        Returns:
            The matching ApplicationModifier, or None if not found.
        """
        for m in self._modifiers:
            if m.definition.id == mod_id:
                return m
        return None

    def get_all_effects(self) -> List[Any]:
        """Get all evaluated effects from all applied modifiers.

        Returns:
            List of ModifierEffect from all modifiers.
        """
        all_effects = []
        for app_mod in self._modifiers:
            effects = app_mod.definition.evaluate_effects(app_mod.value)
            all_effects.extend(effects)
        return all_effects

    def get_stat_summary(self) -> Dict[str, Dict]:
        """Get summary grouped by stat with net values and contributors.

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

        all_effects = self.get_all_effects()

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

