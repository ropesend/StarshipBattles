"""BUG-123: end-to-end integration tests for per-empire Event Log filtering.

Spins up a real GameSession with two empires, logs events for each (and one
global event), and exercises the facade-side empire scoping that drives the
Event Log UI.
"""

from game.strategy.engine.game_session import GameSession
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.strategy.events import EventCategory, EventType
from game.strategy.facade.strategy_session_facade import StrategySessionFacade


def _make_config() -> GameConfig:
    config = GameConfig()
    config.galaxy_radius = 300
    config.system_count = 2
    config.players = [
        PlayerConfig(name="Chimera", is_human=True, color=(0, 100, 200)),
        PlayerConfig(name="Lahore", is_human=True, color=(200, 100, 0)),
    ]
    return config


def _seed_two_empire_events(session: GameSession) -> None:
    """Match the BUG-123 screenshot: each empire has production events,
    plus one global star-destroyed event."""
    session._event_bus.log_event(
        EventType.SHIP_BUILT, category=EventCategory.PRODUCTION,
        message="Built Scout at Chimera", empire_id=0,
    )
    session._event_bus.log_event(
        EventType.COMPLEX_BUILT, category=EventCategory.PRODUCTION,
        message="Production paused at Chimera", empire_id=0,
    )
    session._event_bus.log_event(
        EventType.SHIP_BUILT, category=EventCategory.PRODUCTION,
        message="Built Frigate at Lahore", empire_id=1,
    )
    session._event_bus.log_event(
        EventType.COMPLEX_BUILT, category=EventCategory.PRODUCTION,
        message="Production paused at Lahore", empire_id=1,
    )
    # Global event — broadcast to all empires.
    session._event_bus.log_event(
        EventType.STAR_DESTROYED, category=EventCategory.SUPERWEAPONS,
        message="A star has been destroyed", empire_id=-1,
    )


class TestEventLogEmpireFilter:
    """Acceptance: each empire only sees its own events plus globals."""

    def test_active_empire_0_sees_only_own_and_global(self) -> None:
        session = GameSession(config=_make_config())
        facade = StrategySessionFacade(session)
        _seed_two_empire_events(session)

        events = facade.events.all(empire_id=0)
        messages = {e["message"] for e in events}

        # Owns: Chimera empire's two events + the global broadcast.
        assert "Built Scout at Chimera" in messages
        assert "Production paused at Chimera" in messages
        assert "A star has been destroyed" in messages
        # Doesn't leak: Lahore's events.
        assert "Built Frigate at Lahore" not in messages
        assert "Production paused at Lahore" not in messages

    def test_active_empire_1_sees_only_own_and_global(self) -> None:
        session = GameSession(config=_make_config())
        facade = StrategySessionFacade(session)
        _seed_two_empire_events(session)

        events = facade.events.all(empire_id=1)
        messages = {e["message"] for e in events}

        assert "Built Frigate at Lahore" in messages
        assert "Production paused at Lahore" in messages
        assert "A star has been destroyed" in messages
        assert "Built Scout at Chimera" not in messages
        assert "Production paused at Chimera" not in messages

    def test_global_event_visible_to_both_empires(self) -> None:
        """Single source of truth: the same event reaches both empires."""
        session = GameSession(config=_make_config())
        facade = StrategySessionFacade(session)
        _seed_two_empire_events(session)

        msgs_0 = {e["message"] for e in facade.events.all(empire_id=0)}
        msgs_1 = {e["message"] for e in facade.events.all(empire_id=1)}
        assert "A star has been destroyed" in msgs_0
        assert "A star has been destroyed" in msgs_1

    def test_total_event_count_drops_when_filter_active(self) -> None:
        """Acceptance #3 (BUG-123): scoped count < unscoped count."""
        session = GameSession(config=_make_config())
        facade = StrategySessionFacade(session)
        _seed_two_empire_events(session)

        unscoped = facade.events.all()
        scoped = facade.events.all(empire_id=0)
        assert len(scoped) < len(unscoped)
        assert len(scoped) == 3   # 2 own + 1 global
        assert len(unscoped) == 5  # 2 + 2 + 1

    def test_get_turn_events_scoping_matches_acceptance(self) -> None:
        """Per-turn auto-popup path: only the active empire's events surface."""
        session = GameSession(config=_make_config())
        facade = StrategySessionFacade(session)
        _seed_two_empire_events(session)

        turn = session.turn_number
        e0 = facade.events.turn_events(turn=turn, empire_id=0)
        e1 = facade.events.turn_events(turn=turn, empire_id=1)
        assert len(e0) == 3   # 2 own + 1 global
        assert len(e1) == 3   # 2 own + 1 global
        assert {e["message"] for e in e0}.isdisjoint(
            {"Built Frigate at Lahore", "Production paused at Lahore"}
        )

    def test_no_empire_id_kwarg_returns_unscoped_baseline(self) -> None:
        """Defaults preserve behaviour for legacy callers / tests."""
        session = GameSession(config=_make_config())
        facade = StrategySessionFacade(session)
        _seed_two_empire_events(session)

        assert len(facade.events.all()) == 5
        assert len(facade.events.turn_events()) == 5
