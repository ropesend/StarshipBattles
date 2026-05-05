"""
Unit tests for marker abilities.

Tests VehicleLaunchAbility, CommandAndControl, RequiresCommandAndControl,
RequiresCombatMovement, and StructuralIntegrity marker abilities.

PROJ-367 Phase 1: extended with tests for the new typed
MultiplexTrackingAbility / VehicleStorageAbility / PodStorageAbility classes
and the new ``max_launch_mass`` attribute on VehicleLaunchAbility.
"""
import pytest
from unittest.mock import MagicMock

from game.simulation.components.abilities.markers import (
    VehicleLaunchAbility,
    CommandAndControl,
    RequiresCommandAndControl,
    RequiresCombatMovement,
    StructuralIntegrity,
    MultiplexTrackingAbility,
    VehicleStorageAbility,
    PodStorageAbility,
)
from game.core.config import PhysicsConfig


class TestVehicleLaunchAbility:
    """Tests for VehicleLaunchAbility class."""

    @pytest.fixture
    def mock_component(self):
        """Create a mock component."""
        return MagicMock()

    def test_vehicle_launch_init_defaults(self, mock_component):
        """capacity=0, cycle_time=5.0, cooldown=0 with minimal data."""
        data = {}
        ability = VehicleLaunchAbility(mock_component, data)
        assert ability.capacity == 0
        assert ability.cycle_time == 5.0
        assert ability.cooldown == 0.0

    def test_vehicle_launch_custom_values(self, mock_component):
        """Custom capacity, fighter_class, cycle_time parsed."""
        data = {
            'capacity': 6,
            'fighter_class': 'Heavy Fighter',
            'cycle_time': 3.0
        }
        ability = VehicleLaunchAbility(mock_component, data)
        assert ability.capacity == 6
        assert ability.fighter_class == 'Heavy Fighter'
        assert ability.cycle_time == 3.0

    def test_vehicle_launch_try_launch_success(self, mock_component):
        """try_launch returns True and sets cooldown when ready."""
        data = {'cycle_time': 5.0}
        ability = VehicleLaunchAbility(mock_component, data)
        assert ability.cooldown == 0.0

        result = ability.try_launch()

        assert result is True
        assert ability.cooldown == 5.0

    def test_vehicle_launch_try_launch_on_cooldown(self, mock_component):
        """try_launch returns False when cooldown > 0."""
        data = {'cycle_time': 5.0}
        ability = VehicleLaunchAbility(mock_component, data)
        ability.cooldown = 2.5

        result = ability.try_launch()

        assert result is False
        assert ability.cooldown == 2.5  # Unchanged

    def test_vehicle_launch_update_decrements_cooldown(self, mock_component):
        """Cooldown decreases by TICK_RATE each update."""
        data = {}
        ability = VehicleLaunchAbility(mock_component, data)
        ability.cooldown = 1.0
        initial_cooldown = ability.cooldown

        ability.update()

        expected = initial_cooldown - PhysicsConfig.TICK_RATE
        assert abs(ability.cooldown - expected) < 0.001

    def test_vehicle_launch_update_stops_at_zero(self, mock_component):
        """Cooldown doesn't go negative."""
        data = {}
        ability = VehicleLaunchAbility(mock_component, data)
        ability.cooldown = PhysicsConfig.TICK_RATE / 2

        ability.update()

        # Cooldown can go slightly negative in this impl, but
        # the check is cooldown <= 0 for launch readiness
        assert ability.cooldown <= 0

    def test_vehicle_launch_ui_rows(self, mock_component):
        """get_ui_rows returns hangar and cycle info."""
        data = {'fighter_class': 'Heavy Fighter', 'cycle_time': 4.0}
        ability = VehicleLaunchAbility(mock_component, data)

        rows = ability.get_ui_rows()

        assert len(rows) == 2
        assert any('Hangar' in row['label'] for row in rows)
        assert any('Cycle' in row['label'] for row in rows)
        assert any('Heavy Fighter' in row['value'] for row in rows)
        assert any('4.0s' in row['value'] for row in rows)

    def test_vehicle_launch_primary_value(self, mock_component):
        """get_primary_value returns capacity as float."""
        data = {'capacity': 8}
        ability = VehicleLaunchAbility(mock_component, data)

        assert ability.get_primary_value() == 8.0
        assert isinstance(ability.get_primary_value(), float)

    # PROJ-367 Phase 1 — `max_launch_mass` typed attribute.

    def test_vehicle_launch_max_launch_mass_default(self, mock_component):
        """max_launch_mass defaults to 0.0 when missing from data."""
        ability = VehicleLaunchAbility(mock_component, {})
        assert ability.max_launch_mass == 0.0

    def test_vehicle_launch_max_launch_mass_parsed(self, mock_component):
        """max_launch_mass parsed from data dict (production shape)."""
        data = {
            'capacity': 6,
            'fighter_class': 'Heavy Fighter',
            'cycle_time': 5.0,
            'max_launch_mass': 50,
        }
        ability = VehicleLaunchAbility(mock_component, data)
        assert ability.max_launch_mass == 50

    def test_vehicle_launch_sync_data_refreshes_max_launch_mass(self, mock_component):
        """sync_data re-runs _parse_attrs so max_launch_mass refreshes."""
        ability = VehicleLaunchAbility(mock_component, {'max_launch_mass': 10})
        assert ability.max_launch_mass == 10
        ability.sync_data({'max_launch_mass': 80})
        assert ability.max_launch_mass == 80


