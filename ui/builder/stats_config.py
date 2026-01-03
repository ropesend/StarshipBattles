from game.simulation.entities.ship import LayerType
import ship_stats # Needed for accessing defaults/constants if any


class StatDefinition:
    def __init__(self, id, label, key=None, getter=None, formatter="{:.0f}", unit="", validator=None):
        self.key = id # Unique ID for the row map
        self.attr_key = key if key is not None else id # Attribute on ship object
        self.label = label
        self.getter = getter
        self.formatter = formatter
        self.unit = unit
        self.validator = validator # func(ship, value) -> (is_ok, status_text)

    def get_value(self, ship):
        if self.getter:
            if callable(self.getter):
                return self.getter(ship)
            return getattr(ship, self.getter, 0)
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
    if val == float('inf') or val > 99999:
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

# --- Validators ---
def mass_validator(ship, val):
    return (ship.mass_limits_ok, "✓" if ship.mass_limits_ok else "✗")

def crew_validator(ship, val):
    # val is crew_housed (capacity)
    req = ship.get_ability_total('CrewRequired')
    # Legacy fallback logic from right_panel.py
    legacy_req = abs(min(0, ship.get_ability_total('CrewCapacity')))
    req += legacy_req
    
    if val >= req:
        return (True, "✓")
    return (False, f"✗ Miss {req - val}")

def life_support_validator(ship, val):
    req = ship.get_ability_total('CrewRequired')
    legacy_req = abs(min(0, ship.get_ability_total('CrewCapacity')))
    req += legacy_req
    
    if val >= req:
        return (True, "✓")
    return (False, f"✗ -{req - val}")

# --- Getters ---
def get_mass_display(ship):
    return ship.mass

def get_crew_required(ship):
    req = ship.get_ability_total('CrewRequired')
    legacy_req = abs(min(0, ship.get_ability_total('CrewCapacity')))
    return req + legacy_req

def get_crew_capacity(ship):
    return max(0, ship.get_ability_total('CrewCapacity'))
    
def get_life_support(ship):
    return ship.get_ability_total('LifeSupportCapacity')

def get_max_targets(ship):
    return getattr(ship, 'max_targets', 1)

def fmt_targeting(val):
    return "Single" if val == 1 else f"Multi ({val})"

# --- New Getters (Logistics Update) ---
def get_armor_hp(ship):
    from game.simulation.entities.ship import LayerType
    if LayerType.ARMOR in ship.layers:
        return ship.layers[LayerType.ARMOR].get('max_hp_pool', 0)
    return 0

def get_maneuver_points(ship):
    return getattr(ship, 'total_maneuver_points', 0)

def get_zero(ship):
    return 0

def get_fuel_recharge(ship):
    # Placeholder: No regen mechanism yet
    return 0
    
def get_ammo_recharge(ship):
    # Placeholder: No regen mechanism yet
    return 0
    
def get_fuel_consumption(ship):
    return getattr(ship, 'fuel_consumption', 0)

def get_ammo_consumption(ship):
    return getattr(ship, 'ammo_consumption', 0)

