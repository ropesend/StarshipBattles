"""Event data model and event log collection for the strategy layer."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Union

from game.strategy.events.event_types import EventCategory
from game.core.validation_helpers import require_keys


@dataclass
class Event:
    """A single game event recorded during turn processing.

    Attributes:
        event_type: The type of event (e.g. "ship_built", "combat_resolved").
        category: The event category for filtering (e.g. "production", "combat").
        turn: The turn number when the event occurred.
        empire_id: The empire that owns or triggered the event.
        message: Human-readable description of the event.
        details: Additional structured data specific to the event type.
    """

    event_type: str
    category: str
    turn: int
    empire_id: int
    message: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a plain dictionary for save game persistence."""
        return {
            "event_type": self.event_type,
            "category": self.category,
            "turn": self.turn,
            "empire_id": self.empire_id,
            "message": self.message,
            "details": self.details,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Reconstruct an Event from a serialized dictionary.

        Args:
            data: Dictionary containing event data

        Returns:
            Event instance

        Raises:
            PersistenceException: If required keys are missing
        """
        require_keys(
            data,
            ['event_type', 'category', 'turn', 'empire_id', 'message'],
            'Event'
        )
        return cls(
            event_type=data["event_type"],
            category=data["category"],
            turn=data["turn"],
            empire_id=data["empire_id"],
            message=data["message"],
            details=data.get("details", {}),
        )


class EventLog:
    """Collection of game events with filtering and serialization.

    Stores all events that occur during turn processing and provides
    methods to query them by turn number or category.
    """

    def __init__(self) -> None:
        self._events: List[Event] = []

    def append(self, event: Event) -> None:
        """Add an event to the log."""
        self._events.append(event)

    def get_all_events(self) -> List[Event]:
        """Return all events in the log."""
        return list(self._events)

    def get_events_for_turn(self, turn: int) -> List[Event]:
        """Return all events that occurred on the given turn."""
        return [e for e in self._events if e.turn == turn]

    def get_events_by_category(self, category: Union[str, EventCategory]) -> List[Event]:
        """Return events matching the given category.

        If category is "all" (or EventCategory.ALL), returns all events.

        Args:
            category: Category string or EventCategory enum value to filter by.
        """
        cat_value = category.value if isinstance(category, EventCategory) else category
        if cat_value == EventCategory.ALL.value:
            return list(self._events)
        return [e for e in self._events if e.category == cat_value]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the entire event log for save game persistence."""
        return {"events": [e.to_dict() for e in self._events]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventLog':
        """Reconstruct an EventLog from a serialized dictionary."""
        log = cls()
        for event_data in data.get("events", []):
            log.append(Event.from_dict(event_data))
        return log
