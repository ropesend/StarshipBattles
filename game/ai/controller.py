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

Exception Handling
==================
This module uses defensive programming for robustness during combat:
- Target evaluation failures are logged and targets are skipped
- Formation dropout failures are logged but don't interrupt combat
- All errors include ship/target context for debugging
"""
import logging
import math
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

from game.core.math import Vector2, angle_diff, angle_from_vector
from game.core.config import AIConfig, BattleTuning
from game.ai.behaviors import (RamBehavior, FleeBehavior, KiteBehavior, AttackRunBehavior,
                          FormationBehavior, DoNothingBehavior, StraightLineBehavior,
                          RotateOnlyBehavior, ErraticBehavior, OrbitBehavior, StationaryFireBehavior)
from game.core.constants import AttackType, CombatConstants
from game.core.protocols import is_combatant
from game.ai.protocols import is_projectile, IGridEntity
from game.ai.interfaces.controllable import ShipControllableAdapter
from game.ai.target_evaluator import TargetEvaluator
from game.ai.strategy_manager import StrategyManager
from game.ai.combat_utils import get_entity_id, get_hp_percent, is_in_pdc_arc

# Behaviors that can execute without an enemy target
_NO_TARGET_BEHAVIORS = frozenset({
    'straight_line', 'rotate_only', 'erratic', 'do_nothing', 'stationary_fire'
})

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

    def get_resolved_strategy(self) -> Dict[str, Any]:
        """Get the fully resolved strategy for this ship's AI strategy ID."""
        strategy_id = self.ship.get_ai_strategy()
        return StrategyManager.instance().resolve_strategy(strategy_id)

    def get_engage_distance_multiplier(self, policy) -> float:
        """Helper to get engage distance multiplier from policy."""
        val = policy.get('engage_distance', 'max_range')
        if val == 'max_range':
            return 1.0
        elif val == 'ram':
            return 0.0
        elif isinstance(val, (int, float)):
            return float(val)
        return 1.0

    def _find_enemies_in_radius(self, exclude: Optional[Any] = None, include_missiles: bool = False) -> List[Any]:
        """Find alive enemy entities within targeting radius.

        Args:
            exclude: Optional entity to exclude from results (e.g., primary target)
            include_missiles: If True, also include enemy missiles within missile query radius

        Returns:
            List of enemy entities (ships and optionally missiles)
        """
        candidates = self.grid.query_radius(self.ship.get_position(), BattleTuning.TARGET_QUERY_RADIUS)
        enemies = [obj for obj in candidates
                   if obj.is_alive and is_combatant(obj)
                   and obj.team_id == self.enemy_team_id
                   and obj != exclude]

        if include_missiles:
            missiles = [obj for obj in self.grid.query_radius(self.ship.get_position(), BattleTuning.MISSILE_QUERY_RADIUS)
                        if is_projectile(obj)
                        and obj.type == AttackType.MISSILE
                        and obj.is_alive
                        and obj.team_id != self.ship.get_team_id()
                        and obj != exclude]
            enemies.extend(missiles)

        return enemies

    def _build_capabilities_cache(self, ships: List[Any]) -> Dict[str, Dict[str, Any]]:
        """Pre-compute expensive capability checks for all ships.

        PERF: Builds capability data once per ship instead of repeatedly during
        rule evaluation. This converts O(n*m) component lookups (n targets, m rules)
        to O(n) lookups.

        Args:
            ships: List of ships to cache capabilities for

        Returns:
            Dict mapping ship.id to capability data:
            {
                ship_id: {
                    'has_weapons': bool,
                    'weapon_components': List[Component],
                    'has_pdc': bool,
                    'pdc_components': List[Component],
                }
            }
        """
        cache = {}
        for ship in ships:
            # Ships have .name; getattr for defensive handling of malformed entities
            ship_id = getattr(ship, 'name', None)  # INTENTIONAL: defensive for cache building
            if ship_id is None:
                continue

            # Get weapon components once
            weapons = ship.get_components_by_ability('WeaponAbility', operational_only=True)

            # Filter for PDC weapons
            pdc_weapons = [w for w in weapons if w.has_ability('PDCAbility')]

            cache[ship_id] = {
                'has_weapons': len(weapons) > 0,
                'weapon_components': weapons,
                'has_pdc': len(pdc_weapons) > 0,
                'pdc_components': pdc_weapons,
            }

        return cache

    def _score_and_sort_enemies(self, enemies: List[Any], rules: List[Dict[str, Any]]) -> List[Any]:
        """Score enemies using targeting rules and return sorted list (highest first).

        Args:
            enemies: List of potential targets
            rules: Targeting rules from strategy policy

        Returns:
            List of enemies sorted by score (highest first), excluding -inf scores

        Note:
            If target evaluation fails for a candidate, the candidate is skipped
            and a warning is logged. This ensures combat continues even if
            individual targets have invalid data.
        """
        scored_enemies = []
        ship_id = get_entity_id(self.ship)

        # PERF: Pre-calculate distances once for all candidates
        # Avoids redundant distance calculations in TargetEvaluator
        ship_pos = self.ship.get_position()
        distance_cache = {}
        for e in enemies:
            try:
                # IGridEntity guarantees .position attribute
                distance_cache[e] = ship_pos.distance_to(e.position)
            except (AttributeError, TypeError):
                pass  # Will fall back to _safe_distance in evaluate()

        # PERF: Pre-compute capability checks once for all candidates
        # Avoids redundant component lookups for has_weapons, pdc_arc rules
        capabilities_cache = self._build_capabilities_cache(enemies)

        for e in enemies:
            try:
                score = TargetEvaluator.evaluate(
                    self.ship, e, rules,
                    distance_cache=distance_cache,
                    ship_capabilities_cache=capabilities_cache
                )
                if score > -float('inf'):
                    scored_enemies.append((score, e))
            except (AttributeError, TypeError) as err:
                logger.warning(
                    "Target evaluation failed for ship=%s target=%s: %s. Skipping target.",
                    ship_id, get_entity_id(e), err
                )

        scored_enemies.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in scored_enemies]

    def find_target(self) -> Optional[Any]:
        """Find target based on strategy's targeting priority."""
        resolved = self.get_resolved_strategy()
        targeting_policy = resolved['targeting']
        rules = targeting_policy.get('rules', [])

        # Check if policy cares about missiles
        include_missiles = any(r.get('type') in ['pdc_arc', 'missiles_in_pdc_arc'] for r in rules)

        enemies = self._find_enemies_in_radius(include_missiles=include_missiles)
        if not enemies:
            return None

        sorted_enemies = self._score_and_sort_enemies(enemies, rules)
        return sorted_enemies[0] if sorted_enemies else None

    def find_secondary_targets(self) -> List[Any]:
        """Find additional targets if ship has multiplex tracking."""
        max_targets = self.ship.get_max_targets()
        if max_targets <= CombatConstants.DEFAULT_MAX_TARGETS:
            return []

        count_needed = max_targets - 1
        current = self.ship.get_current_target()

        resolved = self.get_resolved_strategy()
        targeting_policy = resolved['targeting']
        rules = targeting_policy.get('rules', [])

        # Check if policy cares about missiles
        include_missiles = any(r.get('type') in ['pdc_arc', 'missiles_in_pdc_arc'] for r in rules)

        enemies = self._find_enemies_in_radius(exclude=current, include_missiles=include_missiles)
        if not enemies:
            return []

        sorted_enemies = self._score_and_sort_enemies(enemies, rules)
        return sorted_enemies[:count_needed]

    def update(self) -> None:
        """Execute one AI update cycle: target selection, behavior selection, movement."""
        if not self.ship.is_alive():
            return

        # Throttle Reset
        self.ship.set_turn_throttle(1.0)
        self.ship.set_throttle(AIConfig.FORMATION_ENGINE_THROTTLE if self.ship.get_formation_members() else 1.0)

        # Formation Logic (Inline for now, could be moved to Behavior)
        if self.ship.get_formation_members():
            self._handle_formation_master()

        # Formation Dropout Check
        if self.ship.is_in_formation() and self.ship.get_formation_master():
            self._check_formation_integrity()

        resolved = self.get_resolved_strategy()
        movement_policy = resolved['movement']

        # Formation Targeting Sync
        if self.ship.is_in_formation() and self.ship.get_formation_master():
            master_target = self.ship.get_formation_master().current_target
            if master_target and master_target.is_alive:
                self.ship.set_current_target(master_target)

        # Target Acquisition
        target = self.ship.get_current_target()
        if target and not target.is_alive:
            target = None
            self.ship.set_current_target(None)

        if not target and not (self.ship.is_in_formation() and self.ship.get_formation_master()):
            target = self.find_target()
            self.ship.set_current_target(target)

        # Secondary target acquisition for ships with multiplex tracking
        if self.ship.get_max_targets() > CombatConstants.DEFAULT_MAX_TARGETS:
            self.ship.set_secondary_targets(self.find_secondary_targets())
        else:
            self.ship.set_secondary_targets([])

        # No-target handling: still execute movement-only behaviors
        if not target and not self.ship.is_in_formation():
            self.ship.set_trigger_pulled(False)
            # Check if the behavior can run without a target
            behavior_key = movement_policy.get('behavior', 'kite')
            if behavior_key not in _NO_TARGET_BEHAVIORS:
                return
        else:
            self.ship.set_trigger_pulled(True)

        # Satellite Exception
        if self.ship.get_vehicle_type() == 'Satellite':
            return

        # Determine Behavior
        if self.ship.is_in_formation() and self.ship.get_formation_master():
            behavior_key = 'formation'
        else:
            # Policy-driven behavior selection
            hp_pct = get_hp_percent(self.ship)
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
            # Only run behavior if target exists OR behavior doesn't need one
            if target or behavior_key in _NO_TARGET_BEHAVIORS:
                self.current_behavior.update(target, behavior_context)

    def _handle_formation_master(self):
        """Limit turn/throttle when leading a formation to keep members together."""
        diam = self.ship.get_radius() * 2
        max_radius = 0
        # formation_members contains raw Ships, not adapters
        for member in self.ship.get_formation_members():
            if member.formation.offset:
                r = member.formation.offset.length()
                if r > max_radius:
                    max_radius = r

        if max_radius > 0:
            max_speed = self.ship.get_max_speed()
            max_w_rad = max_speed / max_radius
            max_w_deg = math.degrees(max_w_rad)
            base_turn = self.ship.get_turn_speed() / 100.0
            if base_turn > 0:
                turn_limit = max_w_deg / base_turn
                # Turn throttle was just set to 1.0 at start of update()
                self.ship.set_turn_throttle(min(1.0, turn_limit))

        slow_down = False
        # formation_members contains raw Ships, not adapters
        for member in self.ship.get_formation_members():
            if not member.is_alive or not member.formation.active:
                continue
            rotated_offset = member.formation.offset.rotate(self.ship.get_rotation())
            target_pos = self.ship.get_position() + rotated_offset
            d = member.position.distance_to(target_pos)
            if d > 0.5 * diam:
                slow_down = True
                break

        if slow_down:
            self.ship.set_throttle(AIConfig.FORMATION_SLOWDOWN_THROTTLE)
            # Turn throttle may have been limited by turn_limit above
            self.ship.set_turn_throttle(AIConfig.FORMATION_SLOWDOWN_THROTTLE)

    def _check_formation_integrity(self):
        # Check if propulsion components are damaged
        dmg = False
        propulsion_comps = (
            self.ship.get_components_by_ability('CombatPropulsion', operational_only=False) +
            self.ship.get_components_by_ability('ManeuveringThruster', operational_only=False)
        )
        for comp in propulsion_comps:
            # Component always has current_hp and max_hp attributes
            if comp.current_hp < comp.max_hp:
                dmg = True
                break

        if dmg:
            self.ship.set_in_formation(False)
            self.ship.leave_formation()
            self.ship.set_formation_master(None)
            self.ship.set_turn_throttle(1.0)
            self.ship.set_throttle(1.0)

    def check_avoidance(self):
        """Check for nearby collisions."""
        nearby = self.grid.query_radius(self.ship.get_position(), BattleTuning.AVOIDANCE_RADIUS)
        closest = None
        min_d = float('inf')

        for obj in nearby:
            # Skip self: self.ship may be ShipControllableAdapter wrapping the raw ship
            # Grid contains raw Ship objects, so compare via .ship property if adapter
            own_ship = self.ship.ship if isinstance(self.ship, ShipControllableAdapter) else self.ship
            if obj == own_ship:
                continue
            if not obj.is_alive:
                continue
            if not is_combatant(obj):
                continue

            d = self.ship.get_position().distance_to(obj.position)
            # IGridEntity guarantees .radius attribute
            thresh = self.ship.get_radius() + obj.radius + BattleTuning.COLLISION_BUFFER

            if d < thresh:
                if d < min_d:
                    min_d = d
                    closest = obj

        if closest:
            vec = self.ship.get_position() - closest.position
            if vec.length() == 0:
                vec = Vector2(1, 0)
            return self.ship.get_position() + vec.normalize() * BattleTuning.AVOIDANCE_TARGET_DISTANCE
        return None

    def navigate_to(self, target_pos, stop_dist: float = 0) -> None:
        """Navigate ship toward target position using rotation and thrust."""
        ship_pos = self.ship.get_position()
        distance = ship_pos.distance_to(target_pos)
        dx = target_pos.x - ship_pos.x
        dy = target_pos.y - ship_pos.y
        target_angle = angle_from_vector(dx, dy)
        current_angle = self.ship.get_rotation() % 360
        ang_diff = angle_diff(current_angle, target_angle)

        if abs(ang_diff) > AIConfig.NAVIGATION_ROTATION_DEADBAND:
            direction = 1 if ang_diff > 0 else -1
            self.ship.rotate(direction)

        eff_stop_dist = stop_dist
        if abs(ang_diff) < AIConfig.NAVIGATION_THRUST_ANGLE_MAX and distance > eff_stop_dist:
            self.ship.thrust_forward()
