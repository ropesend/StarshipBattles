import json
import math
from enum import Enum, auto
from formula_system import evaluate_math_formula

class ComponentStatus(Enum):
    ACTIVE = auto()
    DAMAGED = auto() # >50% damage
    NO_CREW = auto()
    NO_POWER = auto()
    NO_FUEL = auto()
    NO_AMMO = auto()

class LayerType(Enum):
    CORE = 1
    INNER = 2
    OUTER = 3
    ARMOR = 4

    @staticmethod
    def from_string(s):
        return getattr(LayerType, s.upper())

class Modifier:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.type_str = data['type'] # 'boolean' or 'linear'
        self.description = data.get('description', '')
        self.effects = data.get('effects', {})
        self.restrictions = data.get('restrictions', {})
        self.param_name = data.get('param_name', 'value')
        self.min_val = data.get('min_val', 0)
        self.max_val = data.get('max_val', 100)
        self.default_val = data.get('default_val', self.min_val)
        self.readonly = data.get('readonly', False)

    def create_modifier(self, value=None):
        return ApplicationModifier(self, value)

MODIFIER_REGISTRY = {}

class ApplicationModifier:
    """Instance of a modifier applied to a component"""
    def __init__(self, mod_def, value=None):
        self.definition = mod_def
        self.value = value if value is not None else mod_def.default_val

