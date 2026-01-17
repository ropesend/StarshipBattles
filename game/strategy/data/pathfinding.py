import heapq
from game.core.logger import log_error, log_info, log_warning, log_debug
from game.strategy.data.hex_math import hex_distance, hex_linedraw
from game.strategy.data.fleet import OrderType

def find_path_deep_space(start, end):
    """
    Find path in deep space (no obstacles).
    Returns list of HexCoords.
    """
    return hex_linedraw(start, end)

def find_path_interstellar(start_system, end_system, galaxy):
    """
    Find path between systems using Warp Lanes (A*).
    start_system: StarSystem object
    end_system: StarSystem object
    galaxy: Galaxy object
    
    Returns: List of StarSystem objects (the route).
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
        # StrategyScene probably needs to build one or we iterate.
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

def get_system_at_hex(galaxy, hex_c, radius=50):
    """Find which system implies ownership of this hex (simplistic radius check)."""
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

def find_nearest_system(galaxy, hex_c):
    """Find the nearest system to a hex coordinate (ignoring radius)."""
    best_sys = None
    min_dist = float('inf')
    
    for sys in galaxy.systems.values():
        dist = hex_distance(hex_c, sys.global_location)
        if dist < min_dist:
            min_dist = dist
            best_sys = sys
    return best_sys

def find_hybrid_path(galaxy, start_hex, end_hex):
    """
    Calculate path combining local hex movement and interstellar warp jumps.
    Returns list of HexCoords.
    """
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
        
    # Case B: Interstellar
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
    
    Delegates to FleetMovementSimulator for consistent movement logic.
    
    Returns a list of segment dictionaries:
    {
        'start': HexCoord,
        'end': HexCoord (this is the 'hex' occupied at end of step),
        'turn': int (relative turn number, 0 = next turn),
        'is_warp': bool,
        'hex': HexCoord (alias for end)
    }
    """
    from game.strategy.engine.fleet_movement import FleetMovementSimulator
    
    simulator = FleetMovementSimulator()
    return simulator.project_path_as_dicts(fleet, galaxy, max_turns)

