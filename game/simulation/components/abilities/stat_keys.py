"""
Stat Keys and Ability Bindings for the modifier-ability system.

This module provides:
- StatKey: Enumeration of all stat keys used in the modifier system
- AbilityStatBinding: Declares how a stat key maps to an ability attribute

These are the explicit contracts between modifiers and abilities.
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Set

from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode


class StatKey(Enum):
    """
    Explicit enumeration of all stat keys in the modifier system.

    Each key corresponds to a multiplier or additive value that modifiers
    can produce and abilities can consume.

    Usage:
        # In modifier evaluation
        stats[StatKey.DAMAGE_MULT.value] *= 1.5

        # In ability recalculation
        damage = base_damage * component.stats.get(StatKey.DAMAGE_MULT.value, 1.0)
    """

    # Multiplicative stats (default 1.0)
    MASS_MULT = "mass_mult"
    HP_MULT = "hp_mult"
    DAMAGE_MULT = "damage_mult"
    RANGE_MULT = "range_mult"
    COST_MULT = "cost_mult"
    THRUST_MULT = "thrust_mult"
    TURN_MULT = "turn_mult"
    STRATEGIC_MULT = "strategic_mult"
    ENERGY_GEN_MULT = "energy_gen_mult"
    CAPACITY_MULT = "capacity_mult"
    CREW_CAPACITY_MULT = "crew_capacity_mult"
    LIFE_SUPPORT_CAPACITY_MULT = "life_support_capacity_mult"
    CONSUMPTION_MULT = "consumption_mult"
    RELOAD_MULT = "reload_mult"
    ENDURANCE_MULT = "endurance_mult"
    PROJECTILE_HP_MULT = "projectile_hp_mult"
    PROJECTILE_DAMAGE_MULT = "projectile_damage_mult"
    CREW_REQ_MULT = "crew_req_mult"

    # Additive stats (default 0.0)
    MASS_ADD = "mass_add"
    ARC_ADD = "arc_add"
    ACCURACY_ADD = "accuracy_add"
    PROJECTILE_STEALTH_LEVEL = "projectile_stealth_level"

    # Set/Override stats (default None)
    ARC_SET = "arc_set"

    @classmethod
    def get_default(cls, stat_key: 'StatKey') -> float:
        """
        Get the default value for a stat key.

        Multiplicative stats default to 1.0.
        Additive stats default to 0.0.
        Set stats default to None.
        """
        additive_stats = {
            cls.MASS_ADD,
            cls.ARC_ADD,
            cls.ACCURACY_ADD,
            cls.PROJECTILE_STEALTH_LEVEL,
        }
        set_stats = {
            cls.ARC_SET,
        }

        if stat_key in additive_stats:
            return 0.0
        elif stat_key in set_stats:
            return None
        else:
            return 1.0

    @classmethod
    def create_default_stats_dict(cls) -> dict:
        """
        Create a stats dictionary with all keys set to their defaults.

        This mirrors the stats dict in Component._calculate_modifier_stats().
        """
        stats = {}
        for key in cls:
            stats[key.value] = cls.get_default(key)
        # Special case: properties dict
        stats['properties'] = {}
        return stats


@dataclass
class AbilityStatBinding:
    """
    Declares how a stat key maps to an ability attribute.

    This is the explicit contract between modifiers and abilities.
    Each binding specifies:
    - Which stat key to read from component.stats
    - Which ability attribute to modify
    - What operation to apply (multiply, add, set)
    - What base attribute to use for calculations

    Example:
        # Weapon damage binding
        AbilityStatBinding(
            stat_key=StatKey.DAMAGE_MULT,
            attribute_name='damage',
            operation='multiply',
            base_attribute='_base_damage'  # Computed from default if None
        )
    """
    stat_key: StatKey
    attribute_name: str
    operation: str = "multiply"  # "multiply", "add", "set"
    base_attribute: Optional[str] = None  # Defaults to f"_base_{attribute_name}"

    def __post_init__(self):
        """Validate the binding configuration."""
        valid_operations = {'multiply', 'add', 'set'}
        if self.operation not in valid_operations:
            raise ValidationException(
                f"Invalid stat binding operation: '{self.operation}'",
                code=ErrorCode.VALIDATION_FAILED.value,
                context={
                    "operation": self.operation,
                    "valid_operations": list(valid_operations)
                }
            )

    def get_base_attribute_name(self) -> str:
        """Get the base attribute name (for recalculation)."""
        if self.base_attribute:
            return self.base_attribute
        return f"_base_{self.attribute_name}"

    def apply(self, ability, stats: dict) -> bool:
        """
        Apply this binding to an ability using the given stats dict.

        Args:
            ability: The ability instance to modify
            stats: The stats dictionary from component.stats

        Returns:
            True if the binding was applied, False if skipped (stat not present or no base value)
        """
        stat_value = stats.get(self.stat_key.value)
        if stat_value is None:
            return False

        base_attr = self.get_base_attribute_name()
        base_value = getattr(ability, base_attr, None)
        if base_value is None:
            return False

        if self.operation == "multiply":
            new_value = base_value * stat_value
        elif self.operation == "add":
            new_value = base_value + stat_value
        elif self.operation == "set":
            new_value = stat_value
        else:
            return False

        setattr(ability, self.attribute_name, new_value)
        return True

    def describe(self) -> str:
        """Return a human-readable description of this binding."""
        op_desc = {
            'multiply': 'multiplied by',
            'add': 'increased by',
            'set': 'set to',
        }
        return f"{self.attribute_name} is {op_desc[self.operation]} {self.stat_key.value}"
