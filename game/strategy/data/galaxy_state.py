"""``GalaxyState`` — shared mutable state owned by ``Galaxy`` services.

PROJ-372 Phase 3: extracts the 11 mutable indexes + 2 ID counters +
``radius`` from ``Galaxy`` into a focused dataclass. The four
PROJ-173-Phase-2 delegates (``GalaxyEntityRegistry``,
``GalaxySpatialIndex``, ``GalaxyWarpGenerator``,
``GalaxySystemGenerator``) take ``GalaxyState`` instead of holding
``_galaxy: Galaxy`` back-references — breaking the circular aliasing
and making delegates unit-testable without constructing a real
``Galaxy()`` (which loads naming registries from disk).

Field renames: leading-underscore dict fields drop the underscore on
the state object (``_global_hex_planets`` -> ``global_hex_planets``).
PROJ-387 deleted the five legacy underscore-prefixed ``@property``
forwarders that briefly bridged the rename. Cross-module readers now
go through ``Galaxy.state`` (a public ``@property`` returning this
``GalaxyState`` instance) introduced by PROJ-394.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from game.core.hex_math import HexCoord
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.galaxy import StarSystem
    from game.strategy.data.planet import Planet


__all__ = ["GalaxyState"]


@dataclass
class GalaxyState:
    """Owns all mutable state historically held on ``Galaxy``.

    Services receive an instance of this class and read/write its
    fields directly. The ``Galaxy`` facade exposes this object as
    ``Galaxy.state`` (PROJ-394) for cross-module readers; the public
    Galaxy attributes (``radius``, ``systems``, ``name_map``,
    ``planets_by_id``, ``fleets_by_id``) remain as thin
    ``@property`` forwarders onto these fields.
    """

    radius: int

    # System lookup tables (was Galaxy.systems, .name_map).
    systems: Dict["HexCoord", "StarSystem"] = field(default_factory=dict)
    name_map: Dict[str, "StarSystem"] = field(default_factory=dict)

    # Entity registries (was Galaxy.planets_by_id, .fleets_by_id).
    planets_by_id: Dict[int, "Planet"] = field(default_factory=dict)
    fleets_by_id: Dict[int, "Fleet"] = field(default_factory=dict)

    # Spatial reverse-lookups (was Galaxy._planet_to_system).
    planet_to_system: Dict["Planet", "StarSystem"] = field(default_factory=dict)

    # Spatial forward-lookups (was Galaxy._global_hex_*).
    global_hex_planets: Dict["HexCoord", List["Planet"]] = field(default_factory=dict)
    global_hex_zones: Dict["HexCoord", list] = field(default_factory=dict)
    global_hex_warp_points: Dict["HexCoord", "StarSystem"] = field(default_factory=dict)

    # Zone reverse-lookup keyed by id() (was Galaxy._zone_to_system).
    zone_to_system: Dict[int, "StarSystem"] = field(default_factory=dict)

    # ID counters (was Galaxy._next_planet_id, ._next_fleet_id).
    next_planet_id: int = 1
    next_fleet_id: int = 1
