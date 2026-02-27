"""
Layer Iterator - Utilities for iterating over design_data layer structures.

PROJ-204 Phase 1: Centralized layer iteration to eliminate duplication
across strategy layer modules.

Design data layers support two formats:
1. List format: layers[layer_name] = [comp1, comp2, ...]
2. Dict format: layers[layer_name] = {"components": [comp1, comp2, ...]}

Components can be:
- Dict with "id" key: {"id": "reactor", "modifiers": [...]}
- String (component ID directly): "reactor"

This module provides generators that handle all format variations uniformly.
"""

from typing import Any, Dict, Generator, Tuple


def get_component_id(comp_entry: Any) -> str:
    """Extract component ID from a component entry.

    Handles:
    - String: returns the string itself
    - Dict: returns the 'id' field or empty string
    - Other: returns empty string

    Args:
        comp_entry: Component entry from design_data layers

    Returns:
        Component ID string, or empty string if not found
    """
    if isinstance(comp_entry, str):
        return comp_entry
    if isinstance(comp_entry, dict):
        return comp_entry.get('id', '')
    return ''


def iter_components(design_data: Dict[str, Any]) -> Generator[Any, None, None]:
    """Iterate over all components in a design's layers.

    Handles both layer formats:
    - List: layers[name] = [comp1, comp2, ...]
    - Dict: layers[name] = {"components": [comp1, ...]}

    Args:
        design_data: Design data dict with 'layers' key

    Yields:
        Each component entry (dict or string)
    """
    layers = design_data.get('layers', {})

    for layer_data in layers.values():
        # Handle list format: layers[name] = [comp1, comp2, ...]
        if isinstance(layer_data, list):
            yield from layer_data
        # Handle dict format: layers[name] = {"components": [...]}
        elif isinstance(layer_data, dict):
            components = layer_data.get('components', [])
            if isinstance(components, list):
                yield from components


def iter_layers_and_components(
    design_data: Dict[str, Any]
) -> Generator[Tuple[str, Any], None, None]:
    """Iterate over (layer_name, component) pairs.

    Same format handling as iter_components, but includes layer name.

    Args:
        design_data: Design data dict with 'layers' key

    Yields:
        Tuples of (layer_name, component_entry)
    """
    layers = design_data.get('layers', {})

    for layer_name, layer_data in layers.items():
        # Handle list format
        if isinstance(layer_data, list):
            for comp in layer_data:
                yield (layer_name, comp)
        # Handle dict format
        elif isinstance(layer_data, dict):
            components = layer_data.get('components', [])
            if isinstance(components, list):
                for comp in components:
                    yield (layer_name, comp)


def iter_components_with_ids(
    design_data: Dict[str, Any]
) -> Generator[Tuple[Any, str], None, None]:
    """Iterate over (component_entry, component_id) pairs.

    Convenience function that extracts IDs as it iterates.

    Args:
        design_data: Design data dict with 'layers' key

    Yields:
        Tuples of (component_entry, component_id)
    """
    for comp in iter_components(design_data):
        yield (comp, get_component_id(comp))
