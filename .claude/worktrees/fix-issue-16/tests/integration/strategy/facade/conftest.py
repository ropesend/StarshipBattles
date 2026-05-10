"""Shared fixtures for strategy facade integration tests."""
import pytest
from unittest.mock import Mock


def create_mock_session_with_fleet_lookup(empires=None, **kwargs):
    """Create a mock session with _get_fleet_by_id support.

    This helper ensures facade tests work with the delegation pattern
    where StrategySessionFacade._get_fleet_by_id calls session._get_fleet_by_id().

    Args:
        empires: List of mock empires with fleets
        **kwargs: Additional attributes to set on the mock session

    Returns:
        Mock session with proper _get_fleet_by_id implementation
    """
    session = Mock()
    session.empires = empires or []

    def get_fleet_by_id(fleet_id):
        for empire in session.empires:
            for fleet in empire.fleets:
                if fleet.id == fleet_id:
                    return fleet
        return None

    session._get_fleet_by_id = get_fleet_by_id

    # Apply additional kwargs
    for key, value in kwargs.items():
        setattr(session, key, value)

    return session
