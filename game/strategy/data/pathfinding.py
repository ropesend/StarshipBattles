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
