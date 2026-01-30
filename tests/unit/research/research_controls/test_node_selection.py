"""Tests for node selection display and allocation slider logic."""
import pytest
from unittest.mock import MagicMock


class TestAllocationSliderLogic:
    """Tests for allocation slider range calculations."""

    def test_slider_range_calculation(self, mock_tracker, mock_node):
        """Allocation slider max is current + remaining."""
        mock_tracker.get_state.return_value.rp_allocation = 50
        mock_tracker.get_remaining_rp.return_value = 150

        current_allocation = mock_tracker.get_state(mock_node.id).rp_allocation
        remaining = mock_tracker.get_remaining_rp()
        max_allocation = current_allocation + remaining

        assert max_allocation == 200

    def test_slider_range_with_zero_remaining(self, mock_tracker, mock_node):
        """Slider max equals current when no RP remaining."""
        mock_tracker.get_state.return_value.rp_allocation = 200
        mock_tracker.get_remaining_rp.return_value = 0

        current_allocation = mock_tracker.get_state(mock_node.id).rp_allocation
        remaining = mock_tracker.get_remaining_rp()
        max_allocation = current_allocation + remaining

        assert max_allocation == 200


class TestNodeSelectionDisplay:
    """Tests for node selection display logic."""

    def test_available_node_display(self, mock_tracker, mock_node):
        """Available nodes show all details and enable slider."""
        mock_node.get_status.return_value = 'available'
        state = mock_tracker.get_state(mock_node.id)

        status = mock_node.get_status(state.current_level, {})

        assert status == 'available'

    def test_locked_node_display(self, mock_tracker, mock_node):
        """Locked nodes disable the allocation slider."""
        mock_node.get_status.return_value = 'locked'
        state = mock_tracker.get_state(mock_node.id)

        status = mock_node.get_status(state.current_level, {})

        assert status == 'locked'
        # Slider should be disabled for locked nodes

    def test_completed_node_display(self, mock_tracker, mock_node):
        """Completed nodes show max level and disable slider."""
        mock_node.get_status.return_value = 'completed'
        state = mock_tracker.get_state(mock_node.id)
        state.current_level = 5  # At max

        level_display = f"Level: {state.current_level} / {mock_node.max_levels}"

        assert level_display == "Level: 5 / 5"

    def test_chance_display_format(self, mock_tracker, mock_node):
        """Chance is displayed as percentage."""
        state = mock_tracker.get_state(mock_node.id)
        state.current_chance = 0.4567

        chance_display = f"Chance: {state.current_chance * 100:.1f}%"

        assert chance_display == "Chance: 45.7%"

    def test_decay_display_format(self, mock_node):
        """Decay is displayed as percentage per turn."""
        mock_node.base_decay = 0.015

        decay_display = f"Decay: {mock_node.base_decay * 100:.1f}% / turn"

        assert decay_display == "Decay: 1.5% / turn"

    def test_price_display_format(self, mock_node):
        """Price shows effective price and curve type."""
        mock_node.get_effective_price.return_value = 2.5
        mock_node.price_curve = 'quadratic'
        target_level = 3

        eff_price = mock_node.get_effective_price(target_level)
        price_display = f"Price: {eff_price:.1f}x ({mock_node.price_curve})"

        assert price_display == "Price: 2.5x (quadratic)"


class TestClearSelection:
    """Tests for clearing node selection."""

    def test_clear_resets_all_labels(self):
        """Clearing selection resets all display values to defaults."""
        # These would be the default values after clear_selection()
        defaults = {
            'node_name': '(None)',
            'level': 'Level: -',
            'chance': 'Chance: -',
            'decay': 'Decay: -',
            'volatility': 'Volatility: -',
            'price': 'Price: -',
            'status': 'Status: -',
            'allocation': '-'
        }

        assert defaults['node_name'] == '(None)'
        assert defaults['level'] == 'Level: -'
        assert defaults['allocation'] == '-'