class Component:
    def __init__(self, data):
        import copy
        self.data = copy.deepcopy(data) # Store raw data for reference/cloning
        self.id = data['id']
        self.name = data['name']
        self.base_mass = data['mass']
        self.mass = self.base_mass
        self.base_max_hp = data['hp']
        self.max_hp = self.base_max_hp
        self.current_hp = self.max_hp
        # allowed_layers removed in refactor
        # self.allowed_layers = [LayerType.from_string(l) for l in data['allowed_layers']]
        self.allowed_vehicle_types = data.get('allowed_vehicle_types', ["Ship"])
        self.is_active = True
        self.status = ComponentStatus.ACTIVE
        self.layer_assigned = None
        self.type_str = data['type']
        self.sprite_index = data.get('sprite_index', 0)
        self.cost = data.get('cost', 0)
        
        # Parse abilities from data
        self.abilities = data.get('abilities', {}) # This is already a copy from self.data deepcopy? No, data passed in.
        # self.data is safe. But we used `data` arg.
        self.data = copy.deepcopy(data)
        
        # Re-source from deepcopy to be sure? Use self.data
        self.abilities = self.data.get('abilities', {})
        self.base_abilities = copy.deepcopy(self.abilities)
        
        self.ship = None # Container reference
        
        self.modifiers = [] # list of ApplicationModifier
        
        # Load default modifiers from data definition
        if 'modifiers' in self.data:
            for mod_data in self.data['modifiers']:
                mod_id = mod_data['id']
                val = mod_data.get('value', None)
                # We need to access registry. BUT registry might not be fully loaded if simple import.
                # Assuming MODIFIER_REGISTRY is populated by load_modifiers globally.
                from components import MODIFIER_REGISTRY
                if mod_id in MODIFIER_REGISTRY:
                    mod_def = MODIFIER_REGISTRY[mod_id]
                    self.modifiers.append(mod_def.create_modifier(val))
                else:
                    # If modifiers loaded later, this might fail. 
                    # Ideally modifiers are loaded before components.
                    pass
                    
        # Parse Formulas
        self.formulas = {}
        for key, value in self.data.items():
            if isinstance(value, str) and value.startswith("="):
                # It's a formula!
                self.formulas[key] = value[1:] # Store without '='
                # Initialize base value to something safe? Or keep it as is?
                # Probably keep undefined or 0 until recalculated? 
                # Better to set a default if possible, but hard to guess.
                # If it's mass/hp, 0 is safer than crashing.
                if key in ['mass', 'hp', 'damage', 'range', 'cost']:
                     setattr(self, f"base_{key}" if key in ['mass', 'hp'] else key, 0)
                     if key == 'mass': self.mass = 0
                     if key == 'hp': 
                         self.max_hp = 0
                         self.current_hp = 0




    def take_damage(self, amount):
        self.current_hp -= amount
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_active = False
            return True # Destroyed
        return False

    def reset_hp(self):
        self.current_hp = self.max_hp
        self.is_active = True
        self.status = ComponentStatus.ACTIVE

    def add_modifier(self, mod_id, value=None):
        if mod_id not in MODIFIER_REGISTRY: return False
        
        # Check restrictions
        mod_def = MODIFIER_REGISTRY[mod_id]
        if 'deny_types' in mod_def.restrictions:
            if self.type_str in mod_def.restrictions['deny_types']:
                return False
        if 'allow_types' in mod_def.restrictions:
            if self.type_str not in mod_def.restrictions['allow_types']:
                return False
                
        # Remove existing if any (replace)
        self.remove_modifier(mod_id)
            
        app_mod = ApplicationModifier(mod_def, value)
        self.modifiers.append(app_mod)
        self.recalculate_stats()
        return True

    def remove_modifier(self, mod_id):
        self.modifiers = [m for m in self.modifiers if m.definition.id != mod_id]
        self.recalculate_stats()

    def get_modifier(self, mod_id):
        for m in self.modifiers:
            if m.definition.id == mod_id:
                return m
        return None
        


    def recalculate_stats(self):
        """Recalculate component stats with multiplicative modifier stacking."""
        # Capture old hp for current_hp logic at end
        old_max_hp = self.max_hp

        # 1. Reset and Evaluate Base Formulas
        self._reset_and_evaluate_base_formulas()

        # 2. Calculate Modifier Stats (Accumulate multipliers)
        stats = self._calculate_modifier_stats()

        # 3. Apply Base Stats (Generic attributes)
        self._apply_base_stats(stats, old_max_hp)
        
        # 4. Apply Custom/Subclass Stats
        self._apply_custom_stats(stats)

    def _reset_and_evaluate_base_formulas(self):
        import copy
        # Reset abilities from raw data
        self.abilities = copy.deepcopy(self.data.get('abilities', {}))
        
        # Context building
        context = {
            'ship_class_mass': 1000 # Default fallback
        }
        if self.ship:
             context['ship_class_mass'] = getattr(self.ship, 'max_mass_budget', 1000)

        # Evaluate Formulas for attributes
        for attr, formula in self.formulas.items():
            val = evaluate_math_formula(formula, context)
            if attr == 'mass':
                self.base_mass = float(val)
                self.mass = self.base_mass # Reset to base
            elif attr == 'hp':
                self.base_max_hp = int(val)
                self.max_hp = self.base_max_hp # Reset to base
            else:
                 if hasattr(self, attr):
                     if isinstance(getattr(self, attr), int):
                         setattr(self, attr, int(val))
                     else:
                         setattr(self, attr, val)
        
        # Evaluate formulas in abilities
        for ability_name, val in self.abilities.items():
            if isinstance(val, str) and val.startswith("="):
                new_val = evaluate_math_formula(val[1:], context)
                self.abilities[ability_name] = new_val
            elif isinstance(val, dict):
                 if 'value' in val and isinstance(val['value'], str) and val['value'].startswith("="):
                     new_val = evaluate_math_formula(val['value'][1:], context)
                     val['value'] = new_val

    def _calculate_modifier_stats(self):
        from component_modifiers import apply_modifier_effects
        stats = {
            'mass_mult': 1.0,
            'hp_mult': 1.0,
            'damage_mult': 1.0,
            'range_mult': 1.0,
            'cost_mult': 1.0,
            'thrust_mult': 1.0,
            'turn_mult': 1.0,
            'energy_gen_mult': 1.0,
            'capacity_mult': 1.0,
            'crew_capacity_mult': 1.0,
            'life_support_capacity_mult': 1.0,
            'consumption_mult': 1.0,
            'mass_add': 0.0,
            'arc_add': 0.0,
            'arc_set': None,
            'properties': {},
            # New Modifier Support
            'reload_mult': 1.0,
            'endurance_mult': 1.0,
            'projectile_hp_mult': 1.0,
            'projectile_damage_mult': 1.0,
            'projectile_stealth_level': 0.0,
            'crew_req_mult': 1.0
        }
        
        for m in self.modifiers:
            apply_modifier_effects(m.definition, m.value, stats, component=self)
            
        return stats

    def _apply_base_stats(self, stats, old_max_hp):
        # Apply specific property overrides
        for prop, val in stats['properties'].items():
            if hasattr(self, prop):
                setattr(self, prop, val)

        # Apply Arc effects
        if hasattr(self, 'firing_arc'):
            if stats['arc_set'] is not None:
                self.firing_arc = stats['arc_set']
            else:
                base = self.data.get('firing_arc', 3)
                self.firing_arc = base + stats['arc_add']

        # Apply Base Multipliers
        self.mass = (self.base_mass + stats['mass_add']) * stats['mass_mult']
        
        # Note: old_max_hp is passed in, captured before base formula reset
        self.max_hp = int(self.base_max_hp * stats['hp_mult'])
        
        # Multipliers for generic attributes
        self.damage_multiplier = stats['damage_mult'] # Persist for get_damage
        
        if hasattr(self, 'damage'):
            # logic for handling formula-based damage is in Weapon subclass or get_damage usually,
            # but if 'damage' is a simple int attribute, we scale it.
            # However, Weapon class stores 'damage' as base int.
            # To handle non-Weapon components with damage:
            raw_damage = self.data.get('damage', 0)
            if not (isinstance(raw_damage, str) and raw_damage.startswith("=")):
                 self.damage = int(raw_damage * stats['damage_mult'])

        if hasattr(self, 'range'):
            self.range = int(self.data.get('range', 0) * stats['range_mult'])
        if hasattr(self, 'cost'):
            self.cost = int(self.data.get('cost', 0) * stats['cost_mult'])
        if hasattr(self, 'thrust_force'):
            self.thrust_force = self.data.get('thrust_force', 0) * stats['thrust_mult']
        if hasattr(self, 'turn_speed'):
            self.turn_speed = self.data.get('turn_speed', 0) * stats['turn_mult']
        if hasattr(self, 'energy_generation_rate'):
            self.energy_generation_rate = self.data.get('energy_generation', 0) * stats['energy_gen_mult']
        if hasattr(self, 'capacity'):
            self.capacity = int(self.data.get('capacity', 0) * stats['capacity_mult'])
            
        # Fix for missing resource costs in recalc
        if hasattr(self, 'energy_cost'):
             # Reload from data first to get base
             base_energy = self.data.get('energy_cost', 0)
             self.energy_cost = base_energy * stats.get('consumption_mult', 1.0)
        
        if hasattr(self, 'ammo_cost'):
            base_ammo = self.data.get('ammo_cost', 0)
            self.ammo_cost = base_ammo * stats.get('consumption_mult', 1.0)
            
        if hasattr(self, 'reload_time'):
             self.reload_time = self.data.get('reload', 1.0) * stats.get('reload_mult', 1.0)

        # Apply Consumption Multipliers to specific components
        if isinstance(self, Engine) and hasattr(self, 'fuel_cost_per_sec'):
            base_fuel = self.data.get('fuel_cost', 0)
            self.fuel_cost_per_sec = base_fuel * stats.get('consumption_mult', 1.0)

        # Crew Requirement Scaling
        # Rule: crew requirements should grow with the sqrt of mass of the component
        # We derive this from the total mass multiplier
        mass_scaling_factor = stats.get('mass_mult', 1.0)
        # Avoid complex numbers if somehow negative
        if mass_scaling_factor < 0: mass_scaling_factor = 0
        
        crew_mult = math.sqrt(mass_scaling_factor)
        
        # Apply to CrewRequired ability
        if 'CrewRequired' in self.abilities:
            val = self.abilities['CrewRequired']
            if isinstance(val, (int, float)):
                # If it's a raw number, scale it
                # Note: We should probably use the base value if we could, but abilities dict is reset in _reset_and_evaluate_base_formulas
                # So 'val' here is the base value from data/formula
                self.abilities['CrewRequired'] = int(math.ceil(val * crew_mult * stats.get('crew_req_mult', 1.0)))

        # Handle HP update (healing/new component logic)
        if old_max_hp == 0:
            self.current_hp = self.max_hp
        elif self.current_hp >= old_max_hp:
            self.current_hp = self.max_hp
            
        # Ensure cap
        self.current_hp = min(self.current_hp, self.max_hp)

    def _apply_custom_stats(self, stats):
        """Hook for subclasses to apply specific stats."""
        # Base implementation handles Crew/LifeSupport as they are somewhat generic in this system
        if 'CrewCapacity' in self.abilities:
            val = self.abilities['CrewCapacity']
            if isinstance(val, (int, float)):
                self.abilities['CrewCapacity'] = int(val * stats['crew_capacity_mult'])
        
        if hasattr(self, 'crew_capacity'):
             base = self.data.get('crew_capacity', 10)
             self.crew_capacity = int(base * stats['crew_capacity_mult'])

        if 'LifeSupportCapacity' in self.abilities:
            val = self.abilities['LifeSupportCapacity']
            if isinstance(val, (int, float)):
                self.abilities['LifeSupportCapacity'] = int(val * stats['life_support_capacity_mult'])
        
        if hasattr(self, 'life_support_capacity'):
             base = self.data.get('life_support_capacity', 10)
             self.life_support_capacity = int(base * stats['life_support_capacity_mult'])

    def clone(self):
        # Create a new instance with the same data
        # We need a Factory, but since we are refactoring, we can just make a new instance of the same class.
        # But we need to know the class.
        return self.__class__(self.data)

