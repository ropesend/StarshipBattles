"""Spatial / hex-contents query slice (PROJ-477 Phase 2).

``contents_at_hex`` answers "what occupies this global map hex" as a grouped,
multi-hex-aware summary DTO. It is DISTINCT from ``planets.at_hex`` (exact-center
planet membership only): the zone spatial index registers every hex a multi-hex
object (Dyson Sphere, storm, large star) occupies, so a zone whose CENTER is a
different hex is still reported here. Projection to a summary DTO is acceptable
because this is a cold, summary-only read surface; callers that need the LIVE
domain objects (identity compares, ``is_planet`` protocol checks, id round-trips
into commands) use ``scene.world.zones_at_hex`` / ``planets_at_exact_hex``
instead (decisions.md EXECUTION deviation).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from game.core.hex_math import HexCoord
from game.strategy.facade.dto import HexContentsInfo

if TYPE_CHECKING:
    from game.strategy.facade.slices._facade_state import FacadeSessionState


class SpatialSlice:
    """Grouped hex-contents reads (planets / zones / warp points at a hex)."""

    __slots__ = ("_state",)

    def __init__(self, state: "FacadeSessionState") -> None:
        self._state = state

    def contents_at_hex(self, hex_coord: HexCoord) -> HexContentsInfo:
        """Grouped planet / zone / warp-point membership at a global hex.

        Multi-hex aware (preserves Dyson-Sphere edge-hex membership). Returns a
        summary DTO; never ``None`` (empty groups when nothing is present).
        """
        galaxy = self._state._session.galaxy

        get_planets = getattr(galaxy, "get_planets_at_global_hex", None)
        planets = get_planets(hex_coord) if get_planets is not None else []
        planet_names = tuple(
            getattr(p, "name", None) for p in (planets or [])
            if getattr(p, "name", None) is not None
        )

        get_zones = getattr(galaxy, "get_zones_at_global_hex", None)
        zones = get_zones(hex_coord) if get_zones is not None else []
        zone_names = tuple(
            getattr(z, "name", None) for z in (zones or [])
            if getattr(z, "name", None) is not None
        )

        warp_point_names: tuple[str, ...] = ()
        state = getattr(galaxy, "state", None)
        warp_map = getattr(state, "global_hex_warp_points", None) if state else None
        if isinstance(warp_map, dict):
            owner_system = warp_map.get(hex_coord)
            if owner_system is not None:
                name = getattr(owner_system, "name", None)
                if name is not None:
                    warp_point_names = (name,)

        return HexContentsInfo(
            hex=hex_coord,
            planet_names=planet_names,
            zone_names=zone_names,
            warp_point_names=warp_point_names,
        )
