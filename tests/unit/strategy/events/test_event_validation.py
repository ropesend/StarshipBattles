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

    def test_missing_event_type_raises_persistence_exception(self, valid_event_data):
        """Missing event_type should raise PersistenceException."""
        del valid_event_data['event_type']
        with pytest.raises(PersistenceException) as exc_info:
            Event.from_dict(valid_event_data)
        assert 'event_type' in str(exc_info.value)
        assert 'Event' in str(exc_info.value)

    def test_missing_category_raises_persistence_exception(self, valid_event_data):
        """Missing category should raise PersistenceException."""
        del valid_event_data['category']
        with pytest.raises(PersistenceException) as exc_info:
            Event.from_dict(valid_event_data)
        assert 'category' in str(exc_info.value)

    def test_missing_turn_raises_persistence_exception(self, valid_event_data):
        """Missing turn should raise PersistenceException."""
        del valid_event_data['turn']
        with pytest.raises(PersistenceException) as exc_info:
            Event.from_dict(valid_event_data)
        assert 'turn' in str(exc_info.value)

    def test_missing_empire_id_raises_persistence_exception(self, valid_event_data):
        """Missing empire_id should raise PersistenceException."""
        del valid_event_data['empire_id']
        with pytest.raises(PersistenceException) as exc_info:
            Event.from_dict(valid_event_data)
        assert 'empire_id' in str(exc_info.value)

    def test_missing_message_raises_persistence_exception(self, valid_event_data):
        """Missing message should raise PersistenceException."""
        del valid_event_data['message']
        with pytest.raises(PersistenceException) as exc_info:
            Event.from_dict(valid_event_data)
        assert 'message' in str(exc_info.value)

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
