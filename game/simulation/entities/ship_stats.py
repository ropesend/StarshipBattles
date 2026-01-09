from game.simulation.components.component import ComponentStatus, LayerType
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
        from game.simulation.systems.resource_manager import ResourceStorage, ResourceGeneration

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
            
        # Update cached values via property setters
        ship.mass = ship.current_mass + ship.base_mass
        ship.max_hp = sum(c.max_hp for layer in ship.layers.values() for c in layer['components'])
        ship.hp = sum(c.current_hp for layer in ship.layers.values() for c in layer['components'])

        # Base Stats Reset
        ship.total_thrust = 0
        ship.turn_speed = 0
        ship.resources.reset_stats()
            
        ship.max_shields = 0
        ship.shield_regen_rate = 0
        ship.shield_regen_cost = 0
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
                
                # Check Damage Threshold (ignore Armor - armor uses HP pool, not individual component threshold)
                if not comp.abilities.get('Armor', False):
                     if comp.max_hp > 0 and (comp.current_hp / comp.max_hp) <= 0.5:
                         comp.is_active = False
                         comp.status = ComponentStatus.DAMAGED
                
                # If armor is dead (0 hp), it's inactive
                if comp.abilities.get('Armor', False) and comp.current_hp <= 0:
                    comp.is_active = False
                    comp.status = ComponentStatus.DAMAGED
                
                # Gather Supply from FUNCTIONAL components
                if comp.is_active:
                    abilities = comp.abilities
                    # Crew Provided (Positive CrewCapacity)
                    # Crew Provided
                    for ab in comp.get_abilities('CrewCapacity'):
                        available_crew += ab.amount
                        
                    # Life Support Provided
                    for ab in comp.get_abilities('LifeSupportCapacity'):
                        available_life_support += ab.amount

                component_pool.append(comp)

        # 3. Phase 2: Resource Allocation (Crew & Life Support)
        # -----------------------------------------------------
        # Store for UI
        ship.crew_onboard = available_crew
        ship.crew_required = 0
        ship.max_targets = 1 # Reset to default
        
        # Centralize mass budget lookup
        ship.max_mass_budget = self.vehicle_classes.get(ship.ship_class, {}).get('max_mass', 1000)
        
        # Effective Crew is limited by Life Support
        effective_crew = min(available_crew, available_life_support)
        
        # Priority sort using helper
        component_pool.sort(key=self._priority_sort_key)
        
        for comp in component_pool:
            if not comp.is_active: continue # Already damaged
            
            # Check Crew Requirement
            req_crew = 0
            for ab in comp.get_abilities('CrewRequired'):
                req_crew += ab.amount
            
            # Satellite Exception: Satellites ignore crew requirements
            if ship.vehicle_type == "Satellite":
                req_crew = 0
            

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
                    ab_cls = ability.__class__.__name__
                    if ab_cls == 'ResourceStorage':
                        res_type = getattr(ability, 'resource_type', '')
                        max_amt = getattr(ability, 'max_amount', 0.0)
                        if res_type == 'fuel':
                            total_max_fuel += max_amt
                        elif res_type == 'ammo':
                            total_max_ammo += max_amt
                        elif res_type == 'energy':
                            total_max_energy += max_amt
                    
                    # Resource Generation
                    elif ab_cls == 'ResourceGeneration':
                        res_type = getattr(ability, 'resource_type', '')
                        rate = getattr(ability, 'rate', 0.0)
                        if res_type == 'energy':
                            total_energy_gen += rate
                        elif res_type == 'ammo':
                            total_ammo_gen += rate
            
            # Phase 3: Ability-Based Stats Aggregation
            
            # Thrust from CombatPropulsion abilities
            for ab in comp.get_abilities('CombatPropulsion'):
                total_thrust += ab.thrust_force
            
            # Turn speed from ManeuveringThruster abilities
            for ab in comp.get_abilities('ManeuveringThruster'):
                total_turn_speed += ab.turn_rate
                ship.total_maneuver_points += ab.turn_rate
            
            # Armor HP pool (using ability-based detection)
            if comp.abilities.get('Armor', False):
                if LayerType.ARMOR in ship.layers:
                    ship.layers[LayerType.ARMOR]['max_hp_pool'] += comp.max_hp
            
            # Shields from ShieldProjection abilities
            for ab in comp.get_abilities('ShieldProjection'):
                total_max_shields += ab.capacity
            
            # Shield regen from ShieldRegeneration abilities
            for ab in comp.get_abilities('ShieldRegeneration'):
                total_shield_regen += ab.rate
            
            # Shield energy cost from EnergyConsumption abilities on shield regen components
            if comp.has_ability('ShieldRegeneration'):
                for ab in comp.ability_instances:
                    if ab.__class__.__name__ == 'ResourceConsumption' and getattr(ab, 'resource_name', '') == 'energy':
                        total_shield_cost += getattr(ab, 'amount', 0.0)
                        break
            
            # Hangar stats (still uses VehicleLaunch ability from abilities dict)
            if comp.has_ability('VehicleLaunch') or 'VehicleLaunch' in comp.abilities:
                vl = comp.abilities.get('VehicleLaunch', {})
                ship.fighter_capacity += comp.abilities.get('VehicleStorage', 0)
                ship.fighters_per_wave += 1
                max_mass = vl.get('max_launch_mass', 0) if isinstance(vl, dict) else 0
                if max_mass > ship.fighter_size_cap:
                    ship.fighter_size_cap = max_mass
                    
                cycle = vl.get('cycle_time', 5.0) if isinstance(vl, dict) else 5.0
                if cycle > ship.launch_cycle:
                    ship.launch_cycle = cycle
            
            # Check for generic abilities that affect stats
            # MultiplexTracking
            mt = comp.abilities.get('MultiplexTracking', 0)
            if mt > 0:
                if mt > ship.max_targets:
                    ship.max_targets = mt 

        # Apply Accumulated Totals Atomicially
        ship.resources.register_storage('fuel', total_max_fuel)
        ship.resources.register_storage('ammo', total_max_ammo)
        ship.resources.register_storage('energy', total_max_energy)
        ship.resources.register_generation('energy', total_energy_gen)
        ship.resources.register_generation('ammo', total_ammo_gen)
        ship.total_thrust = total_thrust
        ship.turn_speed = total_turn_speed
        ship.max_shields = total_max_shields
        ship.shield_regen_rate = total_shield_regen
        ship.shield_regen_cost = total_shield_cost

        # 5. Phase 4: Physics & Limits
        # ----------------------------
        
        # Derelict check is now handled via update_derelict_status() in ship.py
        # and ability-based logic in ClassRequirementsRule.
        
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

        # 6. Aggregate Resources (Storage & Generation) - DEPRECATED / REMOVED
        # Phase 3 already handles Ability aggregation for Ship properties and ResourceRegistry.
        # This block was legacy/redundant and risked double-counting if active.
        pass


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
        from game.simulation.systems.resource_manager import ResourceConsumption

        
        # Rate = Sum of ResourceConsumption(fuel, constant)
        # A. Fuel
        fuel_consumption = 0.0
        potential_fuel = 0.0
        
        # B. Ordinance (Ammo)
        ammo_consumption = 0.0
        potential_ammo = 0.0
        
        # C. Energy
        energy_consumption = 0.0
        potential_energy = 0.0

        for c in component_pool:
            # Local accumulators for this component
            c_fuel = 0.0
            c_ammo = 0.0
            c_energy = 0.0
            
            # Iterate Abilities for Source of Truth
            if hasattr(c, 'ability_instances'):
                for ab in c.ability_instances:
                    ab_cls = ab.__class__.__name__
                    # Resource Storage dealt with in Phase 3 aggregation
                    
                    if ab_cls == 'ResourceConsumption':
                        # Constant Consumption (Generic)
                        trigger = getattr(ab, 'trigger', 'constant')
                        resource_name = getattr(ab, 'resource_name', '')
                        amount = getattr(ab, 'amount', 0.0)
                        
                        if trigger == 'constant':
                            if resource_name == 'fuel':
                                c_fuel += amount
                            elif resource_name == 'energy':
                                c_energy += amount
                            elif resource_name == 'ammo':
                                c_ammo += amount
                            
                        # Activation Costs (Energy/Ammo) -> Convert to Rate
                        elif trigger == 'activation':
                            # Get fire rate (1/reload)
                            # Look for associated WeaponAbility to get accurate reload time
                            reload_t = 1.0
                            found_weapon = False
                            
                            # Try to find WeaponAbility on component
                            if hasattr(c, 'ability_instances'):
                                for inst in c.ability_instances:
                                    if inst.__class__.__name__ in ['WeaponAbility', 'ProjectileWeaponAbility', 'BeamWeaponAbility', 'SeekerWeaponAbility']:
                                        reload_t = getattr(inst, 'reload_time', 1.0)
                                        found_weapon = True
                                        break
                            
                            # Fallback to component attribute (Legacy)
                            if not found_weapon:
                                reload_t = getattr(c, 'reload_time', 1.0)
                                
                            if reload_t > 0:
                                rate = ab.amount / reload_t
                                if ab.resource_name == 'ammo':
                                    c_ammo += rate
                                elif ab.resource_name == 'energy':
                                    c_energy += rate

            # Add to Potentials (Always)
            potential_fuel += c_fuel
            potential_ammo += c_ammo
            potential_energy += c_energy
            
            # Add to Actuals (Only if Active)
            if c.is_active:
                fuel_consumption += c_fuel
                ammo_consumption += c_ammo
                energy_consumption += c_energy

        # Store Actuals (used for physics/endurance)
        ship.fuel_consumption = fuel_consumption
        ship.ammo_consumption = ammo_consumption
        ship.energy_consumption = energy_consumption

        # Store Potentials (used for UI projections)
        ship.potential_fuel_consumption = potential_fuel
        ship.potential_ammo_consumption = potential_ammo
        ship.potential_energy_consumption = potential_energy
        
        # Use registry directly
        max_fuel = ship.resources.get_max_value('fuel')
        # Endurance calculation uses ACTIVE consumption
        ship.fuel_endurance = (max_fuel / fuel_consumption) if fuel_consumption > 0 else float('inf')

        max_ammo = ship.resources.get_max_value('ammo')
        ship.ammo_endurance = (max_ammo / ammo_consumption) if ammo_consumption > 0 else float('inf')
        
        # Energy Gen Rate
        r_energy = ship.resources.get_resource('energy')
        energy_gen_rate = r_energy.regen_rate if r_energy else 0.0
        
        ship.energy_net = energy_gen_rate - energy_consumption
        
        max_energy = ship.resources.get_max_value('energy')
        
        if ship.energy_net < 0:
            # Draining
            drain_rate = abs(ship.energy_net)
            ship.energy_endurance = max_energy / drain_rate
        else:
            # Sustainable
            ship.energy_endurance = float('inf')
            
        # Recharge Time
        # Assume starting from 0 to Full using only Generation (no consumption)
        # Or should it be Net Recharge? Prompt says "if consumption stops". So purely Generation.
        if energy_gen_rate > 0:
            ship.energy_recharge = max_energy / energy_gen_rate
        else:
            ship.energy_recharge = float('inf')

        # Populate Cached Summary
        dps = 0
        from game.simulation.components.abilities import WeaponAbility
        
        # Calculate theoretical max DPS (all weapons)
        for layer in ship.layers.values():
            for c in layer['components']:
                 # Use get_abilities to handle polymorphism
                 for ab in c.get_abilities('WeaponAbility'):
                     if ab.reload_time > 0:
                         dps += ab.damage / ab.reload_time
        
        ship._cached_summary = {
            'mass': ship.mass,
            'max_hp': ship.max_hp,
            'speed': ship.max_speed,
            'turn': ship.turn_speed,
            'shield': ship.max_shields,
            'dps': dps,
            'range': ship.max_weapon_range
        }

    def _priority_sort_key(self, c):
        # Bridge (Command)
        if c.has_ability('CommandAndControl'): return 0
        # Engines (Movement)
        if c.has_ability('CombatPropulsion') or c.has_ability('ManeuveringThruster'): return 1
        # Weapons (Offense)
        if c.has_ability('WeaponAbility'): return 2
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
        
        # Get current max values directly from registry
        curr_max_fuel = ship.resources.get_max_value('fuel')
        curr_max_ammo = ship.resources.get_max_value('ammo')
        curr_max_energy = ship.resources.get_max_value('energy')
        
        if not getattr(ship, '_resources_initialized', False):
            # First init - fill to max
            if curr_max_fuel > 0:
                ship.resources.set_value('fuel', curr_max_fuel)
            if curr_max_ammo > 0:
                ship.resources.set_value('ammo', curr_max_ammo)
            if curr_max_energy > 0:
                ship.resources.set_value('energy', curr_max_energy)
            if ship.max_shields > 0:
                ship.current_shields = ship.max_shields
            ship._resources_initialized = True
        else:
            # Handle capacity increases (preserve current relative usage or just add delta?)
            # Logic: If max increased, add difference to current.
            if curr_max_fuel > prev_max_fuel:
                delta = curr_max_fuel - prev_max_fuel
                ship.resources.modify_value('fuel', delta)
            if curr_max_ammo > prev_max_ammo:
                delta = curr_max_ammo - prev_max_ammo
                ship.resources.modify_value('ammo', delta)
            if curr_max_energy > prev_max_energy:
                delta = curr_max_energy - prev_max_energy
                ship.resources.modify_value('energy', delta)
            if ship.max_shields > prev_max_shields:
                ship.current_shields += (ship.max_shields - prev_max_shields)
        
        # Remember current max for next recalculate
        ship._prev_max_fuel = curr_max_fuel
        ship._prev_max_ammo = curr_max_ammo
        ship._prev_max_energy = curr_max_energy
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
            # 1. Process Ability Instances (New System - Scaled Values)
            # Track which abilities are handled to avoid double counting from dict
            handled_abilities = set()
            
            if hasattr(comp, 'ability_instances'):
                # Handle List (Current Implementation)
                if isinstance(comp.ability_instances, list):
                    for ab in comp.ability_instances:
                        ability_name = ab.__class__.__name__
                        handled_abilities.add(ability_name)
                        
                        # Extract value from Object
                        value = None
                        if hasattr(ab, 'amount'): value = ab.amount
                        elif hasattr(ab, 'value'): value = ab.value
                        elif hasattr(ab, 'capacity'): value = ab.capacity # Some use capacity
                        elif hasattr(ab, 'max_amount'): value = ab.max_amount # ResourceStorage uses max_amount
                        elif hasattr(ab, 'thrust_force'): value = ab.thrust_force # CombatPropulsion uses thrust_force
                        # Special case for CommandAndControl (Flag)
                        elif ability_name == 'CommandAndControl': value = True
                        
                        # Fallback for marker abilities (if it exists, it's True)
                        if value is None: 
                            value = True
                        
                        stack_group = getattr(ab, 'stack_group', None)
                        group_key = stack_group if stack_group else comp

                        if ability_name not in ability_groups: ability_groups[ability_name] = {}
                        if group_key not in ability_groups[ability_name]: ability_groups[ability_name][group_key] = []
                        
                        ability_groups[ability_name][group_key].append(value)
                        
                        # Fix for BUG-08: Alias ResourceStorage(fuel) to FuelStorage for ClassRequirementsRule
                        if ability_name == 'ResourceStorage' and getattr(ab, 'resource_type', '') == 'fuel':
                             alias = 'FuelStorage'
                             if alias not in ability_groups: ability_groups[alias] = {}
                             if group_key not in ability_groups[alias]: ability_groups[alias][group_key] = []
                             ability_groups[alias][group_key].append(value)
                
                # Handle Dict
                elif isinstance(comp.ability_instances, dict):
                     # ... (omitted for brevity, assume debug print sufficient in list block)
                     pass

            # 2. Process Raw Dictionary
            abilities = getattr(comp, 'abilities', {})
            if isinstance(abilities, dict):
                for ability_name, raw_value in abilities.items():
                    # Check handled
                    if ability_name in handled_abilities:
                        continue
                    
                    # Parse Value & Group
                    value = raw_value
                    stack_group = None
                    
                    if isinstance(raw_value, dict) and 'value' in raw_value:
                        value = raw_value['value']
                        stack_group = raw_value.get('stack_group')
                    
                    # Determine Group Key
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
