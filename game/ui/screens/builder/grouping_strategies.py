from typing import Protocol, List, Any, Tuple
from collections import defaultdict

class GroupingStrategy(Protocol):
    """Protocol for component grouping strategies."""
    def group_components(self, components: List[Any]) -> List[Tuple[List[Any], int, float, Any]]:
        """
        Groups components based on specific criteria.
        Returns: List of tuples (list_of_components, count, total_mass, group_key)
        """
        ...

class DefaultGroupingStrategy:
    """Groups components by ID and non-readonly modifiers."""
    
    def group_components(self, components: List[Any]) -> List[Tuple[List[Any], int, float, Any]]:
        groups = defaultdict(list)
        
        for c in components:
            key = get_component_group_key(c)
            groups[key].append(c)
            
        result = []
        # Sort groups by name of first component for stability
        sorted_keys = sorted(groups.keys(), key=lambda k: groups[k][0].name)
        
        for key in sorted_keys:
            comps = groups[key]
            total_mass = sum(c.mass for c in comps)
            result.append((comps, len(comps), total_mass, key))
            
        return result

def get_component_group_key(component):
    """
    Returns a hashable key for grouping identical components.
    Key: (component_id, tuple(sorted((mod_id, mod_value))))
    """
    mod_list = []
    for m in component.modifiers:
        # Ignore readonly modifiers (like Mass Scaling) for grouping keys
        if getattr(m.definition, 'readonly', False):
            continue
        mod_list.append((m.definition.id, m.value))
    mod_list.sort()
    return (component.id, tuple(mod_list))

class TypeGroupingStrategy:
    """Groups components merely by their type/name, ignoring modifiers."""
    
    def group_components(self, components: List[Any]) -> List[Tuple[List[Any], int, float, Any]]:
        groups = defaultdict(list)
        
        for c in components:
            # Simple grouping by component definition ID (or name)
            key = c.id 
            groups[key].append(c)
            
        result = []
        sorted_keys = sorted(groups.keys())
        
        for key in sorted_keys:
            comps = groups[key]
            total_mass = sum(c.mass for c in comps)
            result.append((comps, len(comps), total_mass, key))
            
        return result

class FlatGroupingStrategy:
    """Displays components individually in order."""
    def group_components(self, components: List[Any]) -> List[Tuple[List[Any], int, float, Any]]:
        result = []
        for i, c in enumerate(components):
            # Unique key for every item
            key = (c.id, i, "flat")
            result.append(([c], 1, c.mass, key))
        return result
