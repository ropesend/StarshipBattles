import heapq
from game.strategy.data.hex_math import hex_distance, hex_linedraw

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
