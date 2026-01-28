"""
Tests for MountDependencyRule validation (NEW-SIM-006).

Verifies that components requiring mounts are validated against available mounts.
"""
import pytest
from unittest.mock import Mock

from game.simulation.systems.validator import MountDependencyRule
from game.simulation.components.component_constants import LayerType


class TestMountDependencyRuleFullScan:
    """Tests for full ship scan validation (no component/layer params)."""

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

    def test_full_scan_no_mounts_required_passes(self, rule, mock_ship_with_layers):
        """Ship with no mount-requiring components should pass."""
        # Add components that don't require mounts
        comp1 = Mock()
        comp1.data = {'name': 'engine'}
        mock_ship_with_layers.layers[LayerType.INNER]['components'] = [comp1]

        result = rule.validate(mock_ship_with_layers)

        assert result.is_valid is True

    def test_full_scan_mount_satisfied_passes(self, rule, mock_ship_with_layers):
        """Ship with mount requirement satisfied should pass."""
        # Add a mount
        mount = Mock()
        mount.data = {'name': 'weapon_mount', 'mount_type': 'weapon_mount'}

        # Add component that requires that mount
        weapon = Mock()
        weapon.data = {'name': 'laser', 'required_mount': 'weapon_mount'}

        mock_ship_with_layers.layers[LayerType.OUTER]['components'] = [mount, weapon]

        result = rule.validate(mock_ship_with_layers)

        assert result.is_valid is True

    def test_full_scan_mount_missing_fails(self, rule, mock_ship_with_layers):
        """Ship with unsatisfied mount requirement should fail."""
        # Add component that requires a mount, but no mount present
        weapon = Mock()
        weapon.data = {'name': 'laser', 'required_mount': 'weapon_mount'}

        mock_ship_with_layers.layers[LayerType.OUTER]['components'] = [weapon]

        result = rule.validate(mock_ship_with_layers)

        assert result.is_valid is False
        assert 'weapon_mount' in result.errors[0]

    def test_full_scan_multiple_users_one_mount_fails(self, rule, mock_ship_with_layers):
        """Two mount users with only one mount should fail."""
        # Add one mount
        mount = Mock()
        mount.data = {'mount_type': 'weapon_mount'}

        # Add two weapons that require mounts
        weapon1 = Mock()
        weapon1.data = {'name': 'laser1', 'required_mount': 'weapon_mount'}
        weapon2 = Mock()
        weapon2.data = {'name': 'laser2', 'required_mount': 'weapon_mount'}

        mock_ship_with_layers.layers[LayerType.OUTER]['components'] = [mount, weapon1, weapon2]

        result = rule.validate(mock_ship_with_layers)

        assert result.is_valid is False
        assert 'weapon_mount' in result.errors[0]

    def test_full_scan_multiple_users_multiple_mounts_passes(self, rule, mock_ship_with_layers):
        """Two mount users with two mounts should pass."""
        # Add two mounts
        mount1 = Mock()
        mount1.data = {'mount_type': 'weapon_mount'}
        mount2 = Mock()
        mount2.data = {'mount_type': 'weapon_mount'}

        # Add two weapons
        weapon1 = Mock()
        weapon1.data = {'name': 'laser1', 'required_mount': 'weapon_mount'}
        weapon2 = Mock()
        weapon2.data = {'name': 'laser2', 'required_mount': 'weapon_mount'}

        mock_ship_with_layers.layers[LayerType.OUTER]['components'] = [mount1, mount2, weapon1, weapon2]

        result = rule.validate(mock_ship_with_layers)

        assert result.is_valid is True

    def test_full_scan_across_layers(self, rule, mock_ship_with_layers):
        """Validation should check all layers for mount requirements."""
        # Add weapon in OUTER layer without mount
        weapon = Mock()
        weapon.data = {'name': 'laser', 'required_mount': 'weapon_mount'}
        mock_ship_with_layers.layers[LayerType.OUTER]['components'] = [weapon]

        # Mount in a different layer shouldn't help
        mount = Mock()
        mount.data = {'mount_type': 'weapon_mount'}
        mock_ship_with_layers.layers[LayerType.INNER]['components'] = [mount]

        result = rule.validate(mock_ship_with_layers)

        # Should fail - mount is in different layer than the weapon
        assert result.is_valid is False
