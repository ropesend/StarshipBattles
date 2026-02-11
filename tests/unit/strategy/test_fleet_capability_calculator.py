"""Tests for FleetCapabilityCalculator.

PROJ-87 Phase 4: Extracted capability logic from Fleet class.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock


def make_ship_instance(name: str, design_data: dict = None):
    """Helper to create ShipInstance with required fields."""
    from game.strategy.data.ship_instance import ShipInstance
    return ShipInstance(
        instance_id=f"test-{name}",
        design_id=f"design-{name}",
        name=name,
        owner_id=0,
        design_data=design_data or {}
    )


class TestShipHasSpaceyard:
    """Tests for ship_has_spaceyard() static method."""

    def test_ship_has_spaceyard_with_fleet_space_yard_component(self):
        """Ship with fleet_space_yard component returns True."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator

        ship = make_ship_instance(
            name="Yard Ship",
            design_data={"layers": {"hull": [{"id": "fleet_space_yard"}]}}
        )
        assert FleetCapabilityCalculator.ship_has_spaceyard(ship) is True

    def test_ship_has_spaceyard_with_ability_dict(self):
        """Ship with SpaceShipyard ability returns True."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator

        ship = make_ship_instance(
            name="Yard Ship",
            design_data={"layers": {"hull": [{"abilities": {"SpaceShipyard": {}}}]}}
        )
        assert FleetCapabilityCalculator.ship_has_spaceyard(ship) is True

    def test_ship_has_spaceyard_without_yard(self):
        """Ship without space yard returns False."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator

        ship = make_ship_instance(
            name="Normal Ship",
            design_data={"layers": {"hull": [{"id": "laser"}]}}
        )
        assert FleetCapabilityCalculator.ship_has_spaceyard(ship) is False

    def test_ship_has_spaceyard_empty_layers(self):
        """Ship with empty layers returns False."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator

        ship = make_ship_instance(name="Empty Ship", design_data={"layers": {}})
        assert FleetCapabilityCalculator.ship_has_spaceyard(ship) is False

    def test_ship_has_spaceyard_no_design_data(self):
        """Ship with no design data returns False."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator

        ship = make_ship_instance(name="No Design", design_data={})
        assert FleetCapabilityCalculator.ship_has_spaceyard(ship) is False


