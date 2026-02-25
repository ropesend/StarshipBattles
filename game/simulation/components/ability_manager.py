"""
AbilityManager - Centralized ability handling for components.

PROJ-44 Phase 4: Extracted from Component god class to reduce complexity.
PROJ-190: Updated to use IAbility protocol for type-safe checks.

This module provides utility functions for:
- Instantiating abilities from component data
- Querying abilities by type (with polymorphic support)
- Aggregating UI information from abilities

Usage:
    The Component class delegates ability operations to this manager.
    Methods are implemented as static/class methods for flexibility.
"""
from typing import List, Optional, Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from game.simulation.components.abilities import Ability


class AbilityManager:
    """
    Utility class for ability operations.

    All methods are static - this is a namespace for ability-related functions,
    not a stateful manager. Component instances own their ability_instances list.
    """

    @staticmethod
    def get_abilities(ability_name: str, instances: List['Ability']) -> List['Ability']:
        """
        Get all abilities of a specific type from an instance list.

        Supports polymorphic matching - asking for 'WeaponAbility' will return
        ProjectileWeaponAbility, BeamWeaponAbility, etc.

        Args:
            ability_name: The ability class name to search for (e.g., 'WeaponAbility')
            instances: List of ability instances to search

        Returns:
            List of matching ability instances (may be empty)
        """
        from game.simulation.components.abilities import ABILITY_REGISTRY

        target_class = None
        if ability_name in ABILITY_REGISTRY:
            val = ABILITY_REGISTRY[ability_name]
            if isinstance(val, type):
                target_class = val

        found = []
        for ab in instances:
            # 1. Polymorphic check (preferred)
            if target_class and isinstance(ab, target_class):
                found.append(ab)
            # [KNOWN_ISSUE] Fallback for Module Identity Drift in tests.
            # When test modules reload ability classes, isinstance() fails due to
            # different class objects. This __name__ check provides test isolation.
            # Ref: Phase 2 Task 2.5 audit - documented as intentional tech debt.
            else:
                for cls in ab.__class__.mro():
                    if cls.__name__ == ability_name:
                        found.append(ab)
                        break

        return found

    @staticmethod
    def get_ability(ability_name: str, instances: List['Ability']) -> Optional['Ability']:
        """
        Get first ability of a specific type.

        Args:
            ability_name: The ability class name to search for
            instances: List of ability instances to search

        Returns:
            First matching ability instance, or None if not found
        """
        abilities = AbilityManager.get_abilities(ability_name, instances)
        return abilities[0] if abilities else None

    @staticmethod
    def has_ability(ability_name: str, instances: List['Ability'], abilities_dict: Dict = None) -> bool:
        """
        Check if any ability of the specified type exists.

        Supports both direct dict lookup (fast) and polymorphic search (thorough).

        Args:
            ability_name: The ability class name to check for
            instances: List of ability instances to search
            abilities_dict: Optional dict for fast direct lookup

        Returns:
            True if ability exists, False otherwise
        """
        # 1. Direct check in abilities dict (fast path)
        if abilities_dict and ability_name in abilities_dict:
            return True

        # 2. Polymorphic check via instances
        return len(AbilityManager.get_abilities(ability_name, instances)) > 0

    @staticmethod
    def has_pdc_ability(instances: List['Ability']) -> bool:
        """
        Check if any ability is a Point Defense weapon.

        Returns True if any ability has 'pdc' in its tags.

        Args:
            instances: List of ability instances to search

        Returns:
            True if PDC ability found, False otherwise
        """
        for ab in instances:
            # All ability instances have tags (set attribute in Ability base class)
            if ab.tags and 'pdc' in ab.tags:
                return True
        return False

    @staticmethod
    def get_ui_rows(instances: List['Ability']) -> List[Dict[str, Any]]:
        """
        Aggregate UI rows from all ability instances.

        Each ability can provide display rows for detail panels.
        Format: [{'label': 'Thrust', 'value': '1500 N'}, ...]

        Args:
            instances: List of ability instances

        Returns:
            Aggregated list of UI row dicts
        """
        rows = []
        for ab in instances:
            # All ability instances have get_ui_rows (defined in Ability base class)
            rows.extend(ab.get_ui_rows())
        return rows

    @staticmethod
    def instantiate_abilities(
        abilities_dict: Dict[str, Any],
        existing_instances: List['Ability'],
        component_ref: Any
    ) -> List['Ability']:
        """
        Instantiate or sync ability objects from an abilities dict.

        Preserves existing instances to maintain runtime state (cooldowns, energy).
        Adds new abilities, removes obsolete ones.

        Args:
            abilities_dict: Dict of ability definitions from component data
            existing_instances: Current ability instances (may be empty)
            component_ref: Reference to the owning Component

        Returns:
            New list of ability instances
        """
        from game.simulation.components.abilities import ABILITY_REGISTRY, create_ability

        # 1. Map existing instances for quick lookup
        # Key: (ability_type_name, index_in_that_type)
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

            # Get the target class for this registry entry
            target = ABILITY_REGISTRY[name]
            target_cls_name = target.__name__ if isinstance(target, type) else None

            for item in items:
                # Heuristic: Match by Target Class Name if known
                match_name = target_cls_name or name

                found_existing = False
                if match_name in existing_map and existing_map[match_name]:
                    ab = existing_map[match_name].pop(0)
                    # All ability instances have sync_data (defined in Ability base class)
                    ab.sync_data(item)
                    new_instances.append(ab)
                    found_existing = True

                if not found_existing:
                    ab = create_ability(name, component_ref, item)
                    if ab:
                        new_instances.append(ab)

        return new_instances
