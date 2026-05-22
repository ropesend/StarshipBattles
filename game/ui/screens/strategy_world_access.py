"""Scene-owned live raw-domain traversal seam (PROJ-477 Phase 5 Task 5.1).

``StrategyWorldAccess`` is the SINGLE raw-domain seam for the render-hot stack
(``StrategyRenderer`` + ``strategy_render/*``) and the raw-window handoffs (menu
builders, list windows, build-queue chain). It replaces the broad
``scene.galaxy`` / ``scene.empires`` / ``scene.systems`` pass-through bus and the
renderer re-exporters ``r.galaxy`` / ``r.empires`` / ``r.systems``.

**Performance contract (HARD):** every method hands back the UNDERLYING live
collections / O(1) map lookups. There is NO per-frame DTO allocation here — the
render migration is a mechanical source-swap (read ``scene.world.iter_systems()``
instead of ``r.galaxy.systems.values()``), not a DTO rewrite. ``iter_systems()``
yields the live ``StarSystem`` objects (element identity preserved); the
``global_hex_*`` accessors return the live galaxy-state dicts by reference.

Backed by the screen's private ``_session`` through a provider callable so the
seam always resolves the CURRENT session (honours test ``session`` swaps). The
screen is the composition root — it owns the only legitimate ``_session`` handle
— so the ``_session`` reads inside this module are Category-A allowlisted in the
session guard, and guard #3's end-state allowlist permits this module.
"""

from __future__ import annotations

from typing import Any, Callable, Iterator, List

from game.core.hex_math import HexCoord


class StrategyWorldAccess:
    """Live raw-domain traversal over the strategy session's galaxy + empires.

    All reads are live — no DTO projection. See module docstring for the
    performance contract.
    """

    __slots__ = ("_session_provider",)

    def __init__(self, session_provider: Callable[[], Any]) -> None:
        self._session_provider = session_provider

    @property
    def _galaxy(self) -> Any:
        return self._session_provider().galaxy

    # ------------------------------------------------------------------
    # Live iteration (no allocation beyond the underlying view)
    # ------------------------------------------------------------------

    def iter_systems(self) -> Iterator[Any]:
        """Yield the LIVE ``StarSystem`` objects (element identity preserved)."""
        return iter(self._galaxy.systems.values())

    def iter_empires(self) -> Iterator[Any]:
        """Yield the LIVE empire objects."""
        return iter(self._session_provider().empires)

    # ------------------------------------------------------------------
    # O(1) system resolution (live objects)
    # ------------------------------------------------------------------

    def system_by_name(self, name: str) -> Any | None:
        """LIVE system with the given name (O(1) name map), or ``None``."""
        return self._galaxy.get_system_by_name(name)

    def system_for_object(self, obj: object) -> Any | None:
        """LIVE system containing an object, or ``None``."""
        return self._galaxy.get_system_of_object(obj)

    def system_at_map_hex(self, hex_coord: HexCoord, radius: int = 50) -> Any | None:
        """LIVE system OWNING a map hex (pathfinder system-radius, default 50).

        DISTINCT from ``near_hex(max_dist=8)`` — system-ownership semantics.
        """
        return self._galaxy._pathfinder.get_system_at_hex(hex_coord, radius)

    # ------------------------------------------------------------------
    # O(1) spatial membership (live objects)
    # ------------------------------------------------------------------

    def planets_at_exact_hex(self, hex_coord: HexCoord) -> List[Any]:
        """LIVE planets at the EXACT global hex (no multi-hex zone widening)."""
        return self._galaxy.get_planets_at_global_hex(hex_coord)

    def zones_at_hex(self, hex_coord: HexCoord) -> List[Any]:
        """LIVE multi-hex zone objects registered at the global hex.

        Multi-hex-aware (the spatial index registers every occupied hex), so a
        Dyson Sphere whose center is elsewhere is still returned here.
        """
        get_zones = getattr(self._galaxy, "get_zones_at_global_hex", None)
        if get_zones is None:
            return []
        return get_zones(hex_coord) or []

    def warp_points_at_hex(self, hex_coord: HexCoord) -> Any | None:
        """The LIVE system owning the warp point at the global hex, or ``None``."""
        return self._galaxy.state.global_hex_warp_points.get(hex_coord)

    def planet_by_id(self, planet_id: int) -> Any | None:
        """LIVE planet by id (O(1)), or ``None`` (POST-FLESH B3 — live-yard resolve)."""
        return self._galaxy.get_planet_by_id(planet_id)

    # ------------------------------------------------------------------
    # Live galaxy-state map accessors (returned by reference — render-hot)
    # ------------------------------------------------------------------

    @property
    def global_hex_planets(self) -> Any:
        """LIVE ``HexCoord -> [Planet]`` map (by reference; render-hot)."""
        return self._galaxy.state.global_hex_planets

    @property
    def global_hex_zones(self) -> Any:
        """LIVE ``HexCoord -> [zone]`` map (by reference; render-hot)."""
        return self._galaxy.state.global_hex_zones

    @property
    def global_hex_warp_points(self) -> Any:
        """LIVE ``HexCoord -> StarSystem`` warp-point map (by reference)."""
        return self._galaxy.state.global_hex_warp_points
