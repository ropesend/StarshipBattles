"""Target evaluation for AI decision making.

This module provides the TargetEvaluator class which scores potential targets
based on configurable rules from combat strategies.

Exception Handling
==================
This module uses defensive programming with fallback behavior for robustness
during combat. All errors are logged for debugging, but the system continues
operating when possible:

- Position/rotation access failures: Logged, falls back to direct attribute
- Division by zero: Protected with zero checks
- Missing attributes: Uses safe defaults

For fatal errors that indicate programming bugs, TargetingException is raised.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from game.core.math import Vector2
from game.core.constants import AttackType, LayerType
from game.ai.protocols import is_projectile
from game.simulation.interfaces.entity_protocols import is_combat_ship
from game.ai.combat_utils import (
    get_capability_cache_key,
    get_position,
    get_rotation,
    get_all_components,
    safe_distance,
    get_hp_percent,
    is_in_pdc_arc,
)


class TargetEvaluator:
    """Helper to evaluate targets based on rules."""

    @staticmethod
    def _eval_distance_rule(ship, candidate, rule, distance_cache) -> tuple[float, bool]:
        """Evaluate distance-based rules: nearest, farthest, distance.

        Args:
            ship: The ship doing the targeting
            candidate: The potential target
            rule: The targeting rule dict
            distance_cache: Optional dict mapping candidate to pre-calculated distance

        Returns:
            Tuple of (score_value, match_succeeded)
        """
        r_type = rule.get('type')
        weight = rule.get('weight', 0)
        factor = rule.get('factor', 1)

        # PERF: Use cached distance if available
        if distance_cache and candidate in distance_cache:
            dist = distance_cache[candidate]
        else:
            dist = safe_distance(ship, candidate)

        if r_type == 'nearest':
            # Closer is better (higher score)
            if weight > 0:
                val = -dist * weight
            else:
                val = dist * factor
        elif r_type == 'farthest':
            # Farther is better
            if weight > 0:
                val = dist * weight
            else:
                val = dist * factor
        else:  # 'distance'
            val = dist * factor

        return (val, True)

    @staticmethod
    def _eval_mass_rule(candidate, rule) -> tuple[float, bool]:
        """Evaluate mass/size-based rules: mass, largest, smallest, strongest, weakest.

        Args:
            candidate: The potential target
            rule: The targeting rule dict

        Returns:
            Tuple of (score_value, match_succeeded)
        """
        r_type = rule.get('type')
        weight = rule.get('weight', 0)
        factor = rule.get('factor', 1)
        # PhysicsBody always has .mass attribute
        mass = candidate.mass

        if r_type in ('mass', 'largest', 'strongest'):
            # Larger/stronger is better
            if weight > 0:
                val = mass * weight
            else:
                val = mass * factor
        else:  # 'smallest' or 'weakest'
            # Smaller/weaker is better
            if weight > 0:
                val = -mass * weight
            else:
                val = mass * factor  # factor should be negative

        return (val, True)

    @staticmethod
    def _eval_speed_rule(candidate, rule) -> tuple[float, bool]:
        """Evaluate speed-based rules: fastest, slowest.

        Args:
            candidate: The potential target
            rule: The targeting rule dict

        Returns:
            Tuple of (score_value, match_succeeded)
        """
        r_type = rule.get('type')
        weight = rule.get('weight', 0)
        factor = rule.get('factor', 1)
        # PhysicsBody always has .velocity attribute
        speed = candidate.velocity.length()

        if r_type == 'fastest':
            val = speed * (weight if weight > 0 else factor)
        else:  # 'slowest'
            val = -speed * (weight if weight > 0 else -factor)

        return (val, True)

    @staticmethod
    def _eval_damage_rule(candidate, rule, stat_helpers) -> tuple[float, bool]:
        """Evaluate damage-based rules: most_damaged, least_damaged.

        Args:
            candidate: The potential target
            rule: The targeting rule dict
            stat_helpers: Dict with 'get_hp_percent' function

        Returns:
            Tuple of (score_value, match_succeeded)
        """
        r_type = rule.get('type')
        weight = rule.get('weight', 0)
        factor = rule.get('factor', 1)
        hp_pct = stat_helpers['get_hp_percent'](candidate)

        if r_type == 'most_damaged':
            # Lower HP % is better
            if weight > 0:
                val = -hp_pct * weight * 100
            else:
                val = hp_pct * factor
        else:  # 'least_damaged'
            # Higher HP % is better
            if weight > 0:
                val = hp_pct * weight * 100
            else:
                val = hp_pct * factor

        return (val, True)

    @staticmethod
    def _eval_has_weapons_rule(candidate, rule, ship_capabilities_cache) -> tuple[float, bool]:
        """Evaluate has_weapons rule.

        PROJ-272 Phase 3: projectile candidates (missiles) have no
        components — rule treats them as "no weapons" without crashing
        on the `get_components_by_ability` call. Previously crashed in
        the cache-miss fallback; outer try/except silently dropped the
        missile from scoring.
        """
        weight = rule.get('weight', 0)
        required = rule.get('required', False)

        # PERF: Use cached capability check if available
        candidate_id = get_capability_cache_key(candidate)
        if ship_capabilities_cache and candidate_id in ship_capabilities_cache:
            has_wpns = ship_capabilities_cache[candidate_id]['has_weapons']
        elif is_combat_ship(candidate):
            # Fall back to component lookup — only valid for ship-like entities.
            has_wpns = any(candidate.get_components_by_ability('WeaponAbility', operational_only=False))
        else:
            # Projectile or non-combat-ship entity — no component query possible.
            has_wpns = False

        if has_wpns:
            return (weight if weight > 0 else 1000, True)
        return (0, not required)

    @staticmethod
    def _eval_least_armor_rule(candidate, rule) -> tuple[float, bool]:
        """Evaluate least_armor rule.

        PROJ-272 Phase 3: projectile candidates have no armor layer —
        rule treats them as "zero armor" (score 0) without crashing on
        the `get_components_by_layer` call.
        """
        weight = rule.get('weight', 0)
        factor = rule.get('factor', 1)

        if not is_combat_ship(candidate):
            # Projectiles have no layers/components. Score as zero armor.
            return (0, True)

        armor_comps = candidate.get_components_by_layer(LayerType.ARMOR)
        # BUG FIX: Component has .current_hp, not .hp (getattr(c, 'hp', 0) always returned 0)
        armor_hp = sum(c.current_hp for c in armor_comps)
        val = -armor_hp * (weight if weight > 0 else -factor)
        return (val, True)

    @staticmethod
    def _eval_pdc_arc_rule(ship, candidate, rule, stat_helpers) -> tuple[float, bool]:
        """Evaluate pdc_arc/missiles_in_pdc_arc rule."""
        weight = rule.get('weight', 0)
        required = rule.get('required', False)

        # Use protocol check instead of getattr for type detection
        is_missile = is_projectile(candidate) and candidate.type == AttackType.MISSILE

        if not is_missile:
            # Rule is specific to missiles, target is not a missile - pass through
            return (0, True)

        in_arc = stat_helpers['is_in_pdc_arc'](ship, candidate)
        if in_arc:
            return (weight if weight > 0 else 2000, True)

        # Not in arc
        if required:
            return (0, False)
        # Strong penalty if not required but logic implies we want it
        return (-999999, False)

    @staticmethod
    def _eval_capability_rule(ship, candidate, rule, stat_helpers, ship_capabilities_cache) -> tuple[float, bool]:
        """Evaluate capability-based rules: has_weapons, least_armor, pdc_arc/missiles_in_pdc_arc.

        Args:
            ship: The ship doing the targeting
            candidate: The potential target
            rule: The targeting rule dict
            stat_helpers: Dict with 'is_in_pdc_arc' function
            ship_capabilities_cache: Optional dict for cached capabilities

        Returns:
            Tuple of (score_value, match_succeeded)
        """
        r_type = rule.get('type')

        if r_type == 'has_weapons':
            return TargetEvaluator._eval_has_weapons_rule(
                candidate, rule, ship_capabilities_cache
            )
        elif r_type == 'least_armor':
            return TargetEvaluator._eval_least_armor_rule(candidate, rule)
        else:  # 'pdc_arc' or 'missiles_in_pdc_arc'
            return TargetEvaluator._eval_pdc_arc_rule(ship, candidate, rule, stat_helpers)

    @staticmethod
    def evaluate(
        ship: Any,
        candidate: Any,
        rules: List[Dict[str, Any]],
        stat_helpers: Optional[Dict[str, Any]] = None,
        distance_cache: Optional[Dict[Any, float]] = None,
        ship_capabilities_cache: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> float:
        """Evaluate a candidate target based on targeting rules.

        Args:
            ship: The ship doing the targeting
            candidate: The potential target to evaluate
            rules: List of targeting rules from strategy
            stat_helpers: Optional dict with 'get_hp_percent' and 'is_in_pdc_arc' functions
                         If not provided, uses default implementations
            distance_cache: Optional dict mapping candidate to pre-calculated distance.
                           PERF: Avoids redundant distance calculations across rules.
            ship_capabilities_cache: Optional dict mapping ship.id to pre-computed capabilities.
                           PERF: Avoids redundant component lookups for has_weapons, pdc_arc rules.
                           Structure: {ship_id: {'has_weapons': bool, 'weapon_components': List,
                                                  'has_pdc': bool, 'pdc_components': List}}

        Returns:
            Score for this target (higher is better), or -inf if required rule fails
        """
        score = 0

        # Use provided helpers or defaults from combat_utils
        if stat_helpers is None:
            stat_helpers = {
                'get_hp_percent': get_hp_percent,
                'is_in_pdc_arc': is_in_pdc_arc
            }

        for rule in rules:
            r_type = rule.get('type')
            required = rule.get('required', False)
            val = 0
            match = True

            if r_type in ('nearest', 'farthest', 'distance'):
                val, match = TargetEvaluator._eval_distance_rule(
                    ship, candidate, rule, distance_cache
                )

            elif r_type in ('mass', 'largest', 'smallest', 'strongest', 'weakest'):
                val, match = TargetEvaluator._eval_mass_rule(candidate, rule)

            elif r_type in ('fastest', 'slowest'):
                val, match = TargetEvaluator._eval_speed_rule(candidate, rule)

            elif r_type in ('most_damaged', 'least_damaged'):
                val, match = TargetEvaluator._eval_damage_rule(candidate, rule, stat_helpers)

            elif r_type in ('has_weapons', 'least_armor', 'pdc_arc', 'missiles_in_pdc_arc'):
                val, match = TargetEvaluator._eval_capability_rule(
                    ship, candidate, rule, stat_helpers, ship_capabilities_cache
                )

            if required and not match:
                return -float('inf')

            score += val

        return score