class Bridge(Component):
    def __init__(self, data):
        super().__init__(data)

class Weapon(Component):
    def __init__(self, data):
        super().__init__(data)
        # Store raw damage value/formula
        raw_damage = data.get('damage', 0)
        if isinstance(raw_damage, str) and raw_damage.startswith("="):
            self.damage_formula = raw_damage[1:]  # Store formula without '='
            # Evaluate at range 0 for base display value
            self.damage = int(max(0, evaluate_math_formula(self.damage_formula, {'range_to_target': 0})))
        else:
            self.damage_formula = None
            self.damage = int(raw_damage) if raw_damage else 0
        
        self.range = data.get('range', 0)
        self.reload_time = data.get('reload', 1.0)
        self.ammo_cost = data.get('ammo_cost', 0)
        self.cooldown_timer = 0.0
        self.firing_arc = data.get('firing_arc', 20) # Degrees
        self.facing_angle = data.get('facing_angle', 0) # Degrees relative to component forward (0)
        self.fire_count = 0  # Track how many times weapon has fired
        self.shots_fired = 0
        self.shots_hit = 0

    def get_damage(self, range_to_target: float) -> int:
        """Evaluate damage at a specific range. Returns base damage if no formula."""
        if self.damage_formula:
            context = {'range_to_target': range_to_target}
            base_val = max(0, evaluate_math_formula(self.damage_formula, context))
            mult = getattr(self, 'damage_multiplier', 1.0)
            return int(base_val * mult)
        return int(self.damage)

    def update(self):
        # Cycle-Based: 1 tick = 0.01 seconds. Decrement timer by dt.
        dt = 0.01
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt

    def can_fire(self):
        return self.is_active and self.cooldown_timer <= 0

    def fire(self):
        if self.can_fire():
            self.cooldown_timer = self.reload_time
            self.fire_count += 1
            return True
        return False
    
    def clone(self):
        # Default clone for base weapon, though usually we clone concrete types
        return Weapon(self.data)

