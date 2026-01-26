"""
Unit tests for WorkshopViewModel class (renamed from BuilderViewModel).

Tests the MVVM ViewModel for the Design Workshop, verifying state management
and event emission without requiring Pygame display.
"""
import pytest
from unittest.mock import MagicMock, patch, call

import pygame

from game.core.registry import RegistryManager
from tests.fixtures.paths import get_project_root, get_data_dir


class MockEventBus:
    """Mock EventBus for testing event emissions."""

    def __init__(self):
        self.emitted_events = []

    def emit(self, event_type, data=None):
        self.emitted_events.append((event_type, data))

    def subscribe(self, event_type, callback):
        pass

    def get_events(self, event_type):
        """Get all emitted events of a specific type."""
        return [e for e in self.emitted_events if e[0] == event_type]

    def clear(self):
        self.emitted_events = []


@pytest.fixture(scope="class")
def workshop_class_setup():
    """Class-level setup for WorkshopViewModel tests."""
    pygame.init()
    # Load data for Ship creation
    from game.simulation.entities.ship_loader import initialize_ship_data
    from game.simulation.components.component import load_components, load_modifiers
    initialize_ship_data(str(get_project_root()))
    data_dir = get_data_dir()
    load_components(str(data_dir / "components.json"))
    load_modifiers(str(data_dir / "modifiers.json"))

    yield

    RegistryManager.instance().clear()
    pygame.quit()


@pytest.fixture
def viewmodel_setup(workshop_class_setup):
    """Set up a fresh viewmodel with mock event bus for each test."""
    event_bus = MockEventBus()
    from game.ui.screens.workshop_viewmodel import WorkshopViewModel
    viewmodel = WorkshopViewModel(event_bus, 1280, 720)

    yield viewmodel, event_bus

    patch.stopall()


