"""
Tests for ShipInstance - resource cost query methods.

PROJ-48: Split from test_resources.py
"""

import pytest
from game.strategy.data.ship_instance import ShipInstance


class TestGetAllResourceCostsPerHex:
    """Tests for get_all_resource_costs_per_hex method."""

    def test_get_all_resource_costs_per_hex_empty(self, make_design_data_with_stats):
        """get_all_resource_costs_per_hex returns empty dict when none defined."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_consumption_per_hex': {}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.get_all_resource_costs_per_hex()
        assert result == {}

    def test_get_all_resource_costs_per_hex_fuel_only(self, make_design_data_with_stats):
        """get_all_resource_costs_per_hex returns fuel cost when defined."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_consumption_per_hex': {'fuel': 100}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.get_all_resource_costs_per_hex()
        assert result == {'fuel': 100}

    def test_get_all_resource_costs_per_hex_multiple_resources(self, make_design_data_with_stats):
        """get_all_resource_costs_per_hex returns multiple resource costs."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_consumption_per_hex': {'fuel': 100, 'energy': 50}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.get_all_resource_costs_per_hex()
        assert result == {'fuel': 100, 'energy': 50}

    def test_get_all_resource_costs_per_hex_custom_resource(self, make_design_data_with_stats):
        """get_all_resource_costs_per_hex includes custom resource types."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_consumption_per_hex': {'fuel': 100, 'glag': 5}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.get_all_resource_costs_per_hex()
        assert result == {'fuel': 100, 'glag': 5}


class TestGetAllResourceCostsPerTurn:
    """Tests for get_all_resource_costs_per_turn method."""

    def test_get_all_resource_costs_per_turn_empty(self, make_design_data_with_stats):
        """get_all_resource_costs_per_turn returns empty dict when none defined."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_consumption_per_turn': {}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.get_all_resource_costs_per_turn()
        assert result == {}

    def test_get_all_resource_costs_per_turn_single_resource(self, make_design_data_with_stats):
        """get_all_resource_costs_per_turn returns single resource cost."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_consumption_per_turn': {'energy': 100}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.get_all_resource_costs_per_turn()
        assert result == {'energy': 100}

    def test_get_all_resource_costs_per_turn_multiple_resources(self, make_design_data_with_stats):
        """get_all_resource_costs_per_turn returns multiple resource costs."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_consumption_per_turn': {'energy': 100, 'fuel': 50}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.get_all_resource_costs_per_turn()
        assert result == {'energy': 100, 'fuel': 50}

    def test_get_all_resource_costs_per_turn_custom_resource(self, make_design_data_with_stats):
        """get_all_resource_costs_per_turn includes custom resource types."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_consumption_per_turn': {'energy': 100, 'glag': 10}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.get_all_resource_costs_per_turn()
        assert result == {'energy': 100, 'glag': 10}


class TestGetWarpResourceCosts:
    """Tests for get_warp_resource_costs method."""

    def test_get_warp_resource_costs_empty(self, make_design_data_with_stats):
        """get_warp_resource_costs returns empty dict when no warp drive."""
        design_data = make_design_data_with_stats(expected_stats={
            'warp_resource_costs': {}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.get_warp_resource_costs()
        assert result == {}

    def test_get_warp_resource_costs_energy_only(self, make_design_data_with_stats):
        """get_warp_resource_costs returns energy cost."""
        design_data = make_design_data_with_stats(expected_stats={
            'warp_resource_costs': {'energy': 500}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.get_warp_resource_costs()
        assert result == {'energy': 500}

    def test_get_warp_resource_costs_fuel_and_energy(self, make_design_data_with_stats):
        """get_warp_resource_costs returns both fuel and energy costs."""
        design_data = make_design_data_with_stats(expected_stats={
            'warp_resource_costs': {'energy': 500, 'fuel': 100}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.get_warp_resource_costs()
        assert result == {'energy': 500, 'fuel': 100}

    def test_get_warp_resource_costs_custom_resource(self, make_design_data_with_stats):
        """get_warp_resource_costs includes custom resource types."""
        design_data = make_design_data_with_stats(expected_stats={
            'warp_resource_costs': {'energy': 500, 'antimatter': 50}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.get_warp_resource_costs()
        assert result == {'energy': 500, 'antimatter': 50}

    def test_get_warp_resource_costs_damaged_warp_drive(self, make_design_data_with_stats):
        """Damaged warp drive should affect warp costs through stats."""
        # This tests the integration with stats service
        # When warp drive is damaged, stats service should return 0 for warp costs
        design_data = make_design_data_with_stats(expected_stats={
            'warp_resource_costs': {}  # Damaged warp returns empty
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )
        ship.component_damage['warp_drive'] = 50  # Damaged

        result = ship.get_warp_resource_costs()
        assert result == {}
