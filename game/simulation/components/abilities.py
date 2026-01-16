import math
from typing import Dict, Any, Optional, List, Union
from game.core.logger import log_debug
from game.core.config import PhysicsConfig

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
        self.stack_group = data.get('stack_group') if isinstance(data, dict) else None
    
    def sync_data(self, data: Any):
        """Update internal state when component data changes."""
        self.data = data
        if isinstance(data, dict):
            self._tags = set(data.get('tags', []))
            self.stack_group = data.get('stack_group')
        else:
            pass
    
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
        
    def recalculate(self) -> None:
        """
        Called when component stats have changed (e.g. modifiers applied).
        Override to update internal values derived from component stats.
        """
        pass

    def get_primary_value(self) -> float:
        """
        Return the primary numeric value for aggregation.
        Override in subclasses to return the appropriate value (e.g., thrust_force, capacity).
        Marker abilities return 0.0 by default.
        """
        return 0.0

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

    def sync_data(self, data: Any):
        super().sync_data(data)
        if isinstance(data, dict):
            self.resource_name = data.get('resource', self.resource_name)
            self.amount = data.get('amount', 0.0)
            self.trigger = data.get('trigger', 'constant')
        elif isinstance(data, (int, float)):
            self.amount = float(data)
            self.trigger = 'constant' # Default for shortcut

    def update(self) -> bool:
        if self.trigger == 'constant':
            # Need access to ship's resources
            if self.component.ship and self.component.ship.resources:
                res = self.component.ship.resources.get_resource(self.resource_name)
                if res:
                    # Constant consumption is per second, multiply by tick duration
                    cost = self.amount * PhysicsConfig.TICK_RATE
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

    def get_primary_value(self) -> float:
        return self.amount

class ResourceStorage(Ability):
    """
    Ability to store resources.
    Data: { "resource": "fuel", "amount": 100 }
    """
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.resource_type = data.get('resource', '')
        self.max_amount = data.get('amount', 0.0)

    def sync_data(self, data: Any):
        super().sync_data(data)
        if isinstance(data, dict):
            self.resource_type = data.get('resource', self.resource_type)
            self.max_amount = data.get('amount', 0.0)
        elif isinstance(data, (int, float)):
            self.max_amount = float(data)
        
    def get_ui_rows(self):
        color = '#64FFFF' # Cyan default for caps
        if self.resource_type == 'shield': color = '#00FFFF' # Standard Shield Cyan
        
        return [{'label': f"{self.resource_type.title()} Cap", 'value': f"{self.max_amount:.0f}", 'color_hint': color}]

    def get_primary_value(self) -> float:
        return self.max_amount

class ResourceGeneration(Ability):
    """
    Ability to generate resources.
    Data: { "resource": "energy", "amount": 10 }
    """
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.resource_type = data.get('resource', '')
        self.rate = data.get('amount', 0.0)

    def sync_data(self, data: Any):
        super().sync_data(data)
        if isinstance(data, dict):
            self.resource_type = data.get('resource', self.resource_type)
            self.rate = data.get('amount', 0.0)
        elif isinstance(data, (int, float)):
            self.rate = float(data)

    def get_ui_rows(self):
        color = '#FFFFFF' 
        if self.resource_type == 'energy': color = '#FFFF00' # Yellow
        
        return [{'label': f"{self.resource_type.title()} Gen", 'value': f"{self.rate:.1f}/s", 'color_hint': color}]

    def get_primary_value(self) -> float:
        return self.rate

# --- Core Mechanics ---

class CombatPropulsion(Ability):
    """Provides Thrust."""
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        # Handle 'val' if primitive shortcut used, else explicit 'value'
        val = data if isinstance(data, (int, float)) else data.get('value', 0)
        self.base_thrust = float(val)
        self.thrust_force = self.base_thrust

    def recalculate(self):
        self.thrust_force = self.base_thrust * self.component.stats.get('thrust_mult', 1.0)

    def get_ui_rows(self):
        return [{'label': 'Thrust', 'value': f"{self.thrust_force:.0f} N", 'color_hint': '#64FF64'}] # Light Green

    def get_primary_value(self) -> float:
        return self.thrust_force

