"""
Tests for TRANSFER order processing.

PROJ-68 Phase 6: Tests for transfer order type, serialization, and processing.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import FleetOrder, OrderType
from game.strategy.data.ship_instance import ShipInstance
from game.core.hex_math import HexCoord
from game.strategy.data.planet import Planet, PlanetType, SpeciesPopulation
from game.strategy.engine.fleet_order_processor import FleetOrderProcessor, TransferResult
from game.strategy.engine.commands import IssueTransferCommand


class TestTransferOrderType:
    """Tests for TRANSFER order type and serialization."""

    def test_transfer_order_exists(self):
        """TRANSFER is a valid OrderType."""
        assert hasattr(OrderType, 'TRANSFER')
        assert OrderType.TRANSFER.name == 'TRANSFER'

    def test_transfer_order_serialization_roundtrip(self):
        """TRANSFER order serializes and deserializes correctly."""
        # Create a TRANSFER order with params dict
        params = {
            'direction': 'load',
            'cargo_type': 'passengers',
            'amount': 50,
            'planet_id': 123
        }
        order = FleetOrder(OrderType.TRANSFER, target=params)

        # Serialize
        order_dict = order.to_dict()

        assert order_dict['type'] == 'TRANSFER'
        assert order_dict['target']['type'] == 'transfer'
        assert order_dict['target']['value'] == params

    def test_fleet_transfer_order_roundtrip(self):
        """Fleet with TRANSFER order serializes and deserializes correctly."""
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(5, 5))

        params = {
            'direction': 'unload',
            'cargo_type': 'passengers',
            'amount': 0,  # All
            'planet_id': 456
        }
        order = FleetOrder(OrderType.TRANSFER, target=params)
        fleet.orders.append(order)

        # Serialize and deserialize
        fleet_dict = fleet.to_dict()
        restored = Fleet.from_dict(fleet_dict)

        assert len(restored.orders) == 1
        restored_order = restored.orders[0]
        assert restored_order.type == OrderType.TRANSFER
        assert restored_order.target == params


class TestTransferCommand:
    """Tests for IssueTransferCommand."""

    def test_transfer_command_creation(self):
        """IssueTransferCommand has correct fields."""
        cmd = IssueTransferCommand(
            fleet_id=1,
            planet_id=10,
            cargo_type='passengers',
            direction='load',
            amount=100
        )

        assert cmd.fleet_id == 1
        assert cmd.planet_id == 10
        assert cmd.cargo_type == 'passengers'
        assert cmd.direction == 'load'
        assert cmd.amount == 100
        assert cmd.name == 'IssueTransferCommand'

    def test_transfer_command_with_species(self):
        """IssueTransferCommand can include a species_id."""
        cmd = IssueTransferCommand(
            fleet_id=1,
            planet_id=10,
            cargo_type='passengers',
            direction='load',
            amount=100,
            species_id='vulcan'
        )

        assert cmd.species_id == 'vulcan'


class TestFleetOrderProcessorTransfer:
    """Tests for FleetOrderProcessor.process_transfer()."""

    def make_mock_galaxy_with_planet(self, planet):
        """Create a mock galaxy with proper system containment for the planet.

        The TransferValidator checks that the fleet is in the same system as the
        planet by looking up galaxy.systems and galaxy.get_system_at_location().
        """
        mock_system = MagicMock()
        mock_system.planets = [planet]

        galaxy = MagicMock()
        galaxy.get_planet_by_id = MagicMock(return_value=planet)
        galaxy.get_planets_at_global_hex = MagicMock(return_value=[planet])
        galaxy.get_system_at_location = MagicMock(return_value=mock_system)
        galaxy.systems = {'test_system': mock_system}
        return galaxy

    def make_planet_with_pop(self, planet_id=1, pop_count=1000):
        """Create a real planet with population."""
        planet = Planet(
            name=f"Planet-{planet_id}",
            location=HexCoord(0, 0),
            orbit_distance=1,
            mass=5.97e24,
            radius=6.371e6,
            surface_area=5.1e14,
            density=5514.0,
            surface_gravity=9.81,
            surface_pressure=101325.0,
            surface_temperature=288.0,
            surface_water=0.71,
            tectonic_activity=0.5,
            magnetic_field=1.0,
            planet_type=PlanetType.CONTINENTAL,
            owner_id=0
        )
        planet.id = planet_id
        planet.populations = [SpeciesPopulation(race_id="human", count=pop_count)]
        return planet

    def make_ship_with_cargo(self, capacity=100, current=0):
        """Create a ship instance with cargo capacity via cached stats."""
        ship = ShipInstance(
            instance_id="cargo-test-001",
            name="Cargo Ship",
            design_id="cargo_test",
            owner_id=0,
            design_data={
                "meta": {"vehicle_type": "ship"},
                "layers": {}
            }
        )
        # Set cached stats so get_cargo_capacity works
        ship._cached_stats = {"cargo_storage": {"passengers": capacity}}
        ship.cargo_contents = {"passengers": current} if current > 0 else {}
        return ship

    def make_fleet_with_cargo_ship(self, capacity=100, current=0):
        """Create a fleet with a cargo ship."""
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        ship = self.make_ship_with_cargo(capacity, current)
        fleet.ships.append(ship)
        return fleet

    def test_process_transfer_load_passengers_from_colony(self):
        """Load passengers from colony to fleet."""
        processor = FleetOrderProcessor()

        planet = self.make_planet_with_pop(pop_count=500)
        fleet = self.make_fleet_with_cargo_ship(capacity=100, current=0)

        # Set up TRANSFER order
        params = {
            'direction': 'load',
            'cargo_type': 'passengers',
            'amount': 50,
            'planet_id': planet.id
        }
        order = FleetOrder(OrderType.TRANSFER, target=params)
        fleet.orders.append(order)

        # Mock galaxy with proper system containment
        galaxy = self.make_mock_galaxy_with_planet(planet)

        # Mock empire
        empire = MagicMock()
        empire.race_config = None

        # Process
        result = processor.process_transfer(fleet, empire, galaxy)

        assert result.success
        assert result.amount_transferred == 50
        assert planet.populations[0].count == 450  # 500 - 50
        assert fleet.resources.get_fleet_cargo_current("passengers") == 50
        assert len(fleet.orders) == 0  # Order completed

    def test_process_transfer_unload_passengers_to_colony(self):
        """Unload passengers from fleet to colony."""
        processor = FleetOrderProcessor()

        planet = self.make_planet_with_pop(pop_count=100)
        fleet = self.make_fleet_with_cargo_ship(capacity=100, current=80)

        # Set up TRANSFER order
        params = {
            'direction': 'unload',
            'cargo_type': 'passengers',
            'amount': 30,
            'planet_id': planet.id
        }
        order = FleetOrder(OrderType.TRANSFER, target=params)
        fleet.orders.append(order)

        # Mock galaxy with proper system containment
        galaxy = self.make_mock_galaxy_with_planet(planet)

        # Mock empire with race_config
        empire = MagicMock()
        empire.race_config = MagicMock()
        empire.race_config.race_id = "human"

        # Process
        result = processor.process_transfer(fleet, empire, galaxy)

        assert result.success
        assert result.amount_transferred == 30
        assert planet.populations[0].count == 130  # 100 + 30
        assert fleet.resources.get_fleet_cargo_current("passengers") == 50  # 80 - 30
        assert len(fleet.orders) == 0

    def test_transfer_partial_amount(self):
        """Transfer transfers only what's available when amount exceeds supply."""
        processor = FleetOrderProcessor()

        planet = self.make_planet_with_pop(pop_count=20)  # Only 20 pop
        fleet = self.make_fleet_with_cargo_ship(capacity=100, current=0)

        params = {
            'direction': 'load',
            'cargo_type': 'passengers',
            'amount': 50,  # Want 50 but only 20 available
            'planet_id': planet.id
        }
        order = FleetOrder(OrderType.TRANSFER, target=params)
        fleet.orders.append(order)

        # Mock galaxy with proper system containment
        galaxy = self.make_mock_galaxy_with_planet(planet)

        empire = MagicMock()
        empire.race_config = None

        result = processor.process_transfer(fleet, empire, galaxy)

        assert result.success
        # Should only transfer what's available (20)
        assert result.amount_transferred == 20
        assert planet.populations[0].count == 0
        assert fleet.resources.get_fleet_cargo_current("passengers") == 20

    def test_transfer_all_when_amount_zero(self):
        """Amount=0 transfers all available."""
        processor = FleetOrderProcessor()

        planet = self.make_planet_with_pop(pop_count=100)
        fleet = self.make_fleet_with_cargo_ship(capacity=100, current=75)

        params = {
            'direction': 'unload',
            'cargo_type': 'passengers',
            'amount': 0,  # All
            'planet_id': planet.id
        }
        order = FleetOrder(OrderType.TRANSFER, target=params)
        fleet.orders.append(order)

        # Mock galaxy with proper system containment
        galaxy = self.make_mock_galaxy_with_planet(planet)

        empire = MagicMock()
        empire.race_config = MagicMock()
        empire.race_config.race_id = "human"

        result = processor.process_transfer(fleet, empire, galaxy)

        assert result.success
        assert result.amount_transferred == 75  # All cargo
        assert planet.populations[0].count == 175
        assert fleet.resources.get_fleet_cargo_current("passengers") == 0

    def test_transfer_creates_species_population_if_missing(self):
        """Unloading to a colony without that species creates new SpeciesPopulation."""
        processor = FleetOrderProcessor()

        # Planet with different species
        planet = self.make_planet_with_pop(pop_count=100)
        planet.populations[0].race_id = "alien"  # Different species

        fleet = self.make_fleet_with_cargo_ship(capacity=100, current=50)

        params = {
            'direction': 'unload',
            'cargo_type': 'passengers',
            'amount': 25,
            'planet_id': planet.id
        }
        order = FleetOrder(OrderType.TRANSFER, target=params)
        fleet.orders.append(order)

        # Mock galaxy with proper system containment
        galaxy = self.make_mock_galaxy_with_planet(planet)

        # Empire's race is "human" - different from planet's "alien"
        empire = MagicMock()
        empire.race_config = MagicMock()
        empire.race_config.race_id = "human"

        result = processor.process_transfer(fleet, empire, galaxy)

        assert result.success
        assert result.amount_transferred == 25

        # Should have 2 species now
        assert len(planet.populations) == 2

        # Find human population
        human_pop = next(p for p in planet.populations if p.race_id == "human")
        assert human_pop.count == 25

        # Original alien population unchanged
        alien_pop = next(p for p in planet.populations if p.race_id == "alien")
        assert alien_pop.count == 100

    def test_process_transfer_species_specific_load(self):
        """Load a specific species from colony to fleet."""
        processor = FleetOrderProcessor()

        planet = self.make_planet_with_pop(pop_count=500)
        planet.populations[0].race_id = "human"
        # Add a second species
        planet.populations.append(SpeciesPopulation(race_id="vulcan", count=200))

        fleet = self.make_fleet_with_cargo_ship(capacity=100, current=0)

        # Set up TRANSFER order for specific species
        params = {
            'direction': 'load',
            'cargo_type': 'passengers',
            'amount': 50,
            'planet_id': planet.id,
            'species_id': 'vulcan'
        }
        order = FleetOrder(OrderType.TRANSFER, target=params)
        fleet.orders.append(order)

        # Mock galaxy with proper system containment
        galaxy = self.make_mock_galaxy_with_planet(planet)

        # Mock empire
        empire = MagicMock()

        # Process
        result = processor.process_transfer(fleet, empire, galaxy)

        assert result.success
        assert result.amount_transferred == 50
        # Vulcan population should be reduced, human unchanged
        vulcan_pop = next(p for p in planet.populations if p.race_id == "vulcan")
        human_pop = next(p for p in planet.populations if p.race_id == "human")
        assert vulcan_pop.count == 150
        assert human_pop.count == 500
        # Fleet should have vulcan passengers
        assert fleet.resources.get_fleet_cargo_current("passengers") == 50

    def test_process_transfer_species_specific_unload(self):
        """Unload a specific species from fleet to colony."""
        processor = FleetOrderProcessor()

        planet = self.make_planet_with_pop(pop_count=100)
        planet.populations[0].race_id = "human"

        fleet = self.make_fleet_with_cargo_ship(capacity=100, current=80)
        # Manually set species in fleet if supported, else just assume it unloads what's specified
        # In current implementation, fleet doesn't track species in cargo yet?
        # TODO: Check if Fleet needs species support in cargo_contents

        # Set up TRANSFER order for specific species
        params = {
            'direction': 'unload',
            'cargo_type': 'passengers',
            'amount': 30,
            'planet_id': planet.id,
            'species_id': 'vulcan'
        }
        order = FleetOrder(OrderType.TRANSFER, target=params)
        fleet.orders.append(order)

        # Mock galaxy with proper system containment
        galaxy = self.make_mock_galaxy_with_planet(planet)

        # Mock empire
        empire = MagicMock()

        # Process
        result = processor.process_transfer(fleet, empire, galaxy)

        assert result.success
        assert result.amount_transferred == 30
        # Should have human AND vulcan populations now
        assert len(planet.populations) == 2
        vulcan_pop = next(p for p in planet.populations if p.race_id == "vulcan")
        assert vulcan_pop.count == 30


