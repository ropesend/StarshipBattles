"""
Tests for TransferValidator.

PROJ-68 Phase 6: Validates cargo transfer operations between fleets and colonies.
"""
import pytest
from unittest.mock import MagicMock, PropertyMock

from game.strategy.validation.transfer_validator import TransferValidator
from game.strategy.data.planet import Planet, PlanetType, SpeciesPopulation
from game.strategy.data.fleet import Fleet
from game.core.hex_math import HexCoord


def make_mock_planet(planet_id=1, owner_id=0, total_pop=1000, location=HexCoord(0, 0)):
    """Create a mock planet with configurable properties."""
    planet = MagicMock(spec=Planet)
    planet.id = planet_id
    planet.name = f"Planet-{planet_id}"
    planet.owner_id = owner_id
    planet.total_population = total_pop
    planet.location = location
    planet.populations = [SpeciesPopulation(race_id="human", count=total_pop)]
    return planet


def make_mock_fleet(fleet_id=1, location=HexCoord(0, 0), capacity=100, current=0):
    """Create a mock fleet with cargo capacity."""
    fleet = MagicMock(spec=Fleet)
    fleet.id = fleet_id
    fleet.location = location
    fleet.get_fleet_cargo_capacity = MagicMock(return_value=capacity)
    fleet.get_fleet_cargo_current = MagicMock(return_value=current)
    return fleet


def make_mock_galaxy(planets_at_hex):
    """Create a mock galaxy that returns given planets at any hex."""
    galaxy = MagicMock()
    galaxy.get_planets_at_global_hex = MagicMock(return_value=planets_at_hex)
    return galaxy


class TestTransferValidatorLoad:
    """Tests for load (colony → fleet) validation."""

    def test_valid_load_passengers(self):
        """Load is valid when fleet has capacity and colony has population."""
        planet = make_mock_planet(owner_id=0, total_pop=500)
        fleet = make_mock_fleet(capacity=100, current=0)
        galaxy = make_mock_galaxy([planet])

        result = TransferValidator.validate(
            galaxy, fleet, planet, "passengers", "load", 50
        )

        assert result.is_valid
        assert result.errors == []

    def test_load_no_cargo_space_fails(self):
        """Load fails when fleet has no available cargo capacity."""
        planet = make_mock_planet(owner_id=0, total_pop=500)
        fleet = make_mock_fleet(capacity=100, current=100)  # Full
        galaxy = make_mock_galaxy([planet])

        result = TransferValidator.validate(
            galaxy, fleet, planet, "passengers", "load", 50
        )

        assert not result.is_valid
        assert result.error_code == "NO_CARGO_SPACE"

    def test_load_no_population_fails(self):
        """Load fails when colony has no population."""
        planet = make_mock_planet(owner_id=0, total_pop=0)
        fleet = make_mock_fleet(capacity=100, current=0)
        galaxy = make_mock_galaxy([planet])

        result = TransferValidator.validate(
            galaxy, fleet, planet, "passengers", "load", 50
        )

        assert not result.is_valid
        assert result.error_code == "NO_POPULATION"


class TestTransferValidatorUnload:
    """Tests for unload (fleet → colony) validation."""

    def test_valid_unload_passengers(self):
        """Unload is valid when fleet has cargo to unload."""
        planet = make_mock_planet(owner_id=0)
        fleet = make_mock_fleet(capacity=100, current=50)
        galaxy = make_mock_galaxy([planet])

        result = TransferValidator.validate(
            galaxy, fleet, planet, "passengers", "unload", 30
        )

        assert result.is_valid
        assert result.errors == []

    def test_unload_no_cargo_to_unload_fails(self):
        """Unload fails when fleet has no cargo of this type."""
        planet = make_mock_planet(owner_id=0)
        fleet = make_mock_fleet(capacity=100, current=0)  # Empty
        galaxy = make_mock_galaxy([planet])

        result = TransferValidator.validate(
            galaxy, fleet, planet, "passengers", "unload", 30
        )

        assert not result.is_valid
        assert result.error_code == "NO_CARGO_TO_UNLOAD"