class ManeuveringThruster(Ability):
    """Provides Rotation."""
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        val = data if isinstance(data, (int, float)) else data.get('value', 0)
        self.base_turn_rate = float(val)
        self.turn_rate = self.base_turn_rate

    def recalculate(self):
        self.turn_rate = self.base_turn_rate * self.component.stats.get('turn_mult', 1.0)

    def get_ui_rows(self):
        return [{'label': 'Turn Speed', 'value': f"{self.turn_rate:.1f} deg/s", 'color_hint': '#64FF96'}] # Slightly different green

    def get_primary_value(self) -> float:
        return self.turn_rate

class ShieldProjection(Ability):
    """Provides Shield Capacity."""
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        val = data if isinstance(data, (int, float)) else data.get('value', 0)
        self.base_capacity = float(val)
        self.capacity = self.base_capacity

    def recalculate(self):
        # Apply capacity_mult from component stats (populated by modifiers)
        mult = self.component.stats.get('capacity_mult', 1.0)
        self.capacity = self.base_capacity * mult

    def get_ui_rows(self):
        return [{'label': 'Shield Cap', 'value': f"{self.capacity:.0f}", 'color_hint': '#00FFFF'}] # Cyan

    def get_primary_value(self) -> float:
        return self.capacity

class ShieldRegeneration(Ability):
    """Regenerates Shields."""
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        val = data if isinstance(data, (int, float)) else data.get('value', 0)
        self.base_rate = float(val)
        self.rate = self.base_rate
        
    def recalculate(self):
        # Apply energy_gen_mult (modifier stat key)
        mult = self.component.stats.get('energy_gen_mult', 1.0) 
        self.rate = self.base_rate * mult

    def get_ui_rows(self):
        return [{'label': 'Regen', 'value': f"{self.rate:.1f}/s", 'color_hint': '#00C8FF'}] # Deep Sky Blue

    def get_primary_value(self) -> float:
        return self.rate

class VehicleLaunchAbility(Ability):
    """Allows storing and launching fighters."""
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.fighter_class = data.get('fighter_class', 'Fighter (Small)')
        self.capacity = data.get('capacity', 0)
        self._base_capacity = self.capacity
        self.cycle_time = data.get('cycle_time', 5.0)
        self.cooldown = 0.0

    def recalculate(self):
        # Apply capacity mult
        self.capacity = int(self._base_capacity * self.component.stats.get('capacity_mult', 1.0))
        
    def update(self) -> bool:
        if self.cooldown > 0:
            self.cooldown -= PhysicsConfig.TICK_RATE
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

    def get_primary_value(self) -> float:
        return float(self.capacity)

class CommandAndControl(Ability):
    """Marks component as providing ship command capability."""
    def get_ui_rows(self):
        return [{'label': 'Command', 'value': 'Active', 'color_hint': '#96FF96'}]

    def get_primary_value(self) -> float:
        return 1.0

class RequiresCommandAndControl(Ability):
    """Marker ability: Component (e.g. Hull) requires Command and Control to be operational."""
    def get_ui_rows(self):
        return [{'label': 'Requires C&C', 'value': 'Yes', 'color_hint': '#FFCC66'}]

    def get_primary_value(self) -> float:
        return 1.0

class RequiresCombatMovement(Ability):
    """Marker ability: Component (e.g. Hull) requires Combat Propulsion to be operational."""
    def get_ui_rows(self):
        return [{'label': 'Requires Propulsion', 'value': 'Yes', 'color_hint': '#FFCC66'}]

    def get_primary_value(self) -> float:
        return 1.0

class StructuralIntegrity(Ability):
    """Marker ability: Hull provides structural integrity for the ship."""
    def get_ui_rows(self):
        return [{'label': 'Structural Integrity', 'value': 'Yes', 'color_hint': '#96FF96'}]

class CrewCapacity(Ability):
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        val = data if isinstance(data, (int, float)) else data.get('value', 0)
        self.amount = int(val)
        self._base_amount = self.amount

    def recalculate(self):
        self.amount = int(self._base_amount * self.component.stats.get('crew_capacity_mult', 1.0))

    def get_ui_rows(self):
        return [{'label': 'Crew Cap', 'value': f"{self.amount}", 'color_hint': '#96FF96'}]

    def get_primary_value(self) -> float:
        return float(self.amount)

