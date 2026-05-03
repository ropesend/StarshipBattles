"""Tests for Event deserialization validation.

PROJ-171: Phase 5 - Event.from_dict() validation.
"""

import pytest
from game.strategy.events.event_log import Event
from game.core.exceptions import PersistenceException


class TestEventValidation:
    """Tests for Event.from_dict() validation."""

    @pytest.fixture
    def valid_event_data(self):
        """Minimal valid Event data."""
        return {
            'event_type': 'ship_built',
            'category': 'production',
            'turn': 5,
            'empire_id': 1,
            'message': 'Cruiser completed at Alpha Centauri',
            'details': {'ship_name': 'USS Enterprise'}
        }

    def test_valid_data_creates_event(self, valid_event_data):
        """Valid data should create Event successfully."""
        event = Event.from_dict(valid_event_data)
        assert event.event_type == 'ship_built'
        assert event.category == 'production'
        assert event.turn == 5
        assert event.empire_id == 1
        assert event.message == 'Cruiser completed at Alpha Centauri'

    @pytest.mark.parametrize('field', [
        'event_type',
        'category',
        'turn',
        'empire_id',
        'message',
    ])
    def test_missing_required_field_raises_persistence_exception(
        self, valid_event_data, field,
    ):
        """Each required Event field, when absent, raises a
        PersistenceException naming the field. Parametrized in PROJ-322
        Task 1.10 (S08-CAT4-001)."""
        del valid_event_data[field]
        with pytest.raises(PersistenceException) as exc_info:
            Event.from_dict(valid_event_data)
        assert field in str(exc_info.value)
        if field == 'event_type':
            # Original test asserted on the exception's class context label.
            assert 'Event' in str(exc_info.value)

    def test_missing_details_defaults_to_empty_dict(self, valid_event_data):
        """Missing details should default to empty dict."""
        del valid_event_data['details']
        event = Event.from_dict(valid_event_data)
        assert event.details == {}

    def test_turn_zero_is_valid(self, valid_event_data):
        """Turn 0 is valid (game start events)."""
        valid_event_data['turn'] = 0
        event = Event.from_dict(valid_event_data)
        assert event.turn == 0
