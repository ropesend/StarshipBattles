"""
Tests for MountDependencyRule validation (NEW-SIM-006).

Verifies that components requiring mounts are validated against available mounts.

PROJ-43 Phase 11: Updated tests to match actual implementation behavior.
MountDependencyRule is an AdditionValidationRule that validates component additions,
not full ship scans. Full-ship mount validation is intentionally not supported
because mount validation happens at component-addition time via validate_addition().

The design_rules in ShipDesignValidator do not include MountDependencyRule because
mount consistency is enforced during the build process, not as a post-hoc check.
"""
import pytest
from unittest.mock import Mock

from game.simulation.validation.ship_validator import MountDependencyRule
from game.core.constants import LayerType


class TestMountDependencyRuleComponentAddition:
    """Tests for component addition validation (with component/layer_type params).

    This is the primary use case - validating whether a component can be added
    to a ship based on available mounts.
    """

    @pytest.fixture
    def rule(self):
        """Create the validation rule."""
        return MountDependencyRule()

    @pytest.fixture
    def mock_ship_with_layers(self):
        """Create a mock ship with layer structure."""
        ship = Mock()
        ship.layers = {
            LayerType.OUTER: {'components': []},
            LayerType.INNER: {'components': []},
            LayerType.CORE: {'components': []},
        }
        return ship

    def test_component_without_mount_requirement_passes(self, rule, mock_ship_with_layers):
        """Component that doesn't require a mount should always pass."""
        component = Mock()
        component.data = {'name': 'engine'}

        result = rule.validate(mock_ship_with_layers, component, LayerType.INNER)

        assert result.is_valid is True

    def test_component_with_satisfied_mount_passes(self, rule, mock_ship_with_layers):
        """Component with mount requirement satisfied should pass."""
        # Add a mount to the layer first
        mount = Mock()
        mount.data = {'name': 'weapon_mount', 'mount_type': 'weapon_mount'}
        mock_ship_with_layers.layers[LayerType.OUTER]['components'] = [mount]

        # Try to add component that requires that mount
        weapon = Mock()
        weapon.data = {'name': 'laser', 'required_mount': 'weapon_mount'}

        result = rule.validate(mock_ship_with_layers, weapon, LayerType.OUTER)

        assert result.is_valid is True

    def test_component_with_missing_mount_fails(self, rule, mock_ship_with_layers):
        """Component with unsatisfied mount requirement should fail."""
        # No mount in the layer
        component = Mock()
        component.data = {'name': 'laser', 'required_mount': 'weapon_mount'}

        result = rule.validate(mock_ship_with_layers, component, LayerType.OUTER)

        assert result.is_valid is False
        assert 'weapon_mount' in result.errors[0]
        assert 'OUTER' in result.errors[0]

    def test_mount_in_different_layer_does_not_satisfy(self, rule, mock_ship_with_layers):
        """Mount in different layer should not satisfy requirement."""
        # Add mount to INNER layer
        mount = Mock()
        mount.data = {'mount_type': 'weapon_mount'}
        mock_ship_with_layers.layers[LayerType.INNER]['components'] = [mount]

        # Try to add weapon to OUTER layer
        weapon = Mock()
        weapon.data = {'name': 'laser', 'required_mount': 'weapon_mount'}

        result = rule.validate(mock_ship_with_layers, weapon, LayerType.OUTER)

        assert result.is_valid is False
        assert 'weapon_mount' in result.errors[0]

    def test_mount_can_only_be_used_once(self, rule, mock_ship_with_layers):
        """One mount should only support one mount-requiring component."""
        # Add one mount and one existing weapon user
        mount = Mock()
        mount.data = {'mount_type': 'weapon_mount'}
        existing_weapon = Mock()
        existing_weapon.data = {'name': 'existing_laser', 'required_mount': 'weapon_mount'}
        mock_ship_with_layers.layers[LayerType.OUTER]['components'] = [mount, existing_weapon]

        # Try to add another weapon (should fail - mount already in use)
        new_weapon = Mock()
        new_weapon.data = {'name': 'new_laser', 'required_mount': 'weapon_mount'}

        result = rule.validate(mock_ship_with_layers, new_weapon, LayerType.OUTER)

        assert result.is_valid is False
        assert 'weapon_mount' in result.errors[0]

    def test_multiple_mounts_support_multiple_components(self, rule, mock_ship_with_layers):
        """Two mounts should support two mount-requiring components."""
        # Add two mounts and one existing weapon user
        mount1 = Mock()
        mount1.data = {'mount_type': 'weapon_mount'}
        mount2 = Mock()
        mount2.data = {'mount_type': 'weapon_mount'}
        existing_weapon = Mock()
        existing_weapon.data = {'name': 'existing_laser', 'required_mount': 'weapon_mount'}
        mock_ship_with_layers.layers[LayerType.OUTER]['components'] = [mount1, mount2, existing_weapon]

        # Try to add another weapon (should pass - second mount is available)
        new_weapon = Mock()
        new_weapon.data = {'name': 'new_laser', 'required_mount': 'weapon_mount'}

        result = rule.validate(mock_ship_with_layers, new_weapon, LayerType.OUTER)

        assert result.is_valid is True


class TestMountDependencyRuleNoComponent:
    """Tests for behavior when called without component/layer_type.

    PROJ-43: AdditionValidationRule skips validation when component/layer_type
    are not provided. This is by design - mount validation is an addition-time
    check, not a design-time check.
    """

    @pytest.fixture
    def rule(self):
        """Create the validation rule."""
        return MountDependencyRule()

    @pytest.fixture
    def mock_ship_with_layers(self):
        """Create a mock ship with layer structure."""
        ship = Mock()
        ship.layers = {
            LayerType.OUTER: {'components': []},
            LayerType.INNER: {'components': []},
            LayerType.CORE: {'components': []},
        }
        return ship

    def test_no_component_returns_valid(self, rule, mock_ship_with_layers):
        """Calling validate without component should return valid (skips check)."""
        # This behavior is intentional - AdditionValidationRule skips when no component
        result = rule.validate(mock_ship_with_layers)

        assert result.is_valid is True

    def test_no_component_does_not_scan_ship(self, rule, mock_ship_with_layers):
        """Calling validate without component should not perform full-ship scan.

        PROJ-43: Full-ship mount validation is not supported. Mount consistency
        is enforced at component-addition time. If you have a ship with invalid
        mount relationships, it means validation was bypassed during construction.
        """
        # Add a weapon without a mount (invalid state)
        weapon = Mock()
        weapon.data = {'name': 'laser', 'required_mount': 'weapon_mount'}
        mock_ship_with_layers.layers[LayerType.OUTER]['components'] = [weapon]

        # Call without component - should NOT detect the invalid state
        result = rule.validate(mock_ship_with_layers)

        # Returns valid because no component-addition check is performed
        assert result.is_valid is True