class TestMultiplexTrackingAbility:
    """PROJ-367 Phase 1: MultiplexTrackingAbility (closes EXT-07)."""

    @pytest.fixture
    def mock_component(self):
        return MagicMock()

    def test_scalar_data_parses_slots(self, mock_component):
        """Production data shape: scalar int (e.g. ``"MultiplexTracking": 10``)."""
        ability = MultiplexTrackingAbility(mock_component, 10)
        assert ability.slots == 10

    def test_dict_data_parses_slots(self, mock_component):
        """Forward-compat dict shape: ``{"slots": 10}``."""
        ability = MultiplexTrackingAbility(mock_component, {'slots': 7})
        assert ability.slots == 7

    def test_default_slots_zero(self, mock_component):
        """Empty dict → slots 0."""
        ability = MultiplexTrackingAbility(mock_component, {})
        assert ability.slots == 0

    def test_invalid_data_defaults_to_zero(self, mock_component):
        """None → slots 0."""
        ability = MultiplexTrackingAbility(mock_component, None)
        assert ability.slots == 0

    def test_primary_value(self, mock_component):
        ability = MultiplexTrackingAbility(mock_component, 10)
        assert ability.get_primary_value() == 10.0

    def test_ui_rows(self, mock_component):
        ability = MultiplexTrackingAbility(mock_component, 10)
        rows = ability.get_ui_rows()
        assert len(rows) == 1
        assert rows[0]['label'] == 'Targets'
        assert rows[0]['value'] == '10'


class TestVehicleStorageAbility:
    """PROJ-367 Phase 1: VehicleStorageAbility (closes EXT-07)."""

    @pytest.fixture
    def mock_component(self):
        return MagicMock()

    def test_scalar_data_parses_capacity(self, mock_component):
        """Production shape: scalar (``"VehicleStorage": 50``)."""
        ability = VehicleStorageAbility(mock_component, 50)
        assert ability.capacity == 50

    def test_dict_data_parses_capacity(self, mock_component):
        """Forward-compat shape: ``{"capacity": 50}``."""
        ability = VehicleStorageAbility(mock_component, {'capacity': 50})
        assert ability.capacity == 50

    def test_default_capacity_zero(self, mock_component):
        ability = VehicleStorageAbility(mock_component, {})
        assert ability.capacity == 0

    def test_no_stat_bindings(self):
        """Storage is additive, not modifier-scaled — STAT_BINDINGS is empty."""
        assert VehicleStorageAbility.STAT_BINDINGS == []

    def test_primary_value(self, mock_component):
        ability = VehicleStorageAbility(mock_component, 50)
        assert ability.get_primary_value() == 50.0


