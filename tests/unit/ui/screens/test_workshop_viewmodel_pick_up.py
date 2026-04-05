"""TDD tests for WorkshopViewModel.pick_up_component (Fix 1).

The bug: InteractionController called ship.remove_component() directly (line 94
of interaction_controller.py), bypassing the ViewModel and VehicleDesignService.
This skips validation logic and breaks the MVVM contract.

The fix: WorkshopViewModel gains pick_up_component(layer, index) which:
  1. Delegates to VehicleDesignService.remove_component() (validated removal)
  2. Emits SHIP_UPDATED via notify_ship_changed()
  3. Clears selection and emits SELECTION_CHANGED
  4. Returns the removed component for the caller to use as dragged_item
"""
import pytest
from unittest.mock import MagicMock, patch, call

from game.core.constants import LayerType
from game.simulation.services.vehicle_design_service import DesignResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_registries():
    reg = MagicMock()
    reg.vehicle_classes = {'Escort': {'type': 'Ship', 'max_mass': 100}}
    reg.components = {}
    reg.modifiers = {}
    reg.resources = MagicMock()
    return reg


def _make_context(registries=None):
    if registries is None:
        registries = _make_registries()
    ctx = MagicMock()
    ctx.registries = registries
    return ctx


def _make_viewmodel(context=None):
    """Create a WorkshopViewModel with all heavy deps mocked out."""
    from game.ui.screens.workshop_viewmodel import WorkshopViewModel

    ctx = context or _make_context()
    event_bus = MagicMock()

    with patch(
        'game.ui.screens.workshop_viewmodel.VehicleDesignService'
    ) as MockService:
        vm = WorkshopViewModel(event_bus, 1920, 1080, context=ctx)

    # Expose the mock service instance for assertion
    vm._mock_service = vm._ship_service
    return vm


# ---------------------------------------------------------------------------
# Tests: pick_up_component exists and has correct contract
# ---------------------------------------------------------------------------

class TestPickUpComponentExists:
    def test_method_exists_on_viewmodel(self):
        """WorkshopViewModel must expose a pick_up_component method."""
        from game.ui.screens.workshop_viewmodel import WorkshopViewModel
        assert hasattr(WorkshopViewModel, 'pick_up_component'), (
            "WorkshopViewModel must define pick_up_component(layer, index)"
        )

    def test_method_is_callable(self):
        """pick_up_component must be callable."""
        from game.ui.screens.workshop_viewmodel import WorkshopViewModel
        assert callable(getattr(WorkshopViewModel, 'pick_up_component', None))


# ---------------------------------------------------------------------------
# Tests: pick_up_component behaviour
# ---------------------------------------------------------------------------

class TestPickUpComponentBehaviour:

    def _make_vm_with_ship(self):
        """Return a ViewModel whose _ship_service is a controlled mock."""
        from game.ui.screens.workshop_viewmodel import WorkshopViewModel

        ctx = _make_context()
        event_bus = MagicMock()

        with patch('game.ui.screens.workshop_viewmodel.VehicleDesignService') as MockServiceClass:
            vm = WorkshopViewModel(event_bus, 1920, 1080, context=ctx)

        # Give the vm a fake ship
        fake_ship = MagicMock()
        fake_ship.name = "TestShip"
        vm._ship = fake_ship

        return vm

    def test_delegates_to_service_remove_component(self):
        """pick_up_component must call the service, not ship.remove_component."""
        vm = self._make_vm_with_ship()
        fake_comp = MagicMock()
        fake_comp.id = "laser"

        success_result = DesignResult(success=True, removed_component=fake_comp)
        vm._ship_service.remove_component.return_value = success_result

        vm.pick_up_component(LayerType.OUTER, 0)

        # Service must have been called with the ship + layer + index
        vm._ship_service.remove_component.assert_called_once_with(
            vm._ship, LayerType.OUTER, 0
        )

    def test_does_not_call_ship_remove_component_directly(self):
        """pick_up_component must NOT bypass the service."""
        vm = self._make_vm_with_ship()
        fake_comp = MagicMock()
        success_result = DesignResult(success=True, removed_component=fake_comp)
        vm._ship_service.remove_component.return_value = success_result

        vm.pick_up_component(LayerType.OUTER, 0)

        # ship.remove_component must NOT have been called directly
        vm._ship.remove_component.assert_not_called()

    def test_emits_ship_updated_on_success(self):
        """pick_up_component must emit SHIP_UPDATED after successful removal."""
        from game.ui.screens.builder_utils import BuilderEvents

        vm = self._make_vm_with_ship()
        fake_comp = MagicMock()
        success_result = DesignResult(success=True, removed_component=fake_comp)
        vm._ship_service.remove_component.return_value = success_result

        vm.pick_up_component(LayerType.OUTER, 0)

        # event_bus.emit should have been called for SHIP_UPDATED
        emitted_events = [c.args[0] for c in vm.event_bus.emit.call_args_list]
        assert BuilderEvents.SHIP_UPDATED in emitted_events

    def test_returns_removed_component_on_success(self):
        """pick_up_component must return the removed component so caller can drag it."""
        vm = self._make_vm_with_ship()
        fake_comp = MagicMock()
        fake_comp.id = "laser"
        success_result = DesignResult(success=True, removed_component=fake_comp)
        vm._ship_service.remove_component.return_value = success_result

        result = vm.pick_up_component(LayerType.OUTER, 0)

        assert result is fake_comp

    def test_returns_none_on_failure(self):
        """pick_up_component returns None when service reports failure."""
        vm = self._make_vm_with_ship()
        failure_result = DesignResult(success=False, errors=["not found"])
        vm._ship_service.remove_component.return_value = failure_result

        result = vm.pick_up_component(LayerType.OUTER, 99)

        assert result is None

    def test_returns_none_when_no_ship(self):
        """pick_up_component returns None (gracefully) when no ship is loaded."""
        vm = self._make_vm_with_ship()
        vm._ship = None

        result = vm.pick_up_component(LayerType.OUTER, 0)

        assert result is None
        vm._ship_service.remove_component.assert_not_called()

    def test_clears_selection_on_success(self):
        """pick_up_component clears the selection after removing the component."""
        from game.ui.screens.builder_utils import BuilderEvents

        vm = self._make_vm_with_ship()
        fake_comp = MagicMock()
        # Pre-populate selection
        vm._selected_components = [(LayerType.OUTER, 0, fake_comp)]

        success_result = DesignResult(success=True, removed_component=fake_comp)
        vm._ship_service.remove_component.return_value = success_result

        vm.pick_up_component(LayerType.OUTER, 0)

        assert vm._selected_components == []
        emitted_events = [c.args[0] for c in vm.event_bus.emit.call_args_list]
        assert BuilderEvents.SELECTION_CHANGED in emitted_events


