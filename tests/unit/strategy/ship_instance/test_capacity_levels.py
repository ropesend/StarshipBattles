"""
Tests for ShipInstance - resource capacity and level management.

PROJ-48: Split from test_resources.py
"""

import pytest
from game.strategy.data.ship_instance import ShipInstance


class TestGetResourceCapacity:
    """Tests for get_resource_capacity method."""

    def test_get_resource_capacity_fuel(self, make_design_data_with_stats):
        """get_resource_capacity returns fuel capacity from resource_storage."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'fuel': 5000}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        assert ship.get_resource_capacity('fuel') == 5000

    def test_get_resource_capacity_energy(self, make_design_data_with_stats):
        """get_resource_capacity returns energy capacity from resource_storage."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'energy': 2000}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        assert ship.get_resource_capacity('energy') == 2000

    def test_get_resource_capacity_custom_resource(self, make_design_data_with_stats):
        """get_resource_capacity returns custom resource capacity."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'fuel': 1000, 'energy': 500, 'glag': 200}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        assert ship.get_resource_capacity('glag') == 200

    def test_get_resource_capacity_unknown_resource(self, make_design_data_with_stats):
        """get_resource_capacity returns 0 for unknown resource types."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'fuel': 1000}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        assert ship.get_resource_capacity('unknown_resource') == 0

    def test_get_resource_capacity_zero_capacity(self, make_design_data_with_stats):
        """get_resource_capacity returns 0 when resource has zero capacity."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'fuel': 0, 'energy': 100}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        assert ship.get_resource_capacity('fuel') == 0


class TestGetCurrentResource:
    """Tests for get_current_resource method."""

    def test_get_current_resource_returns_stored_value(self, make_design_data_with_stats):
        """get_current_resource returns stored value.

        PROJ-95: Resources always stored with actual values.
        """
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'fuel': 5000}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data,
            resource_levels={'fuel': 5000}  # Explicitly stored at full
        )

        assert ship.get_current_resource('fuel') == 5000

    def test_get_current_resource_returns_current_when_partial(self, make_design_data_with_stats):
        """get_current_resource returns tracked value when partially consumed."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'fuel': 5000}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        ship.resource_levels['fuel'] = 3000
        assert ship.get_current_resource('fuel') == 3000

    def test_get_current_resource_with_all_types(self, make_design_data_with_stats):
        """get_current_resource works with multiple resource types.

        PROJ-95: Resources always stored with actual values.
        """
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'fuel': 5000, 'energy': 2000, 'ammo': 500}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data,
            resource_levels={'fuel': 2500, 'energy': 1000, 'ammo': 500}
        )

        assert ship.get_current_resource('fuel') == 2500
        assert ship.get_current_resource('energy') == 1000
        assert ship.get_current_resource('ammo') == 500

    def test_get_current_resource_custom_resource(self, make_design_data_with_stats):
        """get_current_resource works with custom resource types."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'glag': 100}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        ship.resource_levels['glag'] = 50
        assert ship.get_current_resource('glag') == 50


class TestConsumeResource:
    """Tests for consume_resource method."""

    def test_consume_resource_success(self, make_design_data_with_stats):
        """consume_resource returns True and updates level on success.

        PROJ-95: Resources always stored with actual values.
        """
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'fuel': 5000}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data,
            resource_levels={'fuel': 5000}  # Start at full
        )

        result = ship.consume_resource('fuel', 1000)

        assert result is True
        assert ship.resource_levels['fuel'] == 4000

    def test_consume_resource_insufficient_fails(self, make_design_data_with_stats):
        """consume_resource returns False when insufficient resources."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'fuel': 5000}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        ship.resource_levels['fuel'] = 500
        result = ship.consume_resource('fuel', 1000)

        assert result is False
        assert ship.resource_levels['fuel'] == 500  # Unchanged

    def test_consume_resource_exact_amount(self, make_design_data_with_stats):
        """consume_resource succeeds when consuming exactly available amount."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'fuel': 5000}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        ship.resource_levels['fuel'] = 1000
        result = ship.consume_resource('fuel', 1000)

        assert result is True
        assert ship.resource_levels['fuel'] == 0

    def test_consume_resource_zero_amount(self, make_design_data_with_stats):
        """consume_resource with zero amount returns True without changes.

        PROJ-95: Resources always stored with actual values.
        """
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'fuel': 5000}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data,
            resource_levels={'fuel': 5000}
        )

        result = ship.consume_resource('fuel', 0)

        assert result is True
        assert ship.get_current_resource('fuel') == 5000

    def test_consume_resource_multiple_types(self, make_design_data_with_stats):
        """consume_resource handles multiple resource types independently.

        PROJ-95: Resources always stored with actual values.
        """
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'fuel': 5000, 'energy': 2000}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data,
            resource_levels={'fuel': 5000, 'energy': 2000}
        )

        ship.consume_resource('fuel', 1000)
        ship.consume_resource('energy', 500)

        assert ship.resource_levels['fuel'] == 4000
        assert ship.resource_levels['energy'] == 1500

    def test_consume_resource_custom_type(self, make_design_data_with_stats):
        """consume_resource works with custom resource types.

        PROJ-95: Resources always stored with actual values.
        """
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'glag': 100}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data,
            resource_levels={'glag': 100}
        )

        result = ship.consume_resource('glag', 25)

        assert result is True
        assert ship.resource_levels['glag'] == 75

    def test_consume_resource_from_full(self, make_design_data_with_stats):
        """consume_resource works when starting from full capacity.

        PROJ-95: Resources always stored with actual values.
        """
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'fuel': 5000}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data,
            resource_levels={'fuel': 5000}
        )

        # Start at full
        assert ship.resource_levels['fuel'] == 5000

        result = ship.consume_resource('fuel', 1000)

        assert result is True
        assert ship.resource_levels['fuel'] == 4000