class LifeSupportCapacity(Ability):
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        val = data if isinstance(data, (int, float)) else data.get('value', 0)
        self.amount = int(val)
        self._base_amount = self.amount

    def recalculate(self):
        self.amount = int(self._base_amount * self.component.stats.get('life_support_capacity_mult', 1.0))

    def get_ui_rows(self):
        return [{'label': 'Life Support', 'value': f"{self.amount}", 'color_hint': '#96FFFF'}]

    def get_primary_value(self) -> float:
        return float(self.amount)

class CrewRequired(Ability):
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        val = data if isinstance(data, (int, float)) else data.get('value', data.get('amount', 0))
        self.amount = int(val)
        self._base_amount = self.amount

    def recalculate(self):
        # Crew requirements scale with mass (sqrt) AND specific multiplier
        mass_mult = self.component.stats.get('mass_mult', 1.0)
        if mass_mult < 0: mass_mult = 0
        crew_mult = math.sqrt(mass_mult)
        
        self.amount = int(math.ceil(self._base_amount * crew_mult * self.component.stats.get('crew_req_mult', 1.0)))

    def get_ui_rows(self):
        return [{'label': 'Crew Req', 'value': f"{self.amount}", 'color_hint': '#FF9696'}]

    def get_primary_value(self) -> float:
        return float(self.amount)

class ToHitAttackModifier(Ability):
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        val = data if isinstance(data, (int, float)) else data.get('value', 0)
        self.value = float(val)
        self._base_value = self.value

    def recalculate(self):
        # Apply generic properties or specific mult if needed. 
        # Modifiers usually stack by addition in 'properties', but if we want mult:
        # For now, just re-setting base in case we add multipliers later.
        pass

    def get_ui_rows(self):
        val = self.value
        sign = "+" if val >= 0 else ""
        return [{'label': 'Targeting', 'value': f"{sign}{val:.1f}", 'color_hint': '#FF6464'}]

    def get_primary_value(self) -> float:
        return self.value

class ToHitDefenseModifier(Ability):
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        val = data if isinstance(data, (int, float)) else data.get('value', 0)
        self.value = float(val)
        self._base_value = self.value

    def recalculate(self):
        pass

    def get_ui_rows(self):
        val = self.value
        sign = "+" if val >= 0 else ""
        return [{'label': 'Evasion', 'value': f"{sign}{val:.1f}", 'color_hint': '#64FFFF'}]

    def get_primary_value(self) -> float:
        return self.value

class EmissiveArmor(Ability):
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        val = data if isinstance(data, (int, float)) else data.get('value', 0)
        self.amount = int(val)
        self._base_amount = self.amount

    def recalculate(self):
        pass

    def get_ui_rows(self):
        return [{'label': 'Dmg Ignore', 'value': f"{self.amount}", 'color_hint': '#FFFF00'}]

    def get_primary_value(self) -> float:
        return float(self.amount)
        
# --- Weapon Abilities ---

