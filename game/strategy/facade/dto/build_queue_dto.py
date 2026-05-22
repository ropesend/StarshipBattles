"""Data Transfer Objects for Build Queues."""
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from game.core.hex_math import HexCoord

@dataclass(frozen=True)
class BuildQueueSourceDTO:
    """Immutable representation of a build queue source for the UI layer.

    Replaces the domain-coupled BuildQueueSource to ensure the UI
    cannot mutate the origin entity.

    PROJ-472 Phase 1B: ``is_paused`` + the owner-derived SCALARS
    ``owner_global_hex`` / ``owner_system_name`` are projected here so the
    build-queue UI no longer needs a live ``owner_entity`` reference. The
    owner scalars are resolved against the galaxy at slice-projection time
    (``EmpireSlice``); ``from_domain`` cannot reach the galaxy itself, so
    callers pass the resolved values in. ``HexCoord`` / ``str`` are
    immutable value types, so holding them directly does not re-leak the
    mutable domain object.
    """
    queue_id: str
    display_name: str
    entity_id: int
    construction_queue: List[Dict[str, Any]]
    can_build_ships: bool
    can_build_complexes: bool
    context_type: str
    build_rate: Dict[str, float]
    planet_id: Optional[int] = None
    empire_id: Optional[int] = None
    is_paused: bool = False
    owner_global_hex: Optional[HexCoord] = None
    owner_system_name: Optional[str] = None

    @classmethod
    def from_domain(
        cls,
        source: Any,
        *,
        owner_global_hex: Optional[HexCoord] = None,
        owner_system_name: Optional[str] = None,
    ) -> 'BuildQueueSourceDTO':
        """Convert a domain BuildQueueSource to a purely immutable DTO.

        ``owner_global_hex`` / ``owner_system_name`` are resolved by the
        caller (the empire slice has galaxy access) and threaded through —
        the DTO never holds the live owner entity.
        """
        entity_id = getattr(source.owner_entity, 'id', 0)
        empire_id = getattr(source.owner_entity, 'owner_id', None)
        return cls(
            queue_id=source.queue_id,
            display_name=source.display_name,
            entity_id=entity_id,
            # Create detached copies of the queue items to prevent UI mutation
            construction_queue=[deepcopy(item) for item in list(source.construction_queue)],
            can_build_ships=source.can_build_ships,
            can_build_complexes=source.can_build_complexes,
            context_type=source.context_type,
            # Freeze the build rate dict
            build_rate=dict(source.build_rate),
            planet_id=source.planet_id,
            empire_id=empire_id,
            is_paused=getattr(source, 'is_paused', False),
            owner_global_hex=owner_global_hex,
            owner_system_name=owner_system_name,
        )
