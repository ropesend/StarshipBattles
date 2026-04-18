"""Regression test for WorkshopEventRouter._handle_select_component_type crash.

Bug: Clicking a ship-class-mass-dependent component (bridge, warp_drive,
armor variants, central_complex_command) in the Workshop palette raised
FormulaException: `Undefined variable: 'ship_class_mass'`.

Root cause: `c.clone()` produces a detached component (ship=None). The
immediate `recalculate_stats()` call built a formula context with no
`ship_class_mass`, so formulas like bridge's `=50 * sqrt(ship_class_mass / 1000)`
failed. `docs/02_PATTERNS.md` Pattern 3 and `docs/guides/component_system.md`
require either explicit context OR attachment to a ship before
`recalculate_stats()`.

Fix: Attach the cloned dragged_item to `gui.ship` (the design being edited
in the Workshop) before `recalculate_stats()`. Mirrors the existing fix in
`game/ui/screens/builder/interaction_controller.py:95-99` (shift-drop path).
"""
from unittest.mock import MagicMock

import pytest

from game.simulation.components.component import create_component
from game.ui.screens.workshop_event_router import WorkshopEventRouter


def _make_gui(design_mass_budget: float = 2000.0):
    """Build a minimal mock DesignWorkshopScreen for the router.

    Only the attributes `_handle_select_component_type` touches are set.
    """
    gui = MagicMock()
    # Workshop ship-in-progress with the attribute build_formula_context reads.
    gui.ship = MagicMock()
    gui.ship.max_mass_budget = design_mass_budget
    # Controller holds dragged_item (starts unset).
    gui.controller = MagicMock()
    gui.controller.dragged_item = None
    # Panels touched by the handler.
    gui.layer_panel = MagicMock()
    gui.layer_panel.selected_group_key = None
    gui.layer_panel.selected_component_id = None
    return gui


class TestSelectComponentTypeAttachesShip:
    """The cloned dragged_item must be attached to gui.ship before
    recalculate_stats() so ship_class_mass-dependent formulas resolve."""

    def test_selecting_bridge_does_not_raise_formula_exception(
        self, fresh_registries
    ):
        """Clicking bridge in the palette must not raise FormulaException.

        Bridge mass: `=50 * sqrt(ship_class_mass / 1000)` (data/components.json).
        Before the fix this crashed because the cloned dragged_item had
        ship=None and no explicit context was threaded through.
        """
        bridge = create_component('bridge', registries=fresh_registries)
        gui = _make_gui(design_mass_budget=2000.0)
        router = WorkshopEventRouter(gui)

        # Must not raise.
        router._handle_select_component_type(bridge)

    def test_dragged_item_is_attached_to_workshop_ship(self, fresh_registries):
        """After selection the dragged_item.ship must be the Workshop's
        design ship, so downstream recalculate_stats() calls (modifier
        toggles, value edits) also resolve ship_class_mass via the
        attached-component path."""
        bridge = create_component('bridge', registries=fresh_registries)
        gui = _make_gui(design_mass_budget=2000.0)
        router = WorkshopEventRouter(gui)

        router._handle_select_component_type(bridge)

        assert gui.controller.dragged_item is not None
        assert gui.controller.dragged_item.ship is gui.ship

    def test_dragged_item_mass_reflects_design_mass_budget(
        self, fresh_registries
    ):
        """With the fix, bridge mass is computed against the Workshop's
        design ship. Formula: 50 * sqrt(2000/1000) ≈ 70.7 for a 2000t design."""
        bridge = create_component('bridge', registries=fresh_registries)
        gui = _make_gui(design_mass_budget=2000.0)
        router = WorkshopEventRouter(gui)

        router._handle_select_component_type(bridge)

        expected = 50.0 * (2000.0 / 1000.0) ** 0.5
        assert gui.controller.dragged_item.mass == pytest.approx(expected, abs=0.1)