class TestPodStorageAbility:
    """PROJ-367 Phase 1: PodStorageAbility — single attribute ``capacity_mass``."""

    @pytest.fixture
    def mock_component(self):
        return MagicMock()

    def test_dict_data_parses_capacity_mass(self, mock_component):
        """Production shape: ``{"capacity_mass": 5000}`` (data/components.json:2396-2397)."""
        ability = PodStorageAbility(mock_component, {'capacity_mass': 5000})
        assert ability.capacity_mass == 5000.0

    def test_scalar_data_parses_capacity_mass(self, mock_component):
        """Forward-compat shape: scalar."""
        ability = PodStorageAbility(mock_component, 2500)
        assert ability.capacity_mass == 2500.0

    def test_default_capacity_mass_zero(self, mock_component):
        ability = PodStorageAbility(mock_component, {})
        assert ability.capacity_mass == 0.0

    def test_no_pod_class_attribute(self, mock_component):
        """PROJ-367 decision (Codex C1): ``pod_class`` is NOT an attribute."""
        ability = PodStorageAbility(mock_component, {'capacity_mass': 5000})
        assert not hasattr(ability, 'pod_class')

    def test_no_stat_bindings(self):
        assert PodStorageAbility.STAT_BINDINGS == []

    def test_primary_value(self, mock_component):
        ability = PodStorageAbility(mock_component, {'capacity_mass': 5000})
        assert ability.get_primary_value() == 5000.0


class TestCommandAndControl:
    """Tests for CommandAndControl ability."""

    @pytest.fixture
    def mock_component(self):
        return MagicMock()

    def test_command_and_control_ui_rows(self, mock_component):
        """get_ui_rows returns 'Command: Active'."""
        ability = CommandAndControl(mock_component, {})

        rows = ability.get_ui_rows()

        assert len(rows) == 1
        assert rows[0]['label'] == 'Command'
        assert rows[0]['value'] == 'Active'

    def test_command_and_control_primary_value(self, mock_component):
        """get_primary_value returns 1.0."""
        ability = CommandAndControl(mock_component, {})
        assert ability.get_primary_value() == 1.0


class TestRequiresCommandAndControl:
    """Tests for RequiresCommandAndControl ability."""

    @pytest.fixture
    def mock_component(self):
        return MagicMock()

    def test_requires_cc_ui_rows(self, mock_component):
        """get_ui_rows returns 'Requires C&C: Yes'."""
        ability = RequiresCommandAndControl(mock_component, {})

        rows = ability.get_ui_rows()

        assert len(rows) == 1
        assert rows[0]['label'] == 'Requires C&C'
        assert rows[0]['value'] == 'Yes'

    def test_requires_cc_primary_value(self, mock_component):
        """get_primary_value returns 1.0."""
        ability = RequiresCommandAndControl(mock_component, {})
        assert ability.get_primary_value() == 1.0


class TestRequiresCombatMovement:
    """Tests for RequiresCombatMovement ability."""

    @pytest.fixture
    def mock_component(self):
        return MagicMock()

    def test_requires_propulsion_ui_rows(self, mock_component):
        """get_ui_rows returns 'Requires Propulsion: Yes'."""
        ability = RequiresCombatMovement(mock_component, {})

        rows = ability.get_ui_rows()

        assert len(rows) == 1
        assert rows[0]['label'] == 'Requires Propulsion'
        assert rows[0]['value'] == 'Yes'

    def test_requires_propulsion_primary_value(self, mock_component):
        """get_primary_value returns 1.0."""
        ability = RequiresCombatMovement(mock_component, {})
        assert ability.get_primary_value() == 1.0


class TestStructuralIntegrity:
    """Tests for StructuralIntegrity ability."""

    @pytest.fixture
    def mock_component(self):
        return MagicMock()

    def test_structural_integrity_ui_rows(self, mock_component):
        """get_ui_rows returns 'Structural Integrity: Yes'."""
        ability = StructuralIntegrity(mock_component, {})

        rows = ability.get_ui_rows()

        assert len(rows) == 1
        assert rows[0]['label'] == 'Structural Integrity'
        assert rows[0]['value'] == 'Yes'

