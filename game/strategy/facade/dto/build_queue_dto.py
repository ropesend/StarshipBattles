"""Data Transfer Objects for Build Queues."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

@dataclass(frozen=True)
class BuildQueueSourceDTO:
    """Immutable representation of a build queue source for the UI layer.
    
    Replaces the domain-coupled BuildQueueSource to ensure the UI
    cannot mutate the origin entity.
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

    @classmethod
    def from_domain(cls, source: Any) -> 'BuildQueueSourceDTO':
        """Convert a domain BuildQueueSource to a purely immutable DTO."""
        entity_id = getattr(source.owner_entity, 'id', 0)
        empire_id = getattr(source.owner_entity, 'owner_id', None)
        return cls(
            queue_id=source.queue_id,
            display_name=source.display_name,
            entity_id=entity_id,
            # Create a detached copy of the queue items to prevent UI mutation
            construction_queue=[dict(item) for item in list(source.construction_queue)],
            can_build_ships=source.can_build_ships,
            can_build_complexes=source.can_build_complexes,
            context_type=source.context_type,
            # Freeze the build rate dict
            build_rate=dict(source.build_rate),
            planet_id=source.planet_id,
            empire_id=empire_id
        )
