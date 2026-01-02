
import math
from typing import Dict, Any, Optional, List, Union

# --- Base Ability ---
class Ability:
    """
    Base class for component abilities.
    Abilities represent functional capabilities (Consumption, Storage, Generation, special effects)
    that are data-driven and attached to Components.
    """
    def __init__(self, component, data: Dict[str, Any]):
        self.component = component
        self.data = data
        self._tags = set(data.get('tags', [])) if isinstance(data, dict) else set()
    
    @property
    def tags(self):
        return self._tags

    def update(self) -> bool:
        """
        Called every tick (0.01s). 
        Used for constant resource consumption or continuous effects.
        Returns True if operational, False if failed (e.g. starvation).
        """
        return True

    def on_activation(self) -> bool:
        """
        Called when component tries to activate (e.g. fire weapon). 
        Used for checking activation costs or conditions.
        Returns True if allowed.
        """
        return True
        
    def get_ui_rows(self) -> List[Dict[str, str]]:
        """
        Return list of UI rows for the capability scanner/details panel.
        Format: [{'label': 'Thrust', 'value': '1500 N', 'color_hint': '#FFFFFF'}]
        """
        return []

# --- Resource Abilities (Migrated from resources.py) ---

class ResourceConsumption(Ability):
    """
    Ability to consume resources.
    Data: { "resource": "fuel", "amount": 10, "trigger": "constant"|"activation" }
    """
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.resource_name = data.get('resource', '')
        self.amount = data.get('amount', 0.0)
        self.trigger = data.get('trigger', 'constant') # 'constant' or 'activation'

    def update(self) -> bool:
        TICK_DURATION = 0.01  # Fixed tick duration
        if self.trigger == 'constant':
            # Need access to ship's resources
            if self.component.ship and self.component.ship.resources:
                res = self.component.ship.resources.get_resource(self.resource_name)
                if res:
                    # Constant consumption is per second, multiply by tick duration
                    cost = self.amount * TICK_DURATION
                    if not res.consume(cost):
                        return False # Starvation
                else:
                    if self.amount > 0: return False
        return True
                    
    def check_and_consume(self) -> bool:
        """Explicitly call for one-shot consumption checks."""
        if self.component.ship and self.component.ship.resources:
            res = self.component.ship.resources.get_resource(self.resource_name)
            if res:
                return res.consume(self.amount)
            else:
                return self.amount <= 0
        return False
        
    def check_available(self) -> bool:
        if self.component.ship and self.component.ship.resources:
            res = self.component.ship.resources.get_resource(self.resource_name)
            if res:
               return res.check(self.amount)
            else:
               return self.amount <= 0
        return False
        
    def get_ui_rows(self):
        trigger_str = "/s" if self.trigger == 'constant' else "/use"
        
        # Color mapping based on resource type
        color = '#FFFFFF'
        if self.resource_name == 'fuel': color = '#FFA500' # Orange
        elif self.resource_name == 'energy': color = '#64C8FF' # Light Blue
        elif self.resource_name == 'ammo': color = '#C8C832' # Dirty Yellow
        
        label_text = f"{self.resource_name.title()} {'Cost' if self.trigger!='constant' else 'Use'}"
        return [{'label': label_text, 'value': f"{self.amount:.1f}{trigger_str}", 'color_hint': color}]

class ResourceStorage(Ability):
    """
    Ability to store resources.
    Data: { "resource": "fuel", "amount": 100 }
    """
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.resource_type = data.get('resource', '')
        self.max_amount = data.get('amount', 0.0)
        
    def get_ui_rows(self):
        color = '#64FFFF' # Cyan default for caps
        if self.resource_type == 'shield': color = '#00FFFF' # Standard Shield Cyan
        
        return [{'label': f"{self.resource_type.title()} Cap", 'value': f"{self.max_amount:.0f}", 'color_hint': color}]

class ResourceGeneration(Ability):
    """
    Ability to generate resources.
    Data: { "resource": "energy", "amount": 10 }
    """
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.resource_type = data.get('resource', '')
        self.rate = data.get('amount', 0.0)

    def get_ui_rows(self):
        color = '#FFFFFF' 
        if self.resource_type == 'energy': color = '#FFFF00' # Yellow
        
        return [{'label': f"{self.resource_type.title()} Gen", 'value': f"{self.rate:.1f}/s", 'color_hint': color}]

# --- Core Mechanics ---

class CombatPropulsion(Ability):
    """Provides Thrust."""
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        # Handle 'val' if primitive shortcut used, else explicit 'value'
        val = data if isinstance(data, (int, float)) else data.get('value', 0)
        self.thrust_force = float(val)

    def get_ui_rows(self):
        return [{'label': 'Thrust', 'value': f"{self.thrust_force:.0f} N", 'color_hint': '#64FF64'}] # Light Green

class ManeuveringThruster(Ability):
    """Provides Rotation."""
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        val = data if isinstance(data, (int, float)) else data.get('value', 0)
        self.turn_rate = float(val)

    def get_ui_rows(self):
        return [{'label': 'Turn Speed', 'value': f"{self.turn_rate:.1f} deg/s", 'color_hint': '#64FF96'}] # Slightly different green

class ShieldProjection(Ability):
    """Provides Shield Capacity."""
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        val = data if isinstance(data, (int, float)) else data.get('value', 0)
        self.capacity = float(val)

    def get_ui_rows(self):
        return [{'label': 'Shield Cap', 'value': f"{self.capacity:.0f}", 'color_hint': '#00FFFF'}] # Cyan

