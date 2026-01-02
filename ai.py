import math
import json
import os
import pygame
from components import LayerType
from logger import log_info
from ai_behaviors import (RamBehavior, FleeBehavior, KiteBehavior, AttackRunBehavior, 
                          FormationBehavior, DoNothingBehavior, StraightLineBehavior,
                          RotateOnlyBehavior, ErraticBehavior, OrbitBehavior)
from game_constants import AttackType

# Global Managers
STRATEGY_MANAGER = None

class StrategyManager:
    def __init__(self):
        self.targeting_policies = {}
        self.movement_policies = {}
        self.strategies = {}
        self.defaults = {
            'targeting': {'name': 'Default', 'rules': [{'type': 'nearest', 'weight': 100}]},
            'movement': {'behavior': 'kite', 'engage_distance': 'max_range', 'retreat_hp_threshold': 0.1, 'avoid_collisions': True},
            'strategy': {'name': 'Default', 'targeting_policy': 'standard', 'movement_policy': 'kite_max'}
        }

    def load_data(self, base_path="data", targeting_file="targeting_policies.json", movement_file="movement_policies.json", strategy_file="combat_strategies.json"):
        # Load Targeting Policies
        try:
            with open(os.path.join(base_path, targeting_file), 'r') as f:
                self.targeting_policies = json.load(f).get('policies', {})
        except FileNotFoundError:
            print(f"Warning: {targeting_file} not found in {base_path}")
            
        # Load Movement Policies
        try:
            with open(os.path.join(base_path, movement_file), 'r') as f:
                self.movement_policies = json.load(f).get('policies', {})
        except FileNotFoundError:
             print(f"Warning: {movement_file} not found in {base_path}")

        # Load Strategies
        try:
            with open(os.path.join(base_path, strategy_file), 'r') as f:
                self.strategies = json.load(f).get('strategies', {})
        except FileNotFoundError:
             print(f"Warning: {strategy_file} not found in {base_path}")
             
        log_info(f"StrategyManager loaded: {len(self.strategies)} strategies, {len(self.targeting_policies)} targeting, {len(self.movement_policies)} movement")

    def get_strategy(self, strategy_id):
        return self.strategies.get(strategy_id, self.defaults['strategy'])

    def get_targeting_policy(self, policy_id):
        return self.targeting_policies.get(policy_id, self.defaults['targeting'])
        
    def get_movement_policy(self, policy_id):
        return self.movement_policies.get(policy_id, self.defaults['movement'])

    def resolve_strategy(self, strategy_id):
        """Returns fully resolved strategy object with policy data embedded (helper)."""
        strat_def = self.get_strategy(strategy_id)

        t_pol = self.get_targeting_policy(strat_def.get('targeting_policy'))
        m_pol = self.get_movement_policy(strat_def.get('movement_policy'))
        
        return {
            'definition': strat_def,
            'targeting': t_pol,
            'movement': m_pol
        }

def load_combat_strategies(filepath=None):
    """Entry point for loading. Filepath arg is legacy/optional override for base path."""
    global STRATEGY_MANAGER
    STRATEGY_MANAGER = StrategyManager()
    
    # Determine base path from filepath or default
    if filepath:
        base_dir = os.path.dirname(filepath)
    else:
        base_dir = "data"
        
    STRATEGY_MANAGER.load_data(base_dir)

# Initialize on import
load_combat_strategies()

def get_strategy_names():
    """Return list of available strategy IDs for UI."""
    if STRATEGY_MANAGER:
         return list(STRATEGY_MANAGER.strategies.keys())
    return []

# Legacy support for tests/other modules accessing strategies directly
# We expose a proxy or just the internal dict if needed, but better to use Manager
COMBAT_STRATEGIES = STRATEGY_MANAGER.strategies if STRATEGY_MANAGER else {}


