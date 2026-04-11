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


# --- Weapon Getters ---

def get_weapon_count(ship):
    """Count total weapon components on the ship."""
    count = 0
    for comp in ship.get_all_components():
        if comp.has_ability('WeaponAbility'):
            count += 1
    return count

def get_total_dps(ship):
    """Calculate total damage per second across all weapons."""
    summary = ship.cached_summary
    return summary.get('dps', 0) if summary else 0

def get_dps_duration(ship):
    """Calculate how long DPS can be sustained (min of ammo and energy endurance)."""
    ammo_end = getattr(ship, 'ammo_endurance', float('inf'))
    energy_end = getattr(ship, 'energy_endurance', float('inf'))
    return min(ammo_end, energy_end)

def get_max_range(ship):
    """Get maximum weapon range."""
    return ship.max_weapon_range


# --- Strategic Movement Getters ---

def get_warp_capable(ship):
    """Check if ship has warp capability."""
    return 1.0 if ship.warp_max_tonnage > 0 else 0.0

def get_warp_tonnage(ship):
    """Get maximum warp tonnage."""
    return ship.warp_max_tonnage

def get_warp_cost(ship):
    """Get warp energy cost per jump."""
    return ship.warp_energy_cost

def get_warp_jumps(ship):
    """Calculate number of warp jumps possible from full resources."""
    warp_costs = ship.warp_resource_costs
    if not warp_costs:
        return 0
    min_jumps = float('inf')
    for res_type, cost in warp_costs.items():
        if cost > 0:
            capacity = get_resource_storage(ship, res_type)
            jumps = int(capacity / cost) if capacity > 0 else 0
            min_jumps = min(min_jumps, jumps)
    return int(min_jumps) if min_jumps != float('inf') else 0

def get_fuel_per_hex(ship):
    """Get fuel consumption per strategic hex moved."""
    from game.simulation.components.abilities.resources import ResourceConsumption
    total = 0.0
    for layer in ship.layers.values():
        for comp in layer.components:
            for ability in comp.ability_instances:
                if isinstance(ability, ResourceConsumption):
                    if ability.resource_type == 'fuel' and ability.trigger == 'strategic_per_hex':
                        total += ability.amount
    return total

def get_hex_range(ship):
    """Calculate strategic hex range from fuel storage and per-hex consumption."""
    fuel_cap = get_resource_storage(ship, 'fuel')
    cost_per_hex = get_fuel_per_hex(ship)
    if cost_per_hex <= 0:
        return float('inf') if fuel_cap > 0 else 0
    return int(fuel_cap / cost_per_hex)


# --- Cargo & Transport Getters ---

def get_cargo_capacity(ship, cargo_type='generic'):
    """Get cargo capacity for a specific type."""
    return ship.cargo_storage.get(cargo_type, 0)

def get_passenger_capacity(ship):
    """Get passenger transport capacity."""
    return ship.cargo_storage.get('passengers', 0)

def get_pod_storage(ship):
    """Get pod/item storage mass capacity."""
    return ship.pod_storage_mass

def get_colony_types(ship):
    """Get list of planet types this design can colonize."""
    types = set()
    for comp in ship.get_all_components():
        if comp.has_ability('ColonizePlanet'):
            ab = comp.get_ability('ColonizePlanet')
            if hasattr(ab, 'planet_type'):
                types.add(ab.planet_type)
    return ', '.join(sorted(types)) if types else 'None'


# --- Superweapon Getters ---

_SUPERWEAPON_ABILITIES = [
    'DestroyPlanet', 'DestroyStar', 'OpenWarpPoint',
    'CloseWarpPoint', 'CreateDysonSphere', 'SelfDestruct',
]

_SUPERWEAPON_LABELS = {
    'DestroyPlanet': 'Planet Imploder',
    'DestroyStar': 'Stellerator',
    'OpenWarpPoint': 'Warp Point Creator',
    'CloseWarpPoint': 'Warp Point Closer',
    'CreateDysonSphere': 'Dyson Sphere Constructor',
    'SelfDestruct': 'Self-Destruct',
}

def get_superweapon_summary(ship):
    """Get formatted summary of superweapon capabilities with activation counts."""
    entries = []
    for ab_name in _SUPERWEAPON_ABILITIES:
        count = 0
        for comp in ship.get_all_components():
            if comp.has_ability(ab_name):
                count += 1
        if count > 0:
            label = _SUPERWEAPON_LABELS.get(ab_name, ab_name)
            entries.append(f"{label} x{count}")
    return '; '.join(entries) if entries else 'None'

def has_superweapons(ship):
    """Check if ship has any superweapon abilities."""
    for comp in ship.get_all_components():
        for ab_name in _SUPERWEAPON_ABILITIES:
            if comp.has_ability(ab_name):
                return True
    return False


# --- Misc Getters ---

def get_repair_rate(ship):
    """Get hull repair rate."""
    return ship.repair_rate

def get_command_status(ship):
    """Check if ship has command and control (bridge)."""
    for comp in ship.get_all_components():
        if comp.has_ability('CommandAndControl'):
            return 1.0
    return 0.0


# --- New Formatters ---

def fmt_yes_no(val):
    """Format boolean-like value as Yes/No."""
    return "Yes" if val > 0 else "No"

def fmt_int(val):
    """Format as integer."""
    if val == float('inf') or val > 999999:
        return "∞"
    return f"{int(val)}"

def fmt_text(val):
    """Format string values (pass-through)."""
    return str(val) if val else "None"


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
    # Weapons
    'get_weapon_count': get_weapon_count,
    'get_total_dps': get_total_dps,
    'get_dps_duration': get_dps_duration,
    'get_max_range': get_max_range,
    # Strategic movement
    'get_warp_capable': get_warp_capable,
    'get_warp_tonnage': get_warp_tonnage,
    'get_warp_cost': get_warp_cost,
    'get_warp_jumps': get_warp_jumps,
    'get_fuel_per_hex': get_fuel_per_hex,
    'get_hex_range': get_hex_range,
    # Cargo & transport
    'get_cargo_capacity': get_cargo_capacity,
    'get_passenger_capacity': get_passenger_capacity,
    'get_pod_storage': get_pod_storage,
    'get_colony_types': get_colony_types,
    # Superweapons
    'get_superweapon_summary': get_superweapon_summary,
    # Misc
    'get_repair_rate': get_repair_rate,
    'get_command_status': get_command_status,
}

FORMATTERS = {
    'fmt_time': fmt_time,
    'fmt_multiply': fmt_multiply,
    'fmt_decimal': fmt_decimal,
    'fmt_score': fmt_score,
    'fmt_targeting': fmt_targeting,
    'fmt_yes_no': fmt_yes_no,
    'fmt_int': fmt_int,
    'fmt_text': fmt_text,
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
