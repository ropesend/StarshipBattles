"""Tests for UI widget classes."""
import pygame

from game.ui.widgets import Button, Label, Slider


class TestButton:
    """Test Button widget."""

    def test_button_initialization(self):
        """Button should initialize with correct rect."""
        btn = Button(10, 20, 100, 50, "Test", None)

        assert btn.rect.x == 10
        assert btn.rect.y == 20
        assert btn.rect.w == 100
        assert btn.rect.h == 50

    def test_button_stores_callback(self):
        """Button should store its callback."""
        cb_called = [False]
        def callback():
            cb_called[0] = True

        btn = Button(0, 0, 100, 50, "Test", callback)

        assert btn.callback == callback

    def test_button_hover_detection(self):
        """Hover state should change on mouse motion."""
        btn = Button(0, 0, 100, 50, "Test", None)

        # Motion inside
        event = pygame.event.Event(pygame.MOUSEMOTION, {'pos': (50, 25)})
        btn.handle_event(event)

        assert btn.is_hovered is True

        # Motion outside
        event = pygame.event.Event(pygame.MOUSEMOTION, {'pos': (200, 200)})
        btn.handle_event(event)

        assert btn.is_hovered is False

    def test_button_click_fires_callback(self):
        """Click on hovered button should fire callback."""
        cb_called = [False]
        def callback():
            cb_called[0] = True

        btn = Button(0, 0, 100, 50, "Test", callback)

        # First hover over button
        motion_event = pygame.event.Event(pygame.MOUSEMOTION, {'pos': (50, 25)})
        btn.handle_event(motion_event)

        # Then click
        click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (50, 25)})
        btn.handle_event(click_event)

        assert cb_called[0] is True


class TestLabel:
    """Test Label widget."""

    def test_label_initialization(self):
        """Label should initialize with correct position and text."""
        lbl = Label(10, 20, "Hello World")

        assert lbl.pos == (10, 20)
        assert lbl.text == "Hello World"

    def test_label_update_text(self):
        """update_text should change label text."""
        lbl = Label(0, 0, "Original")

        lbl.update_text("New Text")

        assert lbl.text == "New Text"

    def test_label_custom_color(self):
        """Label should accept custom color."""
        lbl = Label(0, 0, "Test", color=(255, 0, 0))

        assert lbl.color == (255, 0, 0)


class TestSlider:
    """Test Slider widget."""

    def test_slider_initialization(self):
        """Slider should initialize with correct values."""
        slider = Slider(0, 0, 100, 20, 0, 100, 50, None)

        assert slider.min_val == 0
        assert slider.max_val == 100
        assert slider.val == 50

    def test_slider_value_update(self):
        """update_val should change slider value."""
        slider = Slider(0, 0, 100, 20, 0, 100, 50, None)

        # Drag to middle of slider
        slider.update_val(50)

        # Value should have updated
        assert slider.val is not None

    def test_slider_callback_fires(self):
        """Slider should fire callback on value change."""
        cb_called = [False]
        def callback(val):
            cb_called[0] = True

        slider = Slider(0, 0, 100, 20, 0, 100, 50, callback)

        # Update value (simulate drag)
        slider.update_val(75)

        assert cb_called[0] is True

    def test_slider_clamps_value(self):
        """Slider should clamp value within bounds."""
        slider = Slider(0, 0, 100, 20, 0, 100, 50, None)

        # Value should stay within min/max
        assert slider.val >= slider.min_val
        assert slider.val <= slider.max_val


class TestButtonEdgeCases:
    """Additional edge case tests for Button widget."""

    def test_button_hover_state_change_returns_true(self):
        """Hover state change should return True."""
        btn = Button(0, 0, 100, 50, "Test", None)

        # Initial state is not hovered
        assert btn.is_hovered is False

        # Move into button - state changes, should return True
        event = pygame.event.Event(pygame.MOUSEMOTION, {'pos': (50, 25)})
        result = btn.handle_event(event)

        assert result is True
        assert btn.is_hovered is True

    def test_button_click_without_hover_does_nothing(self):
        """Click outside hovered area should not fire callback."""
        cb_called = [False]
        def callback():
            cb_called[0] = True

        btn = Button(0, 0, 100, 50, "Test", callback)

        # Click without hovering first
        click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (50, 25)})
        result = btn.handle_event(click_event)

        assert cb_called[0] is False


class TestSliderEdgeCases:
    """Additional edge case tests for Slider widget."""

    def test_slider_drag_at_min_position(self):
        """Dragging to minimum position gives min_val."""
        slider = Slider(0, 0, 100, 20, 0, 100, 50, None)

        # Drag to the leftmost position
        slider.update_val(0)

        assert slider.val == slider.min_val

    def test_slider_drag_at_max_position(self):
        """Dragging to maximum position gives max_val."""
        slider = Slider(0, 0, 100, 20, 0, 100, 50, None)

        # Max position is rect.x + rect.w - handle_w = 0 + 100 - 20 = 80
        slider.update_val(80)

        assert slider.val == slider.max_val

    def test_slider_handle_rect_at_min_val(self):
        """Handle rect at min value is at left edge."""
        slider = Slider(0, 0, 100, 20, 0, 100, 0, None)  # Start at min

        handle = slider.get_handle_rect()

        assert handle.x == 0  # At left edge


class TestLabelEdgeCases:
    """Additional edge case tests for Label widget."""

    def test_label_update_text_changes_attribute(self):
        """update_text should change the text attribute."""
        lbl = Label(0, 0, "Original")

        lbl.update_text("New Text")

        assert lbl.text == "New Text"

    def test_label_multiple_updates(self):
        """Multiple text updates should work."""
        lbl = Label(0, 0, "First")

        lbl.update_text("Second")
        assert lbl.text == "Second"

        lbl.update_text("Third")
        assert lbl.text == "Third"