class ProjectileWeapon(Weapon):
    def __init__(self, data):
        super().__init__(data)
        self.projectile_speed = data.get('projectile_speed', 1200) # Default speed
        
    def clone(self):
        return ProjectileWeapon(self.data)

class Engine(Component):
    def __init__(self, data):
        super().__init__(data)
        self.thrust_force = data.get('thrust_force', 0)
        self.fuel_cost_per_sec = data.get('fuel_cost', 0)
    
    def clone(self):
        return Engine(self.data)

class Thruster(Component):
    def __init__(self, data):
        super().__init__(data)
        self.turn_speed = data.get('turn_speed', 0)

    def clone(self):
        return Thruster(self.data)

class Tank(Component):
    def __init__(self, data):
        super().__init__(data)
        self.capacity = data.get('capacity', 0)
        self.resource_type = data.get('resource_type', 'fuel')

    def clone(self):
        return Tank(self.data)

class Armor(Component):
    def __init__(self, data):
        super().__init__(data)
    
    def clone(self):
        return Armor(self.data)

# Registry
class Generator(Component):
    def __init__(self, data):
        super().__init__(data)
        self.energy_generation_rate = data.get('energy_generation', 0)

    def clone(self):
        return Generator(self.data)

class BeamWeapon(Weapon):
    def __init__(self, data):
        super().__init__(data)
        self.energy_cost = data.get('energy_cost', 0)
        self.base_accuracy = data.get('base_accuracy', 1.0)
        self.accuracy_falloff = data.get('accuracy_falloff', 0.001)

    def _apply_custom_stats(self, stats):
        super()._apply_custom_stats(stats)
        
        # Apply accuracy falloff multiplier
        base = self.data.get('accuracy_falloff', 0.001)
        # Check if accuracy_falloff_mult was set by properties in super (it would be in stats['properties'])
        # Actually in old code it was checking `getattr(self, 'accuracy_falloff_mult')`.
        # Base `_apply_base_stats` applies properties to self. So this works.
        self.accuracy_falloff = base * getattr(self, 'accuracy_falloff_mult', 1.0)


    def clone(self):
        return BeamWeapon(self.data)
    
    def calculate_hit_chance(self, distance):
        """Calculate hit chance based on distance with multiplicative falloff."""
        factor = 1.0 - (distance * self.accuracy_falloff)
        factor = max(0.0, factor)
        chance = self.base_accuracy * factor
        return max(0.0, min(1.0, chance))

