"""
Integration tests for TransferValidator.

PROJ-159: Rewritten from unit tests to use real Planet/Fleet objects
instead of MagicMock, which doesn't satisfy protocol checks.

Tests 12 core validation scenarios covering:
- Load success/failures (3 tests)
- Unload success/failures (2 tests)
- General validation failures (6 tests)
- Species-specific edge cases (2 tests)
"""

import pytest
from game.strategy.validation.transfer_validator import TransferValidator
from game.core.hex_math import HexCoord

from tests.integration.strategy.transfer.conftest import (
    create_test_planet,
    create_transport_fleet,
    MockGalaxy,
    MockSystem,
)


# --- Load Validation Tests ---

def test_load_passengers_success(mock_galaxy, colonized_planet, transport_fleet):
    """Load is valid when fleet has capacity and colony has population."""
    result = TransferValidator.validate(
        mock_galaxy, transport_fleet, colonized_planet,
        "passengers", "load", 50
    )
    assert result.is_valid
    assert result.errors == []


def test_load_fails_when_fleet_full(mock_galaxy, colonized_planet, fresh_registries):
    """Load fails when fleet has no available cargo capacity."""
    full_fleet = create_transport_fleet(cargo_capacity=100, current_cargo=100, registries=fresh_registries)
    # Put fleet at same location as galaxy system
    mock_galaxy.systems[HexCoord(0, 0)].planets.append(colonized_planet)

    result = TransferValidator.validate(
        mock_galaxy, full_fleet, colonized_planet,
        "passengers", "load", 50
    )
    assert not result.is_valid
    assert result.error_code == "NO_CARGO_SPACE"


def test_load_fails_when_colony_empty(mock_galaxy, transport_fleet):
    """Load fails when colony has no population."""
    empty_colony = create_test_planet(
        name="Empty Colony",
        owner_id=0,
        population_count=0,
        location=HexCoord(0, 0)
    )
    # Add empty colony to the system
    mock_galaxy.systems[HexCoord(0, 0)].planets.append(empty_colony)

    result = TransferValidator.validate(
        mock_galaxy, transport_fleet, empty_colony,
        "passengers", "load", 50
    )
    assert not result.is_valid
    assert result.error_code == "NO_POPULATION"


# --- Unload Validation Tests ---

def test_unload_passengers_success(mock_galaxy, colonized_planet, loaded_fleet):
    """Unload is valid when fleet has cargo to unload."""
    result = TransferValidator.validate(
        mock_galaxy, loaded_fleet, colonized_planet,
        "passengers", "unload", 30
    )
    assert result.is_valid
    assert result.errors == []


def test_unload_fails_when_fleet_empty(mock_galaxy, colonized_planet, transport_fleet):
    """Unload fails when fleet has no cargo of this type."""
    result = TransferValidator.validate(
        mock_galaxy, transport_fleet, colonized_planet,
        "passengers", "unload", 30
    )
    assert not result.is_valid
    assert result.error_code == "NO_CARGO_TO_UNLOAD"


# --- General Validation Tests ---

def test_fails_when_fleet_not_at_planet(fresh_registries):
    """Transfer fails when fleet is not at the planet's system."""
    # Planet in system at (10, 10), fleet at (0, 0)
    galaxy = MockGalaxy()
    planet = create_test_planet(name="Distant Colony", owner_id=0, location=HexCoord(0, 0))
    system = MockSystem(HexCoord(10, 10), [planet])
    galaxy.add_system(system)

    fleet = create_transport_fleet(location=HexCoord(0, 0), registries=fresh_registries)

    result = TransferValidator.validate(
        galaxy, fleet, planet,
        "passengers", "load", 50
    )
    assert not result.is_valid
    assert result.error_code == "NOT_AT_PLANET"


def test_fails_when_planet_uncolonized(fresh_registries):
    """Transfer fails when planet is not colonized."""
    galaxy = MockGalaxy()
    uncolonized = create_test_planet(name="Wild Planet", owner_id=None, population_count=0)
    system = MockSystem(HexCoord(0, 0), [uncolonized])
    galaxy.add_system(system)

    fleet = create_transport_fleet(location=HexCoord(0, 0), registries=fresh_registries)

    result = TransferValidator.validate(
        galaxy, fleet, uncolonized,
        "passengers", "load", 50
    )
    assert not result.is_valid
    assert result.error_code == "NOT_COLONIZED"


def test_fails_when_fleet_none(mock_galaxy, colonized_planet):
    """Transfer fails when fleet is None."""
    result = TransferValidator.validate(
        mock_galaxy, None, colonized_planet,
        "passengers", "load", 50
    )
    assert not result.is_valid
    assert result.error_code == "FLEET_NOT_FOUND"


def test_fails_when_planet_none(mock_galaxy, transport_fleet):
    """Transfer fails when planet is None."""
    result = TransferValidator.validate(
        mock_galaxy, transport_fleet, None,
        "passengers", "load", 50
    )
    assert not result.is_valid
    assert result.error_code == "TARGET_NOT_FOUND"


def test_fails_with_invalid_direction(mock_galaxy, colonized_planet, transport_fleet):
    """Transfer fails with invalid direction."""
    result = TransferValidator.validate(
        mock_galaxy, transport_fleet, colonized_planet,
        "passengers", "invalid", 50
    )
    assert not result.is_valid
    assert result.error_code == "INVALID_DIRECTION"


def test_fails_with_invalid_cargo_type(mock_galaxy, colonized_planet, transport_fleet):
    """Transfer fails with unrecognized cargo type."""
    result = TransferValidator.validate(
        mock_galaxy, transport_fleet, colonized_planet,
        "unknown_cargo", "load", 50
    )
    assert not result.is_valid
    assert result.error_code == "INVALID_CARGO_TYPE"


# --- Species-Specific Edge Cases ---

def test_load_specific_species_success(mock_galaxy, transport_fleet):
    """Load passengers of specific species when available."""
    planet = create_test_planet(
        name="Vulcan Colony",
        owner_id=0,
        population_count=500,
        species_id="vulcan",
        location=HexCoord(0, 0)
    )
    mock_galaxy.systems[HexCoord(0, 0)].planets.append(planet)

    result = TransferValidator.validate(
        mock_galaxy, transport_fleet, planet,
        "passengers", "load", 50, species_id="vulcan"
    )
    assert result.is_valid


def test_load_specific_species_not_present_fails(mock_galaxy, colonized_planet, transport_fleet):
    """Load fails when specified species not present on planet."""
    # colonized_planet has "human" species by default
    result = TransferValidator.validate(
        mock_galaxy, transport_fleet, colonized_planet,
        "passengers", "load", 50, species_id="alien"
    )
    assert not result.is_valid
    assert result.error_code == "NO_POPULATION"
    assert "alien" in result.errors[0]
