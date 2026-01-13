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
        """Process 1 sub-tick of movement and combat."""
        
        # --- A. Movement ---
        for empire in empires:
            # Iterate backwards or copy? Fleet death might happen in combat step later.
            # Movement happens BEFORE combat check in this tick.
            for fleet in empire.fleets:
                if fleet.speed <= 0: continue
                
                interval = int(100 // fleet.speed)
                if interval <= 0: interval = 1 # Safety
                
                if tick % interval == 0:
                    self._execute_move_step(fleet, galaxy)

        # --- B. Combat ---
        self._resolve_conflicts(empires)

    def _execute_move_step(self, fleet, galaxy):
        """Advance fleet 1 hex if it has a MOVE order and path."""
        order = fleet.get_current_order()
        if not order or order.type != OrderType.MOVE:
            return
            
        # Check if we have a path. If not, calculate it.
        # This handles:
        # 1. New orders popped from queue
        # 2. Path recalculation if needed (future)
        if not fleet.path:
            # Need pathfinding!
            # We need to import here to avoid circular dependencies if any, 
            # or move imports to top if safe. Pathfinding usually safe.
            from game.strategy.data.pathfinding import find_path_interstellar, find_path_deep_space, find_hybrid_path
            from game.strategy.data.hex_math import hex_distance
            
            # Use Hybrid Pathfinding (Warp Point Aware)
            fleet.path = find_hybrid_path(galaxy, fleet.location, order.target)
            
            # If path still empty (already at target?), pop order.
            if not fleet.path:
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
            planet = order.target
            
            # Resolve "Any Planet" (None target)
            if planet is None:
                # Find unowned planet at current location
                # Global lookup
                system = galaxy.systems.get(fleet.location)
                
                # If not at system center, maybe at planet offset? 
                # Simplification: Colonize must be AT system or planet.
                # If system is found at fleet.location (center hex):
                if system:
                    # Check ALL planets in system (assuming abstract 'in system' range)
                    # OR check if we have to be at specific hex?
                    # StrategyScene defaults to 'target_hex' which might be specific planet hex.
                    # BUT if we moved to a specific hex, we are there.
                    
                    # 1. Check planets strictly at this hex
                    local_candidates = []
                    # System center is 0,0 relative.
                    # Planets have relative locations.
                    # Fleet location is global.
                    
                    # If we are at system center, can we colonize any? Usually yes in simple 4X.
                    # But let's check strict location first.
                    
                    # Iterate all planets in system
                    for p in system.planets:
                        p_global = system.global_location + p.location
                        if p_global == fleet.location and p.owner_id is None:
                            local_candidates.append(p)
                            
                    # If no local matches, check if we are simply "In System" 
                    # (Allow colonizing from center star hex?) -> User preference?
                    # For now: strict location. If "Any" was picked for a multi-planet sector,
                    # the fleet moved to that sector (hex). So planets should be there.
                    
                    if local_candidates:
                        # Pick first (or random?)
                        planet = local_candidates[0]
                        print(f"TurnEngine: Deferred colonization selected {planet.name}")
                    else:
                        print(f"TurnEngine: No valid planets found at {fleet.location} for deferred colonize.")
                else: 
                     # Maybe fleet is at a peripheral hex that IS a planet location?
                     # We need to find the system this hex belongs to.
                     # Galaxy doesn't have reverse lookup easily?
                     # Using brute force for now (fast enough for 80 systems)
                     for sys in galaxy.systems.values():
                         found = False
                         for p in sys.planets:
                             if sys.global_location + p.location == fleet.location:
                                 if p.owner_id is None:
                                     planet = p
                                     found = True
                                     print(f"TurnEngine: Deferred colonization resolved {planet.name} in {sys.name}")
                                     break
                         if found: break
            
            # Execute colonization
            if planet:
                # Verify ownership again just in case (race condition double check)
                if planet.owner_id is not None:
                    print(f"TurnEngine: Colonization failed. {planet.name} is already owned.")
                    # Abort order? Keep trying? 
                    # For now, consume order to prevent infinite loop.
                    fleet.pop_order()
                    return False
                    
                empire.add_colony(planet)
                fleet.pop_order()
                
                # Colonizing ship is consumed to create the colony
                empire.remove_fleet(fleet)
                print(f"TurnEngine: Colonization successful. {empire.name} claimed {planet.name}")
                return True
            else:
                print("TurnEngine: Colonization skipped (No valid target).")
                # Don't pop order? Retry next turn? 
                # Or pop to avoid stuck fleet? 
                # Pop it.
                fleet.pop_order()
        
        return False

