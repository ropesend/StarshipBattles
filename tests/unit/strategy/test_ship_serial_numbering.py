"""Tests for ship serial number system - PROJ-03 Phase 1."""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.ship_instance import ShipInstance
from game.strategy.data.empire import Empire


class TestEmpireSerialCounter:
    """Test cases for Empire.get_next_serial() method."""

    @pytest.fixture
    def empire(self):
        """Create a basic empire for testing."""
        return Empire(
            empire_id=0,
            name="Test Empire",
            color=(255, 0, 0)
        )

    def test_serial_counter_starts_at_one(self, empire):
        """First serial for a design should be 1."""
        serial = empire.get_next_serial("Destroyer")
        assert serial == 1

    def test_serial_counter_increments(self, empire):
        """Serial counter should increment with each call."""
        serial1 = empire.get_next_serial("Destroyer")
        serial2 = empire.get_next_serial("Destroyer")
        serial3 = empire.get_next_serial("Destroyer")

        assert serial1 == 1
        assert serial2 == 2
        assert serial3 == 3

    def test_different_designs_have_independent_counters(self, empire):
        """Each design_id should have its own counter."""
        serial_destroyer_1 = empire.get_next_serial("Destroyer")
        serial_cruiser_1 = empire.get_next_serial("Cruiser")
        serial_destroyer_2 = empire.get_next_serial("Destroyer")
        serial_scout_1 = empire.get_next_serial("Scout")
        serial_cruiser_2 = empire.get_next_serial("Cruiser")

        assert serial_destroyer_1 == 1
        assert serial_destroyer_2 == 2
        assert serial_cruiser_1 == 1
        assert serial_cruiser_2 == 2
        assert serial_scout_1 == 1

    def test_serial_counter_persists_through_save_load(self, empire):
        """Serial counters should be saved and restored correctly."""
        # Generate some serials
        empire.get_next_serial("Destroyer")
        empire.get_next_serial("Destroyer")
        empire.get_next_serial("Cruiser")

        # Serialize
        data = empire.to_dict()

        # Check serialization includes counters
        assert '_design_serial_counters' in data
        assert data['_design_serial_counters']['Destroyer'] == 2
        assert data['_design_serial_counters']['Cruiser'] == 1

        # Deserialize (galaxy=None is ok for this test)
        restored = Empire.from_dict(data, galaxy=None)

        # Next serials should continue from where we left off
        assert restored.get_next_serial("Destroyer") == 3
        assert restored.get_next_serial("Cruiser") == 2
        assert restored.get_next_serial("Scout") == 1  # New design starts at 1


class TestShipInstanceSerial:
    """Test cases for ShipInstance serial number field."""

    @pytest.fixture
    def design_data(self):
        """Create basic design data for testing."""
        return {
            'name': 'Destroyer',
            'expected_stats': {'max_hp': 100, 'mass': 500}
        }

    def test_ship_instance_has_serial_field(self, design_data):
        """ShipInstance should have a serial field."""
        instance = ShipInstance.create(design_data, owner_id=0)
        # Serial should be None by default if not provided
        assert hasattr(instance, 'serial')
        assert instance.serial is None

    def test_serial_saved_to_dict(self, design_data):
        """Serial should be included in to_dict() output."""
        instance = ShipInstance.create(design_data, owner_id=0)
        instance.serial = 42

        data = instance.to_dict()

        assert 'serial' in data
        assert data['serial'] == 42

    def test_serial_restored_from_dict(self, design_data):
        """Serial should be restored by from_dict()."""
        instance = ShipInstance.create(design_data, owner_id=0)
        instance.serial = 123

        data = instance.to_dict()
        restored = ShipInstance.from_dict(data)

        assert restored.serial == 123

    def test_serial_none_when_not_in_dict(self, design_data):
        """Serial should be None when loading old save without serial."""
        data = {
            'instance_id': 'test-123',
            'design_id': 'Destroyer',
            'name': 'Destroyer',
            'owner_id': 0,
            'design_data': design_data,
            # No 'serial' key - simulates old save format
        }

        instance = ShipInstance.from_dict(data)

        assert instance.serial is None