class TestWorkshopViewModel:
    """Test WorkshopViewModel state management and event emission."""

    # ─────────────────────────────────────────────────────────────────
    # Ship Property Tests
    # ─────────────────────────────────────────────────────────────────

    def test_ship_property_emits_event(self, viewmodel_setup):
        """Setting ship property emits SHIP_UPDATED event."""
        viewmodel, event_bus = viewmodel_setup
        from game.simulation.entities.ship import Ship

        ship = Ship("Test Ship", 640, 360, (255, 255, 255), ship_class="Escort")
        viewmodel.ship = ship

        events = event_bus.get_events('SHIP_UPDATED')
        assert len(events) == 1
        assert events[0][1] is ship

    def test_notify_ship_changed_recalculates_and_emits(self, viewmodel_setup):
        """notify_ship_changed recalculates stats and emits event."""
        viewmodel, event_bus = viewmodel_setup
        from game.simulation.entities.ship import Ship

        ship = Ship("Test Ship", 640, 360, (255, 255, 255), ship_class="Escort")
        viewmodel._ship = ship  # Set directly to avoid initial event
        event_bus.clear()

        viewmodel.notify_ship_changed()

        events = event_bus.get_events('SHIP_UPDATED')
        assert len(events) == 1

    def test_create_default_ship(self, viewmodel_setup):
        """create_default_ship creates and sets a new ship."""
        viewmodel, event_bus = viewmodel_setup
        ship = viewmodel.create_default_ship("Frigate")

        assert viewmodel.ship is not None
        assert viewmodel.ship.ship_class == "Frigate"
        assert ship is viewmodel.ship

    # ─────────────────────────────────────────────────────────────────
    # Selection Tests
    # ─────────────────────────────────────────────────────────────────

    def test_select_component_single(self, viewmodel_setup):
        """Single selection replaces existing selection."""
        viewmodel, event_bus = viewmodel_setup
        from game.simulation.entities.ship import Ship, LayerType
        from game.simulation.components.component import create_component

        ship = Ship("Test", 640, 360, (255, 255, 255), ship_class="Escort")
        viewmodel._ship = ship

        comp = create_component('armor_plate')
        selection = (LayerType.ARMOR, 0, comp)

        viewmodel.select_component(selection)

        assert len(viewmodel.selected_components) == 1
        assert viewmodel.selected_components[0][2] is comp

    def test_select_component_append(self, viewmodel_setup):
        """Append selection adds to existing selection."""
        viewmodel, event_bus = viewmodel_setup
        from game.simulation.entities.ship import Ship, LayerType
        from game.simulation.components.component import create_component

        ship = Ship("Test", 640, 360, (255, 255, 255), ship_class="Escort")
        viewmodel._ship = ship

        comp1 = create_component('armor_plate')
        comp2 = create_component('armor_plate')

        viewmodel.select_component((LayerType.ARMOR, 0, comp1))
        viewmodel.select_component((LayerType.ARMOR, 1, comp2), append=True)

        assert len(viewmodel.selected_components) == 2

    def test_select_component_toggle(self, viewmodel_setup):
        """Toggle deselects already selected component."""
        viewmodel, event_bus = viewmodel_setup
        from game.simulation.entities.ship import LayerType
        from game.simulation.components.component import create_component

        comp = create_component('armor_plate')
        selection = (LayerType.ARMOR, 0, comp)

        # Select
        viewmodel.select_component(selection)
        assert len(viewmodel.selected_components) == 1

        # Toggle off
        viewmodel.select_component(selection, append=True, toggle=True)
        assert len(viewmodel.selected_components) == 0

    def test_select_component_homogeneity_enforced(self, viewmodel_setup):
        """Selecting different component type replaces selection."""
        viewmodel, event_bus = viewmodel_setup
        from game.simulation.entities.ship import LayerType
        from game.simulation.components.component import create_component

        armor = create_component('armor_plate')
        engine = create_component('standard_engine')

        viewmodel.select_component((LayerType.ARMOR, 0, armor))
        # Trying to append different type should replace
        viewmodel.select_component((LayerType.INNER, 0, engine), append=True)

        assert len(viewmodel.selected_components) == 1
        assert viewmodel.selected_components[0][2] is engine

    def test_select_none_clears_selection(self, viewmodel_setup):
        """Selecting None clears the selection."""
        viewmodel, event_bus = viewmodel_setup
        from game.simulation.entities.ship import LayerType
        from game.simulation.components.component import create_component

        comp = create_component('armor_plate')
        viewmodel.select_component((LayerType.ARMOR, 0, comp))
        assert len(viewmodel.selected_components) == 1

        viewmodel.select_component(None)
        assert len(viewmodel.selected_components) == 0

    def test_primary_selection_returns_last(self, viewmodel_setup):
        """primary_selection returns last selected component."""
        viewmodel, event_bus = viewmodel_setup
        from game.simulation.entities.ship import LayerType
        from game.simulation.components.component import create_component

        comp1 = create_component('armor_plate')
        comp2 = create_component('armor_plate')

        viewmodel.select_component((LayerType.ARMOR, 0, comp1))
        viewmodel.select_component((LayerType.ARMOR, 1, comp2), append=True)

        primary = viewmodel.primary_selection
        assert primary[2] is comp2

    def test_selection_emits_event(self, viewmodel_setup):
        """Selection changes emit SELECTION_CHANGED event."""
        viewmodel, event_bus = viewmodel_setup
        from game.simulation.entities.ship import LayerType
        from game.simulation.components.component import create_component

        event_bus.clear()

        comp = create_component('armor_plate')
        viewmodel.select_component((LayerType.ARMOR, 0, comp))

        events = event_bus.get_events('SELECTION_CHANGED')
        assert len(events) == 1

    # ─────────────────────────────────────────────────────────────────
    # Drag State Tests
    # ─────────────────────────────────────────────────────────────────

    def test_dragged_item_setter_emits_event(self, viewmodel_setup):
        """Setting dragged_item emits DRAG_STATE_CHANGED event."""
        viewmodel, event_bus = viewmodel_setup
        from game.simulation.components.component import create_component

        event_bus.clear()

        comp = create_component('armor_plate')
        viewmodel.dragged_item = comp

        events = event_bus.get_events('DRAG_STATE_CHANGED')
        assert len(events) == 1
        assert events[0][1] is comp

    # ─────────────────────────────────────────────────────────────────
    # Ship Operations Tests
    # ─────────────────────────────────────────────────────────────────

    def test_clear_design_preserves_hull(self, viewmodel_setup):
        """clear_design removes components but preserves hull layer."""
        viewmodel, event_bus = viewmodel_setup
        from game.simulation.entities.ship import Ship, LayerType
        from game.simulation.components.component import create_component

        ship = Ship("Test", 640, 360, (255, 255, 255), ship_class="Escort")
        ship.add_component(create_component('armor_plate'), LayerType.ARMOR)

        # Add engine only if INNER layer exists
        if LayerType.INNER in ship.layers:
            ship.add_component(create_component('standard_engine'), LayerType.INNER)

        viewmodel._ship = ship

        viewmodel.clear_design()

        # Non-hull layers should be empty
        for layer_type, layer_data in ship.layers.items():
            if layer_type != LayerType.HULL:
                assert len(layer_data['components']) == 0, \
                    f"Layer {layer_type.name} should be empty after clear_design"

        # Hull should remain
        if LayerType.HULL in ship.layers:
            assert len(ship.layers[LayerType.HULL]['components']) > 0