class WeaponAbility(Ability):
    """Base for offensive capabilities."""
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        
        # Handle damage (may be number or formula string)
        if isinstance(data, dict):
            raw_damage = data.get('damage', 0)
        else:
            # Fallback to component base stats if data is not a dict (e.g. shortcut 'true')
            raw_damage = self.component.data.get('damage', 0)
            if not raw_damage: raw_damage = self.component.data.get('base_damage', 0)
            
        if isinstance(raw_damage, str) and raw_damage.startswith('='):
            from game.simulation.formula_system import evaluate_math_formula
            self.damage_formula = raw_damage[1:]  # Store without '='
            # Evaluate at range 0 for base value
            self.damage = float(max(0, evaluate_math_formula(self.damage_formula, {'range_to_target': 0})))
        else:
            self.damage_formula = None
            self.damage = float(raw_damage) if raw_damage else 0.0
        self._base_damage = self.damage  # Store for modifier sync
        
        # Handle range (may be number or formula string)
        if isinstance(data, dict):
            raw_range = data.get('range', 0)
        else:
            raw_range = self.component.data.get('range', 0)
            if not raw_range: raw_range = self.component.data.get('base_range', 0)
            
        if isinstance(raw_range, str) and raw_range.startswith('='):
            from game.simulation.formula_system import evaluate_math_formula
            self.range = float(max(0, evaluate_math_formula(raw_range[1:], {})))
        else:
            self.range = float(raw_range) if raw_range else 0.0
        self._base_range = self.range  # Store for modifier sync
        
        # Handle reload (may be number or formula string)  
        if isinstance(data, dict):
            raw_reload = data.get('reload', 1.0)
        else:
            raw_reload = self.component.data.get('reload', 1.0)
            if not raw_reload: raw_reload = self.component.data.get('base_reload', 1.0)
            
        if isinstance(raw_reload, str) and raw_reload.startswith('='):
            from game.simulation.formula_system import evaluate_math_formula
            self.reload_time = float(max(0.0, evaluate_math_formula(raw_reload[1:], {})))
        else:
            self.reload_time = float(raw_reload) if raw_reload is not None else 1.0
        self._base_reload = self.reload_time  # Store for modifier sync
        
        self.cooldown_timer = 0.0
        
        if isinstance(data, dict):
            self.firing_arc = float(data.get('firing_arc', 360))
            self.facing_angle = float(data.get('facing_angle', 0))
            self._tags.update(data.get('tags', []))
        else:
            self.firing_arc = float(self.component.data.get('firing_arc', 360))
            self.facing_angle = float(self.component.data.get('facing_angle', 0))
        
        self._base_firing_arc = self.firing_arc

    def sync_data(self, data: Any):
        super().sync_data(data)
        if not isinstance(data, dict): return
        
        # Syncing fields that might change in data
        if 'firing_arc' in data:
            self.firing_arc = float(data['firing_arc'])
            self._base_firing_arc = self.firing_arc
        if 'facing_angle' in data:
            self.facing_angle = float(data['facing_angle'])
        
        # Damage/Range/Reload might be formulas, but usually they are base values in data 
        # which recalculate() then uses to apply multipliers.
        # We update the _base_ values from data if they exist.
        if 'damage' in data:
            raw = data['damage']
            if isinstance(raw, str) and raw.startswith('='):
                 from game.simulation.formula_system import evaluate_math_formula
                 self._base_damage = float(max(0, evaluate_math_formula(raw[1:], {})))
            else:
                 self._base_damage = float(raw)
            self.damage = self._base_damage
        if 'range' in data:
            raw = data['range']
            if isinstance(raw, str) and raw.startswith('='):
                 from game.simulation.formula_system import evaluate_math_formula
                 self._base_range = float(max(0, evaluate_math_formula(raw[1:], {})))
            else:
                 self._base_range = float(raw)
            self.range = self._base_range
        if 'reload' in data:
            raw = data['reload']
            if isinstance(raw, str) and raw.startswith('='):
                 from game.simulation.formula_system import evaluate_math_formula
                 self._base_reload = float(max(0.0, evaluate_math_formula(raw[1:], {})))
            else:
                 self._base_reload = float(raw)
            self.reload_time = self._base_reload

    def recalculate(self):
        pass

        # Apply modifiers to base stats
        if hasattr(self, '_base_damage'):
            self.damage = self._base_damage * self.component.stats.get('damage_mult', 1.0)
        if hasattr(self, '_base_range'):
            self.range = self._base_range * self.component.stats.get('range_mult', 1.0)
        if hasattr(self, '_base_reload'):
            self.reload_time = self._base_reload * self.component.stats.get('reload_mult', 1.0)
            
        # Apply Arc Modifiers
        if hasattr(self, '_base_firing_arc'):
            # Check for override first (`arc_set`) then additive (`arc_add`)
            if self.component.stats.get('arc_set') is not None:
                self.firing_arc = self.component.stats['arc_set']
            else:
                self.firing_arc = self._base_firing_arc + self.component.stats.get('arc_add', 0.0)
        
        # Sync facing_angle from properties (if not already overridden)
        if 'facing_angle' in self.component.stats.get('properties', {}):
             if not hasattr(self.component, 'facing_angle'):
                self.facing_angle = self.component.stats['properties']['facing_angle']

    def update(self) -> bool:
        if self.cooldown_timer > 0:
            self.cooldown_timer -= PhysicsConfig.TICK_RATE
        return True

    def can_fire(self):
        return self.cooldown_timer <= 0

    def fire(self, target: Any) -> bool:
        """Execute weapon fire logic. Returns True if successfully fired."""
        if self.can_fire():
            # DEBUG: Commented out to reduce spam
            # print(f"DEBUG: {self.__class__.__name__}.fire() called for {self.component.name}", flush=True)
            # Consume resources via Component (Bridge to ResourceRegistry)
            if self.component:
                self.component.consume_activation()
                
            self.cooldown_timer = self.reload_time
            return True
        # else:
        #     print(f"DEBUG: {self.__class__.__name__}.fire() BLOCKED by cooldown for {self.component.name}: {self.cooldown_timer}")
        return False

    def get_damage(self, range_to_target: float = 0) -> float:
        """Evaluate damage at a specific range. Returns base damage if no formula."""
        if self.damage_formula:
            from game.simulation.formula_system import evaluate_math_formula
            context = {'range_to_target': range_to_target}
            return max(0.0, evaluate_math_formula(self.damage_formula, context))
        return self.damage

    def get_ui_rows(self):
        return [
            {'label': 'Damage', 'value': f"{self.damage:.0f}", 'color_hint': '#FF6464'}, # Red
            {'label': 'Range', 'value': f"{self.range:.0f}", 'color_hint': '#FFA500'}, # Orange
            {'label': 'Reload', 'value': f"{self.reload_time:.1f}s", 'color_hint': '#FFC864'} # Gold
        ]

    def get_primary_value(self) -> float:
        return self.damage

    def check_firing_solution(self, ship_pos, ship_angle, target_pos) -> bool:
        """
        Check if target is within Range and Arc.
        Encapsulates geometric logic previously done in ship_combat.py.
        """
        # 1. Range Check
        dist = ship_pos.distance_to(target_pos)
        if dist > self.range:
            log_debug(f"check_firing_solution Range FAIL: dist {dist} > range {self.range}")
            return False
            
        # 2. Arc Check
        # Vector to target
        aim_vec = target_pos - ship_pos
        aim_angle = math.degrees(math.atan2(aim_vec.y, aim_vec.x)) % 360
        
        # Component Global Facing
        comp_facing = (ship_angle + self.facing_angle) % 360
        
        # Shortest angular difference
        diff = (aim_angle - comp_facing + 180) % 360 - 180
        
        # Phase 7: Use epsilon for boundary floating point stability
        if abs(diff) <= (self.firing_arc / 2) + 0.01:
            return True

        log_debug(f"check_firing_solution Arc FAIL: diff {abs(diff)} > {self.firing_arc/2}")
        return False