class SeekerWeapon(Weapon):
    def __init__(self, data):
        super().__init__(data)
        self.projectile_speed = data.get('projectile_speed', 1000)
        self.turn_rate = data.get('turn_rate', 30)
        self.endurance = data.get('endurance', 5.0)
        self.hp = data.get('hp', 1)
        self.range = int(self.projectile_speed * self.endurance * 0.8)

    def _apply_custom_stats(self, stats):
        super()._apply_custom_stats(stats)
        
        # Apply 80% rule to the calculated range (Straight Line * 0.8 * Multipliers)
        # Apply endurance_mult
        self.endurance = self.data.get('endurance', 5.0) * stats.get('endurance_mult', 1.0)
        
        self.range = int((self.projectile_speed * self.endurance) * 0.8 * stats['range_mult'])
        
        # Apply projectile HP modifier
        base_proj_hp = self.data.get('hp', 1)
        self.hp = int(base_proj_hp * stats.get('projectile_hp_mult', 1.0))
        
        # Apply projectile damage modifier
        # For seekers, damage is a payload value applied on impact, stored in self.damage
        base_damage = self.data.get('damage', 10)
        self.damage = int(base_damage * stats.get('projectile_damage_mult', 1.0))
        
        # We also clear damage_multiplier as we applied it directly to the base value
        # This prevents double application if get_damage() is used
        self.damage_multiplier = 1.0
        
        # Apply stealth
        self.projectile_stealth_level = stats.get('projectile_stealth_level', 0.0)
        
        # Calculate To-Hit Defense (Baseline + Stealth)
        # Assuming baseline is 0 unless in data
        base_def = self.data.get('to_hit_defense', 0.0)
        # Assuming each stealth level adds 0.1 (10%) to defense? 
        # Or level IS the value? Description says "Stealth Level".
        # Let's assume linear addition.
        self.to_hit_defense = base_def + (self.projectile_stealth_level * 0.1)
        
    def clone(self):
        return SeekerWeapon(self.data)

