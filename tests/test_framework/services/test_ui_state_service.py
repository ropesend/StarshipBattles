"""
Unit tests for UIStateService.

Tests state management, observer pattern, and state change notifications.
"""

import pytest
from unittest.mock import Mock
from test_framework.services.ui_state_service import UIStateService


class TestUIStateServiceInit:
    """Test UIStateService initialization."""

    def test_init(self):
        """Test service initialization with default state."""
        service = UIStateService()

        assert service.get_selected_category() is None
        assert service.get_selected_test_id() is None
        assert service.get_category_hover() is None
        assert service.get_test_hover() is None
        assert service.is_json_popup_visible() is False
        assert service.is_confirmation_dialog_visible() is False
        assert service.is_headless_running() is False


class TestCategorySelection:
    """Test category selection."""

    def test_select_category(self):
        """Test selecting a category."""
        service = UIStateService()

        service.select_category("Beam Weapons")

        assert service.get_selected_category() == "Beam Weapons"

    def test_select_category_clears_test(self):
        """Test that selecting category clears test selection."""
        service = UIStateService()
        service.select_test("TEST-001")

        service.select_category("Beam Weapons")

        assert service.get_selected_test_id() is None

    def test_select_category_notifies_observers(self, observer_spy):
        """Test that category selection notifies observers."""
        service = UIStateService()
        service.add_observer(observer_spy)

        service.select_category("Beam Weapons")

        assert observer_spy.call_count['count'] == 1

    def test_select_category_same_value_notifies(self, observer_spy):
        """Test that selecting same category does not notify."""
        service = UIStateService()
        service.select_category("Beam Weapons")
        service.add_observer(observer_spy)

        service.select_category("Beam Weapons")  # Same value

        assert observer_spy.call_count['count'] == 0

    def test_select_category_none(self):
        """Test deselecting category."""
        service = UIStateService()
        service.select_category("Beam Weapons")

        service.select_category(None)

        assert service.get_selected_category() is None

    def test_select_category_changes_value(self):
        """Test changing category selection."""
        service = UIStateService()
        service.select_category("Beam Weapons")

        service.select_category("Seeker Weapons")

        assert service.get_selected_category() == "Seeker Weapons"


class TestTestSelection:
    """Test test selection."""

    def test_select_test(self):
        """Test selecting a test."""
        service = UIStateService()

        service.select_test("TEST-001")

        assert service.get_selected_test_id() == "TEST-001"

    def test_select_test_notifies_observers(self, observer_spy):
        """Test that test selection notifies observers."""
        service = UIStateService()
        service.add_observer(observer_spy)

        service.select_test("TEST-001")

        assert observer_spy.call_count['count'] == 1

    def test_select_test_same_value_no_notify(self, observer_spy):
        """Test that selecting same test does not notify."""
        service = UIStateService()
        service.select_test("TEST-001")
        service.add_observer(observer_spy)

        service.select_test("TEST-001")  # Same value

        assert observer_spy.call_count['count'] == 0

    def test_select_test_none(self):
        """Test deselecting test."""
        service = UIStateService()
        service.select_test("TEST-001")

        service.select_test(None)

        assert service.get_selected_test_id() is None

    def test_select_test_changes_value(self):
        """Test changing test selection."""
        service = UIStateService()
        service.select_test("TEST-001")

        service.select_test("TEST-002")

        assert service.get_selected_test_id() == "TEST-002"


class TestHoverState:
    """Test hover state management."""

    def test_set_category_hover(self):
        """Test setting category hover."""
        service = UIStateService()

        service.set_category_hover("Beam Weapons")

        assert service.get_category_hover() == "Beam Weapons"

    def test_set_category_hover_none(self):
        """Test clearing category hover."""
        service = UIStateService()
        service.set_category_hover("Beam Weapons")

        service.set_category_hover(None)

        assert service.get_category_hover() is None

    def test_set_test_hover(self):
        """Test setting test hover."""
        service = UIStateService()

        service.set_test_hover("TEST-001")

        assert service.get_test_hover() == "TEST-001"

    def test_set_test_hover_none(self):
        """Test clearing test hover."""
        service = UIStateService()
        service.set_test_hover("TEST-001")

        service.set_test_hover(None)

        assert service.get_test_hover() is None

    def test_hover_does_not_notify_observers(self, observer_spy):
        """Test that hover changes do not notify observers."""
        service = UIStateService()
        service.add_observer(observer_spy)

        service.set_category_hover("Beam Weapons")
        service.set_test_hover("TEST-001")

        assert observer_spy.call_count['count'] == 0


class TestModalVisibility:
    """Test modal visibility state."""

    def test_set_json_popup_visible(self):
        """Test showing JSON popup."""
        service = UIStateService()

        service.set_json_popup_visible(True)

        assert service.is_json_popup_visible() is True

    def test_set_json_popup_hidden(self):
        """Test hiding JSON popup."""
        service = UIStateService()
        service.set_json_popup_visible(True)

        service.set_json_popup_visible(False)

        assert service.is_json_popup_visible() is False

    def test_set_confirmation_dialog_visible(self):
        """Test showing confirmation dialog."""
        service = UIStateService()

        service.set_confirmation_dialog_visible(True)

        assert service.is_confirmation_dialog_visible() is True

    def test_set_confirmation_dialog_hidden(self):
        """Test hiding confirmation dialog."""
        service = UIStateService()
        service.set_confirmation_dialog_visible(True)

        service.set_confirmation_dialog_visible(False)

        assert service.is_confirmation_dialog_visible() is False


