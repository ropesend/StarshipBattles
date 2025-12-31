from ship import LayerType

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
    from ship import LayerType
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
            getter = GETTERS.get(item_data.get('getter')) if item_data.get('getter') else None
            
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
