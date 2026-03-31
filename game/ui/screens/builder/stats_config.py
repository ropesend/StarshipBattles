"""Stats configuration for the ship builder.

Defines stat definitions, formatters, and validators for ship statistics display.

Cross-layer imports (acceptable for builder UI):
- LayerType: Runtime - layer stat organization
"""
import logging
from game.core.constants import LayerType  # Canonical location for LayerType
from game.core.json_utils import load_json

logger = logging.getLogger(__name__)


class StatDefinition:
    """
    Defines a single stat row for the ship builder UI.

    INTENTIONAL DYNAMIC DISPATCH PATTERN:
    The `get_value()` method uses `getattr(ship, self.attr_key, 0)` intentionally.
    This is the core mechanism for declaratively mapping stat names to ship attributes
    via JSON configuration (stats_layout.json). The attr_key is a runtime string that
    cannot be replaced with typed access.

    DO NOT refactor get_value() to use direct attribute access - it must remain dynamic.
    """

    def __init__(self, id, label, key=None, getter=None, formatter="{:.0f}", unit="", validator=None):
        self.key = id  # Unique ID for the row map
        self.attr_key = key if key is not None else id  # Attribute on ship object
        self.label = label
        self.getter = getter
        self.formatter = formatter
        self.unit = unit
        self.validator = validator  # func(ship, value) -> (is_ok, status_text)

    def get_value(self, ship):
        """Get stat value from ship using configured getter or dynamic attr lookup."""
        if self.getter:
            if callable(self.getter):
                return self.getter(ship)
            return getattr(ship, self.getter, 0)
        # INTENTIONAL: Dynamic attribute lookup - see class docstring
        return getattr(ship, self.attr_key, 0)

    def format_value(self, val):
        if callable(self.formatter):
            return self.formatter(val)
        return self.formatter.format(val)

    def get_display_unit(self, ship, val):
        if callable(self.unit):
            return self.unit(ship, val)
        return self.unit
        
    def get_status(self, ship, val):
        if self.validator:
            return self.validator(ship, val)
        return (True, "")

# --- Formatters ---
def fmt_time(val):
    if val == float('inf') or val > 999999:  # ~277 hours before showing "Infinite"
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

# --- Helpers ---
def _get_total_crew_requirement(ship):
    """Get total crew requirement from CrewRequired ability.

    Note: Legacy pattern using negative CrewCapacity was removed in PROJ-42
    as no components in components.json use that pattern.
    """
    return ship.get_ability_total('CrewRequired')


# --- Validators ---
def mass_validator(ship, val):
    return (ship.mass_limits_ok, "✓" if ship.mass_limits_ok else "✗")

def crew_validator(ship, val):
    # val is crew_housed (capacity)
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

def fmt_targeting(val):
    return "Single" if val == 1 else f"Multi ({val})"

# --- New Getters (Logistics Update) ---
def get_armor_hp(ship):
    from game.core.constants import LayerType
    if LayerType.ARMOR in ship.layers:
        return ship.layers[LayerType.ARMOR].max_hp_pool
    return 0

def get_maneuver_points(ship):
    return ship.total_maneuver_points

def get_strategic_speed(ship):
    """Calculate strategic speed (hexes per turn) from movement points and mass."""
    # Uses same formula as FleetSpeedCalculator
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


# --- New Generic Getters (Dynamic Resource System) ---
def get_resource_storage(ship, res_name):
    """Get max storage for a specific resource."""
    r = ship.resources.get_resource(res_name)
    return r.max_value if r else 0

def get_resource_current(ship, res_name):
    """Get current value (for battle or init state) for a specific resource."""
    r = ship.resources.get_resource(res_name)
    return r.current_value if r else 0

def get_resource_generation(ship, res_name):
    """Get generation/regen rate for a specific resource."""
    r = ship.resources.get_resource(res_name)
    return r.regen_rate if r else 0

def get_resource_consumption(ship, res_name):
    """
    Get total consumption for a resource.
    First checks ship attributes (set by combat_endurance.py), then falls back to
    calculating constant consumption from component abilities.
    """
    # First check ship-level consumption attribute (includes activation-based consumption)
    # PROJ-194: Use typed accessor instead of dynamic f-string getattr
    val = ship.get_resource_stat(res_name, 'consumption')
    if val > 0:
        return val

    # Fallback: Calculate constant consumption from component abilities
    from game.simulation.components.abilities.resources import ResourceConsumption
    total = 0
    # Iterate all components in all layers
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
    """
    Get maximum resource usage (constant + max activation rate).
    Uses 'potential' stats to ensure UI shows component load even if currently inactive (e.g. no crew).
    """
    # PROJ-194: Use typed accessor instead of dynamic attr lookup
    # Try potential consumption first (e.g., 'potential_fuel' + '_consumption')
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

    # Fallback to standard consumption if potential not calculated
    val = ship.get_resource_stat(res_name, 'consumption')
    if val > 0:
        return val

    return 0

