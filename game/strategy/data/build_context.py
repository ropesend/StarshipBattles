"""
BuildContext Protocol - Abstract interface for build queue producers.

Created as part of PROJ-67 Phase 4 to allow BuildQueueScreen and BuildQueueController
to work with both Planet and Fleet build contexts.
"""
from __future__ import annotations

from typing import Any, List, Dict, Protocol, runtime_checkable


@runtime_checkable
class BuildContext(Protocol):
    """
    Protocol for entities that can have a build queue.

    Both Planet and Fleet implement this protocol, allowing the UI layer
    to work with either without needing to know the concrete type.

    Properties:
        name: Display name of the build context (planet name or fleet name)
        construction_queue: List of items being built
        has_space_shipyard: Whether this context can build ships
        owner_id: ID of the owning empire
        context_type: "planet" or "fleet" for UI branching
    """

    @property
    def name(self) -> str:
        """Display name for the build context."""
        ...

    @property
    def construction_queue(self) -> List[Dict[str, Any]]:
        """List of build queue items."""
        ...

    @property
    def has_space_shipyard(self) -> bool:
        """Whether this context has an operational space shipyard."""
        ...

    @property
    def owner_id(self) -> int:
        """ID of the owning empire."""
        ...

    @property
    def context_type(self) -> str:
        """Return 'planet' or 'fleet' for UI branching."""
        ...

    def can_build_type(self, vehicle_type: str) -> bool:
        """
        Check if this context can build the given vehicle type.

        Args:
            vehicle_type: Type of vehicle ("ship", "fighter", "satellite", "complex")

        Returns:
            True if this context can build the given type.
        """
        ...
