import json
from enum import Enum, auto

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
        self.default_val = data.get('default_val', self.min_val)

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
        self.allowed_vehicle_types = data.get('allowed_vehicle_types', ["Ship"])
        self.is_active = True
        self.status = ComponentStatus.ACTIVE
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
        """Recalculate component stats with multiplicative modifier stacking.
        
        Modifiers stack multiplicatively.
        Logic is now delegated to component_modifiers.py registry.
        """
        from component_modifiers import apply_modifier_effects

        # Start with base values
        self.mass = self.base_mass
        self.max_hp = self.base_max_hp
        
        old_max_hp = self.max_hp
        
        # Initialize stat multipliers and accumulators
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
            'mass_add': 0.0,
            'arc_add': 0.0,
            'arc_set': None,
            'properties': {}
        }
        
        # Process all modifiers
        for m in self.modifiers:
            apply_modifier_effects(m.definition, m.value, stats)

        # Apply specific property overrides (like facing)
        for prop, val in stats['properties'].items():
            if hasattr(self, prop):
                setattr(self, prop, val)

        # Apply Arc effects
        if hasattr(self, 'firing_arc'):
            # If 'arc_set' was used, it overrides everything else
            if stats['arc_set'] is not None:
                self.firing_arc = stats['arc_set']
            else:
                # Otherwise apply additive modifiers to base
                # Using 3 as base assumption if missing, to match original logic
                base = self.data.get('firing_arc', 3)
                self.firing_arc = base + stats['arc_add']

        # Apply all accumulated multipliers to base values
        # Mass has an additive component too
        self.mass = (self.mass + stats['mass_add']) * stats['mass_mult']
        
        self.max_hp = int(self.base_max_hp * stats['hp_mult'])
        
        if hasattr(self, 'damage'):
            self.damage = int(self.data.get('damage', 0) * stats['damage_mult'])
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
            
        # If component was at full HP before calculation, or is new (current>=old_max), update to new max
        if self.current_hp >= old_max_hp:
            self.current_hp = self.max_hp
        else:
            # Otherwise keep damage but cap at new max
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
        self.fire_count = 0  # Track how many times weapon has fired
        self.shots_fired = 0
        self.shots_hit = 0

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

    def recalculate_stats(self):
        # Reset specific modifiers before parent calc (which might set them if modifier exists)
        self.accuracy_falloff_mult = 1.0
        
        super().recalculate_stats()
        
        # Apply accuracy falloff multiplier
        # If modifier exists, self.accuracy_falloff_mult was updated by stats['properties'] logic in super
        base = self.data.get('accuracy_falloff', 0.001)
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

    def recalculate_stats(self):
        super().recalculate_stats()
        from component_modifiers import apply_modifier_effects

        # Recalculate range mult locally since super() uses data['range'] which is invalid for Seeker
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
            'mass_add': 0.0,
            'arc_add': 0.0,
            'arc_set': None,
            'properties': {}
        }
        
        for m in self.modifiers:
            apply_modifier_effects(m.definition, m.value, stats)

        # Apply 80% rule to the calculated range (Straight Line * 0.8 * Multipliers)
        self.range = int((self.projectile_speed * self.endurance) * 0.8 * stats['range_mult'])
        
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

class Shield(Component):
    def __init__(self, data):
        super().__init__(data)
        # We might parse 'ShieldProjection' from abilities as a direct property
        self.shield_capacity = self.abilities.get('ShieldProjection', 0)
    
    def clone(self):
        return Shield(self.data)

class ShieldRegenerator(Component):
    def __init__(self, data):
        super().__init__(data)
        self.regen_rate = self.abilities.get('ShieldRegeneration', 0)
        self.energy_cost = self.abilities.get('EnergyConsumption', 0)
    
    def clone(self):
        return ShieldRegenerator(self.data)

COMPONENT_REGISTRY = {}

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
                elif c_type == "Shield":
                    obj = Shield(comp_def)
                elif c_type == "ShieldRegenerator":
                    obj = ShieldRegenerator(comp_def)
                elif c_type == "SeekerWeapon":
                    obj = SeekerWeapon(comp_def)
                else:
                    obj = Component(comp_def)
                
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
