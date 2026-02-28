"""
Tests for ShipInstance registries DI (PROJ-211 Phase 2).

Tests that ShipInstance properly stores and uses injected registries
instead of calling get_default_registry_provider().
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from game.strategy.data.ship_instance import ShipInstance
from game.core.registry import GameRegistries


@pytest.fixture
def mock_registries():
    """Create mock GameRegistries for testing."""
    registries = Mock(spec=GameRegistries)
    registries.components = {}
    registries.modifiers = {}
    registries.vehicle_classes = {}
    registries.resources = {}
    return registries


@pytest.fixture
def basic_design_data():
    """Minimal design data for ShipInstance."""
    return {
        'name': 'TestShip',
        'ship_class': 'Frigate',
        'layers': {},
    }


class TestShipInstanceRegistriesField:
    """Tests for _registries field on ShipInstance."""

    def test_registries_field_exists(self, basic_design_data):
        """ShipInstance should have _registries field."""
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=basic_design_data
        )
        assert hasattr(ship, '_registries')

    def test_registries_field_default_none(self, basic_design_data):
        """_registries should default to None when not provided."""
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=basic_design_data
        )
        assert ship._registries is None


class TestShipInstanceCreateWithRegistries:
    """Tests for ShipInstance.create() with registries parameter."""

    def test_create_stores_registries(self, mock_registries, basic_design_data):
        """create() should store registries on the instance."""
        with patch('game.strategy.services.ship_stats_calculator.ShipStatsCalculator') as mock_calc_cls:
            mock_calc = MagicMock()
            mock_calc.calculate_stats.return_value = {'resource_storage': {}}
            mock_calc_cls.return_value = mock_calc

            ship = ShipInstance.create(
                design_data=basic_design_data,
                owner_id=0,
                registries=mock_registries,
            )

            assert ship._registries is mock_registries

    def test_create_uses_stored_registries_for_stats(self, mock_registries, basic_design_data):
        """create() should use stored registries when calling get_calculated_stats()."""
        with patch('game.strategy.services.ship_stats_calculator.ShipStatsCalculator') as mock_calc_cls:
            mock_calc = MagicMock()
            mock_calc.calculate_stats.return_value = {'resource_storage': {'fuel': 100}}
            mock_calc_cls.return_value = mock_calc

            ship = ShipInstance.create(
                design_data=basic_design_data,
                owner_id=0,
                registries=mock_registries,
            )

            # Verify ShipStatsCalculator was created with our registries
            mock_calc_cls.assert_called_with(registries=mock_registries)


class TestShipInstanceFromDictWithRegistries:
    """Tests for ShipInstance.from_dict() with registries parameter."""

    def test_from_dict_stores_registries(self, mock_registries, basic_design_data):
        """from_dict() should store registries on the instance."""
        data = {
            'instance_id': 'test-1',
            'design_id': 'TestDesign',
            'name': 'Test Ship',
            'owner_id': 0,
            'design_data': basic_design_data,
        }

        ship = ShipInstance.from_dict(data, registries=mock_registries)

        assert ship._registries is mock_registries

    def test_from_dict_without_registries_sets_none(self, basic_design_data):
        """from_dict() without registries should set _registries to None."""
        data = {
            'instance_id': 'test-1',
            'design_id': 'TestDesign',
            'name': 'Test Ship',
            'owner_id': 0,
            'design_data': basic_design_data,
        }

        ship = ShipInstance.from_dict(data)

        assert ship._registries is None


class TestGetCalculatedStatsWithRegistries:
    """Tests for get_calculated_stats() using stored registries."""

    def test_uses_stored_registries(self, mock_registries, basic_design_data):
        """get_calculated_stats() should use stored _registries."""
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=basic_design_data
        )
        ship._registries = mock_registries

        with patch('game.strategy.services.ship_stats_calculator.ShipStatsCalculator') as mock_calc_cls:
            mock_calc = MagicMock()
            mock_calc.calculate_stats.return_value = {'max_hp': 100}
            mock_calc_cls.return_value = mock_calc

            ship.get_calculated_stats(force_refresh=True)

            # Verify ShipStatsCalculator was created with stored registries
            mock_calc_cls.assert_called_with(registries=mock_registries)

    def test_raises_when_registries_none(self, basic_design_data):
        """get_calculated_stats() should raise ValueError when _registries is None.

        PROJ-211: Fallback removed. Registries must be explicitly provided.
        """
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=basic_design_data
        )
        ship._registries = None

        # Should raise - no fallback to global registry
        with pytest.raises(ValueError, match="ShipInstance requires registries"):
            ship.get_calculated_stats(force_refresh=True)


class TestSetRegistriesMethod:
    """Tests for set_registries() method."""

    def test_set_registries_stores_value(self, mock_registries, basic_design_data):
        """set_registries() should store the provided registries."""
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=basic_design_data
        )

        ship.set_registries(mock_registries)

        assert ship._registries is mock_registries

    def test_set_registries_invalidates_cache(self, mock_registries, basic_design_data):
        """set_registries() should invalidate stats cache."""
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=basic_design_data
        )
        ship._cached_stats = {'max_hp': 100}  # Pre-populate cache

        ship.set_registries(mock_registries)

        assert ship._cached_stats is None
