import heapq
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
    return find_path_deep_space(start_hex, end_hex)

def project_fleet_path(fleet, galaxy, max_turns=10):
    """
    Simulate future fleet movement based on current speed and orders.
    Returns a list of segment dictionaries:
    {
        'start': HexCoord,
        'end': HexCoord (this is the 'hex' occupied at end of step),
        'turn': int (relative turn number, 0 = next turn),
        'is_warp': bool,
        'hex': HexCoord (alias for end)
    }
    """
    segments = []
    
    # Clone fleet state for simulation (path, location, orders)
    # We don't want to modify actual fleet
    sim_location = fleet.location
    sim_path = list(fleet.path) # Copy
    sim_orders = list(fleet.orders) # Copy
    
    moves_per_turn = int(fleet.speed)
    moves_left_in_turn = moves_per_turn
    current_turn = 0
    
    # Safety
    iterations = 0
    max_steps = max_turns * moves_per_turn
    
    # 1. Process active path first
    # 2. Then pop orders and generate new paths
    
    # We loop until path empty AND orders empty OR max turns reached
    while (sim_path or sim_orders) and current_turn < max_turns:
        iterations += 1
        if iterations > max_steps + 100: break # Safety brake
        
        # If no path but have orders, generate path
        if not sim_path and sim_orders:
            # Check if we need to pop an old order?
            # If path was empty to start with, sim_orders[0] is the active one if logic aligns with fleet.py
            # fleet.get_current_order() returns orders[0].
            # If fleet.path is empty, it means we either just finished an order or haven't started.
            
            # Logic: If we are here, we need a path for the *current* order.
            # If sim_orders[0] is MOVE, gen path.
            # If COLONIZE, it consumes no movement? Or consumes turn?
            # For visualization, we skip non-move orders or maybe mark them?
            # Let's assume non-move orders are instantaneous or consume 0 movement for this "path line" viz.
            
            order = sim_orders[0]
            if order.type != OrderType.MOVE:
                sim_orders.pop(0)
                continue
                
            # It is a MOVE order.
            # Generate path from sim_location to order.target
            target = order.target
            
            # Use hybrid path
            new_path_segment = find_hybrid_path(galaxy, sim_location, target)
            if new_path_segment:
                if new_path_segment and new_path_segment[0] == sim_location:
                    new_path_segment.pop(0)
                sim_path = new_path_segment
                # We do NOT pop order yet; we pop it when path finished.
            else:
                # Cannot reach? Abort
                break
                
        if not sim_path:
             break # No path and no orders left
             
        # Execute one step
        next_hex = sim_path.pop(0)
        
        # Check if Warp Jump
        # Detection: If distance > 1, it's a warp jump (teleport)
        is_warp = False
        if hex_distance(sim_location, next_hex) > 1:
            is_warp = True
            
        segment = {
            'start': sim_location,
            'end': next_hex,
            'hex': next_hex, # For convenience
            'turn': current_turn,
            'is_warp': is_warp
        }
        segments.append(segment)
        
        sim_location = next_hex
        
        # Cost Logic
        if not is_warp:
             moves_left_in_turn -= 1
        else:
             # Warp Jump cost?
             # Usually consumes movement?
             # Let's assume it costs 1 MP for entering/exiting warp
             moves_left_in_turn -= 1
             
        if moves_left_in_turn <= 0:
            current_turn += 1
            moves_left_in_turn = moves_per_turn
            
        # Check if Order Finished
        if not sim_path and sim_orders:
             # Just finished this order's path
             sim_orders.pop(0)
             
    return segments

def calculate_intercept_point(chaser_fleet, target_fleet, galaxy):
    """
    Calculate the optimal interception hex.
    
    Uses real path lengths (via find_hybrid_path) rather than straight-line
    distance to ensure the chaser takes an efficient route.
    
    Algorithm:
    1. Project target's future path.
    2. For each point on target's path, calculate how long chaser needs to get there.
    3. Find the earliest point where chaser_arrival_time <= target_arrival_time.
    4. If no intercept possible, chase the endpoint of target's path.
    """
    # Project target's future path
    target_path = project_fleet_path(target_fleet, galaxy, max_turns=50)
    
    chaser_speed = chaser_fleet.speed
    if chaser_speed <= 0:
        return target_fleet.location
    
    # Build list: [(hex, target_turn), ...]
    points_to_check = [{'hex': target_fleet.location, 'turn': 0}] + target_path
    
    best_intercept = None
    
    for pt in points_to_check:
        target_turn = pt['turn']
        target_hex = pt['hex']
        
        # Calculate REAL path length using hybrid pathfinding
        path_to_target = find_hybrid_path(galaxy, chaser_fleet.location, target_hex)
        
        if not path_to_target:
            # Can't reach this hex at all, skip
            continue
            
        # Path length is number of steps
        path_length = len(path_to_target)
        
        # Time for chaser = path_length / speed
        chaser_turns = path_length / chaser_speed
        
        # Can we intercept?
        if chaser_turns <= target_turn:
            # Found earliest intercept point
            return target_hex
            
        # Track as fallback if this is the closest we can get
        if best_intercept is None:
            best_intercept = target_hex
    
    # No intercept found on projected path - chase the endpoint
    if target_path:
        return target_path[-1]['hex']
        
    return best_intercept if best_intercept else target_fleet.location

