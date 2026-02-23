"""Unit tests for CargoTransferService.

PROJ-162: Tests for cargo transfer business logic extracted from UI dialogs.
"""

import pytest
from unittest.mock import MagicMock, PropertyMock

from game.strategy.services.cargo_transfer_service import CargoTransferService
from game.strategy.engine.commands import IssueTransferCommand


class TestResolveColonies:
    """Tests for CargoTransferService.resolve_colonies()"""

    def test_resolve_colonies_at_primary_hex(self):
        """When planets exist at primary hex, returns colonies from that hex."""
        # Arrange
        facade = MagicMock()
        fleet = MagicMock()
        hex_coord = (1, 2)

        colony = MagicMock()
        colony.owner_id = 1  # Colonized
        uncolonized = MagicMock()
        uncolonized.owner_id = None  # Not colonized

        facade.get_planets_at_hex.return_value = [colony, uncolonized]

        # Act
        result = CargoTransferService.resolve_colonies(facade, hex_coord, fleet)

        # Assert
        assert len(result) == 1
        assert result[0] == colony
        facade.get_planets_at_hex.assert_called_once_with(hex_coord)

    def test_resolve_colonies_fallback_to_fleet_location(self):
        """When primary hex is empty, falls back to fleet's location."""
        # Arrange
        facade = MagicMock()
        fleet = MagicMock()
        fleet.location = (5, 6)
        hex_coord = (1, 2)  # Empty hex

        colony = MagicMock()
        colony.owner_id = 1

        # First call returns empty, second returns colony
        facade.get_planets_at_hex.side_effect = [[], [colony]]

        # Act
        result = CargoTransferService.resolve_colonies(facade, hex_coord, fleet)

        # Assert
        assert len(result) == 1
        assert result[0] == colony
        assert facade.get_planets_at_hex.call_count == 2
        facade.get_planets_at_hex.assert_any_call(hex_coord)
        facade.get_planets_at_hex.assert_any_call(fleet.location)

    def test_resolve_colonies_filters_uncolonized(self):
        """Only returns planets with owner_id not None."""
        # Arrange
        facade = MagicMock()
        fleet = MagicMock()
        hex_coord = (1, 2)

        uncolonized1 = MagicMock()
        uncolonized1.owner_id = None
        uncolonized2 = MagicMock()
        uncolonized2.owner_id = None

        facade.get_planets_at_hex.return_value = [uncolonized1, uncolonized2]

        # Act
        result = CargoTransferService.resolve_colonies(facade, hex_coord, fleet)

        # Assert
        assert len(result) == 0

    def test_resolve_colonies_no_fallback_if_fleet_has_no_location(self):
        """If fleet has no location attribute, doesn't try fallback."""
        # Arrange
        facade = MagicMock()
        fleet = MagicMock(spec=[])  # No attributes
        hex_coord = (1, 2)

        facade.get_planets_at_hex.return_value = []

        # Act
        result = CargoTransferService.resolve_colonies(facade, hex_coord, fleet)

        # Assert
        assert len(result) == 0
        facade.get_planets_at_hex.assert_called_once_with(hex_coord)


class TestGetUnloadItems:
    """Tests for CargoTransferService.get_unload_items()"""

    def test_get_unload_items_with_passengers(self):
        """Fleet with passengers returns passenger item."""
        # Arrange
        facade = MagicMock()
        fleet_info = MagicMock()
        fleet_info.passengers_current = 5000
        facade.get_fleet.return_value = fleet_info

        colony = MagicMock()
        colony.owner_id = 1

        # Act
        result = CargoTransferService.get_unload_items(facade, 42, [colony])

        # Assert
        assert len(result) == 1
        assert result[0]['label'] == "Passengers (5000)"
        assert result[0]['cargo_type'] == 'passengers'
        assert result[0]['species_id'] is None
        assert result[0]['max_amount'] == 5000

    def test_get_unload_items_zero_passengers(self):
        """Fleet with zero passengers returns empty list."""
        # Arrange
        facade = MagicMock()
        fleet_info = MagicMock()
        fleet_info.passengers_current = 0
        facade.get_fleet.return_value = fleet_info

        colony = MagicMock()
        colony.owner_id = 1

        # Act
        result = CargoTransferService.get_unload_items(facade, 42, [colony])

        # Assert
        assert len(result) == 0

    def test_get_unload_items_no_colonies_returns_empty(self):
        """No colonies means nothing to unload to."""
        # Arrange
        facade = MagicMock()

        # Act
        result = CargoTransferService.get_unload_items(facade, 42, [])

        # Assert
        assert len(result) == 0
        facade.get_fleet.assert_not_called()

    def test_get_unload_items_no_fleet_returns_empty(self):
        """If fleet not found, returns empty list."""
        # Arrange
        facade = MagicMock()
        facade.get_fleet.return_value = None

        colony = MagicMock()
        colony.owner_id = 1

        # Act
        result = CargoTransferService.get_unload_items(facade, 42, [colony])

        # Assert
        assert len(result) == 0


