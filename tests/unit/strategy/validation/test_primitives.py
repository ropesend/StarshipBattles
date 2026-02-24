"""Tests for validator primitive functions.

PROJ-176: Tests for shared validation primitives.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.validation.primitives import (
    require_fleet,
    require_planet,
    require_system_at_location,
)
from game.core.hex_math import HexCoord


class TestRequireFleet:
    """Tests for require_fleet primitive."""

    def test_require_fleet_not_found(self):
        """Returns error when fleet doesn't exist."""
        session = MagicMock()
        session.empires = []  # No empires = no fleets

        result = require_fleet(session, fleet_id=999, empire_id=1)

        assert result is not None
        assert not result.is_valid
        assert "Fleet not found" in result.errors[0]

    def test_require_fleet_wrong_owner(self):
        """Returns error when fleet belongs to different empire."""
        fleet = MagicMock()
        fleet.id = 1
        fleet.owner_id = 2  # Different owner

        empire = MagicMock()
        empire.fleets = [fleet]

        session = MagicMock()
        session.empires = [empire]

        result = require_fleet(session, fleet_id=1, empire_id=1)  # Expect owner 1

        assert result is not None
        assert not result.is_valid
        assert "does not belong" in result.errors[0]

    def test_require_fleet_success(self):
        """Returns None when fleet is valid and owned by empire."""
        fleet = MagicMock()
        fleet.id = 1
        fleet.owner_id = 1

        empire = MagicMock()
        empire.fleets = [fleet]

        session = MagicMock()
        session.empires = [empire]

        result = require_fleet(session, fleet_id=1, empire_id=1)

        assert result is None


class TestRequirePlanet:
    """Tests for require_planet primitive."""

    def test_require_planet_not_found(self):
        """Returns error when planet doesn't exist."""
        system = MagicMock()
        system.planets = []  # No planets

        galaxy = MagicMock()
        galaxy.systems = {"sys1": system}

        session = MagicMock()
        session.galaxy = galaxy

        result = require_planet(session, planet_id=999)

        assert result is not None
        assert not result.is_valid
        assert "Planet not found" in result.errors[0]

    def test_require_planet_success(self):
        """Returns None when planet exists."""
        planet = MagicMock()
        planet.id = 42

        system = MagicMock()
        system.planets = [planet]

        galaxy = MagicMock()
        galaxy.systems = {"sys1": system}

        session = MagicMock()
        session.galaxy = galaxy

        result = require_planet(session, planet_id=42)

        assert result is None


class TestRequireSystemAtLocation:
    """Tests for require_system_at_location primitive."""

    def test_require_system_at_location_not_found(self):
        """Returns error when no system at location."""
        galaxy = MagicMock()
        galaxy.get_system_at_location.return_value = None

        result = require_system_at_location(galaxy, HexCoord(0, 0))

        assert result is not None
        assert not result.is_valid
        assert "No system at this location" in result.errors[0]

    def test_require_system_at_location_success(self):
        """Returns None when system exists at location."""
        system = MagicMock()

        galaxy = MagicMock()
        galaxy.get_system_at_location.return_value = system

        result = require_system_at_location(galaxy, HexCoord(5, 5))

        assert result is None