class CrewQuarters(Component):
    """Provides crew capacity for the ship."""
    def __init__(self, data):
        super().__init__(data)
        self.crew_capacity = data.get('crew_capacity', 10)
    
    def clone(self):
        return CrewQuarters(self.data)

class LifeSupport(Component):
    """Provides life support capacity for crew."""
    def __init__(self, data):
        super().__init__(data)
        self.life_support_capacity = data.get('life_support_capacity', 10)
    
    def clone(self):
        return LifeSupport(self.data)

class Sensor(Component):
    """Provides sensor capabilities like attack modifiers."""
    def __init__(self, data):
        super().__init__(data)
        val = self.abilities.get('ToHitAttackModifier', 1.0)
        self.attack_modifier = val.get('value', 1.0) if isinstance(val, dict) else val
    
    def clone(self):
        return Sensor(self.data)

class Electronics(Component):
    """Provides electronic warfare capabilities like defense modifiers."""
    def __init__(self, data):
        super().__init__(data)
        val = self.abilities.get('ToHitDefenseModifier', 1.0)
        self.defense_modifier = val.get('value', 1.0) if isinstance(val, dict) else val
    
    def clone(self):
        return Electronics(self.data)

class Shield(Component):
    def __init__(self, data):
        super().__init__(data)
        # We might parse 'ShieldProjection' from abilities as a direct property
        self.shield_capacity = self.abilities.get('ShieldProjection', 0)
        self.base_shield_capacity = self.shield_capacity
    
    def _apply_custom_stats(self, stats):
        super()._apply_custom_stats(stats)
        self.shield_capacity = int(self.base_shield_capacity * stats.get('capacity_mult', 1.0))

    def clone(self):
        return Shield(self.data)

class ShieldRegenerator(Component):
    def __init__(self, data):
        super().__init__(data)
        self.regen_rate = self.abilities.get('ShieldRegeneration', 0)
        self.base_regen_rate = self.regen_rate
        self.energy_cost = self.abilities.get('EnergyConsumption', 0)
    
    def _apply_custom_stats(self, stats):
        super()._apply_custom_stats(stats)
        # Use energy_gen_mult for regeneration rate scaling as simple_size affects it
        self.regen_rate = self.base_regen_rate * stats.get('energy_gen_mult', 1.0)
        
        # Restore energy_cost from abilities (Source of Truth) as _apply_base_stats overwrites it
        # Apply cost_mult for scaling consistency
        raw_cost = self.abilities.get('EnergyConsumption', 0)
        self.energy_cost = raw_cost * stats.get('cost_mult', 1.0)

    def clone(self):
        return ShieldRegenerator(self.data)

