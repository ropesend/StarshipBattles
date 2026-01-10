"""
Unit tests for BuilderViewModel class.

Tests the MVVM ViewModel for the Ship Builder, verifying state management
and event emission without requiring Pygame display.
"""
import unittest
from unittest.mock import MagicMock, patch, call
import os

import pygame

from game.core.registry import RegistryManager


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


class TestBuilderViewModel(unittest.TestCase):
    """Test BuilderViewModel state management and event emission."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
        # Load data for Ship creation
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from game.simulation.entities.ship import initialize_ship_data
        from game.simulation.components.component import load_components, load_modifiers
        initialize_ship_data(base_dir)
        load_components(os.path.join(base_dir, "data", "components.json"))
        load_modifiers(os.path.join(base_dir, "data", "modifiers.json"))
        
    @classmethod
    def tearDownClass(cls):
        RegistryManager.instance().clear()
        pygame.quit()
    
    def setUp(self):
        self.event_bus = MockEventBus()
        from game.ui.screens.builder_viewmodel import BuilderViewModel
        self.viewmodel = BuilderViewModel(self.event_bus, 1280, 720)
        
    def tearDown(self):
        patch.stopall()
        
    # ─────────────────────────────────────────────────────────────────
    # Ship Property Tests
    # ─────────────────────────────────────────────────────────────────
    
    def test_ship_property_emits_event(self):
        """Setting ship property emits SHIP_UPDATED event."""
        from game.simulation.entities.ship import Ship
        
        ship = Ship("Test Ship", 640, 360, (255, 255, 255), ship_class="Escort")
        self.viewmodel.ship = ship
        
        events = self.event_bus.get_events('SHIP_UPDATED')
        self.assertEqual(len(events), 1)
        self.assertIs(events[0][1], ship)
        
    def test_notify_ship_changed_recalculates_and_emits(self):
        """notify_ship_changed recalculates stats and emits event."""
        from game.simulation.entities.ship import Ship
        
        ship = Ship("Test Ship", 640, 360, (255, 255, 255), ship_class="Escort")
        self.viewmodel._ship = ship  # Set directly to avoid initial event
        self.event_bus.clear()
        
        self.viewmodel.notify_ship_changed()
        
        events = self.event_bus.get_events('SHIP_UPDATED')
        self.assertEqual(len(events), 1)
        
    def test_create_default_ship(self):
        """create_default_ship creates and sets a new ship."""
        ship = self.viewmodel.create_default_ship("Frigate")
        
        self.assertIsNotNone(self.viewmodel.ship)
        self.assertEqual(self.viewmodel.ship.ship_class, "Frigate")
        self.assertIs(ship, self.viewmodel.ship)
        
    # ─────────────────────────────────────────────────────────────────
    # Selection Tests
    # ─────────────────────────────────────────────────────────────────
    
    def test_select_component_single(self):
        """Single selection replaces existing selection."""
        from game.simulation.entities.ship import Ship, LayerType
        from game.simulation.components.component import create_component
        
        ship = Ship("Test", 640, 360, (255, 255, 255), ship_class="Escort")
        self.viewmodel._ship = ship
        
        comp = create_component('armor_plate')
        selection = (LayerType.ARMOR, 0, comp)
        
        self.viewmodel.select_component(selection)
        
        self.assertEqual(len(self.viewmodel.selected_components), 1)
        self.assertIs(self.viewmodel.selected_components[0][2], comp)
        
    def test_select_component_append(self):
        """Append selection adds to existing selection."""
        from game.simulation.entities.ship import Ship, LayerType
        from game.simulation.components.component import create_component
        
        ship = Ship("Test", 640, 360, (255, 255, 255), ship_class="Escort")
        self.viewmodel._ship = ship
        
        comp1 = create_component('armor_plate')
        comp2 = create_component('armor_plate')
        
        self.viewmodel.select_component((LayerType.ARMOR, 0, comp1))
        self.viewmodel.select_component((LayerType.ARMOR, 1, comp2), append=True)
        
        self.assertEqual(len(self.viewmodel.selected_components), 2)
        
    def test_select_component_toggle(self):
        """Toggle deselects already selected component."""
        from game.simulation.entities.ship import LayerType
        from game.simulation.components.component import create_component
        
        comp = create_component('armor_plate')
        selection = (LayerType.ARMOR, 0, comp)
        
        # Select
        self.viewmodel.select_component(selection)
        self.assertEqual(len(self.viewmodel.selected_components), 1)
        
        # Toggle off
        self.viewmodel.select_component(selection, append=True, toggle=True)
        self.assertEqual(len(self.viewmodel.selected_components), 0)
        
    def test_select_component_homogeneity_enforced(self):
        """Selecting different component type replaces selection."""
        from game.simulation.entities.ship import LayerType
        from game.simulation.components.component import create_component
        
        armor = create_component('armor_plate')
        engine = create_component('standard_engine')
        
        self.viewmodel.select_component((LayerType.ARMOR, 0, armor))
        # Trying to append different type should replace
        self.viewmodel.select_component((LayerType.INNER, 0, engine), append=True)
        
        self.assertEqual(len(self.viewmodel.selected_components), 1)
        self.assertIs(self.viewmodel.selected_components[0][2], engine)
        
    def test_select_none_clears_selection(self):
        """Selecting None clears the selection."""
        from game.simulation.entities.ship import LayerType
        from game.simulation.components.component import create_component
        
        comp = create_component('armor_plate')
        self.viewmodel.select_component((LayerType.ARMOR, 0, comp))
        self.assertEqual(len(self.viewmodel.selected_components), 1)
        
        self.viewmodel.select_component(None)
        self.assertEqual(len(self.viewmodel.selected_components), 0)
        
    def test_primary_selection_returns_last(self):
        """primary_selection returns last selected component."""
        from game.simulation.entities.ship import LayerType
        from game.simulation.components.component import create_component
        
        comp1 = create_component('armor_plate')
        comp2 = create_component('armor_plate')
        
        self.viewmodel.select_component((LayerType.ARMOR, 0, comp1))
        self.viewmodel.select_component((LayerType.ARMOR, 1, comp2), append=True)
        
        primary = self.viewmodel.primary_selection
        self.assertIs(primary[2], comp2)
        
    def test_selection_emits_event(self):
        """Selection changes emit SELECTION_CHANGED event."""
        from game.simulation.entities.ship import LayerType
        from game.simulation.components.component import create_component
        
        self.event_bus.clear()
        
        comp = create_component('armor_plate')
        self.viewmodel.select_component((LayerType.ARMOR, 0, comp))
        
        events = self.event_bus.get_events('SELECTION_CHANGED')
        self.assertEqual(len(events), 1)
        
    # ─────────────────────────────────────────────────────────────────
    # Template Modifiers Tests
    # ─────────────────────────────────────────────────────────────────
    
    def test_template_modifiers_setter_emits_event(self):
        """Setting template_modifiers emits event."""
        self.event_bus.clear()
        
        self.viewmodel.template_modifiers = {'armor_quality': 2}
        
        events = self.event_bus.get_events('TEMPLATE_MODIFIERS_CHANGED')
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0][1], {'armor_quality': 2})
        
    def test_set_template_modifier(self):
        """set_template_modifier updates single modifier."""
        self.viewmodel.set_template_modifier('armor_quality', 3)
        
        self.assertEqual(self.viewmodel.template_modifiers.get('armor_quality'), 3)
        
    def test_remove_template_modifier(self):
        """remove_template_modifier removes a modifier."""
        self.viewmodel._template_modifiers = {'armor_quality': 2, 'damage_boost': 1}
        self.event_bus.clear()
        
        self.viewmodel.remove_template_modifier('armor_quality')
        
        self.assertNotIn('armor_quality', self.viewmodel.template_modifiers)
        self.assertIn('damage_boost', self.viewmodel.template_modifiers)
        
    def test_clear_template_modifiers(self):
        """clear_template_modifiers empties all modifiers."""
        self.viewmodel._template_modifiers = {'armor_quality': 2, 'damage_boost': 1}
        self.event_bus.clear()
        
        self.viewmodel.clear_template_modifiers()
        
        self.assertEqual(len(self.viewmodel.template_modifiers), 0)
        
    # ─────────────────────────────────────────────────────────────────
    # Drag State Tests
    # ─────────────────────────────────────────────────────────────────
    
    def test_dragged_item_setter_emits_event(self):
        """Setting dragged_item emits DRAG_STATE_CHANGED event."""
        from game.simulation.components.component import create_component
        
        self.event_bus.clear()
        
        comp = create_component('armor_plate')
        self.viewmodel.dragged_item = comp
        
        events = self.event_bus.get_events('DRAG_STATE_CHANGED')
        self.assertEqual(len(events), 1)
        self.assertIs(events[0][1], comp)
        
    # ─────────────────────────────────────────────────────────────────
    # Ship Operations Tests
    # ─────────────────────────────────────────────────────────────────
    
    def test_clear_design_preserves_hull(self):
        """clear_design removes components but preserves hull layer."""
        from game.simulation.entities.ship import Ship, LayerType
        from game.simulation.components.component import create_component
        
        ship = Ship("Test", 640, 360, (255, 255, 255), ship_class="Escort")
        ship.add_component(create_component('armor_plate'), LayerType.ARMOR)
        
        # Add engine only if INNER layer exists
        if LayerType.INNER in ship.layers:
            ship.add_component(create_component('standard_engine'), LayerType.INNER)
            
        self.viewmodel._ship = ship
        
        self.viewmodel.clear_design()
        
        # Non-hull layers should be empty
        for layer_type, layer_data in ship.layers.items():
            if layer_type != LayerType.HULL:
                self.assertEqual(
                    len(layer_data['components']), 0,
                    f"Layer {layer_type.name} should be empty after clear_design"
                )
        
        # Hull should remain
        if LayerType.HULL in ship.layers:
            self.assertGreater(len(ship.layers[LayerType.HULL]['components']), 0)


if __name__ == '__main__':
    unittest.main()
