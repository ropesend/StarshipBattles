"""Stat value getters, formatters, validators, and function registries.

These functions are referenced by name from stats_layout.json and resolved
at load time via the GETTERS, FORMATTERS, VALIDATORS, and UNITS registries.
"""

# --- Formatters ---

def fmt_time(val):
    if val == float('inf') or val > 999999:
        return "Infinite"
    if val <= 0:
        return "0.0s"
    if val > 3600:
        return f"{val/3600:.1f}h"
    if val > 60:
        return f"{val/60:.1f}m"
    return f"{val:.1f}s"

def fmt_multiply(val):
    return f"{val:.4f}"

def fmt_decimal(val):
    return f"{val:.1f}"

def fmt_score(val):
    return f"+{val:.1f}" if val >= 0 else f"{val:.1f}"

def fmt_targeting(val):
    return "Single" if val == 1 else f"Multi ({val})"


# --- Helpers ---

def _get_total_crew_requirement(ship):
    """Get total crew requirement from CrewRequired ability."""
    return ship.get_ability_total('CrewRequired')


# --- Validators ---

def mass_validator(ship, val):
    return (ship.mass_limits_ok, "✓" if ship.mass_limits_ok else "✗")

def crew_validator(ship, val):
    req = _get_total_crew_requirement(ship)
    if val >= req:
        return (True, "✓")
    return (False, f"✗ Miss {req - val}")

def life_support_validator(ship, val):
    req = _get_total_crew_requirement(ship)
    if val >= req:
        return (True, "✓")
    return (False, f"✗ -{req - val}")


# --- Getters ---

def get_mass_display(ship):
    return ship.mass

def get_crew_required(ship):
    return _get_total_crew_requirement(ship)

def get_crew_capacity(ship):
    return max(0, ship.get_ability_total('CrewCapacity'))

def get_life_support(ship):
    return ship.get_ability_total('LifeSupportCapacity')

def get_max_targets(ship):
    return ship.max_targets

def get_armor_hp(ship):
    from game.core.constants import LayerType
    if LayerType.ARMOR in ship.layers:
        return ship.layers[LayerType.ARMOR].max_hp_pool
    return 0

def get_maneuver_points(ship):
    return ship.total_maneuver_points

def get_strategic_speed(ship):
    """Calculate strategic speed (hexes per turn) from movement points and mass."""
    K_STRATEGIC = 25
    MAX_HEXES = 10
    MIN_HEXES = 0
    mass = ship.mass
    movement_points = ship.total_strategic_movement
    if mass <= 0 or movement_points <= 0:
        return 0
    raw_hexes = (movement_points * K_STRATEGIC) / mass
    return max(MIN_HEXES, min(MAX_HEXES, int(raw_hexes)))

def get_fuel_consumption(ship):
    return ship.fuel_consumption

def get_ammo_consumption(ship):
    return ship.ammo_consumption

def get_energy_consumption(ship):
    return ship.energy_consumption


# --- Generic Resource Getters ---

def get_resource_storage(ship, res_name):
    """Get max storage for a specific resource."""
    r = ship.resources.get_resource(res_name)
    return r.max_value if r else 0

def get_resource_current(ship, res_name):
    """Get current value for a specific resource."""
    r = ship.resources.get_resource(res_name)
    return r.current_value if r else 0

def get_resource_generation(ship, res_name):
    """Get generation/regen rate for a specific resource."""
    r = ship.resources.get_resource(res_name)
    return r.regen_rate if r else 0

def get_resource_consumption(ship, res_name):
    """Get total consumption for a resource."""
    val = ship.get_resource_stat(res_name, 'consumption')
    if val > 0:
        return val
    from game.simulation.components.abilities.resources import ResourceConsumption
    total = 0
    for layer in ship.layers.values():
        for comp in layer.components:
            for ability in comp.ability_instances:
                if isinstance(ability, ResourceConsumption):
                    if ability.resource_type == res_name and ability.trigger == 'constant':
                        total += ability.amount
    return total

def get_resource_endurance(ship, res_name):
    """Calculate endurance (time to empty) based on max storage and constant consumption."""
    capacity = get_resource_storage(ship, res_name)
    burn = get_resource_consumption(ship, res_name)
    if burn <= 0:
        return float('inf')
    return capacity / burn

def get_resource_replenish(ship, res_name):
    """Calculate time to full from empty based on regen."""
    capacity = get_resource_storage(ship, res_name)
    regen = get_resource_generation(ship, res_name)
    if regen <= 0:
        return float('inf')
    return capacity / regen

def get_resource_max_usage(ship, res_name):
    """Get maximum resource usage (constant + max activation rate)."""
    potential_map = {
        "fuel": 'potential_fuel',
        "ammo": 'potential_ammo',
        "energy": 'potential_energy'
    }
    potential_res = potential_map.get(res_name)
    if potential_res:
        val = ship.get_resource_stat(potential_res, 'consumption')
        if val > 0:
            return val
    val = ship.get_resource_stat(res_name, 'consumption')
    if val > 0:
        return val
    return 0


# --- Function Registries ---

GETTERS = {
    'get_mass_display': get_mass_display,
    'get_crew_required': get_crew_required,
    'get_crew_capacity': get_crew_capacity,
    'get_life_support': get_life_support,
    'get_max_targets': get_max_targets,
    'get_armor_hp': get_armor_hp,
    'get_maneuver_points': get_maneuver_points,
    'get_strategic_speed': get_strategic_speed,
    'get_resource_storage': get_resource_storage,
    'get_resource_current': get_resource_current,
    'get_resource_generation': get_resource_generation,
    'get_resource_consumption': get_resource_consumption,
    'get_resource_endurance': get_resource_endurance,
    'get_resource_replenish': get_resource_replenish,
    'get_resource_max_usage': get_resource_max_usage,
    'get_fuel_consumption': get_fuel_consumption,
    'get_ammo_consumption': get_ammo_consumption,
    'get_energy_consumption': get_energy_consumption,
}

FORMATTERS = {
    'fmt_time': fmt_time,
    'fmt_multiply': fmt_multiply,
    'fmt_decimal': fmt_decimal,
    'fmt_score': fmt_score,
    'fmt_targeting': fmt_targeting,
}

VALIDATORS = {
    'mass_validator': mass_validator,
    'crew_validator': crew_validator,
    'life_support_validator': life_support_validator,
}

def mass_unit_func(ship, val):
    return f"/ {ship.max_mass_budget}"

UNITS = {
    'mass_unit': mass_unit_func,
}
