"""Event type and category enumerations for the strategy event log system."""

from enum import Enum


class EventType(str, Enum):
    """Types of events that can occur during turn processing."""

    SHIP_BUILT = "ship_built"
    COMPLEX_BUILT = "complex_built"
    COLONY_FOUNDED = "colony_founded"
    COMBAT_RESOLVED = "combat_resolved"
    PLANET_DESTROYED = "planet_destroyed"
    STAR_DESTROYED = "star_destroyed"
    WARP_POINT_OPENED = "warp_point_opened"
    WARP_POINT_CLOSED = "warp_point_closed"
    DYSON_SPHERE_CREATED = "dyson_sphere_created"
    SHIPS_SELF_DESTRUCTED = "ships_self_destructed"


class EventCategory(str, Enum):
    """Categories for grouping and filtering events."""

    PRODUCTION = "production"
    COLONIES = "colonies"
    COMBAT = "combat"
    SUPERWEAPONS = "superweapons"
    ALL = "all"
