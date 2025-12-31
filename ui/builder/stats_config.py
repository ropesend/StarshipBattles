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

# --- Config Groups ---

STATS_GENERAL = [
    StatDefinition('mass', 'Mass', getter=get_mass_display, unit=lambda s, v: f"/ {s.max_mass_budget}", validator=mass_validator),
    StatDefinition('max_hp', 'Max HP'),
    StatDefinition('emissive_armor', 'Dmg Ignore'),
    StatDefinition('max_shields', 'Shields'),
    StatDefinition('shield_regen', 'Shield Regen', key='shield_regen_rate', formatter=fmt_decimal, unit="/s"),
    StatDefinition('shield_cost', 'Regen Cost', key='shield_regen_cost', formatter=fmt_decimal, unit=" E/t"),
    StatDefinition('max_speed', 'Max Speed'),
    StatDefinition('turn_rate', 'Turn Rate', key='turn_speed', unit=" deg/s"),
    StatDefinition('acceleration', 'Acceleration', key='acceleration_rate', formatter="{:.2f}"),
    StatDefinition('thrust', 'Total Thrust', key='total_thrust'),
    StatDefinition('energy_gen', 'Energy Gen', key='energy_gen_rate', formatter=fmt_decimal, unit="/s"),
    StatDefinition('max_fuel', 'Max Fuel'),
    StatDefinition('max_ammo', 'Max Ammo'),
    StatDefinition('max_energy', 'Max Energy'),
    StatDefinition('targeting', 'Targeting', getter=get_max_targets, formatter=fmt_targeting),
    StatDefinition('target_profile', 'Defensive Odds', key='to_hit_profile', formatter=fmt_multiply, unit="x"),
    StatDefinition('scan_strength', 'Offensive Odds', key='baseline_to_hit_offense', formatter=fmt_decimal, unit="x"),
]

STATS_FIGHTER = [
    StatDefinition('fighter_capacity', 'Total Storage', unit="t"),
    StatDefinition('fighter_size_cap', 'Max Size Cap', unit="t"),
    StatDefinition('fighters_per_wave', 'Per Wave'),
    StatDefinition('launch_cycle', 'Cycle Time', formatter=fmt_decimal, unit="s"),
]

STATS_CREW = [
    StatDefinition('crew_required', 'Crew Required', getter=get_crew_required),
    StatDefinition('crew_housed', 'Crew On Board', getter=get_crew_capacity, validator=crew_validator),
    StatDefinition('life_support', 'Life Support', getter=get_life_support, validator=life_support_validator),
]

STATS_ENDURANCE = [
    StatDefinition('fuel_time', 'Fuel Time', key='fuel_endurance', formatter=fmt_time),
    StatDefinition('ammo_time', 'Ordnance Time', key='ammo_endurance', formatter=fmt_time),
    StatDefinition('energy_time', 'Energy Time', key='energy_endurance', formatter=fmt_time),
    StatDefinition('recharge_time', 'Recharge Time', key='energy_recharge', formatter=fmt_time),
]
