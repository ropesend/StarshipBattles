"""Tests for FleetCapabilityCalculator.

PROJ-87 Phase 4: Extracted capability logic from Fleet class.
PROJ-211 Phase 5: Updated to use DI-compliant ship creation.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock


def make_ship_instance(name: str, design_data: dict = None, registries=None):
    """Helper to create ShipInstance with required fields.

    Args:
        name: Ship name
        design_data: Component/layer data for the ship
        registries: GameRegistries for DI (required for Fleet.add_ship)
    """
    from game.strategy.data.ship_instance import ShipInstance
    ship = ShipInstance(
        instance_id=f"test-{name}",
        design_id=f"design-{name}",
        name=name,
        owner_id=0,
        design_data=design_data or {},
    )
    if registries is not None:
        ship.set_registries(registries)
    return ship


class TestShipHasSpaceyard:
    """Tests for ship_has_spaceyard() static method.

    PROJ-211: Tests pass fresh_registries to ships so they have _registries set,
    which is required after fallback removal.
    """

    def test_ship_has_spaceyard_with_space_shipyard_component(self, fresh_registries):
        """Ship with space_shipyard component returns True."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator

        ship = make_ship_instance(
            name="Yard Ship",
            design_data={"layers": {"hull": [{"id": "space_shipyard"}]}},
            registries=fresh_registries
        )
        assert FleetCapabilityCalculator.ship_has_spaceyard(ship) is True

    def test_ship_has_spaceyard_with_ability_dict(self, fresh_registries):
        """Ship with SpaceShipyard ability returns True."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator

        ship = make_ship_instance(
            name="Yard Ship",
            design_data={"layers": {"hull": [{"abilities": {"SpaceShipyard": {}}}]}},
            registries=fresh_registries
        )
        assert FleetCapabilityCalculator.ship_has_spaceyard(ship) is True

    def test_ship_has_spaceyard_without_yard(self, fresh_registries):
        """Ship without space yard returns False."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator

        ship = make_ship_instance(
            name="Normal Ship",
            design_data={"layers": {"hull": [{"id": "laser"}]}},
            registries=fresh_registries
        )
        assert FleetCapabilityCalculator.ship_has_spaceyard(ship) is False

    def test_ship_has_spaceyard_empty_layers(self, fresh_registries):
        """Ship with empty layers returns False."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator

        ship = make_ship_instance(
            name="Empty Ship",
            design_data={"layers": {}},
            registries=fresh_registries
        )
        assert FleetCapabilityCalculator.ship_has_spaceyard(ship) is False

    def test_ship_has_spaceyard_no_design_data(self, fresh_registries):
        """Ship with no design data returns False."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator

        ship = make_ship_instance(
            name="No Design",
            design_data={},
            registries=fresh_registries
        )
        assert FleetCapabilityCalculator.ship_has_spaceyard(ship) is False