# --- Config Groups ---


# --- Function Registry ---
# Maps string names from JSON to actual functions

GETTERS = {
    'get_mass_display': get_mass_display,
    'get_crew_required': get_crew_required,
    'get_crew_capacity': get_crew_capacity,
    'get_life_support': get_life_support,
    'get_max_targets': get_max_targets,
    'get_armor_hp': get_armor_hp,
    'get_maneuver_points': get_maneuver_points,
    'get_strategic_speed': get_strategic_speed,

    # Generic Resource Getters
    'get_resource_storage': get_resource_storage,
    'get_resource_current': get_resource_current,
    'get_resource_generation': get_resource_generation,
    'get_resource_consumption': get_resource_consumption,
    'get_resource_endurance': get_resource_endurance,
    'get_resource_replenish': get_resource_replenish,
    'get_resource_max_usage': get_resource_max_usage,

    # Type-specific consumption getters (used by stats_layout.json)
    'get_fuel_consumption': get_fuel_consumption,
    'get_ammo_consumption': get_ammo_consumption,
    'get_energy_consumption': get_energy_consumption
}

FORMATTERS = {
    'fmt_time': fmt_time,
    'fmt_multiply': fmt_multiply,
    'fmt_decimal': fmt_decimal,
    'fmt_score': fmt_score,
    'fmt_targeting': fmt_targeting
}

VALIDATORS = {
    'mass_validator': mass_validator,
    'crew_validator': crew_validator,
    'life_support_validator': life_support_validator
}

# lambda s, v: f"/ {s.max_mass_budget}" cannot be easily jsonified.
# We will create a named function for it.
def mass_unit_func(ship, val):
    return f"/ {ship.max_mass_budget}"

UNITS = {
    'mass_unit': mass_unit_func
}

def load_stats_config():
    """Load stats configuration from data/stats_layout.json."""
    import os

    path = os.path.join(os.getcwd(), 'data', 'stats_layout.json')
    data = load_json(path, default={})
    if not data:
        logger.warning(f"Stats config not found or empty: {path}")
        return {}
        
    loaded_groups = {}
    
    if 'groups' not in data:
        return {}
        
    for group_key, group_data in data['groups'].items():
        items = []
        for item_data in group_data.get('items', []):
            # Resolve functions
            raw_getter = GETTERS.get(item_data.get('getter')) if item_data.get('getter') else None
            
            # Helper to bind arguments if provided
            getter = raw_getter
            if raw_getter and item_data.get('getter_args'):
                args = item_data['getter_args']
                # Create a closure that calls the getter with ship + args
                # Use default arg hack to capture loop variable/list value
                getter = lambda s, g=raw_getter, a=args: g(s, *a)
            
            fmt_val = item_data.get('formatter', "{:.0f}")
            formatter = FORMATTERS.get(fmt_val, fmt_val) # Try lookup, else treat as string
            
            unit_val = item_data.get('unit', "")
            unit = UNITS.get(unit_val, unit_val)
            
            validator = VALIDATORS.get(item_data.get('validator')) if item_data.get('validator') else None
            
            stat_def = StatDefinition(
                id=item_data['id'],
                label=item_data['label'],
                key=item_data.get('key'),
                getter=getter,
                formatter=formatter,
                unit=unit,
                validator=validator
            )
            items.append(stat_def)
        loaded_groups[group_key] = items
        
    return loaded_groups

# Load on module import
STATS_CONFIG = load_stats_config()

STATS_MAIN = STATS_CONFIG.get('main', [])
STATS_MANEUVERING = STATS_CONFIG.get('maneuvering', [])
STATS_SHIELDS = STATS_CONFIG.get('shields', [])
STATS_ARMOR = STATS_CONFIG.get('armor', [])
STATS_TARGETING = STATS_CONFIG.get('targeting', [])
STATS_LOGISTICS = STATS_CONFIG.get('logistics', [])
STATS_CREW_LOGISTICS = STATS_CONFIG.get('crewlogistics', [])
STATS_FIGHTER_SUPPORT = STATS_CONFIG.get('fightersupport', [])

