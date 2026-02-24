import logging
import math
from typing import Dict, Any, List

from game.core.config import PhysicsConfig

logger = logging.getLogger(__name__)
from .base import Ability
from .stat_keys import StatKey, AbilityStatBinding
from .ui_colors import HINT_DAMAGE, HINT_RANGE, HINT_RELOAD, HINT_PROJECTILE_SPEED, HINT_ACCURACY


class WeaponAbility(Ability):
    """Base class for all offensive weapon capabilities.

    Formula System:
        Damage, range, and reload values can be specified as either:
        - Static numbers: damage=100
        - Runtime formulas: damage="=10 + range_to_target * 0.5"

        Formulas start with '=' and are evaluated at runtime using safe_evaluate_math_formula().
        Available context variables:
        - range_to_target (float): Distance to the target in game units

        Example usage in component JSON:
            "abilities": {
                "ProjectileWeaponAbility": {
                    "damage": "=50 + range_to_target * 0.1",
                    "range": 5000,
                    "reload": 2.0
                }
            }

    Stat Bindings (modifiers applied via STAT_BINDINGS):
        - DAMAGE_MULT: Multiplies base damage
        - RANGE_MULT: Multiplies base range
        - RELOAD_MULT: Multiplies base reload time
        - ARC_SET: Overrides firing arc to fixed value
        - ARC_ADD: Adds to base firing arc
    """

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.DAMAGE_MULT, 'damage', 'multiply', '_base_damage'),
        AbilityStatBinding(StatKey.RANGE_MULT, 'range', 'multiply', '_base_range'),
        AbilityStatBinding(StatKey.RELOAD_MULT, 'reload_time', 'multiply', '_base_reload'),
        AbilityStatBinding(StatKey.ARC_SET, 'firing_arc', 'set'),
        AbilityStatBinding(StatKey.ARC_ADD, 'firing_arc', 'add', '_base_firing_arc'),
    ]

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        # Handle damage (may be number or formula string)
        if isinstance(data, dict):
            raw_damage = data.get('damage', 0)
        else:
            # Fallback to component base stats if data is not a dict (e.g. shortcut 'true')
            raw_damage = self.component.data.get('damage', 0)
            if not raw_damage:
                raw_damage = self.component.data.get('base_damage', 0)

        if isinstance(raw_damage, str) and raw_damage.startswith('='):
            from game.simulation.formula_system import safe_evaluate_math_formula
            self.damage_formula = raw_damage[1:]  # Store without '='
            # Evaluate at range 0 for base value
            self.damage = float(max(0, safe_evaluate_math_formula(self.damage_formula, {'range_to_target': 0})))
        else:
            self.damage_formula = None
            self.damage = float(raw_damage) if raw_damage else 0.0
        self._base_damage = self.damage  # Store for modifier sync

        # Handle range (may be number or formula string)
        if isinstance(data, dict):
            raw_range = data.get('range', 0)
        else:
            raw_range = self.component.data.get('range', 0)
            if not raw_range:
                raw_range = self.component.data.get('base_range', 0)

        if isinstance(raw_range, str) and raw_range.startswith('='):
            from game.simulation.formula_system import safe_evaluate_math_formula
            self.range = float(max(0, safe_evaluate_math_formula(raw_range[1:], {})))
        else:
            self.range = float(raw_range) if raw_range else 0.0
        self._base_range = self.range  # Store for modifier sync

        # Handle reload (may be number or formula string)
        if isinstance(data, dict):
            raw_reload = data.get('reload', 1.0)
        else:
            raw_reload = self.component.data.get('reload', 1.0)
            if not raw_reload:
                raw_reload = self.component.data.get('base_reload', 1.0)

        if isinstance(raw_reload, str) and raw_reload.startswith('='):
            from game.simulation.formula_system import safe_evaluate_math_formula
            self.reload_time = float(max(0.0, safe_evaluate_math_formula(raw_reload[1:], {})))
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
        if not isinstance(data, dict):
            return

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
                from game.simulation.formula_system import safe_evaluate_math_formula
                self._base_damage = float(max(0, safe_evaluate_math_formula(raw[1:], {})))
            else:
                self._base_damage = float(raw)
            self.damage = self._base_damage
        if 'range' in data:
            raw = data['range']
            if isinstance(raw, str) and raw.startswith('='):
                from game.simulation.formula_system import safe_evaluate_math_formula
                self._base_range = float(max(0, safe_evaluate_math_formula(raw[1:], {})))
            else:
                self._base_range = float(raw)
            self.range = self._base_range
        if 'reload' in data:
            raw = data['reload']
            if isinstance(raw, str) and raw.startswith('='):
                from game.simulation.formula_system import safe_evaluate_math_formula
                self._base_reload = float(max(0.0, safe_evaluate_math_formula(raw[1:], {})))
            else:
                self._base_reload = float(raw)
            self.reload_time = self._base_reload

    def recalculate(self):
        # Apply modifiers to base stats using get_effective_stat for multi-ability support
        self.damage = self._base_damage * self.get_effective_stat('damage_mult', 1.0)
        self.range = self._base_range * self.get_effective_stat('range_mult', 1.0)
        self.reload_time = self._base_reload * self.get_effective_stat('reload_mult', 1.0)

        # Apply Arc Modifiers
        # Check for override first (`arc_set`) then additive (`arc_add`)
        arc_set = self.get_effective_stat('arc_set', None)
        if arc_set is not None:
            self.firing_arc = arc_set
        else:
            self.firing_arc = self._base_firing_arc + self.get_effective_stat('arc_add', 0.0)

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
            # Consume resources via Component (Bridge to ResourceRegistry)
            if self.component:
                self.component.consume_activation()

            self.cooldown_timer = self.reload_time
            return True
        return False

    def get_damage(self, range_to_target: float = 0) -> float:
        """Evaluate damage at a specific range.

        If a damage formula was specified (starting with '='), evaluates the formula
        with range_to_target as context. Otherwise returns the static damage value
        (which may have been modified by DAMAGE_MULT modifiers).

        Args:
            range_to_target: Distance to target in game units (default 0)

        Returns:
            Calculated damage value, minimum 0.0
        """
        if self.damage_formula:
            from game.simulation.formula_system import safe_evaluate_math_formula
            context = {'range_to_target': range_to_target}
            return max(0.0, safe_evaluate_math_formula(self.damage_formula, context))
        return self.damage

    def get_ui_rows(self):
        return [
            {'label': 'Damage', 'value': f"{self.damage:.0f}", 'color_hint': HINT_DAMAGE},
            {'label': 'Range', 'value': f"{self.range:.0f}", 'color_hint': HINT_RANGE},
            {'label': 'Reload', 'value': f"{self.reload_time:.1f}s", 'color_hint': HINT_RELOAD}
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
            logger.debug(f"check_firing_solution Range FAIL: dist {dist} > range {self.range}")
            return False

        # 2. Arc Check
        # Vector to target
        aim_vec = target_pos - ship_pos
        aim_angle = math.degrees(math.atan2(aim_vec.y, aim_vec.x)) % 360

        # Component Global Facing
        comp_facing = (ship_angle + self.facing_angle) % 360

        # Shortest angular difference
        diff = (aim_angle - comp_facing + 180) % 360 - 180

        # Use epsilon (0.01) for boundary floating point stability
        if abs(diff) <= (self.firing_arc / 2) + 0.01:
            return True

        logger.debug(f"check_firing_solution Arc FAIL: diff {abs(diff)} > {self.firing_arc / 2}")
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
        rows.append({'label': 'Speed', 'value': f"{self.projectile_speed:.0f}", 'color_hint': HINT_PROJECTILE_SPEED})
        return rows


class BeamWeaponAbility(WeaponAbility):
    # Extend parent bindings with accuracy
    STAT_BINDINGS: List[AbilityStatBinding] = WeaponAbility.STAT_BINDINGS + [
        AbilityStatBinding(StatKey.ACCURACY_ADD, 'base_accuracy', 'add', '_base_accuracy'),
    ]

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
        self.base_accuracy = self._base_accuracy + self.get_effective_stat('accuracy_add', 0.0)

    def get_ui_rows(self):
        rows = super().get_ui_rows()
        rows.append({'label': 'Accuracy', 'value': f"{int(self.base_accuracy * 100)}%", 'color_hint': HINT_ACCURACY})
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


class SeekerWeaponAbility(WeaponAbility):
    # Extend parent bindings with seeker-specific stats
    STAT_BINDINGS: List[AbilityStatBinding] = WeaponAbility.STAT_BINDINGS + [
        AbilityStatBinding(StatKey.ENDURANCE_MULT, 'endurance', 'multiply', '_base_endurance'),
        AbilityStatBinding(StatKey.PROJECTILE_DAMAGE_MULT, 'projectile_damage', 'multiply', '_base_projectile_damage'),
        AbilityStatBinding(StatKey.PROJECTILE_HP_MULT, 'projectile_hp', 'multiply', '_base_projectile_hp'),
        AbilityStatBinding(StatKey.PROJECTILE_STEALTH_LEVEL, 'projectile_stealth', 'add', '_base_projectile_stealth'),
    ]

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        if isinstance(data, dict):
            self.projectile_speed = float(data.get('projectile_speed', 500))
            self.endurance = float(data.get('endurance', 3.0))
            self.turn_rate = float(data.get('turn_rate', 30.0))
            self.to_hit_defense = float(data.get('to_hit_defense', 0.0))
            # Seeker projectile stats
            self.projectile_damage = float(data.get('projectile_damage', data.get('damage', 0)))
            self.projectile_hp = float(data.get('projectile_hp', 1.0))
            self.projectile_stealth = float(data.get('projectile_stealth', 0.0))
        else:
            self.projectile_speed = float(getattr(self.component, 'projectile_speed', 500))
            self.endurance = float(getattr(self.component, 'endurance', 3.0))
            self.turn_rate = float(getattr(self.component, 'turn_rate', 30.0))
            self.to_hit_defense = float(getattr(self.component, 'to_hit_defense', 0.0))
            self.projectile_damage = float(getattr(self.component, 'projectile_damage', 0))
            self.projectile_hp = float(getattr(self.component, 'projectile_hp', 1.0))
            self.projectile_stealth = float(getattr(self.component, 'projectile_stealth', 0.0))

        # Store base values for modifier recalculation
        self._base_endurance = self.endurance
        self._base_projectile_damage = self.projectile_damage
        self._base_projectile_hp = self.projectile_hp
        self._base_projectile_stealth = self.projectile_stealth

        # Recalculate range based on endurance if basic range not set or derived
        # Seekers use 80% of straight-line range to account for maneuvering
        if self.range <= 0 and self.projectile_speed > 0:
            self.range = int(self.projectile_speed * self.endurance * 0.8)
            self._base_range = self.range

    def recalculate(self):
        super().recalculate()
        # Apply seeker-specific stats using get_effective_stat for multi-ability support
        self.endurance = self._base_endurance * self.get_effective_stat('endurance_mult', 1.0)
        self.projectile_damage = self._base_projectile_damage * self.get_effective_stat('projectile_damage_mult', 1.0)
        self.projectile_hp = self._base_projectile_hp * self.get_effective_stat('projectile_hp_mult', 1.0)
        self.projectile_stealth = self._base_projectile_stealth + self.get_effective_stat('projectile_stealth_level', 0.0)

    def check_firing_solution(self, ship_pos, ship_angle, target_pos) -> bool:
        """Seekers are omni-directional and ignore firing arcs."""
        dist = ship_pos.distance_to(target_pos)
        return dist <= self.range
