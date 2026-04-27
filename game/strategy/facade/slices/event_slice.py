"""Event-log + plain session-state read slice (PROJ-309 sub-phase 3.7)."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from game.strategy.facade.slices._facade_state import FacadeSessionState


class EventSlice:
    """Event log + plain session-state reads (turn number, save path,
    human-player ids).
    """

    __slots__ = ("_state",)

    def __init__(self, state: "FacadeSessionState") -> None:
        self._state = state

    # ------------------------------------------------------------------
    # Plain session reads
    # ------------------------------------------------------------------

    def get_human_player_ids(self) -> List[int]:
        """Get the empire IDs of human players."""
        return list(self._state.session.human_player_ids)

    def get_turn_number(self) -> int:
        """Get the current turn number (1-indexed)."""
        return self._state.session.turn_number

    def get_save_path(self) -> Optional[str]:
        """Get the current save game file path, or None if not yet saved."""
        return self._state.session.save_path

    # ------------------------------------------------------------------
    # Event log queries (PROJ-77)
    # ------------------------------------------------------------------

    def get_turn_events(self, turn: int = None) -> List[dict]:
        """Get events for a specific turn (or current turn if None).

        Returns a list of immutable event dicts for UI consumption.
        """
        if turn is None:
            turn = self._state.session.turn_number
        events = self._state.session.event_log.get_events_for_turn(turn)
        return [e.to_dict() for e in events]

    def get_all_events(self) -> List[dict]:
        """Get all events from the event log."""
        return [
            e.to_dict()
            for e in self._state.session.event_log.get_all_events()
        ]

    def get_events_by_category(self, category: str) -> List[dict]:
        """Get events filtered by category.

        ``category`` accepts a string or `EventCategory` enum value.
        """
        events = self._state.session.event_log.get_events_by_category(category)
        return [e.to_dict() for e in events]
