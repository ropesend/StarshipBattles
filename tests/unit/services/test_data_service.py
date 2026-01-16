"""
Tests for DataService.

This service provides a facade over data loading operations,
handling components, modifiers, vehicle classes, and related data.
"""
import pytest

from game.simulation.services.data_service import DataService


@pytest.fixture
def service():
    """Create a DataService instance."""
    return DataService()


class TestDataServiceIsLoaded:
    """Tests for DataService.is_loaded()."""

    def test_is_loaded_returns_bool(self, service):
        """is_loaded() returns boolean."""
        # reset_game_state fixture auto-loads data
        result = service.is_loaded()

        assert isinstance(result, bool)

    def test_is_loaded_true_when_data_present(self, service):
        """is_loaded() returns True when registries populated."""
        # reset_game_state fixture loads data
        assert service.is_loaded() is True


class TestDataServiceGetComponents:
    """Tests for DataService.get_components()."""

    def test_get_components_returns_dict(self, service):
        """get_components() returns a dictionary."""
        components = service.get_components()

        assert isinstance(components, dict)
        assert len(components) > 0

    def test_get_components_has_expected_keys(self, service):
        """get_components() returns component definitions."""
        components = service.get_components()

        # Should have some known components
        assert any('bridge' in comp_id for comp_id in components.keys())


class TestDataServiceGetModifiers:
    """Tests for DataService.get_modifiers()."""

    def test_get_modifiers_returns_dict(self, service):
        """get_modifiers() returns a dictionary."""
        modifiers = service.get_modifiers()

        assert isinstance(modifiers, dict)

    def test_get_modifiers_structure(self, service):
        """get_modifiers() returns modifier definitions."""
        modifiers = service.get_modifiers()

        # Modifiers should exist (may be empty in some test configs)
        assert isinstance(modifiers, dict)


class TestDataServiceGetVehicleClasses:
    """Tests for DataService.get_vehicle_classes()."""

    def test_get_vehicle_classes_returns_dict(self, service):
        """get_vehicle_classes() returns a dictionary."""
        classes = service.get_vehicle_classes()

        assert isinstance(classes, dict)
        assert len(classes) > 0

    def test_get_vehicle_classes_has_expected_classes(self, service):
        """get_vehicle_classes() contains known ship classes."""
        classes = service.get_vehicle_classes()

        assert "Escort" in classes
        assert "Cruiser" in classes


class TestDataServiceGetComponent:
    """Tests for DataService.get_component()."""

    def test_get_component_existing(self, service):
        """get_component() returns component definition."""
        component = service.get_component("bridge")

        assert component is not None
        # Registry stores Component objects with id attribute
        assert hasattr(component, 'id') and component.id == "bridge"

    def test_get_component_nonexistent(self, service):
        """get_component() returns None for unknown ID."""
        component = service.get_component("nonexistent_component_xyz")

        assert component is None


class TestDataServiceGetVehicleClass:
    """Tests for DataService.get_vehicle_class()."""

    def test_get_vehicle_class_existing(self, service):
        """get_vehicle_class() returns class definition."""
        class_def = service.get_vehicle_class("Escort")

        assert class_def is not None
        assert class_def.get("type") == "Ship"

    def test_get_vehicle_class_nonexistent(self, service):
        """get_vehicle_class() returns None for unknown class."""
        class_def = service.get_vehicle_class("NonexistentClass")

        assert class_def is None


class TestDataServiceGetComponentsByType:
    """Tests for DataService.get_components_by_type()."""

    def test_get_components_by_type_weapons(self, service):
        """get_components_by_type() filters by classification."""
        weapons = service.get_components_by_classification("Weapons")

        assert isinstance(weapons, list)
        # Should have some weapons
        assert len(weapons) > 0

    def test_get_components_by_type_engines(self, service):
        """get_components_by_type() returns engines."""
        engines = service.get_components_by_classification("Engines")

        assert isinstance(engines, list)


class TestDataServiceGetClassesByType:
    """Tests for DataService.get_classes_by_type()."""

    def test_get_classes_by_type_ship(self, service):
        """get_classes_by_type() returns ship classes."""
        ships = service.get_classes_by_type("Ship")

        assert isinstance(ships, list)
        assert len(ships) > 0
        assert "Escort" in ships

    def test_get_classes_by_type_fighter(self, service):
        """get_classes_by_type() returns fighter classes."""
        fighters = service.get_classes_by_type("Fighter")

        assert isinstance(fighters, list)
