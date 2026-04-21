"""
Tests for BuildContext Protocol compliance.

Verifies that Planet and Fleet both satisfy the BuildContext protocol.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.build_context import BuildContext
from game.strategy.data.planet import Planet
from game.strategy.data.fleet import Fleet
from game.core.hex_math import HexCoord


class TestBuildContextProtocolCompliance:
    """Test that Planet and Fleet satisfy BuildContext protocol."""

    def test_planet_satisfies_build_context_protocol(self, minimal_planet):
        """Planet should satisfy the BuildContext protocol."""
        # Runtime check using isinstance with Protocol
        assert isinstance(minimal_planet, BuildContext)

    def test_fleet_satisfies_build_context_protocol(self, mock_fleet):
        """Fleet should satisfy the BuildContext protocol."""
        # Runtime check using isinstance with Protocol
        assert isinstance(mock_fleet, BuildContext)

class TestBuildContextDuckTyping:
    """Test that BuildContext works with duck typing."""

    def test_function_accepting_build_context_works_with_planet(self, minimal_planet):
        """Functions typed with BuildContext should accept Planet."""

        def get_context_name(ctx: BuildContext) -> str:
            return ctx.name

        result = get_context_name(minimal_planet)
        assert result == minimal_planet.name

    def test_function_accepting_build_context_works_with_fleet(self, mock_fleet):
        """Functions typed with BuildContext should accept Fleet."""

        def get_context_name(ctx: BuildContext) -> str:
            return ctx.name

        result = get_context_name(mock_fleet)
        assert result == mock_fleet.name

    def test_can_build_type_dispatch_by_context(self, minimal_planet, mock_fleet):
        """can_build_type should work polymorphically."""
        # Both should return False for ships when no shipyard
        assert minimal_planet.can_build_type("ship") is False
        # Fleet without yard also returns False
        assert mock_fleet.capabilities.can_build_type("ship") is False

        # Planet can always build complexes
        assert minimal_planet.can_build_type("complex") is True


class TestPlanetCanBuildType:
    """Test Planet.can_build_type() method."""

    def test_planet_can_always_build_complexes(self, minimal_planet):
        """Planet can always build complexes regardless of facilities."""
        assert minimal_planet.can_build_type("complex") is True
        assert minimal_planet.can_build_type("Complex") is True  # Case insensitive

    def test_planet_cannot_build_ships_without_shipyard(self, minimal_planet):
        """Planet without space shipyard cannot build ships."""
        assert minimal_planet.can_build_type("ship") is False

    def test_planet_cannot_build_fighters_without_shipyard(self, minimal_planet):
        """Planet without space shipyard cannot build fighters."""
        assert minimal_planet.can_build_type("fighter") is False

    def test_planet_cannot_build_satellites_without_shipyard(self, minimal_planet):
        """Planet without space shipyard cannot build satellites."""
        assert minimal_planet.can_build_type("satellite") is False

    def test_planet_can_build_ships_with_shipyard(self, planet_with_shipyard):
        """Planet with space shipyard can build ships."""
        assert planet_with_shipyard.can_build_type("ship") is True
        assert planet_with_shipyard.can_build_type("Ship") is True

    def test_planet_can_build_fighters_with_shipyard(self, planet_with_shipyard):
        """Planet with space shipyard can build fighters."""
        assert planet_with_shipyard.can_build_type("fighter") is True

    def test_planet_can_build_satellites_with_shipyard(self, planet_with_shipyard):
        """Planet with space shipyard can build satellites."""
        assert planet_with_shipyard.can_build_type("satellite") is True

    def test_planet_returns_false_for_unknown_types(self, minimal_planet):
        """Planet returns False for unknown vehicle types."""
        assert minimal_planet.can_build_type("unknown") is False
        assert minimal_planet.can_build_type("starbase") is False


class TestFleetContextType:
    """Test Fleet context_type and name properties."""

    def test_fleet_context_type(self, mock_fleet):
        """Fleet.context_type should return 'fleet'."""
        assert mock_fleet.context_type == "fleet"

    def test_fleet_name_empty_fleet(self, mock_fleet):
        """Empty fleet should have descriptive name."""
        assert "Fleet" in mock_fleet.name
        assert "Empty" in mock_fleet.name or str(mock_fleet.id) in mock_fleet.name

    def test_fleet_name_with_ships(self, mock_fleet, mock_ship_instance):
        """Fleet with ships should include ship info in name."""
        mock_fleet.ships.append(mock_ship_instance)
        assert "Fleet" in mock_fleet.name
        assert str(mock_fleet.id) in mock_fleet.name


# Fixtures

@pytest.fixture
def minimal_planet():
    """Create a minimal planet for testing."""
    return Planet(
        name="Test Planet",
        location=HexCoord(0, 0),
        orbit_distance=3,
        mass=5.972e24,
        radius=6.371e6,
        surface_area=5.1e14,
        density=5515,
        surface_gravity=9.8,
        surface_pressure=101325,
        surface_temperature=288,
        surface_water=0.7,
        tectonic_activity=0.5,
        magnetic_field=1.0,
        owner_id=0
    )


@pytest.fixture
def mock_fleet():
    """Create a mock fleet for testing."""
    fleet = Fleet(
        fleet_id=1,
        owner_id=0,
        location=HexCoord(5, 5),
        speed=5.0
    )
    return fleet


@pytest.fixture
def planet_with_shipyard(minimal_planet):
    """Create a planet with an operational space shipyard."""
    from game.strategy.data.planet import PlanetaryFacility

    # Add a facility with space_shipyard ability
    facility = PlanetaryFacility(
        instance_id="test-shipyard-001",
        design_id="orbital_shipyard",
        name="Orbital Shipyard",
        design_data={
            "layers": {
                "hull": [
                    {"id": "space_shipyard", "abilities": {"SpaceShipyard": {}}}
                ]
            }
        },
        is_operational=True
    )
    minimal_planet.facilities.append(facility)
    return minimal_planet


@pytest.fixture
def mock_ship_instance():
    """Create a mock ship instance for testing."""
    from unittest.mock import MagicMock
    ship = MagicMock()
    ship.name = "Test Ship"
    ship.is_combat_capable.return_value = True
    ship.design_data = {"layers": {}}
    return ship
