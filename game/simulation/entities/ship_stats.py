"""
Ship Stats Calculator - Derived Statistics Computation

This module contains ShipStatsCalculator, which computes all derived ship
statistics from the ship's components, abilities, and class definition.

Stat Calculation Phases:
    The calculate() method runs through 5 phases in order:

    Phase 1 - DAMAGE CHECK & SUPPLY GATHERING:
        - Reset component status assumptions
        - Check damage threshold to mark damaged components
        - Gather available crew and life support from active components
        - Build component pool for subsequent phases

    Phase 2 - RESOURCE ALLOCATION:
        - Calculate effective crew (min of available crew, life support)
        - Sort components by priority (critical systems first)
        - Deactivate components that can't be crewed
        - Track crew_required and crew_onboard for UI

    Phase 3 - STATS AGGREGATION:
        - Iterate active components only
        - Aggregate resource storage (fuel, ammo, energy)
        - Aggregate resource generation (energy, ammo)
        - Sum combat stats: thrust, turn speed, shields
        - Sum hangar stats: capacity, launch cycle
        - Track max_targets from MultiplexTracking

    Phase 4 - PHYSICS & LIMITS:
        - Apply physics formulas with inverse mass scaling:
          * max_speed = (thrust * K_SPEED) / mass
          * acceleration = (thrust * K_THRUST) / mass²
          * turn_speed = (raw_turn * K_TURN) / mass^1.5
        - Check mass budget limits
        - Calculate ship radius from total mass

    Phase 5 - SENSOR/DEFENSE SCORES:
        - Aggregate sensor scores for targeting
        - Aggregate ECM scores for defense

Physics Constants:
    K_SPEED, K_THRUST, K_TURN defined in physics_constants.py
    These control how ship stats convert to gameplay behavior.

Example:
    from game.core.registry import get_default_registries
    calculator = ShipStatsCalculator(get_default_registries().vehicle_classes)
    calculator.calculate(ship)
    # ship.max_speed, ship.turn_speed, etc. are now updated
"""
from game.simulation.components.component_constants import ComponentStatus
from game.core.constants import LayerType, ResourceType
from game.simulation.physics_constants import K_SPEED, K_THRUST, K_TURN
from game.simulation.entities.ability_aggregator import calculate_ability_totals, get_ability_total
from game.simulation.entities.combat_endurance import calculate_combat_endurance
from game.core.config import PhysicsConfig
from game.core.constants import CombatConstants
import math

