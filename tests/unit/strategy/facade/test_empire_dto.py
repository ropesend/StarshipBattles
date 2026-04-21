"""Tests for Empire DTOs."""
import pytest
from dataclasses import FrozenInstanceError
from game.core.hex_math import HexCoord


class TestColonySummary:
    """Tests for ColonySummary frozen dataclass."""

    def test_is_frozen(self):
        """ColonySummary is immutable (frozen)."""
        from game.strategy.facade.dto.empire_dto import ColonySummary

        colony = ColonySummary(
            planet_id=1,
            planet_name="Mars",
            has_shipyard=False,
        )

        with pytest.raises(FrozenInstanceError):
            colony.planet_name = "Venus"


class TestFleetSummary:
    """Tests for FleetSummary frozen dataclass."""

    def test_is_frozen(self):
        """FleetSummary is immutable (frozen)."""
        from game.strategy.facade.dto.empire_dto import FleetSummary

        fleet = FleetSummary(
            fleet_id=1,
            ship_count=3,
            has_orders=False,
        )

        with pytest.raises(FrozenInstanceError):
            fleet.ship_count = 10


class TestEmpireInfo:
    """Tests for EmpireInfo frozen dataclass."""

    def test_create_full_empire_info(self):
        """EmpireInfo can include full counts."""
        from game.strategy.facade.dto.empire_dto import EmpireInfo

        empire = EmpireInfo(
            empire_id=1,
            name="Klingon Empire",
            color=(255, 0, 0),
            theme_id="Klingon",
            flag_id="flag_klingon",
            colony_count=5,
            fleet_count=10,
        )

        assert empire.colony_count == 5
        assert empire.fleet_count == 10

    def test_is_frozen(self):
        """EmpireInfo is immutable (frozen)."""
        from game.strategy.facade.dto.empire_dto import EmpireInfo

        empire = EmpireInfo(
            empire_id=0,
            name="Federation",
            color=(0, 0, 255),
            theme_id="Federation",
            flag_id="flag_001",
        )

        with pytest.raises(FrozenInstanceError):
            empire.name = "Romulan Empire"


class TestEmpireInfoFactory:
    """Tests for EmpireInfo.from_empire factory method."""

    def test_from_empire_basic(self):
        """from_empire creates DTO from basic Empire."""
        from game.strategy.facade.dto.empire_dto import EmpireInfo
        from game.strategy.data.empire import Empire

        empire = Empire(
            empire_id=0,
            name="Test Empire",
            color=(100, 150, 200),
            empire_theme_id="TestTheme",
            flag_id="test_flag",
        )

        info = EmpireInfo.from_empire(empire)

        assert info.empire_id == 0
        assert info.name == "Test Empire"
        assert info.color == (100, 150, 200)
        assert info.theme_id == "TestTheme"
        assert info.flag_id == "test_flag"
        assert info.colony_count == 0
        assert info.fleet_count == 0

    def test_from_empire_with_colonies_and_fleets(self):
        """from_empire counts colonies and fleets."""
        from game.strategy.facade.dto.empire_dto import EmpireInfo
        from game.strategy.data.empire import Empire
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.planet import Planet, PlanetType
        from unittest.mock import MagicMock

        empire = Empire(
            empire_id=0,
            name="Test Empire",
            color=(100, 150, 200),
        )

        # Add mock colonies
        for i in range(3):
            planet = MagicMock()
            planet.id = i
            empire.colonies.append(planet)

        # Add fleets
        for i in range(2):
            fleet = Fleet(
                fleet_id=i,
                owner_id=0,
                location=HexCoord(i, 0),
            )
            empire.fleets.append(fleet)

        info = EmpireInfo.from_empire(empire)

        assert info.colony_count == 3
        assert info.fleet_count == 2


class TestColonySummaryFactory:
    """Tests for ColonySummary.from_planet factory method."""

    def test_from_planet_basic(self):
        """from_planet creates DTO from Planet."""
        from game.strategy.facade.dto.empire_dto import ColonySummary
        from game.strategy.data.planet import Planet, PlanetType

        planet = Planet(
            name="Colony Alpha",
            location=HexCoord(3, 0),
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
            planet_type=PlanetType.CONTINENTAL,
        )
        planet.id = 42
        planet.owner_id = 0

        summary = ColonySummary.from_planet(planet)

        assert summary.planet_id == 42
        assert summary.planet_name == "Colony Alpha"
        assert summary.has_shipyard is False

    def test_from_planet_with_shipyard(self):
        """from_planet detects space shipyard."""
        from game.strategy.facade.dto.empire_dto import ColonySummary
        from game.strategy.data.planet import Planet, PlanetType, PlanetaryFacility

        planet = Planet(
            name="Shipyard World",
            location=HexCoord(3, 0),
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
            planet_type=PlanetType.CONTINENTAL,
        )
        planet.id = 1
        planet.owner_id = 0

        # Add facility with space shipyard
        facility = PlanetaryFacility(
            instance_id="facility-001",
            design_id="orbital_shipyard",
            name="Orbital Shipyard",
            design_data={
                "layers": {
                    "OUTER": [{"id": "space_shipyard"}]
                }
            },
        )
        planet.facilities.append(facility)

        summary = ColonySummary.from_planet(planet)

        assert summary.has_shipyard is True


class TestFleetSummaryFactory:
    """Tests for FleetSummary.from_fleet factory method."""

    def test_from_fleet_basic(self):
        """from_fleet creates DTO from basic Fleet."""
        from game.strategy.facade.dto.empire_dto import FleetSummary
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.ship_instance import ShipInstance

        fleet = Fleet(
            fleet_id=100,
            owner_id=0,
            location=HexCoord(5, 5),
        )

        # Add ships
        for i in range(3):
            ship = ShipInstance(
                instance_id=f"ship-{i}",
                design_id="test_design",
                name=f"Ship {i}",
                owner_id=0,
                design_data={"name": f"Ship {i}", "ship_class": "Frigate", "layers": {}},
            )
            fleet.ships.append(ship)

        summary = FleetSummary.from_fleet(fleet)

        assert summary.fleet_id == 100
        assert summary.ship_count == 3
        assert summary.has_orders is False

    def test_from_fleet_with_orders(self):
        """from_fleet detects orders."""
        from game.strategy.facade.dto.empire_dto import FleetSummary
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.order_types import FleetOrder, OrderType

        fleet = Fleet(
            fleet_id=100,
            owner_id=0,
            location=HexCoord(5, 5),
        )
        fleet.add_order(FleetOrder(OrderType.MOVE, HexCoord(10, 10)))

        summary = FleetSummary.from_fleet(fleet)

        assert summary.has_orders is True
