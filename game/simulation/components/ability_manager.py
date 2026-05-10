"""
AbilityManager - Stateful delegate for component ability management.

PROJ-44 Phase 4: Extracted from Component god class to reduce complexity.
PROJ-190: Updated to use IAbility protocol for type-safe checks.
PROJ-241: Converted from static namespace to proper stateful delegate
         matching ComponentHealthManager/ComponentResourceManager pattern.

This module manages:
- Ability state (owns the instances list and MRO-based index)
- Instantiating abilities from component data
- Querying abilities by type (with polymorphic support via index)
- Tag-based ability queries (generalized from has_pdc_ability)
- Aggregating UI information from abilities

Usage:
    The Component class creates an AbilityManager delegate that owns the
    component's ability instances and index. Component facade properties
    provide backward compatibility for external callers.
"""
import logging
from typing import List, Optional, Any, Dict, TYPE_CHECKING

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.simulation.components.abilities import Ability
    from game.simulation.components.component import Component


class AbilityManager:
    """Manages abilities for a Component as a stateful delegate.

    PROJ-241: Converted from static namespace to proper delegate.
    Follows the ComponentHealthManager/ComponentResourceManager pattern:
    - __slots__ for memory efficiency
    - __init__(component) takes component reference
    - Instance methods own and operate on internal state
    - Component provides facade properties for backward compatibility

    The manager owns the _instances list and _index dict, and handles
    ability instantiation, index building, and all querying.
    """

    __slots__ = ('_component', '_instances', '_index')

    def __init__(self, component: 'Component'):
        """Initialize with a component reference, instantiate abilities, build index.

        Args:
            component: The Component instance to manage abilities for.
        """
        self._component = component
        self._instances: List['Ability'] = []
        self._index: Dict[str, List['Ability']] = {}
        self.instantiate_and_index()

    def instantiate_and_index(self) -> None:
        """Instantiate abilities from component data and build MRO-based index.

        Called during construction and also by ComponentStatsCalculator
        during recalculate_stats() to sync abilities after data changes.
        """
        self._instances = self._instantiate(
            self._component.abilities,
            self._instances,
            self._component
        )
        self._build_index()

    def _build_index(self) -> None:
        """Build MRO-based index for O(1) lookup by class name.

        Moved from Component._instantiate_abilities.
        Indexes each ability instance by its class name and all parent
        class names (for polymorphic queries), stopping at 'object'.
        """
        self._index = {}
        for ab in self._instances:
            for cls in ab.__class__.mro():
                cls_name = cls.__name__
                if cls_name == 'object':
                    break
                if cls_name not in self._index:
                    self._index[cls_name] = []
                self._index[cls_name].append(ab)

    @property
    def ability_instances(self) -> List['Ability']:
        """The current list of ability instances."""
        return self._instances

    def get_abilities(self, ability_name: str) -> List['Ability']:
        """Get all abilities of a specific type.

        Uses pre-built MRO index for O(1) lookup. Falls back to
        registry-based polymorphic search for edge cases.

        Args:
            ability_name: The ability class name to search for.

        Returns:
            List of matching ability instances (copy).
        """
        # Fast path: use pre-built index (includes MRO for polymorphism)
        if ability_name in self._index:
            return list(self._index[ability_name])  # Return copy

        # Fallback: delegate to static method for edge cases
        return AbilityManager._get_abilities_polymorphic(
            ability_name, self._instances
        )

    def get_ability(self, ability_name: str) -> Optional['Ability']:
        """Get first ability of a specific type.

        Args:
            ability_name: The ability class name to search for.

        Returns:
            First matching ability instance, or None if not found.
        """
        # Fast path: use pre-built index
        if ability_name in self._index:
            abilities = self._index[ability_name]
            return abilities[0] if abilities else None

        # Fallback
        abilities = AbilityManager._get_abilities_polymorphic(
            ability_name, self._instances
        )
        return abilities[0] if abilities else None

    def has_ability(self, ability_name: str) -> bool:
        """Check if any ability of the specified type exists.

        Args:
            ability_name: The ability class name to check for.

        Returns:
            True if ability exists, False otherwise.
        """
        # Fast path: use pre-built index
        if ability_name in self._index:
            return len(self._index[ability_name]) > 0

        # Fallback: check abilities dict then polymorphic search
        if self._component.abilities and ability_name in self._component.abilities:
            return True

        return len(AbilityManager._get_abilities_polymorphic(
            ability_name, self._instances
        )) > 0

    def has_ability_with_tag(self, tag: str) -> bool:
        """Check if any ability has a specific tag.

        Generalized replacement for the old has_pdc_ability.

        Args:
            tag: The tag to search for (e.g., 'pdc').

        Returns:
            True if any ability has the tag, False otherwise.
        """
        for ab in self._instances:
            if ab.tags and tag in ab.tags:
                return True
        return False

    def has_pdc_ability(self) -> bool:
        """Check if component has a Point Defense weapon ability.

        Returns True if any ability has 'pdc' in its tags.
        Thin wrapper around has_ability_with_tag.
        """
        return self.has_ability_with_tag('pdc')

    def get_ui_rows(self) -> List[Dict[str, Any]]:
        """Aggregate UI rows from all ability instances.

        Each ability can provide display rows for detail panels.
        Format: [{'label': 'Thrust', 'value': '1500 N'}, ...]

        Returns:
            Aggregated list of UI row dicts.
        """
        rows = []
        for ab in self._instances:
            rows.extend(ab.get_ui_rows())
        return rows

    # ---- Private helpers ----

    @staticmethod
    def _instantiate(
        abilities_dict: Dict[str, Any],
        existing_instances: List['Ability'],
        component_ref: Any
    ) -> List['Ability']:
        """Instantiate or sync ability objects from an abilities dict.

        Preserves existing instances to maintain runtime state (cooldowns, energy).

        Args:
            abilities_dict: Dict of ability definitions from component data.
            existing_instances: Current ability instances (may be empty).
            component_ref: Reference to the owning Component.

        Returns:
            New list of ability instances.
        """
        from game.simulation.components.abilities import ABILITY_REGISTRY, create_ability

        existing_map: Dict[str, List['Ability']] = {}
        for ab in existing_instances:
            cls_name = ab.__class__.__name__
            if cls_name not in existing_map:
                existing_map[cls_name] = []
            existing_map[cls_name].append(ab)

        new_instances = []

        for name, data in abilities_dict.items():
            if name not in ABILITY_REGISTRY:
                continue

            items = data if isinstance(data, list) else [data]

            target = ABILITY_REGISTRY[name]
            target_cls_name = target.__name__ if isinstance(target, type) else None

            for item in items:
                match_name = target_cls_name or name

                found_existing = False
                if match_name in existing_map and existing_map[match_name]:
                    ab = existing_map[match_name].pop(0)
                    ab.sync_data(item)
                    new_instances.append(ab)
                    found_existing = True

                if not found_existing:
                    ab = create_ability(name, component_ref, item)
                    if ab:
                        new_instances.append(ab)

        return new_instances

    @staticmethod
    def _get_abilities_polymorphic(
        ability_name: str, instances: List['Ability']
    ) -> List['Ability']:
        """Polymorphic ability search using the ABILITY_REGISTRY.

        Used as fallback when the MRO index doesn't contain the requested name.

        Args:
            ability_name: The ability class name to search for.
            instances: List of ability instances to search.

        Returns:
            List of matching ability instances.
        """
        from game.simulation.components.abilities import ABILITY_REGISTRY

        target_class = None
        if ability_name in ABILITY_REGISTRY:
            val = ABILITY_REGISTRY[ability_name]
            if isinstance(val, type):
                target_class = val

        found = []
        for ab in instances:
            if target_class and isinstance(ab, target_class):
                found.append(ab)
            elif target_class is not None:
                # [KNOWN_ISSUE] Fallback for Module Identity Drift in tests.
                for cls in ab.__class__.mro():
                    if cls.__name__ == ability_name:
                        found.append(ab)
                        break

        return found

