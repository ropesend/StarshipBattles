"""
Unit tests for ColonizeMissionCommandHandler pod validation.

PROJ-140 Phase 4: Tests that mission handler validates pod match before queuing orders.
"""
import pytest
from unittest.mock import MagicMock, PropertyMock

from game.core.validation import ValidationResult
from game.strategy.engine.command_handlers import ColonizeMissionCommandHandler
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import FleetOrder, OrderType
from game.core.hex_math import HexCoord
from game.strategy.data.ship_instance import ShipInstance


def make_colony_ship(planet_type: str, owner_id: int, instance_id: str = "colony-ship-1") -> ShipInstance:
    """Create a ship with a drop pod in carried_items."""
    ship = ShipInstance(
        instance_id=instance_id,
        design_id=f"{planet_type}_colony_ship",
        name=f"Colony Ship ({planet_type})",
        owner_id=owner_id,
        design_data={
            'name': f"Colony Ship ({planet_type})",
            'vehicle_type': 'Ship',
            'stats': {'mass': 100},
            'layers': {
                'HULL': [{'id': 'colony_pod_bay'}]
            }
        },
    )
    ship.carried_items.append({
        "vehicle_type": "drop_pod",
        "design_id": f"{planet_type.lower()}_drop_pod",
        "name": f"Drop Pod ({planet_type})",
        "design_data": {"layers": {"CORE": []}},
        "mass": 500,
    })
    return ship


def make_mock_planet(planet_type_name: str, planet_id: int = 1):
    """Create a mock planet with specified type."""
    from game.strategy.data.planet import Planet

    # PROJ-193: Set all IPlanet protocol properties for spec=Planet mocks
    planet = MagicMock(spec=Planet)
    planet.id = planet_id
    planet.name = f"Test Planet {planet_id}"
    planet.location = HexCoord(0, 0)
    planet.owner_id = None
    planet.deposits = {}

    # Create planet_type mock
    planet_type = MagicMock()
    planet_type.name = planet_type_name
    planet.planet_type = planet_type

    # PROJ-193: Required IPlanet properties
    planet.populations = []
    planet.max_population = 1000
    planet.facilities = []
    planet.atmosphere = {}
    planet.surface_gravity = 9.8
    planet.surface_temperature = 300.0
    planet.orbit_distance = 1
    planet.radius_hexes = 0
    planet.image_id = ""

    return planet


def make_mock_session(fleet, planet=None, component_registry=None):
    """Create a mock session with the given fleet and optional planet."""
    session = MagicMock()

    # Mock _get_fleet_by_id
    session._get_fleet_by_id.return_value = fleet

    # Mock _get_planet_by_id
    if planet:
        session._get_planet_by_id.return_value = planet
    else:
        session._get_planet_by_id.return_value = None

    # Mock galaxy for pathfinding
    session.galaxy = MagicMock()

    # Mock registries (public API)
    if component_registry is not None:
        registries = MagicMock()
        registries.components = component_registry
        session.registries = registries
    else:
        session.registries = MagicMock()
        session.registries.components = {}

    return session


def make_component_registry():
    """Create a component registry with colony pod definitions."""
    return {
        'colony_pod': {
            'abilities': {
                'ColonizePlanet': True
            }
        },
        'colony_pod': {
            'abilities': {
                'ColonizePlanet': True
            }
        },
        'gas_giant_colony_pod': {
            'abilities': {
                'ColonizePlanet': 'GAS_GIANT'
            }
        }
    }


