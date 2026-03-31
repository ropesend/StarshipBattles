"""Unit tests for CargoTransferService.

PROJ-162: Tests for cargo transfer business logic extracted from UI dialogs.
"""

import pytest
from unittest.mock import MagicMock, PropertyMock

from game.core.hex_math import HexCoord
from game.strategy.services.cargo_transfer_service import CargoTransferService
from game.strategy.engine.commands import IssueTransferCommand
from game.strategy.facade.dto.fleet_dto import FleetInfo
from game.strategy.facade.dto.planet_dto import PlanetInfo


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

    # NOTE: test_resolve_colonies_no_fallback_if_fleet_has_no_location removed
    # Fleet always has location attribute - testing "fleet without location" is obsolete


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

        # PlanetInfo always has population_details (empty tuple means fallback to total_population)
        planet_info = MagicMock()
        planet_info.population_details = ()  # Empty - triggers fallback
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
        """FleetInfo with passengers returns passenger items."""
        # Arrange
        fleet_info = FleetInfo(
            fleet_id=1, owner_id=1, location=HexCoord(0, 0),
            speed=5.0, ship_count=1, passengers_current=2500
        )

        # Act
        result = CargoTransferService.get_inventory_items(fleet_info)

        # Assert
        assert len(result) == 1
        assert result[0]['label'] == "Passengers (2500)"
        assert result[0]['cargo_type'] == 'passengers'
        assert result[0]['species_id'] is None
        assert result[0]['max_amount'] == 2500

    def test_get_inventory_items_colony(self):
        """PlanetInfo with population_details returns population items."""
        # Arrange
        planet_info = PlanetInfo(
            planet_id=1, name="Test", planet_type="TERRESTRIAL",
            location=HexCoord(0, 0), orbit_distance=1,
            population_details=(
                ("Human", 4000, 75.0),
                ("Mrrshan", 2000, 85.0),
            )
        )

        # Act
        result = CargoTransferService.get_inventory_items(planet_info)

        # Assert
        assert len(result) == 2
        assert result[0]['label'] == "Population: Human (4000)"
        assert result[0]['species_id'] == "Human"
        assert result[0]['max_amount'] == 4000

        assert result[1]['label'] == "Population: Mrrshan (2000)"
        assert result[1]['species_id'] == "Mrrshan"

    def test_get_inventory_items_planet_fallback(self):
        """PlanetInfo without population_details uses total_population."""
        # Arrange
        planet_info = PlanetInfo(
            planet_id=1, name="Test", planet_type="TERRESTRIAL",
            location=HexCoord(0, 0), orbit_distance=1,
            total_population=7500  # No population_details
        )

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
        """FleetInfo with zero passengers returns empty list."""
        # Arrange
        fleet_info = FleetInfo(
            fleet_id=1, owner_id=1, location=HexCoord(0, 0),
            speed=5.0, ship_count=1, passengers_current=0
        )

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


class TestGetInventoryItemsResources:
    """Tests for resource items in CargoTransferService.get_inventory_items()."""

    def test_planet_with_stockpile_returns_resource_items(self):
        """PlanetInfo with stockpile data returns resource items."""
        planet_info = PlanetInfo(
            planet_id=1, name="Test", planet_type="TERRESTRIAL",
            location=HexCoord(0, 0), orbit_distance=1,
            stockpile=(("metals", 500.0), ("organics", 200.0)),
        )

        result = CargoTransferService.get_inventory_items(planet_info)

        resource_items = [r for r in result if r['cargo_type'] != 'passengers']
        assert len(resource_items) == 2
        metals_item = next(r for r in resource_items if r['cargo_type'] == 'metals')
        assert metals_item['max_amount'] == 500
        assert 'Metals' in metals_item['label'] or 'metals' in metals_item['label']

    def test_planet_with_population_and_stockpile_returns_both(self):
        """PlanetInfo with both population and stockpile returns all items."""
        planet_info = PlanetInfo(
            planet_id=1, name="Test", planet_type="TERRESTRIAL",
            location=HexCoord(0, 0), orbit_distance=1,
            population_details=(("Human", 1000, 75.0),),
            stockpile=(("metals", 300.0),),
        )

        result = CargoTransferService.get_inventory_items(planet_info)

        passenger_items = [r for r in result if r['cargo_type'] == 'passengers']
        resource_items = [r for r in result if r['cargo_type'] != 'passengers']
        assert len(passenger_items) == 1
        assert len(resource_items) == 1

    def test_planet_empty_stockpile_returns_no_resource_items(self):
        """PlanetInfo with empty stockpile returns no resource items."""
        planet_info = PlanetInfo(
            planet_id=1, name="Test", planet_type="TERRESTRIAL",
            location=HexCoord(0, 0), orbit_distance=1,
        )

        result = CargoTransferService.get_inventory_items(planet_info)

        resource_items = [r for r in result if r['cargo_type'] != 'passengers']
        assert len(resource_items) == 0

    def test_fleet_with_cargo_resources_returns_items(self):
        """FleetInfo with cargo resources returns resource items."""
        fleet_info = FleetInfo(
            fleet_id=1, owner_id=1, location=HexCoord(0, 0),
            speed=5.0, ship_count=1,
            cargo_resources=(("metals", 300), ("fuel", 100)),
            cargo_capacities=(("metals", 1000), ("fuel", 500)),
        )

        result = CargoTransferService.get_inventory_items(fleet_info)

        resource_items = [r for r in result if r['cargo_type'] != 'passengers']
        assert len(resource_items) >= 2
        metals_item = next(r for r in resource_items if r['cargo_type'] == 'metals')
        assert metals_item['max_amount'] == 300

    def test_fleet_shows_all_capacity_types_even_empty(self):
        """FleetInfo with cargo capacity but zero current shows item with 0."""
        fleet_info = FleetInfo(
            fleet_id=1, owner_id=1, location=HexCoord(0, 0),
            speed=5.0, ship_count=1,
            cargo_resources=(("metals", 0),),
            cargo_capacities=(("metals", 1000),),
        )

        result = CargoTransferService.get_inventory_items(fleet_info)

        resource_items = [r for r in result if r['cargo_type'] == 'metals']
        assert len(resource_items) == 1
        assert resource_items[0]['max_amount'] == 0
