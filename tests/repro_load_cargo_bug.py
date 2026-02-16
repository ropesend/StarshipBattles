"""
Diagnostic test to reproduce the 'load cargo order not appearing' bug.

This test exercises the full IssueTransferCommand -> TransferCommandHandler.execute
flow with a ship that has CargoStorage passengers capacity.
"""
import unittest
from unittest.mock import MagicMock, PropertyMock, patch
from game.core.hex_math import HexCoord
from game.strategy.engine.commands import IssueTransferCommand
from game.strategy.engine.command_handlers import TransferCommandHandler
from game.strategy.validation.transfer_validator import TransferValidator
from game.strategy.data.planet import Planet, PlanetType, SpeciesPopulation
from game.strategy.data.fleet import Fleet
from game.core.validation import ValidationResult


class TestReproLoadCargoBug(unittest.TestCase):
    """Reproduce the exact scenario: fleet with passenger capacity at a colony."""

    def _make_fleet(self, fleet_id=1, location=HexCoord(5, 5),
                    passenger_capacity=5000, passengers_current=0):
        """Create a mock fleet with passenger CargoStorage."""
        fleet = MagicMock(spec=Fleet)
        fleet.id = fleet_id
        fleet.location = location
        fleet.ships = []
        fleet.orders = []
        fleet.get_fleet_cargo_capacity = MagicMock(return_value=passenger_capacity)
        fleet.get_fleet_cargo_current = MagicMock(return_value=passengers_current)
        return fleet

    def _make_planet(self, planet_id=1, name="TestColony", owner_id=0,
                     location=HexCoord(0, 0), population=1000):
        """Create a mock Planet with population."""
        planet = MagicMock(spec=Planet)
        planet.id = planet_id
        planet.name = name
        planet.owner_id = owner_id
        planet.location = location
        planet.planet_type = PlanetType.CONTINENTAL
        planet.resources = {}
        planet.total_population = population
        planet.populations = [MagicMock(race_id="Human", count=population, happiness=0.8)] if population > 0 else []
        return planet

    def _make_galaxy(self, system_location=HexCoord(5, 5), planets=None):
        """Create a mock galaxy with a system containing planets."""
        galaxy = MagicMock()
        system = MagicMock()
        system.global_location = system_location
        system.planets = planets or []
        galaxy.systems = {'sys1': system}
        
        def get_system_at_location(loc):
            if loc == system_location:
                return system
            return None
        galaxy.get_system_at_location = MagicMock(side_effect=get_system_at_location)
        return galaxy, system

    def _make_session(self, fleet, planet, galaxy, empire=None):
        """Create a mock GameSession."""
        session = MagicMock()
        session.galaxy = galaxy
        
        if empire is None:
            empire = MagicMock()
            empire.fleets = [fleet]
        
        session.empires = [empire]
        session._get_fleet_by_id = MagicMock(return_value=fleet)
        session._get_planet_by_id = MagicMock(return_value=planet)
        return session

    def test_load_cargo_via_command_handler(self):
        """Test the full command handler flow for loading passengers."""
        # Setup
        planet = self._make_planet(planet_id=1, population=1000)
        fleet = self._make_fleet(fleet_id=1, passenger_capacity=5000, passengers_current=0)
        galaxy, system = self._make_galaxy(planets=[planet])
        session = self._make_session(fleet, planet, galaxy)

        # Create command
        cmd = IssueTransferCommand(
            fleet_id=1,
            planet_id=1,
            cargo_type='passengers',
            direction='load',
            amount=0,  # 0 = "all"
            species_id='Human'
        )

        # Execute via handler
        handler = TransferCommandHandler()
        result = handler.execute(session, cmd)

        # Diagnostic output
        print(f"\n=== DIAGNOSTIC ===")
        print(f"Result valid: {result.is_valid}")
        print(f"Result errors: {result.errors}")
        print(f"Result message: {result.message}")
        print(f"Fleet capacity call: {fleet.get_fleet_cargo_capacity.call_args}")
        print(f"Fleet current call: {fleet.get_fleet_cargo_current.call_args}")

        # Assert
        self.assertTrue(result.is_valid, f"Transfer should be valid but got: {result.message}")

    def test_validator_directly(self):
        """Test the validator directly with the same parameters."""
        planet = self._make_planet(planet_id=1, population=1000)
        fleet = self._make_fleet(fleet_id=1, passenger_capacity=5000, passengers_current=0)
        galaxy, system = self._make_galaxy(planets=[planet])

        result = TransferValidator.validate(
            galaxy=galaxy,
            fleet=fleet,
            target=planet,
            cargo_type='passengers',
            direction='load',
            amount=0,
            species_id='Human',
            skip_location_check=True,
            projected_cargo=0
        )

        print(f"\n=== VALIDATOR DIRECT ===")
        print(f"Result valid: {result.is_valid}")
        print(f"Result errors: {result.errors}")
        print(f"Result message: {result.message}")

        self.assertTrue(result.is_valid, f"Validation should pass: {result.message}")

    def test_validator_no_projected_cargo(self):
        """Test validator when projected_cargo is NOT provided (uses fleet.get_fleet_cargo_current)."""
        planet = self._make_planet(planet_id=1, population=1000)
        fleet = self._make_fleet(fleet_id=1, passenger_capacity=5000, passengers_current=0)
        galaxy, system = self._make_galaxy(planets=[planet])

        result = TransferValidator.validate(
            galaxy=galaxy,
            fleet=fleet,
            target=planet,
            cargo_type='passengers',
            direction='load',
            amount=0,
            species_id='Human',
            skip_location_check=True,
            # No projected_cargo — will use fleet.get_fleet_cargo_current
        )

        print(f"\n=== VALIDATOR NO PROJECTED ===")
        print(f"Result valid: {result.is_valid}")
        print(f"Result errors: {result.errors}")

        self.assertTrue(result.is_valid, f"Validation should pass: {result.message}")

    def test_command_handler_fleet_not_found(self):
        """What happens if fleet lookup fails?"""
        planet = self._make_planet(planet_id=1, population=1000)
        fleet = self._make_fleet(fleet_id=1)
        galaxy, system = self._make_galaxy(planets=[planet])
        
        session = MagicMock()
        session.galaxy = galaxy
        session._get_fleet_by_id = MagicMock(return_value=None)  # Fleet not found!
        
        cmd = IssueTransferCommand(
            fleet_id=1, planet_id=1, cargo_type='passengers',
            direction='load', amount=0, species_id='Human'
        )
        
        handler = TransferCommandHandler()
        result = handler.execute(session, cmd)
        
        print(f"\n=== FLEET NOT FOUND ===")
        print(f"Result valid: {result.is_valid}")
        print(f"Result message: {result.message}")
        
        self.assertFalse(result.is_valid)
        self.assertIn("Fleet not found", result.message)

    def test_command_handler_planet_not_found(self):
        """What happens if planet lookup fails?"""
        planet = self._make_planet(planet_id=1, population=1000)
        fleet = self._make_fleet(fleet_id=1)
        galaxy, system = self._make_galaxy(planets=[planet])
        
        session = MagicMock()
        session.galaxy = galaxy
        session._get_fleet_by_id = MagicMock(return_value=fleet)
        session._get_planet_by_id = MagicMock(return_value=None)  # Planet not found!
        empire = MagicMock()
        empire.fleets = [fleet]
        session.empires = [empire]

        cmd = IssueTransferCommand(
            fleet_id=1, planet_id=1, cargo_type='passengers',
            direction='load', amount=0, species_id='Human'
        )
        
        handler = TransferCommandHandler()
        result = handler.execute(session, cmd)
        
        print(f"\n=== PLANET NOT FOUND ===")
        print(f"Result valid: {result.is_valid}")
        print(f"Result message: {result.message}")
        
        self.assertFalse(result.is_valid)
        self.assertIn("Planet not found", result.message)

    def test_command_handler_empire_not_found(self):
        """What happens if owning empire lookup fails?"""
        planet = self._make_planet(planet_id=1, population=1000)
        fleet = self._make_fleet(fleet_id=1)
        galaxy, system = self._make_galaxy(planets=[planet])
        
        session = MagicMock()
        session.galaxy = galaxy
        session._get_fleet_by_id = MagicMock(return_value=fleet)
        session._get_planet_by_id = MagicMock(return_value=planet)
        # No empire owns this fleet!
        other_empire = MagicMock()
        other_empire.fleets = []
        session.empires = [other_empire]

        cmd = IssueTransferCommand(
            fleet_id=1, planet_id=1, cargo_type='passengers',
            direction='load', amount=0, species_id='Human'
        )
        
        handler = TransferCommandHandler()
        result = handler.execute(session, cmd)
        
        print(f"\n=== EMPIRE NOT FOUND ===")
        print(f"Result valid: {result.is_valid}")
        print(f"Result message: {result.message}")
        
        self.assertFalse(result.is_valid)
        self.assertIn("Fleet owner not found", result.message)


if __name__ == '__main__':
    unittest.main(verbosity=2)