class TestColonizeMissionHandlerPodValidation:
    """Tests for pod validation in ColonizeMissionCommandHandler."""

    def test_mission_accepts_universal_drop_pod(self):
        """Phase 3: Any drop pod works on any planet type."""
        # Create fleet with any drop pod (originally labelled CONTINENTAL)
        fleet = Fleet(1, owner_id=1, location=HexCoord(0, 0), speed=10.0)
        fleet.ships = [make_colony_ship("CONTINENTAL", owner_id=1)]

        # Create ICE_DWARF planet -- drop pods are universal
        planet = make_mock_planet("ICE_DWARF", planet_id=1)

        # Create mock session with component registry
        registry = make_component_registry()
        session = make_mock_session(fleet, planet, registry)

        # Create command
        cmd = MagicMock()
        cmd.fleet_id = 1
        cmd.planet_id = 1
        cmd.target_hex = HexCoord(5, 0)

        # Execute handler
        handler = ColonizeMissionCommandHandler()
        result = handler.execute(session, cmd)

        # Phase 3: Drop pods are universal -- should accept
        assert result.is_valid is True

    def test_mission_accepts_matching_pod(self):
        """Fleet with ICE_DWARF pod can queue mission to ICE_DWARF planet."""
        # Create fleet with ICE_DWARF colony pod
        fleet = Fleet(1, owner_id=1, location=HexCoord(0, 0), speed=10.0)
        fleet.ships = [make_colony_ship("ICE_DWARF", owner_id=1)]

        # Create ICE_DWARF planet
        planet = make_mock_planet("ICE_DWARF", planet_id=1)

        # Create mock session with component registry
        registry = make_component_registry()
        session = make_mock_session(fleet, planet, registry)

        # Create command
        cmd = MagicMock()
        cmd.fleet_id = 1
        cmd.planet_id = 1
        cmd.target_hex = HexCoord(5, 0)

        # Execute handler
        handler = ColonizeMissionCommandHandler()
        result = handler.execute(session, cmd)

        # Should accept - matching pod type
        assert result.is_valid is True

    def test_mission_accepts_exhausted_pods_at_command_time(self):
        """Fleet with 1 pod and existing order succeeds — pod check deferred to execution."""
        # Create fleet with 1 ICE_DWARF colony pod
        fleet = Fleet(1, owner_id=1, location=HexCoord(0, 0), speed=10.0)
        fleet.ships = [make_colony_ship("ICE_DWARF", owner_id=1)]

        # Add existing COLONIZE order for ICE_DWARF planet
        existing_planet = make_mock_planet("ICE_DWARF", planet_id=99)
        fleet.add_order(FleetOrder(OrderType.COLONIZE, target=existing_planet))

        # Create new ICE_DWARF planet target
        planet = make_mock_planet("ICE_DWARF", planet_id=1)

        # Create mock session with component registry
        registry = make_component_registry()
        session = make_mock_session(fleet, planet, registry)

        # Create command
        cmd = MagicMock()
        cmd.fleet_id = 1
        cmd.planet_id = 1
        cmd.target_hex = HexCoord(5, 0)

        # Execute handler
        handler = ColonizeMissionCommandHandler()
        result = handler.execute(session, cmd)

        # Pod availability is checked at execution time, not command time
        assert result.is_valid is True

    def test_mission_with_none_planet_skips_pod_check(self):
        """Fleet with any pod can queue mission to 'any planet' (planet_id=None)."""
        # Create fleet with CONTINENTAL colony pod
        fleet = Fleet(1, owner_id=1, location=HexCoord(0, 0), speed=10.0)
        fleet.ships = [make_colony_ship("CONTINENTAL", owner_id=1)]

        # Create mock session with component registry (no planet)
        registry = make_component_registry()
        session = make_mock_session(fleet, planet=None, component_registry=registry)

        # Create command with planet_id=None ("any planet")
        cmd = MagicMock()
        cmd.fleet_id = 1
        cmd.planet_id = None  # "Any planet"
        cmd.target_hex = HexCoord(5, 0)

        # Execute handler
        handler = ColonizeMissionCommandHandler()
        result = handler.execute(session, cmd)

        # Should accept - can't validate without knowing target
        assert result.is_valid is True

    def test_mission_no_pods_succeeds_at_command_time(self):
        """Fleet with zero colony pods succeeds at command time — pod check deferred to execution."""
        # Create fleet with NO colony pods (just a regular ship)
        fleet = Fleet(1, owner_id=1, location=HexCoord(0, 0), speed=10.0)
        regular_ship = ShipInstance(
            instance_id="destroyer-1",
            design_id="destroyer",
            name="Destroyer",
            owner_id=1,
            design_data={
                'name': "Destroyer",
                'vehicle_type': 'Ship',
                'stats': {'mass': 50},
                'layers': {'HULL': [{'id': 'laser'}]}
            },
        )
        fleet.ships = [regular_ship]

        # Create CONTINENTAL planet
        planet = make_mock_planet("CONTINENTAL", planet_id=1)

        # Create mock session with component registry
        registry = make_component_registry()
        session = make_mock_session(fleet, planet, registry)

        # Create command
        cmd = MagicMock()
        cmd.fleet_id = 1
        cmd.planet_id = 1
        cmd.target_hex = HexCoord(5, 0)

        # Execute handler
        handler = ColonizeMissionCommandHandler()
        result = handler.execute(session, cmd)

        # Pod availability is checked at execution time, not command time
        assert result.is_valid is True