class TestGetLoadItems:
    """Tests for CargoTransferService.get_load_items()"""

    def test_get_load_items_with_population_details(self):
        """Colony with population_details returns per-species items."""
        # Arrange
        facade = MagicMock()

        colony = MagicMock()
        colony.planet_id = 10
        colony.name = "Alpha Colony"

        planet_info = MagicMock()
        planet_info.population_details = [
            ("Human", 3000, 80),
            ("Silicoid", 1500, 90),
        ]
        facade.get_planet.return_value = planet_info

        # Act
        result = CargoTransferService.get_load_items(facade, [colony])

        # Assert
        assert len(result) == 2
        assert result[0]['label'] == "Alpha Colony: Human (3000)"
        assert result[0]['cargo_type'] == 'passengers'
        assert result[0]['species_id'] == "Human"
        assert result[0]['max_amount'] == 3000
        assert result[0]['planet_id'] == 10

        assert result[1]['label'] == "Alpha Colony: Silicoid (1500)"
        assert result[1]['species_id'] == "Silicoid"
        assert result[1]['max_amount'] == 1500

    def test_get_load_items_total_population_fallback(self):
        """Colony without population_details uses total_population."""
        # Arrange
        facade = MagicMock()

        colony = MagicMock()
        colony.planet_id = 10
        colony.name = "Beta Colony"

        planet_info = MagicMock(spec=['total_population'])
        planet_info.total_population = 5000
        facade.get_planet.return_value = planet_info

        # Act
        result = CargoTransferService.get_load_items(facade, [colony])

        # Assert
        assert len(result) == 1
        assert result[0]['label'] == "Beta Colony: Population (5000)"
        assert result[0]['cargo_type'] == 'passengers'
        assert result[0]['species_id'] is None
        assert result[0]['max_amount'] == 5000
        assert result[0]['planet_id'] == 10

    def test_get_load_items_no_colony_returns_empty(self):
        """Empty colonies list returns empty items."""
        # Arrange
        facade = MagicMock()

        # Act
        result = CargoTransferService.get_load_items(facade, [])

        # Assert
        assert len(result) == 0
        facade.get_planet.assert_not_called()

    def test_get_load_items_skips_zero_population_species(self):
        """Species with 0 population are skipped."""
        # Arrange
        facade = MagicMock()

        colony = MagicMock()
        colony.planet_id = 10
        colony.name = "Gamma Colony"

        planet_info = MagicMock()
        planet_info.population_details = [
            ("Human", 0, 80),  # Zero population
            ("Silicoid", 1500, 90),
        ]
        facade.get_planet.return_value = planet_info

        # Act
        result = CargoTransferService.get_load_items(facade, [colony])

        # Assert
        assert len(result) == 1
        assert result[0]['species_id'] == "Silicoid"

    def test_get_load_items_empty_population_details(self):
        """Colony with empty population_details uses total_population fallback."""
        # Arrange
        facade = MagicMock()

        colony = MagicMock()
        colony.planet_id = 10
        colony.name = "Delta Colony"

        planet_info = MagicMock()
        planet_info.population_details = []  # Empty list
        planet_info.total_population = 2000
        facade.get_planet.return_value = planet_info

        # Act
        result = CargoTransferService.get_load_items(facade, [colony])

        # Assert
        assert len(result) == 1
        assert result[0]['label'] == "Delta Colony: Population (2000)"


