"""Tests for GameSession event log integration (PROJ-77 Phase 2)."""

import pytest
from unittest.mock import patch

from game.strategy.engine.game_session import GameSession
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.strategy.events import Event, EventLog, EventType, EventCategory


def _make_minimal_config() -> GameConfig:
    """Create a minimal GameConfig for testing."""
    config = GameConfig()
    config.galaxy_radius = 300
    config.system_count = 2
    config.players = [
        PlayerConfig(name="TestPlayer", is_human=True, color=(0, 100, 200)),
        PlayerConfig(name="TestEnemy", is_human=False, color=(200, 100, 0)),
    ]
    return config


class TestGameSessionEventLog:
    """Tests for EventLog integration in GameSession."""

    def test_session_creates_event_log_on_init(self):
        """GameSession initializes an empty EventLog."""
        session = GameSession(config=_make_minimal_config())
        assert isinstance(session.event_log, EventLog)
        assert len(session.event_log.get_all_events()) == 0

    def test_session_event_log_property_returns_event_log(self):
        """event_log property returns the internal EventLog instance."""
        session = GameSession(config=_make_minimal_config())
        log = session.event_log
        assert log is session.event_log  # Same object

    def test_session_registers_event_handler(self):
        """GameSession registers a global event handler via set_event_handler."""
        from game.core import logger as logger_mod

        old_handler = logger_mod._event_handler
        try:
            session = GameSession(config=_make_minimal_config())
            # A handler should now be registered
            assert logger_mod._event_handler is not None
        finally:
            logger_mod._event_handler = old_handler

    def test_event_handler_creates_events(self):
        """log_event() calls route through to the session's EventLog."""
        from game.core.logger import log_event, set_event_handler
        import game.core.logger as logger_mod

        old_handler = logger_mod._event_handler
        try:
            session = GameSession(config=_make_minimal_config())

            # Use the global log_event to simulate engine emission
            log_event(
                EventType.SHIP_BUILT,
                category=EventCategory.PRODUCTION,
                message="Scout built at Alpha",
                empire_id=0,
                ship_name="Scout",
            )

            events = session.event_log.get_all_events()
            assert len(events) == 1
            assert events[0].event_type == EventType.SHIP_BUILT
            assert events[0].category == EventCategory.PRODUCTION
            assert events[0].message == "Scout built at Alpha"
            assert events[0].empire_id == 0
            assert events[0].details == {"ship_name": "Scout"}
        finally:
            logger_mod._event_handler = old_handler

    def test_event_handler_uses_current_turn_number(self):
        """Events created by the handler use the session's current turn number."""
        import game.core.logger as logger_mod
        from game.core.logger import log_event

        old_handler = logger_mod._event_handler
        try:
            session = GameSession(config=_make_minimal_config())
            session.turn_number = 5

            log_event(
                EventType.COLONY_FOUNDED,
                category=EventCategory.COLONIES,
                message="Colony founded",
                empire_id=0,
            )

            events = session.event_log.get_all_events()
            assert len(events) == 1
            assert events[0].turn == 5
        finally:
            logger_mod._event_handler = old_handler

    def test_event_handler_defaults_for_missing_kwargs(self):
        """Handler provides defaults when optional kwargs are missing."""
        import game.core.logger as logger_mod
        from game.core.logger import log_event

        old_handler = logger_mod._event_handler
        try:
            session = GameSession(config=_make_minimal_config())

            # Call with minimal kwargs
            log_event("custom_event")

            events = session.event_log.get_all_events()
            assert len(events) == 1
            assert events[0].event_type == "custom_event"
            assert events[0].category == "other"
            assert events[0].message == ""
            assert events[0].empire_id == -1
        finally:
            logger_mod._event_handler = old_handler

    def test_multiple_events_accumulate(self):
        """Multiple log_event calls accumulate in the EventLog."""
        import game.core.logger as logger_mod
        from game.core.logger import log_event

        old_handler = logger_mod._event_handler
        try:
            session = GameSession(config=_make_minimal_config())

            log_event(EventType.SHIP_BUILT, category=EventCategory.PRODUCTION,
                      message="Ship 1", empire_id=0)
            log_event(EventType.SHIP_BUILT, category=EventCategory.PRODUCTION,
                      message="Ship 2", empire_id=0)
            log_event(EventType.COMBAT_RESOLVED, category=EventCategory.COMBAT,
                      message="Battle", empire_id=1)

            events = session.event_log.get_all_events()
            assert len(events) == 3
        finally:
            logger_mod._event_handler = old_handler


