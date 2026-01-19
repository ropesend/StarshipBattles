from typing import Dict, Any, List
from enum import Enum, Flag, auto


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
    """
    # Class-level defaults (subclasses override)
    layer: AbilityLayer = AbilityLayer.COMBAT
    allowed_scopes: List[AbilityScope] = [AbilityScope.SELF]
    default_scope: AbilityScope = AbilityScope.SELF

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
        except ValueError:
            raise ValueError(
                f"{self.__class__.__name__} received invalid scope '{scope_str}'. "
                f"Valid scopes: {[s.value for s in AbilityScope]}"
            )

        # Validate against allowed scopes
        if requested_scope not in self.allowed_scopes:
            raise ValueError(
                f"{self.__class__.__name__} does not support scope '{scope_str}'. "
                f"Allowed scopes: {[s.value for s in self.allowed_scopes]}"
            )

        return requested_scope

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
