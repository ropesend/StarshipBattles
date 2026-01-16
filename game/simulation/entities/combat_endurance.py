"""Combat endurance calculations for ships.

This module calculates endurance times for Fuel, Ammo, and Energy,
as well as DPS and other combat-related statistics.
"""


def calculate_combat_endurance(ship, component_pool):
    """Calculate endurance times for Fuel, Ammo, and Energy.

    Args:
        ship: The ship to calculate endurance for
        component_pool: List of all components on the ship
    """
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
    if energy_gen_rate > 0:
        ship.energy_recharge = max_energy / energy_gen_rate
    else:
        ship.energy_recharge = float('inf')

    # Populate Cached Summary
    _calculate_cached_summary(ship)


def _calculate_cached_summary(ship):
    """Calculate and cache the ship's summary statistics."""
    dps = 0

    # Calculate theoretical max DPS (all weapons)
    for c in ship.get_all_components():
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