class TargetEvaluator:
    """Helper to evaluate targets based on rules."""
    @staticmethod
    def evaluate(ship, candidate, rules):
        score = 0
        
        for rule in rules:
            r_type = rule.get('type')
            weight = rule.get('weight', 0)
            factor = rule.get('factor', 1) # Multiplier for continuous values
            required = rule.get('required', False)
            
            val = 0
            match = True
            
            if r_type == 'nearest':
                dist = ship.position.distance_to(candidate.position)
                # 'nearest' usually implies closer is better (higher score).
                # Existing logic: score -= dist * weight. 
                # If we use weight > 0, we can do score -= dist * weight
                # Or if using factor: score += dist * factor (where factor is negative)
                if weight > 0:
                    val = -dist * weight
                else:
                    val = dist * factor
                    
            elif r_type == 'farthest':
                dist = ship.position.distance_to(candidate.position)
                if weight > 0:
                     val = dist * weight
                else:
                     val = dist * factor
                     
            elif r_type == 'distance':
                # Generic distance rule
                dist = ship.position.distance_to(candidate.position)
                val = dist * factor
                
            elif r_type == 'mass' or r_type == 'largest':
                mass = getattr(candidate, 'mass', 100)
                if weight > 0:
                    val = mass * weight
                else:
                    val = mass * factor
                    
            elif r_type == 'smallest':
                mass = getattr(candidate, 'mass', 100)
                # Smallest means lower mass is better
                if weight > 0:
                    val = -mass * weight
                else:
                    val = mass * factor # factor should be negative
                    
            elif r_type == 'fastest':
                speed = getattr(candidate, 'velocity', pygame.math.Vector2(0,0)).length()
                val = speed * (weight if weight > 0 else factor)
                
            elif r_type == 'slowest':
                speed = getattr(candidate, 'velocity', pygame.math.Vector2(0,0)).length()
                val = -speed * (weight if weight > 0 else -factor)
                
            elif r_type == 'most_damaged':
                hp_pct = AIController._stat_get_hp_percent(candidate)
                # Lower HP % is better
                # Existing: score -= hp_pct * weight * 100
                if weight > 0:
                    val = -hp_pct * weight * 100
                else:
                    val = hp_pct * factor

            elif r_type == 'least_damaged':
                hp_pct = AIController._stat_get_hp_percent(candidate)
                 # Higher HP % is better
                if weight > 0:
                    val = hp_pct * weight * 100
                else:
                    val = hp_pct * factor
                    
            elif r_type == 'strongest':
                 # Usually alias for mass/weapons?
                 # Existing uses mass
                 mass = getattr(candidate, 'mass', 100)
                 val = mass * (weight if weight > 0 else factor)
                 
            elif r_type == 'weakest':
                 mass = getattr(candidate, 'mass', 100)
                 val = -mass * (weight if weight > 0 else -factor)
                 
            elif r_type == 'has_weapons':
                 has_wpns = any(hasattr(c, 'damage') for layer in getattr(candidate, 'layers', {}).values() 
                                   for c in layer.get('components', []))
                 if has_wpns:
                     val = weight if weight > 0 else 1000
                 else:
                     if required: match = False
            
            elif r_type == 'least_armor':
                 armor_hp = getattr(candidate, 'layers', {}).get(LayerType.ARMOR, {}).get('hp_pool', 0)
                 params = -armor_hp * (weight if weight > 0 else -factor)
                 val = params
                 
            elif r_type == 'pdc_arc' or r_type == 'missiles_in_pdc_arc':
                e_type = getattr(candidate, 'type', '')
                is_missile = e_type == 'missile' or e_type == AttackType.MISSILE
                if is_missile:
                    in_arc = AIController._stat_is_in_pdc_arc(ship, candidate)
                    if in_arc:
                        val = weight if weight > 0 else 2000
                    else:
                        if required: match = False
                        else: 
                             # Strong penalty if not required but logic implies we want it?
                             # Actually typical behavior: if rule exists, we prioritize it.
                             val = -999999 
                             match = False 
                else:
                    # If rule is specific to missiles (pdc_arc), and target is NOT missile, 
                    # pass
                    pass

            if required and not match:
                return -float('inf')
                
            score += val
            
        return score


