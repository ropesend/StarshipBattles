"""FEAT-26 — EventLogDataSource exposes replay_id; per-row Replay button.

The Event Log gains a per-row Replay action column. Combat rows whose
`details["replay_id"]` is non-None render an enabled button; other rows
render disabled cells.

These tests focus on the data-source contract and on the EventLogWindow
button-press dispatch path. The full launch / graceful-degradation flow
is covered by `test_event_log_graceful_degradation.py` (integration).
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pygame
import pytest


# ---------------------------------------------------------------------------
# EventLogDataSource — replay_action column + replay_id surface
# ---------------------------------------------------------------------------


def _combat_row(replay_id):
    return {
        "category": "combat",
        "turn": 7,
        "message": "Battle: 2 fleets engaged",
        "details": {"replay_id": replay_id},
    }


def _production_row():
    return {
        "category": "production",
        "turn": 7,
        "message": "Built Cruiser",
        "details": {},
    }


def test_event_log_columns_include_replay_action() -> None:
    """A `replay_action` column is registered in EVENT_LOG_COLUMNS."""
    from game.ui.screens.event_log_data_source import EVENT_LOG_COLUMNS

    col_ids = [c["id"] for c in EVENT_LOG_COLUMNS]
    assert "replay_action" in col_ids
    col = next(c for c in EVENT_LOG_COLUMNS if c["id"] == "replay_action")
    # Generic single-button action column type.
    assert col.get("type") == "replay_action"
    # Visible by default for feature discovery.
    assert col.get("visible") is True


def test_data_source_get_cell_replay_id_for_combat_row_returns_string() -> None:
    from game.ui.screens.event_log_data_source import EventLogDataSource

    ds = EventLogDataSource([_combat_row("uuid-abc")])
    assert ds.get_cell_replay_id(0) == "uuid-abc"


def test_data_source_get_cell_replay_id_returns_none_when_missing() -> None:
    """Combat row without `replay_id` (legacy) returns None."""
    from game.ui.screens.event_log_data_source import EventLogDataSource

    legacy = {"category": "combat", "turn": 5, "message": "old", "details": {}}
    ds = EventLogDataSource([legacy])
    assert ds.get_cell_replay_id(0) is None


def test_data_source_get_cell_replay_id_returns_none_for_non_combat_rows() -> None:
    """Non-combat rows can never have a replay; return None."""
    from game.ui.screens.event_log_data_source import EventLogDataSource

    ds = EventLogDataSource([_production_row()])
    assert ds.get_cell_replay_id(0) is None


def test_data_source_get_cell_replay_id_out_of_bounds_returns_none() -> None:
    from game.ui.screens.event_log_data_source import EventLogDataSource

    ds = EventLogDataSource([])
    assert ds.get_cell_replay_id(0) is None
    assert ds.get_cell_replay_id(-1) is None


def test_data_source_get_cell_value_replay_action_returns_empty_string() -> None:
    """`get_cell_value` for the replay_action column is irrelevant; the
    column renders a button, not a label. Returning an empty string
    keeps the legacy fallback path safe."""
    from game.ui.screens.event_log_data_source import EventLogDataSource

    ds = EventLogDataSource([_combat_row("uuid")])
    assert ds.get_cell_value(0, "replay_action") == ""


# ---------------------------------------------------------------------------
# VirtualTable — replay_action column type spawns ONE button
# ---------------------------------------------------------------------------


@pytest.fixture
def pygame_init():
    pygame.init()
    pygame.display.set_mode((800, 600), pygame.HIDDEN)
    yield
    pygame.quit()


def _make_virtual_table_with_replay_action(rows):
    """Construct a VirtualTable wired to a real EventLogDataSource so we
    can drive the row-pool factory through the full path."""
    import pygame_gui
    from pygame_gui.elements import UIPanel

    from game.ui.components.table import (
        TableColumnManager,
        VirtualTable,
        NoSelect,
    )
    from game.ui.screens.event_log_data_source import (
        EVENT_LOG_COLUMNS,
        EventLogDataSource,
    )

    manager = pygame_gui.UIManager((800, 600))
    panel = UIPanel(
        relative_rect=pygame.Rect(0, 0, 800, 600),
        manager=manager,
    )
    ds = EventLogDataSource(rows)
    cm = TableColumnManager(EVENT_LOG_COLUMNS)
    table = VirtualTable(
        panel,
        manager,
        ds,
        cm,
        NoSelect(),
        row_height=28,
        header_height=30,
    )
    return table, ds


def test_replay_action_column_spawns_single_button(pygame_init) -> None:
    """The `replay_action` column type creates exactly ONE button per
    row (distinct from the build-queue 4-button `actions` column)."""
    table, ds = _make_virtual_table_with_replay_action(
        [_combat_row("uuid-1")]
    )
    # Find the replay_action widget on the first row.
    replay_widget = None
    for row in table._row_pool:
        for widget in row["widgets"]:
            if widget.get("col", {}).get("id") == "replay_action":
                replay_widget = widget
                break
        if replay_widget:
            break
    assert replay_widget is not None, "replay_action widget not found"
    assert replay_widget["type"] == "replay_action"
    assert "button" in replay_widget
    # Single button — not the 4-key `actions_dict` shape.
    assert "actions_dict" not in replay_widget


def test_replay_action_column_disabled_when_replay_id_none(pygame_init) -> None:
    """Rows with no replay_id render the button disabled."""
    table, ds = _make_virtual_table_with_replay_action(
        [_combat_row(None), _combat_row("uuid")]
    )
    table.update_visible_rows()
    # Find the row pools by row_index.
    row0 = next(r for r in table._row_pool if r.get("row_index") == 0)
    row1 = next(r for r in table._row_pool if r.get("row_index") == 1)
    btn0 = next(
        w for w in row0["widgets"] if w.get("type") == "replay_action"
    )["button"]
    btn1 = next(
        w for w in row1["widgets"] if w.get("type") == "replay_action"
    )["button"]
    assert not btn0.is_enabled
    assert btn1.is_enabled


def test_replay_action_button_press_dispatches_action_replay(pygame_init) -> None:
    """`check_action_button_press` returns ('replay', row_index) when the
    replay_action button is the clicked element."""
    table, ds = _make_virtual_table_with_replay_action(
        [_combat_row("uuid-1")]
    )
    table.update_visible_rows()
    row0 = next(r for r in table._row_pool if r.get("row_index") == 0)
    btn = next(
        w for w in row0["widgets"] if w.get("type") == "replay_action"
    )["button"]

    result = table.check_action_button_press(btn)
    assert result == ("replay", 0)


# ---------------------------------------------------------------------------
# EventLogWindow — Replay button click invokes the resolver + callback
# ---------------------------------------------------------------------------


def _make_event_log_window(events, *, resolver=None, launch_cb=None):
    import pygame_gui

    from game.ui.screens.event_log_window import EventLogWindow

    manager = pygame_gui.UIManager((1024, 768))
    rect = pygame.Rect(0, 0, 1024, 768)
    return EventLogWindow(
        rect,
        manager,
        events,
        window_manager=MagicMock(),
        replay_resolver=resolver,
        launch_replay_callback=launch_cb,
    )


def test_event_log_window_accepts_replay_resolver_and_launch_callback(
    pygame_init,
) -> None:
    """EventLogWindow.__init__ accepts the FEAT-26 kwargs without raising."""
    win = _make_event_log_window(
        [_combat_row("uuid")],
        resolver=MagicMock(),
        launch_cb=MagicMock(),
    )
    assert win is not None


def test_event_log_window_replay_click_invokes_resolver(pygame_init) -> None:
    """Clicking the row's Replay button calls resolver.resolve(replay_id).
    On a healthy lookup, the launch callback fires with the record."""
    from game.strategy.services.replay_resolver import ReplayLookup

    record = MagicMock()
    resolver = MagicMock()
    resolver.resolve.return_value = ReplayLookup(
        found=True, record=record, registry_drift=False
    )
    launch_cb = MagicMock()

    win = _make_event_log_window(
        [_combat_row("uuid-aaa")],
        resolver=resolver,
        launch_cb=launch_cb,
    )
    # Drive the click through the documented public seam: invoke the
    # internal click handler directly with row_index=0 (the e2e UI test
    # exercises the button → process_event path).
    win._handle_replay_click(0)

    resolver.resolve.assert_called_once_with("uuid-aaa")
    launch_cb.assert_called_once_with(record)


def test_event_log_window_replay_click_does_nothing_when_replay_id_missing(
    pygame_init,
) -> None:
    """Legacy combat rows without replay_id never reach the resolver."""
    resolver = MagicMock()
    launch_cb = MagicMock()
    legacy_row = {
        "category": "combat",
        "turn": 5,
        "message": "old",
        "details": {},
    }

    win = _make_event_log_window(
        [legacy_row], resolver=resolver, launch_cb=launch_cb
    )
    win._handle_replay_click(0)

    resolver.resolve.assert_not_called()
    launch_cb.assert_not_called()


def test_event_log_window_replay_click_without_data_source_is_noop(
    pygame_init,
) -> None:
    resolver = MagicMock()
    launch_cb = MagicMock()
    win = _make_event_log_window(
        [_combat_row("uuid")], resolver=resolver, launch_cb=launch_cb
    )
    win.data_source = None

    win._handle_replay_click(0)

    resolver.resolve.assert_not_called()
    launch_cb.assert_not_called()


def test_event_log_window_replay_click_without_resolver_is_noop(
    pygame_init,
) -> None:
    launch_cb = MagicMock()
    win = _make_event_log_window(
        [_combat_row("uuid")], resolver=None, launch_cb=launch_cb
    )

    win._handle_replay_click(0)

    launch_cb.assert_not_called()


def test_event_log_window_replay_click_missing_lookup_shows_reason_message(
    pygame_init,
) -> None:
    from game.strategy.services.replay_resolver import ReplayLookup

    resolver = MagicMock()
    resolver.resolve.return_value = ReplayLookup(
        found=False,
        reason="corrupt",
    )
    launch_cb = MagicMock()
    win = _make_event_log_window(
        [_combat_row("uuid-bad")], resolver=resolver, launch_cb=launch_cb
    )
    win._show_replay_message = MagicMock()

    win._handle_replay_click(0)

    win._show_replay_message.assert_called_once()
    title, message = win._show_replay_message.call_args.args
    assert title == "Replay unavailable"
    assert "corrupt" in message
    launch_cb.assert_not_called()


def test_event_log_window_replay_click_unknown_reason_uses_generic_message(
    pygame_init,
) -> None:
    from game.strategy.services.replay_resolver import ReplayLookup

    resolver = MagicMock()
    resolver.resolve.return_value = ReplayLookup(
        found=False,
        reason="evicted_by_policy",
    )
    win = _make_event_log_window(
        [_combat_row("uuid-missing")],
        resolver=resolver,
        launch_cb=MagicMock(),
    )
    win._show_replay_message = MagicMock()

    win._handle_replay_click(0)

    _, message = win._show_replay_message.call_args.args
    assert message == "Replay unavailable (evicted_by_policy)."


def test_event_log_window_replay_click_registry_drift_warns_and_launches(
    pygame_init,
) -> None:
    from game.strategy.services.replay_resolver import ReplayLookup

    record = MagicMock()
    resolver = MagicMock()
    resolver.resolve.return_value = ReplayLookup(
        found=True,
        record=record,
        registry_drift=True,
    )
    launch_cb = MagicMock()
    win = _make_event_log_window(
        [_combat_row("uuid-drift")], resolver=resolver, launch_cb=launch_cb
    )
    win._show_replay_message = MagicMock()

    win._handle_replay_click(0)

    win._show_replay_message.assert_called_once()
    title, message = win._show_replay_message.call_args.args
    assert title == "Replay version drift"
    assert "different components.json" in message
    launch_cb.assert_called_once_with(record)


# ---------------------------------------------------------------------------
# PROJ-368 — Verification status gating (r002 status table)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "status",
    [None, "PENDING", "PASSED", "FAILED", "ERROR",
     "SKIPPED_QUEUE_FULL", "SKIPPED_DISABLED"],
)
def test_event_log_window_replay_click_launches_for_any_verification_status(
    pygame_init, status,
) -> None:
    """PROJ-368 (post-r001 discussion): verification_status is a diagnostic
    signal, NOT a launch gate. The Event Log launches whenever the resolver
    returns ``found=True``, regardless of verification outcome.

    The prior r002 hard-block on FAILED/ERROR was wrong: it prevented the
    user from ever seeing a captured battle if the headless determinism
    re-run diverged. Verification mismatch ≠ replay unwatchable.
    """
    from game.strategy.services.replay_resolver import ReplayLookup

    record = MagicMock()
    resolver = MagicMock()
    resolver.resolve.return_value = ReplayLookup(
        found=True,
        record=record,
        registry_drift=False,
        verification_status=status,
    )
    launch_cb = MagicMock()
    win = _make_event_log_window(
        [_combat_row(f"uuid-{status or 'none'}")],
        resolver=resolver,
        launch_cb=launch_cb,
    )

    win._handle_replay_click(0)

    launch_cb.assert_called_once_with(record)
