"""
AI Controller - Ship Combat AI Decision Making

This module contains AIController, which provides autonomous behavior for
ships during combat. Each ship gets an AIController that selects targets,
chooses movement behaviors, and coordinates with formations.

Behavior Selection Flowchart:
    1. Is ship alive? → No: Return (no action)
    2. Is ship in formation with master? → Yes: Use 'formation' behavior
    3. Check HP percentage against retreat threshold
       - HP <= threshold → Use 'flee' behavior
    4. Otherwise → Use behavior from movement policy (default: 'kite')

Available Behaviors:
    - kite: Maintain optimal range, close in or back off as needed
    - attack_run: Approach target, fire, retreat, repeat cycle
    - ram: Move directly toward target, no collision avoidance
    - flee: Move away from target (optionally fire while retreating)
    - formation: Follow formation master, maintain offset position
    - orbit: Circle around target at fixed distance
    - stationary_fire: Don't move, just fire (for testing/satellites)
    - do_nothing: No movement or firing (for testing)

Targeting System:
    1. Query spatial grid for entities within TARGET_QUERY_RADIUS
    2. Filter to enemies (matching enemy_team_id)
    3. Include missiles if strategy rules care about them
    4. Score each candidate using TargetEvaluator and targeting rules
    5. Select highest-scoring target as primary
    6. If ship has multiplex tracking, select additional secondary targets

Strategy Resolution:
    Ships have an ai_strategy attribute (e.g., 'standard_ranged', 'aggressive').
    StrategyManager resolves this to a full strategy definition with:
    - targeting: rules for scoring targets
    - movement: behavior, engage_distance, retreat_hp_threshold
    - attack_run_behavior: approach/retreat distances and timing

Example:
    controller = AIController(ship_adapter, grid, enemy_team=1)
    controller.update()  # Called each tick by BattleEngine
"""
import math
import pygame
from game.core.config import AIConfig, BattleConfig
from game.ai.behaviors import (RamBehavior, FleeBehavior, KiteBehavior, AttackRunBehavior,
                          FormationBehavior, DoNothingBehavior, StraightLineBehavior,
                          RotateOnlyBehavior, ErraticBehavior, OrbitBehavior, StationaryFireBehavior)
from game.core.constants import AttackType, CombatConstants

# Re-export from strategy_manager for backward compatibility
from game.ai.strategy_manager import (
    StrategyManager,
    load_combat_strategies,
    get_strategy_names,
    reset_strategy_manager,
)

