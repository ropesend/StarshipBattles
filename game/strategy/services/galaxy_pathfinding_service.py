"""``GalaxyPathfindingService`` — A* / hex-line pathfinding over the galaxy.

PROJ-372 Phase 4: extracted from ``game/strategy/data/pathfinding.py``
to give pathfinding a stub-able protocol surface
(``IGalaxySystemGraph``). Tests can construct a 3-system graph
without instantiating a full Galaxy.

Public API:
- ``find_path_interstellar(start_system, end_system)`` — A* over warp lanes.
- ``find_hybrid_path(start_hex, end_hex, fleet=None, can_warp=None)`` —
  combined deep-space + warp-network path.
- ``find_nearest_system(hex_c)`` — nearest StarSystem to a hex.
- ``get_system_at_hex(hex_c, radius=50)`` — nearest system within radius.
- ``strip_start_hex(current_location, path)`` — drop leading hex if it
  matches current location (PROJ-204 helper).
"""
from __future__ import annotations

import heapq
from typing import TYPE_CHECKING, List, Optional, Sequence, TypeVar, Union

from game.core.hex_math import HexCoord, hex_distance, hex_linedraw

if TYPE_CHECKING:
    from game.strategy.data.galaxy import StarSystem
    from game.strategy.data.galaxy_protocols import IGalaxySystemGraph


__all__ = ["GalaxyPathfindingService"]


PathT = TypeVar("PathT", List[HexCoord], tuple)


class GalaxyPathfindingService:
    """Pathfinding over a graph satisfying ``IGalaxySystemGraph``.

    Tests inject a stub graph; production passes the live Galaxy
    instance (Galaxy satisfies ``IGalaxySystemGraph`` structurally).
    """

    def __init__(self, graph: "IGalaxySystemGraph"):
        self._graph = graph

    @staticmethod
    def strip_start_hex(
        current_location: HexCoord, path: Optional[PathT],
    ) -> Optional[PathT]:
        """Drop leading hex if it matches current location. PROJ-204 helper."""
        if path is None:
            return None
        if not path:
            return path
        if path[0] == current_location:
            if isinstance(path, tuple):
                return path[1:]
            return list(path[1:])
        return path

    def find_path_interstellar(
        self,
        start_system: "StarSystem",
        end_system: "StarSystem",
    ) -> Optional[List["StarSystem"]]:
        """A* path between systems via warp lanes. Returns None if no path."""
        if start_system == end_system:
            return [start_system]

        graph = self._graph
        queue = [(0, start_system.name)]
        came_from: dict = {start_system.name: None}
        cost_so_far: dict = {start_system.name: 0}

        while queue:
            _, current_name = heapq.heappop(queue)

            if current_name == end_system.name:
                break

            current_sys = graph.get_system_by_name(current_name)
            if not current_sys:
                continue

            for wp in current_sys.warp_points:
                next_name = wp.destination_id
                next_sys = graph.get_system_by_name(next_name)
                if not next_sys:
                    continue

                dist = hex_distance(current_sys.global_location, next_sys.global_location)
                new_cost = cost_so_far[current_name] + dist

                if next_name not in cost_so_far or new_cost < cost_so_far[next_name]:
                    cost_so_far[next_name] = new_cost
                    priority = new_cost + hex_distance(
                        next_sys.global_location, end_system.global_location,
                    )
                    heapq.heappush(queue, (priority, next_name))
                    came_from[next_name] = current_name

        if end_system.name not in came_from:
            return None

        path = []
        curr = end_system.name
        while curr != start_system.name:
            path.append(graph.get_system_by_name(curr))
            curr = came_from[curr]
        path.append(start_system)
        path.reverse()
        return path

    def get_system_at_hex(
        self, hex_c: HexCoord, radius: int = 50,
    ) -> Optional["StarSystem"]:
        """Nearest system within `radius` hexes; O(1) exact match fast path."""
        systems = self._graph.systems
        if hex_c in systems:
            return systems[hex_c]

        best_sys = None
        min_dist = float("inf")
        for sys in systems.values():
            dist = hex_distance(hex_c, sys.global_location)
            if dist < radius and dist < min_dist:
                min_dist = dist
                best_sys = sys
        return best_sys

    def find_nearest_system(self, hex_c: HexCoord) -> Optional["StarSystem"]:
        """Nearest system to `hex_c`, ignoring radius."""
        best_sys = None
        min_dist = float("inf")
        for sys in self._graph.systems.values():
            dist = hex_distance(hex_c, sys.global_location)
            if dist < min_dist:
                min_dist = dist
                best_sys = sys
        return best_sys

    def find_hybrid_path(
        self,
        start_hex: HexCoord,
        end_hex: HexCoord,
        fleet=None,
        can_warp: Optional[bool] = None,
    ) -> List[HexCoord]:
        """Combined deep-space + warp-network path."""
        if can_warp is not None:
            can_use_warp = can_warp
        elif fleet is not None:
            can_use_warp = fleet.capabilities.can_use_warp()
        else:
            can_use_warp = True

        start_sys = self.get_system_at_hex(start_hex)
        if not start_sys:
            start_sys = self.find_nearest_system(start_hex)
        end_sys = self.get_system_at_hex(end_hex)
        if not end_sys:
            end_sys = self.find_nearest_system(end_hex)

        # Same system -> deep space only.
        if start_sys and end_sys and start_sys == end_sys:
            return hex_linedraw(start_hex, end_hex)

        # Cannot warp -> direct hex path.
        if not can_use_warp:
            return hex_linedraw(start_hex, end_hex)

        # Interstellar with warp.
        if start_sys and end_sys:
            sys_path = self.find_path_interstellar(start_sys, end_sys)
            if not sys_path:
                return hex_linedraw(start_hex, end_hex)

            full_path: List[HexCoord] = []
            current_hex = start_hex

            for i in range(len(sys_path) - 1):
                curr_sys = sys_path[i]
                next_sys = sys_path[i + 1]

                target_wp = next(
                    (wp for wp in curr_sys.warp_points if wp.destination_id == next_sys.name),
                    None,
                )
                if target_wp:
                    wp_global = curr_sys.global_location + target_wp.location
                    segment = hex_linedraw(current_hex, wp_global)
                    if segment:
                        full_path.extend(segment)

                    arrival_wp = next(
                        (wp for wp in next_sys.warp_points if wp.destination_id == curr_sys.name),
                        None,
                    )
                    if arrival_wp:
                        arrival_global = next_sys.global_location + arrival_wp.location
                        full_path.append(arrival_global)
                        current_hex = arrival_global
                    else:
                        full_path.append(next_sys.global_location)
                        current_hex = next_sys.global_location

            final_segment = hex_linedraw(current_hex, end_hex)
            if final_segment:
                full_path.extend(final_segment)
            return full_path

        return hex_linedraw(start_hex, end_hex)
