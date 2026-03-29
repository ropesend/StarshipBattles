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
    RESOURCE_SHORTAGE = "resource_shortage"
    FLEET_JOINED = "fleet_joined"
    FLEET_JOIN_REDIRECTED = "fleet_join_redirected"
    FLEET_JOIN_CANCELLED = "fleet_join_cancelled"
    # Planet operations (PROJ-237)
    SHIELD_ACTIVATED = "shield_activated"
    SHIELD_DEACTIVATED = "shield_deactivated"
    SHIELD_AUTO_DEACTIVATED = "shield_auto_deactivated"


class EventCategory(str, Enum):
    """Categories for grouping and filtering events."""

    PRODUCTION = "production"
    COLONIES = "colonies"
    COMBAT = "combat"
    SUPERWEAPONS = "superweapons"
    FLEET_OPERATIONS = "fleet_operations"
    PLANET_OPERATIONS = "planet_operations"
    ALL = "all"
