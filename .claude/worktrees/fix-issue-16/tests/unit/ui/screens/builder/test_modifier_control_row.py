"""Tests for ModifierControlRow._get_local_bounds method.

PROJ-204 Phase 5: Test the extracted modifier range logic.
"""
import pytest
from unittest.mock import MagicMock


class TestModifierControlRowGetLocalBounds:
    """Tests for _get_local_bounds() method that centralizes range lookup and clamping."""

    @pytest.fixture
    def mock_mod_def(self):
        """Create a mock modifier definition."""
        mod_def = MagicMock()
        mod_def.min_val = 0.0
        mod_def.max_val = 100.0
        return mod_def

    @pytest.fixture
    def row(self, mock_mod_def):
        """Create a ModifierControlRow instance with mocked dependencies."""
        from game.ui.screens.builder.modifier_row import ModifierControlRow

        manager = MagicMock()
        container = MagicMock()
        row = ModifierControlRow(
            manager=manager,
            container=container,
            width=400,
            mod_id='test_mod',
            mod_def=mock_mod_def,
            config={},
            on_change_callback=MagicMock()
        )
        return row

    def test_get_local_bounds_no_component_uses_mod_def(self, row, mock_mod_def):
        """With no component context, uses mod_def min/max."""
        row.component_context = None
        row.current_value = 50.0

        min_v, max_v, clamped = row._get_local_bounds()

        assert min_v == 0.0
        assert max_v == 100.0
        assert clamped == 50.0

    def test_get_local_bounds_clamps_value_to_min(self, row, mock_mod_def):
        """Value below min is clamped."""
        row.component_context = None
        row.current_value = -10.0

        min_v, max_v, clamped = row._get_local_bounds()

        assert clamped == 0.0

    def test_get_local_bounds_clamps_value_to_max(self, row, mock_mod_def):
        """Value above max is clamped."""
        row.component_context = None
        row.current_value = 150.0

        min_v, max_v, clamped = row._get_local_bounds()

        assert clamped == 100.0

    def test_get_local_bounds_with_component_uses_modifier_logic(self, row, mock_mod_def):
        """With component context, uses modifier logic service for bounds."""
        component = MagicMock()
        row.component_context = component
        row.current_value = 50.0

        mock_logic = MagicMock()
        mock_logic.get_local_min_max.return_value = (10.0, 90.0)
        row._logic = mock_logic

        min_v, max_v, clamped = row._get_local_bounds()

        mock_logic.get_local_min_max.assert_called_once_with('test_mod', component)
        assert min_v == 10.0
        assert max_v == 90.0
        assert clamped == 50.0

    def test_get_local_bounds_with_component_clamps_to_component_bounds(self, row, mock_mod_def):
        """Value is clamped to component-specific bounds."""
        component = MagicMock()
        row.component_context = component
        row.current_value = 5.0  # Below component min

        mock_logic = MagicMock()
        mock_logic.get_local_min_max.return_value = (10.0, 90.0)
        row._logic = mock_logic

        min_v, max_v, clamped = row._get_local_bounds()

        assert clamped == 10.0

    def test_get_local_bounds_value_at_boundary(self, row, mock_mod_def):
        """Value exactly at boundary is not changed."""
        row.component_context = None
        row.current_value = 100.0  # Exactly at max

        min_v, max_v, clamped = row._get_local_bounds()

        assert clamped == 100.0


class TestModifierControlRowSetControlsEnabled:
    """Tests for _set_controls_enabled() method that centralizes enable/disable logic."""

    @pytest.fixture
    def mock_mod_def(self):
        """Create a mock modifier definition."""
        mod_def = MagicMock()
        mod_def.min_val = 0.0
        mod_def.max_val = 100.0
        return mod_def

    @pytest.fixture
    def row(self, mock_mod_def):
        """Create a ModifierControlRow instance with mocked dependencies."""
        from game.ui.screens.builder.modifier_row import ModifierControlRow

        manager = MagicMock()
        container = MagicMock()
        row = ModifierControlRow(
            manager=manager,
            container=container,
            width=400,
            mod_id='test_mod',
            mod_def=mock_mod_def,
            config={},
            on_change_callback=MagicMock()
        )
        # Set up mock UI elements
        row.entry = MagicMock()
        row.slider = MagicMock()
        row.buttons = {MagicMock(): {}, MagicMock(): {}}
        return row

    def test_set_controls_enabled_true_enables_all(self, row):
        """When enabled=True, all controls are enabled."""
        row._set_controls_enabled(True)

        row.entry.enable.assert_called_once()
        row.slider.enable.assert_called_once()
        for btn in row.buttons.keys():
            btn.enable.assert_called_once()

    def test_set_controls_enabled_false_disables_all(self, row):
        """When enabled=False, all controls are disabled."""
        row._set_controls_enabled(False)

        row.entry.disable.assert_called_once()
        row.slider.disable.assert_called_once()
        for btn in row.buttons.keys():
            btn.disable.assert_called_once()

    def test_set_controls_enabled_handles_none_entry(self, row):
        """Method handles None entry gracefully."""
        row.entry = None

        # Should not raise
        row._set_controls_enabled(True)
        row._set_controls_enabled(False)

    def test_set_controls_enabled_handles_none_slider(self, row):
        """Method handles None slider gracefully."""
        row.slider = None

        # Should not raise
        row._set_controls_enabled(True)
        row._set_controls_enabled(False)
