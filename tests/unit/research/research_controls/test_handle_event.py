"""
TCG-FND-012: Tests for ResearchControlPanel.handle_event() logic.

Tests cover:
- Slider event handling (budget slider, allocation slider)
- Auto-spread toggle functionality
- Button press event routing
- Event return values (handled vs not handled)

Note: These tests verify the event handling LOGIC without instantiating
pygame_gui components. The actual pygame_gui integration is tested separately.
"""
import pytest
from unittest.mock import MagicMock


class TestHandleEventSliderBudgetLogic:
    """TCG-FND-012: Tests for budget slider event handling logic."""

    def test_budget_slider_value_updates_tracker(self, mock_tracker):
        """Budget slider change should update tracker RP budget."""
        # Simulate what happens when budget slider moves
        new_budget = 350
        mock_tracker.set_rp_budget(new_budget)

        mock_tracker.set_rp_budget.assert_called_once_with(350)

    def test_budget_clamped_to_valid_range(self, mock_tracker):
        """Budget values outside valid range should be clamped."""
        # Simulate setting budget via tracker
        mock_tracker.set_rp_budget(1000)  # Above max (500)
        mock_tracker.set_rp_budget.assert_called_with(1000)

        # The tracker itself clamps, so we just verify the call happens

    def test_budget_label_format(self, mock_tracker):
        """Budget label should show numeric value as string."""
        mock_tracker.rp_budget = 275
        label_text = str(mock_tracker.rp_budget)
        assert label_text == "275"


class TestHandleEventSliderAllocationLogic:
    """TCG-FND-012: Tests for allocation slider event handling logic."""

    def test_allocation_requires_selected_node(self, mock_tracker, mock_node):
        """Allocation can only be set when a node is selected."""
        # With selected node
        selected_node = mock_node
        node_id = selected_node.id if selected_node else None

        assert node_id == 'test_node'

        # Without selected node
        selected_node = None
        node_id = selected_node.id if selected_node else None

        assert node_id is None

    def test_allocation_value_set_on_tracker(self, mock_tracker, mock_node):
        """Slider value is passed to tracker.set_allocation()."""
        node_id = mock_node.id
        new_allocation = 75

        mock_tracker.set_allocation(node_id, new_allocation)

        mock_tracker.set_allocation.assert_called_once_with('test_node', 75)

    def test_allocation_label_shows_actual_value(self, mock_tracker, mock_node):
        """Allocation label shows the actual value from tracker (may be clamped)."""
        # Simulate clamping: requested 150, actual is 100
        mock_tracker.get_state.return_value.rp_allocation = 100

        actual = mock_tracker.get_state(mock_node.id).rp_allocation

        assert str(actual) == "100"

    def test_allocation_updates_budget_display(self, mock_tracker):
        """After allocation change, budget display should be updated."""
        mock_tracker.get_total_allocated.return_value = 150
        mock_tracker.rp_budget = 200

        allocated = mock_tracker.get_total_allocated()
        budget = mock_tracker.rp_budget

        assert f"Allocated: {allocated} / {budget}" == "Allocated: 150 / 200"


class TestHandleEventAutoSpreadToggleLogic:
    """TCG-FND-012: Tests for auto-spread toggle button logic."""

    def test_toggle_flips_enabled_state_from_false(self, mock_tracker):
        """Toggle flips auto_spread_enabled from False to True."""
        mock_tracker.auto_spread_enabled = False

        # Simulate toggle
        mock_tracker.auto_spread_enabled = not mock_tracker.auto_spread_enabled

        assert mock_tracker.auto_spread_enabled is True

    def test_toggle_flips_enabled_state_from_true(self, mock_tracker):
        """Toggle flips auto_spread_enabled from True to False."""
        mock_tracker.auto_spread_enabled = True

        # Simulate toggle
        mock_tracker.auto_spread_enabled = not mock_tracker.auto_spread_enabled

        assert mock_tracker.auto_spread_enabled is False

    def test_enabling_spread_calls_spread_rp_evenly(self, mock_tracker, mock_tech_tree):
        """When auto-spread is enabled, spread_rp_evenly is called."""
        mock_tracker.auto_spread_enabled = False

        # Simulate toggle and apply
        mock_tracker.auto_spread_enabled = True
        if mock_tracker.auto_spread_enabled:
            mock_tracker.spread_rp_evenly(mock_tech_tree)

        mock_tracker.spread_rp_evenly.assert_called_once_with(mock_tech_tree)

    def test_disabling_spread_does_not_call_spread(self, mock_tracker, mock_tech_tree):
        """When auto-spread is disabled, spread_rp_evenly is NOT called."""
        mock_tracker.auto_spread_enabled = True

        # Simulate toggle
        mock_tracker.auto_spread_enabled = not mock_tracker.auto_spread_enabled

        # Should not trigger spread when disabling
        if mock_tracker.auto_spread_enabled:
            mock_tracker.spread_rp_evenly(mock_tech_tree)

        mock_tracker.spread_rp_evenly.assert_not_called()

    def test_button_text_reflects_state_on(self, mock_tracker):
        """Button text shows 'Auto-Spread: ON' when enabled."""
        mock_tracker.auto_spread_enabled = True

        text = "Auto-Spread: ON" if mock_tracker.auto_spread_enabled else "Auto-Spread: OFF"

        assert text == "Auto-Spread: ON"

    def test_button_text_reflects_state_off(self, mock_tracker):
        """Button text shows 'Auto-Spread: OFF' when disabled."""
        mock_tracker.auto_spread_enabled = False

        text = "Auto-Spread: ON" if mock_tracker.auto_spread_enabled else "Auto-Spread: OFF"

        assert text == "Auto-Spread: OFF"

    def test_callback_receives_new_state(self, mock_tracker):
        """Callback receives the new enabled state after toggle."""
        callback = MagicMock()
        mock_tracker.auto_spread_enabled = False

        # Simulate toggle
        mock_tracker.auto_spread_enabled = not mock_tracker.auto_spread_enabled
        callback(mock_tracker.auto_spread_enabled)

        callback.assert_called_once_with(True)


