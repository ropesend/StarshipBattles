from dataclasses import dataclass
from typing import List

import pytest
from unittest.mock import MagicMock

from game.ui.screens.workshop_screen import DesignWorkshopScreen
from game.ui.screens.workshop_context import WorkshopContext
from game.simulation.components.component import Component


@dataclass
class _MultiSelectionFixture:
    """Value-returning bundle replacing the old `setup(self.X = ...)` autouse.

    Avoids parallel-run fragility from mutating `self.<attr>` in an autouse
    fixture. Each test receives a fresh bundle and operates on it directly.
    """

    builder: DesignWorkshopScreen
    comp_a1: Component
    comp_a2: Component
    comp_a3: Component
    comp_a4: Component


@pytest.fixture
def selection_setup(fresh_registries) -> _MultiSelectionFixture:
    # Display already initialized by enforce_headless / conftest pygame_display_reset

    # PROJ-211: registries is now required
    context = WorkshopContext.standalone(
        tech_preset_name="default", registries=fresh_registries
    )
    builder = DesignWorkshopScreen(800, 600, context)
    builder.viewmodel._ship = MagicMock()
    builder.viewmodel._ship.layers = {}

    # Mocks for panels to avoid errors during event handling/updates
    builder.left_panel = MagicMock()
    builder.right_panel = MagicMock()
    builder.layer_panel = MagicMock()
    builder.modifier_panel = MagicMock()
    builder.weapons_panel = MagicMock()
    if hasattr(builder, "weapons_report_panel"):
        builder.weapons_report_panel = MagicMock()

    comp_data_a = {
        "id": "type_a",
        "name": "Type A",
        "type": "Weapon",
        "mass": 10,
        "hp": 100,
        "modifiers": [],
    }

    comp_a1 = Component(comp_data_a, registries=fresh_registries)
    comp_a2 = Component(comp_data_a, registries=fresh_registries)
    comp_a3 = Component(comp_data_a, registries=fresh_registries)
    comp_a4 = Component(comp_data_a, registries=fresh_registries)

    builder.selected_components = []

    return _MultiSelectionFixture(
        builder=builder,
        comp_a1=comp_a1,
        comp_a2=comp_a2,
        comp_a3=comp_a3,
        comp_a4=comp_a4,
    )


class TestMultiSelectionLogic:
    def test_toggle_behavior(self, selection_setup):
        """Test that Ctrl+Click toggles items in selection."""
        builder = selection_setup.builder

        # 1. Select A1
        builder.on_selection_changed(selection_setup.comp_a1, append=False)
        assert len(builder.selected_components) == 1
        assert builder.selected_components[0][2] == selection_setup.comp_a1

        # 2. Ctrl+Click A2 (Append)
        builder.on_selection_changed(selection_setup.comp_a2, append=True, toggle=True)
        assert len(builder.selected_components) == 2

        # 3. Ctrl+Click A1 (Toggle OFF)
        builder.on_selection_changed(selection_setup.comp_a1, append=True, toggle=True)
        assert len(builder.selected_components) == 1
        assert builder.selected_components[0][2] == selection_setup.comp_a2

        # 4. Ctrl+Click A2 (Toggle OFF) -> Empty
        builder.on_selection_changed(selection_setup.comp_a2, append=True, toggle=True)
        assert len(builder.selected_components) == 0

    def test_range_selection_integration(self, selection_setup):
        """Test usage of get_range_selection via on_selection_changed."""
        builder = selection_setup.builder

        # Setup: A1 is selected
        builder.on_selection_changed(selection_setup.comp_a1, append=False)

        # Simulating Shift Click A4 -> Returns [A1, A2, A3, A4]
        range_selection: List[Component] = [
            selection_setup.comp_a1,
            selection_setup.comp_a2,
            selection_setup.comp_a3,
            selection_setup.comp_a4,
        ]

        # Execute (Shift only -> Replace existing selection with Range)
        builder.on_selection_changed(range_selection, append=False, toggle=False)

        assert len(builder.selected_components) == 4
        # Validate order preservation
        assert builder.selected_components[0][2] == selection_setup.comp_a1
        assert builder.selected_components[3][2] == selection_setup.comp_a4

    def test_range_append_integration(self, selection_setup):
        """Test Ctrl+Shift Append Range."""
        builder = selection_setup.builder

        # Setup A1 Selected
        builder.on_selection_changed(selection_setup.comp_a1, append=False)

        # Range is A3-A4
        range_selection = [selection_setup.comp_a3, selection_setup.comp_a4]

        # Execute (Ctrl+Shift)
        builder.on_selection_changed(range_selection, append=True, toggle=False)

        assert len(builder.selected_components) == 3  # A1 + A3 + A4
        selected_objs = {c[2] for c in builder.selected_components}
        assert selection_setup.comp_a1 in selected_objs
        assert selection_setup.comp_a3 in selected_objs
        assert selection_setup.comp_a4 in selected_objs
