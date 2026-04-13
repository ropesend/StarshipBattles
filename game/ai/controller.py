"""
AI Controller - Ship Combat AI Decision Making

This module contains AIController, which provides autonomous behavior for
ships during combat. Each ship gets an AIController that selects targets
and chooses movement behaviors.

Behavior Selection Flowchart:
    1. Is ship alive? → No: Return (no action)
    2. Check HP percentage against retreat threshold
       - HP <= threshold → Use 'flee' behavior
    3. Otherwise → Use behavior from movement policy (default: 'kite')

Available Behaviors:
    - kite: Maintain optimal range, close in or back off as needed
    - attack_run: Approach target, fire, retreat, repeat cycle
    - ram: Move directly toward target, no collision avoidance
    - flee: Move away from target (optionally fire while retreating)
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

Policy Resolution:
    Ships have movement_policy and targeting_policy attributes (e.g., 'kite_max', 'standard').
    PolicyManager resolves these to full policy definitions with:
    - targeting: rules for scoring targets
    - movement: behavior, engage_distance, retreat_hp_threshold

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
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.engine.spatial import SpatialGrid
    from game.simulation.interfaces.ai_controller import IControllableShip

logger = logging.getLogger(__name__)

from game.core.math import Vector2, angle_diff, angle_from_vector
from game.core.config import AIConfig, BattleTuning
from game.ai.behaviors import (RamBehavior, FleeBehavior, KiteBehavior, AttackRunBehavior,
                          DoNothingBehavior, StraightLineBehavior,
                          RotateOnlyBehavior, ErraticBehavior, OrbitBehavior, StationaryFireBehavior)
from game.core.constants import AttackType, CombatConstants
from game.core.protocols import is_combatant
from game.ai.protocols import is_projectile, IGridEntity
from game.simulation.interfaces.entity_protocols import is_combat_ship
from game.ai.interfaces.controllable import ShipControllableAdapter
from game.ai.target_evaluator import TargetEvaluator
from game.ai.policy_manager import get_default_policy_manager
from game.ai.combat_utils import (
    get_capability_cache_key,
    get_entity_id,
    get_hp_percent,
    is_in_pdc_arc,
)

# Behaviors that can execute without an enemy target
_NO_TARGET_BEHAVIORS = frozenset({
    'straight_line', 'rotate_only', 'erratic', 'do_nothing', 'stationary_fire'
})

class AIController:
    def __init__(self, ship: 'IControllableShip', grid: 'SpatialGrid', enemy_team_id: int):
        self.ship = ship
        self.grid = grid
        self.enemy_team_id = enemy_team_id

        # Initialize behaviors
        self.behaviors = {
            'ram': RamBehavior(self),
            'flee': FleeBehavior(self),
            'kite': KiteBehavior(self),
            'attack_run': AttackRunBehavior(self),
            # Test-specific behaviors
            'do_nothing': DoNothingBehavior(self),
            'stationary_fire': StationaryFireBehavior(self),
            'straight_line': StraightLineBehavior(self),
            'rotate_only': RotateOnlyBehavior(self),
            'erratic': ErraticBehavior(self),
            'orbit': OrbitBehavior(self)
        }
        self.current_behavior = None

    def get_resolved_policies(self) -> Dict[str, Any]:
        """Get the resolved targeting and movement policies for this ship."""
        pm = get_default_policy_manager()
        return {
            'targeting': pm.get_targeting_policy(self.ship.get_targeting_policy()),
            'movement': pm.get_movement_policy(self.ship.get_movement_policy()),
        }

    def get_engage_distance_multiplier(self, policy) -> float:
        """Helper to get engage distance multiplier from policy."""
        val = policy.get('engage_distance', 'max_range')
        if val == 'max_range':
            return 1.0
        elif val == 'optimal_range':
            return 0.5
        elif val == 'medium_range':
            return 0.6
        elif val == 'short_range':
            return 0.3
        elif val == 'point_blank':
            return 0.1
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
        # PROJ-254: Use exact-distance query to avoid broad-phase false positives
        # PROJ-269 Phase 3 Task 3.4: N-team targeting — every non-self team
        # counts as enemy (no alliances, no target preference). Ignores
        # `self.enemy_team_id` in favor of `obj.team_id != self.ship.get_team_id()`.
        candidates = self.grid.query_radius_exact(self.ship.get_position(), BattleTuning.TARGET_QUERY_RADIUS)
        my_team_id = self.ship.get_team_id()
        enemies = [obj for obj in candidates
                   if obj.is_alive and is_combatant(obj)
                   and obj.team_id != my_team_id
                   and obj != exclude]

        if include_missiles:
            missiles = [obj for obj in self.grid.query_radius_exact(self.ship.get_position(), BattleTuning.MISSILE_QUERY_RADIUS)
                        if is_projectile(obj)
                        and obj.type == AttackType.MISSILE
                        and obj.is_alive
                        and obj.team_id != self.ship.get_team_id()
                        and obj != exclude]
            enemies.extend(missiles)

        return enemies

    def _build_capabilities_cache(self, entities: List[Any]) -> Dict[str, Dict[str, Any]]:
        """Pre-compute expensive capability checks for ship-like entities.

        PERF: Builds capability data once per ship instead of repeatedly during
        rule evaluation. This converts O(n*m) component lookups (n targets, m rules)
        to O(n) lookups.

        Args:
            entities: Heterogeneous list of potential targets. Callers pass a
                mix of ship-like entities (ICombatShip) AND projectile
                instances (IProjectile) — `_find_enemies_in_radius` extends
                the enemy list with missiles when the targeting policy has
                `pdc_arc` rules. Only ICombatShip entities are cached here;
                projectiles have no components to query and are skipped. Their
                absence from the cache is the normal path — `TargetEvaluator`
                per-rule paths (`_eval_pdc_arc_rule`, etc.) handle projectile
                candidates directly via `is_projectile` guards.

        Returns:
            Dict mapping entity id to capability data:
            {
                entity_id: {
                    'has_weapons': bool,
                    'weapon_components': List[Component],
                    'has_pdc': bool,
                    'pdc_components': List[Component],
                }
            }
        """
        cache = {}
        for entity in entities:
            # Only ICombatShip entities carry component queries. Projectiles
            # (missiles) fail this TypeGuard — skip them. See patterns §2
            # Protocol + TypeGuard in docs/02_PATTERNS.md.
            if not is_combat_ship(entity):
                continue

            entity_id = get_capability_cache_key(entity)
            if entity_id is None:
                continue

            # Get weapon components once
            weapons = entity.get_components_by_ability('WeaponAbility', operational_only=True)

            # Filter for PDC weapons
            pdc_weapons = [w for w in weapons if w.has_ability('PDCAbility')]

            cache[entity_id] = {
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
        resolved = self.get_resolved_policies()
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

        resolved = self.get_resolved_policies()
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
        """Execute one AI update cycle.

        Stages:
        1. Target acquisition (primary + secondary)
        2. Behavior selection (retreat threshold)
        3. Behavior execution
        """
        if not self.ship.is_alive():
            return

        self.ship.set_turn_throttle(1.0)
        self.ship.set_throttle(1.0)

        resolved = self.get_resolved_policies()
        movement_policy = resolved['movement']

        target = self._acquire_targets()

        # No-target early exit for behaviors that require a target
        if target is None:
            self.ship.set_trigger_pulled(False)
            behavior_key = movement_policy.get('behavior', 'kite')
            if behavior_key not in _NO_TARGET_BEHAVIORS:
                return
        else:
            self.ship.set_trigger_pulled(True)

        # Satellites don't execute behaviors
        if self.ship.get_vehicle_type() == 'Satellite':
            return

        behavior_key = self._select_behavior(movement_policy)
        self._execute_behavior(behavior_key, target, movement_policy)

    # -- Stage 1: Target acquisition --------------------------------------

    def _acquire_targets(self) -> Optional[Any]:
        """Acquire primary and secondary targets. Returns primary target or None."""
        target = self.ship.get_current_target()
        if target and not target.is_alive:
            target = None
            self.ship.set_current_target(None)

        if not target:
            target = self.find_target()
            self.ship.set_current_target(target)

        # Secondary targets for multiplex tracking
        if self.ship.get_max_targets() > CombatConstants.DEFAULT_MAX_TARGETS:
            self.ship.set_secondary_targets(self.find_secondary_targets())
        else:
            self.ship.set_secondary_targets([])

        return target

    # -- Stage 2: Behavior selection --------------------------------------

    def _select_behavior(self, movement_policy: Dict[str, Any]) -> str:
        """Select behavior key based on HP and policy."""
        hp_pct = get_hp_percent(self.ship)
        retreat_threshold = movement_policy.get('retreat_hp_threshold', 0.1)

        if hp_pct <= retreat_threshold and retreat_threshold > 0:
            return 'flee'

        return movement_policy.get('behavior', 'kite')

    # -- Stage 4: Behavior execution --------------------------------------

    def _execute_behavior(
        self,
        behavior_key: str,
        target: Optional[Any],
        movement_policy: Dict[str, Any],
    ) -> None:
        """Instantiate and tick the selected behavior."""
        behavior = self.behaviors.get(behavior_key)
        if self.current_behavior != behavior:
            if behavior:
                behavior.enter()
            self.current_behavior = behavior

        if self.current_behavior:
            behavior_context = dict(movement_policy)
            if target or behavior_key in _NO_TARGET_BEHAVIORS:
                self.current_behavior.update(target, behavior_context)

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
