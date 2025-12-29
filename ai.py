import math
import json
import pygame
from components import LayerType
from logger import log_info
from ai_behaviors import RamBehavior, FleeBehavior, KiteBehavior, AttackRunBehavior, FormationBehavior
from game_constants import AttackType

# Load combat strategies from JSON
COMBAT_STRATEGIES = {}
ENGAGE_DISTANCES = {}

def load_combat_strategies(filepath="data/combatstrategies.json"):
    global COMBAT_STRATEGIES, ENGAGE_DISTANCES
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            COMBAT_STRATEGIES = data.get('strategies', {})
            ENGAGE_DISTANCES = data.get('engage_distances', {})
            log_info(f"Loaded {len(COMBAT_STRATEGIES)} combat strategies")
    except FileNotFoundError:
        print(f"Warning: {filepath} not found, using defaults")
        COMBAT_STRATEGIES = {
            'max_range': {
                'name': 'Max Range',
                'engage_distance': 'max_range',
                'targeting_priority': ['nearest'],
                'avoid_collisions': True,
                'retreat_hp_threshold': 0.1
            }
        }
        ENGAGE_DISTANCES = {'max_range': 1.0, 'ram': 0}

# Load on module import
load_combat_strategies()

def get_strategy_names():
    """Return list of available strategy IDs for UI."""
    return list(COMBAT_STRATEGIES.keys())