class TestFleetCapabilityCalculator:
    """Tests for FleetCapabilityCalculator."""

    def test_has_space_shipyard_no_ships(self):
        """Empty fleet has no space shipyard."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        calc = FleetCapabilityCalculator(fleet)

        assert calc.has_space_shipyard is False

    def test_has_space_shipyard_with_yard_component(self):
        """Fleet with fleet_space_yard component has space shipyard."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship = make_ship_instance(
            name="Yard Ship",
            design_data={
                "layers": {
                    "hull": [{"id": "fleet_space_yard"}]
                }
            }
        )
        fleet.add_ship(ship)
        calc = FleetCapabilityCalculator(fleet)

        assert calc.has_space_shipyard is True

    def test_has_space_shipyard_with_ability_dict(self):
        """Fleet with SpaceShipyard ability in abilities dict has space shipyard."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship = make_ship_instance(
            name="Yard Ship",
            design_data={
                "layers": {
                    "hull": [{"abilities": {"SpaceShipyard": {}}}]
                }
            }
        )
        fleet.add_ship(ship)
        calc = FleetCapabilityCalculator(fleet)

        assert calc.has_space_shipyard is True

    def test_has_space_shipyard_no_yard(self):
        """Fleet without space yard component has no space shipyard."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship = make_ship_instance(
            name="Normal Ship",
            design_data={
                "layers": {
                    "hull": [{"id": "laser"}]
                }
            }
        )
        fleet.add_ship(ship)
        calc = FleetCapabilityCalculator(fleet)

        assert calc.has_space_shipyard is False

    def test_can_build_type_no_yard(self):
        """Fleet without shipyard cannot build anything."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        calc = FleetCapabilityCalculator(fleet)

        assert calc.can_build_type("ship") is False
        assert calc.can_build_type("fighter") is False
        assert calc.can_build_type("complex") is False

    def test_can_build_type_ships_with_yard(self):
        """Fleet with shipyard can build ships, fighters, satellites."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship = make_ship_instance(
            name="Yard Ship",
            design_data={"layers": {"hull": [{"id": "fleet_space_yard"}]}}
        )
        fleet.add_ship(ship)
        calc = FleetCapabilityCalculator(fleet)

        assert calc.can_build_type("ship") is True
        assert calc.can_build_type("fighter") is True
        assert calc.can_build_type("satellite") is True

    def test_can_build_type_complex_requires_planet(self):
        """Complex building requires being at a planet."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship = make_ship_instance(
            name="Yard Ship",
            design_data={"layers": {"hull": [{"id": "fleet_space_yard"}]}}
        )
        fleet.add_ship(ship)
        calc = FleetCapabilityCalculator(fleet)

        # No galaxy = no planet check possible
        assert calc.can_build_type("complex", galaxy=None) is False

        # Mock galaxy with no planets
        mock_galaxy = MagicMock()
        mock_galaxy.get_planets_at_global_hex.return_value = []
        assert calc.can_build_type("complex", galaxy=mock_galaxy) is False

        # Mock galaxy with planets
        mock_galaxy.get_planets_at_global_hex.return_value = [MagicMock()]
        assert calc.can_build_type("complex", galaxy=mock_galaxy) is True

    def test_can_use_warp_no_ships(self):
        """Empty fleet cannot use warp."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        calc = FleetCapabilityCalculator(fleet)

        assert calc.can_use_warp() is False

    def test_can_use_warp_all_capable(self):
        """Fleet where all ships are warp-capable can use warp."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship = make_ship_instance(name="Warper", design_data={})
        fleet.add_ship(ship)
        calc = FleetCapabilityCalculator(fleet)

        with patch(
            'game.strategy.services.ship_stats_calculator.ShipStatsCalculator.has_warp_capability',
            return_value=True
        ):
            assert calc.can_use_warp() is True

    def test_can_use_warp_one_incapable(self):
        """Fleet with one non-warp ship cannot use warp."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship1 = make_ship_instance(name="Warper", design_data={})
        ship2 = make_ship_instance(name="NoWarp", design_data={})
        fleet.add_ship(ship1)
        fleet.add_ship(ship2)
        calc = FleetCapabilityCalculator(fleet)

        def mock_warp(ship):
            return ship.name == "Warper"

        with patch(
            'game.strategy.services.ship_stats_calculator.ShipStatsCalculator.has_warp_capability',
            side_effect=mock_warp
        ):
            assert calc.can_use_warp() is False

    def test_get_warp_limiting_ship_all_capable(self):
        """No limiting ship when all are warp-capable."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship = make_ship_instance(name="Warper", design_data={})
        fleet.add_ship(ship)
        calc = FleetCapabilityCalculator(fleet)

        with patch(
            'game.strategy.services.ship_stats_calculator.ShipStatsCalculator.has_warp_capability',
            return_value=True
        ):
            assert calc.get_warp_limiting_ship() is None

    def test_get_warp_limiting_ship_one_incapable(self):
        """Returns the first non-warp capable ship."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship1 = make_ship_instance(name="Warper", design_data={})
        ship2 = make_ship_instance(name="NoWarp", design_data={})
        fleet.add_ship(ship1)
        fleet.add_ship(ship2)
        calc = FleetCapabilityCalculator(fleet)

        def mock_warp(ship):
            return ship.name == "Warper"

        with patch(
            'game.strategy.services.ship_stats_calculator.ShipStatsCalculator.has_warp_capability',
            side_effect=mock_warp
        ):
            limiting = calc.get_warp_limiting_ship()
            assert limiting is not None
            assert limiting.name == "NoWarp"


class TestFleetCapabilityCalculatorDelegation:
    """Test that Fleet properly delegates to FleetCapabilityCalculator."""

    def test_fleet_has_space_shipyard_delegates(self):
        """Fleet.has_space_shipyard delegates to calculator."""
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship = make_ship_instance(
            name="Yard Ship",
            design_data={"layers": {"hull": [{"id": "fleet_space_yard"}]}}
        )
        fleet.add_ship(ship)

        assert fleet.has_space_shipyard is True

    def test_fleet_can_build_type_delegates(self):
        """Fleet.can_build_type delegates to calculator."""
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship = make_ship_instance(
            name="Yard Ship",
            design_data={"layers": {"hull": [{"id": "fleet_space_yard"}]}}
        )
        fleet.add_ship(ship)

        assert fleet.can_build_type("ship") is True

    def test_fleet_can_use_warp_delegates(self):
        """Fleet.can_use_warp delegates to calculator."""
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        # No ships = cannot warp
        assert fleet.can_use_warp() is False

    def test_fleet_get_warp_limiting_ship_delegates(self):
        """Fleet.get_warp_limiting_ship delegates to calculator."""
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        # No ships = no limiting ship
        assert fleet.get_warp_limiting_ship() is None