class ShieldRegeneration(Ability):
    """Regenerates Shields."""
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        val = data if isinstance(data, (int, float)) else data.get('value', 0)
        self.rate = float(val)
        
    def get_ui_rows(self):
        return [{'label': 'Regen', 'value': f"{self.rate:.1f}/s", 'color_hint': '#00C8FF'}] # Deep Sky Blue

class VehicleLaunchAbility(Ability):
    """Allows storing and launching fighters."""
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.fighter_class = data.get('fighter_class', 'Fighter (Small)')
        self.capacity = data.get('capacity', 0)
        self.cycle_time = data.get('cycle_time', 5.0)
        self.cooldown = 0.0
        
    def update(self) -> bool:
        if self.cooldown > 0:
            self.cooldown -= 0.01
        return True
        
    def try_launch(self):
        if self.cooldown <= 0:
            self.cooldown = self.cycle_time
            return True
        return False
        
    def get_ui_rows(self):
        return [
            {'label': 'Hangar', 'value': f"{self.fighter_class}", 'color_hint': '#C8C8C8'},
            {'label': 'Cycle', 'value': f"{self.cycle_time}s", 'color_hint': '#C8C8C8'}
        ]
        
# --- Weapon Abilities ---

class WeaponAbility(Ability):
    """Base for offensive capabilities."""
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.damage = float(data.get('damage', 0))
        self.range = float(data.get('range', 0))
        self.reload_time = float(data.get('reload', 1.0))
        self.firing_arc = float(data.get('firing_arc', 360))
        self.facing_angle = float(data.get('facing_angle', 0))
        self.cooldown_timer = 0.0
        
        # Tags for targeting logic (e.g. 'pdc')
        self._tags.update(data.get('tags', []))

    def update(self) -> bool:
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 0.01
        return True

    def can_fire(self):
        return self.cooldown_timer <= 0

    def fire(self, target):
        """Perform firing logic. Returns dict or Projectile, or False if failed."""
        if self.can_fire():
            self.cooldown_timer = self.reload_time
            return True
        return False

    def get_ui_rows(self):
        return [
            {'label': 'Damage', 'value': f"{self.damage:.0f}", 'color_hint': '#FF6464'}, # Red
            {'label': 'Range', 'value': f"{self.range:.0f}", 'color_hint': '#FFA500'}, # Orange
            {'label': 'Reload', 'value': f"{self.reload_time:.1f}s", 'color_hint': '#FFC864'} # Gold
        ]

class ProjectileWeaponAbility(WeaponAbility):
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.projectile_speed = float(data.get('projectile_speed', 500))

    def get_ui_rows(self):
        rows = super().get_ui_rows()
        rows.append({'label': 'Speed', 'value': f"{self.projectile_speed:.0f}", 'color_hint': '#C8C832'}) # Yellow-ish
        return rows

class BeamWeaponAbility(WeaponAbility):
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.accuracy_falloff = float(data.get('accuracy_falloff', 0.001))
        self.base_accuracy = float(data.get('base_accuracy', 1.0))

class SeekerWeaponAbility(WeaponAbility):
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.projectile_speed = float(data.get('projectile_speed', 500))
        self.endurance = float(data.get('endurance', 3.0))
        self.turn_rate = float(data.get('turn_rate', 30.0))
        self.to_hit_defense = float(data.get('to_hit_defense', 0.0))
        
        # Recalculate range based on endurance if basic range not set or derived
        # Often range is just speed * endurance
        if self.range <= 0 and self.projectile_speed > 0:
             self.range = self.projectile_speed * self.endurance

# --- Registry ---

ABILITY_REGISTRY = {
    "ResourceConsumption": ResourceConsumption,
    "ResourceStorage": ResourceStorage,
    "ResourceGeneration": ResourceGeneration,
    "CombatPropulsion": CombatPropulsion,
    "ManeuveringThruster": ManeuveringThruster,
    "ShieldProjection": ShieldProjection,
    "ShieldRegeneration": ShieldRegeneration,
    "VehicleLaunch": VehicleLaunchAbility,
    "WeaponAbility": WeaponAbility,
    "ProjectileWeaponAbility": ProjectileWeaponAbility,
    "BeamWeaponAbility": BeamWeaponAbility,
    "SeekerWeaponAbility": SeekerWeaponAbility,
    
    # Primitive/Shortcut Factories
    "FuelStorage": lambda c, d: ResourceStorage(c, {"resource": "fuel", "amount": d} if isinstance(d, (int, float)) else {**d, "resource": "fuel"}),
    "EnergyStorage": lambda c, d: ResourceStorage(c, {"resource": "energy", "amount": d} if isinstance(d, (int, float)) else {**d, "resource": "energy"}),
    "AmmoStorage": lambda c, d: ResourceStorage(c, {"resource": "ammo", "amount": d} if isinstance(d, (int, float)) else {**d, "resource": "ammo"}),
    "EnergyGeneration": lambda c, d: ResourceGeneration(c, {"resource": "energy", "amount": d} if isinstance(d, (int, float)) else {**d, "resource": "energy"}),
    "EnergyConsumption": lambda c, d: ResourceConsumption(c, {"resource": "energy", "amount": d, "trigger": "constant"} if isinstance(d, (int, float)) else {**d, "resource": "energy"})
}

def create_ability(name: str, component, data: Any) -> Optional[Ability]:
    if name in ABILITY_REGISTRY:
        try:
             # Handle primitive shortcut inputs (e.g. "CombatPropulsion": 100)
             # passed as 'data'. Constructor must handle it, or we normalize here.
             # Our constructors above handle `isinstance(data, (int, float))` checks.
            return ABILITY_REGISTRY[name](component, data)
        except Exception as e:
            # print(f"Error creating ability {name}: {e}")
            return None
    return None
