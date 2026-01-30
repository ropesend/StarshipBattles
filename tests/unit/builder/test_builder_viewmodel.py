"""
Unit tests for BuilderViewModel class.

Tests the MVVM ViewModel for the Ship Builder, verifying state management
and event emission without requiring Pygame display.

PROJ-40: Updated to use DI pattern with WorkshopContext.
"""
import pytest
from unittest.mock import MagicMock, patch

import pygame

from game.core.registry import RegistryManager, GameRegistries
from game.ui.screens.workshop_context import WorkshopContext, WorkshopMode
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
def pygame_and_data():
    """Class-level fixture to initialize pygame and load data."""
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
def mock_registries(pygame_and_data):
    """Create GameRegistries for DI testing.

    PROJ-40: Load real data into registries.
    """
    from game.simulation.components.component import load_components_data, load_modifiers_data
    from game.simulation.entities.ship_loader import load_vehicle_classes_data

    return GameRegistries(
        components=load_components_data(),
        modifiers=load_modifiers_data(),
        vehicle_classes=load_vehicle_classes_data(),
        resources={}
    )


@pytest.fixture
def viewmodel_setup(pygame_and_data, mock_registries, fresh_registries):
    """Per-test fixture to create a fresh viewmodel.

    PROJ-40: Updated to use DI with WorkshopContext.
    PROJ-50: Includes fresh_registries for Ship/Component creation.
    """
    event_bus = MockEventBus()
    context = WorkshopContext(
        mode=WorkshopMode.STANDALONE,
        registries=mock_registries
    )
    from game.ui.screens.workshop_viewmodel import WorkshopViewModel as BuilderViewModel
    viewmodel = BuilderViewModel(event_bus, 1280, 720, context=context)

    yield {'event_bus': event_bus, 'viewmodel': viewmodel, 'registries': fresh_registries}

    patch.stopall()