def get_energy_consumption(ship):
    return getattr(ship, 'energy_consumption', 0)


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
    Calculate constant consumption for a resource across all components.
    This aggregates 'ResourceConsumption' abilities with trigger='constant'.
    """
    from game.simulation.systems.resource_manager import ResourceConsumption
    total = 0
    # Iterate all components in all layers
    for layer in ship.layers.values():
        for comp in layer['components']:
            if hasattr(comp, 'ability_instances'):
                for ability in comp.ability_instances:
                    if isinstance(ability, ResourceConsumption):
                        if ability.resource_name == res_name and ability.trigger == 'constant':
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

# --- Config Groups ---


# --- Function Registry ---
# Maps string names from JSON to actual functions

GETTERS = {
    'get_mass_display': get_mass_display,
    'get_crew_required': get_crew_required,
    'get_crew_capacity': get_crew_capacity,
    'get_life_support': get_life_support,
    'get_max_targets': get_max_targets,
    # New
    'get_armor_hp': get_armor_hp,
    'get_maneuver_points': get_maneuver_points,
    'get_zero': get_zero,
    
    # Generic Resource Getters
    'get_resource_storage': get_resource_storage,
    'get_resource_current': get_resource_current,
    'get_resource_generation': get_resource_generation,
    'get_resource_consumption': get_resource_consumption,
    'get_resource_endurance': get_resource_endurance,
    'get_resource_replenish': get_resource_replenish,
    
    # Legacy (Mapped to Generics or Keep implementations?)
    # Kept for compatibility if JSON not fully migrated yet
    'get_fuel_recharge': get_fuel_recharge,
    'get_ammo_recharge': get_ammo_recharge,
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
    import json
    import os
    
    path = os.path.join(os.getcwd(), 'data', 'stats_layout.json')
    if not os.path.exists(path):
        print(f"Warning: {path} not found. Using empty config.")
        return {}

    try:
        with open(path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading stats config: {e}")
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

def get_logistics_rows(ship):
    """
    Generate the list of stat rows for the Logistics section.
    Combines static rows (mass, etc.) with dynamic resource rows.
    """
    # 1. Start with static config (Mass, etc)
    # Filter out any hardcoded legacy resource rows if they exist in JSON
    # (We assume "Fuel Capacity" etc are legacy)
    legacy_keys = ['max_fuel', 'max_energy', 'max_ammo', 'fuel_endurance', 'ammo_endurance', 'energy_endurance']
    base_rows = [r for r in STATS_LOGISTICS if r.key not in legacy_keys]
    
    # 2. Add Dynamic Resource Rows
    # We want a specific order: Fuel, Energy, Ammo, [Others]
    resource_order = ['fuel', 'energy', 'ammo']
    
    # Identify all resources present on ship (Max > 0 for storage, or just exists?)
    # Generally we care about Storage (Capacity) and Endurance
    
    if hasattr(ship, 'resources'):
        # Get all resource names from registry
        # We need access to the private dict or iterate keys. 
        # ResourceRegistry doesn't expose keys directly in this version?
        # Let's peek resources.py... it has _resources dict.
        # Ideally we add a public method `get_resource_names()` to ResourceRegistry.
        # But for now, we can iterate _resources.
        res_names = list(ship.resources._resources.keys())
        
        # Sort based on preferred order
        def sort_key(name):
            if name in resource_order:
                return resource_order.index(name)
            return 999 # Others at end
            
        res_names.sort(key=sort_key)
        
        dynamic_rows = []
        for r_name in res_names:
            r = ship.resources.get_resource(r_name)
            if not r or r.max_value <= 0: continue
            
            # Capitalize name
            label_base = r_name.title()
            
            # 1. Capacity Row
            # ID collision avoidance: key = "max_" + r_name
            cap_row = StatDefinition(
                id=f"max_{r_name}",
                label=f"{label_base} Capacity",
                getter=lambda s, n=r_name: get_resource_storage(s, n),
                formatter="{:.0f}",
                unit=""
            )
            dynamic_rows.append(cap_row)
            
            # 2. Endurance/Recharge Row (if applicable)
            # Logic: If it has consumption -> Endurance. If it has Gen but no consumption -> Recharge?
            consumption = get_resource_consumption(ship, r_name)
            generation = get_resource_generation(ship, r_name)
            
            if consumption > 0:
                end_row = StatDefinition(
                    id=f"{r_name}_endurance",
                    label=f"{label_base} Endurance",
                    getter=lambda s, n=r_name: get_resource_endurance(s, n),
                    formatter=fmt_time,
                    unit=""
                )
                dynamic_rows.append(end_row)
            elif generation > 0 and consumption <= 0:
                 # Recharge time?
                 rech_row = StatDefinition(
                    id=f"{r_name}_recharge",
                    label=f"{label_base} Recharge",
                    getter=lambda s, n=r_name: get_resource_replenish(s, n),
                    formatter=fmt_time,
                    unit=""
                 )
                 dynamic_rows.append(rech_row)
        
        # Merge: Base (Mass) -> Dynamic -> Base (Others?)
        # Usually Mass is first.
        return base_rows + dynamic_rows
        
    return base_rows


