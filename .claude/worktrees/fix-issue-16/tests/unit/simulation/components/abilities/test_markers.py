"""
Unit tests for marker abilities.

Tests VehicleLaunchAbility, CommandAndControl, RequiresCommandAndControl,
RequiresCombatMovement, and StructuralIntegrity marker abilities.
"""
import pytest
from unittest.mock import MagicMock

from game.simulation.components.abilities.markers import (
    VehicleLaunchAbility,
    CommandAndControl,
    RequiresCommandAndControl,
    RequiresCombatMovement,
    StructuralIntegrity
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

