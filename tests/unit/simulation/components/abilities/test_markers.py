"""
Unit tests for marker abilities.

Tests CommandAndControl, RequiresCommandAndControl, RequiresCombatMovement,
and StructuralIntegrity marker abilities.

PROJ-367 Phase 1: extended with tests for the new typed
MultiplexTrackingAbility / VehicleStorageAbility / PodStorageAbility classes.

PROJ-FMS-C audit Fix 1: ``TestVehicleLaunchAbility`` removed — the
``VehicleLaunchAbility`` class itself was deleted in favor of the
PROJ-FMS-A Phase 5 ``TacticalFighterLaunchAbility`` /
``StrategicFighterLaunchAbility`` pair (see
``tests/unit/simulation/components/abilities/test_tactical_fighter_launch.py``).
"""
import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock

from game.simulation.components.abilities.markers import (
    CommandAndControl,
    RequiresCommandAndControl,
    RequiresCombatMovement,
    StructuralIntegrity,
    MultiplexTrackingAbility,
    VehicleStorageAbility,
    PodStorageAbility,
)


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

    def test_update_allows_component_without_ship_context(self, mock_component):
        mock_component.ship = None
        ability = RequiresCommandAndControl(mock_component, {})

        assert ability.update() is True

    def test_update_passes_when_active_command_provider_exists(self, mock_component):
        provider = MagicMock()
        provider.is_active = True
        provider.has_ability.return_value = True
        layer = SimpleNamespace(components=[mock_component, provider])
        mock_component.ship = SimpleNamespace(layers={"CORE": layer})
        ability = RequiresCommandAndControl(mock_component, {})

        assert ability.update() is True
        provider.has_ability.assert_called_once_with('CommandAndControl')

    def test_update_fails_when_only_provider_is_inactive(self, mock_component):
        provider = MagicMock()
        provider.is_active = False
        provider.has_ability.return_value = True
        layer = SimpleNamespace(components=[mock_component, provider])
        mock_component.ship = SimpleNamespace(layers={"CORE": layer})
        ability = RequiresCommandAndControl(mock_component, {})

        assert ability.update() is False
        provider.has_ability.assert_not_called()

    def test_update_ignores_own_component_as_command_provider(self, mock_component):
        mock_component.is_active = True
        mock_component.has_ability.return_value = True
        layer = SimpleNamespace(components=[mock_component])
        mock_component.ship = SimpleNamespace(layers={"CORE": layer})
        ability = RequiresCommandAndControl(mock_component, {})

        assert ability.update() is False


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

