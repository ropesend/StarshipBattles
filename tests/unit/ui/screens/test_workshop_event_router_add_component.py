"""Regression test for WorkshopEventRouter._handle_add_component crash.

Bug: Clicking the ``+`` button to add another instance of a component that
already exists in a ship layer raised ``FormulaException: Undefined variable:
'ship_class_mass'`` whenever the component had a ``ship_class_mass``-dependent
formula (bridge, the three armor variants, warp_drive).

Crash flow (pre-fix):
1. ``_handle_add_component`` clones ``target_comp`` -> ``new_comp.ship is None``
2. ``copy_modifiers(target_comp, new_comp)`` calls
   ``new_comp.recalculate_stats()`` with no context.
3. ``build_formula_context`` returns ``{}`` (no ``.ship``, no explicit context).
4. ``FormulaEvaluator.evaluate("=50 * sqrt(ship_class_mass / 1000)", {})``
   raises ``FormulaException``.

Root cause: ``Component.clone()`` did not propagate ``self.ship``. Two other
call sites (``_handle_select_component_type`` and the shift-drop path in
``interaction_controller``) had been mitigating this manually via
``clone.ship = source.ship``; this third call site was missed. Fixing
``Component.clone()`` to propagate ``.ship`` removes the bug class for all
clone-then-recalc paths.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.core.constants import LayerType
from game.simulation.components.component import create_component
from game.simulation.entities.ship import Ship
from game.ui.screens.workshop_event_router import WorkshopEventRouter


def _make_gui_with_target_comp(target_comp):
    """Build a minimal mock DesignWorkshopScreen for the router.

    Only the attributes ``_handle_add_component`` touches in the
    ``add_individual`` branch are populated. The viewmodel's
    ``add_component_instance`` is stubbed to return True so the handler
    completes without exercising the real ship service.
    """
    gui = MagicMock()
    gui.viewmodel.add_component_instance.return_value = True
    gui.viewmodel.last_errors = []
    return gui


def _attached_ship_and_comp(comp_id, fresh_registries):
    """Create a real Ship + real component with the component attached.

    Mirrors how a workshop design holds components: ``component.ship`` is
    set to the design's Ship instance, which has ``max_mass_budget``.
    """
    ship = Ship(
        "TestShip", 0, 0, (255, 255, 255), registries=fresh_registries
    )
    ship.max_mass_budget = 2000.0
    comp = create_component(comp_id, registries=fresh_registries)
    comp.ship = ship
    return ship, comp


class TestHandleAddComponentDoesNotCrash:
    """Adding another instance of a ``ship_class_mass``-formula component
    must not raise ``FormulaException``. This was the user-reported crash."""

    @pytest.mark.parametrize(
        "comp_id",
        [
            "bridge",
            "emissive_armor",
            "shield_regenerating_armor",
            "scattering_armor",
            "warp_drive",
        ],
    )
    def test_add_individual_does_not_raise_for_ship_class_mass_formula_component(
        self, fresh_registries, comp_id
    ):
        """For every ship-side component whose mass formula references
        ``ship_class_mass``, ``_handle_add_component`` for the
        ``add_individual`` action must not crash."""
        _ship, target_comp = _attached_ship_and_comp(comp_id, fresh_registries)
        gui = _make_gui_with_target_comp(target_comp)
        router = WorkshopEventRouter(gui)

        # Must not raise. data is (target_comp, target_layer).
        router._handle_add_component(
            "add_individual", (target_comp, LayerType.CORE)
        )

    def test_added_component_has_recalculated_mass_from_design_budget(
        self, fresh_registries
    ):
        """After the fix, the cloned-and-added component evaluates its
        mass formula against the design ship's mass budget. With a 2000t
        budget bridge mass = 50 * sqrt(2000/1000) ~= 70.7t."""
        _ship, target_comp = _attached_ship_and_comp("bridge", fresh_registries)
        gui = _make_gui_with_target_comp(target_comp)
        router = WorkshopEventRouter(gui)

        router._handle_add_component(
            "add_individual", (target_comp, LayerType.CORE)
        )

        # Inspect the component handed to add_component_instance.
        call_args = gui.viewmodel.add_component_instance.call_args
        assert call_args is not None
        added_comp = call_args[0][0]
        expected = 50.0 * (2000.0 / 1000.0) ** 0.5
        assert added_comp.mass == pytest.approx(expected, abs=0.1)