def calculate_intercept_point(chaser_fleet, target_fleet, galaxy):
    """
    Calculate the optimal interception hex.
    
    Uses real path lengths (via find_hybrid_path) rather than straight-line
    distance to ensure the chaser takes an efficient route.
    
    Algorithm:
    1. Project target's future path.
    2. For each point on target's path, calculate how long chaser needs to get there.
    3. Find the point with MINIMUM chaser arrival time where chaser_turns < target_turn + 1.
    4. Early exit if we find a perfect intercept (chaser arrives in <= 1 turn).
    5. If no intercept possible, chase the endpoint of target's path.
    """
    # Log header
    log_debug("=" * 60)
    log_debug("INTERCEPT CALCULATION")
    log_debug("=" * 60)
    log_debug(f"Chaser Fleet ID: {getattr(chaser_fleet, 'id', 'unknown')}")
    log_debug(f"  Location: {chaser_fleet.location}")
    log_debug(f"  Speed: {chaser_fleet.speed}")
    log_debug(f"Target Fleet ID: {getattr(target_fleet, 'id', 'unknown')}")
    log_debug(f"  Location: {target_fleet.location}")
    log_debug(f"  Speed: {getattr(target_fleet, 'speed', 'unknown')}")
    
    # Project target's future path
    target_path = project_fleet_path(target_fleet, galaxy, max_turns=50)
    
    log_debug(f"Target Projected Path ({len(target_path)} segments):")
    for i, seg in enumerate(target_path[:15]):  # Log first 15
        log_debug(f"  [{i}] Turn {seg['turn']}: {seg['hex']}")
    if len(target_path) > 15:
        log_debug(f"  ... ({len(target_path) - 15} more)")
    
    chaser_speed = chaser_fleet.speed
    if chaser_speed <= 0:
        log_debug("ERROR: Chaser speed <= 0, returning target location")
        return target_fleet.location
    
    # Build list of intercept candidates
    if target_path:
        points_to_check = target_path
        log_debug("Target is MOVING - using projected path only")
    else:
        points_to_check = [{'hex': target_fleet.location, 'turn': 0}]
        log_debug("Target is STATIONARY - using current location")
    
    best_intercept = None
    best_intercept_time = float('inf')
    best_target_turn = None
    fallback_hex = None
    
    log_debug("Evaluating intercept candidates:")
    
    for i, pt in enumerate(points_to_check):
        target_turn = pt['turn']
        target_hex = pt['hex']
        
        # Calculate REAL path length using hybrid pathfinding
        path_to_target = find_hybrid_path(galaxy, chaser_fleet.location, target_hex)
        
        if not path_to_target:
            log_debug(f"  [{i}] {target_hex} @ T{target_turn}: UNREACHABLE")
            continue
            
        path_length = max(0, len(path_to_target) - 1)
        chaser_turns = path_length / chaser_speed
        
        # Condition: chaser_turns < target_turn + 1
        valid = chaser_turns < target_turn + 1
        
        log_debug(f"  [{i}] {target_hex} @ T{target_turn}: path={path_length} steps, "
            f"chaser_time={chaser_turns:.2f} turns, valid={valid}")
        
        if valid:
            if chaser_turns < best_intercept_time:
                best_intercept_time = chaser_turns
                best_intercept = target_hex
                best_target_turn = target_turn
                log_debug("      -> NEW BEST INTERCEPT")
                
                # Early exit ONLY if chaser would arrive at the SAME subtick as target
                # (i.e., chaser_turns matches target_turn closely)
                if abs(chaser_turns - target_turn) < 0.1:
                    log_debug("      -> EARLY EXIT (perfectly synchronized)")
                    break
        else:
            if fallback_hex is None:
                fallback_hex = target_hex
                
        # Early exit if we've clearly passed the optimal point
        if best_intercept is not None and target_turn > best_intercept_time + 3:
            log_debug("      -> EARLY EXIT (target_turn >> best_time)")
            break
    
    # Determine result
    if best_intercept is not None:
        result = best_intercept
        log_debug(f">>> SELECTED INTERCEPT: {result}")
        log_debug(f"    Chaser arrives in {best_intercept_time:.2f} turns")
        log_debug(f"    Target at hex during turn {best_target_turn}")
        
        # Cross-verification: simulate chaser path to verify
        chaser_path = find_hybrid_path(galaxy, chaser_fleet.location, result)
        if chaser_path:
            log_debug("--- CROSS-VERIFICATION ---")
            chaser_path_len = len(chaser_path) - 1
            chaser_subticks_total = int(chaser_path_len * (100 / chaser_speed))
            chaser_arrival_turn = chaser_subticks_total // 100
            chaser_arrival_subtick = chaser_subticks_total % 100
            log_debug(f"Chaser path length: {chaser_path_len} steps")
            log_debug(f"Chaser subticks: {chaser_subticks_total} (Turn {chaser_arrival_turn}, Subtick {chaser_arrival_subtick})")
            
            # Find when target is at intercept hex
            target_at_intercept = None
            for seg in target_path:
                if seg['hex'] == result:
                    target_at_intercept = seg
                    break
            
            if target_at_intercept:
                target_turn_at_intercept = target_at_intercept['turn']
                log_debug(f"Target at intercept hex during turn: {target_turn_at_intercept}")
                
                # Check if they actually meet
                if chaser_arrival_turn <= target_turn_at_intercept:
                    log_debug(f"VERIFIED: Chaser arrives Turn {chaser_arrival_turn} <= Target there Turn {target_turn_at_intercept}")
                else:
                    log_debug(f"*** MISMATCH! Chaser Turn {chaser_arrival_turn} > Target leaves after Turn {target_turn_at_intercept} ***")
            else:
                log_debug("WARNING: Could not find intercept hex in target path")
    elif target_path:
        result = target_path[-1]['hex']
        log_debug(f">>> NO INTERCEPT FOUND - chasing endpoint: {result}")
    else:
        result = fallback_hex if fallback_hex else target_fleet.location
        log_debug(f">>> FALLBACK: {result}")
    
    log_debug("=" * 60)
    
    return result