class TestTransferValidatorGeneral:
    """Tests for general validation rules."""

    def test_fleet_not_at_colony_fails(self):
        """Transfer fails when fleet is not at the colony's location."""
        planet = make_mock_planet(owner_id=0, location=HexCoord(10, 10))
        fleet = make_mock_fleet(location=HexCoord(0, 0))  # Different location
        galaxy = make_mock_galaxy([])  # Empty - planet not at fleet location

        result = TransferValidator.validate(
            galaxy, fleet, planet, "passengers", "load", 50
        )

        assert not result.is_valid
        assert result.error_code == "NOT_AT_PLANET"

    def test_uncolonized_planet_fails(self):
        """Transfer fails when planet is not colonized."""
        planet = make_mock_planet(owner_id=None)  # Uncolonized
        fleet = make_mock_fleet()
        galaxy = make_mock_galaxy([planet])

        result = TransferValidator.validate(
            galaxy, fleet, planet, "passengers", "load", 50
        )

        assert not result.is_valid
        assert result.error_code == "NOT_COLONIZED"

    def test_invalid_direction_fails(self):
        """Transfer fails with invalid direction."""
        planet = make_mock_planet(owner_id=0)
        fleet = make_mock_fleet()
        galaxy = make_mock_galaxy([planet])

        result = TransferValidator.validate(
            galaxy, fleet, planet, "passengers", "invalid", 50
        )

        assert not result.is_valid
        assert result.error_code == "INVALID_DIRECTION"

    def test_invalid_cargo_type_fails(self):
        """Transfer fails with unrecognized cargo type."""
        planet = make_mock_planet(owner_id=0)
        fleet = make_mock_fleet()
        galaxy = make_mock_galaxy([planet])

        result = TransferValidator.validate(
            galaxy, fleet, planet, "unknown_cargo", "load", 50
        )

        assert not result.is_valid
        assert result.error_code == "INVALID_CARGO_TYPE"

    def test_fleet_not_found_fails(self):
        """Transfer fails when fleet is None."""
        planet = make_mock_planet(owner_id=0)
        galaxy = make_mock_galaxy([planet])

        result = TransferValidator.validate(
            galaxy, None, planet, "passengers", "load", 50
        )

        assert not result.is_valid
        assert result.error_code == "FLEET_NOT_FOUND"

    def test_planet_not_found_fails(self):
        """Transfer fails when planet is None."""
        fleet = make_mock_fleet()
        galaxy = make_mock_galaxy([])

        result = TransferValidator.validate(
            galaxy, fleet, None, "passengers", "load", 50
        )

        assert not result.is_valid
        assert result.error_code == "PLANET_NOT_FOUND"