# Re-export TargetEvaluator for backward compatibility
from game.ai.target_evaluator import TargetEvaluator


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
            'stationary_fire': StationaryFireBehavior(self),
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
        return StrategyManager.instance().resolve_strategy(strategy_id)

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

    def _find_enemies_in_radius(self, exclude=None, check_missiles=False):
        """Find alive enemy entities within targeting radius.

        Args:
            exclude: Optional entity to exclude from results (e.g., primary target)
            check_missiles: If True, also include enemy missiles within missile query radius

        Returns:
            List of enemy entities (ships and optionally missiles)
        """
        candidates = self.grid.query_radius(self.ship.position, BattleConfig.TARGET_QUERY_RADIUS)
        enemies = [obj for obj in candidates
                   if obj.is_alive and hasattr(obj, 'team_id')
                   and obj.team_id == self.enemy_team_id
                   and obj != exclude]

        if check_missiles:
            missiles = [obj for obj in self.grid.query_radius(self.ship.position, BattleConfig.MISSILE_QUERY_RADIUS)
                        if (getattr(obj, 'type', '') == 'missile' or getattr(obj, 'type', '') == AttackType.MISSILE)
                        and obj.is_alive
                        and getattr(obj, 'team_id', -1) != self.ship.team_id
                        and obj != exclude]
            enemies.extend(missiles)

        return enemies

    def _score_and_sort_enemies(self, enemies, rules):
        """Score enemies using targeting rules and return sorted list (highest first).

        Args:
            enemies: List of potential targets
            rules: Targeting rules from strategy policy

        Returns:
            List of enemies sorted by score (highest first), excluding -inf scores
        """
        scored_enemies = []
        for e in enemies:
            score = TargetEvaluator.evaluate(self.ship, e, rules)
            if score > -float('inf'):
                scored_enemies.append((score, e))

        scored_enemies.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in scored_enemies]

    def find_target(self):
        """Find target based on strategy's targeting priority."""
        resolved = self.get_resolved_strategy()
        targeting_policy = resolved['targeting']
        rules = targeting_policy.get('rules', [])

        # Check if policy cares about missiles
        check_missiles = any(r.get('type') in ['pdc_arc', 'missiles_in_pdc_arc'] for r in rules)

        enemies = self._find_enemies_in_radius(check_missiles=check_missiles)
        if not enemies:
            return None

        sorted_enemies = self._score_and_sort_enemies(enemies, rules)
        return sorted_enemies[0] if sorted_enemies else None

    def find_secondary_targets(self):
        """Find additional targets if ship has multiplex tracking."""
        max_targets = getattr(self.ship, 'max_targets', CombatConstants.DEFAULT_MAX_TARGETS)
        if max_targets <= CombatConstants.DEFAULT_MAX_TARGETS:
            return []

        count_needed = max_targets - 1
        current = self.ship.current_target

        resolved = self.get_resolved_strategy()
        targeting_policy = resolved['targeting']
        rules = targeting_policy.get('rules', [])

        # Check if policy cares about missiles
        check_missiles = any(r.get('type') in ['pdc_arc', 'missiles_in_pdc_arc'] for r in rules)

        enemies = self._find_enemies_in_radius(exclude=current, check_missiles=check_missiles)
        if not enemies:
            return []

        sorted_enemies = self._score_and_sort_enemies(enemies, rules)
        return sorted_enemies[:count_needed]

    @staticmethod
    def _stat_get_hp_percent(ship):
        """Static version for evaluator - delegates to TargetEvaluator."""
        return TargetEvaluator._default_get_hp_percent(ship)

    def _get_hp_percent(self, ship):
        return TargetEvaluator._default_get_hp_percent(ship)

    @staticmethod
    def _stat_is_in_pdc_arc(ship, target):
        """Static version for evaluator - delegates to TargetEvaluator."""
        return TargetEvaluator._default_is_in_pdc_arc(ship, target)

    def _is_in_pdc_arc(self, target):
        return TargetEvaluator._default_is_in_pdc_arc(self.ship, target)

    def update(self):

        if not self.ship.is_alive:
            return

        # Throttle Reset
        self.ship.turn_throttle = 1.0
        self.ship.engine_throttle = AIConfig.FORMATION_ENGINE_THROTTLE if self.ship.formation_members else 1.0

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
        if getattr(self.ship, 'max_targets', CombatConstants.DEFAULT_MAX_TARGETS) > CombatConstants.DEFAULT_MAX_TARGETS:
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
            if behavior:
                behavior.enter()
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
                if r > max_radius:
                    max_radius = r

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
            if not member.is_alive or not member.in_formation:
                continue
            rotated_offset = member.formation_offset.rotate(self.ship.angle)
            target_pos = self.ship.position + rotated_offset
            d = member.position.distance_to(target_pos)
            if d > 0.5 * diam:
                slow_down = True
                break

        if slow_down:
            self.ship.engine_throttle = AIConfig.FORMATION_SLOWDOWN_THROTTLE
            self.ship.turn_throttle = min(self.ship.turn_throttle, AIConfig.FORMATION_SLOWDOWN_THROTTLE)

    def _check_formation_integrity(self):
        # Check if propulsion components are damaged
        dmg = False
        propulsion_comps = (
            self.ship.get_components_by_ability('CombatPropulsion', operational_only=False) +
            self.ship.get_components_by_ability('ManeuveringThruster', operational_only=False)
        )
        for comp in propulsion_comps:
            if getattr(comp, 'current_hp', 1) < getattr(comp, 'max_hp', 1):
                dmg = True
                break

        if dmg:
            self.ship.in_formation = False
            try:
                # Unwrap adapter if present: formation_members contains raw Ships,
                # but self.ship may be a ShipControllableAdapter
                own_ship = getattr(self.ship, 'ship', self.ship)
                own_ship.formation_master.formation_members.remove(own_ship)
            except (AttributeError, ValueError):
                pass
            self.ship.formation_master = None
            self.ship.turn_throttle = 1.0
            self.ship.engine_throttle = 1.0

    def check_avoidance(self):
        """Check for nearby collisions."""
        nearby = self.grid.query_radius(self.ship.position, BattleConfig.AVOIDANCE_RADIUS)
        closest = None
        min_d = float('inf')

        for obj in nearby:
            # Skip self: self.ship may be ShipControllableAdapter wrapping the raw ship
            # Grid contains raw Ship objects, so compare via .ship property if adapter
            own_ship = getattr(self.ship, 'ship', self.ship)
            if obj == own_ship:
                continue
            if not obj.is_alive:
                continue
            if not hasattr(obj, 'team_id'):
                continue

            d = self.ship.position.distance_to(obj.position)
            thresh = self.ship.radius + getattr(obj, 'radius', 40) + BattleConfig.COLLISION_BUFFER

            if d < thresh:
                if d < min_d:
                    min_d = d
                    closest = obj

        if closest:
            vec = self.ship.position - closest.position
            if vec.length() == 0:
                vec = pygame.math.Vector2(1, 0)
            return self.ship.position + vec.normalize() * BattleConfig.AVOIDANCE_TARGET_DISTANCE
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
