from components import ComponentStatus, LayerType, Engine, Thruster, Generator, Tank, Armor, Shield, ShieldRegenerator, Weapon, Bridge, Hangar
import math

class ShipStatsCalculator:
    """
    Encapsulates the logic for calculating ship statistics from its components.
    """
    def __init__(self, vehicle_classes):
        self.vehicle_classes = vehicle_classes

    def calculate(self, ship):
        """
        Recalculates all derived stats for the ship based on its components and class.
        """
        # Import local to avoid circular dep if needed, or top level if safe.
        # resources.py likely imports NOTHING from ship_stats.
        from resources import ResourceStorage, ResourceGeneration

        # 1. Reset Base Calculations
        ship.current_mass = 0
        ship.layer_status = {}
        ship.mass_limits_ok = True
        ship.drag = 0.5 
        
        # Calculate Mass (Mass never changes due to damage/status in this model, dead weight remains)
        for layer_type, layer_data in ship.layers.items():
            l_mass = sum(c.mass for c in layer_data['components'])
            layer_data['mass'] = l_mass
            ship.current_mass += l_mass
            
        ship.mass = ship.current_mass + ship.base_mass

        # Base Stats Reset
        ship.total_thrust = 0
        ship.turn_speed = 0
        if hasattr(ship, 'resources'):
            ship.resources.reset_stats()
            
        ship.max_shields = 0
        ship.shield_regen_rate = 0
        ship.shield_regen_rate = 0
        ship.shield_regen_cost = 0
        ship.repair_rate = 0
        if LayerType.ARMOR in ship.layers:
            ship.layers[LayerType.ARMOR]['max_hp_pool'] = 0
            
        ship.emissive_armor = 0
        ship.crystalline_armor = 0
        
        # Maneuvering Points (Raw Thrust/Turning Capability unrelated to mass)
        ship.total_maneuver_points = 0
        
        # Hangar Stats
        ship.fighter_capacity = 0
        ship.fighters_per_wave = 0
        ship.fighter_size_cap = 0
        ship.launch_cycle = 0
        
        # 2. Phase 1: Damage Check & Resource Supply Gathering
        # ----------------------------------------------------
        available_crew = 0     # From Crew Quarters
        available_life_support = 0 # From Life Support
        
        component_pool = [] # List of (comp) for next phases
        
        for layer_type, layer_data in ship.layers.items():
            for comp in layer_data['components']:
                # Reset Status Assumption
                comp.is_active = True
                comp.status = ComponentStatus.ACTIVE
                
                # Check Damage Threshold (ignore Armor)
                if not isinstance(comp, Armor):
                     if comp.max_hp > 0 and (comp.current_hp / comp.max_hp) <= 0.5:
                         comp.is_active = False
                         comp.status = ComponentStatus.DAMAGED
                
                # If armor is dead (0 hp), it's inactive
                if isinstance(comp, Armor) and comp.current_hp <= 0:
                    comp.is_active = False
                    comp.status = ComponentStatus.DAMAGED
                
                # Gather Supply from FUNCTIONAL components
                if comp.is_active:
                    abilities = comp.abilities
                    # Crew Provided (Positive CrewCapacity)
                    c_cap = abilities.get('CrewCapacity', 0)
                    if c_cap > 0:
                        available_crew += c_cap
                        
                    # Life Support Provided
                    ls_cap = abilities.get('LifeSupportCapacity', 0)
                    if ls_cap > 0:
                        available_life_support += ls_cap

                component_pool.append(comp)

        # 3. Phase 2: Resource Allocation (Crew & Life Support)
        # -----------------------------------------------------
        # Store for UI
        ship.crew_onboard = available_crew
        ship.crew_required = 0
        ship.max_targets = 1 # Reset to default
        
        # Effective Crew is limited by Life Support
        effective_crew = min(available_crew, available_life_support)
        
        # Priority sort using helper
        component_pool.sort(key=self._priority_sort_key)
        
        for comp in component_pool:
            if not comp.is_active: continue # Already damaged
            
            # Check Crew Requirement (Use positive CrewRequired)
            req_crew = comp.abilities.get('CrewRequired', 0)
            
            # Satellite Exception: Satellites ignore crew requirements
            if ship.vehicle_type == "Satellite":
                req_crew = 0
            
            # Legacy fallback: Check for negative CrewCapacity if CrewRequired missing
            if req_crew == 0:
                 req_crew = abs(min(0, comp.abilities.get('CrewCapacity', 0)))

            ship.crew_required += req_crew
            
            if req_crew > 0:
                if effective_crew >= req_crew:
                    effective_crew -= req_crew
                else:
                    comp.is_active = False
                    comp.status = ComponentStatus.NO_CREW
        
        # 4. Phase 3: Stats Aggregation (Active Components Only)
        # ------------------------------------------------------
        
        # Local accumulators for atomic updates (prevents premature clamping)
        total_max_fuel = 0
        total_max_ammo = 0
        total_max_energy = 0
        total_energy_gen = 0
        total_ammo_gen = 0
        total_thrust = 0
        total_turn_speed = 0
        total_max_shields = 0
        total_shield_regen = 0
        total_shield_cost = 0

        for comp in component_pool:
            if not comp.is_active: continue
            
            # Generic Ability Handling
            # Using Ability Instances (New System)
            if hasattr(comp, 'ability_instances'):
                for ability in comp.ability_instances:
                    # Resource Storage
                    if isinstance(ability, ResourceStorage):
                        if ability.resource_type == 'fuel':
                            total_max_fuel += ability.max_amount
                        elif ability.resource_type == 'ammo':
                            total_max_ammo += ability.max_amount
                        elif ability.resource_type == 'energy':
                            total_max_energy += ability.max_amount
                    
                    # Resource Generation
                    elif isinstance(ability, ResourceGeneration):
                        if ability.resource_type == 'energy':
                            total_energy_gen += ability.rate
                        elif ability.resource_type == 'ammo':
                            total_ammo_gen += ability.rate
            
            # Legacy / Specific Hardware Checks
            if isinstance(comp, Engine):
                total_thrust += comp.thrust_force
            elif isinstance(comp, Thruster):
                total_turn_speed += comp.turn_speed
                ship.total_maneuver_points += comp.turn_speed
            elif isinstance(comp, Armor):
                if LayerType.ARMOR in ship.layers:
                    ship.layers[LayerType.ARMOR]['max_hp_pool'] += comp.max_hp
            elif isinstance(comp, Shield):
                total_max_shields += comp.shield_capacity
            elif isinstance(comp, ShieldRegenerator):
                total_shield_regen += comp.regen_rate
                # Find energy cost from ability
                from resources import ResourceConsumption
                for ab in comp.ability_instances:
                    if isinstance(ab, ResourceConsumption) and ab.resource_name == 'energy':
                         total_shield_cost += ab.amount
                         break
            elif isinstance(comp, Hangar):
                ship.fighter_capacity += comp.storage_capacity
                ship.fighters_per_wave += 1
                if comp.max_launch_mass > ship.fighter_size_cap:
                    ship.fighter_size_cap = comp.max_launch_mass
                    
                if comp.cycle_time > ship.launch_cycle:
                    ship.launch_cycle = comp.cycle_time
            
            # Check for generic abilities that affect stats
            # MultiplexTracking
            mt = comp.abilities.get('MultiplexTracking', 0)
            if mt > 0:
                if mt > ship.max_targets:
                    ship.max_targets = mt 

        # Apply Accumulated Totals Atomicially
        if hasattr(ship, 'resources'):
            ship.resources.register_storage('fuel', total_max_fuel)
            ship.resources.register_storage('ammo', total_max_ammo)
            ship.resources.register_storage('energy', total_max_energy)
            ship.resources.register_generation('energy', total_energy_gen)
            ship.resources.register_generation('ammo', total_ammo_gen)
        else:
             # Fallback for tests/mocks without resources?
             ship.max_fuel = total_max_fuel
             ship.max_ammo = total_max_ammo
             ship.max_energy = total_max_energy
             ship.energy_gen_rate = total_energy_gen
             ship.ammo_gen_rate = total_ammo_gen
        ship.total_thrust = total_thrust
        ship.turn_speed = total_turn_speed
        ship.max_shields = total_max_shields
        ship.shield_regen_rate = total_shield_regen
        ship.shield_regen_cost = total_shield_cost

        # 5. Phase 4: Physics & Limits
        # ----------------------------
        
        # Derelict Check - REMOVED per user request
        # Condition: Ships are never derelict, they only die when destroyed.
        ship.is_derelict = False
        
        # Physics Stats - INVERSE MASS SCALING
        K_THRUST = 2500
        K_TURN = 25000
        
        if ship.mass > 0:
            ship.acceleration_rate = (ship.total_thrust * K_THRUST) / (ship.mass * ship.mass)
            raw_turn_speed = ship.turn_speed
            ship.turn_speed = (raw_turn_speed * K_TURN) / (ship.mass ** 1.5)
            
            K_SPEED = 25
            ship.max_speed = (ship.total_thrust * K_SPEED) / ship.mass if ship.total_thrust > 0 else 0
        else:
            ship.acceleration_rate = 0
            ship.max_speed = 0
        
        # Limit Checks (Budget)
        self._check_mass_limits(ship)
    
        # Radius Calculation
        base_radius = 40
        ref_mass = 1000
        actual_mass = max(ship.mass, 100)
        ratio = actual_mass / ref_mass
        ship.radius = base_radius * (ratio ** (1/3.0))

        # 6. Phase 5: To-Hit & Electronic Warfare Stats
        # ---------------------------------------------
        
        # New Logit-Score System:
        # Defense Score (Higher = Harder to Hit). Is SUBTRACTED from Accuracy.
        # Components:
        # 1. Size: Larger = Easier to Hit (Negative Score).
        # 2. Maneuver: Agile = Harder to Hit (Positive Score).
        # 3. ECM: Noise = Harder to Hit (Positive Score).
        
        diameter = ship.radius * 2
        
        # Size Score:
        # Baseline Diameter 80 (Mass ~1k) = 0.0
        # Formula: -2.5 * log10(diameter / 80)
        # Prevents log(0)
        d_ratio = max(0.1, diameter / 80.0)
        size_score = -2.5 * math.log10(d_ratio)
        
        # Maneuver Score:
        # Accel contributes ~0-2.5 pts (Fighters 25 accel) -> /10
        # Turn contributes ~0-2.0 pts (Fighters 180 turn) -> /90
        maneuver_score = math.sqrt((ship.acceleration_rate / 20.0) + (ship.turn_speed / 360.0))
        
        # ECM Score (Additive)
        ecm_score = self._get_ability_total(component_pool, 'ToHitDefenseModifier')
        # Default 0 if none
        if isinstance(ecm_score, bool): ecm_score = 0.0
        
        # Total Defense Score
        ship.total_defense_score = size_score + maneuver_score + ecm_score
        
        # Legacy/Alias for UI until fully refactored
        ship.to_hit_profile = ship.total_defense_score
        
        # Offensive Baseline (Sensor Strength) - Score
        attack_mods = self._get_ability_total(component_pool, 'ToHitAttackModifier')
        # Default 0
        if isinstance(attack_mods, bool): attack_mods = 0.0
        
        ship.baseline_to_hit_offense = attack_mods

        # Emissive Armor (Max Stacking)
        ship.emissive_armor = self._get_ability_total(component_pool, 'EmissiveArmor')
        
        # Crystalline Armor (Max Stacking)
        ship.crystalline_armor = self._get_ability_total(component_pool, 'CrystallineArmor')

        # Ship Repair (SumStacking)
        ship.repair_rate = self._get_ability_total(component_pool, 'ShipRepair')
        
        # Ammo Generation (SumStacking)
        ship.ammo_gen_rate = self._get_ability_total(component_pool, 'AmmoGeneration')

        # 6. Aggregate Resources (Storage & Generation)
        # ---------------------------------------------
        total_fuel = 0
        total_energy = 0
        total_ammo = 0
        total_energy_gen = 0
        
        for comp in component_pool:
            if not comp.is_active: continue
            
            # Use instantiated abilities (Source of truth for modified values)
            if hasattr(comp, 'ability_instances'):
                for ab in comp.ability_instances:
                    # Note: ResourceStorage/Generation are imported at start of calculate
                    
                    if isinstance(ab, ResourceStorage):
                         # ab.max_amount is the modified capacity
                         if ab.resource_type == 'fuel':
                             total_fuel += ab.max_amount
                         elif ab.resource_type == 'energy':
                             total_energy += ab.max_amount
                         elif ab.resource_type == 'ammo':
                             total_ammo += ab.max_amount
                             
                    elif isinstance(ab, ResourceGeneration):
                         # ab.rate is the modified rate
                         if ab.resource_type == 'energy':
                             total_energy_gen += ab.rate

        if hasattr(ship, 'resources'):
             # Note: We are re-registering here essentially (or overwriting?). 
             # Phase 3 handled 'Legacy' components but Phase 6 handles 'Abilities'.
             # Wait, logic check: 
             # Phase 3 iterates Component Pool.
             # Phase 6 ALSO iterates Component Pool but specifically for 'ResourceStorage'.
             # Actually, Phase 3 loop INCLUDES generic ability handling (lines 154+).
             # So Phase 3 IS accumulating ability values into total_max_fuel.
             # Phase 6 loop (lines 312+) seems REDUNDANT or conflicting if it re-sums.
             # Let's check logic flow.
             # Phase 3:
             #   Iterate components:
             #     If ResourceStorage -> add to total_max_fuel
             #   Apply to ship.max_fuel
             # Phase 6:
             #   Iterate components AGAIN:
             #     If ResourceStorage -> add to total_fuel (local var)
             #   Apply to ship.max_fuel ( overwriting Phase 3?)
             #
             # YES. Phase 6 seems to be a duplicate or specific override.
             # Given refactor, we should probably UNIFY this.
             # But to be safe and follow plan, let's just update this block to behave correctly.
             # The existing code OVERWRITES ship.max_fuel with 'total_fuel' calculated here.
             # So we should register here too? Or relies on `register_storage` being additive?
             # `register_storage` ADDS to capacity.
             # If we call it in Phase 3 AND Phase 6, we DOUBLE capacity.
             #
             # Investigation:
             # Phase 3 loop (lines 149-207) Handles:
             #  - ResourceStorage ability (lines 157-164)
             #  - Engine/Thruster/Armor legacy (lines 173+)
             #
             # Phase 6 loop (lines 312-333) Handles:
             #  - ResourceStorage ability (lines 320-327)
             #  - ResourceGeneration ability (lines 329-333)
             #
             # It looks like Phase 6 is partially redundant but might have been intended for 'final separate pass'.
             # Since 'register_storage' adds, calling it twice IS A BUG.
             # We should probably REMOVE the Phase 6 redundant aggregation if Phase 3 covers it.
             # Phase 3 covers 'ResourceStorage' (lines 157) and 'ResourceGeneration' (Phase 3 lines 166: YES).
             #
             # Wait, Phase 3 has:
             #   elif isinstance(ability, ResourceGeneration):
             #       if ability.resource_type == 'energy': total_energy_gen += ability.rate
             #
             # So Phase 3 covers everything. 
             # Phase 6 appears to be dead/duplicate code from refactor attempts.
             # However, let's verify if Phase 3 *applies* everything.
             # Phase 3 applies to 'total_max_fuel' etc local vars.
             # Then lines 208 applies to ship properties.
             #
             # Phase 6 calculates 'total_fuel' etc.
             # Then lines 334 applies to ship properties.
             #
             # IF we keep both, we are just overwriting.
             # BUT `register_storage` accumulates.
             # So we MUST NOT call register_storage twice for the same components.
             #
             # DECISION:
             # Phase 6 is redundant. I will COMMENT OUT Phase 6 application or remove it,
             # essentially relying on Phase 3.
             # BUT wait: Phase 3 loop accumulates `total_max_fuel`.
             # Phase 6 loop accumulates `total_fuel`.
             # If I remove Phase 6, I must ensure Phase 3 is correct.
             # Phase 3 looks correct.
             #
             # Let's replace Phase 6 application with a PASS or reset?
             # Actually, `ship.resources.reset_stats()` was called at start.
             # So if Phase 3 registers, we are good.
             # If Phase 6 also registers (if I changed it), it would double.
             # The existing code (before my changes) was OVERWRITING properties.
             # `ship.max_fuel = total_fuel`.
             # So effectively Phase 6 'won'. 
             # Since Phase 3 and Phase 6 logic is identical for ResourceStorage, result is same.
             #
             # Strategy: Remove Phase 6 redundant logic to clean up confusion and avoid double-counting with `register`.
             pass
        # ship.max_fuel = total_fuel
        # ship.max_ammo = total_ammo
        # ship.max_energy = total_energy
        # ship.energy_gen_rate = total_energy_gen

        # Shield Stats
        ship.max_shields = self._get_ability_total(component_pool, 'ShieldProjection')
        # Default 0 if bool/none
        if isinstance(ship.max_shields, bool): ship.max_shields = 0.0
            
        ship.shield_regen_rate = self._get_ability_total(component_pool, 'ShieldRegeneration')
        if isinstance(ship.shield_regen_rate, bool): ship.shield_regen_rate = 0.0

        # Armor Pool Init (if starting)
        if LayerType.ARMOR in ship.layers:
            if ship.layers[LayerType.ARMOR]['hp_pool'] == 0:
                ship.layers[LayerType.ARMOR]['hp_pool'] = ship.layers[LayerType.ARMOR]['max_hp_pool']
            
        # Initialize Resources 
        self._initialize_resources(ship)
        
        # 7. Combat Endurance Stats
        # -------------------------
        self._calculate_combat_endurance(ship, component_pool)

    def _calculate_combat_endurance(self, ship, component_pool):
        """Calculate endurance times for Fuel, Ammo, and Energy."""
        from resources import ResourceConsumption

        
        # A. Fuel
        # Rate = Sum of ResourceConsumption(fuel, constant)
        fuel_consumption = 0.0
        
        # B. Ordinance (Ammo)
        # Rate = Sum of ResourceConsumption(ammo, activation) / reload_time
        ammo_consumption = 0.0
        
        # C. Energy
        # Rate = Sum of ResourceConsumption(energy, activation) / reload_time
        energy_consumption = 0.0

        for c in component_pool:
            if not c.is_active: continue

            # Iterate Abilities for Source of Truth
            if hasattr(c, 'ability_instances'):
                for ab in c.ability_instances:
                    # Resource Storage dealt with in Phase 3 aggregation
                    
                    if isinstance(ab, ResourceConsumption):
                        # Constant Consumption (Generic)
                        if ab.trigger == 'constant':
                            if ab.resource_name == 'fuel':
                                fuel_consumption += ab.amount
                            elif ab.resource_name == 'energy':
                                energy_consumption += ab.amount
                            elif ab.resource_name == 'ammo':
                                ammo_consumption += ab.amount
                            
                        # Activation Costs (Energy/Ammo) -> Convert to Rate
                        elif ab.trigger == 'activation':
                            # Get fire rate (1/reload)
                            # Assume component has reload_time if it has activation costs
                            reload_t = getattr(c, 'reload_time', 1.0)
                            if reload_t > 0:
                                rate = ab.amount / reload_t
                                if ab.resource_name == 'ammo':
                                    ammo_consumption += rate
                                elif ab.resource_name == 'energy':
                                    energy_consumption += rate
            
            # Additional Energy Consumers that might not be fully in abilities yet?
            # ShieldRegenerator cost is usually handled via generic abilities now?
            # Note: ShieldRegen is usually 'constant' consumption in some systems, 
            # but here it's traditionally per tick conditional. 
            # ship_combat.py logic: if current < max, consume.
            # Stats assume WORST CASE (continuous regeneration).
            # OLD Logic: ship.shield_regen_cost added to energy_consumption.
            pass

        # Add aggregated shield cost (Assuming worst case continuous regen)
        energy_consumption += ship.shield_regen_cost
        
        ship.fuel_consumption = fuel_consumption
        ship.fuel_endurance = (ship.max_fuel / fuel_consumption) if fuel_consumption > 0 else float('inf')

        ship.ammo_consumption = ammo_consumption
        ship.ammo_endurance = (ship.max_ammo / ammo_consumption) if ammo_consumption > 0 else float('inf')
        
        ship.energy_consumption = energy_consumption
        ship.energy_net = ship.energy_gen_rate - energy_consumption

        
        if ship.energy_net < 0:
            # Draining
            drain_rate = abs(ship.energy_net)
            ship.energy_endurance = ship.max_energy / drain_rate
        else:
            # Sustainable
            ship.energy_endurance = float('inf')
            
        # Recharge Time
        # Assume starting from 0 to Full using only Generation (no consumption)
        # Or should it be Net Recharge? Prompt says "if consumption stops". So purely Generation.
        if ship.energy_gen_rate > 0:
            ship.energy_recharge = ship.max_energy / ship.energy_gen_rate
        else:
            ship.energy_recharge = float('inf')

    def _priority_sort_key(self, c):
        t = c.type_str
        # Bridge (Command)
        if t == "Bridge": return 0
        # Engines (Movement)
        if t == "Engine" or t == "Thruster": return 1
        # Weapons (Offense)
        if isinstance(c, Weapon): return 2
        # Others
        return 3

    def _check_mass_limits(self, ship):
        ship.mass_limits_ok = True
        # Budget check (Max Mass)
        ship.max_mass_budget = 1000 # Default
        
        if ship.ship_class in self.vehicle_classes:
             ship.max_mass_budget = self.vehicle_classes[ship.ship_class].get('max_mass', 1000)

        for layer_type, layer_data in ship.layers.items():
            limit_ratio = layer_data.get('max_mass_pct', 1.0)
            ratio = layer_data['mass'] / ship.max_mass_budget
            is_ok = ratio <= limit_ratio
            ship.layer_status[layer_type] = {
                'mass': layer_data['mass'],
                'ratio': ratio,
                'limit': limit_ratio,
                'ok': is_ok
            }
            if not is_ok: ship.mass_limits_ok = False
        
        if ship.mass > ship.max_mass_budget:
            ship.mass_limits_ok = False

    def _initialize_resources(self, ship):
        # Resource Initialization (Auto-fill on first load only, or when capacity increases)
        prev_max_fuel = getattr(ship, '_prev_max_fuel', 0)
        prev_max_ammo = getattr(ship, '_prev_max_ammo', 0)
        prev_max_energy = getattr(ship, '_prev_max_energy', 0)
        prev_max_shields = getattr(ship, '_prev_max_shields', 0)
        
        if not getattr(ship, '_resources_initialized', False):
            if ship.max_fuel > 0:
                ship.current_fuel = ship.max_fuel
            if ship.max_ammo > 0:
                ship.current_ammo = ship.max_ammo
            if ship.max_energy > 0:
                ship.current_energy = ship.max_energy
            if ship.max_shields > 0:
                ship.current_shields = ship.max_shields
            ship._resources_initialized = True
        else:
            # Handle capacity increases
            if ship.max_fuel > prev_max_fuel:
                ship.current_fuel += (ship.max_fuel - prev_max_fuel)
            if ship.max_ammo > prev_max_ammo:
                ship.current_ammo += (ship.max_ammo - prev_max_ammo)
            if ship.max_energy > prev_max_energy:
                ship.current_energy += (ship.max_energy - prev_max_energy)
            if ship.max_shields > prev_max_shields:
                ship.current_shields += (ship.max_shields - prev_max_shields)
        
        # Remember current max for next recalculate
        ship._prev_max_fuel = ship.max_fuel
        ship._prev_max_ammo = ship.max_ammo
        ship._prev_max_energy = ship.max_energy
        ship._prev_max_shields = ship.max_shields

    def calculate_ability_totals(self, components):
        """
        Calculate total values for all abilities from components.
        Supports 'stack_group' in ability definition for redundancy (MAX) vs stacking (SUM/MULT).
        """
        totals = {}
        
        # Abilities that should multiply instead of sum
        MULTIPLICATIVE_ABILITIES = {'ToHitAttackModifier', 'ToHitDefenseModifier'}
        
        # Intermediate structure: ability -> { group_key -> [values] }
        ability_groups = {}

        for comp in components:
            abilities = getattr(comp, 'abilities', {})
            for ability_name, raw_value in abilities.items():
                
                # Parse Value & Group
                value = raw_value
                stack_group = None
                
                if isinstance(raw_value, dict) and 'value' in raw_value:
                    value = raw_value['value']
                    stack_group = raw_value.get('stack_group')
                
                # Determine Group Key
                # If no stack_group, use component instance (unique) so it behaves as individual item (stacking with everything)
                group_key = stack_group if stack_group else comp

                if ability_name not in ability_groups:
                    ability_groups[ability_name] = {}
                if group_key not in ability_groups[ability_name]:
                    ability_groups[ability_name][group_key] = []
                
                ability_groups[ability_name][group_key].append(value)

        # Aggregate
        for ability_name, groups in ability_groups.items():
            # 1. Intra-Group Aggregation (MAX / Redundancy)
            # All items in a Named Group provide redundancy -> Take MAX
            group_contributions = []
            
            for key, values in groups.items():
                # Filter for numeric
                nums = [v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
                if nums:
                    group_contributions.append(max(nums))
                elif any(v is True for v in values):
                     # Boolean support (if any is True, the group is True)
                     group_contributions.append(True)

            if not group_contributions:
                continue

            # 2. Inter-Group Aggregation (Sum or Multiply)
            first = group_contributions[0]
            
            if isinstance(first, bool):
                # If any group contributes True, result is True
                totals[ability_name] = True
            else:
                if ability_name in MULTIPLICATIVE_ABILITIES:
                    val = 1.0
                    for v in group_contributions:
                         if isinstance(v, (int, float)): val *= v
                    totals[ability_name] = val
                else:
                    val = sum(v for v in group_contributions if isinstance(v, (int, float)))
                    totals[ability_name] = val
        
        return totals

    def _get_ability_total(self, component_list, ability_name):
        """Calculate total value of a specific ability across provided components."""
        totals = self.calculate_ability_totals(component_list)
        return totals.get(ability_name, 0)
