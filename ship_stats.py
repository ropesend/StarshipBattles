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
        ship.max_fuel = 0
        ship.max_ammo = 0
        ship.max_energy = 0
        ship.energy_gen_rate = 0
        ship.max_shields = 0
        ship.shield_regen_rate = 0
        ship.shield_regen_cost = 0
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
        
        for comp in component_pool:
            if not comp.is_active: continue
            
            if isinstance(comp, Engine):
                ship.total_thrust += comp.thrust_force
            elif isinstance(comp, Thruster):
                ship.turn_speed += comp.turn_speed
                ship.total_maneuver_points += comp.turn_speed
            elif isinstance(comp, Generator):
                ship.energy_gen_rate += comp.energy_generation_rate
            elif isinstance(comp, Tank):
                if comp.resource_type == 'fuel':
                    ship.max_fuel += comp.capacity
                elif comp.resource_type == 'ammo':
                    ship.max_ammo += comp.capacity
                elif comp.resource_type == 'energy':
                    ship.max_energy += comp.capacity
            elif isinstance(comp, Armor):
                if LayerType.ARMOR in ship.layers:
                    ship.layers[LayerType.ARMOR]['max_hp_pool'] += comp.max_hp
            elif isinstance(comp, Shield):
                ship.max_shields += comp.shield_capacity
            elif isinstance(comp, ShieldRegenerator):
                ship.shield_regen_rate += comp.regen_rate
                ship.shield_regen_cost += comp.energy_cost
            elif isinstance(comp, Hangar):
                ship.fighter_capacity += comp.storage_capacity
                # ship.launch_mass is replaced by granular stats
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
                    
            # Emissive Armor - NOW HANDLED IN calculate_ability_totals
            # ea = comp.abilities.get('EmissiveArmor', 0)
            # if ea > 0:
            #     ship.emissive_armor += ea 
            pass  # Removed manual summation 

        # 5. Phase 4: Physics & Limits
        # ----------------------------
        
        # Derelict Check
        # Condition: No functional Bridge OR No functional Engines (Thrust <= 0)
        has_active_bridge = False
        for c in component_pool:
            if isinstance(c, Bridge) and c.is_active:
                has_active_bridge = True
                break
        
        if ship.vehicle_type == "Satellite":
            if not has_active_bridge:
                ship.is_derelict = True
            else:
                ship.is_derelict = False
        else:
            if (not has_active_bridge) or (ship.total_thrust <= 0):
                ship.is_derelict = True
                ship.total_thrust = 0 # Ensure 0
            else:
                ship.is_derelict = False
        
        # Physics Stats - INVERSE MASS SCALING
        K_THRUST = 2500
        K_TURN = 25000
        
        if ship.mass > 0:
            if ship.is_derelict:
                ship.acceleration_rate = 2.0 # Allow deceleration to stop
                ship.turn_speed = 0
                ship.max_speed = 0
            else:
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
        maneuver_score = (ship.acceleration_rate / 20.0) + (ship.turn_speed / 360.0)
        
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
        
        # A. Fuel
        # Rate = Sum of Engine.fuel_cost_per_sec (active)
        # Thrusters assumed to not consume fuel for cruising/combat duration per spec assumptions
        fuel_consumption = 0.0
        for c in component_pool:
            if c.is_active and isinstance(c, Engine):
                fuel_consumption += getattr(c, 'fuel_cost_per_sec', 0)
        
        ship.fuel_consumption = fuel_consumption
        ship.fuel_endurance = (ship.max_fuel / fuel_consumption) if fuel_consumption > 0 else float('inf')
        
        # B. Ordinance (Ammo)
        # Rate = Sum of Weapon.ammo_cost * (1.0 / reload_time)
        ammo_consumption = 0.0
        for c in component_pool:
            if c.is_active and isinstance(c, Weapon):
                cost = getattr(c, 'ammo_cost', 0)
                reload_t = getattr(c, 'reload_time', 1.0)
                if cost > 0 and reload_t > 0:
                    rate = cost / reload_t
                    ammo_consumption += rate

        ship.ammo_consumption = ammo_consumption
        ship.ammo_endurance = (ship.max_ammo / ammo_consumption) if ammo_consumption > 0 else float('inf')

        # C. Energy
        # Rate = Weapons + Shield Regen + Other?
        # Net = Gen - Consumption
        energy_consumption = 0.0
        for c in component_pool:
            if c.is_active:
                # Weapons
                if isinstance(c, Weapon):
                    # Check for energy cost
                    cost = getattr(c, 'energy_cost', 0)
                    reload_t = getattr(c, 'reload_time', 1.0)
                    if cost > 0 and reload_t > 0:
                        energy_consumption += cost / reload_t
                elif isinstance(c, ShieldRegenerator):
                     # Shield Regen Cost is handled in Phase 3 aggregation as 'shield_regen_cost'
                     # But we should probably use the aggregated value to ensure we capture it all.
                     pass 
        
        # Add aggregated shield cost
        energy_consumption += ship.shield_regen_cost
        
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