class TestFleetCapabilityCalculator:
    """Tests for FleetCapabilityCalculator.

    PROJ-211: Tests that add ships to fleets use fresh_registries for DI compliance.
    """

    def test_has_space_shipyard_no_ships(self):
        """Empty fleet has no space shipyard."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        calc = FleetCapabilityCalculator(fleet)

        assert calc.has_space_shipyard is False

    def test_has_space_shipyard_with_yard_component(self, fresh_registries):
        """Fleet with space_shipyard component has space shipyard."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship = make_ship_instance(
            name="Yard Ship",
            design_data={
                "layers": {
                    "hull": [{"id": "space_shipyard"}]
                }
            },
            registries=fresh_registries
        )
        fleet.add_ship(ship)
        calc = FleetCapabilityCalculator(fleet)

        assert calc.has_space_shipyard is True

    def test_has_space_shipyard_with_ability_dict(self, fresh_registries):
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
            },
            registries=fresh_registries
        )
        fleet.add_ship(ship)
        calc = FleetCapabilityCalculator(fleet)

        assert calc.has_space_shipyard is True

    def test_has_space_shipyard_no_yard(self, fresh_registries):
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
            },
            registries=fresh_registries
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

    def test_can_build_type_ships_with_yard(self, fresh_registries):
        """Fleet with shipyard can build ships, fighters, satellites."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship = make_ship_instance(
            name="Yard Ship",
            design_data={"layers": {"hull": [{"id": "space_shipyard"}]}},
            registries=fresh_registries
        )
        fleet.add_ship(ship)
        calc = FleetCapabilityCalculator(fleet)

        assert calc.can_build_type("ship") is True
        assert calc.can_build_type("fighter") is True
        assert calc.can_build_type("satellite") is True

    def test_can_build_type_complex_requires_planet(self, fresh_registries):
        """Complex building requires being at a planet."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship = make_ship_instance(
            name="Yard Ship",
            design_data={"layers": {"hull": [{"id": "space_shipyard"}]}},
            registries=fresh_registries
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

    def test_can_use_warp_all_capable(self, fresh_registries):
        """Fleet where all ships are warp-capable can use warp."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship = make_ship_instance(name="Warper", design_data={}, registries=fresh_registries)
        fleet.add_ship(ship)
        calc = FleetCapabilityCalculator(fleet)

        with patch(
            'game.strategy.services.component_inspector.has_warp_capability',
            return_value=True
        ):
            assert calc.can_use_warp() is True

    def test_can_use_warp_one_incapable(self, fresh_registries):
        """Fleet with one non-warp ship cannot use warp."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship1 = make_ship_instance(name="Warper", design_data={}, registries=fresh_registries)
        ship2 = make_ship_instance(name="NoWarp", design_data={}, registries=fresh_registries)
        fleet.add_ship(ship1)
        fleet.add_ship(ship2)
        calc = FleetCapabilityCalculator(fleet)

        def mock_warp(ship):
            return ship.name == "Warper"

        with patch(
            'game.strategy.services.component_inspector.has_warp_capability',
            side_effect=mock_warp
        ):
            assert calc.can_use_warp() is False

    def test_get_warp_limiting_ship_all_capable(self, fresh_registries):
        """No limiting ship when all are warp-capable."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship = make_ship_instance(name="Warper", design_data={}, registries=fresh_registries)
        fleet.add_ship(ship)
        calc = FleetCapabilityCalculator(fleet)

        with patch(
            'game.strategy.services.component_inspector.has_warp_capability',
            return_value=True
        ):
            assert calc.get_warp_limiting_ship() is None

    def test_get_warp_limiting_ship_one_incapable(self, fresh_registries):
        """Returns the first non-warp capable ship."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship1 = make_ship_instance(name="Warper", design_data={}, registries=fresh_registries)
        ship2 = make_ship_instance(name="NoWarp", design_data={}, registries=fresh_registries)
        fleet.add_ship(ship1)
        fleet.add_ship(ship2)
        calc = FleetCapabilityCalculator(fleet)

        def mock_warp(ship):
            return ship.name == "Warper"

        with patch(
            'game.strategy.services.component_inspector.has_warp_capability',
            side_effect=mock_warp
        ):
            limiting = calc.get_warp_limiting_ship()
            assert limiting is not None
            assert limiting.name == "NoWarp"


