"""ComponentRef: Typed wrapper for component references.

This module provides a standard pattern for referencing components in the builder,
replacing error-prone tuple access patterns like (layer_type, index, component).

USAGE:
    # Old pattern (fragile, index-based access):
    selection = (LayerType.WEAPONS, 3, component)
    comp = selection[2]  # Error-prone magic number

    # New pattern (explicit, typed access):
    selection = ComponentRef(component=component, layer_type=LayerType.WEAPONS, index=3)
    comp = selection.component  # Clear and type-safe

NOTE: ComponentRef is frozen (immutable) to ensure consistency when used as
dict keys or in sets. The underlying component object can still be mutated,
but the reference itself cannot change.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Any

if TYPE_CHECKING:
    from game.core.constants import LayerType
    from game.simulation.components.component import Component


@dataclass(frozen=True)
class ComponentRef:
    """Immutable reference to a component instance in the ship structure.

    Attributes:
        component: The actual component object (required for all operations).
        layer_type: Which layer the component is in (None if not placed).
        index: Position in layer's component list (None if not placed).

    Properties:
        component_id: The component's type identifier (e.g., "weapon_laser_mk2").
        is_placed: Whether this component is actively placed in a layer.

    Example:
        ref = ComponentRef(
            component=my_component,
            layer_type=LayerType.WEAPONS,
            index=0
        )
        assert ref.component_id == "weapon_laser_mk2"
        assert ref.is_placed is True
    """

    component: Any  # Component type, but avoiding import cycle
    layer_type: Optional["LayerType"] = None
    index: Optional[int] = None

    @property
    def component_id(self) -> str:
        """Return the component's type identifier."""
        return self.component.id

    @property
    def is_placed(self) -> bool:
        """Check if this component is actively placed in a layer."""
        return self.layer_type is not None and self.index is not None
