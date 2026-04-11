"""
Unit tests for WorkshopViewModel class (renamed from BuilderViewModel).

Tests the MVVM ViewModel for the Design Workshop, verifying state management
and event emission without requiring Pygame display.

PROJ-40: Updated to use DI pattern with WorkshopContext instead of global fallbacks.
"""
import pytest
from unittest.mock import MagicMock, patch, call

import pygame

from game.core.registry import GameRegistries, get_default_registry_provider
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
def workshop_class_setup():
    """Class-level setup for WorkshopViewModel tests."""
    pygame.init()
    # Load data for Ship creation
    from game.simulation.entities.ship_loader import initialize_ship_data
    from game.simulation.components.component import load_components, load_modifiers
    # PROJ-211: Pass registry_provider explicitly
    provider = get_default_registry_provider()
    initialize_ship_data(str(get_project_root()), registry_provider=provider)
    data_dir = get_data_dir()
    load_components(str(data_dir / "components.json"), registry_provider=provider)
    load_modifiers(str(data_dir / "modifiers.json"), registry_provider=provider)

    yield

    pygame.quit()


@pytest.fixture
def mock_registries(workshop_class_setup):
    """Create GameRegistries for DI testing.

    PROJ-40: Load real data into registries for proper testing.
    """
    from game.simulation.components.component import load_components_data, load_modifiers_data
    from game.simulation.entities.ship_loader import load_vehicle_classes_data

    # PROJ-211: Only load_components_data needs registries
    minimal_registries = GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={})
    return GameRegistries(
        components=load_components_data(registries=minimal_registries),
        modifiers=load_modifiers_data(),
        vehicle_classes=load_vehicle_classes_data(),
        resources={}
    )


@pytest.fixture
def viewmodel_setup(workshop_class_setup, mock_registries):
    """Set up a fresh viewmodel with mock event bus for each test.

    PROJ-40: Updated to use DI with WorkshopContext instead of global fallbacks.
    """
    event_bus = MockEventBus()
    context = WorkshopContext(
        mode=WorkshopMode.STANDALONE,
        registries=mock_registries
    )
    from game.ui.screens.workshop_viewmodel import WorkshopViewModel
    viewmodel = WorkshopViewModel(event_bus, 1280, 720, context=context)

    yield viewmodel, event_bus

    patch.stopall()