class ProjectileWeaponAbility(WeaponAbility):
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        # Handle dict vs primitive shortcut
        if isinstance(data, dict):
            self.projectile_speed = float(data.get('projectile_speed', 500))
        else:
            self.projectile_speed = float(getattr(self.component, 'projectile_speed', 500))

    def get_ui_rows(self):
        rows = super().get_ui_rows()
        rows.append({'label': 'Speed', 'value': f"{self.projectile_speed:.0f}", 'color_hint': '#C8C832'}) # Yellow-ish
        return rows

class BeamWeaponAbility(WeaponAbility):
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        if isinstance(data, dict):
             self.accuracy_falloff = float(data.get('accuracy_falloff', 0.001))
             self.base_accuracy = float(data.get('base_accuracy', 1.0))
        else:
             self.accuracy_falloff = float(getattr(self.component, 'accuracy_falloff', 0.001))
             self.base_accuracy = float(getattr(self.component, 'base_accuracy', 1.0))
        self._base_accuracy = self.base_accuracy

    def recalculate(self):
        super().recalculate()
        self.base_accuracy = self._base_accuracy + self.component.stats.get('accuracy_add', 0.0)

    def get_ui_rows(self):
        rows = super().get_ui_rows()
        rows.append({'label': 'Accuracy', 'value': f"{int(self.base_accuracy*100)}%", 'color_hint': '#FFFF00'})
        return rows

    def calculate_hit_chance(self, distance: float, attack_score_bonus: float = 0.0, defense_score_penalty: float = 0.0) -> float:
        """
        Calculate hit chance using the Logistic Function (Sigmoid).
        Formula: P = 1 / (1 + e^-x)
        Where x = (BaseScore + AttackBonuses) - (RangePenalty + DefensePenalties)
        """
        # Range Penalty: falloff * distance
        range_penalty = self.accuracy_falloff * distance
        
        net_score = (self.base_accuracy + attack_score_bonus) - (range_penalty + defense_score_penalty)
        
        # Sigmoid Function
        try:
            # Clamp exp input to avoid overflow
            clamped_score = max(-20.0, min(20.0, net_score))
            chance = 1.0 / (1.0 + math.exp(-clamped_score))
        except OverflowError:
            chance = 0.0 if net_score < 0 else 1.0
            
        return chance

    def get_damage(self, range_to_target: float = 0) -> float:
        """Evaluate damage at a specific range. Returns base damage if no formula."""
        if self.damage_formula:
            from game.simulation.formula_system import evaluate_math_formula
            context = {'range_to_target': range_to_target}
            return max(0.0, evaluate_math_formula(self.damage_formula, context))
        return self.damage


