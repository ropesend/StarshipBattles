"""Unit tests for VehicleClassService.

PROJ-43: Tests for the VehicleClassService facade that decouples UI from simulation.
PROJ-50: Added test for strict DI (registry_provider is required).
"""
from unittest.mock import MagicMock
import pytest

from game.ui.services.vehicle_class_service import VehicleClassService
from game.core.exceptions import ValidationException


class TestVehicleClassService:
    """Tests for VehicleClassService class."""

    def test_init_requires_registry_provider(self):
        """Test that registry_provider is required (PROJ-50 strict DI)."""
        with pytest.raises(ValidationException, match="registry_provider is required"):
            VehicleClassService(None)

    def test_get_all_classes_returns_dict(self):
        """Test get_all_classes returns vehicle classes from registry."""
        mock_provider = MagicMock()
        mock_classes = {
            'Escort': {'type': 'Ship', 'max_mass': 1000},
            'Frigate': {'type': 'Ship', 'max_mass': 2000},
            'Fighter': {'type': 'Craft', 'max_mass': 100},
        }
        mock_provider.get_vehicle_classes.return_value = mock_classes

        service = VehicleClassService(registry_provider=mock_provider)
        result = service.get_all_classes()

        assert result == mock_classes
        mock_provider.get_vehicle_classes.assert_called_once()

    def test_get_class_definition_returns_definition(self):
        """Test get_class_definition returns specific class def."""
        mock_provider = MagicMock()
        mock_classes = {
            'Escort': {'type': 'Ship', 'max_mass': 1000},
            'Frigate': {'type': 'Ship', 'max_mass': 2000},
        }
        mock_provider.get_vehicle_classes.return_value = mock_classes

        service = VehicleClassService(registry_provider=mock_provider)
        result = service.get_class_definition('Escort')

        assert result == {'type': 'Ship', 'max_mass': 1000}

    def test_get_class_definition_returns_none_for_missing(self):
        """Test get_class_definition returns None for unknown class."""
        mock_provider = MagicMock()
        mock_provider.get_vehicle_classes.return_value = {}

        service = VehicleClassService(registry_provider=mock_provider)
        result = service.get_class_definition('NonExistent')

        assert result is None

    def test_get_vehicle_types_returns_sorted_types(self):
        """Test get_vehicle_types returns sorted unique types."""
        mock_provider = MagicMock()
        mock_classes = {
            'Escort': {'type': 'Ship', 'max_mass': 1000},
            'Frigate': {'type': 'Ship', 'max_mass': 2000},
            'Fighter': {'type': 'Craft', 'max_mass': 100},
            'Bomber': {'type': 'Craft', 'max_mass': 150},
            'Hauler': {'type': 'Freighter', 'max_mass': 5000},
        }
        mock_provider.get_vehicle_classes.return_value = mock_classes

        service = VehicleClassService(registry_provider=mock_provider)
        result = service.get_vehicle_types()

        assert result == ['Craft', 'Freighter', 'Ship']  # Sorted

    def test_get_vehicle_types_handles_missing_type_field(self):
        """Test get_vehicle_types uses 'Ship' as default for missing type."""
        mock_provider = MagicMock()
        mock_classes = {
            'Escort': {'max_mass': 1000},  # No 'type' field
            'Fighter': {'type': 'Craft', 'max_mass': 100},
        }
        mock_provider.get_vehicle_classes.return_value = mock_classes

        service = VehicleClassService(registry_provider=mock_provider)
        result = service.get_vehicle_types()

        assert result == ['Craft', 'Ship']  # 'Ship' is the default

    def test_get_classes_for_type_filters_correctly(self):
        """Test get_classes_for_type filters classes by vehicle type."""
        mock_provider = MagicMock()
        mock_classes = {
            'Escort': {'type': 'Ship', 'max_mass': 1000},
            'Frigate': {'type': 'Ship', 'max_mass': 2000},
            'Fighter': {'type': 'Craft', 'max_mass': 100},
            'Bomber': {'type': 'Craft', 'max_mass': 150},
        }
        mock_provider.get_vehicle_classes.return_value = mock_classes

        service = VehicleClassService(registry_provider=mock_provider)
        result = service.get_classes_for_type('Craft')

        # Result should be list of (name, max_mass) tuples
        assert len(result) == 2
        names = [r[0] for r in result]
        assert 'Fighter' in names
        assert 'Bomber' in names
        assert 'Escort' not in names

    def test_get_classes_for_type_returns_tuples_with_max_mass(self):
        """Test get_classes_for_type returns (name, max_mass) tuples."""
        mock_provider = MagicMock()
        mock_classes = {
            'Escort': {'type': 'Ship', 'max_mass': 1000},
            'Frigate': {'type': 'Ship', 'max_mass': 2000},
        }
        mock_provider.get_vehicle_classes.return_value = mock_classes

        service = VehicleClassService(registry_provider=mock_provider)
        result = service.get_classes_for_type('Ship')

        assert ('Escort', 1000) in result
        assert ('Frigate', 2000) in result

    def test_get_classes_for_type_handles_missing_max_mass(self):
        """Test get_classes_for_type uses 0 for missing max_mass."""
        mock_provider = MagicMock()
        mock_classes = {
            'Unknown': {'type': 'Ship'},  # No max_mass
        }
        mock_provider.get_vehicle_classes.return_value = mock_classes

        service = VehicleClassService(registry_provider=mock_provider)
        result = service.get_classes_for_type('Ship')

        assert result == [('Unknown', 0)]

    def test_get_max_mass_returns_value(self):
        """Test get_max_mass returns max_mass for class."""
        mock_provider = MagicMock()
        mock_classes = {
            'Frigate': {'type': 'Ship', 'max_mass': 2000},
        }
        mock_provider.get_vehicle_classes.return_value = mock_classes

        service = VehicleClassService(registry_provider=mock_provider)
        result = service.get_max_mass('Frigate')

        assert result == 2000

    def test_get_max_mass_returns_zero_for_missing_class(self):
        """Test get_max_mass returns 0 for unknown class."""
        mock_provider = MagicMock()
        mock_provider.get_vehicle_classes.return_value = {}

        service = VehicleClassService(registry_provider=mock_provider)
        result = service.get_max_mass('NonExistent')

        assert result == 0

    def test_get_max_mass_returns_zero_for_missing_field(self):
        """Test get_max_mass returns 0 if max_mass field missing."""
        mock_provider = MagicMock()
        mock_classes = {
            'Unknown': {'type': 'Ship'},  # No max_mass
        }
        mock_provider.get_vehicle_classes.return_value = mock_classes

        service = VehicleClassService(registry_provider=mock_provider)
        result = service.get_max_mass('Unknown')

        assert result == 0

    def test_get_type_for_class_returns_type(self):
        """Test get_type_for_class returns the vehicle type for a class."""
        mock_provider = MagicMock()
        mock_classes = {
            'Frigate': {'type': 'Ship', 'max_mass': 2000},
            'Fighter': {'type': 'Craft', 'max_mass': 100},
        }
        mock_provider.get_vehicle_classes.return_value = mock_classes

        service = VehicleClassService(registry_provider=mock_provider)

        assert service.get_type_for_class('Frigate') == 'Ship'
        assert service.get_type_for_class('Fighter') == 'Craft'

    def test_get_type_for_class_returns_default_for_missing(self):
        """Test get_type_for_class returns 'Ship' for unknown class."""
        mock_provider = MagicMock()
        mock_provider.get_vehicle_classes.return_value = {}

        service = VehicleClassService(registry_provider=mock_provider)
        result = service.get_type_for_class('NonExistent')

        assert result == 'Ship'