# --- Dynamic Row Generators ---

def _get_constant_consumption(ship, res_name):
    """Get constant consumption rate for a resource (excludes activation-based)."""
    from game.simulation.components.abilities.resources import ResourceConsumption
    total = 0
    try:
        for layer in ship.layers.values():
            for comp in layer.components:
                for ability in comp.ability_instances:
                    if isinstance(ability, ResourceConsumption):
                        if ability.resource_type == res_name and ability.trigger == 'constant':
                            total += ability.amount
    except (TypeError, AttributeError):
        # Handle mock objects or missing attributes
        pass
    return total


def _get_max_endurance(ship, res_name):
    """Calculate endurance at max usage rate (constant + all weapons firing)."""
    try:
        capacity = get_resource_storage(ship, res_name)
        max_usage = get_resource_max_usage(ship, res_name)
        if not isinstance(max_usage, (int, float)) or max_usage <= 0:
            return float('inf')
        if not isinstance(capacity, (int, float)):
            return float('inf')
        return capacity / max_usage
    except (TypeError, AttributeError):
        return float('inf')


def _discover_resources(ship):
    """Discover all resource names present on a ship from 3 sources and return sorted.

    Sources:
    1. Resource registry (ship.resources.get_resource_names())
    2. Consumption attributes ({resource}_consumption)
    3. Generation attributes ({resource}_generation)

    Returns sorted list: Fuel, Energy, Ammo first, then others alphabetically.
    """
    resource_order = ["fuel", "energy", "ammo"]

    # Get all resource names from registry
    res_names = set(ship.resources.get_resource_names())

    # Also discover resources from consumption/generation attributes
    # This handles the case where a weapon consumes a resource but no storage exists
    # PROJ-194: Use typed accessor instead of dynamic f-string getattr
    for stat_type in ['consumption', 'generation']:
        for res in resource_order:
            val = ship.get_resource_stat(res, stat_type)
            if val > 0:
                res_names.add(res)

    res_names = list(res_names)

    # Sort based on preferred order
    def sort_key(name):
        if name in resource_order:
            return resource_order.index(name)
        return 999  # Others at end

    res_names.sort(key=sort_key)
    return res_names


