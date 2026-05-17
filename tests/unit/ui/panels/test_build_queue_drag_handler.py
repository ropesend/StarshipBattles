"""Characterization tests for ``BuildQueueDragHandler`` (PROJ-338 Phase 1).

Pin the drag-handler state machine. The handler accepts pygame events
directly and dispatches via injected callbacks; these tests synthesize
``pygame.event.Event`` objects and stub the scrollable / virtual-table /
build-queue-panel surfaces with ``MagicMock``s shaped to the production
contract (per PROJ-338 D-001).

The drag handler is the highest-priority gap because it is the only
state machine in the build-queue UI without unit-level coverage.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pygame
import pytest

from game.ui.panels.build_queue_drag_handler import BuildQueueDragHandler


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _pygame_init():
    """Init pygame once per test (event constructor needs it)."""
    pygame.init()
    yield


def _make_design(design_id: str, name: str = None):
    """Plain object stub for a DesignMetadata row.

    ``MagicMock`` would auto-create ``design_id``/``name`` for any attribute
    access, which makes the design-list scan loop incorrectly match every
    element. A plain class with explicit attributes avoids that.
    """
    obj = MagicMock(spec=["design_id", "name"])
    obj.design_id = design_id
    obj.name = name or design_id
    return obj


def _make_scrollable(elements):
    """Stub for an ``items_scrollable`` UIScrollingContainer.

    Production reads ``items_scrollable.get_container().elements``. Each
    element either has ``design_id`` (clickable) or doesn't.
    """
    container = MagicMock()
    container.elements = elements
    scrollable = MagicMock()
    scrollable.get_container.return_value = container
    return scrollable


def _make_design_button(design_id: str, abs_rect: pygame.Rect):
    """Stub for a UIPanel that wraps a design button."""
    btn = MagicMock(spec=["design_id", "get_abs_rect"])
    btn.design_id = design_id
    btn.get_abs_rect.return_value = abs_rect
    return btn


def _make_handler(*, with_remove_callback: bool = True):
    """Build a handler with all callbacks as MagicMocks.

    PROJ-393 made ``on_remove_from_queue`` a required arg; the
    ``with_remove_callback=False`` flavor that legacy tests used to exercise
    the construction-queue direct-pop fallback is gone, so the kwarg now
    just toggles whether the callback mock is attached vs replaced. Kept
    the kwarg for ABI parity with existing call sites that pass True.
    """
    portrait_loader = MagicMock()
    portrait_loader.load_design_portrait.return_value = pygame.Surface((48, 48))
    portrait_loader.load_queue_item_portrait.return_value = pygame.Surface((48, 48))

    design_catalog = MagicMock()
    design_catalog.scan_designs.return_value = []

    on_add = MagicMock()
    on_refresh_q = MagicMock()
    on_refresh_dr = MagicMock()
    on_remove = MagicMock()

    handler = BuildQueueDragHandler(
        portrait_loader=portrait_loader,
        design_catalog=design_catalog,
        on_add_to_queue=on_add,
        on_refresh_queue=on_refresh_q,
        on_refresh_design_report=on_refresh_dr,
        on_remove_from_queue=on_remove,
    )
    return handler


def _md_event(button: int, pos: tuple) -> pygame.event.Event:
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": button, "pos": pos})


def _mu_event(button: int, pos: tuple) -> pygame.event.Event:
    return pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": button, "pos": pos})


def _mm_event(pos: tuple, buttons=(1, 0, 0)) -> pygame.event.Event:
    return pygame.event.Event(pygame.MOUSEMOTION, {"pos": pos, "buttons": buttons, "rel": (0, 0)})


# ===========================================================================
# A.1 — Constructor + state defaults
# ===========================================================================


class TestConstructorDefaults:
    def test_constructor_initial_state_no_drag(self):
        h = _make_handler()
        assert h.is_dragging is False
        assert h.dragged_item is None
        assert h.selected_design is None
        assert h._pending_queue_index is None
        assert h.drag_threshold == 10
        assert h.drag_start_pos is None

    def test_reset_state_clears_selected_design(self):
        """PROJ-410 Task 1.1: locking regression.

        ``reset_state()`` is called from ``BuildQueueScreen.open_for_yard``
        when the screen is reused across yard switches (PROJ-376). The
        production reset at ``build_queue_drag_handler.py:101`` clears
        ``selected_design`` so the next yard does not inherit the prior
        yard's selection (e.g., the "Add to Queue" hotkey would otherwise
        add the previous yard's design).

        This test locks that behavior — if a future refactor drops the
        ``self.selected_design = None`` line, this test fails.
        """
        h = _make_handler()
        h.selected_design = "DSN-prior-yard"

        h.reset_state()

        assert h.selected_design is None, (
            "reset_state() must clear selected_design (PROJ-410 lock). "
            "If this fails, check build_queue_drag_handler.py:101."
        )

    def test_reset_state_clears_all_five_drag_fields(self):
        """PROJ-410 Task 1.1: locking regression for the full reset_state contract.

        The docstring at ``build_queue_drag_handler.py:91-95`` lists 5
        fields that must be cleared. Lock all of them so a partial
        future regression on any one is caught.
        """
        h = _make_handler()
        h.dragged_item = {"design_id": "X"}
        h.drag_preview = pygame.Surface((10, 10))
        h.drag_start_pos = (5, 5)
        h._pending_queue_index = 2
        h.selected_design = "DSN-x"

        h.reset_state()

        assert h.dragged_item is None
        assert h.drag_preview is None
        assert h.drag_start_pos is None
        assert h._pending_queue_index is None
        assert h.selected_design is None

    def test_drag_from_queue_invokes_remove_callback_when_provided(self):
        """When constructed WITH on_remove_from_queue, a queue-pickup drag
        dispatches the callback with the picked-up index instead of
        mutating ``construction_queue`` in place.

        PROJ-346 strengthening: was a constructor tautology
        (``h._on_remove_from_queue is not None`` after passing a callback
        in __init__). Now pin the production branch at
        build_queue_drag_handler.py:193-194 — the actual reason the
        callback is wired.
        """
        h = _make_handler(with_remove_callback=True)
        # Seed pending-drag state directly so handle_mouse_motion's threshold
        # check has something to act on (production normally seeds this in
        # handle_mouse_down on the queue side; we test the motion branch
        # in isolation).
        h.drag_start_pos = (50, 50)
        h._pending_queue_index = 0

        queue = [{'design_id': 'Frigate', 'type': 'ship', 'turns_remaining': 3}]
        # Move past the drag threshold (10).
        result = h.handle_mouse_motion(
            _mm_event(pos=(70, 70), buttons=(1, 0, 0)),
            queue,
            multi_select_active=False,
        )

        assert result is True
        # Callback received the picked-up index.
        h._on_remove_from_queue.assert_called_once_with(0)
        # Production branch: when callback exists, the queue is NOT
        # mutated in-place — removal is the caller's responsibility.
        assert queue == [{'design_id': 'Frigate', 'type': 'ship', 'turns_remaining': 3}]

    # PROJ-393: deleted test_drag_from_queue_falls_back_to_direct_pop_without_callback
    # alongside the legacy direct-pop fallback in build_queue_drag_handler.py.
    # on_remove_from_queue is now a required constructor arg.


# ===========================================================================
# A.2 — handle_mouse_down design-list path
# ===========================================================================


class TestMouseDownDesignList:
    def test_mouse_down_right_button_returns_false(self):
        h = _make_handler()
        scrollable = _make_scrollable([])
        result = h.handle_mouse_down(
            _md_event(button=3, pos=(50, 50)),
            scrollable,
            MagicMock(),
            [],
            "ship",
        )
        assert result is False
        assert h.is_dragging is False

    def test_mouse_down_multi_select_active_returns_false_no_state_change(self):
        h = _make_handler()
        scrollable = _make_scrollable([])
        result = h.handle_mouse_down(
            _md_event(button=1, pos=(50, 50)),
            scrollable,
            MagicMock(),
            [],
            "ship",
            multi_select_active=True,
        )
        assert result is False
        assert h.selected_design is None
        assert h.dragged_item is None

    def test_mouse_down_on_design_button_starts_drag_with_portrait(self):
        h = _make_handler()
        design = _make_design("DSN-1", name="Frigate")
        h.design_catalog.scan_designs.return_value = [design]

        btn = _make_design_button("DSN-1", pygame.Rect(40, 40, 100, 30))
        scrollable = _make_scrollable([btn])
        vt = MagicMock()
        vt.handle_click.return_value = -1

        result = h.handle_mouse_down(
            _md_event(button=1, pos=(50, 50)),
            scrollable,
            vt,
            [],
            "ship",
        )
        assert result is True
        assert h.selected_design == "DSN-1"
        assert h.dragged_item is not None
        assert h.dragged_item["design_id"] == "DSN-1"
        assert h.dragged_item["name"] == "Frigate"
        assert h.dragged_item["category"] == "ship"
        assert h.dragged_item["portrait"] is not None
        h.on_refresh_design_report.assert_called_once_with("DSN-1")

    def test_mouse_down_on_design_button_with_no_matching_design_skips_dragged_item(self):
        h = _make_handler()
        # scan_designs returns nothing matching the button's design_id
        h.design_catalog.scan_designs.return_value = []
        btn = _make_design_button("DSN-MISSING", pygame.Rect(40, 40, 100, 30))
        scrollable = _make_scrollable([btn])
        vt = MagicMock()
        vt.handle_click.return_value = -1

        result = h.handle_mouse_down(
            _md_event(button=1, pos=(50, 50)),
            scrollable,
            vt,
            [],
            "ship",
        )
        assert result is True
        assert h.selected_design == "DSN-MISSING"
        h.on_refresh_design_report.assert_called_once_with("DSN-MISSING")
        assert h.dragged_item is None

    def test_mouse_down_on_design_button_uses_48px_portrait_for_cursor(self):
        h = _make_handler()
        design = _make_design("DSN-2")
        h.design_catalog.scan_designs.return_value = [design]
        btn = _make_design_button("DSN-2", pygame.Rect(40, 40, 100, 30))
        scrollable = _make_scrollable([btn])
        vt = MagicMock()
        vt.handle_click.return_value = -1

        h.handle_mouse_down(
            _md_event(button=1, pos=(50, 50)),
            scrollable,
            vt,
            [],
            "ship",
        )
        h.portrait_loader.load_design_portrait.assert_called_once_with(design, 48)

    def test_mouse_down_no_collision_returns_false_no_state_change(self):
        h = _make_handler()
        # Button exists but click is far away
        btn = _make_design_button("DSN-1", pygame.Rect(0, 0, 10, 10))
        scrollable = _make_scrollable([btn])
        vt = MagicMock()
        vt.handle_click.return_value = -1

        result = h.handle_mouse_down(
            _md_event(button=1, pos=(500, 500)),
            scrollable,
            vt,
            [],
            "ship",
        )
        assert result is False
        assert h.selected_design is None
        assert h._pending_queue_index is None


# ===========================================================================
# A.3 — handle_mouse_down queue-row path
# ===========================================================================


class TestMouseDownQueueRow:
    def test_mouse_down_on_queue_row_sets_pending_index_no_drag_yet(self):
        h = _make_handler()
        scrollable = _make_scrollable([])  # no design buttons
        vt = MagicMock()
        vt.handle_click.return_value = 2  # row 2 was clicked

        result = h.handle_mouse_down(
            _md_event(button=1, pos=(100, 200)),
            scrollable,
            vt,
            [{"design_id": "A"}, {"design_id": "B"}, {"design_id": "C"}],
            "ship",
        )
        assert result is True
        assert h._pending_queue_index == 2
        assert h.drag_start_pos == (100, 200)
        assert h.dragged_item is None  # not actually dragging yet


# ===========================================================================
# A.4 — handle_mouse_motion threshold
# ===========================================================================


class TestMouseMotionThreshold:
    def _seed_pending(self, h, idx=0, start=(100, 100)):
        h._pending_queue_index = idx
        h.drag_start_pos = start

    def test_motion_below_threshold_no_drag_started(self):
        h = _make_handler(with_remove_callback=True)
        self._seed_pending(h)
        queue = [{"design_id": "A", "type": "ship", "turns_remaining": 3}]
        result = h.handle_mouse_motion(_mm_event((103, 104)), queue)
        assert result is False
        assert h.dragged_item is None
        # callback NOT fired
        h._on_remove_from_queue.assert_not_called()

    def test_motion_above_threshold_starts_drag_pops_via_callback_when_present(self):
        h = _make_handler(with_remove_callback=True)
        self._seed_pending(h, idx=0)
        queue = [{"design_id": "A", "type": "ship", "turns_remaining": 3}]
        # Motion 11px past threshold
        result = h.handle_mouse_motion(_mm_event((112, 100)), queue)
        assert result is True
        h._on_remove_from_queue.assert_called_once_with(0)
        # Production does NOT mutate the queue when callback is present
        assert len(queue) == 1
        assert h.dragged_item is not None
        assert h.dragged_item["design_id"] == "A"

    # PROJ-393: deleted test_motion_above_threshold_legacy_pops_directly_when_no_callback
    # alongside the production legacy fallback (on_remove_from_queue is now required).

    def test_motion_above_threshold_with_invalid_index_skips_pop(self):
        h = _make_handler(with_remove_callback=True)
        self._seed_pending(h, idx=5)  # out-of-range
        queue = [{"design_id": "A"}]
        result = h.handle_mouse_motion(_mm_event((112, 100)), queue)
        assert result is True  # threshold path executed
        h._on_remove_from_queue.assert_not_called()
        # Pending state still cleared
        assert h._pending_queue_index is None
        assert h.drag_start_pos is None
        # No drag started because guard skipped the pop branch
        assert h.dragged_item is None

    def test_motion_multi_select_active_returns_false_no_drag_started(self):
        h = _make_handler()
        self._seed_pending(h)
        result = h.handle_mouse_motion(
            _mm_event((200, 200)),
            [{"design_id": "A"}],
            multi_select_active=True,
        )
        assert result is False
        assert h.dragged_item is None

    def test_motion_button_not_pressed_returns_false(self):
        h = _make_handler(with_remove_callback=True)
        self._seed_pending(h)
        # buttons[0]=0 means LMB not held
        result = h.handle_mouse_motion(_mm_event((200, 200), buttons=(0, 0, 0)), [{"design_id": "A"}])
        assert result is False
        assert h.dragged_item is None

    def test_motion_clears_pending_state_after_drag_starts(self):
        h = _make_handler(with_remove_callback=True)
        self._seed_pending(h, idx=0)
        h.handle_mouse_motion(_mm_event((112, 100)), [{"design_id": "A"}])
        assert h._pending_queue_index is None
        assert h.drag_start_pos is None

    def test_motion_dragged_item_carries_source_queue_marker(self):
        h = _make_handler(with_remove_callback=True)
        self._seed_pending(h, idx=0)
        h.handle_mouse_motion(_mm_event((112, 100)), [{"design_id": "A", "type": "complex"}])
        assert h.dragged_item["source"] == "queue"
        assert h.dragged_item["category"] == "complex"


# ===========================================================================
# A.5 — handle_mouse_up drop
# ===========================================================================


def _make_panel(rect: pygame.Rect):
    panel = MagicMock()
    panel.rect = rect
    return panel


def _make_virtual_table(list_panel_top: int = 100, row_height: int = 30):
    """VirtualTable stub: ``_list_view_panel.get_abs_rect().top`` and ``_row_height``."""
    list_panel = MagicMock()
    list_panel.get_abs_rect.return_value = pygame.Rect(0, list_panel_top, 200, 400)
    vt = MagicMock()
    vt._list_view_panel = list_panel
    vt._row_height = row_height
    return vt


class TestMouseUpDrop:
    def test_mouse_up_right_button_returns_none_no_state_change(self):
        h = _make_handler()
        h.dragged_item = {"design_id": "A", "category": "ship"}
        result = h.handle_mouse_up(_mu_event(button=3, pos=(0, 0)), _make_panel(pygame.Rect(0, 0, 200, 200)), _make_virtual_table(), [])
        assert result is None
        # Drag state still set (right-button is a no-op)
        assert h.dragged_item is not None

    def test_mouse_up_click_without_drag_returns_pending_index(self):
        h = _make_handler()
        h._pending_queue_index = 3
        h.dragged_item = None
        panel = _make_panel(pygame.Rect(0, 0, 200, 200))
        result = h.handle_mouse_up(_mu_event(1, (50, 50)), panel, _make_virtual_table(), [])
        assert result == 3
        h.on_refresh_queue.assert_called_once()
        assert h._pending_queue_index is None

    def test_mouse_up_drop_inside_panel_calls_add_to_queue_with_calculated_index(self):
        h = _make_handler()
        h.dragged_item = {"design_id": "A", "category": "ship", "turns": 2, "source": "queue"}
        panel = _make_panel(pygame.Rect(0, 0, 500, 500))
        vt = _make_virtual_table(list_panel_top=100, row_height=30)
        # Click at y=190 → rel_y=90 → 90//30 = 3
        h.handle_mouse_up(_mu_event(1, (250, 190)), panel, vt, [{"design_id": "X"}, {"design_id": "Y"}])
        h.on_add_to_queue.assert_called_once()
        args = h.on_add_to_queue.call_args[0]
        assert args[0] == "A"  # design_id
        assert args[1] == 2  # turns
        assert args[2] == "ship"  # category
        # estimated_idx=3, queue length=2 → clamped to 2
        assert args[3] == 2

    def test_mouse_up_drop_inside_clamps_index_at_queue_length(self):
        h = _make_handler()
        h.dragged_item = {"design_id": "A", "category": "ship", "turns": None, "source": "queue"}
        panel = _make_panel(pygame.Rect(0, 0, 500, 500))
        # Place the list panel near the top with small row height so a
        # click near the bottom of the build-queue panel produces an
        # estimated_idx larger than the queue length.
        vt = _make_virtual_table(list_panel_top=0, row_height=10)
        # Click at y=400 inside the (0..500) panel → rel_y=400 → idx=40,
        # queue length=2 → clamp to 2.
        h.handle_mouse_up(_mu_event(1, (10, 400)), panel, vt, [{"design_id": "X"}, {"design_id": "Y"}])
        args = h.on_add_to_queue.call_args[0]
        assert args[3] == 2

    def test_mouse_up_drop_inside_clamps_index_at_zero(self):
        h = _make_handler()
        h.dragged_item = {"design_id": "A", "category": "ship", "turns": None, "source": "queue"}
        panel = _make_panel(pygame.Rect(0, 0, 500, 500))
        vt = _make_virtual_table(list_panel_top=500, row_height=10)
        # rel_y = -490 → estimated_idx negative → max(0, ...) = 0
        h.handle_mouse_up(_mu_event(1, (10, 10)), panel, vt, [{"design_id": "X"}])
        args = h.on_add_to_queue.call_args[0]
        assert args[3] == 0

    def test_mouse_up_drop_outside_panel_drops_item_silently_when_from_queue(self):
        h = _make_handler()
        h.dragged_item = {"design_id": "A", "category": "ship", "source": "queue", "turns": None}
        # Panel only covers (0,0,100,100); click at (500,500) is outside
        panel = _make_panel(pygame.Rect(0, 0, 100, 100))
        h.handle_mouse_up(_mu_event(1, (500, 500)), panel, _make_virtual_table(), [])
        h.on_add_to_queue.assert_not_called()
        # came_from_queue=True → refresh fires
        h.on_refresh_queue.assert_called()

    def test_mouse_up_drop_outside_panel_no_refresh_when_from_design_list(self):
        h = _make_handler()
        h.dragged_item = {"design_id": "A", "category": "ship", "turns": None}  # no 'source'
        panel = _make_panel(pygame.Rect(0, 0, 100, 100))
        h.handle_mouse_up(_mu_event(1, (500, 500)), panel, _make_virtual_table(), [])
        h.on_add_to_queue.assert_not_called()
        h.on_refresh_queue.assert_not_called()

    def test_mouse_up_clears_dragged_item_state_after_drop(self):
        h = _make_handler()
        h.dragged_item = {"design_id": "A", "category": "ship", "turns": None}
        panel = _make_panel(pygame.Rect(0, 0, 500, 500))
        h.handle_mouse_up(_mu_event(1, (50, 50)), panel, _make_virtual_table(), [])
        assert h.dragged_item is None

    def test_mouse_up_multi_select_clears_all_pending_state_returns_none(self):
        h = _make_handler()
        h._pending_queue_index = 1
        h.drag_start_pos = (10, 10)
        h.dragged_item = {"design_id": "A"}
        result = h.handle_mouse_up(
            _mu_event(1, (0, 0)),
            _make_panel(pygame.Rect(0, 0, 200, 200)),
            _make_virtual_table(),
            [],
            multi_select_active=True,
        )
        assert result is None
        assert h._pending_queue_index is None
        assert h.drag_start_pos is None
        assert h.dragged_item is None


# ===========================================================================
# A.6 — draw_drag_preview
# ===========================================================================


class TestDrawDragPreview:
    def test_draw_preview_no_drag_no_blits(self):
        h = _make_handler()
        screen = MagicMock()
        h.draw_drag_preview(screen)
        screen.blit.assert_not_called()

    def test_draw_preview_with_portrait_blits_shadow_and_icon_and_border(self, monkeypatch):
        h = _make_handler()
        h.dragged_item = {"design_id": "A", "category": "ship", "portrait": pygame.Surface((48, 48))}
        monkeypatch.setattr("pygame.mouse.get_pos", lambda: (100, 100))

        screen = MagicMock()
        # Capture pygame.draw.rect to count border draws
        rect_calls = []
        monkeypatch.setattr("pygame.draw.rect", lambda *args, **kw: rect_calls.append((args, kw)))

        h.draw_drag_preview(screen)
        # 2 blits: shadow + portrait icon
        assert screen.blit.call_count == 2
        # 1 border rect
        assert len(rect_calls) == 1

    def test_draw_preview_without_portrait_uses_color_map_fallback_for_known_category(self, monkeypatch):
        h = _make_handler()
        h.dragged_item = {"design_id": "A", "category": "complex", "portrait": None}
        monkeypatch.setattr("pygame.mouse.get_pos", lambda: (10, 10))
        rect_calls = []
        monkeypatch.setattr("pygame.draw.rect", lambda *args, **kw: rect_calls.append((args, kw)))
        screen = MagicMock()
        h.draw_drag_preview(screen)
        # 1 blit (placeholder square), 1 border
        assert screen.blit.call_count == 1
        assert len(rect_calls) == 1

    def test_draw_preview_unknown_category_falls_back_to_text_dim(self, monkeypatch):
        h = _make_handler()
        h.dragged_item = {"design_id": "A", "category": "unknownX", "portrait": None}
        monkeypatch.setattr("pygame.mouse.get_pos", lambda: (10, 10))
        rect_calls = []
        monkeypatch.setattr("pygame.draw.rect", lambda *args, **kw: rect_calls.append((args, kw)))
        screen = MagicMock()
        # Should not raise; falls back to TEXT_DIM color
        h.draw_drag_preview(screen)
        assert screen.blit.call_count == 1


# ===========================================================================
# Review-4 follow-up: design-button drag motion suppression (missing transition)
# ===========================================================================


class TestMouseMotionDesignButtonDragSuppressed:
    def test_handle_mouse_motion_returns_false_during_design_button_drag_due_to_drag_start_pos_none(self):
        """State-machine gap pinned: design-button drags set
        `dragged_item` directly in `handle_mouse_down` (no
        `drag_start_pos` is recorded), so any subsequent MOUSEMOTION
        events return False without entering the threshold-check path.
        Queue-row drags, by contrast, set both `drag_start_pos` AND
        `_pending_queue_index` and DO process motion.

        This pins the production guard at build_queue_drag_handler.py:176:
            `if not (event.buttons[0] and self.drag_start_pos and ...)`
        which silently skips the design-button drag path.
        """
        h = _make_handler()
        # Simulate the post-mousedown state from the design-button path:
        # dragged_item populated, but drag_start_pos / _pending_queue_index
        # remain at their constructor defaults (None).
        h.dragged_item = {
            'design_id': 'frigate', 'name': 'Frigate',
            'category': 'ship', 'portrait': pygame.Surface((48, 48)),
        }
        assert h.drag_start_pos is None
        assert h._pending_queue_index is None

        # Motion well past the threshold — would normally start a drag if
        # this were the queue-row path.
        result = h.handle_mouse_motion(
            _mm_event(pos=(500, 500), buttons=(1, 0, 0)),
            construction_queue=[],
        )

        assert result is False
        # Critically: dragged_item is NOT re-built or modified by motion.
        assert h.dragged_item['design_id'] == 'frigate'

