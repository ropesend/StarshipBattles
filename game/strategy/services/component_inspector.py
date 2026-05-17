"""Backwards-compatible re-export shim for the component-inspector helpers.

PROJ-433 split the original module into two cohesive halves:

- ``game.strategy.services.component_abilities`` — Surface A: ability
  iteration helpers (``get_component_abilities``,
  ``extract_abilities_from_component``, ``iterate_design_components``,
  ``ship_has_ability``, ``count_ability``, ``list_ship_abilities``,
  ``iter_facility_ability_entries``, ``has_warp_capability``, etc.).
- ``game.strategy.services.component_layers`` — Surface B: per-instance
  layer-view helpers added by PROJ-425 Phase 2
  (``iter_components_by_layer``, ``damaged_components_by_layer``,
  ``count_damaged_components``, ``lookup_design_max_hp``).

This module is preserved as a thin re-export so the ~50 existing
``from game.strategy.services.component_inspector import X`` call sites
across engines, UI, validators, and tests keep working unchanged.

New code should prefer importing directly from ``component_abilities``
or ``component_layers``.

PROJ-108 Phase 3 origin: consolidated duplicated component/ability
iteration patterns from ColonizeValidator, SuperweaponValidator, and
other strategy-layer code.
PROJ-425 Phase 2 (TD-06): per-instance layer-view helpers added.
PROJ-433: module split for the 500-LOC convention.
"""
from game.strategy.services.component_abilities import (
    count_ability,
    extract_abilities_from_component,
    find_ship_with_ability,
    get_ability_list,
    get_component_abilities,
    get_component_threshold,
    get_component_type,
    has_warp_capability,
    iter_facility_ability_entries,
    iterate_design_components,
    list_ship_abilities,
    ship_has_ability,
)
from game.strategy.services.component_layers import (
    count_damaged_components,
    damaged_components_by_layer,
    iter_components_by_layer,
    lookup_design_max_hp,
)


__all__ = [
    "get_component_abilities",
    "extract_abilities_from_component",
    "get_component_type",
    "get_component_threshold",
    "iterate_design_components",
    "iter_facility_ability_entries",
    "ship_has_ability",
    "find_ship_with_ability",
    "count_ability",
    "list_ship_abilities",
    "get_ability_list",
    "has_warp_capability",
    "iter_components_by_layer",
    "damaged_components_by_layer",
    "count_damaged_components",
    "lookup_design_max_hp",
]
