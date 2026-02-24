"""
WeaponsViewModel - MVVM ViewModel for Weapons Report Panel.

Owns all weapon data and calculations. No Pygame dependencies.
Emits events via EventBus when state changes.

PROJ-172: Extracted from WeaponsReportPanel for better separation of concerns.
"""
from __future__ import annotations

import math
import logging
from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from game.ui.screens.builder.event_bus import EventBus

logger = logging.getLogger(__name__)


class WeaponsEvents:
    """Event constants for WeaponsViewModel."""

    WEAPONS_UPDATED = 'weapons_updated'
    FILTER_CHANGED = 'filter_changed'
    TARGET_CHANGED = 'target_changed'
    HOVER_CHANGED = 'hover_changed'


class WeaponsViewModel:
    """
    ViewModel for Weapons Report Panel.

    Owns all mutable state related to weapons display:
    - Weapon grouping and filtering
    - Target ship and defense modifier
    - Threshold range calculations
    - Points of interest computation
    - Hover state

    Emits events when state changes, views subscribe to update UI.
    """

    # === Calculation Constants ===
    THRESHOLDS = [0.99, 0.90, 0.80, 0.70, 0.60, 0.50, 0.40, 0.30, 0.20, 0.10, 0.01]
    INTEREST_POINTS_RANGE = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    INTEREST_POINTS_ACCURACY = [0.99, 0.80, 0.60, 0.40, 0.20, 0.01]

    def __init__(self, event_bus: EventBus):
        """
        Initialize the ViewModel.

        Args:
            event_bus: EventBus for emitting state change notifications
        """
        self.event_bus = event_bus

        # Filter state
        self._filter_states = {
            'projectile': True,
            'beam': True,
            'seeker': True
        }

        # Target state
        self._target_name: Optional[str] = None
        self._target_defense_mod: float = 0.0

        # Weapon data cache
        self._weapon_groups: List[Dict[str, Any]] = []
        self._max_range: int = 0

        # Hover state
        self._hovered_weapon = None

        # Verbose tooltip mode
        self.verbose_tooltip: bool = False

    # ─────────────────────────────────────────────────────────────────
    # Properties
    # ─────────────────────────────────────────────────────────────────

    @property
    def filter_states(self) -> Dict[str, bool]:
        """Current filter states for weapon types."""
        return self._filter_states

    @property
    def target_name(self) -> Optional[str]:
        """Name of the target ship (for display)."""
        return self._target_name

    @property
    def target_defense_mod(self) -> float:
        """Defense modifier from target ship."""
        return self._target_defense_mod

    @property
    def weapon_groups(self) -> List[Dict[str, Any]]:
        """Grouped weapon data: list of {'weapon': Component, 'count': int}."""
        return self._weapon_groups

    @property
    def max_range(self) -> int:
        """Maximum range across all currently loaded weapons."""
        return self._max_range

    @property
    def hovered_weapon(self):
        """Currently hovered weapon (for firing arc display)."""
        return self._hovered_weapon

    # ─────────────────────────────────────────────────────────────────
    # Filter Management
    # ─────────────────────────────────────────────────────────────────

    def toggle_filter(self, filter_type: str) -> None:
        """
        Toggle a weapon type filter.

        Args:
            filter_type: One of 'projectile', 'beam', 'seeker'
        """
        if filter_type in self._filter_states:
            self._filter_states[filter_type] = not self._filter_states[filter_type]
            self.event_bus.emit(WeaponsEvents.FILTER_CHANGED, self._filter_states.copy())

    def enable_all_filters(self) -> None:
        """Enable all weapon type filters."""
        self._filter_states['projectile'] = True
        self._filter_states['beam'] = True
        self._filter_states['seeker'] = True
        self.event_bus.emit(WeaponsEvents.FILTER_CHANGED, self._filter_states.copy())

    # ─────────────────────────────────────────────────────────────────
    # Target Management
    # ─────────────────────────────────────────────────────────────────

    def set_target(self, ship) -> None:
        """
        Set a target ship for accuracy calculations.

        Args:
            ship: Target ship with name and total_defense_score attributes
        """
        self._target_name = ship.name
        self._target_defense_mod = getattr(ship, 'total_defense_score', 0.0)
        self.event_bus.emit(WeaponsEvents.TARGET_CHANGED, {
            'name': self._target_name,
            'defense_mod': self._target_defense_mod
        })

    def clear_target(self) -> None:
        """Reset target to default parameters."""
        self._target_name = None
        self._target_defense_mod = 0.0
        self.event_bus.emit(WeaponsEvents.TARGET_CHANGED, None)

    # ─────────────────────────────────────────────────────────────────
    # Hover State
    # ─────────────────────────────────────────────────────────────────

    def set_hovered_weapon(self, weapon) -> None:
        """
        Set the currently hovered weapon.

        Args:
            weapon: Weapon component or None
        """
        self._hovered_weapon = weapon
        self.event_bus.emit(WeaponsEvents.HOVER_CHANGED, weapon)

    # ─────────────────────────────────────────────────────────────────
    # Weapon Loading
    # ─────────────────────────────────────────────────────────────────

    def load_weapons(self, ship) -> None:
        """
        Load and process weapons from a ship.

        Extracts all weapon components, applies filters, groups identical
        weapons, and calculates max range.

        Args:
            ship: Ship entity with layers containing weapon components
        """
        raw_weapons = self._get_all_weapons(ship)
        self._weapon_groups = self.group_weapons(raw_weapons)

        # Calculate max range
        self._max_range = 0
        for item in self._weapon_groups:
            weapon = item['weapon']
            ab = weapon.get_ability('WeaponAbility')
            weapon_range = ab.range if ab else 0
            if weapon_range > self._max_range:
                self._max_range = weapon_range

        self.event_bus.emit(WeaponsEvents.WEAPONS_UPDATED, {
            'groups': self._weapon_groups,
            'max_range': self._max_range
        })

    def _get_all_weapons(self, ship) -> List:
        """
        Get list of all weapon components from ship, filtered by type.

        Args:
            ship: Ship entity with layers

        Returns:
            List of weapon components matching current filters
        """
        weapons = []
        for layer_data in ship.layers.values():
            for comp in layer_data.components:
                if comp.has_ability('WeaponAbility'):
                    # Apply type filters
                    if comp.has_ability('ProjectileWeaponAbility') and not self._filter_states['projectile']:
                        continue
                    if comp.has_ability('BeamWeaponAbility') and not self._filter_states['beam']:
                        continue
                    if comp.has_ability('SeekerWeaponAbility') and not self._filter_states['seeker']:
                        continue
                    weapons.append(comp)
        return weapons

    # ─────────────────────────────────────────────────────────────────
    # Weapon Grouping
    # ─────────────────────────────────────────────────────────────────

    def group_weapons(self, weapons: List) -> List[Dict[str, Any]]:
        """
        Group identical weapons into stacks.

        Weapons are considered identical if they have the same:
        - Component ID
        - Modifiers (sorted)
        - Facing angle
        - Firing arc

        Args:
            weapons: List of weapon components

        Returns:
            List of {'weapon': Component, 'count': int} dicts, sorted by name
        """
        def get_key(w):
            ab = w.get_ability('WeaponAbility')
            if not ab:
                return (w.id, (), 0, 0)

            mods = []
            for m in w.modifiers:
                mods.append((m.definition.id, m.value))
            mods.sort()
            return (w.id, tuple(mods), ab.facing_angle, ab.firing_arc)

        stacks: Dict[Any, Dict[str, Any]] = {}

        for w in weapons:
            k = get_key(w)
            if k in stacks:
                stacks[k]['count'] += 1
            else:
                stacks[k] = {'weapon': w, 'count': 1}

        # Sort by weapon name
        sorted_stacks = sorted(stacks.values(), key=lambda x: x['weapon'].name)
        return sorted_stacks

    # ─────────────────────────────────────────────────────────────────
    # Threshold Calculation
    # ─────────────────────────────────────────────────────────────────

    def calculate_threshold_ranges(self, weapon, ship) -> List[Tuple[float, Optional[float], int]]:
        """
        Calculate the range at which each hit probability threshold is reached.

        Uses sigmoid math: P = 1 / (1 + exp(-x))
        where x = (Base + Attack) - (Range * Falloff + Defense)

        Args:
            weapon: Weapon component
            ship: Attacking ship (for sensor score)

        Returns:
            List of tuples: (threshold, range_value, damage)
            range_value may be None if threshold is unreachable
        """
        results = []

        ab = weapon.get_ability('WeaponAbility')
        if not ab:
            return []

        base_acc = getattr(ab, 'base_accuracy', 2.0)
        falloff = getattr(ab, 'accuracy_falloff', 0.001)
        max_range = ab.range
        damage = ab.damage

        # Ship sensor score
        attack_score = 0.0
        if hasattr(ship, 'get_total_sensor_score'):
            attack_score = ship.get_total_sensor_score()

        defense_score = self._target_defense_mod
        net_starting_score = (base_acc + attack_score) - defense_score

        for threshold in self.THRESHOLDS:
            p = max(0.0001, min(0.9999, threshold))
            logit_p = math.log(p / (1.0 - p))

            if falloff > 0:
                r = (net_starting_score - logit_p) / falloff

                # Clamp logic
                if r < 0:
                    score_at_0 = net_starting_score
                    p_at_0 = 1.0 / (1.0 + math.exp(-score_at_0))
                    if p_at_0 > p:
                        range_for_threshold = None
                    else:
                        range_for_threshold = None
                elif r > max_range:
                    score_at_max = net_starting_score - max_range * falloff
                    if score_at_max > logit_p:
                        range_for_threshold = max_range
                    else:
                        range_for_threshold = max_range
                else:
                    range_for_threshold = r
            else:
                # No falloff - constant accuracy
                if net_starting_score >= logit_p:
                    range_for_threshold = max_range
                else:
                    range_for_threshold = None

            results.append((threshold, range_for_threshold, damage))

        return results

    # ─────────────────────────────────────────────────────────────────
    # Points of Interest
    # ─────────────────────────────────────────────────────────────────

    def get_points_of_interest(self, weapon, ship) -> List[Dict[str, Any]]:
        """
        Generate unified points of interest for weapon bar visualization.

        Returns a sorted list of dicts with:
        - 'range': distance value in game units
        - 'damage': damage at that range
        - 'accuracy': hit chance at that range (beam only, None for others)
        - 'type': 'range' (percentage breakpoint) or 'accuracy' (threshold crossing)
        - 'priority': 0 = must show (endpoints), 1 = important, 2 = nice to have

        Args:
            weapon: Weapon component
            ship: Attacking ship (for sensor score)

        Returns:
            List of point dicts sorted by range
        """
        points = []

        ab = weapon.get_ability('WeaponAbility')
        if not ab:
            return points

        weapon_range = ab.range
        base_damage = ab.damage

        is_beam = weapon.has_ability('BeamWeaponAbility')

        # Accuracy parameters for beam weapons
        base_acc = getattr(ab, 'base_accuracy', 2.0) if is_beam else None
        falloff = getattr(ab, 'accuracy_falloff', 0.001) if is_beam else None

        # Ship sensor score
        attack_score = 0.0
        if hasattr(ship, 'get_total_sensor_score'):
            attack_score = ship.get_total_sensor_score()
        defense_score = self._target_defense_mod

        def calc_accuracy_at_range(r):
            if not is_beam or base_acc is None or falloff is None:
                return None
            range_penalty = falloff * r
            net_score = (base_acc + attack_score) - (range_penalty + defense_score)
            clamped = max(-20.0, min(20.0, net_score))
            return 1.0 / (1.0 + math.exp(-clamped))

        def calc_damage_at_range(r):
            if hasattr(ab, 'get_damage'):
                return ab.get_damage(r)
            return base_damage

        # 1. Add range percentage breakpoints
        for pct in self.INTEREST_POINTS_RANGE:
            r = int(weapon_range * pct)
            dmg = calc_damage_at_range(r)
            acc = calc_accuracy_at_range(r)

            priority = 0 if pct in [0.0, 1.0] else 2

            points.append({
                'range': r,
                'damage': dmg,
                'accuracy': acc,
                'type': 'range',
                'priority': priority,
                'label_pct': pct
            })

        # 2. For beam weapons, add accuracy threshold crossings
        if is_beam and falloff and falloff > 0:
            net_starting_score = (base_acc + attack_score) - defense_score

            for threshold in self.INTEREST_POINTS_ACCURACY:
                p = max(0.0001, min(0.9999, threshold))
                logit_p = math.log(p / (1.0 - p))

                r = (net_starting_score - logit_p) / falloff

                if 0 < r < weapon_range:
                    too_close = any(abs(pt['range'] - r) < weapon_range * 0.05 for pt in points)
                    if not too_close:
                        dmg = calc_damage_at_range(r)
                        points.append({
                            'range': int(r),
                            'damage': dmg,
                            'accuracy': threshold,
                            'type': 'accuracy',
                            'priority': 1,
                            'label_acc': threshold
                        })

        # Sort by range
        points.sort(key=lambda p: p['range'])
        return points

    # ─────────────────────────────────────────────────────────────────
    # Tooltip Calculation
    # ─────────────────────────────────────────────────────────────────

    def calculate_tooltip_data(self, weapon, ship, hover_range: float) -> Optional[Dict[str, Any]]:
        """
        Calculate tooltip data for a specific range on a weapon bar.

        Args:
            weapon: Weapon component
            ship: Attacking ship
            hover_range: Range value at cursor position

        Returns:
            Dict with range, accuracy, damage, and optional verbose info
        """
        ab = weapon.get_ability('WeaponAbility')
        if not ab:
            return None

        weapon_range = ab.range
        hover_range = max(0, min(hover_range, weapon_range))

        damage = ab.damage

        if weapon.has_ability('BeamWeaponAbility'):
            base_acc = getattr(ab, 'base_accuracy', 1.0)
            falloff = getattr(ab, 'accuracy_falloff', 0.0)

            attack_score = 0.0
            if hasattr(ship, 'get_total_sensor_score'):
                attack_score = ship.get_total_sensor_score()

            defense_score = self._target_defense_mod
            range_penalty = hover_range * falloff
            net_score = (base_acc + attack_score) - (range_penalty + defense_score)

            clamped = max(-20.0, min(20.0, net_score))
            hit_chance = 1.0 / (1.0 + math.exp(-clamped))

            acc_text = f"{int(hit_chance * 100)}%"
            verbose_info = {
                'base_acc': base_acc,
                'attack_score': attack_score,
                'defense_score': defense_score,
                'range_penalty': range_penalty,
                'net_score': net_score
            }
        else:
            acc_text = "N/A"
            verbose_info = None

        return {
            'range': int(hover_range),
            'accuracy': acc_text,
            'damage': int(damage),
            'verbose': verbose_info
        }