class TestShipInstanceDisplayId:
    """Test cases for ShipInstance.get_display_id() method."""

    @pytest.fixture
    def design_data(self):
        """Create basic design data for testing."""
        return {
            'name': 'Destroyer',
            'expected_stats': {'max_hp': 100}
        }

    def test_display_id_format(self, design_data):
        """Display ID should be 'DesignName-000001' format."""
        instance = ShipInstance.create(design_data, owner_id=0)
        instance.serial = 1

        display_id = instance.get_display_id()

        assert display_id == "Destroyer-000001"

    def test_display_id_with_larger_serial(self, design_data):
        """Display ID should pad serial to 6 digits."""
        instance = ShipInstance.create(design_data, owner_id=0)
        instance.serial = 1034

        display_id = instance.get_display_id()

        assert display_id == "Destroyer-001034"

    def test_display_id_uses_design_name(self):
        """Display ID should use design name, not instance name."""
        design_data = {'name': 'Cruiser', 'expected_stats': {'max_hp': 200}}
        instance = ShipInstance.create(design_data, owner_id=0, name="USS Enterprise")
        instance.serial = 7

        display_id = instance.get_display_id()

        # Should use design name "Cruiser", not instance name "USS Enterprise"
        assert display_id == "Cruiser-000007"

    def test_display_id_returns_none_without_serial(self, design_data):
        """Display ID should return None if serial is not set."""
        instance = ShipInstance.create(design_data, owner_id=0)
        instance.serial = None

        display_id = instance.get_display_id()

        assert display_id is None


class TestShipCreationWithEmpire:
    """Test cases for ShipInstance.create() with empire parameter."""

    @pytest.fixture
    def empire(self):
        """Create a basic empire for testing."""
        return Empire(empire_id=0, name="Test Empire", color=(255, 0, 0))

    @pytest.fixture
    def design_data(self):
        """Create basic design data for testing."""
        return {
            'name': 'Destroyer',
            'expected_stats': {'max_hp': 100}
        }

    def test_create_with_empire_assigns_serial(self, design_data, empire):
        """Creating ship with empire should automatically assign serial."""
        instance = ShipInstance.create(design_data, owner_id=0, empire=empire)

        assert instance.serial == 1

    def test_create_with_empire_increments_serial(self, design_data, empire):
        """Multiple ships with same design get incrementing serials."""
        instance1 = ShipInstance.create(design_data, owner_id=0, empire=empire)
        instance2 = ShipInstance.create(design_data, owner_id=0, empire=empire)
        instance3 = ShipInstance.create(design_data, owner_id=0, empire=empire)

        assert instance1.serial == 1
        assert instance2.serial == 2
        assert instance3.serial == 3

    def test_create_without_empire_has_no_serial(self, design_data):
        """Creating ship without empire should leave serial as None."""
        instance = ShipInstance.create(design_data, owner_id=0)

        assert instance.serial is None

    def test_create_with_empire_uses_design_id_for_counter(self, empire):
        """Serial counter should use design_id, not design name."""
        design_data = {
            'name': 'Destroyer MK1',  # Display name
            'expected_stats': {'max_hp': 100}
        }

        # Create with explicit design_id
        instance1 = ShipInstance.create(
            design_data,
            owner_id=0,
            design_id="destroyer_mk1_v2",
            empire=empire
        )
        instance2 = ShipInstance.create(
            design_data,
            owner_id=0,
            design_id="destroyer_mk1_v2",
            empire=empire
        )

        assert instance1.serial == 1
        assert instance2.serial == 2

        # Different design_id should start at 1
        instance3 = ShipInstance.create(
            design_data,
            owner_id=0,
            design_id="different_design",
            empire=empire
        )
        assert instance3.serial == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
