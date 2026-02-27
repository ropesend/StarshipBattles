import heapq
import logging
from typing import List, Union, Optional, TYPE_CHECKING

from game.core.hex_math import hex_distance, hex_linedraw, HexCoord
from game.strategy.data.fleet import OrderType

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.galaxy import Galaxy, StarSystem
    from game.strategy.services.fleet_navigation_service import NavigationState

def find_path_deep_space(start: HexCoord, end: HexCoord) -> List[HexCoord]:
    """
    Find path in deep space (no obstacles).

    Args:
        start: Starting hex coordinate.
        end: Destination hex coordinate.

    Returns:
        List of HexCoords forming the path from start to end.
    """
    return hex_linedraw(start, end)

def find_path_interstellar(
    start_system: 'StarSystem',
    end_system: 'StarSystem',
    galaxy: 'Galaxy'
) -> Optional[List['StarSystem']]:
    """
    Find path between systems using Warp Lanes (A*).

    Args:
        start_system: Starting StarSystem object.
        end_system: Destination StarSystem object.
        galaxy: Galaxy object containing all systems and warp lanes.

    Returns:
        List of StarSystem objects representing the route, or None if no path exists.
    """
    if start_system == end_system:
        return [start_system]
        
    # Priority Queue: (cost, system_name)
    # We store system name to handle dictionary lookups easily
    queue = [(0, start_system.name)]
    came_from = {start_system.name: None}
    cost_so_far = {start_system.name: 0}
    
    while queue:
        current_cost, current_name = heapq.heappop(queue)
        current_sys = galaxy.systems[galaxy.get_system_by_name(current_name).global_location] 
        # Wait, galaxy.systems is keyed by location.
        # We need a name lookup or pass the object map differently.
        # Let's assume we can get system object.
        
        # Optimization: Build name_to_system cache or linear search?
        # Galaxy doesn't have name index by default.
        # StrategyScreen probably needs to build one or we iterate.
        # For now, let's assume galaxy has a helper or we search.
        # Actually start_system AND end_system are passed as objects.
        # We can iterate neighbors via warp points.
        
        if current_name == end_system.name:
            break
            
        current_sys = galaxy.get_system_by_name(current_name)
        if not current_sys:
            continue
            
        for wp in current_sys.warp_points:
            next_name = wp.destination_id
            
            # Cost is distance? Or just +1 hop?
            # User said "map exists... massive scale".
            # Usually travel time depends on warp lane length.
            # Let's use hex_distance between systems as G-cost?
            # Or fixed cost per jump? Let's use distance for realism.
            
            next_sys = galaxy.get_system_by_name(next_name)
            if not next_sys:
               continue
               
            dist = hex_distance(current_sys.global_location, next_sys.global_location)
            new_cost = cost_so_far[current_name] + dist
            
            if next_name not in cost_so_far or new_cost < cost_so_far[next_name]:
                cost_so_far[next_name] = new_cost
                priority = new_cost + hex_distance(next_sys.global_location, end_system.global_location)
                heapq.heappush(queue, (priority, next_name))
                came_from[next_name] = current_name
                
    # Reconstruct path
    if end_system.name not in came_from:
        return None # No path
        
    path = []
    curr = end_system.name
    while curr != start_system.name:
        path.append(galaxy.get_system_by_name(curr))
        curr = came_from[curr]
    path.append(start_system)
    path.reverse()
    return path

def get_system_at_hex(
    galaxy: 'Galaxy',
    hex_c: HexCoord,
    radius: int = 50
) -> Optional['StarSystem']:
    """
    Find which system implies ownership of this hex.

    Uses a simplistic radius check - returns the nearest system within radius.

    Args:
        galaxy: Galaxy containing all star systems.
        hex_c: Hex coordinate to check.
        radius: Maximum distance to search for a system (default 50).

    Returns:
        The nearest StarSystem within radius, or None if none found.
    """
    # Fast path: O(1) exact match
    if hex_c in galaxy.systems:
        return galaxy.systems[hex_c]
    
    # Slow path: radius search for nearby systems
    best_sys = None
    min_dist = float('inf')
    
    for sys in galaxy.systems.values():
        dist = hex_distance(hex_c, sys.global_location)
        if dist < radius:
            if dist < min_dist:
                min_dist = dist
                best_sys = sys
    return best_sys

def find_nearest_system(galaxy: 'Galaxy', hex_c: HexCoord) -> Optional['StarSystem']:
    """
    Find the nearest system to a hex coordinate (ignoring radius).

    Args:
        galaxy: Galaxy containing all star systems.
        hex_c: Hex coordinate to find nearest system to.

    Returns:
        The nearest StarSystem, or None if galaxy has no systems.
    """
    best_sys = None
    min_dist = float('inf')
    
    for sys in galaxy.systems.values():
        dist = hex_distance(hex_c, sys.global_location)
        if dist < min_dist:
            min_dist = dist
            best_sys = sys
    return best_sys

