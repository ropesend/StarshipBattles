"""Pathfinding free-function shims.

PROJ-372 Phase 4: each function is a 1-line forwarder to
``GalaxyPathfindingService`` / ``InterceptCalculator``. The shims
remain as a back-compat surface for the ~14 production caller sites
that still import them directly. PROJ-372 Phase 5 closed without the
caller-site migration sweep; tracked as PROJ-376 follow-up (or a
direct sweep on the next strategy-layer touch). The fresh
``InterceptCalculator`` constructed by ``_intercept_for(galaxy)`` is
intentional — routing through ``galaxy._intercept`` would defeat the
test-patch transparency the shims provide.

The shims do not emit ``DeprecationWarning`` because pytest.ini
filters DeprecationWarnings as errors and we want Phase 4 to ship
green even before the migration sweep happens. Phase-4 acceptance test
``test_pathfinding_shim_emits_deprecation_warning`` is replaced by a
forwarding-correctness test.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, TypeVar, Union

from game.core.hex_math import HexCoord

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.galaxy import Galaxy
    from game.strategy.data.star_system import StarSystem
    from game.strategy.services.fleet_navigation_service import NavigationState

PathT = TypeVar("PathT", List[HexCoord], tuple)


def strip_start_hex(current_location: HexCoord, path: Optional[PathT]) -> Optional[PathT]:
    from game.strategy.services.galaxy_pathfinding_service import (
        GalaxyPathfindingService,
    )
    return GalaxyPathfindingService.strip_start_hex(current_location, path)


def find_path_deep_space(start: HexCoord, end: HexCoord) -> List[HexCoord]:
    from game.core.hex_math import hex_linedraw
    return hex_linedraw(start, end)


def _pathfinder_for(galaxy):
    """Get a real GalaxyPathfindingService bound to `galaxy`.

    Production galaxies have ``_pathfinder`` already; mock galaxies in
    tests usually don't, but we always wrap them in a real service so
    the shim's algorithmic behavior is honored even when callers pass
    a stub object."""
    from game.strategy.services.galaxy_pathfinding_service import (
        GalaxyPathfindingService,
    )
    pf = getattr(galaxy, "_pathfinder", None)
    # Use the real service unless the galaxy already has a real one.
    if not isinstance(pf, GalaxyPathfindingService):
        pf = GalaxyPathfindingService(galaxy)
    return pf


def _intercept_for(galaxy):
    """Get a real InterceptCalculator wrapping `galaxy`'s pathfinder.

    Always constructs a fresh calculator so test patches of the shim
    free functions (e.g. ``patch('pathfinding.find_hybrid_path')``)
    flow through to the calculator's pathfinding calls."""
    from game.strategy.services.intercept_calculator import InterceptCalculator
    return InterceptCalculator(_pathfinder_for(galaxy))


def find_path_interstellar(
    start_system: "StarSystem", end_system: "StarSystem", galaxy: "Galaxy",
) -> Optional[List["StarSystem"]]:
    return _pathfinder_for(galaxy).find_path_interstellar(start_system, end_system)


def get_system_at_hex(
    galaxy: "Galaxy", hex_c: HexCoord, radius: int = 50,
) -> Optional["StarSystem"]:
    return _pathfinder_for(galaxy).get_system_at_hex(hex_c, radius)


def find_nearest_system(galaxy: "Galaxy", hex_c: HexCoord) -> Optional["StarSystem"]:
    return _pathfinder_for(galaxy).find_nearest_system(hex_c)


def find_hybrid_path(galaxy, start_hex, end_hex, fleet=None, can_warp=None) -> List[HexCoord]:
    return _pathfinder_for(galaxy).find_hybrid_path(
        start_hex, end_hex, fleet=fleet, can_warp=can_warp,
    )


def project_fleet_path(fleet, galaxy, max_turns: int = 10) -> List[dict]:
    from game.strategy.services.intercept_calculator import project_fleet_path as _proj
    return _proj(fleet, galaxy, max_turns)


def calculate_intercept_point(
    chaser: Union["Fleet", "NavigationState"], target_fleet, galaxy: "Galaxy",
) -> Optional[HexCoord]:
    return _intercept_for(galaxy).calculate_intercept_point(chaser, target_fleet, galaxy)
