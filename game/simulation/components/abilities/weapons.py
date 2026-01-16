import math
from typing import Dict, Any

from game.core.logger import log_debug
from game.core.config import PhysicsConfig
from .base import Ability


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
            if not raw_damage:
                raw_damage = self.component.data.get('base_damage', 0)

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
            if not raw_range:
                raw_range = self.component.data.get('base_range', 0)

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
            if not raw_reload:
                raw_reload = self.component.data.get('base_reload', 1.0)

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
            # Consume resources via Component (Bridge to ResourceRegistry)
            if self.component:
                self.component.consume_activation()

            self.cooldown_timer = self.reload_time
            return True
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
            {'label': 'Damage', 'value': f"{self.damage:.0f}", 'color_hint': '#FF6464'},  # Red
            {'label': 'Range', 'value': f"{self.range:.0f}", 'color_hint': '#FFA500'},  # Orange
            {'label': 'Reload', 'value': f"{self.reload_time:.1f}s", 'color_hint': '#FFC864'}  # Gold
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

        log_debug(f"check_firing_solution Arc FAIL: diff {abs(diff)} > {self.firing_arc / 2}")
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
        rows.append({'label': 'Speed', 'value': f"{self.projectile_speed:.0f}", 'color_hint': '#C8C832'})  # Yellow-ish
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
        rows.append({'label': 'Accuracy', 'value': f"{int(self.base_accuracy * 100)}%", 'color_hint': '#FFFF00'})
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
