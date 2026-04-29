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

    def get_turn_events(
        self, turn: Optional[int] = None, *, empire_id: Optional[int] = None
    ) -> List[dict]:
        """Get events for a specific turn (or current turn if None).

        Returns a list of immutable event dicts for UI consumption.

        Args:
            turn: Turn number (None → current turn).
            empire_id: BUG-123 — when not None, scope to that empire's
                view (broadcasts on ``GLOBAL_EVENT_EMPIRE_ID`` (-1)
                are still included). When None the call is forwarded
                positionally so legacy callers/tests continue to see
                the prior call shape.
        """
        if turn is None:
            turn = self._state.session.turn_number
        log = self._state.session.event_log
        if empire_id is None:
            events = log.get_events_for_turn(turn)
        else:
            events = log.get_events_for_turn(turn, empire_id=empire_id)
        return [e.to_dict() for e in events]

    def get_all_events(self, *, empire_id: Optional[int] = None) -> List[dict]:
        """Get all events from the event log.

        Args:
            empire_id: BUG-123 — when not None, scope to that empire's
                view via ``EventLog.get_events_for_empire`` (broadcasts
                on ``GLOBAL_EVENT_EMPIRE_ID`` (-1) included by default).
        """
        log = self._state.session.event_log
        if empire_id is None:
            events = log.get_all_events()
        else:
            events = log.get_events_for_empire(empire_id)
        return [e.to_dict() for e in events]

    def get_events_by_category(
        self, category: str, *, empire_id: Optional[int] = None
    ) -> List[dict]:
        """Get events filtered by category.

        Args:
            category: Category string or ``EventCategory`` enum value.
            empire_id: BUG-123 — optional empire scoping (broadcasts
                included). When None the call is forwarded positionally
                to preserve the prior call shape for existing tests.
        """
        log = self._state.session.event_log
        if empire_id is None:
            events = log.get_events_by_category(category)
        else:
            events = log.get_events_by_category(category, empire_id=empire_id)
        return [e.to_dict() for e in events]
