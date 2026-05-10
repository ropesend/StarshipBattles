"""Tests for reset() method and state reference consistency."""
import pytest
from unittest.mock import MagicMock


class TestResetMethod:
    """Tests for reset() method that properly reinitializes control panel state.

    The reset() method is designed to be called by ResearchTreeScene._on_reset()
    to properly update the control panel's internal state without bypassing
    constructor initialization. This addresses finding RES-01.

    Note: These tests create a minimal mock panel object to test the reset()
    method logic without requiring full pygame_gui initialization.
    """

    def _create_mock_panel(self, rc, mock_tracker, mock_tech_tree):
        """Create a mock panel with minimal attributes needed for reset()."""
        panel = MagicMock(spec=rc.ResearchControlPanel)
        panel.tracker = mock_tracker
        panel.tech_tree = mock_tech_tree
        panel._selected_node = None
        panel.on_next_turn = MagicMock()
        panel.on_close = MagicMock()
        panel.on_reset = MagicMock()
        panel.on_auto_spread_changed = MagicMock()
        # Mock the slider_budget UI element
        panel.slider_budget = MagicMock()
        # Bind the actual reset method to the mock
        panel.reset = lambda t, tt: rc.ResearchControlPanel.reset(panel, t, tt)
        return panel

    def test_reset_updates_tracker_reference(self, mock_pygame_gui, mock_tracker,
                                              mock_tech_tree):
        """Reset method should update tracker reference properly."""
        rc = mock_pygame_gui
        panel = self._create_mock_panel(rc, mock_tracker, mock_tech_tree)

        # Create a new tracker for reset
        new_tracker = MagicMock()
        new_tracker.turn_number = 0
        new_tracker.rp_budget = 300
        new_tracker.auto_spread_enabled = True
        new_tracker.get_total_allocated.return_value = 0

        new_tech_tree = MagicMock()

        # Call reset
        panel.reset(new_tracker, new_tech_tree)

        # Tracker should be updated
        assert panel.tracker is new_tracker

    def test_reset_updates_tech_tree_reference(self, mock_pygame_gui, mock_tracker,
                                                mock_tech_tree):
        """Reset method should update tech_tree reference properly."""
        rc = mock_pygame_gui
        panel = self._create_mock_panel(rc, mock_tracker, mock_tech_tree)

        new_tracker = MagicMock()
        new_tracker.turn_number = 0
        new_tracker.rp_budget = 200
        new_tracker.auto_spread_enabled = False
        new_tracker.get_total_allocated.return_value = 0

        new_tech_tree = MagicMock()
        new_tech_tree.nodes = {'new_node': MagicMock()}

        panel.reset(new_tracker, new_tech_tree)

        assert panel.tech_tree is new_tech_tree

    def test_reset_calls_clear_selection(self, mock_pygame_gui, mock_tracker,
                                          mock_tech_tree):
        """Reset method should call clear_selection to update UI."""
        rc = mock_pygame_gui
        panel = self._create_mock_panel(rc, mock_tracker, mock_tech_tree)

        new_tracker = MagicMock()
        new_tracker.turn_number = 0
        new_tracker.rp_budget = 200
        new_tracker.auto_spread_enabled = False
        new_tracker.get_total_allocated.return_value = 0

        panel.reset(new_tracker, mock_tech_tree)

        panel.clear_selection.assert_called_once()

    def test_reset_calls_update_budget_display(self, mock_pygame_gui, mock_tracker,
                                                mock_tech_tree):
        """Reset method should update budget display after reset."""
        rc = mock_pygame_gui
        panel = self._create_mock_panel(rc, mock_tracker, mock_tech_tree)

        new_tracker = MagicMock()
        new_tracker.turn_number = 0
        new_tracker.rp_budget = 200
        new_tracker.auto_spread_enabled = False
        new_tracker.get_total_allocated.return_value = 0

        panel.reset(new_tracker, mock_tech_tree)

        panel.update_budget_display.assert_called_once()

    def test_reset_calls_clear_log(self, mock_pygame_gui, mock_tracker,
                                    mock_tech_tree):
        """Reset method should clear the event log."""
        rc = mock_pygame_gui
        panel = self._create_mock_panel(rc, mock_tracker, mock_tech_tree)

        new_tracker = MagicMock()
        new_tracker.turn_number = 0
        new_tracker.rp_budget = 200
        new_tracker.auto_spread_enabled = False
        new_tracker.get_total_allocated.return_value = 0

        panel.reset(new_tracker, mock_tech_tree)

        panel.clear_log.assert_called_once()

    def test_reset_calls_update_auto_spread_button(self, mock_pygame_gui, mock_tracker,
                                                    mock_tech_tree):
        """Reset method should update auto-spread button state."""
        rc = mock_pygame_gui
        panel = self._create_mock_panel(rc, mock_tracker, mock_tech_tree)

        new_tracker = MagicMock()
        new_tracker.turn_number = 0
        new_tracker.rp_budget = 200
        new_tracker.auto_spread_enabled = False
        new_tracker.get_total_allocated.return_value = 0

        panel.reset(new_tracker, mock_tech_tree)

        panel._update_auto_spread_button.assert_called_once()

    def test_reset_preserves_callbacks(self, mock_pygame_gui, mock_tracker,
                                        mock_tech_tree):
        """Reset method should not modify callback references."""
        rc = mock_pygame_gui

        on_next_turn = MagicMock()
        on_close = MagicMock()
        on_reset_cb = MagicMock()
        on_auto_spread_changed = MagicMock()

        panel = self._create_mock_panel(rc, mock_tracker, mock_tech_tree)
        panel.on_next_turn = on_next_turn
        panel.on_close = on_close
        panel.on_reset = on_reset_cb
        panel.on_auto_spread_changed = on_auto_spread_changed

        new_tracker = MagicMock()
        new_tracker.turn_number = 0
        new_tracker.rp_budget = 200
        new_tracker.auto_spread_enabled = False
        new_tracker.get_total_allocated.return_value = 0

        panel.reset(new_tracker, mock_tech_tree)

        # Callbacks should be unchanged
        assert panel.on_next_turn is on_next_turn
        assert panel.on_close is on_close
        assert panel.on_reset is on_reset_cb
        assert panel.on_auto_spread_changed is on_auto_spread_changed

    def test_reset_updates_budget_slider_position(self, mock_pygame_gui, mock_tracker,
                                                    mock_tech_tree):
        """Reset method should update the budget slider to match new tracker's budget.

        This test addresses Audit Cycle 1 finding: after reset(), the slider_budget
        position should be synchronized with the new tracker's rp_budget value.
        """
        rc = mock_pygame_gui
        panel = self._create_mock_panel(rc, mock_tracker, mock_tech_tree)

        # New tracker has a specific budget value
        new_tracker = MagicMock()
        new_tracker.turn_number = 0
        new_tracker.rp_budget = 300  # Different from default
        new_tracker.auto_spread_enabled = False
        new_tracker.get_total_allocated.return_value = 0

        panel.reset(new_tracker, mock_tech_tree)

        # Slider should be updated to match new tracker's budget
        panel.slider_budget.set_current_value.assert_called_once_with(300)