class TestTransferValidatorEdgeCases:
    """Edge case tests for TransferValidator."""

    def test_load_with_specific_species_id_valid(self):
        """Load passengers of specific species when available."""
        planet = make_mock_planet(owner_id=0, total_pop=500)
        # Population has human species with count > 0
        planet.populations = [SpeciesPopulation(race_id="human", count=500)]
        fleet = make_mock_fleet(capacity=100, current=0)
        galaxy = make_mock_galaxy([planet])

        result = TransferValidator.validate(
            galaxy, fleet, planet, "passengers", "load", 50, species_id="human"
        )

        assert result.is_valid

    def test_load_with_species_id_not_present_fails(self):
        """Load fails when specified species not present on planet."""
        planet = make_mock_planet(owner_id=0, total_pop=500)
        planet.populations = [SpeciesPopulation(race_id="human", count=500)]
        fleet = make_mock_fleet(capacity=100, current=0)
        galaxy = make_mock_galaxy([planet])

        result = TransferValidator.validate(
            galaxy, fleet, planet, "passengers", "load", 50, species_id="alien"
        )

        assert not result.is_valid
        assert result.error_code == "NO_POPULATION"
        assert "alien" in result.errors[0]

    def test_load_with_species_zero_count_fails(self):
        """Load fails when species exists but has zero population."""
        planet = make_mock_planet(owner_id=0, total_pop=500)
        planet.populations = [
            SpeciesPopulation(race_id="human", count=500),
            SpeciesPopulation(race_id="alien", count=0)  # Zero count
        ]
        fleet = make_mock_fleet(capacity=100, current=0)
        galaxy = make_mock_galaxy([planet])

        result = TransferValidator.validate(
            galaxy, fleet, planet, "passengers", "load", 50, species_id="alien"
        )

        assert not result.is_valid
        assert result.error_code == "NO_POPULATION"

    def test_load_amount_zero_still_validates(self):
        """amount=0 (all available) still requires validation."""
        planet = make_mock_planet(owner_id=0, total_pop=500)
        fleet = make_mock_fleet(capacity=100, current=0)
        galaxy = make_mock_galaxy([planet])

        result = TransferValidator.validate(
            galaxy, fleet, planet, "passengers", "load", 0
        )

        assert result.is_valid

    def test_unload_amount_zero_still_validates(self):
        """amount=0 for unload still validates."""
        planet = make_mock_planet(owner_id=0)
        fleet = make_mock_fleet(capacity=100, current=50)
        galaxy = make_mock_galaxy([planet])

        result = TransferValidator.validate(
            galaxy, fleet, planet, "passengers", "unload", 0
        )

        assert result.is_valid

    def test_load_capacity_exactly_full(self):
        """Load fails when fleet is exactly at capacity."""
        planet = make_mock_planet(owner_id=0, total_pop=500)
        fleet = make_mock_fleet(capacity=100, current=100)  # Exactly full
        galaxy = make_mock_galaxy([planet])

        result = TransferValidator.validate(
            galaxy, fleet, planet, "passengers", "load", 1
        )

        assert not result.is_valid
        assert result.error_code == "NO_CARGO_SPACE"

    def test_load_capacity_slightly_available(self):
        """Load succeeds when even 1 unit of space available."""
        planet = make_mock_planet(owner_id=0, total_pop=500)
        fleet = make_mock_fleet(capacity=100, current=99)  # 1 space
        galaxy = make_mock_galaxy([planet])

        result = TransferValidator.validate(
            galaxy, fleet, planet, "passengers", "load", 1
        )

        assert result.is_valid

    def test_multiple_planets_at_hex_correct_planet_validates(self):
        """Transfer validates when planet is in the list at hex."""
        planet1 = make_mock_planet(planet_id=1, owner_id=0, total_pop=500)
        planet2 = make_mock_planet(planet_id=2, owner_id=0, total_pop=300)
        fleet = make_mock_fleet(capacity=100, current=0)
        galaxy = make_mock_galaxy([planet1, planet2])  # Both at same hex

        result = TransferValidator.validate(
            galaxy, fleet, planet2, "passengers", "load", 50
        )

        assert result.is_valid

    def test_multiple_planets_at_hex_wrong_planet_fails(self):
        """Transfer fails when planet not in the list at hex."""
        planet1 = make_mock_planet(planet_id=1, owner_id=0, total_pop=500)
        planet_other = make_mock_planet(planet_id=99, owner_id=0, total_pop=300)
        fleet = make_mock_fleet(capacity=100, current=0)
        galaxy = make_mock_galaxy([planet1])  # Only planet1 at hex

        result = TransferValidator.validate(
            galaxy, fleet, planet_other, "passengers", "load", 50
        )

        assert not result.is_valid
        assert result.error_code == "NOT_AT_PLANET"

    def test_error_message_includes_planet_name(self):
        """Error messages include relevant names for user clarity."""
        planet = make_mock_planet(planet_id=42, owner_id=None)
        planet.name = "Alpha Centauri IV"
        fleet = make_mock_fleet()
        galaxy = make_mock_galaxy([planet])

        result = TransferValidator.validate(
            galaxy, fleet, planet, "passengers", "load", 50
        )

        assert "Alpha Centauri IV" in result.errors[0]

    def test_error_message_invalid_direction_shows_value(self):
        """Invalid direction error shows the provided value."""
        planet = make_mock_planet(owner_id=0)
        fleet = make_mock_fleet()
        galaxy = make_mock_galaxy([planet])

        result = TransferValidator.validate(
            galaxy, fleet, planet, "passengers", "transfer", 50
        )

        assert "transfer" in result.errors[0]

    def test_error_message_invalid_cargo_type_shows_value(self):
        """Invalid cargo type error shows the provided value."""
        planet = make_mock_planet(owner_id=0)
        fleet = make_mock_fleet()
        galaxy = make_mock_galaxy([planet])

        result = TransferValidator.validate(
            galaxy, fleet, planet, "minerals", "load", 50
        )

        assert "minerals" in result.errors[0]

    def test_unload_with_species_id_parameter(self):
        """Unload still works when species_id provided (unused for unload)."""
        planet = make_mock_planet(owner_id=0)
        fleet = make_mock_fleet(capacity=100, current=50)
        galaxy = make_mock_galaxy([planet])

        # species_id is accepted but not validated for unload
        result = TransferValidator.validate(
            galaxy, fleet, planet, "passengers", "unload", 30, species_id="human"
        )

        assert result.is_valid

    def test_load_empty_populations_list(self):
        """Load fails when planet has empty populations list."""
        planet = make_mock_planet(owner_id=0, total_pop=0)
        planet.populations = []  # Empty list
        fleet = make_mock_fleet(capacity=100, current=0)
        galaxy = make_mock_galaxy([planet])

        result = TransferValidator.validate(
            galaxy, fleet, planet, "passengers", "load", 50
        )

        assert not result.is_valid
        assert result.error_code == "NO_POPULATION"

    def test_load_with_species_multiple_populations(self):
        """Load validates correctly with multiple species populations."""
        planet = make_mock_planet(owner_id=0, total_pop=800)
        planet.populations = [
            SpeciesPopulation(race_id="human", count=500),
            SpeciesPopulation(race_id="alien", count=300)
        ]
        fleet = make_mock_fleet(capacity=100, current=0)
        galaxy = make_mock_galaxy([planet])

        # Both species should validate
        result_human = TransferValidator.validate(
            galaxy, fleet, planet, "passengers", "load", 50, species_id="human"
        )
        result_alien = TransferValidator.validate(
            galaxy, fleet, planet, "passengers", "load", 50, species_id="alien"
        )

        assert result_human.is_valid
        assert result_alien.is_valid

    def test_validation_order_fleet_checked_first(self):
        """Fleet validation happens before planet validation."""
        galaxy = make_mock_galaxy([])

        result = TransferValidator.validate(
            galaxy, None, None, "passengers", "load", 50
        )

        # Fleet checked first
        assert result.error_code == "FLEET_NOT_FOUND"

    def test_validation_order_direction_before_cargo_type(self):
        """Direction validated before cargo type."""
        planet = make_mock_planet(owner_id=0)
        fleet = make_mock_fleet()
        galaxy = make_mock_galaxy([planet])

        result = TransferValidator.validate(
            galaxy, fleet, planet, "unknown", "invalid", 50
        )

        # Direction checked before cargo type
        assert result.error_code == "INVALID_DIRECTION"

    def test_valid_cargo_types_constant(self):
        """VALID_CARGO_TYPES contains expected values."""
        assert "passengers" in TransferValidator.VALID_CARGO_TYPES

    def test_valid_directions_constant(self):
        """VALID_DIRECTIONS contains expected values."""
        assert "load" in TransferValidator.VALID_DIRECTIONS
        assert "unload" in TransferValidator.VALID_DIRECTIONS
