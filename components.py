import json
from enum import Enum

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
        self.default_val = data.get('default_val', 0)

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
        self.data = data # Store raw data for reference/cloning
        self.id = data['id']
        self.name = data['name']
        self.base_mass = data['mass']
        self.mass = self.base_mass
        self.base_max_hp = data['hp']
        self.max_hp = self.base_max_hp
        self.current_hp = self.max_hp
        self.allowed_layers = [LayerType.from_string(l) for l in data['allowed_layers']]
        self.is_active = True
        self.layer_assigned = None
        self.type_str = data['type']
        self.sprite_index = data.get('sprite_index', 0)
        self.cost = data.get('cost', 0)
        
        # Parse abilities from data
        self.abilities = data.get('abilities', {})
        
        self.modifiers = [] # list of ApplicationModifier
        # If cloning, data might have modifiers? Not yet supported in save/load but structure ready

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
        """Recalculate component stats with multiplicative modifier stacking.
        
        Modifiers stack multiplicatively:
        - size_mount 2x * range_mount 1.5x = 3x total multiplier
        """
        # Start with base values
        self.mass = self.base_mass
        self.max_hp = self.base_max_hp
        
        # Initialize stat multipliers (start at 1.0)
        mass_mult = 1.0
        hp_mult = 1.0
        damage_mult = 1.0
        range_mult = 1.0
        cost_mult = 1.0
        thrust_mult = 1.0
        turn_mult = 1.0
        energy_gen_mult = 1.0
        capacity_mult = 1.0
        
        # Process all modifiers to collect multipliers
        for m in self.modifiers:
            eff = m.definition.effects
            val = m.value
            
            # Simple additive effects (add percentage to multiplier)
            if 'mass_mult' in eff:
                mass_mult *= (1.0 + eff['mass_mult'])  # 0.25 means +25% = 1.25x
            if 'hp_mult' in eff:
                hp_mult *= (1.0 + eff['hp_mult'])  # 1.0 means +100% = 2x
                
            # Mass added per unit (e.g. turret mount)
            if 'mass_add_per_unit' in eff:
                self.mass += val * eff['mass_add_per_unit']
                
            # Arc effects
            if 'arc_add' in eff:
                if hasattr(self, 'firing_arc'):
                    base = self.data.get('firing_arc', 3)
                    self.firing_arc = base + val
                    
            if 'arc_set' in eff:
                if hasattr(self, 'firing_arc'):
                    self.firing_arc = val
                    
            # SPECIAL EFFECTS - collect multipliers
            if 'special' in eff:
                if eff['special'] == 'simple_size':
                    # Multiplies almost everything by Value (1x-128x)
                    scale = val
                    mass_mult *= scale
                    hp_mult *= scale
                    damage_mult *= scale
                    cost_mult *= scale
                    thrust_mult *= scale
                    turn_mult *= scale
                    energy_gen_mult *= scale
                    capacity_mult *= scale
                    
                elif eff['special'] == 'range_mount':
                    # Each level doubles range, mass/hp/cost increase by 3.5x per level
                    level = val
                    range_mult *= 2.0 ** level   # 1, 2, 4, 8, 16, 32
                    cost_mult_increase = 3.5 ** level   # 1, 3.5, 12.25, etc.
                    mass_mult *= cost_mult_increase
                    hp_mult *= cost_mult_increase
                    
                elif eff['special'] == 'turret_mount':
                    # Logarithmic scaling - first degrees cost most, diminishing returns
                    # At 0°: 1.0x, at 90°: ~1.71x, at 180°: 2.0x
                    # Formula: mult = 1.0 + 0.514 * ln(1 + arc/30)
                    import math
                    arc = val
                    if arc > 0:
                        turret_mult = 1.0 + 0.514 * math.log(1.0 + arc / 30.0)
                        mass_mult *= turret_mult
                    
                elif eff['special'] == 'facing':
                    if hasattr(self, 'facing_angle'):
                        self.facing_angle = val

        # Apply all accumulated multipliers to base values
        self.mass *= mass_mult
        self.max_hp = int(self.base_max_hp * hp_mult)
        
        if hasattr(self, 'damage'):
            self.damage = int(self.data.get('damage', 0) * damage_mult)
        if hasattr(self, 'range'):
            self.range = int(self.data.get('range', 0) * range_mult)
        if hasattr(self, 'cost'):
            self.cost = int(self.data.get('cost', 0) * cost_mult)
        if hasattr(self, 'thrust_force'):
            self.thrust_force = self.data.get('thrust_force', 0) * thrust_mult
        if hasattr(self, 'turn_speed'):
            self.turn_speed = self.data.get('turn_speed', 0) * turn_mult
        if hasattr(self, 'energy_generation_rate'):
            self.energy_generation_rate = self.data.get('energy_generation', 0) * energy_gen_mult
        if hasattr(self, 'capacity'):
            self.capacity = int(self.data.get('capacity', 0) * capacity_mult)
            
        self.current_hp = min(self.current_hp, self.max_hp)

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
        self.damage = data.get('damage', 0)
        self.range = data.get('range', 0)
        self.reload_time = data.get('reload', 1.0)
        self.ammo_cost = data.get('ammo_cost', 0)
        self.cooldown_timer = 0.0
        self.firing_arc = data.get('firing_arc', 20) # Degrees
        self.facing_angle = data.get('facing_angle', 0) # Degrees relative to component forward (0)

    def update(self, dt):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt

    def can_fire(self):
        return self.is_active and self.cooldown_timer <= 0

    def fire(self):
        if self.can_fire():
            self.cooldown_timer = self.reload_time
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

    def clone(self):
        return BeamWeapon(self.data)
    
    def calculate_hit_chance(self, distance):
        """Calculate hit chance based on distance with linear falloff."""
        chance = self.base_accuracy - (distance * self.accuracy_falloff)
        return max(0.0, min(1.0, chance))

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
        self.attack_modifier = self.abilities.get('ToHitAttackModifier', 1.0)
    
    def clone(self):
        return Sensor(self.data)

