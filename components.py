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

class Component:
    def __init__(self, data):
        self.data = data # Store raw data for reference/cloning
        self.id = data['id']
        self.name = data['name']
        self.mass = data['mass']
        self.max_hp = data['hp']
        self.current_hp = self.max_hp
        self.allowed_layers = [LayerType.from_string(l) for l in data['allowed_layers']]
        self.is_active = True
        self.layer_assigned = None
        self.type_str = data['type']
        self.sprite_index = data.get('sprite_index', 0)

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
        return Weapon(self.data)

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
COMPONENT_REGISTRY = {}

def load_components(filepath="components.json"):
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
                elif c_type == "Weapon":
                    obj = Weapon(comp_def)
                elif c_type == "Engine":
                    obj = Engine(comp_def)
                elif c_type == "Thruster":
                    obj = Thruster(comp_def)
                elif c_type == "Tank":
                    obj = Tank(comp_def)
                elif c_type == "Armor":
                    obj = Armor(comp_def)
                else:
                    obj = Component(comp_def)
                
                COMPONENT_REGISTRY[comp_def['id']] = obj
            except Exception as e:
                print(f"ERROR creating component {comp_def.get('id')}: {e}")
                
        print(f"DEBUG: COMPONENT_REGISTRY now has {len(COMPONENT_REGISTRY)} items.")
        
    except Exception as e:
        print(f"ERROR loading/parsing components json: {e}")

def create_component(component_id):
    if component_id in COMPONENT_REGISTRY:
        return COMPONENT_REGISTRY[component_id].clone()
    print(f"Error: Component ID {component_id} not found in registry.")
    return None

def get_all_components():
    return list(COMPONENT_REGISTRY.values())

# For backwards compatibility during refactor, we might need aliases references.
# But better to fix the calls.
