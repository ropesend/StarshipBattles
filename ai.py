import math
import json
import pygame
from components import LayerType
from logger import log_info

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
        self.attack_state = 'approach'
        self.attack_timer = 0
        self.last_strategy = None
        
    def get_current_strategy(self):
        """Get strategy definition for ship's current strategy."""
        strategy_id = getattr(self.ship, 'ai_strategy', 'max_weapons_range')
        return COMBAT_STRATEGIES.get(strategy_id, COMBAT_STRATEGIES.get('max_weapons_range', {}))
    
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
                weight = len(priorities) - i  # Higher weight for earlier priorities
                
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
                    score -= hp_pct * weight * 100  # Prefer lower HP%
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
            return score
        
        return max(enemies, key=score_target)

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
            
        # Use same scoring logic as primary for consistency, or just nearest?
        # User asked for "criteria for selecting targets should be that all weapons... should be able to fire".
        # This implies we should prioritize targets we CAN hit.
        # But for AI target selection (strategic), we usually stick to priorities.
        # Let's blindly trust strategy priorities for now, or just distance.
        # Re-using strategy logic:
        
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
                    # Only score high if it is a missile AND in arc
                    if getattr(enemy, 'type', '') == 'missile':
                        # Check strictly if it is in valid arc of any PDC
                        if self._is_in_pdc_arc(enemy):
                             score += weight * 2000 # High priority
                        else:
                             score -= 999999 # Hard filter: NEVER satisfy if not in arc?
                             # Or just very low priority? User said "never be on the list".
                             return -float('inf')
                    else:
                        pass # Ignore non-missiles for this specific priority, but don't penalize?

            return score
            
        # Candidates expansion: If missile priority is active, we must include projectiles
        if 'missiles_in_pdc_arc' in priorities:
             missiles = [obj for obj in self.grid.query_radius(self.ship.position, 1500) 
                         if getattr(obj, 'type', '') == 'missile' 
                         and obj.is_alive 
                         and getattr(obj, 'team_id', -1) != self.ship.team_id]
             enemies.extend(missiles)
        
        # Sort by score info desc
        enemies.sort(key=score_target, reverse=True)
        
        # Filter negative infinity (hard filter)
        valid_enemies = [e for e in enemies if score_target(e) > -9999]
        
        return valid_enemies[:count_needed]

    def _is_in_pdc_arc(self, target):
        """Check if target is within range and arc of at least one active PDC."""
        # This requires iterating ship components.
        import math
        from components import Weapon
        
        for layer in self.ship.layers.values():
            for comp in layer['components']:
                if isinstance(comp, Weapon) and comp.is_active and comp.abilities.get('PointDefense', False):
                    # Check Range
                    dist = self.ship.position.distance_to(target.position)
                    if dist > comp.range: continue
                    
                    # Check Arc
                    # Simple angle check to target (not lead pos, to be fast)
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
        # Check armor layer HP pool
        total_max = sum(layer.get('max_hp_pool', 0) for layer in getattr(ship, 'layers', {}).values())
        total_current = sum(layer.get('hp_pool', 0) for layer in getattr(ship, 'layers', {}).values())
        
        # If no armor HP pools, check individual component HP
        if total_max == 0:
            for layer in getattr(ship, 'layers', {}).values():
                for comp in layer.get('components', []):
                    total_max += getattr(comp, 'max_hp', 0)
                    total_current += getattr(comp, 'current_hp', getattr(comp, 'max_hp', 0))
        
        return total_current / total_max if total_max > 0 else 1.0

    def update(self):
        if not self.ship.is_alive: 
            return

        # Derelict Check - Stop all AI if derelict
        if getattr(self.ship, 'is_derelict', False):
            self.ship.comp_trigger_pulled = False
            self.ship.target_speed = 0 # Ensure we stop
            return

        strategy = self.get_current_strategy()
        strategy_id = getattr(self.ship, 'ai_strategy', 'max_weapons_range')
        
        # Target Acquisition (do this first so retreat can use target)
        target = self.ship.current_target
        
        # Check if current target is invalid or derelict
        if target:
            if not target.is_alive or getattr(target, 'is_derelict', False):
                target = None
                self.ship.current_target = None
                self.ship.secondary_targets = []

                
        if not target:
            target = self.find_target()
            self.ship.current_target = target
            
        # Update Secondary Targets if capable
        if self.ship.max_targets > 1:
            self.ship.secondary_targets = self.find_secondary_targets()
        else:
            self.ship.secondary_targets = []

            
        if not target:
            self.ship.comp_trigger_pulled = False
            return
            
        # Always attempt to fire if we have a target
        self.ship.comp_trigger_pulled = True
        
        # Check retreat condition
        hp_pct = self._get_hp_percent(self.ship)
        retreat_threshold = strategy.get('retreat_hp_threshold', 0.1)
        
        if hp_pct <= retreat_threshold and retreat_threshold > 0:
            # Retreat mode
            self.update_flee(target, strategy.get('fire_while_retreating', False))
            return
        
        # Satellite Exception: Satellites do NOT navigate or maneuver.
        # They are stationary platforms that just target and fire.
        if getattr(self.ship, 'vehicle_type', 'Ship') == 'Satellite':
            # Satellite AI: Just targeting and firing (comp_trigger already set above)
            # No movement, no navigation. Skip all movement logic.
            return
        
        # Reset state on strategy change
        if self.last_strategy != strategy_id:
            self.attack_state = 'approach'
            self.attack_timer = 0
            self.last_strategy = strategy_id
        
        # Get engage distance multiplier
        engage_key = strategy.get('engage_distance', 'max_range')
        engage_mult = ENGAGE_DISTANCES.get(engage_key, 1.0)
        
        # Dispatch based on engage distance
        if engage_key == 'ram':
            self.update_ramming(target)
        elif strategy.get('attack_run_behavior'):
            self.update_attack_run(target, strategy)
        else:
            self.update_range_engagement(target, engage_mult, strategy)

    def update_ramming(self, target):
        """Ram target, no avoidance."""
        self.navigate_to(target.position, stop_dist=0, precise=False)
        
    def update_flee(self, target, fire_while_fleeing=False):
        """Run away from target."""
        # Only fire while fleeing if strategy allows it
        self.ship.comp_trigger_pulled = fire_while_fleeing
        
        vec = self.ship.position - target.position
        if vec.length() == 0: 
            vec = pygame.math.Vector2(1, 0)
        
        flee_pos = self.ship.position + vec.normalize() * 1000
        self.navigate_to(flee_pos, stop_dist=0, precise=False)

    def update_attack_run(self, target, strategy):
        """Attack run: approach -> fire -> retreat -> repeat."""
        behavior = strategy.get('attack_run_behavior', {})
        approach_dist = self.ship.max_weapon_range * behavior.get('approach_distance', 0.3)
        retreat_dist = self.ship.max_weapon_range * behavior.get('retreat_distance', 0.8)
        retreat_duration = behavior.get('retreat_duration', 2.0)
        
        dist = self.ship.position.distance_to(target.position)
        
        if self.attack_state == 'approach':
            self.navigate_to(target.position, stop_dist=approach_dist, precise=False)
            
            if dist < approach_dist * 1.5:
                self.attack_state = 'retreat'
                self.attack_timer = retreat_duration
                
        elif self.attack_state == 'retreat':
            # Cycle-Based: 1 tick = 0.01 seconds. Decrement timer by 0.01.
            self.attack_timer -= 0.01
            
            vec = self.ship.position - target.position
            if vec.length() == 0: 
                vec = pygame.math.Vector2(1, 0)
            flee_pos = self.ship.position + vec.normalize() * 1000
            
            self.navigate_to(flee_pos, stop_dist=0, precise=False)
            
            if self.attack_timer <= 0 and dist > retreat_dist:
                self.attack_state = 'approach'

    def update_range_engagement(self, target, engage_mult, strategy):
        """Engage at specified range multiplier of max weapon range."""
        
        # Collision avoidance if enabled
        if strategy.get('avoid_collisions', True):
            override_pos = self.check_avoidance()
            if override_pos:
                self.navigate_to(override_pos, stop_dist=0, precise=False)
                return
        
        # Calculate optimal distance based on engage multiplier
        opt_dist = self.ship.max_weapon_range * engage_mult
        if opt_dist < 150:
            opt_dist = 150  # Minimum spacing
        
        dist = self.ship.position.distance_to(target.position)
        
        if dist > opt_dist:
            # Close in
            self.navigate_to(target.position, stop_dist=opt_dist, precise=True)
        else:
            # Kite - maintain distance
            vec = self.ship.position - target.position
            if vec.length() == 0: 
                vec = pygame.math.Vector2(1, 0)
            
            kite_pos = target.position + vec.normalize() * opt_dist
            self.navigate_to(kite_pos, stop_dist=0, precise=True)

    def update_max_range(self, target):
        # MAX RANGE (Kiting) - Original behavior + Coll Avoidance
        
        # Collision Avoidance (Only for subtle/smart strategies)
        override_pos = self.check_avoidance()
        if override_pos:
            self.navigate_to(override_pos, stop_dist=0, precise=False)
            return

        # Optimal Distance
        opt_dist = self.ship.max_weapon_range * 0.9
        if opt_dist < 200: opt_dist = 200 # Minimum spacing
        
        dist = self.ship.position.distance_to(target.position)
        
        if dist > opt_dist:
            # Close in
            self.navigate_to(target.position, stop_dist=opt_dist, precise=True)
        else:
            # Too close, back off or circle?
            # Back off logic similar to flee but keeping facing?
            # Simple kiting: just stop thrusting if too close, maybe reverse?
            # If we just stop, we drift.
            # Let's try to maintain distance.
            vec = self.ship.position - target.position
            if vec.length() == 0: vec = pygame.math.Vector2(1,0)
            
            # Kite point
            kite_pos = target.position + vec.normalize() * opt_dist
            self.navigate_to(kite_pos, stop_dist=0, precise=True)

    def check_avoidance(self):
        # Extracted Collision Logic
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
        # 1. Navigation
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
        # If precise, we slow down earlier
        eff_stop_dist = stop_dist
        
        if abs(angle_diff) < 30 and distance > eff_stop_dist:
            # Throttle if facing roughly right
             self.ship.thrust_forward()

    # attempt_fire removed, logic moved to Ship update via trigger

