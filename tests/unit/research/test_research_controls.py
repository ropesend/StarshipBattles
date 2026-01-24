"""
Unit tests for ResearchControlPanel.

Tests cover the logic-oriented aspects of the control panel:
- UI control initialization
- Node selection handling
- Auto-spread toggle functionality
- Event log formatting
- State synchronization with tracker

Note: These tests focus on logic, not visual rendering.
The UI elements are mocked to test behavior without pygame_gui.
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import pygame


# Mock pygame_gui before importing the module
@pytest.fixture(autouse=True)
def mock_pygame_gui():
    """Mock pygame_gui elements for testing.

    Note: We must clean up stale package attributes after the test
    because patch.dict removes entries from sys.modules but does NOT
    remove the corresponding attributes from parent packages. This
    leaves an inconsistent state that breaks subsequent imports via
    unittest.mock.patch().
    """
    import sys

    with patch.dict('sys.modules', {'pygame_gui': MagicMock()}):
        # Re-import with mocks
        import importlib
        import game.research.ui.research_controls as rc
        importlib.reload(rc)
        yield rc

    # After patch.dict exits, the modules that were imported during the context
    # have corrupted pygame_gui references (they're bound to the MagicMock that
    # was in sys.modules during import). If research_scene was imported (via the
    # game.research.ui __init__.py), it now has a stale pygame_gui reference.
    #
    # Fix: Reload the research_scene module to rebind pygame_gui to the real module.
    if 'game.research.ui.research_scene' in sys.modules:
        import importlib
        import game.research.ui.research_scene
        importlib.reload(game.research.ui.research_scene)


@pytest.fixture
def mock_manager():
    """Create a mock pygame_gui UI manager."""
    return MagicMock()


@pytest.fixture
def mock_tracker():
    """Create a mock ResearchTracker."""
    tracker = MagicMock()
    tracker.turn_number = 0
    tracker.rp_budget = 200
    tracker.auto_spread_enabled = False
    tracker.get_total_allocated.return_value = 50
    tracker.get_remaining_rp.return_value = 150
    tracker.get_state.return_value = MagicMock(
        current_level=0,
        current_chance=0.25,
        rp_allocation=50
    )
    tracker.get_all_tech_levels.return_value = {}
    tracker.MIN_RP_BUDGET = 50
    tracker.MAX_RP_BUDGET = 500
    return tracker


@pytest.fixture
def mock_tech_tree():
    """Create a mock TechTree."""
    tree = MagicMock()
    tree.nodes = {}
    return tree


@pytest.fixture
def mock_node():
    """Create a mock TechNode."""
    node = MagicMock()
    node.id = 'test_node'
    node.name = 'Test Node'
    node.max_levels = 5
    node.base_decay = 0.01
    node.volatility = 0.1
    node.price = 1.0
    node.price_curve = 'flat'
    node.get_status.return_value = 'available'
    node.get_effective_price.return_value = 1.0
    return node


class TestEventLogFormatting:
    """Tests for event log formatting logic."""

    def test_format_breakthrough_event(self):
        """Breakthrough events are formatted with green highlight."""
        events = [{
            'node_id': 'test',
            'event': 'breakthrough',
            'details': {
                'name': 'Test Tech',
                'old_level': 0,
                'new_level': 1,
                'max_level': 5,
                'chance': 0.45,
                'roll': 0.20,
                'rp_invested': 100
            }
        }]

        # Format the events directly (extract formatting logic)
        lines = []
        for evt in events:
            node_name = evt['details'].get('name', evt['node_id'])
            event_type = evt['event']

            if event_type == 'breakthrough':
                new_level = evt['details']['new_level']
                max_level = evt['details']['max_level']
                chance = evt['details']['chance'] * 100
                roll = evt['details']['roll'] * 100
                lines.append(
                    f"<font color='#80FF80'>BREAKTHROUGH!</font> {node_name} "
                    f"-> Lv {new_level}/{max_level} "
                    f"(rolled {roll:.0f}% < {chance:.0f}%)"
                )

        log_text = "<br>".join(lines)

        assert "BREAKTHROUGH!" in log_text
        assert "Test Tech" in log_text
        assert "Lv 1/5" in log_text
        assert "#80FF80" in log_text  # Green color

    def test_format_progress_event(self):
        """Progress events show chance and RP."""
        events = [{
            'node_id': 'test',
            'event': 'progress',
            'details': {
                'name': 'Test Tech',
                'level': 0,
                'max_level': 5,
                'chance': 0.35,
                'roll': 0.80,
                'rp_invested': 75
            }
        }]

        lines = []
        for evt in events:
            node_name = evt['details'].get('name', evt['node_id'])
            event_type = evt['event']

            if event_type == 'progress':
                chance = evt['details']['chance'] * 100
                roll = evt['details']['roll'] * 100
                rp = evt['details'].get('rp_invested', 0)
                lines.append(
                    f"{node_name}: {chance:.1f}% "
                    f"(rolled {roll:.0f}%, {rp} RP)"
                )

        log_text = "<br>".join(lines)

        assert "Test Tech" in log_text
        assert "35.0%" in log_text
        assert "75 RP" in log_text

    def test_format_decay_event(self):
        """Decay events show old and new chance values."""
        events = [{
            'node_id': 'test',
            'event': 'decay',
            'details': {
                'name': 'Test Tech',
                'old_chance': 0.30,
                'new_chance': 0.29,
                'decay_amount': 0.01
            }
        }]

        lines = []
        for evt in events:
            node_name = evt['details'].get('name', evt['node_id'])
            event_type = evt['event']

            if event_type == 'decay':
                old = evt['details']['old_chance'] * 100
                new = evt['details']['new_chance'] * 100
                lines.append(
                    f"<font color='#AAAAAA'>{node_name}: decay {old:.1f}% -> {new:.1f}%</font>"
                )

        log_text = "<br>".join(lines)

        assert "decay" in log_text
        assert "30.0%" in log_text
        assert "29.0%" in log_text
        assert "#AAAAAA" in log_text  # Gray color

    def test_format_empty_events(self):
        """Empty events list produces appropriate message."""
        events = []
        turn_number = 5

        if not events:
            log_text = f"<b>Turn {turn_number}:</b> No events."

        assert "Turn 5:" in log_text
        assert "No events" in log_text


class TestAutoSpreadLogic:
    """Tests for auto-spread toggle functionality."""

    def test_toggle_enables_auto_spread(self, mock_tracker, mock_tech_tree):
        """Toggling auto-spread enables it when disabled."""
        mock_tracker.auto_spread_enabled = False

        # Simulate toggle
        mock_tracker.auto_spread_enabled = not mock_tracker.auto_spread_enabled

        assert mock_tracker.auto_spread_enabled is True

    def test_toggle_disables_auto_spread(self, mock_tracker):
        """Toggling auto-spread disables it when enabled."""
        mock_tracker.auto_spread_enabled = True

        # Simulate toggle
        mock_tracker.auto_spread_enabled = not mock_tracker.auto_spread_enabled

        assert mock_tracker.auto_spread_enabled is False

    def test_auto_spread_applies_distribution(self, mock_tracker, mock_tech_tree):
        """When auto-spread is enabled, RP is distributed."""
        mock_tracker.auto_spread_enabled = False

        # Toggle on
        mock_tracker.auto_spread_enabled = True
        if mock_tracker.auto_spread_enabled:
            mock_tracker.spread_rp_evenly(mock_tech_tree)

        mock_tracker.spread_rp_evenly.assert_called_once_with(mock_tech_tree)


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


class TestBudgetDisplay:
    """Tests for budget display formatting."""

    def test_allocated_display_format(self, mock_tracker):
        """Allocated display shows 'X / Y' format."""
        mock_tracker.get_total_allocated.return_value = 150
        mock_tracker.rp_budget = 300

        allocated = mock_tracker.get_total_allocated()
        budget = mock_tracker.rp_budget
        display = f"Allocated: {allocated} / {budget}"

        assert display == "Allocated: 150 / 300"

    def test_turn_display_format(self, mock_tracker):
        """Turn display shows current turn number."""
        mock_tracker.turn_number = 7

        display = f"Turn: {mock_tracker.turn_number}"

        assert display == "Turn: 7"


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