class ShipStatsCalculator:
    """
    Encapsulates the logic for calculating ship statistics from its components.
    """
    def __init__(self, vehicle_classes):
        self.vehicle_classes = vehicle_classes

    def calculate(self, ship) -> None:
        """
        Recalculates all derived stats for the ship based on its components and class.
        """
        # Import local to avoid circular dep if needed, or top level if safe.
        # resources.py likely imports NOTHING from ship_stats.
        from game.simulation.components.abilities.resources import ResourceStorage, ResourceGeneration

        # 1. Reset Base Calculations
        ship.current_mass = 0
        ship.layer_status = {}
        ship.mass_limits_ok = True
        ship.drag = PhysicsConfig.DEFAULT_LINEAR_DRAG
        
        # Calculate Mass (Mass never changes due to damage/status in this model, dead weight remains)
        for layer_type, layer_data in ship.layers.items():
            l_mass = sum(c.mass for c in layer_data.components)
            layer_data.mass = l_mass
            ship.current_mass += l_mass
            
        # Update cached values via property setters
        ship.mass = ship.current_mass + ship.base_mass
        all_components = ship.get_all_components()
        ship.max_hp = sum(c.max_hp for c in all_components)
        ship.hp = sum(c.current_hp for c in all_components)

        # Resource Costs Aggregation
        ship.construction_cost = {}
        from game.core.constants import PLANET_RESOURCES
        for res in PLANET_RESOURCES:
            ship.construction_cost[res] = 0
            
        for comp in all_components:
            comp_costs = comp.get_resource_cost()
            for res, amount in comp_costs.items():
                if res in ship.construction_cost:
                    ship.construction_cost[res] += amount

        # Base Stats Reset
        ship.total_thrust = 0
        ship.total_strategic_movement = 0  # Strategic layer movement points
        ship.turn_speed = 0
        ship.resources.reset_stats()

        ship.max_shields = 0
        ship.shield_regen_rate = 0
        ship.shield_regen_cost = 0
        ship.repair_rate = 0
        if LayerType.ARMOR in ship.layers:
            ship.layers[LayerType.ARMOR].max_hp_pool = 0
            
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
        component_pool, available_crew, available_life_support = self._phase_damage_check_and_supply(ship)

        # 3. Phase 2: Resource Allocation (Crew & Life Support)
        # -----------------------------------------------------
        self._phase_resource_allocation(ship, component_pool, available_crew, available_life_support)

        # 4. Phase 3: Stats Aggregation (Active Components Only)
        # ------------------------------------------------------
        self._phase_stats_aggregation(ship, component_pool)

        # 5. Phase 4: Physics & Limits
        # ----------------------------
        self._phase_physics_and_limits(ship)

        # 6. Phase 5: To-Hit & Electronic Warfare Stats
        # ---------------------------------------------
        self._phase_sensor_defense_scores(ship, component_pool)

    def _phase_sensor_defense_scores(self, ship, component_pool) -> None:
        """Phase 5: Calculate to-hit, defense scores, and finalize resources.

        Computes defense score (size + maneuver + ECM), offensive modifiers,
        emissive/crystalline armor, repair rate, ammo generation, and initializes resources.
        """
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
        if isinstance(ecm_score, bool):
            ecm_score = 0.0

        # Total Defense Score
        ship.total_defense_score = size_score + maneuver_score + ecm_score

        # Offensive Baseline (Sensor Strength) - Score
        attack_mods = self._get_ability_total(component_pool, 'ToHitAttackModifier')
        # Default 0
        if isinstance(attack_mods, bool):
            attack_mods = 0.0

        ship.baseline_to_hit_offense = attack_mods

        # Emissive Armor (Max Stacking)
        ship.emissive_armor = self._get_ability_total(component_pool, 'EmissiveArmor')

        # Crystalline Armor (Max Stacking)
        ship.crystalline_armor = self._get_ability_total(component_pool, 'CrystallineArmor')

        # Ship Repair (SumStacking)
        ship.repair_rate = self._get_ability_total(component_pool, 'ShipRepair')

        # Ammo Generation (SumStacking) - using value from ResourceGeneration(ammo)
        ammo_res = ship.resources.get_resource(ResourceType.AMMO)
        ship.ammo_gen_rate = ammo_res.regen_rate if ammo_res else 0.0

        # Armor Pool Init (if starting)
        if LayerType.ARMOR in ship.layers:
            if ship.layers[LayerType.ARMOR].hp_pool == 0:
                ship.layers[LayerType.ARMOR].hp_pool = ship.layers[LayerType.ARMOR].max_hp_pool

        # Initialize Resources
        self._initialize_resources(ship)

        # Combat Endurance Stats
        calculate_combat_endurance(ship, component_pool)

    def _phase_physics_and_limits(self, ship) -> None:
        """Phase 4: Apply physics formulas and check mass limits.

        Calculates acceleration, max speed, turn speed using inverse mass scaling.
        Also calculates ship radius and validates mass budget.
        """
        # Physics Stats - INVERSE MASS SCALING
        if ship.mass > 0:
            ship.acceleration_rate = (ship.total_thrust * K_THRUST) / (ship.mass * ship.mass)
            raw_turn_speed = ship.turn_speed
            ship.turn_speed = (raw_turn_speed * K_TURN) / (ship.mass ** 1.5)

            ship.max_speed = (ship.total_thrust * K_SPEED) / ship.mass if ship.total_thrust > 0 else 0
        else:
            ship.acceleration_rate = 0
            ship.max_speed = 0

        # Limit Checks (Budget)
        self._check_mass_limits(ship)

        # Radius Calculation
        base_radius = PhysicsConfig.DEFAULT_BASE_RADIUS
        ref_mass = PhysicsConfig.REFERENCE_MASS
        actual_mass = max(ship.mass, 100)
        ratio = actual_mass / ref_mass
        ship.radius = base_radius * (ratio ** (1/3.0))

    def _phase_stats_aggregation(self, ship, component_pool) -> None:
        """Phase 3: Aggregate stats from active components.

        Iterates all active components and aggregates resource storage, generation,
        thrust, shields, hangar capacity, and other combat stats.
        """
        # Local accumulators for atomic updates (prevents premature clamping)
        acc = {
            'max_fuel': 0, 'max_ammo': 0, 'max_energy': 0,
            'energy_gen': 0, 'ammo_gen': 0,
            'thrust': 0, 'strategic_movement': 0, 'turn_speed': 0,
            'maneuver_points': 0,
            'max_shields': 0, 'shield_regen': 0, 'shield_cost': 0,
            'warp_max_tonnage': 0, 'warp_energy_cost': 0,
        }

        for comp in component_pool:
            if not comp.is_active:
                continue

            self._aggregate_resource_abilities(comp, acc)
            self._aggregate_propulsion_abilities(comp, acc)
            self._aggregate_defense_abilities(ship, comp, acc)
            self._aggregate_hangar_abilities(ship, comp)

            # MultiplexTracking (only 3 lines, uses max not sum)
            mt = comp.abilities.get('MultiplexTracking', 0)
            if mt > 0:
                if mt > ship.max_targets:
                    ship.max_targets = mt

        self._apply_aggregated_stats(ship, acc)

    def _aggregate_resource_abilities(self, comp, acc) -> None:
        """Aggregate ResourceStorage and ResourceGeneration abilities."""
        # Guard for non-Component objects (e.g., mocks in tests)
        abilities = getattr(comp, 'ability_instances', [])
        for ability in abilities:
                ab_cls = ability.__class__.__name__
                if ab_cls == 'ResourceStorage':
                    res_type = getattr(ability, 'resource_type', '')
                    max_amt = getattr(ability, 'max_amount', 0.0)
                    if res_type == ResourceType.FUEL:
                        acc['max_fuel'] += max_amt
                    elif res_type == ResourceType.AMMO:
                        acc['max_ammo'] += max_amt
                    elif res_type == ResourceType.ENERGY:
                        acc['max_energy'] += max_amt

                elif ab_cls == 'ResourceGeneration':
                    res_type = getattr(ability, 'resource_type', '')
                    rate = getattr(ability, 'rate', 0.0)
                    if res_type == ResourceType.ENERGY:
                        acc['energy_gen'] += rate
                    elif res_type == ResourceType.AMMO:
                        acc['ammo_gen'] += rate

    def _aggregate_propulsion_abilities(self, comp, acc) -> None:
        """Aggregate CombatPropulsion, StrategicMovement, WarpJump, ManeuveringThruster."""
        # Thrust from CombatPropulsion abilities
        for ab in comp.get_abilities('CombatPropulsion'):
            acc['thrust'] += ab.thrust_force

        # Strategic movement from StrategicMovement abilities
        for ab in comp.get_abilities('StrategicMovement'):
            acc['strategic_movement'] += ab.movement_points

        # WarpJump capability - use the largest warp drive
        for ab in comp.get_abilities('WarpJump'):
            tonnage = getattr(ab, 'max_tonnage', 0)
            if tonnage > acc['warp_max_tonnage']:
                acc['warp_max_tonnage'] = tonnage
            # Accumulate energy costs from all warp drives
            acc['warp_energy_cost'] += getattr(ab, 'energy_cost', 0)

        # Turn speed from ManeuveringThruster abilities
        for ab in comp.get_abilities('ManeuveringThruster'):
            acc['turn_speed'] += ab.turn_rate
            acc['maneuver_points'] += ab.turn_rate

    def _aggregate_defense_abilities(self, ship, comp, acc) -> None:
        """Aggregate Armor HP pool, ShieldProjection, ShieldRegeneration, shield energy cost."""
        # Armor HP pool (using ability-based detection)
        if comp.abilities.get('Armor', False):
            if LayerType.ARMOR in ship.layers:
                ship.layers[LayerType.ARMOR].max_hp_pool += comp.max_hp

        # Shields from ShieldProjection abilities
        for ab in comp.get_abilities('ShieldProjection'):
            acc['max_shields'] += ab.capacity

        # Shield regen from ShieldRegeneration abilities
        for ab in comp.get_abilities('ShieldRegeneration'):
            acc['shield_regen'] += ab.rate

        # Shield energy cost from ResourceConsumption(energy) abilities on shield regen components
        if comp.has_ability('ShieldRegeneration'):
            for ab in comp.ability_instances:
                if ab.__class__.__name__ == 'ResourceConsumption' and getattr(ab, 'resource_type', '') == ResourceType.ENERGY:
                    acc['shield_cost'] += getattr(ab, 'amount', 0.0)
                    break

    def _aggregate_hangar_abilities(self, ship, comp) -> None:
        """Aggregate VehicleLaunch, VehicleStorage, and launch cycle (directly mutates ship)."""
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

    def _apply_aggregated_stats(self, ship, acc) -> None:
        """Atomic application of accumulated totals to ship."""
        ship.resources.register_storage(ResourceType.FUEL, acc['max_fuel'])
        ship.resources.register_storage(ResourceType.AMMO, acc['max_ammo'])
        ship.resources.register_storage(ResourceType.ENERGY, acc['max_energy'])
        ship.resources.register_generation(ResourceType.ENERGY, acc['energy_gen'])
        ship.resources.register_generation(ResourceType.AMMO, acc['ammo_gen'])
        ship.total_thrust = acc['thrust']
        ship.total_strategic_movement = acc['strategic_movement']
        ship.turn_speed = acc['turn_speed']
        ship.total_maneuver_points = acc['maneuver_points']
        ship.max_shields = acc['max_shields']
        ship.shield_regen_rate = acc['shield_regen']
        ship.shield_regen_cost = acc['shield_cost']
        ship.warp_max_tonnage = acc['warp_max_tonnage']
        ship.warp_energy_cost = acc['warp_energy_cost']

    def _phase_resource_allocation(self, ship, component_pool, available_crew, available_life_support) -> None:
        """Phase 2: Allocate crew and life support to components.

        Deactivates components that cannot be crewed. Updates ship.crew_onboard,
        ship.crew_required, and ship.max_targets.
        """
        # Store for UI
        ship.crew_onboard = available_crew
        ship.crew_required = 0
        ship.max_targets = CombatConstants.DEFAULT_MAX_TARGETS  # Reset to default

        # Centralize mass budget lookup
        ship.max_mass_budget = self.vehicle_classes.get(ship.ship_class, {}).get('max_mass', 1000)

        # Effective Crew is limited by Life Support
        effective_crew = min(available_crew, available_life_support)

        # Priority sort using helper
        component_pool.sort(key=self._priority_sort_key)

        for comp in component_pool:
            if not comp.is_active:
                continue  # Already damaged

            # Check Crew Requirement
            req_crew = 0
            for ab in comp.get_abilities('CrewRequired'):
                req_crew += ab.amount

            ship.crew_required += req_crew

            if req_crew > 0:
                if effective_crew >= req_crew:
                    effective_crew -= req_crew
                else:
                    comp.is_active = False
                    comp.status = ComponentStatus.NO_CREW

    def _phase_damage_check_and_supply(self, ship) -> tuple[list, int, int]:
        """Phase 1: Check damage thresholds and gather crew/life support.

        Returns:
            Tuple of (component_pool, available_crew, available_life_support)
        """
        available_crew = 0
        available_life_support = 0
        component_pool = []

        for layer_type, comp in ship.iter_components():
            # Reset Status Assumption
            comp.is_active = True
            comp.status = ComponentStatus.ACTIVE

            # PROJ-49: Ensure HP ratio cache is refreshed (handles external HP modifications)
            comp.mark_hp_cache_dirty()

            # Check Damage Threshold (ignore Armor - armor uses HP pool, not individual component threshold)
            # PROJ-49: Use cached hp_ratio property to avoid repeated division
            if not comp.abilities.get('Armor', False):
                if comp.hp_ratio <= comp.damage_threshold:
                    comp.is_active = False
                    comp.status = ComponentStatus.DAMAGED

            # If armor is dead (0 hp), it's inactive
            if comp.abilities.get('Armor', False) and comp.current_hp <= 0:
                comp.is_active = False
                comp.status = ComponentStatus.DAMAGED

            # Gather Supply from FUNCTIONAL components
            if comp.is_active:
                # Crew Provided
                for ab in comp.get_abilities('CrewCapacity'):
                    available_crew += ab.amount

                # Life Support Provided
                for ab in comp.get_abilities('LifeSupportCapacity'):
                    available_life_support += ab.amount

            component_pool.append(comp)

        return component_pool, available_crew, available_life_support

    def _priority_sort_key(self, c) -> int:
        # Bridge (Command)
        if c.has_ability('CommandAndControl'): return 0
        # Engines (Movement)
        if c.has_ability('CombatPropulsion') or c.has_ability('ManeuveringThruster'): return 1
        # Weapons (Offense)
        if c.has_ability('WeaponAbility'): return 2
        # Others
        return 3

    def _check_mass_limits(self, ship) -> None:
        ship.mass_limits_ok = True
        # Budget check (Max Mass)
        ship.max_mass_budget = 1000 # Default
        
        if ship.ship_class in self.vehicle_classes:
             ship.max_mass_budget = self.vehicle_classes[ship.ship_class].get('max_mass', 1000)

        for layer_type, layer_data in ship.layers.items():
            limit_ratio = layer_data.max_mass_pct
            ratio = layer_data.mass / ship.max_mass_budget
            is_ok = ratio <= limit_ratio
            ship.layer_status[layer_type] = {
                'mass': layer_data.mass,
                'ratio': ratio,
                'limit': limit_ratio,
                'ok': is_ok
            }
            if not is_ok: ship.mass_limits_ok = False
        
        if ship.mass > ship.max_mass_budget:
            ship.mass_limits_ok = False

    def _initialize_resources(self, ship) -> None:
        # Resource Initialization (Auto-fill on first load only, or when capacity increases)
        prev_max_fuel = getattr(ship, '_prev_max_fuel', 0)
        prev_max_ammo = getattr(ship, '_prev_max_ammo', 0)
        prev_max_energy = getattr(ship, '_prev_max_energy', 0)
        prev_max_shields = getattr(ship, '_prev_max_shields', 0)
        
        # Get current max values directly from registry
        curr_max_fuel = ship.resources.get_max_value(ResourceType.FUEL)
        curr_max_ammo = ship.resources.get_max_value(ResourceType.AMMO)
        curr_max_energy = ship.resources.get_max_value(ResourceType.ENERGY)

        if not getattr(ship, '_resources_initialized', False):
            # First init - fill to max
            if curr_max_fuel > 0:
                ship.resources.set_value(ResourceType.FUEL, curr_max_fuel)
            if curr_max_ammo > 0:
                ship.resources.set_value(ResourceType.AMMO, curr_max_ammo)
            if curr_max_energy > 0:
                ship.resources.set_value(ResourceType.ENERGY, curr_max_energy)
            if ship.max_shields > 0:
                ship.current_shields = ship.max_shields
            ship._resources_initialized = True
        else:
            # Handle capacity increases (preserve current relative usage or just add delta?)
            # Logic: If max increased, add difference to current.
            if curr_max_fuel > prev_max_fuel:
                delta = curr_max_fuel - prev_max_fuel
                ship.resources.modify_value(ResourceType.FUEL, delta)
            if curr_max_ammo > prev_max_ammo:
                delta = curr_max_ammo - prev_max_ammo
                ship.resources.modify_value(ResourceType.AMMO, delta)
            if curr_max_energy > prev_max_energy:
                delta = curr_max_energy - prev_max_energy
                ship.resources.modify_value(ResourceType.ENERGY, delta)
            if ship.max_shields > prev_max_shields:
                ship.current_shields += (ship.max_shields - prev_max_shields)
        
        # Remember current max for next recalculate
        ship._prev_max_fuel = curr_max_fuel
        ship._prev_max_ammo = curr_max_ammo
        ship._prev_max_energy = curr_max_energy
        ship._prev_max_shields = ship.max_shields

    def calculate_ability_totals(self, components) -> dict:
        """Calculate total values for all abilities from components.

        Delegates to the extracted ability_aggregator module.
        """
        return calculate_ability_totals(components)

    def _get_ability_total(self, component_list, ability_name) -> float:
        """Calculate total value of a specific ability across provided components."""
        return get_ability_total(component_list, ability_name)
