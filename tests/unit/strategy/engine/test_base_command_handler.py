"""Tests for BaseCommandHandler resolution methods.

PROJ-176 Phase 2: Unit tests for fleet/planet resolution helpers.
"""
import pytest
from unittest.mock import Mock, MagicMock

from game.strategy.engine.command_handlers import BaseCommandHandler


class TestResolveFleet:
    """Tests for BaseCommandHandler._resolve_fleet()."""

    def test_resolve_fleet_not_found(self):
        """Returns error when fleet doesn't exist."""
        session = Mock()
        session._get_fleet_by_id.return_value = None

        fleet, error = BaseCommandHandler._resolve_fleet(session, fleet_id=999)

        assert fleet is None
        assert error is not None
        assert not error.is_valid
        assert "Fleet not found" in error.errors[0]

    def test_resolve_fleet_wrong_owner(self):
        """Returns error when fleet belongs to different empire."""
        session = Mock()
        mock_fleet = Mock()
        mock_fleet.owner_id = 1
        session._get_fleet_by_id.return_value = mock_fleet

        fleet, error = BaseCommandHandler._resolve_fleet(session, fleet_id=100, empire_id=2)

        assert fleet is None
        assert error is not None
        assert not error.is_valid
        assert "does not belong" in error.errors[0]

    def test_resolve_fleet_success(self):
        """Returns fleet when found and owner matches."""
        session = Mock()
        mock_fleet = Mock()
        mock_fleet.owner_id = 1
        session._get_fleet_by_id.return_value = mock_fleet

        fleet, error = BaseCommandHandler._resolve_fleet(session, fleet_id=100, empire_id=1)

        assert fleet is mock_fleet
        assert error is None

    def test_resolve_fleet_success_no_owner_check(self):
        """Returns fleet when found without owner validation."""
        session = Mock()
        mock_fleet = Mock()
        mock_fleet.owner_id = 1
        session._get_fleet_by_id.return_value = mock_fleet

        fleet, error = BaseCommandHandler._resolve_fleet(session, fleet_id=100)

        assert fleet is mock_fleet
        assert error is None


class TestResolvePlanet:
    """Tests for BaseCommandHandler._resolve_planet()."""

    def test_resolve_planet_not_found(self):
        """Returns error when planet doesn't exist."""
        session = Mock()
        session._get_planet_by_id.return_value = None

        planet, error = BaseCommandHandler._resolve_planet(session, planet_id=999)

        assert planet is None
        assert error is not None
        assert not error.is_valid
        assert "Planet not found" in error.errors[0]

    def test_resolve_planet_success(self):
        """Returns planet when found."""
        session = Mock()
        mock_planet = Mock()
        session._get_planet_by_id.return_value = mock_planet

        planet, error = BaseCommandHandler._resolve_planet(session, planet_id=100)

        assert planet is mock_planet
        assert error is None