class AIController:
    def __init__(self, ship, grid, enemy_team_id):
        self.ship = ship
        self.grid = grid
        self.enemy_team_id = enemy_team_id
        self.last_strategy = None
        
        # Initialize behaviors
        self.behaviors = {
            'ram': RamBehavior(self),
            'flee': FleeBehavior(self),
            'kite': KiteBehavior(self),
            'attack_run': AttackRunBehavior(self),
            'formation': FormationBehavior(self)
        }
        self.current_behavior = None
        self.attack_state = 'approach' 
        self.attack_timer = 0
        
    def get_current_strategy(self):
        """Get strategy definition for ship's current strategy."""
        strategy_id = getattr(self.ship, 'ai_strategy', 'max_weapons_range')
        return COMBAT_STRATEGIES.get(strategy_id, COMBAT_STRATEGIES.get('max_weapons_range', {}))
    
    def get_engage_distance_multiplier(self, strategy):
        """Helper for behaviors to get engage distance multiplier."""
        engage_key = strategy.get('engage_distance', 'max_range')
        return ENGAGE_DISTANCES.get(engage_key, 1.0)
    
    def find_target(self):
        """Find target based on strategy's targeting priority."""
        candidates = self.grid.query_radius(self.ship.position, 200000)
        enemies = [obj for obj in candidates 
                   if obj.is_alive and hasattr(obj, 'team_id') 
                   and obj.team_id == self.enemy_team_id
                   and not getattr(obj, 'is_derelict', False)]
        
        
        if not enemies:
            return None
            
        strategy = self.get_current_strategy()
        priorities = strategy.get('targeting_priority', ['nearest'])
        


        # Score each enemy based on priorities
        def score_target(enemy):
            score = 0
            for i, priority in enumerate(priorities):
                weight = len(priorities) - i
                
                if priority == 'nearest':
                    dist = self.ship.position.distance_to(enemy.position)
                    score -= dist * weight  # Negative = prefer closer
                elif priority == 'farthest':
                    dist = self.ship.position.distance_to(enemy.position)
                    score += dist * weight
                elif priority == 'largest':
                    score += getattr(enemy, 'mass', 100) * weight
                elif priority == 'smallest':
                    score -= getattr(enemy, 'mass', 100) * weight
                elif priority == 'fastest':
                    speed = getattr(enemy, 'velocity', pygame.math.Vector2(0,0)).length()
                    score += speed * weight
                elif priority == 'slowest':
                    speed = getattr(enemy, 'velocity', pygame.math.Vector2(0,0)).length()
                    score -= speed * weight
                elif priority == 'most_damaged':
                    hp_pct = self._get_hp_percent(enemy)
                    score -= hp_pct * weight * 100
                elif priority == 'least_damaged':
                    hp_pct = self._get_hp_percent(enemy)
                    score += hp_pct * weight * 100
                elif priority == 'strongest':
                    score += getattr(enemy, 'mass', 100) * weight
                elif priority == 'weakest':
                    score -= getattr(enemy, 'mass', 100) * weight
                elif priority == 'has_weapons':
                    has_wpns = any(hasattr(c, 'damage') for layer in getattr(enemy, 'layers', {}).values() 
                                   for c in layer.get('components', []))
                    score += weight * 1000 if has_wpns else 0
                elif priority == 'most_armor':
                    armor_hp = getattr(enemy, 'layers', {}).get(LayerType.ARMOR, {}).get('hp_pool', 0)
                    score += armor_hp * weight
                elif priority == 'least_armor':
                    armor_hp = getattr(enemy, 'layers', {}).get(LayerType.ARMOR, {}).get('hp_pool', 0)
                    score -= armor_hp * weight
                elif priority == 'missiles_in_pdc_arc':
                    e_type = getattr(enemy, 'type', '')
                    is_missile = e_type == 'missile' or e_type == AttackType.MISSILE
                    if is_missile:
                        if self._is_in_pdc_arc(enemy):
                             score += weight * 2000
                        else:
                             return -float('inf')
            return score
        

        
        # Candidates expansion: If missile priority is active, we must include projectiles
        if 'missiles_in_pdc_arc' in priorities:
             missiles = [obj for obj in self.grid.query_radius(self.ship.position, 1500) 
                         if (getattr(obj, 'type', '') == 'missile' or getattr(obj, 'type', '') == AttackType.MISSILE)
                         and obj.is_alive 
                         and getattr(obj, 'team_id', -1) != self.ship.team_id]
             enemies.extend(missiles)
        
        # Sort by score info desc
        enemies.sort(key=score_target, reverse=True)
        
        # Filter negative infinity (hard filter)
        valid_enemies = [e for e in enemies if score_target(e) > -9000000]
        
        return valid_enemies[:1][0] if valid_enemies else None

    def find_secondary_targets(self):
        """Find additional targets if ship has multiplex tracking."""
        max_targets = getattr(self.ship, 'max_targets', 1)
        if max_targets <= 1:
            return []
            
        count_needed = max_targets - 1
        current = self.ship.current_target
        
        candidates = self.grid.query_radius(self.ship.position, 200000)
        enemies = [obj for obj in candidates 
                   if obj.is_alive and hasattr(obj, 'team_id') 
                   and obj.team_id == self.enemy_team_id
                   and not getattr(obj, 'is_derelict', False)
                   and obj != current]
                   
        if not enemies:
            return []
            
        strategy = self.get_current_strategy()
        priorities = strategy.get('targeting_priority', ['nearest'])
        
        def score_target(enemy):
            score = 0
            for i, priority in enumerate(priorities):
                weight = len(priorities) - i
                if priority == 'nearest':
                    dist = self.ship.position.distance_to(enemy.position)
                    score -= dist * weight
                elif priority == 'farthest':
                    dist = self.ship.position.distance_to(enemy.position)
                    score += dist * weight
                elif priority == 'largest':
                    score += getattr(enemy, 'mass', 100) * weight
                elif priority == 'smallest':
                    score -= getattr(enemy, 'mass', 100) * weight
                elif priority == 'fastest':
                    speed = getattr(enemy, 'velocity', pygame.math.Vector2(0,0)).length()
                    score += speed * weight
                elif priority == 'slowest':
                    speed = getattr(enemy, 'velocity', pygame.math.Vector2(0,0)).length()
                    score -= speed * weight
                elif priority == 'most_damaged':
                    hp_pct = self._get_hp_percent(enemy)
                    score -= hp_pct * weight * 100
                elif priority == 'least_damaged':
                    hp_pct = self._get_hp_percent(enemy)
                    score += hp_pct * weight * 100
                elif priority == 'strongest':
                    score += getattr(enemy, 'mass', 100) * weight
                elif priority == 'weakest':
                    score -= getattr(enemy, 'mass', 100) * weight
                elif priority == 'has_weapons':
                    has_wpns = any(hasattr(c, 'damage') for layer in getattr(enemy, 'layers', {}).values() 
                                   for c in layer.get('components', []))
                    score += weight * 1000 if has_wpns else 0
                elif priority == 'most_armor':
                    armor_hp = getattr(enemy, 'layers', {}).get(LayerType.ARMOR, {}).get('hp_pool', 0)
                    score += armor_hp * weight
                elif priority == 'least_armor':
                    armor_hp = getattr(enemy, 'layers', {}).get(LayerType.ARMOR, {}).get('hp_pool', 0)
                    score -= armor_hp * weight
                elif priority == 'missiles_in_pdc_arc':
                    e_type = getattr(enemy, 'type', '')
                    is_missile = e_type == 'missile' or e_type == AttackType.MISSILE
                    if is_missile:
                        if self._is_in_pdc_arc(enemy):
                             score += weight * 2000
                        else:
                             return -float('inf')
            return score
            
        if 'missiles_in_pdc_arc' in priorities:
             missiles = [obj for obj in self.grid.query_radius(self.ship.position, 1500) 
                         if (getattr(obj, 'type', '') == 'missile' or getattr(obj, 'type', '') == AttackType.MISSILE)
                         and obj.is_alive 
                         and getattr(obj, 'team_id', -1) != self.ship.team_id]
             enemies.extend(missiles)
        
        enemies.sort(key=score_target, reverse=True)
        valid_enemies = [e for e in enemies if score_target(e) > -9999]
        return valid_enemies[:count_needed]

    def _is_in_pdc_arc(self, target):
        """Check if target is within range and arc of at least one active PDC."""
        import math
        from components import Weapon
        
        for layer in self.ship.layers.values():
            for comp in layer['components']:
                if isinstance(comp, Weapon) and comp.is_active and comp.abilities.get('PointDefense', False):
                    dist = self.ship.position.distance_to(target.position)
                    if dist > comp.range: continue
                    
                    vec_to_target = target.position - self.ship.position
                    if vec_to_target.length_squared() == 0: continue
                    
                    angle_to_target = math.degrees(math.atan2(vec_to_target.y, vec_to_target.x)) % 360
                    
                    ship_angle = self.ship.angle
                    comp_facing = (ship_angle + comp.facing_angle) % 360
                    diff = (angle_to_target - comp_facing + 180) % 360 - 180
                    
                    if abs(diff) <= comp.firing_arc:
                        return True
        return False

    def _get_hp_percent(self, ship):
        """Get ship's current HP as percentage."""
        total_max = sum(layer.get('max_hp_pool', 0) for layer in getattr(ship, 'layers', {}).values())
        total_current = sum(layer.get('hp_pool', 0) for layer in getattr(ship, 'layers', {}).values())
        
        if total_max == 0:
            for layer in getattr(ship, 'layers', {}).values():
                for comp in layer.get('components', []):
                    total_max += getattr(comp, 'max_hp', 0)
                    total_current += getattr(comp, 'current_hp', getattr(comp, 'max_hp', 0))
        
        return total_current / total_max if total_max > 0 else 1.0

    def update(self):
        if not self.ship.is_alive: 
            return

        # Master Turn Limiting & Slowdown (Run Always)
        self.ship.turn_throttle = 1.0 # Default
        
        # Reserve some engine power so followers can catch up (Simulated Formation Speed Cap)
        # If we run at 100%, followers behind us physically cannot catch up.
        self.ship.engine_throttle = 0.9 if self.ship.formation_members else 1.0 
        
        if self.ship.formation_members:
             diam = self.ship.radius * 2
             
             # 1. Calculate Max Formation Radius for Turn Limit
             max_radius = 0
             
             # ... (keep radius search) ...
             for member in self.ship.formation_members:
                 if member.formation_offset:
                     r = member.formation_offset.length()
                     if r > max_radius:
                         max_radius = r
             
             # Limit turn rate
             if max_radius > 0:
                 max_speed = getattr(self.ship, 'max_speed', 10) 
                 max_w_rad = max_speed / max_radius
                 max_w_deg = math.degrees(max_w_rad)
                 
                 base_turn_per_tick = self.ship.turn_speed / 100.0
                 if base_turn_per_tick > 0:
                     turn_limit_throttle = max_w_deg / base_turn_per_tick
                     self.ship.turn_throttle = min(self.ship.turn_throttle, turn_limit_throttle)

             # 2. Existing Slowdown for Out-of-Position ships
             slow_down = False
             for member in self.ship.formation_members:
                 if not member.is_alive or not member.in_formation: continue
                 
                 # Calculate where member SHOULD be
                 rotated_offset = member.formation_offset.rotate(self.ship.angle)
                 target_pos = self.ship.position + rotated_offset
                 
                 d = member.position.distance_to(target_pos)
                 # Tighten tolerance: if followers are > 0.5 diameter out, slow down
                 if d > 0.5 * diam:
                     slow_down = True
                     break
             
             if slow_down:
                 self.ship.engine_throttle = 0.75
                 self.ship.turn_throttle = min(self.ship.turn_throttle, 0.75)


        # 0. Formation Damage Check (Dropout)
        if self.ship.in_formation and self.ship.formation_master:
             from components import Engine, Thruster
             dmg = False
             for layer in self.ship.layers.values():
                 for comp in layer['components']:
                     if isinstance(comp, (Engine, Thruster)):
                         if getattr(comp, 'current_hp', 1) < getattr(comp, 'max_hp', 1):
                             dmg = True
                             break
                 if dmg: break
             
             if dmg:
                 self.ship.in_formation = False
                 try:
                     self.ship.formation_master.formation_members.remove(self.ship)
                 except ValueError: pass
                 self.ship.formation_master = None
                 # Reset throttles
                 self.ship.turn_throttle = 1.0
                 self.ship.engine_throttle = 1.0

        # Derelict Check
        if getattr(self.ship, 'is_derelict', False):
            self.ship.comp_trigger_pulled = False
            self.ship.target_speed = 0 
            return

        strategy = self.get_current_strategy()
        strategy_id = getattr(self.ship, 'ai_strategy', 'max_weapons_range')
        
        # Formation Targeting Sync
        if self.ship.in_formation and self.ship.formation_master:
             master_target = self.ship.formation_master.current_target
             if master_target and master_target.is_alive and not getattr(master_target, 'is_derelict', False):
                 self.ship.current_target = master_target

        # Target Acquisition (Standard)
        target = self.ship.current_target
        if target:
            if not target.is_alive or getattr(target, 'is_derelict', False):
                target = None
                self.ship.current_target = None
                self.ship.secondary_targets = []

        if not target and not (self.ship.in_formation and self.ship.formation_master):
            target = self.find_target()
            self.ship.current_target = target
            
        if self.ship.max_targets > 1:
            self.ship.secondary_targets = self.find_secondary_targets()
        else:
            self.ship.secondary_targets = []

        if not target and not (self.ship.in_formation and self.ship.formation_master):
            self.ship.comp_trigger_pulled = False
            # If formation follower has no target but is in formation, it should still move!
            # So we check formation status before returning.
            # But behavior.update expects a target.
            # FormationBehavior uses master as target (implicitly).
            pass
            
        if not target and not self.ship.in_formation:
             self.ship.comp_trigger_pulled = False
             return

        self.ship.comp_trigger_pulled = True
        
        # Satellite Exception: Satellites do NOT navigate.
        if getattr(self.ship, 'vehicle_type', 'Ship') == 'Satellite':
             return

        # Determine Behavior
        if self.ship.in_formation and self.ship.formation_master:
            behavior_key = 'formation'
        else:
            behavior_key = 'kite' # Default
            
            # Check retreat condition
            hp_pct = self._get_hp_percent(self.ship)
            retreat_threshold = strategy.get('retreat_hp_threshold', 0.1)
            
            if hp_pct <= retreat_threshold and retreat_threshold > 0:
                behavior_key = 'flee'
            else:
                # Check for explicit behavior defined in strategy (Extension Point)
                behavior_key = strategy.get('behavior')
                
                if not behavior_key:
                    # Legacy Inference
                    engage_key = strategy.get('engage_distance', 'max_range')
                    if engage_key == 'ram':
                        behavior_key = 'ram'
                    elif strategy.get('attack_run_behavior'):
                        behavior_key = 'attack_run'
                    else:
                        behavior_key = 'kite'
        
        # Switch behavior if needed
        behavior = self.behaviors.get(behavior_key)
        
        if self.current_behavior != behavior:
            # Note: We don't check strategy change for formation switch
            if behavior:
                behavior.enter()
            self.current_behavior = behavior
            # self.last_strategy = strategy_id cannot be relied on if we switch back and forth
            
        # Execute behavior
        if self.current_behavior:
            # Only execute combat behaviors if we have a target
            # FormationBehavior handles its own internal targeting (positioning)
            if target or self.current_behavior == self.behaviors.get('formation'):
                self.current_behavior.update(target, strategy)

    def check_avoidance(self):
        """Check for nearby collisions and return evasion point."""
        nearby = self.grid.query_radius(self.ship.position, 1000)
        closest = None
        min_d = float('inf')
        
        for obj in nearby:
            if obj == self.ship: continue
            if not obj.is_alive: continue
            if not hasattr(obj, 'team_id'): continue
            
            # Simple physical radius check
            d = self.ship.position.distance_to(obj.position)
            thresh = self.ship.radius + getattr(obj, 'radius', 40) + 100
            
            if d < thresh:
                if d < min_d:
                    min_d = d
                    closest = obj
        
        if closest:
            # Evade
            vec = self.ship.position - closest.position
            if vec.length() == 0: vec = pygame.math.Vector2(1,0)
            return self.ship.position + vec.normalize() * 500
        return None

    def navigate_to(self, target_pos, stop_dist=0, precise=False):
        """Common navigation logic used by behaviors."""
        distance = self.ship.position.distance_to(target_pos)
        
        dx = target_pos.x - self.ship.position.x
        dy = target_pos.y - self.ship.position.y
        
        target_angle = math.degrees(math.atan2(dy, dx)) % 360
        current_angle = self.ship.angle % 360
        
        angle_diff = (target_angle - current_angle + 180) % 360 - 180
        
        # Rotate
        if abs(angle_diff) > 5:
            direction = 1 if angle_diff > 0 else -1
            self.ship.rotate(direction)
        
        # Thrust
        eff_stop_dist = stop_dist
        
        if abs(angle_diff) < 30 and distance > eff_stop_dist:
             self.ship.thrust_forward()

