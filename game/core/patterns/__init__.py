"""
Core patterns module - Reusable iteration and access patterns.

PROJ-204: Extracted from strategy layer to eliminate duplication.
"""

from game.core.patterns.layer_iterator import (
    iter_components,
    iter_layers_and_components,
    iter_components_with_ids,
    get_component_id,
)

__all__ = [
    'iter_components',
    'iter_layers_and_components',
    'iter_components_with_ids',
    'get_component_id',
]