class TestHasAbility:
    """Tests for has_ability() and ships_with_ability() methods (PROJ-102).

    PROJ-211: Tests that add ships to fleets use fresh_registries for DI compliance.
    """

    def test_has_ability_returns_true_whenship_has_ability(self, fresh_registries):
        """has_ability returns True when any ship has the ability."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship = make_ship_instance(
            name="Planet Killer",
            design_data={
                "layers": {
                    "hull": [{"abilities": {"DestroyPlanet": {}}}]
                }
            },
            registries=fresh_registries
        )
        fleet.add_ship(ship)
        calc = FleetCapabilityCalculator(fleet)

        assert calc.has_ability("DestroyPlanet") is True

    def test_has_ability_returns_false_when_noship_has_ability(self, fresh_registries):
        """has_ability returns False when no ship has the ability."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship = make_ship_instance(
            name="Normal Ship",
            design_data={
                "layers": {
                    "hull": [{"abilities": {"WarpJump": {}}}]
                }
            },
            registries=fresh_registries
        )
        fleet.add_ship(ship)
        calc = FleetCapabilityCalculator(fleet)

        assert calc.has_ability("DestroyPlanet") is False

    def test_has_ability_returns_false_for_empty_fleet(self):
        """has_ability returns False for empty fleet."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        calc = FleetCapabilityCalculator(fleet)

        assert calc.has_ability("DestroyPlanet") is False

    def test_ships_with_ability_returns_matching_ships(self, fresh_registries):
        """ships_with_ability returns list of ships with the ability."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship1 = make_ship_instance(
            name="Self Destruct Ship",
            design_data={
                "layers": {
                    "hull": [{"abilities": {"SelfDestruct": {}}}]
                }
            },
            registries=fresh_registries
        )
        ship2 = make_ship_instance(
            name="Normal Ship",
            design_data={
                "layers": {
                    "hull": [{"abilities": {"WarpJump": {}}}]
                }
            },
            registries=fresh_registries
        )
        ship3 = make_ship_instance(
            name="Another Self Destruct",
            design_data={
                "layers": {
                    "hull": [{"abilities": {"SelfDestruct": {}}}]
                }
            },
            registries=fresh_registries
        )
        fleet.add_ship(ship1)
        fleet.add_ship(ship2)
        fleet.add_ship(ship3)
        calc = FleetCapabilityCalculator(fleet)

        result = calc.ships_with_ability("SelfDestruct")
        assert len(result) == 2
        assert ship1 in result
        assert ship3 in result
        assert ship2 not in result

    def test_ships_with_ability_returns_empty_list_when_no_matches(self, fresh_registries):
        """ships_with_ability returns empty list when no ships have ability."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship = make_ship_instance(
            name="Normal Ship",
            design_data={
                "layers": {
                    "hull": [{"abilities": {"WarpJump": {}}}]
                }
            },
            registries=fresh_registries
        )
        fleet.add_ship(ship)
        calc = FleetCapabilityCalculator(fleet)

        result = calc.ships_with_ability("SelfDestruct")
        assert result == []

    def testship_has_ability_checks_all_layers(self, fresh_registries):
        """ship_has_ability checks abilities in all layers."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship = make_ship_instance(
            name="Multi Layer",
            design_data={
                "layers": {
                    "hull": [{"abilities": {"WarpJump": {}}}],
                    "systems": [{"abilities": {"DestroyPlanet": {}}}]
                }
            },
            registries=fresh_registries
        )
        fleet.add_ship(ship)
        calc = FleetCapabilityCalculator(fleet)

        assert calc.has_ability("DestroyPlanet") is True
        assert calc.has_ability("WarpJump") is True


class TestFleetCapabilityCalculatorDelegation:
    """Test that Fleet properly delegates to FleetCapabilityCalculator.

    PROJ-211: Tests that add ships to fleets use fresh_registries for DI compliance.
    """

    def test_fleet_capabilities_has_space_shipyard(self, fresh_registries):
        """Fleet.capabilities.has_space_shipyard works via exposed delegate (PROJ-210)."""
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship = make_ship_instance(
            name="Yard Ship",
            design_data={"layers": {"hull": [{"id": "space_shipyard"}]}},
            registries=fresh_registries
        )
        fleet.add_ship(ship)

        assert fleet.capabilities.has_space_shipyard is True

    def test_fleet_capabilities_can_build_type(self, fresh_registries):
        """Fleet.capabilities.can_build_type works via exposed delegate (PROJ-210)."""
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship = make_ship_instance(
            name="Yard Ship",
            design_data={"layers": {"hull": [{"id": "space_shipyard"}]}},
            registries=fresh_registries
        )
        fleet.add_ship(ship)

        assert fleet.capabilities.can_build_type("ship") is True

    def test_fleet_capabilities_can_use_warp(self):
        """Fleet.capabilities.can_use_warp works via exposed delegate (PROJ-210)."""
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        # No ships = cannot warp
        assert fleet.capabilities.can_use_warp() is False

    def test_fleet_capabilities_get_warp_limiting_ship(self):
        """Fleet.capabilities.get_warp_limiting_ship works via exposed delegate (PROJ-210)."""
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        # No ships = no limiting ship
        assert fleet.capabilities.get_warp_limiting_ship() is None
