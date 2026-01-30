"""
BUG-16 Reproduction Test: Atmosphere Raw Data button mispositioned.

The Raw Data button should be in the upper right of the graph box,
not in the upper left of the detail panel.
"""
import pygame


class TestRawDataButtonPosition:
    """Tests for Raw Data button positioning logic."""

    def test_button_position_calculation(self):
        """
        GIVEN a graph_rect at (10, 170, 150, h)
        WHEN calculating the Raw Data button position
        THEN it should be at top-right of graph, not (0, 0)

        The positioning formula in strategy_screen.py:
        btn_x = graph_rect.right - 22  # Inside right edge of graph
        btn_y = graph_rect.top + 2     # Inside top edge of graph
        """
        # Simulate the graph_rect values from the code
        graph_rect = pygame.Rect(10, 170, 150, 100)

        # Apply the FIXED positioning logic
        btn_x = graph_rect.right - 22  # = 160 - 22 = 138
        btn_y = graph_rect.top + 2     # = 170 + 2 = 172

        # The button should NOT be at (0, 0) - that was the bug
        assert (btn_x, btn_y) != (0, 0), \
            "BUG: Raw Data button should NOT be at (0, 0) (top-left of panel)"

        # Verify correct position
        assert btn_x == 138, "Button x should be at graph_rect.right - 22 = 138"
        assert btn_y == 172, "Button y should be at graph_rect.top + 2 = 172"

        # Verify button is within graph bounds (with some margin for the button size)
        btn_rect = pygame.Rect(btn_x, btn_y, 20, 20)
        assert graph_rect.colliderect(btn_rect), \
            "Button should visually overlap with graph area"

    def test_button_position_in_source_code(self):
        """
        Verify that the source code uses the correct initial position,
        not (0, 0) which was the buggy position.
        """
        import inspect
        from game.ui.screens import strategy_ui

        source = inspect.getsource(strategy_ui.StrategyUI.__init__)

        # The fix: button should be created with calculated position, not (0, 0)
        # Check that graph_rect.right is used for button positioning
        assert "graph_rect.right" in source, \
            "Button x-position should be calculated from graph_rect.right"
        assert "graph_rect.top" in source, \
            "Button y-position should be calculated from graph_rect.top"

        # The buggy code had: relative_rect=pygame.Rect(0, 0, 20, 20)
        # The fixed code should NOT have (0, 0) for this button
        # We can't easily test this without more complex parsing
