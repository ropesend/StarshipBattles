"""Integration tests for the Event Log system (PROJ-77 Phase 5).

Tests the full event flow:
- Events emitted during turn processing
- Events visible through facade queries
- Events persist through save/load cycle
- Facade category and turn filtering
"""

import pytest
from unittest.mock import patch, MagicMock

from game.strategy.engine.game_session import GameSession
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.strategy.facade.strategy_session_facade import StrategySessionFacade
from game.strategy.events import Event, EventLog, EventType, EventCategory


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_config() -> GameConfig:
    """Create a minimal GameConfig for integration testing."""
    config = GameConfig()
    config.galaxy_radius = 300
    config.system_count = 2
    config.players = [
        PlayerConfig(name="TestPlayer", is_human=True, color=(0, 100, 200)),
        PlayerConfig(name="TestEnemy", is_human=False, color=(200, 100, 0)),
    ]
    return config


# ---------------------------------------------------------------------------
# Facade Event Queries
# ---------------------------------------------------------------------------


class TestFacadeEventQueries:
    """Test facade event query methods with real GameSession."""

    def test_facade_get_all_events_returns_dicts(self):
        """get_all_events() returns list of dicts, not Event objects."""
        session = GameSession(config=_make_config())
        facade = StrategySessionFacade(session)

        session._event_bus.log_event(EventType.SHIP_BUILT, category=EventCategory.PRODUCTION,
                      message="Scout built", empire_id=0)

        events = facade.get_all_events()
        assert len(events) == 1
        assert isinstance(events[0], dict)
        assert events[0]["event_type"] == EventType.SHIP_BUILT.value
        assert events[0]["message"] == "Scout built"

    def test_facade_get_turn_events_defaults_to_current_turn(self):
        """get_turn_events() with no arg returns current turn events."""
        session = GameSession(config=_make_config())
        facade = StrategySessionFacade(session)

        session._event_bus.log_event(EventType.SHIP_BUILT, category=EventCategory.PRODUCTION,
                      message="Ship 1", empire_id=0)

        events = facade.get_turn_events()
        assert len(events) == 1
        assert events[0]["turn"] == session.turn_number

    def test_facade_get_turn_events_specific_turn(self):
        """get_turn_events(turn) returns only events from that turn."""
        session = GameSession(config=_make_config())
        facade = StrategySessionFacade(session)

        # Emit events at different turns
        session.turn_number = 1
        session._event_bus.log_event(EventType.SHIP_BUILT, category=EventCategory.PRODUCTION,
                      message="Turn 1 ship", empire_id=0)
        session.turn_number = 2
        session._event_bus.log_event(EventType.COLONY_FOUNDED, category=EventCategory.COLONIES,
                      message="Turn 2 colony", empire_id=0)

        turn_1 = facade.get_turn_events(1)
        turn_2 = facade.get_turn_events(2)
        assert len(turn_1) == 1
        assert turn_1[0]["message"] == "Turn 1 ship"
        assert len(turn_2) == 1
        assert turn_2[0]["message"] == "Turn 2 colony"

    def test_facade_get_events_by_category(self):
        """get_events_by_category() filters correctly."""
        session = GameSession(config=_make_config())
        facade = StrategySessionFacade(session)

        session._event_bus.log_event(EventType.SHIP_BUILT, category=EventCategory.PRODUCTION,
                      message="Ship", empire_id=0)
        session._event_bus.log_event(EventType.COMBAT_RESOLVED, category=EventCategory.COMBAT,
                      message="Battle", empire_id=1)
        session._event_bus.log_event(EventType.COLONY_FOUNDED, category=EventCategory.COLONIES,
                      message="Colony", empire_id=0)

        prod = facade.get_events_by_category("production")
        combat = facade.get_events_by_category("combat")
        colonies = facade.get_events_by_category("colonies")
        all_events = facade.get_events_by_category("all")

        assert len(prod) == 1
        assert len(combat) == 1
        assert len(colonies) == 1
        assert len(all_events) == 3

    def test_ship_built_event_visible_in_facade(self):
        """Ship building event is visible through facade after emission."""
        session = GameSession(config=_make_config())
        facade = StrategySessionFacade(session)

        session._event_bus.log_event(EventType.SHIP_BUILT, category=EventCategory.PRODUCTION,
                      empire_id=0, message="Frigate built at Mars",
                      design_id="frigate_01", planet_id=3)

        events = facade.get_all_events()
        assert len(events) == 1
        assert events[0]["event_type"] == "ship_built"
        assert events[0]["details"]["design_id"] == "frigate_01"
        assert events[0]["details"]["planet_id"] == 3

    def test_complex_built_event_visible_in_facade(self):
        """Complex building event is visible through facade."""
        session = GameSession(config=_make_config())
        facade = StrategySessionFacade(session)

        session._event_bus.log_event(EventType.COMPLEX_BUILT, category=EventCategory.PRODUCTION,
                      empire_id=0, message="Mine built on Alpha",
                      design_id="mining_complex", planet_id=5)

        events = facade.get_all_events()
        assert len(events) == 1
        assert events[0]["event_type"] == "complex_built"
        assert events[0]["category"] == "production"

    def test_colony_founded_event_visible_in_facade(self):
        """Colony founded event is visible through facade."""
        session = GameSession(config=_make_config())
        facade = StrategySessionFacade(session)

        session._event_bus.log_event(EventType.COLONY_FOUNDED, category=EventCategory.COLONIES,
                      empire_id=0, message="Colony on New Earth",
                      planet_id=10, planet_name="New Earth")

        events = facade.get_all_events()
        assert len(events) == 1
        assert events[0]["event_type"] == "colony_founded"
        assert events[0]["category"] == "colonies"
        assert events[0]["details"]["planet_name"] == "New Earth"

    def test_combat_resolved_event_visible_in_facade(self):
        """Combat resolved event is visible through facade."""
        session = GameSession(config=_make_config())
        facade = StrategySessionFacade(session)

        session._event_bus.log_event(EventType.COMBAT_RESOLVED, category=EventCategory.COMBAT,
                      empire_id=0, message="Battle at (3,4)",
                      participating_fleet_ids=[1, 2],
                      surviving_fleet_ids=[1],
                      destroyed_fleet_ids=[2])

        events = facade.get_all_events()
        assert len(events) == 1
        assert events[0]["event_type"] == "combat_resolved"
        assert events[0]["category"] == "combat"
        assert events[0]["details"]["surviving_fleet_ids"] == [1]
        assert events[0]["details"]["destroyed_fleet_ids"] == [2]