class TestWorkshopViewModel:
    """Test WorkshopViewModel state management and event emission."""

    # ─────────────────────────────────────────────────────────────────
    # Ship Property Tests
    # ─────────────────────────────────────────────────────────────────

    def test_ship_property_emits_event(self, viewmodel_setup, mock_registries):
        """Setting ship property emits SHIP_UPDATED event."""
        viewmodel, event_bus = viewmodel_setup
        from game.simulation.entities.ship import Ship

        # PROJ-50: Ship requires registries parameter
        ship = Ship("Test Ship", 640, 360, (255, 255, 255), ship_class="Escort", registries=mock_registries)
        viewmodel.ship = ship

        events = event_bus.get_events('SHIP_UPDATED')
        assert len(events) == 1
        assert events[0][1] is ship

    def test_notify_ship_changed_recalculates_and_emits(self, viewmodel_setup, mock_registries):
        """notify_ship_changed recalculates stats and emits event."""
        viewmodel, event_bus = viewmodel_setup
        from game.simulation.entities.ship import Ship

        # PROJ-50: Ship requires registries parameter
        ship = Ship("Test Ship", 640, 360, (255, 255, 255), ship_class="Escort", registries=mock_registries)
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

    def test_select_component_single(self, viewmodel_setup, mock_registries):
        """Single selection replaces existing selection."""
        viewmodel, event_bus = viewmodel_setup
        from game.simulation.entities.ship import Ship, LayerType
        from game.simulation.components.component import create_component

        # PROJ-50: Ship and create_component require registries
        ship = Ship("Test", 640, 360, (255, 255, 255), ship_class="Escort", registries=mock_registries)
        viewmodel._ship = ship

        comp = create_component('armor_plate', registries=mock_registries)
        selection = (LayerType.ARMOR, 0, comp)

        viewmodel.select_component(selection)

        assert len(viewmodel.selected_components) == 1
        assert viewmodel.selected_components[0][2] is comp

    def test_select_component_append(self, viewmodel_setup, mock_registries):
        """Append selection adds to existing selection."""
        viewmodel, event_bus = viewmodel_setup
        from game.simulation.entities.ship import Ship, LayerType
        from game.simulation.components.component import create_component

        # PROJ-50: Ship and create_component require registries
        ship = Ship("Test", 640, 360, (255, 255, 255), ship_class="Escort", registries=mock_registries)
        viewmodel._ship = ship

        comp1 = create_component('armor_plate', registries=mock_registries)
        comp2 = create_component('armor_plate', registries=mock_registries)

        viewmodel.select_component((LayerType.ARMOR, 0, comp1))
        viewmodel.select_component((LayerType.ARMOR, 1, comp2), append=True)

        assert len(viewmodel.selected_components) == 2

    def test_select_component_toggle(self, viewmodel_setup, mock_registries):
        """Toggle deselects already selected component."""
        viewmodel, event_bus = viewmodel_setup
        from game.simulation.entities.ship import LayerType
        from game.simulation.components.component import create_component

        # PROJ-50: create_component requires registries
        comp = create_component('armor_plate', registries=mock_registries)
        selection = (LayerType.ARMOR, 0, comp)

        # Select
        viewmodel.select_component(selection)
        assert len(viewmodel.selected_components) == 1

        # Toggle off
        viewmodel.select_component(selection, append=True, toggle=True)
        assert len(viewmodel.selected_components) == 0

    def test_select_component_homogeneity_enforced(self, viewmodel_setup, mock_registries):
        """Selecting different component type replaces selection."""
        viewmodel, event_bus = viewmodel_setup
        from game.simulation.entities.ship import LayerType
        from game.simulation.components.component import create_component

        # PROJ-50: create_component requires registries
        armor = create_component('armor_plate', registries=mock_registries)
        engine = create_component('standard_engine', registries=mock_registries)

        viewmodel.select_component((LayerType.ARMOR, 0, armor))
        # Trying to append different type should replace
        viewmodel.select_component((LayerType.INNER, 0, engine), append=True)

        assert len(viewmodel.selected_components) == 1
        assert viewmodel.selected_components[0][2] is engine

    def test_select_none_clears_selection(self, viewmodel_setup, mock_registries):
        """Selecting None clears the selection."""
        viewmodel, event_bus = viewmodel_setup
        from game.simulation.entities.ship import LayerType
        from game.simulation.components.component import create_component

        # PROJ-50: create_component requires registries
        comp = create_component('armor_plate', registries=mock_registries)
        viewmodel.select_component((LayerType.ARMOR, 0, comp))
        assert len(viewmodel.selected_components) == 1

        viewmodel.select_component(None)
        assert len(viewmodel.selected_components) == 0

    def test_primary_selection_returns_last(self, viewmodel_setup, mock_registries):
        """primary_selection returns last selected component."""
        viewmodel, event_bus = viewmodel_setup
        from game.simulation.entities.ship import LayerType
        from game.simulation.components.component import create_component

        # PROJ-50: create_component requires registries
        comp1 = create_component('armor_plate', registries=mock_registries)
        comp2 = create_component('armor_plate', registries=mock_registries)

        viewmodel.select_component((LayerType.ARMOR, 0, comp1))
        viewmodel.select_component((LayerType.ARMOR, 1, comp2), append=True)

        primary = viewmodel.primary_selection
        assert primary[2] is comp2

    def test_selection_emits_event(self, viewmodel_setup, mock_registries):
        """Selection changes emit SELECTION_CHANGED event."""
        viewmodel, event_bus = viewmodel_setup
        from game.simulation.entities.ship import LayerType
        from game.simulation.components.component import create_component

        event_bus.clear()

        # PROJ-50: create_component requires registries
        comp = create_component('armor_plate', registries=mock_registries)
        viewmodel.select_component((LayerType.ARMOR, 0, comp))

        events = event_bus.get_events('SELECTION_CHANGED')
        assert len(events) == 1

    # ─────────────────────────────────────────────────────────────────
    # Drag State Tests
    # ─────────────────────────────────────────────────────────────────

    def test_dragged_item_setter_emits_event(self, viewmodel_setup, mock_registries):
        """Setting dragged_item emits DRAG_STATE_CHANGED event."""
        viewmodel, event_bus = viewmodel_setup
        from game.simulation.components.component import create_component

        event_bus.clear()

        # PROJ-50: create_component requires registries
        comp = create_component('armor_plate', registries=mock_registries)
        viewmodel.dragged_item = comp

        events = event_bus.get_events('DRAG_STATE_CHANGED')
        assert len(events) == 1
        assert events[0][1] is comp

    # ─────────────────────────────────────────────────────────────────
    # Ship Operations Tests
    # ─────────────────────────────────────────────────────────────────

    def test_clear_design_preserves_hull(self, viewmodel_setup, mock_registries):
        """clear_design removes components but preserves hull layer."""
        viewmodel, event_bus = viewmodel_setup
        from game.simulation.entities.ship import Ship, LayerType
        from game.simulation.components.component import create_component

        # PROJ-50: Ship and create_component require registries
        ship = Ship("Test", 640, 360, (255, 255, 255), ship_class="Escort", registries=mock_registries)
        ship.add_component(create_component('armor_plate', registries=mock_registries), LayerType.ARMOR)

        # Add engine only if INNER layer exists
        if LayerType.INNER in ship.layers:
            ship.add_component(create_component('standard_engine', registries=mock_registries), LayerType.INNER)

        viewmodel._ship = ship

        viewmodel.clear_design()

        # Non-hull layers should be empty
        for layer_type, layer_data in ship.layers.items():
            if layer_type != LayerType.HULL:
                assert len(layer_data.components) == 0, \
                    f"Layer {layer_type.name} should be empty after clear_design"

        # Hull should remain
        if LayerType.HULL in ship.layers:
            assert len(ship.layers[LayerType.HULL].components) > 0

    # ─────────────────────────────────────────────────────────────────
    # Remove Component Tests (pick-up-through-viewmodel pattern)
    # ─────────────────────────────────────────────────────────────────

    def test_remove_component_returns_removed(self, viewmodel_setup, mock_registries):
        """remove_component returns the removed component on success."""
        viewmodel, event_bus = viewmodel_setup
        from game.simulation.entities.ship import Ship, LayerType
        from game.simulation.components.component import create_component

        ship = Ship("Test", 640, 360, (255, 255, 255), ship_class="Escort", registries=mock_registries)
        comp = create_component('armor_plate', registries=mock_registries)
        ship.add_component(comp, LayerType.ARMOR)
        viewmodel._ship = ship
        event_bus.clear()

        removed = viewmodel.remove_component(LayerType.ARMOR, 0)

        assert removed is not None
        assert removed is comp

    def test_remove_component_emits_ship_updated(self, viewmodel_setup, mock_registries):
        """remove_component emits SHIP_UPDATED event on success."""
        viewmodel, event_bus = viewmodel_setup
        from game.simulation.entities.ship import Ship, LayerType
        from game.simulation.components.component import create_component

        ship = Ship("Test", 640, 360, (255, 255, 255), ship_class="Escort", registries=mock_registries)
        comp = create_component('armor_plate', registries=mock_registries)
        ship.add_component(comp, LayerType.ARMOR)
        viewmodel._ship = ship
        event_bus.clear()

        viewmodel.remove_component(LayerType.ARMOR, 0)

        events = event_bus.get_events('SHIP_UPDATED')
        assert len(events) >= 1, "remove_component should emit SHIP_UPDATED"

    def test_remove_component_no_ship_returns_none(self, viewmodel_setup):
        """remove_component returns None when no ship is set."""
        viewmodel, event_bus = viewmodel_setup
        viewmodel._ship = None

        removed = viewmodel.remove_component(None, 0)

        assert removed is None

    # ─────────────────────────────────────────────────────────────────
    # Ship Property Mutation Tests (migrated from test_builder_viewmodel.py)
    # ─────────────────────────────────────────────────────────────────

    def test_set_ship_name_updates_and_emits(self, viewmodel_setup, mock_registries):
        """set_ship_name updates ship name and emits SHIP_UPDATED event."""
        from game.simulation.entities.ship import Ship
        viewmodel, event_bus = viewmodel_setup

        ship = Ship("Original Name", 640, 360, (255, 255, 255), ship_class="Escort", registries=mock_registries)
        viewmodel._ship = ship
        event_bus.clear()

        viewmodel.set_ship_name("New Ship Name")

        assert ship.name == "New Ship Name"
        events = event_bus.get_events('SHIP_UPDATED')
        assert len(events) == 1

    def test_set_ship_name_no_change_if_same(self, viewmodel_setup, mock_registries):
        """set_ship_name should not emit if name unchanged."""
        from game.simulation.entities.ship import Ship
        viewmodel, event_bus = viewmodel_setup

        ship = Ship("Same Name", 640, 360, (255, 255, 255), ship_class="Escort", registries=mock_registries)
        viewmodel._ship = ship
        event_bus.clear()

        viewmodel.set_ship_name("Same Name")

        events = event_bus.get_events('SHIP_UPDATED')
        assert len(events) == 0

    def test_set_ship_theme_updates_and_emits(self, viewmodel_setup, mock_registries):
        """set_ship_theme updates ship theme_id and emits SHIP_UPDATED event."""
        from game.simulation.entities.ship import Ship
        viewmodel, event_bus = viewmodel_setup

        ship = Ship("Test Ship", 640, 360, (255, 255, 255), ship_class="Escort", registries=mock_registries)
        viewmodel._ship = ship
        event_bus.clear()

        viewmodel.set_ship_theme("Klingon")

        assert ship.theme_id == "Klingon"
        events = event_bus.get_events('SHIP_UPDATED')
        assert len(events) == 1

    def test_set_ship_theme_no_change_if_same(self, viewmodel_setup, mock_registries):
        """set_ship_theme should not emit if theme unchanged."""
        from game.simulation.entities.ship import Ship
        viewmodel, event_bus = viewmodel_setup

        ship = Ship("Test Ship", 640, 360, (255, 255, 255), ship_class="Escort", theme_id="Federation", registries=mock_registries)
        viewmodel._ship = ship
        event_bus.clear()

        viewmodel.set_ship_theme("Federation")

        events = event_bus.get_events('SHIP_UPDATED')
        assert len(events) == 0

    def test_set_ship_ai_strategy_updates_and_emits(self, viewmodel_setup, mock_registries):
        """set_ship_ai_strategy updates ship ai_strategy and emits SHIP_UPDATED event."""
        from game.simulation.entities.ship import Ship
        viewmodel, event_bus = viewmodel_setup

        ship = Ship("Test Ship", 640, 360, (255, 255, 255), ship_class="Escort", registries=mock_registries)
        ship.ai_strategy = "standard_ranged"
        viewmodel._ship = ship
        event_bus.clear()

        viewmodel.set_ship_ai_strategy("aggressive_close")

        assert ship.ai_strategy == "aggressive_close"
        events = event_bus.get_events('SHIP_UPDATED')
        assert len(events) == 1

    def test_set_ship_ai_strategy_no_change_if_same(self, viewmodel_setup, mock_registries):
        """set_ship_ai_strategy should not emit if strategy unchanged."""
        from game.simulation.entities.ship import Ship
        viewmodel, event_bus = viewmodel_setup

        ship = Ship("Test Ship", 640, 360, (255, 255, 255), ship_class="Escort", registries=mock_registries)
        ship.ai_strategy = "standard_ranged"
        viewmodel._ship = ship
        event_bus.clear()

        viewmodel.set_ship_ai_strategy("standard_ranged")

        events = event_bus.get_events('SHIP_UPDATED')
        assert len(events) == 0

    # ─────────────────────────────────────────────────────────────────
    # on_modifier_changed Tests
    # ─────────────────────────────────────────────────────────────────

    def test_on_modifier_changed_single_selection_emits_ship_updated(self, viewmodel_setup, mock_registries):
        """Single component modifier change emits SHIP_UPDATED."""
        from game.simulation.entities.ship import Ship, LayerType
        from game.simulation.components.component import create_component

        viewmodel, event_bus = viewmodel_setup
        ship = Ship("Test", 640, 360, (255, 255, 255), ship_class="Escort", registries=mock_registries)
        viewmodel._ship = ship

        comp = create_component('armor_plate', registries=mock_registries)
        ship.add_component(comp, LayerType.ARMOR)
        ship.recalculate_stats()

        viewmodel.select_component((LayerType.ARMOR, 0, comp))
        event_bus.clear()

        # Simulate modifier change (modifier panel sets value then calls this)
        comp.add_modifier('hardened')
        comp.recalculate_stats()
        viewmodel.on_modifier_changed()

        events = event_bus.get_events('SHIP_UPDATED')
        assert len(events) >= 1, "on_modifier_changed must emit SHIP_UPDATED for single selection"

    def test_on_modifier_changed_multi_selection_syncs_and_emits(self, viewmodel_setup, mock_registries):
        """Multi-selection modifier change syncs modifiers and emits SHIP_UPDATED."""
        from game.simulation.entities.ship import Ship, LayerType
        from game.simulation.components.component import create_component

        viewmodel, event_bus = viewmodel_setup
        ship = Ship("Test", 640, 360, (255, 255, 255), ship_class="Escort", registries=mock_registries)
        viewmodel._ship = ship

        comp1 = create_component('armor_plate', registries=mock_registries)
        comp2 = create_component('armor_plate', registries=mock_registries)
        ship.add_component(comp1, LayerType.ARMOR)
        ship.add_component(comp2, LayerType.ARMOR)
        ship.recalculate_stats()

        viewmodel.select_component((LayerType.ARMOR, 0, comp1))
        viewmodel.select_component((LayerType.ARMOR, 1, comp2), append=True)

        # Modify primary selection's modifier
        comp2.add_modifier('hardened')
        comp2.recalculate_stats()
        event_bus.clear()

        viewmodel.on_modifier_changed()

        # Should sync modifier to comp1
        assert len(comp1.modifier_manager.modifiers) > 0, "Modifier should sync to other selected components"
        events = event_bus.get_events('SHIP_UPDATED')
        assert len(events) >= 1, "on_modifier_changed must emit SHIP_UPDATED for multi-selection"

    def test_on_modifier_changed_no_selection_is_noop(self, viewmodel_setup, mock_registries):
        """No selection: on_modifier_changed is a safe no-op."""
        from game.simulation.entities.ship import Ship

        viewmodel, event_bus = viewmodel_setup
        ship = Ship("Test", 640, 360, (255, 255, 255), ship_class="Escort", registries=mock_registries)
        viewmodel._ship = ship
        viewmodel._selected_components = []
        event_bus.clear()

        viewmodel.on_modifier_changed()

        events = event_bus.get_events('SHIP_UPDATED')
        assert len(events) == 0, "No events should be emitted with no selection"

    def test_on_modifier_changed_no_ship_is_safe(self, viewmodel_setup):
        """No ship loaded: on_modifier_changed does not crash."""
        viewmodel, event_bus = viewmodel_setup
        viewmodel._ship = None
        viewmodel._selected_components = []

        viewmodel.on_modifier_changed()  # Should not raise
