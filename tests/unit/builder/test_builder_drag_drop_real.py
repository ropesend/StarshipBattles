import pytest
from unittest.mock import MagicMock, patch
import pygame

# We need to mock pygame_gui before importing builder_gui because it initializes UI
# Actually builder_screen imports pygame_gui.
# We can use reference imports if we can instantiate BuilderScreen without a full window.
# But BuilderScreen __init__ creates UIManager which needs a window surface or size.
# We can mock UIManager.

from game.ui.screens import workshop_screen
from game.ui.screens.workshop_screen import DesignWorkshopScreen
from game.ui.screens.workshop_context import WorkshopContext
from game.simulation.entities.ship import LayerType
from game.simulation.entities.layer_data import LayerData


class TestBuilderDragDropReal:

    @pytest.fixture(autouse=True)
    def setup_builder(self, fresh_registries):
        """Set up the builder with mocked dependencies."""
        self._registries = fresh_registries
        if not pygame.get_init():
            pygame.init()
            pygame.display.set_mode((1, 1))  # Mock display for UIManager

        # Mock dependencies that DesignWorkshopScreen init calls
        # IMPORTANT: Patch at workshop_screen level since that's the real implementation
        patchers = []

        # Patch _create_ui to avoid complex UI initialization
        p_create_ui = patch('game.ui.screens.workshop_screen.DesignWorkshopScreen._create_ui')
        mock_create_ui = p_create_ui.start()
        patchers.append(p_create_ui)

        # Patch UIManager to avoid theme loading real files or needing display
        p_manager = patch('game.ui.screens.workshop_screen.pygame_gui.UIManager')
        MockUIManager = p_manager.start()
        patchers.append(p_manager)

        # Patch SpriteManager
        p_sprite = patch('game.ui.screens.workshop_screen.get_default_sprite_manager')
        MockSpriteManager = p_sprite.start()
        patchers.append(p_sprite)

        # Patch ThemeManager
        p_theme = patch('game.ui.screens.workshop_screen.get_default_ship_theme_manager')
        MockThemeManager = p_theme.start()
        patchers.append(p_theme)

        # Initialize Builder
        # We need a valid screen size
        # PROJ-211: registries is now required
        context = WorkshopContext.standalone(tech_preset_name="default", registries=self._registries)
        context.on_return = lambda x: None
        builder = DesignWorkshopScreen(1280, 720, context)

        # Manually setup the mocks that _create_ui would have created
        builder.ui_manager = MagicMock()
        builder.event_bus = MagicMock()
        builder.left_panel = MagicMock()
        builder.right_panel = MagicMock()
        builder.layer_panel = MagicMock()
        builder.modifier_panel = MagicMock()
        builder.weapons_report_panel = MagicMock()
        builder.detail_panel = MagicMock()
        builder.controller = MagicMock()
        builder.schematic_view = MagicMock()

        builder.left_panel.handle_event.return_value = None
        builder.layer_panel.handle_event.return_value = None
        builder.modifier_panel.handle_event.return_value = None
        builder.weapons_report_panel.handle_event.return_value = None

        # Setup test ship via viewmodel
        builder.viewmodel._ship = MagicMock()
        # Use real LayerData objects (PROJ-84)
        builder.ship.layers = {
            LayerType.CORE: LayerData(),
            LayerType.INNER: LayerData(),
            LayerType.OUTER: LayerData(),
            LayerType.ARMOR: LayerData()
        }

        # Add ship helper methods that event_router now uses
        def get_all_components():
            result = []
            for layer_data in builder.ship.layers.values():
                result.extend(layer_data.components)
            return result

        def iter_components():
            for layer_type, layer_data in builder.ship.layers.items():
                for comp in layer_data.components:
                    yield layer_type, comp

        def has_components():
            for layer_data in builder.ship.layers.values():
                if layer_data.components:
                    return True
            return False

        builder.ship.get_all_components = get_all_components
        builder.ship.iter_components = iter_components
        builder.ship.has_components = has_components

        # Set benign defaults to satisfy update loop comparisons
        builder.ship.mass = 1000
        builder.ship.max_mass_budget = 10000
        builder.ship.resources.set_max_value('fuel', 100)
        builder.ship.resources.set_max_value('fuel', 100)
        builder.ship.resources.set_value('fuel', 100)
        builder.ship.resources.set_max_value('ammo', 100)
        builder.ship.resources.set_max_value('ammo', 100)
        builder.ship.resources.set_value('ammo', 100)
        builder.ship.resources.set_max_value('energy', 100)
        builder.ship.resources.set_max_value('energy', 100)
        builder.ship.resources.set_value('energy', 100)
        builder.ship.total_thrust = 500
        builder.ship.drag = 0.1
        builder.ship.name = "Test Ship"

        # Store for use in tests
        self.builder = builder
        self.patchers = patchers

        yield

        # Teardown: Clean up ALL mocks first (prevents mock object pollution)
        patch.stopall()

        for p in patchers:
            p.stop()
        pygame.quit()

    def test_drag_start(self):
        """Verify starting a drag sets dragged_item."""
        # Drag is typically started by InteractionController or UI event.
        # Let's interact with controller directly or simulate the action.

        # Simulate action: 'select_component_type' sets dragged_item
        comp_template = MagicMock()
        comp_template.clone.return_value = comp_template  # Return self for simplicity

        # FIXED: Ensure mock has numeric stats and lists to avoid TypeError >
        comp_template.mass = 10
        comp_template.max_hp = 100
        comp_template.current_hp = 100
        comp_template.modifiers = []
        comp_template.name = "Template Component"
        comp_template.is_active = True

        # Create a fake event or just call the handler logic?
        # BuilderScreen has handle_event which processes actions.
        # But actions come from panels.
        # Let's call the logic block directly via 'handle_event' mocking the action return from left_panel.

        # Mock left_panel.handle_event to return ('select_component_type', comp_template)
        self.builder.left_panel.handle_event = MagicMock(return_value=('select_component_type', comp_template))

        # Trigger builder handle_event with a dummy pygame event
        dummy_event = MagicMock()
        self.builder.handle_event(dummy_event)

        # Verify dragged item is set
        assert self.builder.controller.dragged_item is not None
        assert self.builder.controller.dragged_item == comp_template

    def test_drop_validation_success(self):
        """Verify dropping a valid component calls viewmodel.add_component_instance."""
        # Setup: Original component IS on the ship
        original = MagicMock()
        original.modifiers = []
        original.current_hp = 100
        original.max_hp = 100
        original.mass = 10
        original.is_active = True
        original.name = "Original Component"

        # Key Fix: clone() must return a mock with stats too!
        cloned = MagicMock()
        cloned.current_hp = 100
        cloned.max_hp = 100
        cloned.mass = 10
        cloned.is_active = True
        cloned.name = "Original Component"
        cloned.modifiers = []

        original.clone.return_value = cloned

        self.builder.ship.layers[LayerType.OUTER].components = [original]

        # Mock the viewmodel's add_component_instance to return success
        self.builder.viewmodel.add_component_instance = MagicMock(return_value=True)

        # Pass tuple format (component, layer_type) - layer_type is required
        self.builder.left_panel.handle_event = MagicMock(return_value=('add_individual', (original, LayerType.OUTER)))

        self.builder.handle_event(MagicMock())

        # Verify viewmodel.add_component_instance was called with cloned component
        self.builder.viewmodel.add_component_instance.assert_called()
        call_args = self.builder.viewmodel.add_component_instance.call_args
        # First arg should be the cloned component, second should be the layer
        assert call_args[0][1] == LayerType.OUTER

    def test_drop_validation_failure(self):
        """Verify showing error on invalid add."""
        original = MagicMock()
        original.modifiers = []
        original.current_hp = 100
        original.max_hp = 100
        original.mass = 10
        original.is_active = True
        original.name = "Original Component"

        # Key Fix: clone() must return a mock with stats too!
        cloned = MagicMock()
        cloned.current_hp = 100
        cloned.max_hp = 100
        cloned.mass = 10
        cloned.is_active = True
        cloned.name = "Original Component"
        cloned.modifiers = []

        original.clone.return_value = cloned

        self.builder.ship.layers[LayerType.OUTER].components = [original]

        # Mock the viewmodel's add_component_instance to return failure
        self.builder.viewmodel.add_component_instance = MagicMock(return_value=False)
        # Mock the _last_result to have errors (last_errors is a property that reads from _last_result)
        mock_result = MagicMock()
        mock_result.errors = ["Overlapping"]
        self.builder.viewmodel._last_result = mock_result

        # Pass tuple format (component, layer_type) - layer_type is required
        self.builder.left_panel.handle_event = MagicMock(return_value=('add_individual', (original, LayerType.OUTER)))

        # Capture show_error
        self.builder.show_error = MagicMock()

        self.builder.handle_event(MagicMock())

        # Verify error shown
        self.builder.show_error.assert_called_with("Cannot add: Overlapping")
        # Verify viewmodel was called but returned False
        self.builder.viewmodel.add_component_instance.assert_called()