# ---------------------------------------------------------------------------
# Persistence Integration
# ---------------------------------------------------------------------------


class TestEventPersistenceIntegration:
    """Test events survive save/load cycle through GameSession."""

    def test_events_persist_through_save_load(self):
        """Events in EventLog survive full save/load cycle."""
        session = GameSession(config=_make_config())

        session._event_bus.log_event(EventType.SHIP_BUILT, category=EventCategory.PRODUCTION,
                      empire_id=0, message="Scout built")
        session._event_bus.log_event(EventType.COLONY_FOUNDED, category=EventCategory.COLONIES,
                      empire_id=0, message="Colony founded")
        session._event_bus.log_event(EventType.COMBAT_RESOLVED, category=EventCategory.COMBAT,
                      empire_id=1, message="Battle resolved")

        data = session.to_dict()
        restored = GameSession.from_dict(data)

        events = restored.event_log.get_all_events()
        assert len(events) == 3
        assert events[0].event_type == "ship_built"
        assert events[1].event_type == "colony_founded"
        assert events[2].event_type == "combat_resolved"

    def test_events_persist_details_through_save_load(self):
        """Event details dict survives save/load cycle."""
        session = GameSession(config=_make_config())

        session._event_bus.log_event(EventType.SHIP_BUILT, category=EventCategory.PRODUCTION,
                      empire_id=0, message="Destroyer built",
                      design_id="destroyer_mk2", planet_id=7, cost=250)

        data = session.to_dict()
        restored = GameSession.from_dict(data)

        event = restored.event_log.get_all_events()[0]
        assert event.details["design_id"] == "destroyer_mk2"
        assert event.details["planet_id"] == 7
        assert event.details["cost"] == 250

    def test_restored_session_facade_can_query_events(self):
        """After save/load, facade on restored session can query events."""
        session = GameSession(config=_make_config())

        session._event_bus.log_event(EventType.SHIP_BUILT, category=EventCategory.PRODUCTION,
                      empire_id=0, message="Ship A")
        session._event_bus.log_event(EventType.COMBAT_RESOLVED, category=EventCategory.COMBAT,
                      empire_id=1, message="Battle B")

        data = session.to_dict()
        restored = GameSession.from_dict(data)
        facade = StrategySessionFacade(restored)

        all_events = facade.get_all_events()
        assert len(all_events) == 2

        prod = facade.get_events_by_category("production")
        combat = facade.get_events_by_category("combat")
        assert len(prod) == 1
        assert len(combat) == 1

    def test_empty_event_log_persists_correctly(self):
        """Session with no events saves/loads cleanly."""
        session = GameSession(config=_make_config())

        data = session.to_dict()
        restored = GameSession.from_dict(data)

        assert len(restored.event_log.get_all_events()) == 0