class Hangar(Component):
    """Stores and launches fighter vessels."""
    def __init__(self, data):
        super().__init__(data)
        self.storage_capacity = self.abilities.get('VehicleStorage', 0)
        self.launch_config = self.abilities.get('VehicleLaunch', {})
        self.max_launch_mass = self.launch_config.get('max_launch_mass', 0)
        self.cycle_time = self.launch_config.get('cycle_time', 5.0)
        
        self.cooldown_timer = 0.0
        # For simple implementation, storage equals capacity.
        # In future, we might track individual stored ships.
        # Ideally we'd have a list of stored ship definitions? 
        # For now, we assume infinite stock or capacity-based stock? 
        # Requirement says "launch fighters stored in the vessel".
        # Let's assume we can launch as long as we have "mass capacity" available?
        # OR simple "ammo" approach? The prompt implies "launch fighters stored".
        # A simpler first pass: Infinite fighters, just gated by cooldown? 
        # Or, treat capacity as "Hangar Space". 
        # But where do the fighters come from? 
        # Let's assume the component launches a specific "fighter type" configured in data?
        # The prompt is "launch fighters stored in the vessel".
        # Standard implementation: The SHIP stores the fighters (as cargo?).
        # Hangar just facilitates launch.
        # But in `ship.py`, we don't have a generic "vehicle cargo".
        # Let's make the Hangar essentially a "Fighter Spawner" for now,
        # perhaps using 'capacity' as 'max active fighters'?
        from ship import VEHICLE_CLASSES
        self.fighter_class = "Fighter (Small)" # Default
        
    def update(self):
        dt = 0.01
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt

    def can_launch(self):
        return self.is_active and self.cooldown_timer <= 0

    def launch(self):
        if self.can_launch():
            self.cooldown_timer = self.cycle_time
            return True
        return False

    def clone(self):
        return Hangar(self.data)

COMPONENT_REGISTRY = {}
COMPONENT_TYPE_MAP = {
    "Bridge": Bridge,
    "Weapon": ProjectileWeapon,
    "ProjectileWeapon": ProjectileWeapon,
    "Engine": Engine,
    "Thruster": Thruster,
    "Tank": Tank,
    "Armor": Armor,
    "Generator": Generator,
    "BeamWeapon": BeamWeapon,
    "CrewQuarters": CrewQuarters,
    "LifeSupport": LifeSupport,
    "Sensor": Sensor,
    "Electronics": Electronics,
    "Shield": Shield,
    "ShieldRegenerator": ShieldRegenerator,
    "SeekerWeapon": SeekerWeapon,
    "Hangar": Hangar
}

def load_components(filepath="data/components.json"):
    global COMPONENT_REGISTRY
    import os

    # Try absolute path based on this file if CWD fails
    if not os.path.exists(filepath):
        print(f"WARN: {filepath} not found in CWD ({os.getcwd()}).")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        abs_path = os.path.join(base_dir, filepath)

        if os.path.exists(abs_path):
            filepath = abs_path
        else:
            print(f"ERROR: components file not found at {abs_path}")
            return

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        
        for comp_def in data['components']:
            c_type = comp_def['type']
            try:
                cls = COMPONENT_TYPE_MAP.get(c_type, Component)
                obj = cls(comp_def)
                COMPONENT_REGISTRY[comp_def['id']] = obj
            except Exception as e:
                print(f"ERROR creating component {comp_def.get('id')}: {e}")
                
    except Exception as e:
        print(f"ERROR loading/parsing components json: {e}")

def load_modifiers(filepath="data/modifiers.json"):
    global MODIFIER_REGISTRY
    import os
    if not os.path.exists(filepath):
         base_dir = os.path.dirname(os.path.abspath(__file__))
         filepath = os.path.join(base_dir, filepath)
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        for mod_def in data['modifiers']:
            mod = Modifier(mod_def)
            MODIFIER_REGISTRY[mod.id] = mod
            

    except Exception as e:
        print(f"ERROR loading modifiers: {e}")

def create_component(component_id):
    if component_id in COMPONENT_REGISTRY:
        return COMPONENT_REGISTRY[component_id].clone()
    print(f"Error: Component ID {component_id} not found in registry.")
    return None

def get_all_components():
    return list(COMPONENT_REGISTRY.values())