def find_hybrid_path(galaxy, start_hex, end_hex, fleet=None):
    """
    Calculate path combining local hex movement and interstellar warp jumps.

    Args:
        galaxy: Galaxy object containing star systems and warp points
        start_hex: Starting HexCoord
        end_hex: Destination HexCoord
        fleet: Optional Fleet object. If provided and fleet cannot use warp,
               falls back to direct hex path (no warp network).

    Returns:
        List of HexCoords representing the path.
    """
    # Check if fleet can use warp points
    can_use_warp = True
    if fleet is not None:
        can_use_warp = fleet.can_use_warp()
        logger.debug(f"find_hybrid_path: fleet={fleet.id}, can_use_warp={can_use_warp}")

    # 1. Identify Start/End Systems
    # If in deep space, find NEAREST system to enter/exit the network.
    start_sys = get_system_at_hex(galaxy, start_hex)
    if not start_sys:
        start_sys = find_nearest_system(galaxy, start_hex)

    end_sys = get_system_at_hex(galaxy, end_hex)
    if not end_sys:
        end_sys = find_nearest_system(galaxy, end_hex)

    # Case A: Same System (or both Deep Space near same system)
    if start_sys and end_sys and start_sys == end_sys:
        return find_path_deep_space(start_hex, end_hex)

    # Case B: Fleet cannot warp - use direct hex path
    if not can_use_warp:
        return find_path_deep_space(start_hex, end_hex)

    # Case C: Interstellar with warp capability
    if start_sys and end_sys:
        # 1. Find System Path
        sys_path = find_path_interstellar(start_sys, end_sys, galaxy)
        if not sys_path:
            # If no system path possible (disconnected graph?), fallback to direct
            return find_path_deep_space(start_hex, end_hex)
            
        full_path = []
        current_hex = start_hex
        
        # Iterate through system path to connect warp points
        # sys_path is [StartSys, NextSys, ..., EndSys]
        
        for i in range(len(sys_path) - 1):
            curr_sys = sys_path[i]
            next_sys = sys_path[i+1]
            
            # Find Warp Point in curr_sys connecting to next_sys
            target_wp = next((wp for wp in curr_sys.warp_points if wp.destination_id == next_sys.name), None)
            
            if target_wp:
                # Calculate WP Global Hex
                wp_global = curr_sys.global_location + target_wp.location
                
                # Local Path to WP
                segment = find_path_deep_space(current_hex, wp_global)
                if segment:
                    full_path.extend(segment)
                
                # "Jump" to reciprocal WP (simulated by appending arrival hex)
                # Need to find arrival WP in next_sys
                arrival_wp = next((wp for wp in next_sys.warp_points if wp.destination_id == curr_sys.name), None)
                if arrival_wp:
                    arrival_global = next_sys.global_location + arrival_wp.location
                    full_path.append(arrival_global) # The jump
                    current_hex = arrival_global
                else:
                    # Fallback if reciprocal WP missing (data error?): Jump to system center?
                    # or just continue from current (broken link)
                    # Let's assume jump to center
                    full_path.append(next_sys.global_location)
                    current_hex = next_sys.global_location
        
        # Final Leg: From last arrival point to specific end_hex
        final_segment = find_path_deep_space(current_hex, end_hex)
        if final_segment:
            full_path.extend(final_segment)
        
        return full_path
        
    # Fallback: Just direct line (Deep Space logic)
    return find_path_deep_space(start_hex, end_hex)

def project_fleet_path(fleet, galaxy, max_turns=10):
    """
    Simulate future fleet movement based on current speed and orders.

    Delegates to FleetNavigationService for consistent movement logic.
    (PROJ-35: Migrated from FleetMovementSimulator to unified service)

    Returns a list of segment dictionaries:
    {
        'start': HexCoord,
        'end': HexCoord (this is the 'hex' occupied at end of step),
        'turn': int (relative turn number, 0 = next turn),
        'is_warp': bool,
        'hex': HexCoord (alias for end)
    }
    """
    from game.strategy.services.fleet_navigation_service import FleetNavigationService

    service = FleetNavigationService()
    return service.project_path_as_dicts(fleet, galaxy, max_turns)

class _ChaserProxy:
    """Adapter for find_hybrid_path that provides fleet-like interface.

    This adapter normalizes Fleet and NavigationState objects to provide
    the minimal interface needed by find_hybrid_path():
    - id: Fleet identifier for logging
    - can_use_warp(): Warp capability check

    This is an intentional adapter pattern (not legacy compatibility) that
    allows pure NavigationState objects to be used with pathfinding functions
    that expect Fleet-like objects.

    PROJ-42: Reviewed and kept as proper adapter pattern.
    """

    def __init__(self, can_warp: bool, fleet_id):
        self._can_warp = can_warp
        self.id = fleet_id

    def can_use_warp(self) -> bool:
        return self._can_warp