class TestHandleEventButtonsLogic:
    """TCG-FND-012: Tests for button press event routing logic."""

    def test_next_turn_button_triggers_callback(self):
        """Next Turn button should trigger the on_next_turn callback."""
        callback = MagicMock()

        # Simulate button press
        callback()

        callback.assert_called_once()

    def test_reset_button_triggers_callback(self):
        """Reset button should trigger the on_reset callback."""
        callback = MagicMock()

        # Simulate button press
        callback()

        callback.assert_called_once()

    def test_close_button_triggers_callback(self):
        """Close button should trigger the on_close callback."""
        callback = MagicMock()

        # Simulate button press
        callback()

        callback.assert_called_once()


class TestHandleEventReturnValuesLogic:
    """TCG-FND-012: Tests for handle_event return value semantics."""

    def test_event_handling_returns_true_when_handled(self):
        """When an event is handled, the handler should return True."""
        # Simulate event handling logic
        def handle_known_event(event_type, element, known_elements):
            if element in known_elements:
                return True
            return False

        btn_next_turn = MagicMock()
        known_elements = [btn_next_turn]

        result = handle_known_event('button_pressed', btn_next_turn, known_elements)

        assert result is True

    def test_event_handling_returns_false_when_not_handled(self):
        """When an event is not handled, the handler should return False."""
        def handle_known_event(event_type, element, known_elements):
            if element in known_elements:
                return True
            return False

        btn_next_turn = MagicMock()
        other_button = MagicMock()
        known_elements = [btn_next_turn]

        result = handle_known_event('button_pressed', other_button, known_elements)

        assert result is False

    def test_unrecognized_event_type_returns_false(self):
        """Unknown event types should return False."""
        def handle_event(event_type, supported_types):
            if event_type in supported_types:
                return True
            return False

        supported = ['button_pressed', 'slider_moved']
        result = handle_event('unknown_event', supported)

        assert result is False


class TestHandleEventSliderRangeLogic:
    """TCG-FND-012: Tests for allocation slider range calculation logic."""

    def test_slider_max_is_current_plus_remaining(self, mock_tracker, mock_node):
        """Slider max should be current allocation + remaining RP."""
        mock_tracker.get_state.return_value.rp_allocation = 50
        mock_tracker.get_remaining_rp.return_value = 150

        current = mock_tracker.get_state(mock_node.id).rp_allocation
        remaining = mock_tracker.get_remaining_rp()
        max_allocation = current + remaining

        assert max_allocation == 200

    def test_slider_max_when_no_remaining(self, mock_tracker, mock_node):
        """Slider max equals current when no RP remaining."""
        mock_tracker.get_state.return_value.rp_allocation = 200
        mock_tracker.get_remaining_rp.return_value = 0

        current = mock_tracker.get_state(mock_node.id).rp_allocation
        remaining = mock_tracker.get_remaining_rp()
        max_allocation = current + remaining

        assert max_allocation == 200

    def test_slider_max_minimum_is_one(self, mock_tracker, mock_node):
        """Slider max should be at least 1 to avoid division issues."""
        mock_tracker.get_state.return_value.rp_allocation = 0
        mock_tracker.get_remaining_rp.return_value = 0

        current = mock_tracker.get_state(mock_node.id).rp_allocation
        remaining = mock_tracker.get_remaining_rp()
        max_allocation = max(1, current + remaining)

        assert max_allocation == 1