class SeekerWeaponAbility(WeaponAbility):
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        if isinstance(data, dict):
            self.projectile_speed = float(data.get('projectile_speed', 500))
            self.endurance = float(data.get('endurance', 3.0))
            self.turn_rate = float(data.get('turn_rate', 30.0))
            self.to_hit_defense = float(data.get('to_hit_defense', 0.0))
        else:
            self.projectile_speed = float(getattr(self.component, 'projectile_speed', 500))
            self.endurance = float(getattr(self.component, 'endurance', 3.0))
            self.turn_rate = float(getattr(self.component, 'turn_rate', 30.0))
            self.to_hit_defense = float(getattr(self.component, 'to_hit_defense', 0.0))
        
        # Recalculate range based on endurance if basic range not set or derived
        # Seekers use 80% of straight-line range to account for maneuvering
        if self.range <= 0 and self.projectile_speed > 0:
             self.range = int(self.projectile_speed * self.endurance * 0.8)
             self._base_range = self.range

    def check_firing_solution(self, ship_pos, ship_angle, target_pos) -> bool:
        """Seekers are omni-directional and ignore firing arcs."""
        dist = ship_pos.distance_to(target_pos)
        return dist <= self.range

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
    "CommandAndControl": CommandAndControl,
    "CrewCapacity": CrewCapacity,
    "LifeSupportCapacity": LifeSupportCapacity,
    "CrewRequired": CrewRequired,
    "ToHitAttackModifier": ToHitAttackModifier,
    "ToHitDefenseModifier": ToHitDefenseModifier,
    "EmissiveArmor": EmissiveArmor,
    "Armor": lambda c, d: Ability(c, d), # Dummy ability for tag/existence checks

    "RequiresCommandAndControl": RequiresCommandAndControl,
    "RequiresCombatMovement": RequiresCombatMovement,
    "StructuralIntegrity": StructuralIntegrity,

    # Primitive/Shortcut Factories
    "FuelStorage": lambda c, d: ResourceStorage(c, {"resource": "fuel", "amount": d} if isinstance(d, (int, float)) else {**d, "resource": "fuel"}),
    "EnergyStorage": lambda c, d: ResourceStorage(c, {"resource": "energy", "amount": d} if isinstance(d, (int, float)) else {**d, "resource": "energy"}),
    "AmmoStorage": lambda c, d: ResourceStorage(c, {"resource": "ammo", "amount": d} if isinstance(d, (int, float)) else {**d, "resource": "ammo"}),
    "EnergyGeneration": lambda c, d: ResourceGeneration(c, {"resource": "energy", "amount": d} if isinstance(d, (int, float)) else {**d, "resource": "energy"}),
    "EnergyConsumption": lambda c, d: ResourceConsumption(c, {"resource": "energy", "amount": d, "trigger": "constant"} if isinstance(d, (int, float)) else {**d, "resource": "energy"}),
    "AmmoConsumption": lambda c, d: ResourceConsumption(c, {"resource": "ammo", "amount": d, "trigger": "activation"} if isinstance(d, (int, float)) else {**d, "resource": "ammo"})
}

# Map registry shortcut names to their actual class names for instance matching
ABILITY_CLASS_MAP = {
    "FuelStorage": "ResourceStorage",
    "EnergyStorage": "ResourceStorage",
    "AmmoStorage": "ResourceStorage",
    "EnergyGeneration": "ResourceGeneration",
    "EnergyConsumption": "ResourceConsumption",
    "AmmoConsumption": "ResourceConsumption",
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