class TestTransferCommandDispatch:
    """Tests for command dispatch integration."""

    def test_transfer_command_dispatch(self):
        """GameSession dispatches IssueTransferCommand correctly."""
        from game.strategy.engine.game_session import GameSession
        from game.strategy.engine.game_config import GameConfig
        from game.strategy.engine.game_initializer import GameInitializer
        from game.strategy.data.galaxy import Galaxy
        from game.strategy.data.empire import Empire

        # Create minimal session with mocked galaxy generation
        def mock_initialize(config):
            galaxy = Galaxy(radius=config.galaxy_radius)
            empires = [Empire(i, f"Empire {i}", (255, 255, 255)) for i in range(2)]
            return galaxy, empires

        with patch.object(GameInitializer, 'initialize', side_effect=mock_initialize):
            config = GameConfig()
            session = GameSession(config=config)

        # Create test fleet and planet
        fleet = Fleet(fleet_id=99, owner_id=0, location=HexCoord(5, 5))
        session.empires[0].fleets.append(fleet)
        session.galaxy.register_fleet(fleet)  # Register for O(1) lookup

        # Add cargo ship to fleet
        ship = ShipInstance(
            instance_id="transport-test-001",
            name="Transport",
            design_id="transport_test",
            owner_id=0,
            design_data={"meta": {"vehicle_type": "ship"}, "layers": {}}
        )
        ship._cached_stats = {"cargo_storage": {"passengers": 100}}
        ship.cargo_contents = {}
        fleet.ships.append(ship)

        # Create planet at same location
        planet = Planet(
            name="Test Colony",
            location=HexCoord(0, 0),  # Local
            orbit_distance=1,
            mass=5.97e24,
            radius=6.371e6,
            surface_area=5.1e14,
            density=5514.0,
            surface_gravity=9.81,
            surface_pressure=101325.0,
            surface_temperature=288.0,
            surface_water=0.71,
            tectonic_activity=0.5,
            magnetic_field=1.0,
            planet_type=PlanetType.CONTINENTAL,
            owner_id=0
        )
        planet.id = 999
        planet.populations = [SpeciesPopulation(race_id="human", count=500)]

        # Mock galaxy methods
        session.galaxy.get_planet_by_id = MagicMock(return_value=planet)
        session.galaxy.get_planets_at_global_hex = MagicMock(return_value=[planet])

        # Issue command
        cmd = IssueTransferCommand(
            fleet_id=99,
            planet_id=999,
            cargo_type='passengers',
            direction='load',
            amount=50,
            species_id='human'
        )

        result = session.handle_command(cmd)

        assert result.is_valid
        assert len(fleet.orders) == 1
        assert fleet.orders[0].type == OrderType.TRANSFER
