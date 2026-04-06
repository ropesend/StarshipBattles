import logging
import math
from typing import Dict, Any, List

from game.core.config import PhysicsConfig
from game.core.math import angle_from_vector
from game.simulation.formula_system import FormulaEvaluator

logger = logging.getLogger(__name__)
from .base import Ability
from .stat_keys import StatKey, AbilityStatBinding
from .ui_colors import HINT_DAMAGE, HINT_RANGE, HINT_RELOAD, HINT_PROJECTILE_SPEED, HINT_ACCURACY


def _parse_formula_field(raw, default: float = 0.0, formula_context: dict = None) -> tuple:
    """Parse a field that may be a number or a formula string.

    PROJ-225: Extracted from duplicated logic in WeaponAbility.__init__ and sync_data.

    Args:
        raw: Raw value (number, formula string starting with '=', or None)
        default: Default value if raw is falsy (not including numeric 0)
        formula_context: Variables for formula evaluation (default: empty dict)

    Returns:
        Tuple of (parsed_value: float, formula_string_or_none)
    """
    if formula_context is None:
        formula_context = {}

    if isinstance(raw, str) and raw.startswith('='):
        formula_str = raw[1:]
        value = float(max(0, FormulaEvaluator.evaluate(formula_str, formula_context)))
        return value, formula_str
    elif raw is not None:
        return float(raw), None
    else:
        return float(default), None


class WeaponAbility(Ability):
    """Base class for all offensive weapon capabilities.

    Formula System:
        Damage, range, and reload values can be specified as either:
        - Static numbers: damage=100
        - Runtime formulas: damage="=10 + range_to_target * 0.5"

        Formulas start with '=' and are evaluated at runtime using FormulaEvaluator.safe_evaluate().
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

    def _get_raw_field(self, data, key: str, default, fallback_key: str = None):
        """Get a raw field value from data dict or component fallback.

        Args:
            data: Ability data (dict or primitive)
            key: Primary key to look up
            default: Default value if not found
            fallback_key: Optional fallback key in component.data (e.g. 'base_damage')
        """
        if isinstance(data, dict):
            return data.get(key, default)
        raw = self.component.data.get(key, default)
        if not raw and fallback_key:
            raw = self.component.data.get(fallback_key, default)
        return raw

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        # Parse damage (may be number or formula string)
        raw_damage = self._get_raw_field(data, 'damage', 0, 'base_damage')
        self.damage, self.damage_formula = _parse_formula_field(
            raw_damage, default=0.0, formula_context={'range_to_target': 0}
        )
        self._base_damage = self.damage

        # Parse range (may be number or formula string)
        raw_range = self._get_raw_field(data, 'range', 0, 'base_range')
        self.range, _ = _parse_formula_field(raw_range, default=0.0)
        self._base_range = self.range

        # Parse reload (may be number or formula string)
        raw_reload = self._get_raw_field(data, 'reload', 1.0, 'base_reload')
        self.reload_time, _ = _parse_formula_field(raw_reload, default=1.0)
        self._base_reload = self.reload_time

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
        # PROJ-225: Use shared _parse_formula_field for all three fields.
        # PROJ-246: Provide default formula context so range_to_target formulas
        # don't crash during data loading (same context as __init__).
        default_ctx = {'range_to_target': 0}
        if 'damage' in data:
            self._base_damage, _ = _parse_formula_field(
                data['damage'], formula_context=default_ctx
            )
            self.damage = self._base_damage
        if 'range' in data:
            self._base_range, _ = _parse_formula_field(
                data['range'], formula_context=default_ctx
            )
            self.range = self._base_range
        if 'reload' in data:
            self._base_reload, _ = _parse_formula_field(
                data['reload'], default=1.0, formula_context=default_ctx
            )
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
        # IComponent.stats is guaranteed to exist by the protocol
        properties = self.component.stats.get('properties', {})
        if 'facing_angle' in properties:
            # Check if component-level facing_angle was set (overrides properties)
            if getattr(self.component, 'facing_angle', None) is None:
                self.facing_angle = properties['facing_angle']

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
            context = {'range_to_target': range_to_target}
            return max(0.0, FormulaEvaluator.safe_evaluate(self.damage_formula, context))
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
        aim_angle = angle_from_vector(aim_vec.x, aim_vec.y)

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
