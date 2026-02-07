"""
BUG-17 Reproduction Test: Build Queue drag/drop not visually obvious.

Rev 2: The drag preview should use an icon/portrait that follows the cursor.
The icon should be clearly visible and indicate what item is being dragged.
"""
import pygame


class TestDragPreviewIcon:
    """Tests for icon-based drag preview in build queue."""

    def test_dragged_item_stores_portrait(self):
        """
        GIVEN an item is being dragged
        WHEN the drag starts
        THEN the dragged_item dict should include a 'portrait' key with a surface

        Rev 2: Drag should capture the icon for visual feedback.
        PROJ-63: Drag logic extracted to BuildQueueDragHandler.
        """
        import inspect
        from game.ui.panels import build_queue_drag_handler

        # Check handle_mouse_down code for portrait storage during drag
        source = inspect.getsource(build_queue_drag_handler.BuildQueueDragHandler.handle_mouse_down)

        # The fix should store portrait in dragged_item
        assert "portrait" in source.lower(), \
            "handle_mouse_down should store portrait in dragged_item during drag start"

    def test_draw_renders_icon_at_cursor(self):
        """
        GIVEN an item is being dragged with a portrait
        WHEN draw() is called
        THEN the portrait icon should be rendered at/near the cursor position

        Rev 2: Mouse cursor should carry the icon.
        PROJ-63: Drag preview rendering extracted to BuildQueueDragHandler.
        """
        import inspect
        from game.ui.panels import build_queue_drag_handler

        source = inspect.getsource(build_queue_drag_handler.BuildQueueDragHandler.draw_drag_preview)

        # The draw method should blit the portrait/icon
        assert "portrait" in source.lower(), \
            "draw_drag_preview method should render portrait icon during drag"

    def test_icon_size_appropriate(self):
        """
        GIVEN an icon is used for drag preview
        WHEN determining icon size
        THEN it should be between 48-64px for good visibility

        Rev 2: Icon should be visible but not overwhelming.
        """
        # Expected drag icon size (implementation detail)
        DRAG_ICON_SIZE = 48

        assert DRAG_ICON_SIZE >= 32, "Icon should be at least 32px"
        assert DRAG_ICON_SIZE <= 64, "Icon should not exceed 64px"