class AIController:
    def __init__(self, ship, grid, enemy_team_id):
        self.ship = ship
        self.grid = grid
        self.enemy_team_id = enemy_team_id
        
        # Initialize behaviors
        self.behaviors = {
            'ram': RamBehavior(self),
            'flee': FleeBehavior(self),
            'kite': KiteBehavior(self),
            'attack_run': AttackRunBehavior(self),
            'formation': FormationBehavior(self),
            # Test-specific behaviors
            'do_nothing': DoNothingBehavior(self),
            'straight_line': StraightLineBehavior(self),
            'rotate_only': RotateOnlyBehavior(self),
            'erratic': ErraticBehavior(self),
            'orbit': OrbitBehavior(self)
        }
        self.current_behavior = None
        self.attack_state = 'approach' 
        self.attack_timer = 0
        
    def get_resolved_strategy(self):
        strategy_id = getattr(self.ship, 'ai_strategy', 'standard_ranged')
        return STRATEGY_MANAGER.resolve_strategy(strategy_id)

    def get_engage_distance_multiplier(self, policy):
        """Helper to get engage distance multiplier from policy."""
        val = policy.get('engage_distance', 'max_range')
        if val == 'max_range':
            return 1.0
        elif val == 'ram':
            return 0.0
        elif isinstance(val, (int, float)):
            return float(val)
        return 1.0

    def find_target(self):
        """Find target based on strategy's targeting priority."""
        candidates = self.grid.query_radius(self.ship.position, 200000)
        enemies = [obj for obj in candidates 
                   if obj.is_alive and hasattr(obj, 'team_id') 
                   and obj.team_id == self.enemy_team_id]
        
        resolved = self.get_resolved_strategy()
        targeting_policy = resolved['targeting']
        rules = targeting_policy.get('rules', [])
        
        # Special case: check for missiles if policy cares about them
        check_missiles = any(r.get('type') in ['pdc_arc', 'missiles_in_pdc_arc'] for r in rules)
        
        if check_missiles:
             missiles = [obj for obj in self.grid.query_radius(self.ship.position, 1500) 
                         if (getattr(obj, 'type', '') == 'missile' or getattr(obj, 'type', '') == AttackType.MISSILE)
                         and obj.is_alive 
                         and getattr(obj, 'team_id', -1) != self.ship.team_id]
             enemies.extend(missiles)
        
        if not enemies:
            return None

        # Score
        scored_enemies = []
        for e in enemies:
            score = TargetEvaluator.evaluate(self.ship, e, rules)
            if score > -float('inf'):
                scored_enemies.append((score, e))
                
        scored_enemies.sort(key=lambda x: x[0], reverse=True)
        
        return scored_enemies[0][1] if scored_enemies else None

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
                   and obj != current]
        
        resolved = self.get_resolved_strategy()
        targeting_policy = resolved['targeting']
        rules = targeting_policy.get('rules', [])
        
        # Check for missiles if policy cares about them
        check_missiles = any(r.get('type') in ['pdc_arc', 'missiles_in_pdc_arc'] for r in rules)
        
        if check_missiles:
            missiles = [obj for obj in self.grid.query_radius(self.ship.position, 1500) 
                        if (getattr(obj, 'type', '') == 'missile' or getattr(obj, 'type', '') == AttackType.MISSILE)
                        and obj.is_alive 
                        and getattr(obj, 'team_id', -1) != self.ship.team_id
                        and obj != current]
            enemies.extend(missiles)
        
        if not enemies:
            return []
        
        # Score
        scored_enemies = []
        for e in enemies:
            score = TargetEvaluator.evaluate(self.ship, e, rules)
            if score > -float('inf'):
                scored_enemies.append((score, e))
                
        scored_enemies.sort(key=lambda x: x[0], reverse=True)
        
        return [e for _, e in scored_enemies[:count_needed]] 

    @staticmethod
    def _stat_get_hp_percent(ship):
        """Static version for evaluator."""
        total_max = sum(layer.get('max_hp_pool', 0) for layer in getattr(ship, 'layers', {}).values())
        total_current = sum(layer.get('hp_pool', 0) for layer in getattr(ship, 'layers', {}).values())
        
        if total_max == 0:
            for layer in getattr(ship, 'layers', {}).values():
                for comp in layer.get('components', []):
                    total_max += getattr(comp, 'max_hp', 0)
                    total_current += getattr(comp, 'current_hp', getattr(comp, 'max_hp', 0))
        
        return total_current / total_max if total_max > 0 else 1.0
    
    def _get_hp_percent(self, ship):
        return AIController._stat_get_hp_percent(ship)

    @staticmethod
    def _stat_is_in_pdc_arc(ship, target):
        import math
        from components import Weapon
        
        for layer in ship.layers.values():
            for comp in layer.get('components', []):
                # Phase 4: Use ability-based check instead of isinstance(Weapon)
                if comp.has_ability('WeaponAbility') and comp.is_active and comp.has_pdc_ability():
                    dist = ship.position.distance_to(target.position)
                    if dist > comp.range: continue
                    
                    vec_to_target = target.position - ship.position
                    if vec_to_target.length_squared() == 0: continue
                    
                    angle_to_target = math.degrees(math.atan2(vec_to_target.y, vec_to_target.x)) % 360
                    
                    ship_angle = ship.angle
                    comp_facing = (ship_angle + comp.facing_angle) % 360
                    diff = (angle_to_target - comp_facing + 180) % 360 - 180
                    
                    if abs(diff) <= (comp.firing_arc / 2):
                        return True
        return False
        
    def _is_in_pdc_arc(self, target):
        return AIController._stat_is_in_pdc_arc(self.ship, target)

    def update(self):

        if not self.ship.is_alive: return

        # Throttle Reset
        self.ship.turn_throttle = 1.0
        self.ship.engine_throttle = 0.9 if self.ship.formation_members else 1.0 
        
        # Formation Logic (Inline for now, could be moved to Behavior)
        if self.ship.formation_members:
             self._handle_formation_master()

        # Formation Dropout Check
        if self.ship.in_formation and self.ship.formation_master:
             self._check_formation_integrity()

        resolved = self.get_resolved_strategy()
        movement_policy = resolved['movement']
        
        # Formation Targeting Sync
        if self.ship.in_formation and self.ship.formation_master:
             master_target = self.ship.formation_master.current_target
             if master_target and master_target.is_alive:
                 self.ship.current_target = master_target

        # Target Acquisition
        target = self.ship.current_target
        if target and not target.is_alive:
            target = None
            self.ship.current_target = None

        if not target and not (self.ship.in_formation and self.ship.formation_master):
            target = self.find_target()
            self.ship.current_target = target
        
        # Secondary target acquisition for ships with multiplex tracking
        if getattr(self.ship, 'max_targets', 1) > 1:
            self.ship.secondary_targets = self.find_secondary_targets()
        else:
            self.ship.secondary_targets = []
            
        if not target and not self.ship.in_formation:
             self.ship.comp_trigger_pulled = False
             return

        self.ship.comp_trigger_pulled = True
        
        # Satellite Exception
        if getattr(self.ship, 'vehicle_type', 'Ship') == 'Satellite':
             return

        # Determine Behavior
        if self.ship.in_formation and self.ship.formation_master:
            behavior_key = 'formation'
        else:
            # Policy-driven behavior selection
            hp_pct = self._get_hp_percent(self.ship)
            retreat_threshold = movement_policy.get('retreat_hp_threshold', 0.1)
            
            if hp_pct <= retreat_threshold and retreat_threshold > 0:
                behavior_key = 'flee'
            else:
                behavior_key = movement_policy.get('behavior', 'kite')
        

        
        # Execute Behavior
        behavior = self.behaviors.get(behavior_key)
        if self.current_behavior != behavior:
            if behavior: behavior.enter()
            self.current_behavior = behavior
            
        if self.current_behavior:
            # Merge movement policy with strategy definition for fire_while_retreating etc.
            behavior_context = dict(movement_policy)
            behavior_context.update(resolved.get('definition', {}))
            if target or self.current_behavior == self.behaviors.get('formation'):
                self.current_behavior.update(target, behavior_context)

    def _handle_formation_master(self):
        # (Same logic as original, just encapsulated)
        diam = self.ship.radius * 2
        max_radius = 0
        for member in self.ship.formation_members:
            if member.formation_offset:
                r = member.formation_offset.length()
                if r > max_radius: max_radius = r
        
        if max_radius > 0:
            max_speed = getattr(self.ship, 'max_speed', 10) 
            max_w_rad = max_speed / max_radius
            max_w_deg = math.degrees(max_w_rad)
            base_turn = self.ship.turn_speed / 100.0
            if base_turn > 0:
                turn_limit = max_w_deg / base_turn
                self.ship.turn_throttle = min(self.ship.turn_throttle, turn_limit)

        slow_down = False
        for member in self.ship.formation_members:
            if not member.is_alive or not member.in_formation: continue
            rotated_offset = member.formation_offset.rotate(self.ship.angle)
            target_pos = self.ship.position + rotated_offset
            d = member.position.distance_to(target_pos)
            if d > 0.5 * diam:
                slow_down = True
                break
        
        if slow_down:
            self.ship.engine_throttle = 0.75
            self.ship.turn_throttle = min(self.ship.turn_throttle, 0.75)

    def _check_formation_integrity(self):
        # Phase 4: Use ability-based checks instead of isinstance(Engine, Thruster)
        dmg = False
        for layer in self.ship.layers.values():
            for comp in layer.get('components', []):
                if comp.has_ability('CombatPropulsion') or comp.has_ability('ManeuveringThruster'):
                    if getattr(comp, 'current_hp', 1) < getattr(comp, 'max_hp', 1):
                        dmg = True; break
            if dmg: break
        
        if dmg:
            self.ship.in_formation = False
            try: self.ship.formation_master.formation_members.remove(self.ship)
            except: pass
            self.ship.formation_master = None
            self.ship.turn_throttle = 1.0
            self.ship.engine_throttle = 1.0

    def check_avoidance(self):
        """Check for nearby collisions."""
        nearby = self.grid.query_radius(self.ship.position, 1000)
        closest = None
        min_d = float('inf')
        
        for obj in nearby:
            if obj == self.ship: continue
            if not obj.is_alive: continue
            if not hasattr(obj, 'team_id'): continue
            
            d = self.ship.position.distance_to(obj.position)
            thresh = self.ship.radius + getattr(obj, 'radius', 40) + 100
            
            if d < thresh:
                if d < min_d:
                    min_d = d
                    closest = obj
        
        if closest:
            vec = self.ship.position - closest.position
            if vec.length() == 0: vec = pygame.math.Vector2(1,0)
            return self.ship.position + vec.normalize() * 500
        return None

    def navigate_to(self, target_pos, stop_dist=0, precise=False):
        distance = self.ship.position.distance_to(target_pos)
        dx = target_pos.x - self.ship.position.x
        dy = target_pos.y - self.ship.position.y
        target_angle = math.degrees(math.atan2(dy, dx)) % 360
        current_angle = self.ship.angle % 360
        angle_diff = (target_angle - current_angle + 180) % 360 - 180
        
        if abs(angle_diff) > 5:
            direction = 1 if angle_diff > 0 else -1
            self.ship.rotate(direction)
        
        eff_stop_dist = stop_dist
        if abs(angle_diff) < 30 and distance > eff_stop_dist:
             self.ship.thrust_forward()