class TestGameSessionEventPersistence:
    """Tests for EventLog save/load persistence."""

    def test_to_dict_includes_event_log(self):
        """to_dict() serializes the event log."""
        session = GameSession(config=_make_minimal_config())

        # Manually add an event
        event = Event(
            event_type=EventType.SHIP_BUILT,
            category=EventCategory.PRODUCTION,
            turn=1,
            empire_id=0,
            message="Scout completed",
            details={"ship_name": "Scout"},
        )
        session.event_log.append(event)

        data = session.to_dict()
        assert "event_log" in data
        assert "events" in data["event_log"]
        assert len(data["event_log"]["events"]) == 1
        assert data["event_log"]["events"][0]["event_type"] == EventType.SHIP_BUILT

    def test_from_dict_restores_event_log(self):
        """from_dict() restores the event log from saved data."""
        session = GameSession(config=_make_minimal_config())

        # Add events
        event = Event(
            event_type=EventType.COLONY_FOUNDED,
            category=EventCategory.COLONIES,
            turn=3,
            empire_id=1,
            message="New colony",
        )
        session.event_log.append(event)

        # Round-trip
        data = session.to_dict()
        restored = GameSession.from_dict(data)

        events = restored.event_log.get_all_events()
        assert len(events) == 1
        assert events[0].event_type == EventType.COLONY_FOUNDED
        assert events[0].category == EventCategory.COLONIES
        assert events[0].turn == 3
        assert events[0].empire_id == 1
        assert events[0].message == "New colony"

    def test_from_dict_handles_missing_event_log(self):
        """from_dict() creates empty EventLog when event_log key is missing."""
        session = GameSession(config=_make_minimal_config())
        data = session.to_dict()

        # Remove event_log from saved data (simulates older save)
        del data["event_log"]

        restored = GameSession.from_dict(data)
        assert isinstance(restored.event_log, EventLog)
        assert len(restored.event_log.get_all_events()) == 0

    def test_round_trip_preserves_multiple_events(self):
        """Full save/load preserves multiple events with different categories."""
        session = GameSession(config=_make_minimal_config())

        events_data = [
            (EventType.SHIP_BUILT, EventCategory.PRODUCTION, 1, 0, "Scout built"),
            (EventType.COMPLEX_BUILT, EventCategory.PRODUCTION, 1, 0, "Station built"),
            (EventType.COLONY_FOUNDED, EventCategory.COLONIES, 2, 0, "Colony founded"),
            (EventType.COMBAT_RESOLVED, EventCategory.COMBAT, 2, 1, "Battle resolved"),
        ]

        for etype, ecat, turn, eid, msg in events_data:
            session.event_log.append(Event(
                event_type=etype, category=ecat,
                turn=turn, empire_id=eid, message=msg,
            ))

        data = session.to_dict()
        restored = GameSession.from_dict(data)

        restored_events = restored.event_log.get_all_events()
        assert len(restored_events) == 4
        assert restored_events[0].event_type == EventType.SHIP_BUILT
        assert restored_events[3].event_type == EventType.COMBAT_RESOLVED

    def test_round_trip_preserves_event_details(self):
        """Save/load preserves the details dict on events."""
        session = GameSession(config=_make_minimal_config())

        session.event_log.append(Event(
            event_type=EventType.SHIP_BUILT,
            category=EventCategory.PRODUCTION,
            turn=1,
            empire_id=0,
            message="Destroyer built",
            details={"ship_name": "Destroyer", "planet_name": "Earth", "cost": 150},
        ))

        data = session.to_dict()
        restored = GameSession.from_dict(data)

        event = restored.event_log.get_all_events()[0]
        assert event.details["ship_name"] == "Destroyer"
        assert event.details["planet_name"] == "Earth"
        assert event.details["cost"] == 150
