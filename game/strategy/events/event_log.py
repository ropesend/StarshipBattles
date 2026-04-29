"""Event data model and event log collection for the strategy layer."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from game.strategy.events.event_types import EventCategory
from game.core.validation_helpers import require_keys


# BUG-123: Sentinel ``empire_id`` value for events that have no single
# owning empire (e.g. environmental hazards, star destruction). Set in
# ``GameSession._create_event_handler`` when callers omit the kwarg.
# Treated as a broadcast to all empires by ``get_events_for_empire`` and
# the ``empire_id`` kwarg on the other queries.
GLOBAL_EVENT_EMPIRE_ID = -1


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

    def get_events_for_turn(
        self, turn: int, *, empire_id: Optional[int] = None
    ) -> List[Event]:
        """Return events from the given turn.

        Args:
            turn: Turn number to filter by.
            empire_id: BUG-123 — when not None, also scope to events
                owned by ``empire_id``. ``GLOBAL_EVENT_EMPIRE_ID`` (-1)
                events are included as broadcasts. Use
                ``get_events_for_empire`` directly for the
                ``include_global=False`` opt-out.
        """
        if empire_id is None:
            return [e for e in self._events if e.turn == turn]
        return [
            e for e in self._events
            if e.turn == turn and self._matches_empire(e, empire_id)
        ]

    def get_events_by_category(
        self,
        category: Union[str, EventCategory],
        *,
        empire_id: Optional[int] = None,
    ) -> List[Event]:
        """Return events matching the given category.

        If category is "all" (or EventCategory.ALL), returns all events.

        Args:
            category: Category string or EventCategory enum value to filter by.
            empire_id: BUG-123 — when not None, also scope to events
                owned by ``empire_id``. ``GLOBAL_EVENT_EMPIRE_ID`` (-1)
                events are included as broadcasts.
        """
        cat_value = category.value if isinstance(category, EventCategory) else category
        is_all = cat_value == EventCategory.ALL.value
        if empire_id is None:
            if is_all:
                return list(self._events)
            return [e for e in self._events if e.category == cat_value]
        if is_all:
            return [e for e in self._events if self._matches_empire(e, empire_id)]
        return [
            e for e in self._events
            if e.category == cat_value and self._matches_empire(e, empire_id)
        ]

    def get_events_for_empire(
        self, empire_id: int, *, include_global: bool = True
    ) -> List[Event]:
        """Return events scoped to one empire's view (BUG-123).

        Args:
            empire_id: Empire id to scope to.
            include_global: When True (default), events with
                ``empire_id == GLOBAL_EVENT_EMPIRE_ID`` are included as
                broadcasts (environmental hazards, star destruction —
                events that have no single owner). Pass False for
                strict per-empire visibility.
        """
        if include_global:
            return [
                e for e in self._events
                if e.empire_id == empire_id
                or e.empire_id == GLOBAL_EVENT_EMPIRE_ID
            ]
        return [e for e in self._events if e.empire_id == empire_id]

    @staticmethod
    def _matches_empire(event: Event, empire_id: int) -> bool:
        """BUG-123: shared per-empire visibility predicate.

        Used by the ``empire_id`` kwarg paths on ``get_events_for_turn``
        and ``get_events_by_category``. ``get_events_for_empire`` owns
        its own logic so it can expose the ``include_global`` opt-out.
        """
        return (
            event.empire_id == empire_id
            or event.empire_id == GLOBAL_EVENT_EMPIRE_ID
        )

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