class TestBuilderViewModel:
    """Test BuilderViewModel state management and event emission."""

    # ─────────────────────────────────────────────────────────────────
    # Ship Property Tests
    # ─────────────────────────────────────────────────────────────────

    def test_ship_property_emits_event(self, viewmodel_setup):
        """Setting ship property emits SHIP_UPDATED event."""
        from game.simulation.entities.ship import Ship

        event_bus = viewmodel_setup['event_bus']
        viewmodel = viewmodel_setup['viewmodel']
        registries = viewmodel_setup['registries']

        ship = Ship("Test Ship", 640, 360, (255, 255, 255), ship_class="Escort", registries=registries)
        viewmodel.ship = ship

        events = event_bus.get_events('SHIP_UPDATED')
        assert len(events) == 1
        assert events[0][1] is ship

    def test_notify_ship_changed_recalculates_and_emits(self, viewmodel_setup):
        """notify_ship_changed recalculates stats and emits event."""
        from game.simulation.entities.ship import Ship

        event_bus = viewmodel_setup['event_bus']
        viewmodel = viewmodel_setup['viewmodel']
        registries = viewmodel_setup['registries']

        ship = Ship("Test Ship", 640, 360, (255, 255, 255), ship_class="Escort", registries=registries)
        viewmodel._ship = ship  # Set directly to avoid initial event
        event_bus.clear()

        viewmodel.notify_ship_changed()

        events = event_bus.get_events('SHIP_UPDATED')
        assert len(events) == 1

    def test_create_default_ship(self, viewmodel_setup):
        """create_default_ship creates and sets a new ship."""
        viewmodel = viewmodel_setup['viewmodel']

        ship = viewmodel.create_default_ship("Frigate")

        assert viewmodel.ship is not None
        assert viewmodel.ship.ship_class == "Frigate"
        assert ship is viewmodel.ship

    # ─────────────────────────────────────────────────────────────────
    # Selection Tests
    # ─────────────────────────────────────────────────────────────────

    def test_select_component_single(self, viewmodel_setup):
        """Single selection replaces existing selection."""
        from game.simulation.entities.ship import Ship, LayerType
        from game.simulation.components.component import create_component

        viewmodel = viewmodel_setup['viewmodel']
        registries = viewmodel_setup['registries']

        ship = Ship("Test", 640, 360, (255, 255, 255), ship_class="Escort", registries=registries)
        viewmodel._ship = ship

        comp = create_component('armor_plate', registries=registries)
        selection = (LayerType.ARMOR, 0, comp)

        viewmodel.select_component(selection)

        assert len(viewmodel.selected_components) == 1
        assert viewmodel.selected_components[0][2] is comp

    def test_select_component_append(self, viewmodel_setup):
        """Append selection adds to existing selection."""
        from game.simulation.entities.ship import Ship, LayerType
        from game.simulation.components.component import create_component

        viewmodel = viewmodel_setup['viewmodel']
        registries = viewmodel_setup['registries']

        ship = Ship("Test", 640, 360, (255, 255, 255), ship_class="Escort", registries=registries)
        viewmodel._ship = ship

        comp1 = create_component('armor_plate', registries=registries)
        comp2 = create_component('armor_plate', registries=registries)

        viewmodel.select_component((LayerType.ARMOR, 0, comp1))
        viewmodel.select_component((LayerType.ARMOR, 1, comp2), append=True)

        assert len(viewmodel.selected_components) == 2

    def test_select_component_toggle(self, viewmodel_setup):
        """Toggle deselects already selected component."""
        from game.simulation.entities.ship import LayerType
        from game.simulation.components.component import create_component

        viewmodel = viewmodel_setup['viewmodel']
        registries = viewmodel_setup['registries']

        comp = create_component('armor_plate', registries=registries)
        selection = (LayerType.ARMOR, 0, comp)

        # Select
        viewmodel.select_component(selection)
        assert len(viewmodel.selected_components) == 1

        # Toggle off
        viewmodel.select_component(selection, append=True, toggle=True)
        assert len(viewmodel.selected_components) == 0

    def test_select_component_homogeneity_enforced(self, viewmodel_setup):
        """Selecting different component type replaces selection."""
        from game.simulation.entities.ship import LayerType
        from game.simulation.components.component import create_component

        viewmodel = viewmodel_setup['viewmodel']
        registries = viewmodel_setup['registries']

        armor = create_component('armor_plate', registries=registries)
        engine = create_component('standard_engine', registries=registries)

        viewmodel.select_component((LayerType.ARMOR, 0, armor))
        # Trying to append different type should replace
        viewmodel.select_component((LayerType.INNER, 0, engine), append=True)

        assert len(viewmodel.selected_components) == 1
        assert viewmodel.selected_components[0][2] is engine

    def test_select_none_clears_selection(self, viewmodel_setup):
        """Selecting None clears the selection."""
        from game.simulation.entities.ship import LayerType
        from game.simulation.components.component import create_component

        viewmodel = viewmodel_setup['viewmodel']
        registries = viewmodel_setup['registries']

        comp = create_component('armor_plate', registries=registries)
        viewmodel.select_component((LayerType.ARMOR, 0, comp))
        assert len(viewmodel.selected_components) == 1

        viewmodel.select_component(None)
        assert len(viewmodel.selected_components) == 0

    def test_primary_selection_returns_last(self, viewmodel_setup):
        """primary_selection returns last selected component."""
        from game.simulation.entities.ship import LayerType
        from game.simulation.components.component import create_component

        viewmodel = viewmodel_setup['viewmodel']
        registries = viewmodel_setup['registries']

        comp1 = create_component('armor_plate', registries=registries)
        comp2 = create_component('armor_plate', registries=registries)

        viewmodel.select_component((LayerType.ARMOR, 0, comp1))
        viewmodel.select_component((LayerType.ARMOR, 1, comp2), append=True)

        primary = viewmodel.primary_selection
        assert primary[2] is comp2

    def test_selection_emits_event(self, viewmodel_setup):
        """Selection changes emit SELECTION_CHANGED event."""
        from game.simulation.entities.ship import LayerType
        from game.simulation.components.component import create_component

        event_bus = viewmodel_setup['event_bus']
        viewmodel = viewmodel_setup['viewmodel']
        registries = viewmodel_setup['registries']

        event_bus.clear()

        comp = create_component('armor_plate', registries=registries)
        viewmodel.select_component((LayerType.ARMOR, 0, comp))

        events = event_bus.get_events('SELECTION_CHANGED')
        assert len(events) == 1

    # ─────────────────────────────────────────────────────────────────
    # Drag State Tests
    # ─────────────────────────────────────────────────────────────────

    def test_dragged_item_setter_emits_event(self, viewmodel_setup):
        """Setting dragged_item emits DRAG_STATE_CHANGED event."""
        from game.simulation.components.component import create_component

        event_bus = viewmodel_setup['event_bus']
        viewmodel = viewmodel_setup['viewmodel']
        registries = viewmodel_setup['registries']

        event_bus.clear()

        comp = create_component('armor_plate', registries=registries)
        viewmodel.dragged_item = comp

        events = event_bus.get_events('DRAG_STATE_CHANGED')
        assert len(events) == 1
        assert events[0][1] is comp

    # ─────────────────────────────────────────────────────────────────
    # Ship Operations Tests
    # ─────────────────────────────────────────────────────────────────

    def test_clear_design_preserves_hull(self, viewmodel_setup):
        """clear_design removes components but preserves hull layer."""
        from game.simulation.entities.ship import Ship, LayerType
        from game.simulation.components.component import create_component

        viewmodel = viewmodel_setup['viewmodel']
        registries = viewmodel_setup['registries']

        ship = Ship("Test", 640, 360, (255, 255, 255), ship_class="Escort", registries=registries)
        ship.add_component(create_component('armor_plate', registries=registries), LayerType.ARMOR)

        # Add engine only if INNER layer exists
        if LayerType.INNER in ship.layers:
            ship.add_component(create_component('standard_engine', registries=registries), LayerType.INNER)

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

    # ─────────────────────────────────────────────────────────────────
    # Ship Property Mutation Tests (PROJ-33: UI-01 Remediation)
    # ─────────────────────────────────────────────────────────────────

    def test_set_ship_name_updates_and_emits(self, viewmodel_setup):
        """set_ship_name updates ship name and emits SHIP_UPDATED event."""
        from game.simulation.entities.ship import Ship

        event_bus = viewmodel_setup['event_bus']
        viewmodel = viewmodel_setup['viewmodel']
        registries = viewmodel_setup['registries']

        ship = Ship("Original Name", 640, 360, (255, 255, 255), ship_class="Escort", registries=registries)
        viewmodel._ship = ship
        event_bus.clear()

        viewmodel.set_ship_name("New Ship Name")

        assert ship.name == "New Ship Name"
        events = event_bus.get_events('SHIP_UPDATED')
        assert len(events) == 1

    def test_set_ship_name_no_change_if_same(self, viewmodel_setup):
        """set_ship_name should not emit if name unchanged."""
        from game.simulation.entities.ship import Ship

        event_bus = viewmodel_setup['event_bus']
        viewmodel = viewmodel_setup['viewmodel']
        registries = viewmodel_setup['registries']

        ship = Ship("Same Name", 640, 360, (255, 255, 255), ship_class="Escort", registries=registries)
        viewmodel._ship = ship
        event_bus.clear()

        viewmodel.set_ship_name("Same Name")

        # Should not emit if name is the same
        events = event_bus.get_events('SHIP_UPDATED')
        assert len(events) == 0

    def test_set_ship_theme_updates_and_emits(self, viewmodel_setup):
        """set_ship_theme updates ship theme_id and emits SHIP_UPDATED event."""
        from game.simulation.entities.ship import Ship

        event_bus = viewmodel_setup['event_bus']
        viewmodel = viewmodel_setup['viewmodel']
        registries = viewmodel_setup['registries']

        ship = Ship("Test Ship", 640, 360, (255, 255, 255), ship_class="Escort", registries=registries)
        viewmodel._ship = ship
        event_bus.clear()

        viewmodel.set_ship_theme("Klingon")

        assert ship.theme_id == "Klingon"
        events = event_bus.get_events('SHIP_UPDATED')
        assert len(events) == 1

    def test_set_ship_theme_no_change_if_same(self, viewmodel_setup):
        """set_ship_theme should not emit if theme unchanged."""
        from game.simulation.entities.ship import Ship

        event_bus = viewmodel_setup['event_bus']
        viewmodel = viewmodel_setup['viewmodel']
        registries = viewmodel_setup['registries']

        ship = Ship("Test Ship", 640, 360, (255, 255, 255), ship_class="Escort", theme_id="Federation", registries=registries)
        viewmodel._ship = ship
        event_bus.clear()

        viewmodel.set_ship_theme("Federation")

        # Should not emit if theme is the same
        events = event_bus.get_events('SHIP_UPDATED')
        assert len(events) == 0

    def test_set_ship_ai_strategy_updates_and_emits(self, viewmodel_setup):
        """set_ship_ai_strategy updates ship ai_strategy and emits SHIP_UPDATED event."""
        from game.simulation.entities.ship import Ship

        event_bus = viewmodel_setup['event_bus']
        viewmodel = viewmodel_setup['viewmodel']
        registries = viewmodel_setup['registries']

        ship = Ship("Test Ship", 640, 360, (255, 255, 255), ship_class="Escort", registries=registries)
        ship.ai_strategy = "standard_ranged"  # Set initial value
        viewmodel._ship = ship
        event_bus.clear()

        viewmodel.set_ship_ai_strategy("aggressive_close")

        assert ship.ai_strategy == "aggressive_close"
        events = event_bus.get_events('SHIP_UPDATED')
        assert len(events) == 1

    def test_set_ship_ai_strategy_no_change_if_same(self, viewmodel_setup):
        """set_ship_ai_strategy should not emit if strategy unchanged."""
        from game.simulation.entities.ship import Ship

        event_bus = viewmodel_setup['event_bus']
        registries = viewmodel_setup['registries']
        viewmodel = viewmodel_setup['viewmodel']

        ship = Ship("Test Ship", 640, 360, (255, 255, 255), ship_class="Escort", registries=registries)
        ship.ai_strategy = "standard_ranged"
        viewmodel._ship = ship
        event_bus.clear()

        viewmodel.set_ship_ai_strategy("standard_ranged")

        # Should not emit if strategy is the same
        events = event_bus.get_events('SHIP_UPDATED')
        assert len(events) == 0
