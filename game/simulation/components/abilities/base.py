from typing import Dict, Any, List, Set, TYPE_CHECKING
from enum import Enum, Flag, auto

from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode

if TYPE_CHECKING:
    from .stat_keys import StatKey, AbilityStatBinding


class AbilityLayer(Flag):
    """
    Which game layers an ability applies to.

    COMBAT: Real-time tactical combat simulation
    STRATEGIC: Turn-based strategy map
    BOTH: Ability is active in both layers
    """
    COMBAT = auto()
    STRATEGIC = auto()
    BOTH = COMBAT | STRATEGIC


class AbilityScope(Enum):
    """
    What entities an ability affects.

    SELF: Only the owner entity (ship, complex, etc.)
    SECTOR: All entities in the same hex
    ALLIED_SECTOR: Allied entities in the same hex
    SYSTEM: All entities in the star system
    ALLIED_SYSTEM: Allied entities in the star system
    PLANET: Planet-wide effect (for planetary shields, sensors, etc.)
    """
    SELF = "self"
    SECTOR = "sector"
    ALLIED_SECTOR = "allied_sector"
    SYSTEM = "system"
    ALLIED_SYSTEM = "allied_system"
    PLANET = "planet"


class Ability:
    """
    Base class for component abilities.
    Abilities represent functional capabilities (Consumption, Storage, Generation, special effects)
    that are data-driven and attached to Components.

    Layer and Scope:
    - layer: Class-level constant defining which game layer(s) this ability applies to.
             Inherent to the ability type (subclasses override).
    - allowed_scopes: Class-level list of valid scopes for this ability type.
    - default_scope: Class-level default when JSON doesn't specify scope.
    - scope: Instance-level scope read from JSON data, validated against allowed_scopes.

    Stat Bindings (for modifier system):
    - STAT_BINDINGS: Class-level list declaring which stats this ability consumes.
                     Subclasses override to declare their bindings.
    """
    # Class-level defaults (subclasses override)
    layer: AbilityLayer = AbilityLayer.COMBAT
    allowed_scopes: List[AbilityScope] = [AbilityScope.SELF]
    default_scope: AbilityScope = AbilityScope.SELF

    # Stat bindings for modifier system (subclasses override)
    STAT_BINDINGS: List['AbilityStatBinding'] = []

    def __init__(self, component, data: Dict[str, Any]):
        self.component = component
        self.data = data
        self._tags = set(data.get('tags', [])) if isinstance(data, dict) else set()
        self.stack_group = data.get('stack_group') if isinstance(data, dict) else None

        # Parse scope from JSON data
        self.scope = self._parse_scope(data)

    def _parse_scope(self, data: Any) -> AbilityScope:
        """
        Parse and validate scope from JSON data.

        Args:
            data: Raw ability data (dict or primitive)

        Returns:
            AbilityScope value

        Raises:
            ValueError: If requested scope is not in allowed_scopes
        """
        if not isinstance(data, dict):
            return self.default_scope

        scope_str = data.get('scope')
        if scope_str is None:
            return self.default_scope

        # Convert string to enum
        try:
            requested_scope = AbilityScope(scope_str)
        except ValueError as e:
            raise ValidationException(
                f"{self.__class__.__name__} received invalid scope '{scope_str}'",
                code=ErrorCode.VALIDATION_FAILED.value,
                context={
                    "ability_class": self.__class__.__name__,
                    "scope": scope_str,
                    "valid_scopes": [s.value for s in AbilityScope]
                }
            ) from e

        # Validate against allowed scopes
        if requested_scope not in self.allowed_scopes:
            raise ValidationException(
                f"{self.__class__.__name__} does not support scope '{scope_str}'",
                code=ErrorCode.VALIDATION_FAILED.value,
                context={
                    "ability_class": self.__class__.__name__,
                    "scope": scope_str,
                    "allowed_scopes": [s.value for s in self.allowed_scopes]
                }
            )

        return requested_scope

    @staticmethod
    def _parse_primary_value(
        data,
        key: str = 'value',
        default: float = 0.0,
        fallback_keys: tuple = ()
    ) -> float:
        """
        Parse a primary numeric value from ability data.

        Handles three input formats:
        - Primitive numeric (int/float): Returns float(data) directly
        - Dict with key: Returns float(data[key]) or default
        - Other (str, None, etc.): Returns default

        Args:
            data: Raw ability data (dict, int, float, or other)
            key: Dict key to look up (default: 'value')
            default: Fallback value if key missing (default: 0.0)
            fallback_keys: Additional keys to try if primary key not found

        Returns:
            Parsed float value
        """
        if isinstance(data, (int, float)):
            return float(data)
        if isinstance(data, dict):
            if key in data:
                return float(data[key])
            for fallback in fallback_keys:
                if fallback in data:
                    return float(data[fallback])
            return float(default)
        return float(default)

    def applies_to_layer(self, layer: AbilityLayer) -> bool:
        """
        Check if this ability applies to a given game layer.

        Args:
            layer: The layer to check (COMBAT, STRATEGIC, or BOTH)

        Returns:
            True if this ability is active in the given layer
        """
        return bool(self.layer & layer)

    def sync_data(self, data: Any):
        """Update internal state when component data changes."""
        self.data = data
        if isinstance(data, dict):
            self._tags = set(data.get('tags', []))
            self.stack_group = data.get('stack_group')
            # Re-parse scope if data changes
            self.scope = self._parse_scope(data)
        else:
            pass

    @property
    def tags(self):
        return self._tags

    def update(self) -> bool:
        """
        Called every tick (0.01s).
        Used for constant resource consumption or continuous effects.
        Returns True if operational, False if failed (e.g. starvation).
        """
        return True

    def on_activation(self) -> bool:
        """
        Called when component tries to activate (e.g. fire weapon).
        Used for checking activation costs or conditions.
        Returns True if allowed.
        """
        return True

    def recalculate(self) -> None:
        """
        Called when component stats have changed (e.g. modifiers applied).
        Override to update internal values derived from component stats.
        """
        pass

    # Sentinel value to detect when default wasn't explicitly passed
    _NO_DEFAULT = object()

    def get_effective_stat(self, stat_key: str, default=_NO_DEFAULT):
        """
        Get the effective stat value for this ability, checking ability-specific
        stats first, then falling back to global component stats.

        Args:
            stat_key: The stat key to look up (e.g. 'energy_gen_mult')
            default: Default value if not found. If not specified, uses
                     1.0 for '_mult' keys, 0.0 for '_add' keys, None otherwise.

        Returns:
            The effective stat value for this ability instance
        """
        # Determine default based on key naming convention (only if not explicitly provided)
        if default is Ability._NO_DEFAULT:
            if stat_key.endswith('_mult'):
                default = 1.0
            elif stat_key.endswith('_add'):
                default = 0.0
            else:
                default = None  # Return None for unknown keys (like 'arc_set')

        # Check ability-specific stats first (for targeted modifier effects)
        ability_stats = getattr(self.component, 'ability_stats', {})
        class_name = self.__class__.__name__
        if class_name in ability_stats:
            if stat_key in ability_stats[class_name]:
                return ability_stats[class_name][stat_key]

        # Fall back to global component stats
        stats = getattr(self.component, 'stats', {})
        return stats.get(stat_key, default)

    def get_primary_value(self) -> float:
        """
        Return the primary numeric value for aggregation.
        Override in subclasses to return the appropriate value (e.g., thrust_force, capacity).
        Marker abilities return 0.0 by default.
        """
        return 0.0

    def get_ui_rows(self) -> List[Dict[str, str]]:
        """
        Return list of UI rows for the capability scanner/details panel.
        Format: [{'label': 'Thrust', 'value': '1500 N', 'color_hint': '#FFFFFF'}]
        """
        return []

    # =========================================================================
    # Introspection Methods (for modifier system)
    # =========================================================================

    @classmethod
    def get_consumed_stats(cls) -> Set['StatKey']:
        """
        Returns the set of stat keys this ability type consumes.

        Used by:
        - UI to show what stats affect this ability
        - Validation to warn about unused stats
        - ModifierIntrospection to determine what abilities a modifier affects

        Returns:
            Set of StatKey values that this ability reads from component.stats
        """
        from .stat_keys import StatKey
        return {binding.stat_key for binding in cls.STAT_BINDINGS}

    @classmethod
    def get_stat_bindings_info(cls) -> List[Dict[str, Any]]:
        """
        Returns detailed info about stat bindings for UI introspection.

        Used by tooltips to show "This ability is affected by: Damage (+50%)"

        Returns:
            List of dicts with keys: stat_key, attribute, operation
        """
        return [
            {
                'stat_key': binding.stat_key.value,
                'attribute': binding.attribute_name,
                'operation': binding.operation,
            }
            for binding in cls.STAT_BINDINGS
        ]

    def get_effect_summary(self) -> List[Dict[str, Any]]:
        """
        Returns a summary of all active effects on this ability.

        Used for UI tooltips showing "Damage: 100 -> 150 (+50%)"

        Returns:
            List of dicts with keys: attribute, base, current, stat_key, stat_value, operation
            Only includes stats that are actually modified (not default values).
        """
        summary = []
        stats = getattr(self.component, 'stats', {})

        for binding in self.STAT_BINDINGS:
            stat_value = stats.get(binding.stat_key.value)

            # Skip if stat not present or is at default (1.0 for mult, 0.0 for add)
            if stat_value is None:
                continue
            if binding.operation == 'multiply' and stat_value == 1.0:
                continue
            if binding.operation == 'add' and stat_value == 0.0:
                continue

            base_attr = binding.get_base_attribute_name()
            base_value = getattr(self, base_attr, None)
            if base_value is None:
                continue

            current_value = getattr(self, binding.attribute_name, base_value)

            summary.append({
                'attribute': binding.attribute_name,
                'base': base_value,
                'current': current_value,
                'stat_key': binding.stat_key.value,
                'stat_value': stat_value,
                'operation': binding.operation,
            })

        return summary
