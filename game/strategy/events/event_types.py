"""Event type and category enumerations for the strategy event log system."""

from enum import Enum


class EventType(str, Enum):
    """Types of events that can occur during turn processing."""

    SHIP_BUILT = "ship_built"
    COMPLEX_BUILT = "complex_built"
    COLONY_FOUNDED = "colony_founded"
    COMBAT_RESOLVED = "combat_resolved"


class EventCategory(str, Enum):
    """Categories for grouping and filtering events."""

    PRODUCTION = "production"
    COLONIES = "colonies"
    COMBAT = "combat"
    ALL = "all"