def _extract_chaser_info(chaser: Union['Fleet', 'NavigationState']) -> tuple:
    """
    Extract location, speed, ID, and warp capability from chaser.

    Args:
        chaser: Fleet or NavigationState object.

    Returns:
        Tuple of (location, speed, id, can_warp).
    """
    from game.strategy.services.fleet_navigation_service import NavigationState

    if isinstance(chaser, NavigationState):
        return (chaser.location, chaser.speed, -1, chaser.can_warp)
    else:
        # Fleet always has id
        return (
            chaser.location,
            chaser.speed,
            chaser.id,
            chaser.can_use_warp()
        )


def _evaluate_intercept_candidates(
    points_to_check: list,
    chaser_location: HexCoord,
    chaser_speed: float,
    chaser_proxy: _ChaserProxy,
    galaxy
) -> tuple:
    """
    Evaluate intercept candidates and find optimal intercept point.

    Args:
        points_to_check: List of dicts with 'hex' and 'turn' keys.
        chaser_location: Chaser's starting position.
        chaser_speed: Chaser's movement speed.
        chaser_proxy: Proxy with warp capability info.
        galaxy: Galaxy for pathfinding.

    Returns:
        Tuple of (best_intercept, best_intercept_time, best_target_turn, fallback_hex).
    """
    best_intercept = None
    best_intercept_time = float('inf')
    best_target_turn = None
    fallback_hex = None

    for pt in points_to_check:
        target_turn = pt['turn']
        target_hex = pt['hex']

        path_to_target = find_hybrid_path(galaxy, chaser_location, target_hex, fleet=chaser_proxy)

        if not path_to_target:
            continue

        path_length = max(0, len(path_to_target) - 1)
        chaser_turns = path_length / chaser_speed

        # Chaser can intercept if arrives before or during target's turn at that hex
        if chaser_turns < target_turn + 1:
            if chaser_turns < best_intercept_time:
                best_intercept_time = chaser_turns
                best_intercept = target_hex
                best_target_turn = target_turn

                # Early exit if perfectly synchronized
                if abs(chaser_turns - target_turn) < 0.1:
                    break
        else:
            if fallback_hex is None:
                fallback_hex = target_hex

        # Early exit if clearly past optimal point
        if best_intercept is not None and target_turn > best_intercept_time + 3:
            break

    return (best_intercept, best_intercept_time, best_target_turn, fallback_hex)


def calculate_intercept_point(
    chaser: Union['Fleet', 'NavigationState'],
    target_fleet,
    galaxy
) -> Optional[HexCoord]:
    """
    Calculate the optimal interception hex for a chaser pursuing a target.

    Uses real path lengths (via find_hybrid_path) rather than straight-line
    distance to ensure the chaser takes an efficient route through warp lanes.

    Args:
        chaser: Fleet or NavigationState representing the pursuing fleet.
                Supports both types for caller convenience and pure function usage.
        target_fleet: Fleet object being pursued.
        galaxy: Galaxy object for pathfinding context.

    Returns:
        HexCoord of the optimal interception point, or target's current location
        if interception is impossible.

    Algorithm:
        1. Project target's future path over 50 turns.
        2. For each point on target's path, calculate chaser's travel time
           using hybrid pathfinding (respects warp lanes).
        3. Find the earliest point where chaser arrives before target leaves
           (chaser_turns < target_turn + 1).
        4. Early exit on perfect synchronization (arrival times match within 0.1 turns).
        5. If no intercept possible, chase the endpoint of target's path.
    """
    # Extract chaser properties
    chaser_location, chaser_speed, chaser_id, chaser_can_warp = _extract_chaser_info(chaser)
    chaser_proxy = _ChaserProxy(chaser_can_warp, chaser_id)

    # Fleet always has id
    logger.debug(f"Intercept: chaser={chaser_id} @ {chaser_location} (speed={chaser_speed}) -> "
              f"target={target_fleet.id} @ {target_fleet.location}")

    # Handle zero/negative speed
    if chaser_speed <= 0:
        return target_fleet.location

    # Project target's future path
    target_path = project_fleet_path(target_fleet, galaxy, max_turns=50)

    # Build candidate list
    if target_path:
        points_to_check = target_path
    else:
        points_to_check = [{'hex': target_fleet.location, 'turn': 0}]

    # Find optimal intercept
    best_intercept, best_time, best_turn, fallback = _evaluate_intercept_candidates(
        points_to_check, chaser_location, chaser_speed, chaser_proxy, galaxy
    )

    # Determine result
    if best_intercept is not None:
        logger.debug(f"Intercept selected: {best_intercept} (chaser arrives turn {best_time:.1f}, "
                  f"target at hex turn {best_turn})")
        return best_intercept
    elif target_path:
        result = target_path[-1]['hex']
        logger.debug(f"No intercept possible - chasing endpoint: {result}")
        return result
    else:
        result = fallback if fallback else target_fleet.location
        logger.debug(f"Intercept fallback: {result}")
        return result

