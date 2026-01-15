import random
from game.strategy.data.fleet import OrderType

class TurnEngine:
    def __init__(self):
        pass

    def process_turn(self, empires, galaxy):
        """
        Execute one full turn (100 sub-ticks).
        """
        # 1. Subturn Loop (Movement & Combat)
        for tick in range(1, 101):
            self._process_tick(tick, empires, galaxy)
            
        # 2. End-of-Turn Orders (Static actions like Colonize)
        for empire in empires:
            # Iterate copy since fleets might execute orders that change state? 
            # Actually colonization doesn't remove fleet usually, but we should be safe.
            for fleet in empire.fleets:
                self._process_end_turn_orders(fleet, empire, galaxy)
                
        # 3. Production Phase
        self.process_production(empires, galaxy)
        
    def process_production(self, empires, galaxy=None):
        """Process construction queues for all colonies."""
        for emp in empires:
            for colony in emp.colonies:
                if not colony.construction_queue:
                    continue
                    
                # Process first item
                item_data = colony.construction_queue[0]
                # Item is [name, turns]. We modify list in place.
                item_data[1] -= 1
                
                if item_data[1] <= 0:
                    # Completed!
                    item_name = item_data[0]
                    colony.construction_queue.pop(0)
                    print(f"Production Complete: {item_name} at {colony.planet_type.name}")
                    
                    # Spawn Logic
                    spawn_loc = colony.location
                    if galaxy:
                         # Expensive lookup, but needed until data structure improved
                         parent_sys = next((s for s in galaxy.systems.values() if colony in s.planets), None)
                         if parent_sys:
                             spawn_loc = parent_sys.global_location + colony.location
                    
                    # Create New Fleet
                    import random
                    from game.strategy.data.fleet import Fleet
                    
                    new_fleet = Fleet(random.randint(10000, 99999), emp.id, spawn_loc)
                    new_fleet.ships.append(item_name)
                    emp.add_fleet(new_fleet)

    def _process_tick(self, tick, empires, galaxy):
        """Process 1 sub-tick of movement and combat.
        
        Four-phase processing:
        Phase 0: Execute JOIN_FLEET for any co-located fleets (instant, no movement cost)
        Phase 1: Calculate paths/next moves for all fleets (based on current positions)
        Phase 2: Apply all movements simultaneously
        Phase 3: Combat
        """
        
        # --- Phase 0: Instant Orders (JOIN_FLEET) ---
        # Process JOIN_FLEET orders for any fleets that are already co-located with their target.
        # This happens every subtick so fleets can join as soon as they arrive.
        fleets_to_remove = []
        for empire in empires:
            for fleet in list(empire.fleets):  # Copy list since we may modify it
                order = fleet.get_current_order()
                if order and order.type == OrderType.JOIN_FLEET:
                    target_fleet = order.target
                    if target_fleet and hasattr(target_fleet, 'location'):
                        if fleet.location == target_fleet.location:
                            print(f"TurnEngine [Tick {tick}]: Fleet {fleet.id} merging into {target_fleet.id}")
                            fleet.merge_with(target_fleet)
                            fleets_to_remove.append((empire, fleet))
        
        # Remove merged fleets
        for empire, fleet in fleets_to_remove:
            empire.remove_fleet(fleet)
        
        # --- Phase 1: Calculate Moves ---
        # Collect (fleet, next_hex) pairs for all fleets that should move this tick
        move_queue = []
        
        for empire in empires:
            for fleet in empire.fleets:
                if fleet.speed <= 0: 
                    continue
                
                interval = int(100 // fleet.speed)
                if interval <= 0: 
                    interval = 1  # Safety
                
                if tick % interval == 0:
                    # Calculate next hex WITHOUT moving yet
                    next_hex = self._calculate_next_hex(fleet, galaxy)
                    if next_hex is not None:
                        move_queue.append((fleet, next_hex))
        
        # --- Phase 2: Apply Moves ---
        for fleet, next_hex in move_queue:
            fleet.location = next_hex
            
            # If path complete, order is done
            if not fleet.path:
                fleet.pop_order()

        # --- Phase 3: Combat ---
        self._resolve_conflicts(empires)

    def _calculate_next_hex(self, fleet, galaxy):
        """Calculate (but don't apply) the next hex for a fleet.
        
        Returns the next hex to move to, or None if no movement.
        Side effect: Updates fleet.path if needed.
        """
        order = fleet.get_current_order()
        if not order:
            return None

        destination = None
        
        if order.type == OrderType.MOVE:
            destination = order.target
        elif order.type == OrderType.MOVE_TO_FLEET:
            target_fleet = order.target
            if not target_fleet or not hasattr(target_fleet, 'location'):
                print(f"TurnEngine: Target fleet invalid. Order cancelled.")
                fleet.pop_order()
                return None
            
            # Use Predictive Intercept
            from game.strategy.data.pathfinding import calculate_intercept_point
            destination = calculate_intercept_point(fleet, target_fleet, galaxy)
        else:
            return None
            
        # Check for Re-Pathing (for Dynamic Targets)
        if fleet.path:
            current_dest = fleet.path[-1]
            if current_dest != destination:
                fleet.path = []  # Force recalc
            
        # Calculate path if needed
        if not fleet.path:
            from game.strategy.data.pathfinding import find_hybrid_path
            
            if fleet.location == destination:
                fleet.pop_order()
                return None

            fleet.path = find_hybrid_path(galaxy, fleet.location, destination)
            
            # Remove start hex if path begins with current location
            if fleet.path and fleet.path[0] == fleet.location:
                fleet.path.pop(0)
            
            if not fleet.path:
                if fleet.location != destination:
                    pass  # Retry next tick
                else: 
                    fleet.pop_order()
                return None

        if fleet.path:
            # Pop next hex from path (still part of calculation, applied in Phase 2)
            return fleet.path.pop(0)
        
        return None

    def _execute_move_step(self, fleet, galaxy):
        """Advance fleet 1 hex if it has a MOVE order and path."""
        order = fleet.get_current_order()
        if not order:
            return

        destination = None
        
        if order.type == OrderType.MOVE:
            destination = order.target
        elif order.type == OrderType.MOVE_TO_FLEET:
            target_fleet = order.target
            if not target_fleet or not hasattr(target_fleet, 'location'):
                print(f"TurnEngine: Target fleet invalid. Order cancelled.")
                fleet.pop_order()
                return
            
            # Use Predictive Intercept
            from game.strategy.data.pathfinding import calculate_intercept_point
            destination = calculate_intercept_point(fleet, target_fleet, galaxy)
            
        else:
            return
            
        # Check for Re-Pathing (for Dynamic Targets)
        # If we have a path but the destination has changed, clear path.
        if fleet.path:
            # Current path ends at...?
            # We don't store "target hex" in path easily, but path[-1] is the final step.
            # If our calculated intercept point changed, we must recalc.
            current_dest = fleet.path[-1]
            if current_dest != destination:
                fleet.path = [] # Force recalc
            
        # Check if we have a path. If not, calculate it.
        if not fleet.path:
            # Need pathfinding!
            # We need to import here to avoid circular dependencies if any, 
            # or move imports to top if safe. Pathfinding usually safe.
            from game.strategy.data.pathfinding import find_path_interstellar, find_path_deep_space, find_hybrid_path
            from game.strategy.data.hex_math import hex_distance
            
            # If already at destination?
            if fleet.location == destination:
                fleet.pop_order()
                return

            # Use Hybrid Pathfinding (Warp Point Aware)
            fleet.path = find_hybrid_path(galaxy, fleet.location, destination)
            
            # Remove start hex if path begins with current location
            if fleet.path and fleet.path[0] == fleet.location:
                fleet.path.pop(0)
            
            # If path still empty (unreachable or error?), pop order.
            if not fleet.path:
                # If we are adjacent or something? No, empty path usually means 0 steps needed or unreachable.
                # If pathfinding fails (unreachable), we should probably cancel.
                if fleet.location != destination:
                    # Retry next turn? or Cancel?
                    # For now, if moving to fleet, maybe it just jumped?
                    pass 
                else: 
                     fleet.pop_order()
                return

        if fleet.path:
            # Advance
            next_hex = fleet.path.pop(0)
            fleet.location = next_hex
            
            # If path complete, order is done
            if not fleet.path:
                fleet.pop_order()

    def _resolve_conflicts(self, empires):
        """Check for collisions and resolve battles."""
        # Map: Hex -> List[(Empire, Fleet)]
        hex_map = {}
        
        all_fleets = []
        for emp in empires:
            for f in emp.fleets:
                if f.location not in hex_map:
                    hex_map[f.location] = []
                hex_map[f.location].append((emp, f))
                
        # Check collisions
        for loc, occupants in hex_map.items():
            if len(occupants) < 2:
                continue
                
            # Check if multiple EMPIRES present
            occupied_empires = set(emp.id for emp, f in occupants)
            if len(occupied_empires) > 1:
                # CONFLICT!
                self._resolve_combat_at_hex(occupants)

    def _resolve_combat_at_hex(self, occupants):
        """Simple RNG resolution. Last standing empire wins."""
        # occupants: List[(Empire, Fleet)]
        
        # Group by Empire
        fleets_by_emp = {}
        for emp, f in occupants:
            if emp.id not in fleets_by_emp:
                fleets_by_emp[emp.id] = []
            fleets_by_emp[emp.id].append(f)
            
        # While > 1 empire has ships
        while len(fleets_by_emp) > 1:
            emp_ids = list(fleets_by_emp.keys())
            
            # Pick two random opposing fleets
            id1, id2 = random.sample(emp_ids, 2)
            f1 = fleets_by_emp[id1][0]
            f2 = fleets_by_emp[id2][0]
            
            # Roll
            survivor = self._resolve_combat(f1, f2)
            
            loser = f2 if survivor == f1 else f1
            loser_owner_id = loser.owner_id
            
            # Remove loser
            # 1. From list
            fleets_by_emp[loser_owner_id].remove(loser)
            if not fleets_by_emp[loser_owner_id]:
                del fleets_by_emp[loser_owner_id]
                
            # 2. From Empire (Global State)
            # We need reference to Empire object.
            # occupants has (Empire, Fleet). Find empire for loser.
            start_tuple = next(t for t in occupants if t[1] == loser)
            loser_empire = start_tuple[0]
            loser_empire.remove_fleet(loser)

    def _resolve_combat(self, f1, f2):
        """Return the winner of single encounter."""
        if random.random() > 0.5:
            return f1
        return f2

    def _process_end_turn_orders(self, fleet, empire, galaxy):
        """Process static orders like COLONIZE.
        
        Returns:
            True if fleet was consumed/deleted by the order, False otherwise.
        """
        order = fleet.get_current_order()
        if not order:
            return False
            
        if order.type == OrderType.COLONIZE:
            target_planet = order.target
            
            # 1. Identify valid candidates at current location
            valid_candidates = []
            
            # Find System (Optimized or Lookup)
            # We need the system to resolve global locations of its planets
            # Try direct lookup first (if at system center)
            system = galaxy.systems.get(fleet.location)
            
            if system:
                # Check planets in this system
                for p in system.planets:
                    if (system.global_location + p.location) == fleet.location:
                         if p.owner_id is None:
                             valid_candidates.append(p)
            else:
                # Brute force if fleet is not at system center (peripheral hex)
                # TODO: Add reverse lookup map if this is slow
                for sys in galaxy.systems.values():
                     # Optimization: Check distance? strict equality sufficient
                     # Check if any planet in this system matches location
                     for p in sys.planets:
                         if (sys.global_location + p.location) == fleet.location:
                              if p.owner_id is None:
                                  valid_candidates.append(p)
                                  
            # 2. Resolve target
            final_planet = None
            
            if target_planet is None:
                # "Any Planet": Pick first valid candidate
                if valid_candidates:
                    final_planet = valid_candidates[0]
                    print(f"TurnEngine: Deferred 'Any' colonization selected {final_planet.name}")
            else:
                # Specific Planet: Validate it is here and unowned
                if target_planet in valid_candidates:
                    final_planet = target_planet
                else:
                    # Validation Failed
                    # Why?
                    # A. Not here
                    # B. Owned
                    if target_planet.owner_id is not None:
                         print(f"TurnEngine: Colonize failed - {target_planet.name} is already owned.")
                    else:
                         # Check location mismatch
                         # We can't easily check global loc of target_planet without system ref, 
                         # but we know it wasn't in valid_candidates (which matched location).
                         print(f"TurnEngine: Colonize failed - {target_planet.name} not in sector {fleet.location}.")

            # 3. Execute
            if final_planet:
                empire.add_colony(final_planet)
                fleet.pop_order()
                empire.remove_fleet(fleet)
                print(f"TurnEngine: Colonization successful. {empire.name} claimed {final_planet.name}")
                return True
            else:
                # Failed / No Valid Target
                print("TurnEngine: Colonize order failed (Review logs). Order removed.")
                fleet.pop_order()

        elif order.type == OrderType.JOIN_FLEET:
            target_fleet = order.target
            
            # Validation
            if not target_fleet or not hasattr(target_fleet, 'location'):
                print("TurnEngine: Join Fleet failed - Target invalid/destroyed.")
                fleet.pop_order()
                return False
                
            if fleet.location == target_fleet.location:
                print(f"TurnEngine: Fleet {fleet.id} merging into {target_fleet.id}")
                fleet.merge_with(target_fleet)
                # Remove self from empire
                empire.remove_fleet(fleet)
                return True
            else:
                # Not at location yet? Should have arrived if move order preceded this.
                # If we rely on Move order finishing exactly at location, handling leftovers is tricky.
                # But typically Join follows Move. If Move finished, we are there.
                print("TurnEngine: Join Fleet failed - Not at same location.")
                fleet.pop_order() # Cancel join if we aren't there? Or wait? 
                # If we are not there, and have no move order, we are stuck.
                # Better to cancel.
                
        return False