class TestHeadlessRunningState:
    """Test headless running state."""

    def test_set_headless_running_true(self):
        """Test setting headless running."""
        service = UIStateService()

        service.set_headless_running(True)

        assert service.is_headless_running() is True

    def test_set_headless_running_false(self):
        """Test clearing headless running."""
        service = UIStateService()
        service.set_headless_running(True)

        service.set_headless_running(False)

        assert service.is_headless_running() is False

    def test_set_headless_running_notifies_observers(self, observer_spy):
        """Test that headless running state notifies observers."""
        service = UIStateService()
        service.add_observer(observer_spy)

        service.set_headless_running(True)

        assert observer_spy.call_count['count'] == 1

    def test_set_headless_running_same_value_no_notify(self, observer_spy):
        """Test that same value does not notify."""
        service = UIStateService()
        service.set_headless_running(True)
        service.add_observer(observer_spy)

        service.set_headless_running(True)  # Same value

        assert observer_spy.call_count['count'] == 0


class TestResetSelection:
    """Test selection reset."""

    def test_reset_selection(self):
        """Test resetting all selections."""
        service = UIStateService()
        service.select_category("Beam Weapons")
        service.select_test("TEST-001")

        service.reset_selection()

        assert service.get_selected_category() is None
        assert service.get_selected_test_id() is None

    def test_reset_selection_notifies_observers(self, observer_spy):
        """Test that reset notifies observers."""
        service = UIStateService()
        service.select_category("Beam Weapons")
        service.add_observer(observer_spy)

        service.reset_selection()

        assert observer_spy.call_count['count'] == 1

    def test_reset_selection_when_empty(self, observer_spy):
        """Test reset when already empty."""
        service = UIStateService()
        service.add_observer(observer_spy)

        service.reset_selection()

        # Should still notify even if already empty
        assert observer_spy.call_count['count'] == 1


class TestObserverPattern:
    """Test observer pattern implementation."""

    def test_add_observer(self, observer_spy):
        """Test adding observer."""
        service = UIStateService()

        service.add_observer(observer_spy)
        service.select_category("Beam Weapons")

        assert observer_spy.call_count['count'] == 1

    def test_add_multiple_observers(self):
        """Test adding multiple observers."""
        service = UIStateService()

        observer1 = Mock()
        observer2 = Mock()

        service.add_observer(observer1)
        service.add_observer(observer2)
        service.select_category("Beam Weapons")

        observer1.assert_called_once()
        observer2.assert_called_once()

    def test_add_same_observer_twice(self, observer_spy):
        """Test that same observer is not added twice."""
        service = UIStateService()

        service.add_observer(observer_spy)
        service.add_observer(observer_spy)  # Add again
        service.select_category("Beam Weapons")

        assert observer_spy.call_count['count'] == 1  # Only called once

    def test_remove_observer(self, observer_spy):
        """Test removing observer."""
        service = UIStateService()
        service.add_observer(observer_spy)

        service.remove_observer(observer_spy)
        service.select_category("Beam Weapons")

        assert observer_spy.call_count['count'] == 0  # Not called

    def test_remove_observer_not_added(self):
        """Test removing observer that was never added."""
        service = UIStateService()
        observer = Mock()

        # Should not raise error
        service.remove_observer(observer)

    def test_observer_error_handling(self):
        """Test that observer errors don't break notification."""
        service = UIStateService()

        observer1 = Mock(side_effect=Exception("Test error"))
        observer2 = Mock()

        service.add_observer(observer1)
        service.add_observer(observer2)

        # Should not raise, and observer2 should still be called
        service.select_category("Beam Weapons")

        observer2.assert_called_once()

    def test_observers_called_in_order(self):
        """Test that observers are called in order added."""
        service = UIStateService()

        call_order = []
        observer1 = lambda: call_order.append(1)
        observer2 = lambda: call_order.append(2)
        observer3 = lambda: call_order.append(3)

        service.add_observer(observer1)
        service.add_observer(observer2)
        service.add_observer(observer3)

        service.select_category("Beam Weapons")

        assert call_order == [1, 2, 3]


class TestComplexStateTransitions:
    """Test complex state transitions."""

    def test_category_change_clears_test_and_notifies_once(self, observer_spy):
        """Test that changing category only notifies once."""
        service = UIStateService()
        service.select_category("Beam Weapons")
        service.select_test("TEST-001")
        service.add_observer(observer_spy)

        service.select_category("Seeker Weapons")

        # Should notify once (category change clears test implicitly)
        assert observer_spy.call_count['count'] == 1

    def test_multiple_state_changes(self, observer_spy):
        """Test multiple state changes notify correctly."""
        service = UIStateService()
        service.add_observer(observer_spy)

        service.select_category("Beam Weapons")  # 1
        service.select_test("TEST-001")  # 2
        service.select_test("TEST-002")  # 3
        service.reset_selection()  # 4

        assert observer_spy.call_count['count'] == 4

    def test_state_consistency_after_operations(self):
        """Test state remains consistent after multiple operations."""
        service = UIStateService()

        service.select_category("Beam Weapons")
        service.select_test("TEST-001")
        service.set_category_hover("Seeker Weapons")
        service.set_test_hover("TEST-002")
        service.set_json_popup_visible(True)

        # Verify all state
        assert service.get_selected_category() == "Beam Weapons"
        assert service.get_selected_test_id() == "TEST-001"
        assert service.get_category_hover() == "Seeker Weapons"
        assert service.get_test_hover() == "TEST-002"
        assert service.is_json_popup_visible() is True

        # Now change category - should clear only test selection
        service.select_category("Projectile Weapons")

        assert service.get_selected_category() == "Projectile Weapons"
        assert service.get_selected_test_id() is None
        assert service.get_category_hover() == "Seeker Weapons"  # Unchanged
        assert service.get_test_hover() == "TEST-002"  # Unchanged
        assert service.is_json_popup_visible() is True  # Unchanged