class Electronics(Component):
    """Provides electronic warfare capabilities like defense modifiers."""
    def __init__(self, data):
        super().__init__(data)
        self.defense_modifier = self.abilities.get('ToHitDefenseModifier', 1.0)
    
    def clone(self):
        return Electronics(self.data)


COMPONENT_REGISTRY = {}

def load_components(filepath="data/components.json"):
    global COMPONENT_REGISTRY
    import os
    print(f"DEBUG: load_components called with filepath='{filepath}'")
    
    # Try absolute path based on this file if CWD fails
    if not os.path.exists(filepath):
        print(f"WARN: {filepath} not found in CWD ({os.getcwd()}).")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        abs_path = os.path.join(base_dir, filepath)
        print(f"DEBUG: Trying absolute path: {abs_path}")
        if os.path.exists(abs_path):
            filepath = abs_path
        else:
            print(f"ERROR: components file not found at {abs_path}")
            return

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        print(f"DEBUG: Loaded JSON data. Found {len(data.get('components', []))} definitions.")
        
        for comp_def in data['components']:
            c_type = comp_def['type']
            obj = None
            try:
                if c_type == "Bridge":
                    obj = Bridge(comp_def)
                elif c_type == "Weapon" or c_type == "ProjectileWeapon":
                    obj = ProjectileWeapon(comp_def)
                elif c_type == "Engine":
                    obj = Engine(comp_def)
                elif c_type == "Thruster":
                    obj = Thruster(comp_def)
                elif c_type == "Tank":
                    obj = Tank(comp_def)
                elif c_type == "Armor":
                    obj = Armor(comp_def)
                elif c_type == "Generator":
                    obj = Generator(comp_def)
                elif c_type == "BeamWeapon":
                    obj = BeamWeapon(comp_def)
                elif c_type == "CrewQuarters":
                    obj = CrewQuarters(comp_def)
                elif c_type == "LifeSupport":
                    obj = LifeSupport(comp_def)
                elif c_type == "Sensor":
                    obj = Sensor(comp_def)
                elif c_type == "Electronics":
                    obj = Electronics(comp_def)
                else:
                    obj = Component(comp_def)
                
                COMPONENT_REGISTRY[comp_def['id']] = obj
            except Exception as e:
                print(f"ERROR creating component {comp_def.get('id')}: {e}")
                
        print(f"DEBUG: COMPONENT_REGISTRY now has {len(COMPONENT_REGISTRY)} items.")
        
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
            
        print(f"DEBUG: Loaded {len(MODIFIER_REGISTRY)} modifiers.")
    except Exception as e:
        print(f"ERROR loading modifiers: {e}")

def create_component(component_id):
    if component_id in COMPONENT_REGISTRY:
        return COMPONENT_REGISTRY[component_id].clone()
    print(f"Error: Component ID {component_id} not found in registry.")
    return None

def get_all_components():
    return list(COMPONENT_REGISTRY.values())

# For backwards compatibility during refactor, we might need aliases references.
# But better to fix the calls.