def _build_resource_rows(ship, resource_name):
    """Build conditional stat rows (1-7 StatDefinition rows) for a single resource.

    Row types generated based on resource state:
    1. Capacity (if storage > 0)
    2. Generation (if generation > 0)
    3. Constant Consumption (if constant consumption > 0)
    4. Max Usage (if max usage > 0)
    5. Endurance at constant consumption (if storage and constant consumption)
       OR Endurance at max load (if no constant but has max usage)
    6. Max Endurance (if max usage > constant and both exist)
    7. Recharge time (if generation only, no consumption)

    Returns empty list if resource is truly unused (no storage, consumption, or generation).
    """
    try:
        r = ship.resources.get_resource(resource_name)
        max_value = r.max_value if r else 0
        if not isinstance(max_value, (int, float)):
            max_value = 0

        # Check consumption and generation to determine if resource is used
        const_consumption = _get_constant_consumption(ship, resource_name)
        if not isinstance(const_consumption, (int, float)):
            const_consumption = 0
        max_usage = get_resource_max_usage(ship, resource_name)
        if not isinstance(max_usage, (int, float)):
            max_usage = 0
        generation = get_resource_generation(ship, resource_name)
        if not isinstance(generation, (int, float)):
            generation = 0

        # Skip only if NO storage AND NO consumption AND NO generation (truly unused)
        if max_value <= 0 and const_consumption <= 0 and max_usage <= 0 and generation <= 0:
            return []
    except (TypeError, AttributeError):
        # Skip resources that can't be processed (e.g., mock objects)
        return []

    rows = []
    # Capitalize name
    label_base = resource_name.title()

    # 1. Capacity Row (only if storage exists)
    if max_value > 0:
        cap_row = StatDefinition(
            id=f"max_{resource_name}",
            label=f"{label_base} Capacity",
            getter=lambda s, n=resource_name: get_resource_storage(s, n),
            formatter="{:.0f}",
            unit=""
        )
        rows.append(cap_row)

    # 2. Generation Row (if generation exists)
    if generation > 0:
        gen_row = StatDefinition(
            id=f"{resource_name}_gen",
            label=f"{label_base} Generation",
            getter=lambda s, n=resource_name: get_resource_generation(s, n),
            formatter="{:.1f}",
            unit="/s"
        )
        rows.append(gen_row)

    # 3. Constant Consumption Row (if constant consumption exists)
    if const_consumption > 0:
        const_row = StatDefinition(
            id=f"{resource_name}_constant",
            label=f"{label_base} Constant Use",
            getter=lambda s, n=resource_name: _get_constant_consumption(s, n),
            formatter="{:.1f}",
            unit="/s"
        )
        rows.append(const_row)

    # 4. Max Usage Row (if max usage > constant, i.e. weapons exist)
    if max_usage > 0:
        max_use_row = StatDefinition(
            id=f"{resource_name}_max_usage",
            label=f"{label_base} Max Usage",
            getter=lambda s, n=resource_name: get_resource_max_usage(s, n),
            formatter="{:.1f}",
            unit="/s"
        )
        rows.append(max_use_row)

    # 5. Endurance at constant consumption (if has storage and consumption)
    if max_value > 0 and const_consumption > 0:
        end_row = StatDefinition(
            id=f"{resource_name}_endurance",
            label=f"{label_base} Endurance",
            getter=lambda s, n=resource_name: get_resource_endurance(s, n),
            formatter=fmt_time,
            unit=""
        )
        rows.append(end_row)
    elif max_usage > 0:
        # No constant consumption but has max usage - show endurance at max usage
        end_row = StatDefinition(
            id=f"{resource_name}_endurance",
            label=f"{label_base} Endurance",
            getter=lambda s, n=resource_name: _get_max_endurance(s, n),
            formatter=fmt_time,
            unit=""
        )
        rows.append(end_row)

    # 6. Max Endurance Row (if max usage differs from constant)
    if max_value > 0 and max_usage > const_consumption and const_consumption > 0:
        max_end_row = StatDefinition(
            id=f"{resource_name}_max_endurance",
            label=f"{label_base} Max Endurance",
            getter=lambda s, n=resource_name: _get_max_endurance(s, n),
            formatter=fmt_time,
            unit=""
        )
        rows.append(max_end_row)

    # Recharge time (if generation exists but no consumption)
    if generation > 0 and const_consumption <= 0 and max_usage <= 0 and max_value > 0:
        rech_row = StatDefinition(
            id=f"{resource_name}_recharge",
            label=f"{label_base} Recharge",
            getter=lambda s, n=resource_name: get_resource_replenish(s, n),
            formatter=fmt_time,
            unit=""
        )
        rows.append(rech_row)

    return rows


def get_logistics_rows(ship):
    """
    Generate the list of stat rows for the Logistics section.
    Combines static rows (mass, etc.) with dynamic resource rows.

    BUG-05 Fix: Generates all 6 rows per resource:
    1. Capacity (max_{resource})
    2. Generation ({resource}_gen)
    3. Constant Consumption ({resource}_constant)
    4. Max Usage ({resource}_max_usage)
    5. Endurance at constant ({resource}_endurance)
    6. Endurance at max load ({resource}_max_endurance)
    """
    # Generate dynamic resource rows based on ship's resources
    # ship.resources is always present (initialized as ResourceRegistry() in Ship.__init__)
    res_names = _discover_resources(ship)

    dynamic_rows = []
    for r_name in res_names:
        dynamic_rows.extend(_build_resource_rows(ship, r_name))

    return dynamic_rows


def get_construction_rows(ship):
    """
    Generate the list of stat rows for the Construction section.
    """
    from game.core.resources import ResourceCatalog
    PLANET_RESOURCE_NAMES = [d.id for d in ResourceCatalog.from_json().by_display_group("planetary")]

    # Abbreviations for narrow label columns
    LABEL_ABBREV = {
        "metals": "Metals",
        "organics": "Organics",
        "vapors": "Vapors",
        "radioactives": "Radact",
        "exotics": "Exotics",
    }

    rows = []

    # Construction costs from ship.construction_cost
    for res in PLANET_RESOURCE_NAMES:
        # Use a closure to capture res
        # ship.construction_cost is always present (initialized as {} in Ship.__init__)
        def res_getter(ship, r=res):
            return ship.construction_cost.get(r, 0)

        row = StatDefinition(
            id=f"cost_{res.lower()}",
            label=LABEL_ABBREV.get(res, res),
            getter=res_getter,
            formatter="{:.0f}",
            unit=""
        )
        rows.append(row)

    return rows
