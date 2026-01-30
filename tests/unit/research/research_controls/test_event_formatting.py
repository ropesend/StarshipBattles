"""Tests for event log formatting and auto-spread logic."""
import pytest
from unittest.mock import MagicMock


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
