"""
Tests for BuildQueueDragHandler multi-queue support (PROJ-69 Phase 4).

Tests cover:
- Drag reorder works in single-select mode (active_queue_source)
- Drag operations disabled in multi-select mode
- Mouse down/motion/up use active_queue_source's construction_queue
"""

import pytest
import pygame
from unittest.mock import MagicMock
from game.ui.panels.build_queue_drag_handler import BuildQueueDragHandler
from game.strategy.data.build_queue_source import BuildQueueSource


@pytest.fixture
def drag_handler(single_queue_source):
    """Create a BuildQueueDragHandler for testing.

    PROJ-393 (LEG-03-006) made on_remove_from_queue a required arg and
    deleted the in-place ``construction_queue.pop(idx)`` legacy fallback.
    Production wires the callback to a command dispatcher that ultimately
    removes the item; in tests we wire it to a closure that pops directly
    from the fixture queue, so "item gets removed when callback fires"
    is preserved as the contract under test.
    """
    portrait_loader = MagicMock()
    portrait_loader.load_design_portrait.return_value = None
    portrait_loader.load_queue_item_portrait.return_value = None

    design_catalog = MagicMock()
    design_catalog.scan_designs.return_value = []

    def _remove_from_queue(idx: int) -> None:
        if 0 <= idx < len(single_queue_source.construction_queue):
            single_queue_source.construction_queue.pop(idx)

    handler = BuildQueueDragHandler(
        portrait_loader=portrait_loader,
        design_catalog=design_catalog,
        on_add_to_queue=MagicMock(),
        on_refresh_queue=MagicMock(),
        on_refresh_design_report=MagicMock(),
        on_remove_from_queue=_remove_from_queue,
    )
    return handler


@pytest.fixture
def single_queue_source():
    """Create a BuildQueueSource for single-select mode testing."""
    queue = [
        {"design_id": "item_A", "type": "ship", "turns_remaining": 3},
        {"design_id": "item_B", "type": "ship", "turns_remaining": 5},
    ]
    return BuildQueueSource(
        queue_id="test_queue",
        display_name="Test Queue",
        owner_entity=MagicMock(),
        construction_queue=queue,
        can_build_ships=True,
        can_build_complexes=True,
        context_type="planet",
    )


# --- Multi-select disable tests ---

def test_mouse_down_returns_false_in_multi_select(drag_handler):
    """Test that handle_mouse_down returns False in multi-select mode."""

    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(100, 100))
    items_scrollable = MagicMock()
    items_scrollable.get_container.return_value.elements = []

    result = drag_handler.handle_mouse_down(
        event, items_scrollable, [], None, "ship",
        multi_select_active=True
    )
    assert result is False



def test_mouse_motion_returns_false_in_multi_select(drag_handler):
    """Test that handle_mouse_motion returns False in multi-select mode."""

    event = pygame.event.Event(pygame.MOUSEMOTION, pos=(100, 100),
                                rel=(5, 5), buttons=(1, 0, 0))
    result = drag_handler.handle_mouse_motion(
        event, [], multi_select_active=True
    )
    assert result is False



def test_mouse_up_returns_none_in_multi_select(drag_handler):
    """Test that handle_mouse_up returns None and clears drag in multi-select."""

    event = pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(100, 100))
    build_queue_panel = MagicMock()
    queue_scrollable = MagicMock()

    result = drag_handler.handle_mouse_up(
        event, build_queue_panel, queue_scrollable, [],
        multi_select_active=True
    )
    assert result is None



# --- Single-select queue source tests ---

def test_mouse_motion_pops_from_queue_source(drag_handler, single_queue_source):
    """Test that dragging from queue pops from the active queue source's queue."""


    # Set up pending drag state (simulating mouse down on queue item)
    drag_handler.drag_start_pos = (100, 100)
    drag_handler._pending_queue_index = 0

    # Motion event exceeding threshold
    event = pygame.event.Event(pygame.MOUSEMOTION, pos=(120, 120),
                                rel=(20, 20), buttons=(1, 0, 0))

    result = drag_handler.handle_mouse_motion(
        event, single_queue_source.construction_queue,
        multi_select_active=False
    )

    assert result is True
    assert drag_handler.dragged_item is not None
    assert drag_handler.dragged_item["design_id"] == "item_A"
    # Item should be popped from queue
    assert len(single_queue_source.construction_queue) == 1
    assert single_queue_source.construction_queue[0]["design_id"] == "item_B"




def test_mouse_up_drops_into_queue_source(drag_handler, single_queue_source):
    """Test that dropping calls on_add_to_queue with correct data."""


    # Set up dragged item
    drag_handler.dragged_item = {
        "design_id": "new_ship",
        "name": "New Ship",
        "category": "ship",
        "portrait": None,
    }

    # Build queue panel with rect that contains the drop position
    build_queue_panel = MagicMock()
    build_queue_panel.rect = pygame.Rect(500, 0, 400, 800)

    queue_scrollable = MagicMock()
    queue_scrollable.get_abs_rect.return_value = pygame.Rect(500, 50, 380, 700)

    event = pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(600, 100))

    drag_handler.handle_mouse_up(
        event, build_queue_panel, queue_scrollable,
        single_queue_source.construction_queue,
        multi_select_active=False
    )

    # on_add_to_queue should be called
    drag_handler.on_add_to_queue.assert_called_once()
    call_args = drag_handler.on_add_to_queue.call_args
    assert call_args[0][0] == "new_ship"  # design_id

    # Drag should be cleared
    assert drag_handler.dragged_item is None