class TestGetInventoryItems:
    """Tests for CargoTransferService.get_inventory_items()"""

    def test_get_inventory_items_fleet(self):
        """Fleet object (has passengers_current) returns passenger items."""
        # Arrange
        fleet_info = MagicMock()
        fleet_info.passengers_current = 2500

        # Act
        result = CargoTransferService.get_inventory_items(fleet_info)

        # Assert
        assert len(result) == 1
        assert result[0]['label'] == "Passengers (2500)"
        assert result[0]['cargo_type'] == 'passengers'
        assert result[0]['species_id'] is None
        assert result[0]['max_amount'] == 2500

    def test_get_inventory_items_colony(self):
        """Colony object (has population_details) returns population items."""
        # Arrange
        colony_info = MagicMock(spec=['population_details'])
        colony_info.population_details = [
            ("Human", 4000, 75),
            ("Mrrshan", 2000, 85),
        ]

        # Act
        result = CargoTransferService.get_inventory_items(colony_info)

        # Assert
        assert len(result) == 2
        assert result[0]['label'] == "Population: Human (4000)"
        assert result[0]['species_id'] == "Human"
        assert result[0]['max_amount'] == 4000

        assert result[1]['label'] == "Population: Mrrshan (2000)"
        assert result[1]['species_id'] == "Mrrshan"

    def test_get_inventory_items_planet_fallback(self):
        """Planet without population_details uses total_population."""
        # Arrange
        planet_info = MagicMock(spec=['total_population'])
        planet_info.total_population = 7500

        # Act
        result = CargoTransferService.get_inventory_items(planet_info)

        # Assert
        assert len(result) == 1
        assert result[0]['label'] == "Population (7500)"
        assert result[0]['species_id'] is None
        assert result[0]['max_amount'] == 7500

    def test_get_inventory_items_none_returns_empty(self):
        """None input returns empty list."""
        # Act
        result = CargoTransferService.get_inventory_items(None)

        # Assert
        assert len(result) == 0

    def test_get_inventory_items_fleet_zero_passengers(self):
        """Fleet with zero passengers returns empty list."""
        # Arrange
        fleet_info = MagicMock()
        fleet_info.passengers_current = 0

        # Act
        result = CargoTransferService.get_inventory_items(fleet_info)

        # Assert
        assert len(result) == 0


class TestBuildTransferCommand:
    """Tests for CargoTransferService.build_transfer_command()"""

    def test_build_transfer_command_normal_amount(self):
        """Amount less than max passes through unchanged."""
        # Act
        cmd = CargoTransferService.build_transfer_command(
            fleet_id=1,
            planet_id=10,
            cargo_type='passengers',
            direction='unload',
            amount=500,
            max_amount=1000,
            species_id='Human'
        )

        # Assert
        assert isinstance(cmd, IssueTransferCommand)
        assert cmd.fleet_id == 1
        assert cmd.planet_id == 10
        assert cmd.cargo_type == 'passengers'
        assert cmd.direction == 'unload'
        assert cmd.amount == 500
        assert cmd.species_id == 'Human'

    def test_build_transfer_command_max_becomes_zero(self):
        """Amount >= max becomes 0 (engine convention for 'all')."""
        # Act
        cmd = CargoTransferService.build_transfer_command(
            fleet_id=1,
            planet_id=10,
            cargo_type='passengers',
            direction='load',
            amount=1000,
            max_amount=1000,
            species_id=None
        )

        # Assert
        assert cmd.amount == 0  # Engine convention

    def test_build_transfer_command_amount_exceeds_max(self):
        """Amount > max also becomes 0."""
        # Act
        cmd = CargoTransferService.build_transfer_command(
            fleet_id=2,
            planet_id=20,
            cargo_type='passengers',
            direction='unload',
            amount=1500,  # Exceeds max
            max_amount=1000,
            species_id=None
        )

        # Assert
        assert cmd.amount == 0

    def test_build_transfer_command_species_id_optional(self):
        """species_id defaults to None when not provided."""
        # Act
        cmd = CargoTransferService.build_transfer_command(
            fleet_id=1,
            planet_id=10,
            cargo_type='passengers',
            direction='load',
            amount=100,
            max_amount=500
        )

        # Assert
        assert cmd.species_id is None
