"""PROJ-396 Phase 3: per-superweapon process_* handlers.

Each module exports one free function ``process_<name>(processor, fleet,
empire, galaxy, empires, component_registry=None) -> SuperweaponResult``.
The ``processor: SuperweaponOrderProcessor`` parameter replaces the
implicit ``self`` capture the closures used in the pre-decomposition
monolithic file (PROJ-382 review MAJ-005), without forcing the spec
layer to know about effect closures (Option A).
"""
from __future__ import annotations

from .close_warp_point import process_close_warp_point
from .create_dyson_sphere import process_create_dyson_sphere
from .implode_planet import process_implode_planet
from .open_warp_point import process_open_warp_point
from .stellerate_star import process_stellerate_star

__all__ = [
    "process_close_warp_point",
    "process_create_dyson_sphere",
    "process_implode_planet",
    "process_open_warp_point",
    "process_stellerate_star",
]
