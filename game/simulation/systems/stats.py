from typing import Any, Dict, List, Tuple, Union
from game.simulation.components.component_constants import ComponentStatus
from game.core.constants import LayerType, CombatConstants
from game.simulation.physics_constants import K_SPEED, K_THRUST, K_TURN
from game.simulation.systems.resource_manager import (
    ResourceStorage, ResourceGeneration, ResourceConsumption
)
import math


class ShipStatsCalculator:
    """
    Encapsulates the logic for calculating ship statistics from its components.

    The calculate() method orchestrates 5 phases:
    1. Damage check and resource gathering
    2. Crew and life support allocation
    3. Component stats aggregation
    4. Physics limits and radius
    5. Combat stats (defense score, abilities)
    """

    def __init__(self, vehicle_classes):
        self.vehicle_classes = vehicle_classes

    def calculate(self, ship) -> None:
        """
        Recalculates all derived stats for the ship based on its components and class.

        Orchestrates 5 calculation phases in sequence, each handled by a dedicated
        helper method for maintainability.
        """
        # Reset base calculations
        self._reset_base_stats(ship)

        # Phase 1: Check damage and gather crew/life support resources
        component_pool, available_crew, available_life_support = \
            self._check_damage_and_gather_resources(ship)

        # Phase 2: Allocate crew and life support to components
        self._allocate_crew_and_life_support(
            ship, component_pool, available_crew, available_life_support
        )

        # Phase 3: Aggregate stats from active components
        self._aggregate_component_stats(ship, component_pool)

        # Phase 4: Apply physics calculations and limits
        self._apply_physics_limits(ship)

        # Phase 5: Calculate combat stats (defense score, abilities)
        self._calculate_combat_stats(ship, component_pool)

        # Finalize: Initialize resources and calculate endurance
        self._finalize_resources(ship, component_pool)

    def _reset_base_stats(self, ship) -> None:
        """Reset all ship stats to base values before recalculation."""
        ship.current_mass = 0
        ship.layer_status = {}
        ship.mass_limits_ok = True
        ship.drag = 0.5

        # Calculate Mass (dead weight remains)
        for layer_type, layer_data in ship.layers.items():
            l_mass = sum(c.mass for c in layer_data['components'])
            layer_data['mass'] = l_mass
            ship.current_mass += l_mass

        ship.mass = ship.current_mass + ship.base_mass

        # Base Stats Reset
        ship.total_thrust = 0
        ship.turn_speed = 0
        ship.resources.reset_stats()

        ship.max_shields = 0
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

    def _check_damage_and_gather_resources(
        self, ship
    ) -> Tuple[List[Any], int, int]:
        """
        Phase 1: Check component damage and gather crew/life support resources.

        Returns:
            Tuple of (component_pool, available_crew, available_life_support)
        """
        available_crew = 0
        available_life_support = 0
        component_pool = []

        for layer_type, layer_data in ship.layers.items():
            for comp in layer_data['components']:
                # Reset Status Assumption
                comp.is_active = True
                comp.status = ComponentStatus.ACTIVE

                # Check Damage Threshold (ignore Armor - uses HP pool)
                if not comp.abilities.get('Armor', False):
                    if comp.max_hp > 0 and (comp.current_hp / comp.max_hp) <= CombatConstants.DEFAULT_DAMAGE_THRESHOLD:
                        comp.is_active = False
                        comp.status = ComponentStatus.DAMAGED

                # If armor is dead (0 hp), it's inactive
                if comp.abilities.get('Armor', False) and comp.current_hp <= 0:
                    comp.is_active = False
                    comp.status = ComponentStatus.DAMAGED

                # Gather Supply from FUNCTIONAL components
                if comp.is_active:
                    for ab in comp.get_abilities('CrewCapacity'):
                        available_crew += ab.amount

                    for ab in comp.get_abilities('LifeSupportCapacity'):
                        available_life_support += ab.amount

                component_pool.append(comp)

        return component_pool, available_crew, available_life_support

    def _allocate_crew_and_life_support(
        self, ship, component_pool: List[Any],
        available_crew: int, available_life_support: int
    ) -> None:
        """
        Phase 2: Allocate crew and life support to components.

        Deactivates components that lack required crew.
        """
        # Store for UI
        ship.crew_onboard = available_crew
        ship.crew_required = 0
        ship.max_targets = 1  # Reset to default

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

    def _aggregate_component_stats(self, ship, component_pool: List[Any]) -> None:
        """
        Phase 3: Aggregate stats from all active components.

        Collects thrust, shields, resources, hangar stats, etc.
        """
        # Local accumulators for atomic updates
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
            if not comp.is_active:
                continue

            # Resource abilities
            if hasattr(comp, 'ability_instances'):
                for ability in comp.ability_instances:
                    if isinstance(ability, ResourceStorage):
                        if ability.resource_type == 'fuel':
                            total_max_fuel += ability.max_amount
                        elif ability.resource_type == 'ammo':
                            total_max_ammo += ability.max_amount
                        elif ability.resource_type == 'energy':
                            total_max_energy += ability.max_amount
                    elif isinstance(ability, ResourceGeneration):
                        if ability.resource_type == 'energy':
                            total_energy_gen += ability.rate
                        elif ability.resource_type == 'ammo':
                            total_ammo_gen += ability.rate

            # Thrust from CombatPropulsion abilities
            for ab in comp.get_abilities('CombatPropulsion'):
                total_thrust += ab.thrust_force

            # Turn speed from ManeuveringThruster abilities
            for ab in comp.get_abilities('ManeuveringThruster'):
                total_turn_speed += ab.turn_rate
                ship.total_maneuver_points += ab.turn_rate

            # Armor HP pool
            if comp.abilities.get('Armor', False):
                if LayerType.ARMOR in ship.layers:
                    ship.layers[LayerType.ARMOR]['max_hp_pool'] += comp.max_hp

            # Shields from ShieldProjection abilities
            for ab in comp.get_abilities('ShieldProjection'):
                total_max_shields += ab.capacity

            # Shield regen from ShieldRegeneration abilities
            for ab in comp.get_abilities('ShieldRegeneration'):
                total_shield_regen += ab.rate

            # Shield energy cost
            if comp.has_ability('ShieldRegeneration'):
                for ab in comp.ability_instances:
                    if isinstance(ab, ResourceConsumption) and ab.resource_name == 'energy':
                        total_shield_cost += ab.amount
                        break

            # Hangar stats
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

            # MultiplexTracking
            mt = comp.abilities.get('MultiplexTracking', 0)
            if mt > 0:
                if mt > ship.max_targets:
                    ship.max_targets = mt

        # Apply Accumulated Totals Atomically
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

    def _apply_physics_limits(self, ship) -> None:
        """
        Phase 4: Apply physics calculations and mass limits.

        Calculates acceleration, max speed, turn rate, and radius.
        """
        # Derelict Check - REMOVED per user request
        ship.is_derelict = False

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
        base_radius = 40
        ref_mass = 1000
        actual_mass = max(ship.mass, 100)
        ratio = actual_mass / ref_mass
        ship.radius = base_radius * (ratio ** (1/3.0))

    def _calculate_combat_stats(self, ship, component_pool: List[Any]) -> None:
        """
        Phase 5: Calculate to-hit and electronic warfare stats.

        Computes defense score from size, maneuver, and ECM.
        """
        # Defense Score (Higher = Harder to Hit)
        diameter = ship.radius * 2

        # Size Score: Baseline Diameter 80 (Mass ~1k) = 0.0
        d_ratio = max(0.1, diameter / 80.0)
        size_score = -2.5 * math.log10(d_ratio)

        # Maneuver Score
        maneuver_score = math.sqrt(
            (ship.acceleration_rate / 20.0) + (ship.turn_speed / 360.0)
        )

        # ECM Score (Additive)
        ecm_score = self._get_ability_total(component_pool, 'ToHitDefenseModifier')
        if isinstance(ecm_score, bool):
            ecm_score = 0.0

        # Total Defense Score
        ship.total_defense_score = size_score + maneuver_score + ecm_score
        ship.to_hit_profile = ship.total_defense_score  # Legacy alias

        # Offensive Baseline (Sensor Strength)
        attack_mods = self._get_ability_total(component_pool, 'ToHitAttackModifier')
        if isinstance(attack_mods, bool):
            attack_mods = 0.0
        ship.baseline_to_hit_offense = attack_mods

        # Emissive Armor (Max Stacking)
        ship.emissive_armor = self._get_ability_total(component_pool, 'EmissiveArmor')

        # Crystalline Armor (Max Stacking)
        ship.crystalline_armor = self._get_ability_total(component_pool, 'CrystallineArmor')

        # Ship Repair (SumStacking)
        ship.repair_rate = self._get_ability_total(component_pool, 'ShipRepair')

        # Ammo Generation (SumStacking)
        ship.ammo_gen_rate = self._get_ability_total(component_pool, 'AmmoGeneration')

    def _finalize_resources(self, ship, component_pool: List[Any]) -> None:
        """Finalize resource initialization and calculate combat endurance."""
        # Armor Pool Init (if starting)
        if LayerType.ARMOR in ship.layers:
            if ship.layers[LayerType.ARMOR]['hp_pool'] == 0:
                ship.layers[LayerType.ARMOR]['hp_pool'] = ship.layers[LayerType.ARMOR]['max_hp_pool']

        # Initialize Resources
        self._initialize_resources(ship)

        # Combat Endurance Stats
        self._calculate_combat_endurance(ship, component_pool)

    def _calculate_combat_endurance(self, ship, component_pool: List[Any]) -> None:
        """Calculate endurance times for Fuel, Ammo, and Energy."""
        fuel_consumption = 0.0
        ammo_consumption = 0.0
        energy_consumption = 0.0

        for c in component_pool:
            if not c.is_active:
                continue

            if hasattr(c, 'ability_instances'):
                for ab in c.ability_instances:
                    if isinstance(ab, ResourceConsumption):
                        if ab.trigger == 'constant':
                            if ab.resource_name == 'fuel':
                                fuel_consumption += ab.amount
                            elif ab.resource_name == 'energy':
                                energy_consumption += ab.amount
                            elif ab.resource_name == 'ammo':
                                ammo_consumption += ab.amount
                        elif ab.trigger == 'activation':
                            reload_t = getattr(c, 'reload_time', 1.0)
                            if reload_t > 0:
                                rate = ab.amount / reload_t
                                if ab.resource_name == 'ammo':
                                    ammo_consumption += rate
                                elif ab.resource_name == 'energy':
                                    energy_consumption += rate

        # Add aggregated shield cost (worst case continuous regen)
        energy_consumption += ship.shield_regen_cost

        ship.fuel_consumption = fuel_consumption
        max_fuel = ship.resources.get_max_value('fuel')
        ship.fuel_endurance = (max_fuel / fuel_consumption) if fuel_consumption > 0 else float('inf')

        ship.ammo_consumption = ammo_consumption
        max_ammo = ship.resources.get_max_value('ammo')
        ship.ammo_endurance = (max_ammo / ammo_consumption) if ammo_consumption > 0 else float('inf')

        ship.energy_consumption = energy_consumption
        r_energy = ship.resources.get_resource('energy')
        energy_gen_rate = r_energy.regen_rate if r_energy else 0.0

        ship.energy_net = energy_gen_rate - energy_consumption

        max_energy = ship.resources.get_max_value('energy')

        if ship.energy_net < 0:
            drain_rate = abs(ship.energy_net)
            ship.energy_endurance = max_energy / drain_rate
        else:
            ship.energy_endurance = float('inf')

        if energy_gen_rate > 0:
            ship.energy_recharge = max_energy / energy_gen_rate
        else:
            ship.energy_recharge = float('inf')

        # Populate Cached Summary
        dps = 0
        for layer in ship.layers.values():
            for c in layer['components']:
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

    def _priority_sort_key(self, c: Any) -> int:
        """Return sort priority for component (lower = higher priority)."""
        if c.has_ability('CommandAndControl'):
            return 0
        if c.has_ability('CombatPropulsion') or c.has_ability('ManeuveringThruster'):
            return 1
        if c.has_ability('WeaponAbility'):
            return 2
        return 3

    def _check_mass_limits(self, ship: Any) -> None:
        """Check if ship meets mass budget constraints."""
        ship.mass_limits_ok = True
        ship.max_mass_budget = 1000  # Default

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
            if not is_ok:
                ship.mass_limits_ok = False

        if ship.mass > ship.max_mass_budget:
            ship.mass_limits_ok = False

    def _initialize_resources(self, ship: Any) -> None:
        """Initialize or update resource values based on capacity changes."""
        prev_max_fuel = ship._prev_max_fuel
        prev_max_ammo = ship._prev_max_ammo
        prev_max_energy = ship._prev_max_energy
        prev_max_shields = ship._prev_max_shields

        curr_max_fuel = ship.resources.get_max_value('fuel')
        curr_max_ammo = ship.resources.get_max_value('ammo')
        curr_max_energy = ship.resources.get_max_value('energy')

        if not ship._resources_initialized:
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

        ship._prev_max_fuel = curr_max_fuel
        ship._prev_max_ammo = curr_max_ammo
        ship._prev_max_energy = curr_max_energy
        ship._prev_max_shields = ship.max_shields

    def calculate_ability_totals(self, components: List[Any]) -> Dict[str, Any]:
        """
        Calculate total values for all abilities from components.

        Supports 'stack_group' in ability definition for redundancy (MAX) vs stacking (SUM/MULT).
        """
        totals = {}
        MULTIPLICATIVE_ABILITIES = {'ToHitAttackModifier', 'ToHitDefenseModifier'}
        ability_groups: Dict[str, Dict[Any, List[Any]]] = {}

        for comp in components:
            handled_abilities = set()

            if hasattr(comp, 'ability_instances') and isinstance(comp.ability_instances, dict):
                for ability_name, instances in comp.ability_instances.items():
                    handled_abilities.add(ability_name)
                    for ab in instances:
                        value = None
                        if hasattr(ab, 'amount'):
                            value = ab.amount
                        elif hasattr(ab, 'value'):
                            value = ab.value
                        elif ability_name == 'CommandAndControl':
                            value = True

                        if value is None:
                            continue

                        stack_group = getattr(ab, 'stack_group', None)
                        group_key = stack_group if stack_group else comp

                        if ability_name not in ability_groups:
                            ability_groups[ability_name] = {}
                        if group_key not in ability_groups[ability_name]:
                            ability_groups[ability_name][group_key] = []

                        ability_groups[ability_name][group_key].append(value)

            abilities = getattr(comp, 'abilities', {})
            if isinstance(abilities, dict):
                for ability_name, raw_value in abilities.items():
                    if ability_name in handled_abilities:
                        continue

                    value = raw_value
                    stack_group = None

                    if isinstance(raw_value, dict) and 'value' in raw_value:
                        value = raw_value['value']
                        stack_group = raw_value.get('stack_group')

                    group_key = stack_group if stack_group else comp

                    if ability_name not in ability_groups:
                        ability_groups[ability_name] = {}
                    if group_key not in ability_groups[ability_name]:
                        ability_groups[ability_name][group_key] = []

                    ability_groups[ability_name][group_key].append(value)

        for ability_name, groups in ability_groups.items():
            group_contributions = []

            for key, values in groups.items():
                nums = [v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
                if nums:
                    group_contributions.append(max(nums))
                elif any(v is True for v in values):
                    group_contributions.append(True)

            if not group_contributions:
                continue

            first = group_contributions[0]

            if isinstance(first, bool):
                totals[ability_name] = True
            else:
                if ability_name in MULTIPLICATIVE_ABILITIES:
                    val = 1.0
                    for v in group_contributions:
                        if isinstance(v, (int, float)):
                            val *= v
                    totals[ability_name] = val
                else:
                    val = sum(v for v in group_contributions if isinstance(v, (int, float)))
                    totals[ability_name] = val

        return totals

    def _get_ability_total(
        self, component_list: List[Any], ability_name: str
    ) -> Union[int, float, bool]:
        """Calculate total value of a specific ability across provided components."""
        totals = self.calculate_ability_totals(component_list)
        return totals.get(ability_name, 0)