class TestStateReferenceConsistency:
    """Tests for state reference consistency in ResearchControlPanel.

    PROJ-40/NEW-RES-003: Ensure _selected_node.id is used consistently.

    Note: These tests mock the panel object directly instead of instantiating
    ResearchControlPanel due to pygame_gui dependencies.
    """

    def test_allocation_uses_internal_selected_node(self, mock_pygame_gui, mock_tracker, mock_tech_tree):
        """Allocation slider uses _selected_node.id, not external parameter.

        PROJ-40/NEW-RES-003: When allocation slider is moved, should use
        the internally stored _selected_node, not the parameter.
        """
        rc = mock_pygame_gui

        # Create a mock panel with just the needed attributes
        mock_panel = MagicMock()
        mock_panel.tracker = mock_tracker
        mock_panel.slider_allocation = MagicMock()
        mock_panel.slider_budget = MagicMock()
        mock_panel.btn_next_turn = MagicMock()
        mock_panel.btn_reset = MagicMock()
        mock_panel.btn_close = MagicMock()
        mock_panel.btn_auto_spread = MagicMock()
        mock_panel.lbl_allocation_value = MagicMock()
        mock_panel.slider_allocation.get_current_value.return_value = 50

        # Set up selected node
        mock_node = MagicMock()
        mock_node.id = "test_node_id"
        mock_panel._selected_node = mock_node

        # Set up tracker state
        mock_state = MagicMock()
        mock_state.rp_allocation = 50
        mock_tracker.get_state.return_value = mock_state

        # Create a slider moved event
        event = MagicMock()
        event.type = rc.pygame_gui.UI_HORIZONTAL_SLIDER_MOVED
        event.ui_element = mock_panel.slider_allocation

        # Call handle_event with a DIFFERENT node_id parameter
        # Use the real method bound to our mock
        result = rc.ResearchControlPanel.handle_event(mock_panel, event, "different_node_id", mock_tech_tree)

        # Should use _selected_node.id for allocation
        mock_tracker.set_allocation.assert_called_once_with("test_node_id", 50)
        assert result is True

    def test_allocation_validates_node_state_consistency(self, mock_pygame_gui, mock_tracker, mock_tech_tree):
        """Allocation slider validates that _selected_node matches operation.

        PROJ-40/NEW-RES-003: Internal state should be validated before operations.
        """
        rc = mock_pygame_gui

        # Create a mock panel with no selected node
        mock_panel = MagicMock()
        mock_panel.tracker = mock_tracker
        mock_panel.slider_allocation = MagicMock()
        mock_panel.slider_budget = MagicMock()
        mock_panel.btn_next_turn = MagicMock()
        mock_panel.btn_reset = MagicMock()
        mock_panel.btn_close = MagicMock()
        mock_panel.btn_auto_spread = MagicMock()
        mock_panel._selected_node = None

        # Create a slider moved event
        event = MagicMock()
        event.type = rc.pygame_gui.UI_HORIZONTAL_SLIDER_MOVED
        event.ui_element = mock_panel.slider_allocation

        # Should not crash and should not set allocation
        result = rc.ResearchControlPanel.handle_event(mock_panel, event, "some_node", mock_tech_tree)

        mock_tracker.set_allocation.assert_not_called()
        assert result is False
